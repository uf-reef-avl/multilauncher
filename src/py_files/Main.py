#!/usr/bin/python2.7
#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created:
#

from PyQt5 import QtCore, QtGui, QtWidgets
from Adjust_Arguments import Adjust_Arguments
from Password_Window import Password_Window
import MultilauncherDesign
from Launch_Window import Launch_Window
from Workers import SSH_Transfer_File_Worker, Bashrc_Worker, Launch_Worker, Ping_Worker
from Edit_Robot_Dialog import Edit_Robot_Dialog
import os
import paramiko
import sys

#This class creates the main window of the application
class Multilaunch(QtWidgets.QMainWindow, MultilauncherDesign.Ui_MainWindow):

    #Initializes and defines the Multilaunch window
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.myKey = ""
        self.RSA = self.rsaCheck()
        self.maxSSH = self.setMaxSSH()

        #modify the ui to add the tab widget
        del self.commands
        self.tabCommands = QtWidgets.QTabWidget()
        self.gridLayout_4.addWidget(self.tabCommands, 3, 0, 1, 3)

        #Paring buttons to functions
        self.filesearchbutton.clicked.connect(self.browseForFile)
        self.pingrobotsbutton.clicked.connect(self.pingTest)
        self.bashrcbutton.clicked.connect(self.updateBashrc)
        self.robotlistsavebutton.clicked.connect(self.saveToFile)
        self.spinpackage.valueChanged.connect(self.reloadPackage)
        self.launchbutton.clicked.connect(self.launchCommands)
        self.buttontransfer.clicked.connect(self.gitCopyRepo)
        self.savecommandsbutton.clicked.connect(self.saveCurrentCommand)
        self.loadcommandsbutton.clicked.connect(self.loadCurrentCommand)
        self.argumentbutton.clicked.connect(self.adjustArgsWindow)
        self.editlistsbutton.clicked.connect(self.editRobots)
        self.findRSAButton.clicked.connect(self.findRSA)

        #Backend data structures used for processing user input throughout the application
        self.IPS = []
        self.USERS = []
        self.TYPES = []
        self.DICT_TYPES = {}
        self.CONNECTION_STATUS = []
        self.PASSWORDS = []
        self.ARGS = []
        self.ENABLE = []
        self.STRINGOFPATH = ""
        self.ERRORTEXT = ""

        #Creates the Launch Window used in pinging and executing selected commands
        self.childLaunchWindow = Launch_Window()
        self.childLaunchWindow.buttonStopThread.clicked.connect(self.interruptRemainingThreads)
        self.childLaunchWindow.lineDebugCommand.returnPressed.connect(self.sendDebugCommand)

        #Data structures for the dynamic launch window
        self.layoutTerminalList = []
        self.widgetTerminalList = []
        self.terminalList = []
        self.terminalRefreshSeconds = 0.1
        self.threadList = {}
        self.workerList = {}
        self.threadStillRunning = 'no'

        #Modifies the File Transfer section of the application to dynamically expand
        self.area = QtWidgets.QWidget()
        self.area.setLayout(self.gridpackage)
        self.scrollareapackage.setWidget(self.area)
        self.scrollareapackage.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollareapackage.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.linePathParentPackage = []
        self.linePathGitRepoList = []
        self.buttonDirectoryPackageList = []
        self.comboRobotTypeList = []
        self.comboMakeList = []

        #Data structures to hold and process plaintext commands from the user
        self.layoutCommandList = []
        self.widgetCommandList = []
        self.plaintextCommandDict = {}

        #Only lets the user access certain functions if they have successfully pinged their listed robots
        self.setLaunchEnable(self.checkConnectionAvailable())

        #Corrects the column header sizes
        self.setTableSize()


    #Corrects the column header sizes
    def setTableSize(self):
        print self.width()
        self.robotTable.setColumnWidth(0, self.width()/6)
        self.robotTable.setColumnWidth(1, self.width()/6)
        self.robotTable.setColumnWidth(2, self.width()/6)
        self.robotTable.setColumnWidth(3, self.width()/6)
        self.robotTable.setColumnWidth(4, self.width()/6)
        self.robotTable.setColumnWidth(5, self.width()/6)


    #Creates lists based on the column requested
    def makeListFromTable(self, listName):
        tempList = []
        try:
            if listName == "enablelist":
                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    if self.robotTable.item(y,0).checkState() == 2:
                        tempList.append("True")
                    else:
                        tempList.append("False")

            elif listName == "argumentlist":
                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    text = ""
                    for index in range(self.robotTable.cellWidget(y,4).count()):
                        if index != self.robotTable.cellWidget(y,4).count()-1:
                            text += self.robotTable.cellWidget(y,4).itemText(index)+"|"
                        else:
                            text += self.robotTable.cellWidget(y, 4).itemText(index)
                    tempList.append(text)
            else:
                # Find the correct column
                for x in range(self.robotTable.columnCount()):
                    if listName == self.robotTable.horizontalHeaderItem(x).text():

                        #Append all data in the column
                        for y in range(self.robotTable.rowCount()):
                            tempList.append(self.robotTable.item(y,x).text())
                        break
            return tempList
        except:
            e = sys.exc_info()[0]
            print( "List from Table Error: %s" % e )


    #Runs the Edit Robot Dialog window if there are no other threads running
    def editRobots(self):
        if self.threadStillRunning == 'no':
            self.updateLists()
            self.robotEditDialog = Edit_Robot_Dialog(self)
            self.robotEditDialog.save.connect(self.updateListsFromDialog)
            self.loadTable()
            self.robotEditDialog.show()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)


    #Loads the Edit Robot Dialog's table from the text fields from the Main Window
    def loadTable(self):
        self.updateLists()

        if len(self.IPS) != 0:
            for x in range(len(self.IPS)):
                self.robotEditDialog.robotTable.insertRow(x)
                self.robotEditDialog.robotTable.setItem(x,0,QtWidgets.QTableWidgetItem(self.ENABLE[x]))
                self.robotEditDialog.robotTable.setItem(x,1,QtWidgets.QTableWidgetItem(self.IPS[x]))
                self.robotEditDialog.robotTable.setItem(x,2,QtWidgets.QTableWidgetItem(self.USERS[x]))
                self.robotEditDialog.robotTable.setItem(x,3,QtWidgets.QTableWidgetItem(self.TYPES[x]))


    #Loads the text fields in the Main Window from the Edit Robot Dialog's table
    @QtCore.pyqtSlot(list, list, list, list)
    def updateListsFromDialog(self, enableText, ipText, nameText, typeText):

        #Prevent duplicate/invalid data
        self.robotTable.setRowCount(0)

        #If there are to be no robots selected
        if ipText == []:
            self.updateLists()
            self.flushCommand()

        #Main addition loop
        for index in range(len(ipText)):
            argumentString = "No Args Selected"
            correspond = False
            
            for previousIndex in range(len(self.IPS)):
                
                #the type of the robot already exist and has some arguments
                if typeText[index] == self.TYPES[previousIndex] and self.DICT_TYPES[self.TYPES[previousIndex]][2][0] != "No Args Selected" and not correspond:
                    argumentStringExample = self.DICT_TYPES[self.TYPES[previousIndex]][2][0]
                    numberOfArgument = len(argumentStringExample.split("|"))
                    argumentString = ''
                    
                    #Keep adding arguments for this type until it matches the standard for its type
                    for argumentIndex in range(numberOfArgument):
                        if argumentIndex != numberOfArgument -1:
                            argumentString += "$"+str(argumentIndex)+":|"
                        else:
                            argumentString += "$" +str(argumentIndex) + ":"
                
                #this robot already exist and has some arguments
                if ipText[index] == self.IPS[previousIndex] and nameText[index] == self.USERS[previousIndex] and typeText[index] == self.TYPES[previousIndex]:
                    for indexIPFromDict, IP in enumerate(self.DICT_TYPES[self.TYPES[previousIndex]][0]):
                        if ipText[index] == IP:
                            indexInDict = indexIPFromDict
                    argumentString = self.DICT_TYPES[self.TYPES[previousIndex]][2][indexInDict].replace("#",":")
                    correspond = True

            #Add the completed robot to the text fields in the Main Window
            self.robotTable.insertRow(index)

            tempCheckBox = QtWidgets.QTableWidgetItem()
            tempCheckBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            tempCheckBox.setCheckState(QtCore.Qt.Unchecked)
            if enableText[index] == "True":
                tempCheckBox.setCheckState(QtCore.Qt.Checked)
            else:
                tempCheckBox.setCheckState(QtCore.Qt.Unchecked)

            self.robotTable.setItem(index, 0, QtWidgets.QTableWidgetItem(tempCheckBox))
            self.robotTable.setItem(index, 1, QtWidgets.QTableWidgetItem(ipText[index]))
            self.robotTable.setItem(index, 2, QtWidgets.QTableWidgetItem(nameText[index]))
            self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(typeText[index]))
            tempCombo = QtWidgets.QComboBox()
            argLines = argumentString.split("|")
            tempCombo.addItems(argLines)
            self.robotTable.setCellWidget(index, 4, tempCombo)
            self.robotTable.setItem(index, 5, QtWidgets.QTableWidgetItem("Unknown"))

        #Update the dictionary
        self.updateLists()
        self.flushCommand()

        # Checks to see if the current number of listed robots exceeds the set maximum
        self.checkMaxSSH(len(self.IPS))


    #Opens an Adjust Argument Window for the user to load into the listed robots
    def adjustArgsWindow(self):
        if self.threadStillRunning == 'no':
            self.updateLists()
            self.argsdialog = Adjust_Arguments(self.IPS, self.DICT_TYPES)
            self.argsdialog.save_args.connect(self.write_new_args)
            self.argsdialog.show()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "warning", self.threadStillRunning)


    #Appends the list of arguments to the argumentlist text field
    @QtCore.pyqtSlot(list)
    def write_new_args(self, argsResumeList):

        for index, x in enumerate(argsResumeList):
            self.robotTable.cellWidget(index, 4).clear()
            argLines = x.split("|")
            self.robotTable.cellWidget(index, 4).addItems(argLines)


    #Takes the data from the text fields in the Main Window and loads them into the backend data structures for processing
    def updateLists(self):

        try:
            #Clearing backend data structures
            self.IPS = []
            self.USERS = []
            self.TYPES = []
            self.DICT_TYPES = {}
            self.CONNECTION_STATUS = []
            self.ARGS = []
            self.ENABLE = []

            #Populate backend lists
            self.IPS = self.makeListFromTable("robotaddresslist")
            self.USERS = self.makeListFromTable("robotnamelist")
            self.TYPES = self.makeListFromTable("robottypelist")
            self.CONNECTION_STATUS = self.makeListFromTable("connectionstatuslist")
            self.ARGS = self.makeListFromTable("argumentlist")
            self.ENABLE = self.makeListFromTable("enablelist")

            #Load the data
            for x in range(len(self.IPS)):

                #If the robot's type already exists in the dictionary
                if self.TYPES[x] in self.DICT_TYPES.keys():
                    self.DICT_TYPES[self.TYPES[x]][0].append(self.IPS[x])
                    self.DICT_TYPES[self.TYPES[x]][1].append(self.USERS[x])
                    self.DICT_TYPES[self.TYPES[x]][2].append(self.ARGS[x].replace(":","#"))
                
                #If the robot's type does not already exist in the dictionary
                else:
                    self.DICT_TYPES[self.TYPES[x]] = [[],[],[]]
                    self.DICT_TYPES[self.TYPES[x]][0].append(self.IPS[x])
                    self.DICT_TYPES[self.TYPES[x]][1].append(self.USERS[x])
                    self.DICT_TYPES[self.TYPES[x]][2].append(self.ARGS[x].replace(":","#"))

            #Updates the "Type" combo box in the File Transfer section whenever there is a new type of robot listed
            for combo in self.comboRobotTypeList:
                text = combo.currentText()

                combo.clear()
                combo.addItems(self.DICT_TYPES.keys())
                if text in self.DICT_TYPES.keys():
                    index = combo.findText(text)
                    combo.setCurrentIndex(index)

            #Checks to see if the application should allow the other functions to be active or not
            self.setLaunchEnable(self.checkConnectionAvailable())

        except:
            e = sys.exc_info()[0]
            print( "UpdateLists Error: %s" % e )


    #Sets the maximum number of concurrent SSH sessions based on the user's MaxSessions variable in sshd_config
    def setMaxSSH(self):

        #Open the file and search for the MaxSessions variable
        actualFileName = "/etc/ssh/sshd_config"
        rFile = open(actualFileName, "rU")
        listOfLines = rFile.readlines()
        for line in listOfLines:
            if "MaxSessions" in line:
                temp = line.split(" ")[1].strip()
                return temp
            
        #If the MaxSessions variable was not found return the default number of sessions
        return 10


    #Checks to see if the user is trying to connect to more robots than there sshd_config file will allow
    def checkMaxSSH(self, numOfIPS):
        if numOfIPS > int(self.maxSSH):
            message = "Your list of robots has exceeded your maximum number of concurrent SSH connections." \
                      "\nPlease update your ssh configuration file at:\n/etc/ssh/sshd_config\nand add or update" \
                      " the line: MaxSessions\nto your required number of robots." \
                      "\nCurrent Maximum: "+str(self.maxSSH)+"\nNeeded Maximum: "+str(numOfIPS)
            temp = QtWidgets.QMessageBox.warning(self, "Warning", message)


    #Checks to see if all listed robots have been found by the user's computer
    def checkConnectionAvailable(self):
        connection_available = True
        if self.robotTable.rowCount() == 0:
            connection_available = False
        for status in self.CONNECTION_STATUS:
            if status != "Found":
                connection_available = False

        return connection_available


    #Unlocks several functions after all listed robots have been found
    def setLaunchEnable(self, available):
        self.tabCommands.setEnabled(available)
        self.savecommandsbutton.setEnabled(available)
        self.loadcommandsbutton.setEnabled(available)
        self.launchbutton.setEnabled(available)
        self.buttontransfer.setEnabled(available)
        self.bashrcbutton.setEnabled(available)
        self.argumentbutton.setEnabled(available)
        self.rsacheckbox.setEnabled(available)
        self.spinpackage.setEnabled(available)
        self.lineUsername.setEnabled(available)
        self.linePasswordn.setEnabled(available)
        self.masteruriline.setEnabled(available)
        self.findRSAButton.setEnabled(available)
        self.rsaPath.setEnabled(available)
        self.childLaunchWindow.lineDebugCommand.setEnabled(True)


    #Flushes the tabbed command terminal in the Main Window
    def flushCommand(self):

        while self.tabCommands.count() != 0:
            obj = self.plaintextCommandDict[self.tabCommands.tabText(0)]
            obj.deleteLater()
            obj = self.layoutCommandList.pop(0)
            obj.deleteLater()
            obj = self.widgetCommandList.pop(0)
            obj.deleteLater()
            self.tabCommands.removeTab(0)
        self.plaintextCommandDict.clear()

        for rType in self.DICT_TYPES.keys():
            tempLayout = QtWidgets.QVBoxLayout()
            tempWidget = QtWidgets.QWidget()
            tempCommand = QtWidgets.QPlainTextEdit()
            tempLayout.addWidget(tempCommand, 0)
            tempWidget.setLayout(tempLayout)
            self.widgetCommandList.append(tempWidget)
            self.layoutCommandList.append(tempLayout)
            self.plaintextCommandDict[rType] = tempCommand
            self.tabCommands.addTab(tempWidget, rType)


    #Load data from a .csv or .txt file separated by commas (,)
    def browseForFile(self):
        if self.threadStillRunning == 'no':

            #Open a dialog box where the user can select an existing file
            filePath = QtWidgets.QFileDialog.getOpenFileName(self,"Find your Robotlist file", filter = "csv (*.csv *.)")

            #Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]
            if self.STRINGOFPATH:
                partsOfPath = self.STRINGOFPATH.split("/")
                actualFileName = partsOfPath[-1]

                #Clear the text fields
                self.robotTable.setRowCount(0)

                #Open the file and display the file name in the "selectedfilename" label
                self.selectedfilename.setText("Current File: "+actualFileName)
                robots = open(self.STRINGOFPATH, "rU")

                try:

                    #Get the first line
                    line = robots.readline().split(",")

                    #Until a blank line or EOF is encountered
                    index = 0
                    while line[0] != '':

                        if line[0] !="\n":

                            #Add the basic robot data
                            self.robotTable.insertRow(index)

                            tempCheckBox = QtWidgets.QTableWidgetItem()
                            tempCheckBox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                            tempCheckBox.setCheckState(QtCore.Qt.Unchecked)
                            if line[0] == "True":
                                tempCheckBox.setCheckState(QtCore.Qt.Checked)

                            self.robotTable.setItem(index, 0, QtWidgets.QTableWidgetItem(tempCheckBox))
                            self.robotTable.setItem(index, 1, QtWidgets.QTableWidgetItem(line[1]))
                            self.robotTable.setItem(index, 2, QtWidgets.QTableWidgetItem(line[2]))

                            tempCombo = QtWidgets.QComboBox()

                            #If arguments were not saved with this robot
                            if len(line) == 4:
                                self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(line[3].strip()))
                                tempCombo.addItem("No Args Selected")
                                self.robotTable.setCellWidget(index, 4, tempCombo)

                            #If arguments were saved with this robot
                            else:
                                self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(line[3]))

                                argLines = line[4].strip().split("|")
                                tempCombo.addItems(argLines)

                                self.robotTable.setCellWidget(index, 4, tempCombo)

                            self.robotTable.setItem(index, 5, QtWidgets.QTableWidgetItem("Unknown"))

                            #Get the next line
                            line = robots.readline().split(",")

                        else:

                            #Get the next line
                            line = robots.readline().split(",")
                        index += 1

                except:
                    e = sys.exc_info()[0]
                    print( "Browsing File Error: %s" % e )
                robots.close()

            self.updateLists()
            self.flushCommand()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)

        # Checks to see if the current number of listed robots exceeds the set maximum
        self.checkMaxSSH(self.robotTable.rowCount())


    #Save the current data from the Main Window's text fields to a .csv file
    def saveToFile(self):

        #If there is data to be saved
        if self.saveFileAndPingCheck():

            filePath = QtWidgets.QFileDialog.getSaveFileName(self,"Choose a name for your file", filter = "csv (*.csv *.)")

            try:
                #Test to see if the user selected a valid path or canceled
                self.STRINGOFPATH = filePath[0]
                if self.STRINGOFPATH:
                    partsOfPath = self.STRINGOFPATH.split("/")
                    actualFileName = partsOfPath[-1]

                    #If the user is overwriting an existing .csv file
                    if actualFileName[-1] == "v":
                        rFile = open(self.STRINGOFPATH, "w")

                    #If the user is making a new .csv file
                    else:
                        rFile = open(self.STRINGOFPATH+".csv", "w")

                    self.updateLists()

                    #Append to the file bases on if the robot is saved with arguments or not
                    for x in range(len(self.IPS)):

                        #If the robot has arguments to be saved with
                        if self.ARGS[x] != "No Args Selected":
                            rFile.write(self.ENABLE[x]+","+self.IPS[x]+","+self.USERS[x]+","+self.TYPES[x]+","+self.ARGS[x] +"\n")

                        #If the robot does not have arguments to be saved with
                        else:
                            rFile.write(self.ENABLE[x]+","+self.IPS[x] + "," + self.USERS[x] + "," + self.TYPES[x]+"\n")
                rFile.close()

            except:
                e = sys.exc_info()[0]
                print("Save to File Error: %s" % e)


    #Save the current list of commands from the Command Editor text field to a .txt file
    def saveCurrentCommand(self):

        #If there is data to be saved
        if self.saveCommandCheck():

            filePath = QtWidgets.QFileDialog.getSaveFileName(self,"Choose a name for your file", filter = "txt (*.txt *.)")
            try:

                #Test to see if the user selected a valid path or canceled
                self.STRINGOFPATH = filePath[0]
                if self.STRINGOFPATH:
                    partsOfPath = self.STRINGOFPATH.split("/")
                    actualFileName = partsOfPath[-1]

                    #If the user is overwriting an existing .txt file
                    if actualFileName[-1] == "t":
                        rFile = open(self.STRINGOFPATH, "w")

                    #If the user is making a new .csv file
                    else:
                        rFile = open(self.STRINGOFPATH + ".txt", "w")

                    plaintext = self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())]
                    rFile.write(str(plaintext.toPlainText()))
                rFile.close()
            except:
                e = sys.exc_info()[0]
                print("Save Command to File Error: %s" % e)


    #Loads commands into the Command Editor text field from a .txt file
    def loadCurrentCommand(self):

        #Clear the tabs
        self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].clear()

        #Prompt the user for a file selection
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Find your command file", filter = "txt (*.txt *.)")
        try:

            # Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]
            if self.STRINGOFPATH:
                partsOfPath = self.STRINGOFPATH.split("/")
                actualFileName = partsOfPath[-1]
                self.commandFileLable.setText("Current File: "+actualFileName)


                rFile = open(self.STRINGOFPATH, "rU")
                listOfLines = rFile.readlines()
                plaintext = self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())]

                #Load the commands into the tab
                lines = ''
                for line in listOfLines:
                    if "RSA" in line:
                        path = line[4:]
                        print(path)
                        #self.findRSA(path)
                    else:
                        lines += line
                plaintext.appendPlainText(lines)
            rFile.close()
        except:
            e = sys.exc_info()[0]
            print("Load Command Error: %s" % e)


    #Checks to see if there is robot data to save or ping
    def saveFileAndPingCheck(self):

        #If there is data
        if self.robotTable.rowCount() != 0:
            return True

        #If there is no data
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No robot data found")
            return False


    #Checks to see if there is robot data to save or ping
    def saveCommandCheck(self):
        text = self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].toPlainText()

        # If there is data
        if text != "":
            return True

        # If there is no data
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No command data found in current tab")
            return False


    #Updates the File Transfer section when the user changes the number of packages to transfer
    def reloadPackage(self):

        #Clears the File Transfer section
        while self.linePathParentPackage != []:
            obj = self.linePathParentPackage.pop(0)
            obj.deleteLater()
        while self.linePathGitRepoList != []:
            obj = self.linePathGitRepoList.pop(0)
            obj.deleteLater()
        while self.comboRobotTypeList != []:
            obj = self.comboRobotTypeList.pop(0)
            obj.deleteLater()
        while self.buttonDirectoryPackageList != []:
            obj = self.buttonDirectoryPackageList.pop(0)
            obj.deleteLater()
        while self.comboMakeList != []:
            obj = self.comboMakeList.pop(0)
            obj.deleteLater()

        #Adds widgets to the File Transfer section based on the number of packages listed in the spinbox
        for i in range(self.spinpackage.value()):
            tempPackageWidget = QtWidgets.QLineEdit()
            tempGitRepoWidget = QtWidgets.QLineEdit()
            tempRobotTypeWidget = QtWidgets.QComboBox()
            tempMakeWidget = QtWidgets.QComboBox()
            tempMakeWidget.addItems(["no make", "catkin_make", "catkin_build"])
            typeNames = []
            for typeName in self.TYPES:
                if typeName not in typeNames:
                    typeNames.append(typeName)
            tempRobotTypeWidget.addItems(typeNames)
            tempPackageDirectoryWidget = QtWidgets.QPushButton()
            tempPackageDirectoryWidget.setText("Parent Package Directory")
            tempPackageDirectoryWidget.clicked.connect(lambda state, arg = i:self.specifyPackagePath(arg))
            self.linePathParentPackage.append(tempPackageWidget)
            self.linePathGitRepoList.append(tempGitRepoWidget)
            self.comboRobotTypeList.append(tempRobotTypeWidget)
            self.buttonDirectoryPackageList.append(tempPackageDirectoryWidget)
            self.comboMakeList.append(tempMakeWidget)
            self.gridpackage.addWidget(tempPackageDirectoryWidget, i, 0)
            self.gridpackage.addWidget(tempPackageWidget, i, 1)
            self.gridpackage.addWidget(tempGitRepoWidget, i, 2)
            self.gridpackage.addWidget(tempRobotTypeWidget, i, 3)
            self.gridpackage.addWidget(tempMakeWidget, i, 4)
            self.gridpackage.setColumnStretch(0,1)
            self.gridpackage.setColumnStretch(1,1)
            self.gridpackage.setColumnStretch(2,1)
            self.gridpackage.setColumnStretch(3,1)
            self.gridpackage.setColumnStretch(4,1)


    #Creates the specified package path for cloning the remote repos
    def specifyPackagePath(self, n):
        tempDirectoryPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Specify the Package Directory")

        print tempDirectoryPath
        self.STRINGOFPATH = tempDirectoryPath[0]

        if self.STRINGOFPATH:
            lastPartDirectoryPath = tempDirectoryPath.split('/')[3:]
            directoryPath = "~/"

            print directoryPath

            for i in range(len(lastPartDirectoryPath)):
                directoryPath = directoryPath + lastPartDirectoryPath[i] + "/"

                print directoryPath

            self.linePathParentPackage[n].setText(directoryPath)


    #Handler function to launch one or more threads that perform git commands
    def gitCopyRepo(self):
        self.checkPasswordLaunchThread("git")


    #Handler function to launch one or more threads that perform launch commands
    def launchCommands(self):
        self.checkPasswordLaunchThread("commands")


    #Handler function to launch one or more threads that perform ping commands
    def pingTest(self):

        #If there is data to ping
        if self.saveFileAndPingCheck():
            self.checkPasswordLaunchThread("ping")


    #Handler function to launch one or more threads that perform commands to update the .bashrc file
    def updateBashrc(self):
        self.checkPasswordLaunchThread("bashrc")


    #Sets flags bases on the type of thread to be run and if the RSA checkbox is selected
    def checkPasswordLaunchThread(self, commandType):
        self.updateLists()

        #If the ping button was pushed
        if commandType == "ping":
                self.launchThread(commandType,"rsa")

        #If the rsacheckbox is selected
        elif self.rsacheckbox.isChecked():

            #If the proper RSA key is present on the user's machine at: ~/.ssh
            if self.RSA:
                self.launchThread(commandType,"rsa")

            #The user does not have a correct RSA created on their machine
            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                                     "RSA Key not found")

        #If the command is to be executed via password logins
        else:
            self.passwordWindow = Password_Window(self.IPS,self.USERS,commandType)
            self.passwordWindow.savePasswords.connect(self.update_password)
            self.passwordWindow.show()
            self.passwordWindow.key.connect(self.rsaConfirm)


    #Saves the entered passwords from the password window to the backend data structure
    @QtCore.pyqtSlot(list,str)
    def update_password(self, passwordList, commandType):
        self.PASSWORDS = []
        self.PASSWORDS = passwordList[:]
        self.launchThread(commandType, "password")


    #Create and launch one or more threads to do different commands
    def launchThread(self, threadType, passwordType):
        self.updateLists()
        self.ERRORTEXT = ""
        try:
            
            #If there are no currently running threads
            if self.threadStillRunning == 'no':
                self.refreshLaunchWindow()
                
                #If the user is transferring files to multiple robots
                if threadType == "git":
                    for index in range(len(self.IPS)):
                        threadGitRepoList = []
                        threadPackageList = []
                        threadMakeOptionList = []
                        for i in range(self.spinpackage.value()):
                            if self.TYPES[index] == str(self.comboRobotTypeList[i].currentText()):
                                threadGitRepoList.append(str(self.linePathGitRepoList[i].text()))
                                threadPackageList.append(str(self.linePathParentPackage[i].text()))
                                threadMakeOptionList.append(self.comboMakeList[i].currentIndex())

                        tempThread = QtCore.QThread()
                        tempThread.start()

                        #RSA checkbox test 
                        if passwordType == "password":
                            worker = SSH_Transfer_File_Worker(index,self.IPS[index], self.USERS[index], threadPackageList, threadGitRepoList,
                                                           str(self.lineUsername.text()), str(self.linePasswordn.text()),
                                                           threadMakeOptionList,self.PASSWORDS[index], self.myKey)
                        elif passwordType == "rsa":
                            worker = SSH_Transfer_File_Worker(index, self.IPS[index], self.USERS[index],
                                                           threadPackageList, threadGitRepoList,
                                                           str(self.lineUsername.text()), str(self.linePasswordn.text()),
                                                           threadMakeOptionList, None, self.myKey)
                        
                        #Create the worker
                        worker.terminalSignal.connect(self.writeInOwnedTerminal)
                        worker.finishThread.connect(self.killthread)
                        worker.moveToThread(tempThread)
                        worker.start.emit()
                        self.workerList[index] = worker
                        self.threadList[index] = tempThread
                    self.threadStillRunning = 'Git repository synchronisation still running'
                
                #If the user is launching commands
                elif threadType == "commands":
                    for index in range(len(self.IPS)):

                        tempThread = QtCore.QThread()
                        tempThread.start()

                        commandLinesList = str(self.plaintextCommandDict[self.TYPES[index]].toPlainText()).split("\n")
                        commandLinesList.append("\n")

                        #replacing the arguments in command lines
                        commandLinesArgsList = []
                        for line in commandLinesList:
                            for ipIndex, IP_Type in enumerate(self.DICT_TYPES[self.TYPES[index]][0]):
                                if IP_Type == self.IPS[index]:
                                    ipIndexInDict = ipIndex
                            argumentsString = self.DICT_TYPES[self.TYPES[index]][2][ipIndexInDict]
                            argumentsList = argumentsString.split("|")
                            if argumentsList[0] != "No Args Selected":
                                newReplacedLine = line
                                for arguments in reversed(argumentsList):
                                    tempArgument = arguments.replace('#', ':')
                                    newReplacedLine = newReplacedLine.replace(tempArgument.split(':')[0],
                                                                              ':'.join(tempArgument.split(':')[1:]))
                                commandLinesArgsList.append(newReplacedLine)
                            else:
                                commandLinesArgsList.append(line)
                                
                        #RSA checkbox test 
                        if passwordType == "password":
                            worker = Launch_Worker(index, self.IPS[index], self.USERS[index], commandLinesArgsList,
                                                   self.PASSWORDS[index], self.myKey)
                        elif passwordType == "rsa":
                            worker = Launch_Worker(index, self.IPS[index], self.USERS[index], commandLinesArgsList,
                                                   None, self.myKey)

                        #Create the worker
                        worker.terminalSignal.connect(self.writeInOwnedTerminal)
                        worker.finishThread.connect(self.killthread)
                        worker.moveToThread(tempThread)
                        worker.start.emit()
                        self.workerList[index] = worker
                        self.threadList[index] = tempThread
                    self.threadStillRunning = 'Launch files still running'

                #If the user is pinging the listed robots
                elif threadType == "ping":
                    self.childLaunchWindow.lineDebugCommand.setEnabled(False)
                    for index in range(len(self.IPS)):
                        tempThread = QtCore.QThread()
                        tempThread.start()
                        
                        #Create the worker
                        worker = Ping_Worker(index, self.IPS[index])
                        worker.pingSignal.connect(self.pingWriteInOwnedTerminal)
                        worker.finishThread.connect(self.killthread)
                        worker.moveToThread(tempThread)
                        worker.start.emit()
                        self.workerList[index] = worker
                        self.threadList[index] = tempThread
                    self.threadStillRunning = 'Pings still running'

                #If the user is updating the .bashrc files of the listed robots
                elif threadType == "bashrc":
                    for index in range(len(self.IPS)):
                        tempThread = QtCore.QThread()
                        tempThread.start()
                        
                        #RSA checkbox test 
                        if passwordType == "password":
                            worker = Bashrc_Worker(index, self.IPS[index], self.USERS[index], str(self.masteruriline.text().strip()),self.PASSWORDS[index], self.myKey)
                        elif passwordType == "rsa":
                            worker = Bashrc_Worker(index, self.IPS[index], self.USERS[index], str(self.masteruriline.text().strip()), None, self.myKey)

                        #Create the worker
                        worker.finishThread.connect(self.killthread)
                        worker.terminalSignal.connect(self.writeInOwnedTerminal)
                        worker.moveToThread(tempThread)
                        worker.start.emit()
                        self.workerList[index] = worker
                        self.threadList[index] = tempThread
                    self.threadStillRunning = 'Bashrc still running'

            #If a previous set of threads have not finished running
            else:
                temp = QtWidgets.QMessageBox.warning(self,"Warning", self.threadStillRunning)

            self.childLaunchWindow.show()

        except paramiko.AuthenticationException:
            temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                         "Failed to connect to robot(s), please check your data and passwords")


    #Cleans the Launch Window of previous data and prepares new tabs for the new list of robots
    def refreshLaunchWindow(self):
        while self.childLaunchWindow.tab_Launch.count() != 0:
            self.childLaunchWindow.tab_Launch.removeTab(0)
            try:
                obj = self.terminalList.pop(0)
                obj.deleteLater()
                obj = self.layoutTerminalList.pop(0)
                obj.deleteLater()
                obj = self.widgetTerminalList.pop(0)
                obj.deleteLater()
            except:
                pass

        for index, IP in enumerate(self.IPS):
            tempLayout = QtWidgets.QVBoxLayout()
            tempWidget = QtWidgets.QWidget()
            temp_terminal = QtWidgets.QPlainTextEdit()
            temp_terminal.setReadOnly(True)
            tempLayout.addWidget(temp_terminal, 0)
            tempWidget.setLayout(tempLayout)
            self.widgetTerminalList.append(tempWidget)
            self.layoutTerminalList.append(tempLayout)
            self.terminalList.append(temp_terminal)
            self.childLaunchWindow.tab_Launch.addTab(tempWidget, str(IP))


    #Allows the user to send commands to the remote robots for unexpected requests of authorization and y/n checks
    def sendDebugCommand(self):
        debugCommand = self.childLaunchWindow.lineDebugCommand.text().strip()
        self.childLaunchWindow.lineDebugCommand.clear()
        IP_text = str(self.childLaunchWindow.tab_Launch.tabText(self.childLaunchWindow.tab_Launch.currentIndex()))
        if "Finished" not in IP_text:
            IP_key = self.IPS.index(IP_text)
            self.workerList[IP_key].channel.send(debugCommand + "\n")


    #Visually updates the Launch Window tabs to display feedback from the robots
    @QtCore.pyqtSlot(int, str)
    def writeInOwnedTerminal(self, ipIndex, data):
        self.terminalList[ipIndex].appendPlainText(data)


    #Visually updates the Launch Window tabs to display feedback from pinging the robots
    @QtCore.pyqtSlot(int, str, int)
    def pingWriteInOwnedTerminal(self, ipIndex, data, ping_result):
        try:
            self.terminalList[ipIndex].appendPlainText(data)
            if ping_result == 0:
                self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Found"))
            else:
                self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Not Found"))
            self.updateLists()
        except:
            e = sys.exc_info()[0]
            print( "Ping Error: %s" % e )


    #Terminates the calling thread
    @QtCore.pyqtSlot(int, str)
    def killthread(self, ipIndex, eMessage):
        
        #Append a failed terminal's error string to the master error string
        if eMessage != "":
            self.ERRORTEXT += "\n"+eMessage +"\n"

        del self.workerList[ipIndex]
        self.threadList[ipIndex].quit()
        self.threadList[ipIndex].wait()
        del self.threadList[ipIndex]
        self.childLaunchWindow.tab_Launch.setTabText(ipIndex, self.IPS[ipIndex]+" (Finished)")
        
        #Display the finish message box based on the threads that were running
        if self.workerList == {} and self.threadList == {}:
            if self.threadStillRunning == 'Bashrc still running':
                temp = QtWidgets.QMessageBox.information(self, "Information", "Bashrc Update Finished\n"+self.ERRORTEXT)
            elif self.threadStillRunning == 'Pings still running':
                self.setLaunchEnable(self.checkConnectionAvailable())
                temp = QtWidgets.QMessageBox.information(self, "Information", "Ping Test Finished\n"+self.ERRORTEXT)
            elif self.threadStillRunning == 'Git repository synchronisation still running':
                temp = QtWidgets.QMessageBox.information(self, "Information", "Git Repo Cloning Finished\n"+self.ERRORTEXT)
            elif self.threadStillRunning == 'Launch files still running':
                temp = QtWidgets.QMessageBox.information(self, "Information", "Finished Executing Commands\n"+self.ERRORTEXT)
            self.childLaunchWindow.show()
            self.threadStillRunning = 'no'
        self.updateLists()


    #Checks to see if there is a valid RSA key set, returns True or False
    def rsaCheck(self):

        #RSA Key made through the application
        if os.path.exists(os.path.expanduser('~/.ssh/multikey')):
            privateKeyFile = os.path.expanduser('~/.ssh/multikey')
            self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)
            self.rsaPath.setText('~/.ssh/multikey')
            return True

        #No RSA key found in command file or in default location
        else:
            return False


    #Helper function to catch the signal generated by successfully generating a new RSA key
    @QtCore.pyqtSlot(int)
    def rsaConfirm(self, value):
        self.RSA = value
        privateKeyFile = os.path.expanduser('~/.ssh/multikey')
        self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)


    #Opens a dialog to allow the user to specify their perfered RSA Key
    def findRSA(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Find your RSA Key")
        try:
            print(filePath)
            # Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]

            if self.STRINGOFPATH:

                #RSA key that the User pointed to manually or through a command file
                if os.path.exists(os.path.expanduser(self.STRINGOFPATH)):
                    privateKeyFile = os.path.expanduser(self.STRINGOFPATH)
                    self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)
                    self.rsaPath.setText(self.STRINGOFPATH)
                    self.RSA = True

        except:
            e = sys.exc_info()[0]
            print("Find RSA Error: %s" % e)


    #Interrupts any currently running threads
    def interruptRemainingThreads(self):
        for workerKey in self.workerList.keys():

            self.workerList[workerKey].stopSignal = True
            if self.threadStillRunning == 'git repository synchronisation still running' or self.threadStillRunning == 'bashrc still running' or self.threadStillRunning == 'Launch files still running':
                try:
                    self.workerList[workerKey].channel.send("\x03\n")
                    self.workerList[workerKey].channel.close()

                except:
                    pass


    #Catches all attempts to close the application if there are threads still running
    def closeEvent(self, event):
        self.interruptRemainingThreads()
        canExit = False
        if self.workerList == {} and self.threadList == {}:
            canExit = True
        if canExit:
            event.accept()  # let the window close
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning + "\n the threads are shutting down, just wait a little bit and try one more time!")
            event.ignore()


#Creates and runs the Main Window
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Multilaunch()
    form.showMaximized()
    app.exec_()


#Calls main
if __name__ == '__main__':
    main()
