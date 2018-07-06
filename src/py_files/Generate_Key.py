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
import socket
import os

# This class generate the rsa keys for all the connected devices
class Generate_Key(QtWidgets.QDialog, Generate_Key_Design.Ui_Dialog):
    # signal that make sure that the rsa key has been created
    rsaKey = QtCore.pyqtSignal(bool)

    # Definition of the Generate_Key class
    def __init__(self, ipList, userList, passwordList, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)

        # initialisation of the progress bar
        self.rsaProgressBar.setValue(0)

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
        self.outPutString = ""
        self.error = [False] * len(self.ipList)


    # Launch the rsa key generation
    def generateKey(self):
        self.buttonCancel.setEnabled(False)
        self.buttonGenerateKey.setEnabled(False)


        self.outPutString = ""
        self.error = [False] * len(self.ipList)

        # generate specific multilauncher rsa key local computer
        subprocess.call('echo -e "\n" | ssh-keygen -q -t rsa -N "" -f ~/.ssh/multikey ', stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)

        # update the progress bar
        self.rsaProgressValue = 0
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # Loop that connects to the remote robots, changes the needed permissions, and pushes the public key
        for index in range(len(self.ipList)):

            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self.ssh.connect(self.ipList[index], 22, username=self.userList[index],
                             password=self.passwordList[self.ipList[index]], allow_agent=False, look_for_keys=False)

                # create the shell for the current thread index
                self.channel = self.ssh.invoke_shell()
                self.channel.settimeout(1.5)
                # Changes the remote robot's .ssh directory permissions to the user remote user
                self.launchChmod(index)

                # Pushes the public key to the remote robot
                self.launchPushKey(index)

            except paramiko.AuthenticationException:
                self.outPutString = self.outPutString + "X - Error in connecting to: "+self.ipList[index]+" due to password mismatch\n"

            self.ssh.close()

        # update the progress bar
        self.rsaProgressBar.setValue(100)

        # show the possible occurred errors to the user in a dialog window
        if self.checkError():
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.outPutString)

        else:
            temp = QtWidgets.QMessageBox.information(self, "Information", self.outPutString)

        # finish the rsa key generation and come back to the main window
        self.rsaKey.emit(True)

        self.buttonCancel.setEnabled(True)
        self.buttonGenerateKey.setEnabled(True)
        self.quitWindow()


    # Changes the remote robot's directory permissions to be able to push a public key to the .ssh directory
    def launchChmod(self, index):

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # ssh into the device
        self.channel.send("ssh " + str(self.userList[index]) + "@" + str(self.ipList[index]) + '\n')
        self.waitFinishCommandChmod(self.channel, index)

        # check if the ssh to the device worked properly
        if self.error[index] is False:
            # if the ssh command worked then do the permissions modification to the file

            # update the progress bar
            self.rsaProgressValue += 13 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the owner of ssh directory
            self.channel.send('sudo chown -R ' + str(self.userList[index]) + ' ~/.ssh/\n')
            self.waitFinishCommandChmod(self.channel, index)

            # update the progress bar
            self.rsaProgressValue += 7 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the owner of ssh directory
            self.channel.send('sudo chgrp -R ' + str(self.userList[index]) + ' ~/.ssh/\n')
            self.waitFinishCommandChmod(self.channel, index)

            # update the progress bar
            self.rsaProgressValue += 10 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the permission of the authorized key file
            self.channel.send('sudo chmod 700 ~/.ssh\n')
            self.waitFinishCommandChmod(self.channel, index)

            # update the progress bar
            self.rsaProgressValue += 10 / len(self.ipList)
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            # change the permission of ssh directory
            self.channel.send('sudo chmod 600 ~/.ssh/authorized_keys\n')
            self.waitFinishCommandChmod(self.channel, index)


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
            elif '[sudo]' in data:
                channel.send(self.passwordList[self.ipList[index]] + "\n")
                self.waitFinishCommandChmod(channel, index)
                break
            elif "continue connecting (yes/no)" in data:
                channel.send("yes\n")
                self.waitFinishCommandChmod(channel, index)
                break
            elif "password:" in data:
                channel.send(self.passwordList[self.ipList[index]] + "\n")
                self.waitFinishCommandChmod(channel, index)
                break
            # if the password is wrong and the user cannot ssh to the device change the boolean error
            elif "Permission denied" in data:
                channel.send("\x03\n")
                self.error[index] = True
                self.outPutString = self.outPutString + "X - " + self.ipList[index] + ": Wrong Password \n"
                self.waitFinishCommandChmod(channel, index)
                break
            elif "passphrase for key" in data:
                channel.send("\n")
                self.waitFinishCommandChmod(channel, index)
                break
            elif self.userList[index] + "@" in data:
                break


    # Pushes the public RSA key to the remote robots
    def launchPushKey(self, index):

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # create the public keys and send it to the right device
        copy = "sshpass -p \""+str(self.passwordList[self.ipList[index]])+"\" ssh-copy-id -i ~/.ssh/multikey " + str(self.userList[index]) + "@" + str(self.ipList[index])+"\n"
        subprocess.call(copy, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)

        # update the progress bar
        self.rsaProgressValue += 15 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # wait for the end of the command and check for possible error like : the ip device is wrong or the user device is wrong
        self.waitFinishCommandKey(self.channel, index, "Permission denied", self.userList[index] + "@")

        # update the progress bar
        self.rsaProgressValue += 10 / len(self.ipList)
        self.rsaProgressBar.setValue(self.rsaProgressValue)

        # if an error occurs in this thread, append the error string to the outputstring
        if self.error[index] is False:
            self.outPutString = self.outPutString + "V - " + self.ipList[index] + ": RSA Public Key set up \n"


    # Loops indefinitely until the RSA key has been setup or if the user has interrupted the threads
    def waitFinishCommandKey(self, channel, index, errorString, endString):
        while True:
            try:
                # wait a little bit
                time.sleep(self.sleepTime)

                # retrieve the data from the thread shell
                data = str(channel.recv(1024).decode("utf-8"))
                # if an error has already occurs finish the thread
                if self.error[index] is True:
                    break

                # check the possible error during the process and append error message to the output string
                elif errorString in data:
                    if errorString == "Permission denied":
                        channel.send("\x03\n")
                    self.error[index] = True
                    break

                # check the possible different end of commands
                elif "continue connecting (yes/no)" in data:
                    channel.send("yes\n")
                    self.waitFinishCommandKey(channel, index, errorString, endString)
                    break
                elif "password:" in data:
                    channel.send(self.passwordList[self.ipList[index]] + "\n")
                    self.waitFinishCommandKey(channel, index, errorString, endString)
                    break
                elif '[sudo]' in data:
                    channel.send(self.passwordList[self.ipList[index]] + "\n")
                    self.waitFinishCommandChmod(channel, index)
                    break
                elif endString in data:
                    break
                elif self.userList[index] + "@" in data:
                    break
            except socket.timeout:
                break


    # check if there is at least one error between all the thread
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
