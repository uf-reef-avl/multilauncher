#
# File: Generate_Key.py
# Authors: Matthew Hovatter
#
# Created: Summer 2018
#
# Copyright 2018 FIRSTNAME LASTNAME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import Generate_Key_Design
from PyQt5 import QtCore, QtWidgets
import subprocess
import os
import getpass
from Workers import GenKey_Worker


#This class generate the rsa keys for all the connected devices
class Generate_Key(QtWidgets.QDialog, Generate_Key_Design.Ui_Dialog):

    #Signals that the RSA key has been created
    rsaKey = QtCore.pyqtSignal(bool)

    #Definition of the Generate_Key class
    def __init__(self, ipList, userList, passwordList, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)

        #Initialisation of the progress bar
        self.rsaProgressBar.setValue(0)

        #Initialise the lists of relevant values
        self.ipList = ipList
        self.userList = userList
        self.passwordList = passwordList
        self.workerList = {}
        self.threadList = {}
        self.rsaProgressValue = 0

        #Connect every button to its correct slot
        self.buttonGenerateKey.clicked.connect(self.generateAndPushKey)
        self.buttonCancel.clicked.connect(self.quitWindow)

        #Initialise the error string and list in order to know if some errors occurred during the RSA generation process
        self.outPutString = ""
        self.error = [False] * len(self.ipList)


    #Launch the RSA key generation
    def generateAndPushKey(self):
        self.buttonCancel.setEnabled(False)
        self.buttonGenerateKey.setEnabled(False)

        self.outPutString = ""
        self.error = [False] * len(self.ipList)

        if not os.path.exists(os.path.expanduser("~/.ssh")):

            subprocess.call(["mdkir", "-p", "/home/" + str(getpass.getuser()) + "/.ssh"])

        if not os.path.exists(os.path.expanduser("~/.ssh/multikey")):

            #Generate the specific Multilauncher RSA key on the local computer
            subprocess.call('echo -e "\n" | ssh-keygen -q -t rsa -N "" -C multikey -f ~/.ssh/multikey', stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)

        if os.path.exists(os.path.expanduser("~/.ssh/multikey")):

            #Check to see if a multikey is already added to the ssh-agent
            if not self.checkSSHAgent():
                subprocess.call(["ssh-add", "/home/" + str(getpass.getuser()) + "/.ssh/multikey"], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))

            #Update the progress bar
            self.rsaProgressValue = 0
            self.rsaProgressBar.setValue(self.rsaProgressValue)

            #Loop that connects to the remote robots, occurs changes the needed permissions, and pushes the public key
            for index in range(len(self.ipList)):

                tempThread = QtCore.QThread()
                tempThread.start()
                worker = GenKey_Worker(self.ipList[index], self.userList[index], self.passwordList[self.ipList[index]])

                #Create the worker
                worker.finishThread.connect(self.killThread)
                worker.moveToThread(tempThread)
                worker.updateValue.connect(self.updateProgressbar)
                worker.start.emit()
                self.workerList[index] = worker
                self.threadList[index] = tempThread

        else:
            self.error = [True]
            self.outPutString += "There was an issue with creating the RSA key at: ~/.ssh/multikey\n"
            self.quitWindow()


    #Checks the ssh-agent to see if multikey is already added
    def checkSSHAgent(self):

        process = subprocess.Popen(["ssh-add", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result = process.communicate()

        rFile = open("/home/" + str(getpass.getuser()) + "/.ssh/multikey.pub", "r")
        listOfLines = rFile.readlines()
        rFile.close()
        listOfLines = listOfLines[0].splitlines()
        pubKey = listOfLines[0]

        if str(pubKey) + " multikey" in result[0]:
            return True
        else:
            return False


    #Updates the progress bar for visual feedback
    @QtCore.pyqtSlot(int)
    def updateProgressbar(self, change):
        self.rsaProgressValue += (change/ len(self.ipList))
        self.rsaProgressBar.setValue(self.rsaProgressValue)


    #Terminates the calling thread
    @QtCore.pyqtSlot(str, str, bool)
    def killThread(self, IP, eMessage, result):

        #Append a thread's error string to the master error string
        self.outPutString += eMessage + "\n"
        index = self.ipList.index(IP)
        self.error[index] = result

        #Terminates the thread
        del self.workerList[index]
        self.threadList[index].quit()
        self.threadList[index].wait()
        del self.threadList[index]

        if self.workerList == {} and self.threadList == {}:
            self.quitWindow()


    #Check if there was at least one error during execution
    def checkError(self):
        for error in self.error:
            if error:
                return True
        return False


    #Display the results to the user and close the GenerateKey window
    def quitWindow(self):

        #Update the progress bar
        self.rsaProgressBar.setValue(100)

        #Show the possible occurred errors to the user in a dialog window
        if self.checkError():
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.outPutString)

        else:
            if self.outPutString != "":
                temp = QtWidgets.QMessageBox.information(self, "Information", self.outPutString)

                #Finish the RSA key generation and come back to the Main Window
                self.rsaKey.emit(True)

        self.buttonCancel.setEnabled(True)
        self.buttonGenerateKey.setEnabled(True)

        self.close()
        self.deleteLater()
