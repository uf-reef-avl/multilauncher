#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created:
#


import Generate_Key_Design
from PyQt5 import QtCore, QtWidgets
import paramiko
import time
import subprocess
from multiprocessing.pool import ThreadPool


# This class generate the rsa keys for all the connected devices
class Generate_Key(QtWidgets.QDialog, Generate_Key_Design.Ui_Dialog):

    # signal that make sure that the rsa key has been created
    rsaKey = QtCore.pyqtSignal(bool)


    # Definition of the Generate_Key class
    def __init__(self,ipList, userList, passwordList, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)

        # initialisation of the progress bar
        self.rsaProgressBar.setValue(0)
        self.rsaProgressBar.hide()

        # initialise the useful value of the current case
        self.ipList = ipList
        self.userList = userList
        self.passwordList = passwordList
        self.sleepTime = 1
        self.rsaProgressValue = 0

        # connect every button to his correct slot
        self.buttonGenerateKey.clicked.connect(self.generateKey)
        self.buttonCancel.clicked.connect(self.quitWindow)

        # initialise the error string and list in order to know if some errors occur during the rsa generation process
        self.outputString = ""
        self.error = [False]*len(self.ipList)


    # Launch the rsa key generation
    def generateKey(self):
        self.buttonCancel.setEnabled(False)
        self.buttonGenerateKey.setEnabled(False)

        try:
            self.outputString = ""
            self.error = [False] * len(self.ipList)

            # generate specific multilauncher rsa key in user laptop
            subprocess.call('echo -e "\n" | ssh-keygen -q -t rsa -N "" -f ~/.ssh/multikey ', shell=True)

            # create the paramiko client to ssh in the user device and generate the public keys for others devices
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect("127.0.0.1", 22, username=str(self.lineEditUsername.text().strip()), password=str(self.lineEditPassword.text().strip()), allow_agent=False, look_for_keys=False)

            # update the progress bar
            self.rsaProgressBar.show()
            self.rsaProgressValue = 0
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # launch the different thread which will change the .ssh permission directory to the user
            numberOfThread = len(self.ipList)
            poolChmod = ThreadPool(numberOfThread)
            resultsChmod = poolChmod.map(self.launchChmodThread, range(numberOfThread))

            # Finish to close all the permissions threads and update display components
            poolChmod.close()
            poolChmod.join()

            #close the ssh connection in order to avoid going over the MaxSessions ssh limit set in etc/ssh/sshd_config
            self.ssh.close()

            #reopen the ssh connection
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect("127.0.0.1", 22, username=str(self.lineEditUsername.text().strip()),
                             password=str(self.lineEditPassword.text().strip()), allow_agent=False, look_for_keys=False)

            # launch the different thread which will push the public key
            poolKeygen = ThreadPool(numberOfThread)
            resultsKeygen = poolKeygen.map(self.launchKeyGenerationThread, range(numberOfThread))

            # Finish to close all the threads and update display components and finish the ssh connection
            poolKeygen.close()
            poolKeygen.join()
            self.ssh.close()

            # update the progress bar
            self.rsaProgressBar.setValue(100)
            self.rsaProgressBar.hide()

            # show the possible occurred errors to the user in a dialog window
            if self.checkError():
                temp = QtWidgets.QMessageBox.warning(self, "Warning",  self.outputString)

            else:
                temp = QtWidgets.QMessageBox.information(self, "Information", self.outputString)
                self.close()
                self.deleteLater()

            # finish the rsa key generation and come back to the main window
            self.rsaKey.emit(True)

        except paramiko.AuthenticationException:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Failed to login to the admin session, please re-enter the admin username and the admin password")

        self.buttonCancel.setEnabled(True)
        self.buttonGenerateKey.setEnabled(True)


    # Changes the remote robot's directory permissions to be able to push a public key to the .ssh directory
    def launchChmodThread(self, index):

        # create the shell for the current thread index
        channel = self.ssh.invoke_shell()

        # update the progress bar
        self.rsaProgressValue += 10/len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        #ssh into the device
        channel.send("ssh "+ str(self.userList[index]) + "@" + str(self.ipList[index]) + '\n')
        self.waitFinishCommandChmod(channel,index)

        #check if the ssh to the device worked properly
        if self.error[index] is False:

            # if the ssh command worked then do the permissions modification to the file

            # update the progress bar
            self.rsaProgressValue += 13 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            #change the owner of ssh directory
            channel.send('sudo chown -R '+str(self.userList[index])+' ~/.ssh/\n')
            self.waitFinishCommandChmod(channel, index)

            # update the progress bar
            self.rsaProgressValue += 7 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the owner of ssh directory
            channel.send('sudo chgrp -R '+str(self.userList[index])+' ~/.ssh/\n')
            self.waitFinishCommandChmod(channel, index)

            # update the progress bar
            self.rsaProgressValue += 10 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the permission of the authorized key file
            channel.send('sudo chmod 700 ~/.ssh\n')
            self.waitFinishCommandChmod(channel, index)

            # update the progress bar
            self.rsaProgressValue += 10 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the permission of ssh directory
            channel.send('sudo chmod 600 ~/.ssh/authorized_keys\n')
            self.waitFinishCommandChmod(channel, index)


    # Loops indefinitely until the Chmod commands have finished executing or if the user has interrupted the threads
    def waitFinishCommandChmod(self, channel, index):
        while True:
            # wait a little bit
            time.sleep(self.sleepTime)

            # retrieve the data from the thread shell
            data = str(channel.recv(1024).decode("utf-8"))

            # check the possible different end of commands and adapt the behaviour
            if self.error[index] is True:
                break
            if '[sudo]' in data:
                channel.send(self.passwordList[index] + "\n")
                self.waitFinishCommandChmod(channel, index)
                break
            if "continue connecting (yes/no)" in data:
                channel.send("yes\n")
                self.waitFinishCommandChmod(channel, index)
                break
            if "password:" in data:
                channel.send(self.passwordList[index] + "\n")
                self.waitFinishCommandChmod(channel, index)
                break
            #if the password is wrong and the user cannot ssh to the device change the boolean error
            if "Permission denied" in data:
                channel.send("\x03\n")
                self.error[index] = True
                self.outputString = self.outputString +"X - "+ self.ipList[index] + ": Wrong Password \n"
                self.waitFinishCommandChmod(channel, index)
                break
            if self.userList[index] + "@" in data:
                break


    # Pushes the public RSA key to the remote robots
    def launchKeyGenerationThread(self, index):

        # create the shell for the current thread index
        channel = self.ssh.invoke_shell()

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # create the public keys and send it to the right device
        channel.send("ssh-copy-id -i ~/.ssh/multikey " + str(self.userList[index]) + "@" + str(self.ipList[index]) + '\n')

        # wait for the end of the command and check for possible error like : the key is already on the remote system
        self.waitFinishCommandKey(channel, index, "already exist on the remote system", "password:")

        # update the progress bar
        self.rsaProgressValue += 15 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)
        channel.send(str(self.passwordList[index]) + '\n')

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # wait for the end of the command and check for possible error like : the ip device is wrong or the user device is wrong
        self.waitFinishCommandKey(channel, index, "Permission denied", str(self.lineEditUsername.text()) + "@")

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # if an error occurs in this thread, append the error string to the outputstring
        if self.error[index] is False:
            self.outputString =  self.outputString +"V - "+ self.ipList[index] + ": RSA Public Key set up \n"


    # Loops indefinitely until the RSA key has been setup or if the user has interrupted the threads
    def waitFinishCommandKey(self, channel,index, errorString ,endString):
        while True:

            # wait a little bit
            time.sleep(self.sleepTime)

            # retrieve the data from the thread shell
            data = str(channel.recv(1024).decode("utf-8"))

            # if an error has already occurs finish the thread
            if self.error[index] is True:
                break

            # check the possible error during the process and append error message to the output string
            if errorString in data:
                if errorString == "Permission denied":
                    channel.send("\x03\n")
                elif errorString == "already exist on the remote system":
                    self.outputString = self.outputString  +"X - "+ self.ipList[index] + ": Key is already set up on the remote server\n"
                self.error[index] = True
                break

            # check the possible different end of commands
            if "continue connecting (yes/no)" in data:
                channel.send("yes\n")
                self.waitFinishCommandKey(channel, index, errorString, endString)
                break
            if "password:" in data:
                channel.send(self.passwordList[index]+"\n")
                self.waitFinishCommandKey(channel, index, errorString, endString)
                break
            if '[sudo]' in data:
                channel.send(self.passwordList[index] + "\n")
                self.waitFinishCommandChmod(channel, index)
                break
            if endString in data:
                break
            if self.userList[index] + "@" in data:
                break


    #check if there is at least one error between all the thread
    def checkError(self):
        errorCheck = False
        for error in self.error:
            if error is True:
                return True
        return errorCheck


    # Close the generate key window
    def quitWindow(self):
        self.close()
        self.deleteLater()
