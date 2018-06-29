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
from Workers import SSH_Transfer_File_Worker, Bashrc_Worker, Launch_Worker, Ping_Worker, ROSMASTER_Worker
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
        self.masterSetEnable = False
        self.maxSSHIgnore = False

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
        self.launchTypeButton.clicked.connect(self.launchThisType)
        self.launchMasterButton.clicked.connect(self.launchMaster)

        #Backend data structures used for processing user input throughout the application
        self.IPS = []
        self.USERS = []
        self.TYPES = []
        self.MASTER_TYPE = []
        self.DICT_TYPES = {}
        self.CONNECTION_STATUS = []
        self.PASSWORDS = {}
        self.ARGS = []
        self.ENABLE = []
        self.STRINGOFPATH = ""
        self.ERRORTEXT = ""
        self.comboboxMasterList = []
        self.terminalRefreshSeconds = 0.1

        #Creates the Launch Window used in pinging and executing selected commands
        self.childLaunchWindow = Launch_Window()
        self.childLaunchWindow.window = "launch"
        self.childLaunchWindow.buttonStopThread.clicked.connect(lambda state, arg = "launch":self.interruptRemainingThreads(arg))
        self.childLaunchWindow.lineDebugCommand.returnPressed.connect(self.sendDebugCommand)
        self.childLaunchWindow.stopCurrentThread.clicked.connect(lambda state, arg = "launch":self.terminateCurrentThread(arg))
        self.childLaunchWindow.closeThreads.connect(self.termCheck)

        #Data structures for the dynamic launch window
        self.layoutTerminalList = {}
        self.widgetTerminalList = {}
        self.terminalList = {}
        self.threadList = {}
        self.workerList = {}
        self.threadStillRunning = 'no'

        #Creates the Roscore Window used to manage/observe running roscores
        self.childRoscoreWindow = Launch_Window()
        self.childRoscoreWindow.setWindowTitle("ROSCORE Window")
        self.childRoscoreWindow.window = "masters"
        self.childRoscoreWindow.setModal(False)
        self.childRoscoreWindow.buttonStopThread.clicked.connect(lambda state, arg = "masters":self.interruptRemainingThreads(arg))
        self.childRoscoreWindow.lineDebugCommand.hide()
        self.childRoscoreWindow.stopCurrentThread.clicked.connect(lambda state, arg = "masters":self.terminateCurrentThread(arg))
        self.childRoscoreWindow.closeThreads.connect(self.termCheck)

        #Data structures for the dynamic master window
        self.masterLayoutTerminalList = {}
        self.masterWidgetTerminalList = {}
        self.masterTerminalList = {}
        self.masterThreadList = {}
        self.masterWorkerList = {}
        self.masterThreadStillRunning = 'no'

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
        self.resizeEvent(self.setTableSize())


    #Corrects the column header sizes
    def setTableSize(self):
        self.robotTable.setColumnWidth(0, self.width()/7)
        self.robotTable.setColumnWidth(1, self.width()/7)
        self.robotTable.setColumnWidth(2, self.width()/7)
        self.robotTable.setColumnWidth(3, self.width()/7)
        self.robotTable.setColumnWidth(4, self.width()/7)
        self.robotTable.setColumnWidth(5, self.width()/7)
        self.robotTable.setColumnWidth(6, self.width()/7)


    #Calculates the number of enabled robots
    def calcEnable(self):
        num = 0

        for index in self.ENABLE:
            if index == "True":
                num += 1

        return num


    #Calculates the number of enabled robots with "Master" ROS Settings
    def calcMaster(self):
        mType = 0
        if len(self.ENABLE) != 0:
            for index, typeString in enumerate(self.MASTER_TYPE):
                if typeString == "Master" and self.ENABLE[index] == "True":
                    mType += 1
        return mType


    #Calculates the number of enabled robots with "Master and Launch" ROS Settings
    def calcMasterLaunch(self):
        mType = 0
        if len(self.ENABLE) != 0:
            for index, typeString in enumerate(self.MASTER_TYPE):
                if typeString == "Master and Launch" and self.ENABLE[index] == "True":
                    mType += 1
        return mType


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
                self.robotEditDialog.robotTable.setItem(x,4,QtWidgets.QTableWidgetItem(self.MASTER_TYPE[x]))
                self.robotEditDialog.IPS.append(self.IPS[x])


    #Creates lists based on the column requested
    def makeListFromTable(self, listName):
        tempList = []

        try:
            if listName == "enablelist":

                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    if self.robotTable.cellWidget(y,0).checkState() == 2:
                        tempList.append("True")
                    else:
                        tempList.append("False")

            elif listName == "masterlist":

                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    text = ""
                    tempText = self.robotTable.cellWidget(y,6).currentText()
                    if len(tempText.split(":")) == 2 :
                        text = tempText.split(":")[1]
                    elif tempText == "Master" or tempText == "Master and Launch":
                        text = tempText
                    else:
                        text = "No ROS Settings"
                    tempList.append(text)

            elif listName == "argumentlist":

                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    text = ""
                    for index in range(self.robotTable.cellWidget(y, 4).count()):
                        if index != self.robotTable.cellWidget(y, 4).count() - 1:
                            text += self.robotTable.cellWidget(y, 4).itemText(index) + "|"
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


    #Loads the text fields in the Main Window from the Edit Robot Dialog's table
    @QtCore.pyqtSlot(list, list, list, list, list)
    def updateListsFromDialog(self, enableText, ipText, nameText, typeText, masterList):

        #Prevent duplicate/invalid data
        self.robotTable.setRowCount(0)
        tempMasterList = masterList

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
                if typeText[index] == self.TYPES[previousIndex]:

                    if self.DICT_TYPES[self.TYPES[previousIndex]][2][0] != "No Args Selected" and not correspond:
                        argumentStringExample = self.DICT_TYPES[self.TYPES[previousIndex]][2][0]
                        numberOfArgument = len(argumentStringExample.split("|"))
                        argumentString = ''

                        #Keep adding arguments for this type until it matches the standard for its type
                        for argumentIndex in range(numberOfArgument):
                            argString = self.DICT_TYPES[self.TYPES[previousIndex]][2][0].split("|")[argumentIndex].split("#")[0]
                            if argumentIndex != numberOfArgument -1:
                                if len(argString.split("/")) ==2:
                                    argumentString += "$"+str(argumentIndex)+"/"+argString.split("/")[1]+":|"
                                else:
                                    argumentString += "$" + str(argumentIndex) + ":|"
                            else:
                                if len(argString.split("/")) == 2:
                                    argumentString += "$" +str(argumentIndex) +"/"+argString.split("/")[1]+":"
                                else:
                                    argumentString += "$" + str(argumentIndex) + ":"

                #this robot already exist and has some arguments
                if ipText[index] == self.IPS[previousIndex] and typeText[index] == self.TYPES[previousIndex]:

                    for indexIPFromDict, IP in enumerate(self.DICT_TYPES[self.TYPES[previousIndex]][0]):
                        if ipText[index] == IP:
                            indexInDict = indexIPFromDict
                    argumentString = self.DICT_TYPES[self.TYPES[previousIndex]][2][indexInDict].replace("#",":")
                    correspond = True

            #Add the completed robot to the text fields in the Main Window
            self.robotTable.insertRow(index)

            tempCheckBox = QtWidgets.QCheckBox()

            if enableText[index] == "True":
                tempCheckBox.setCheckState(QtCore.Qt.Checked)
            else:
                tempCheckBox.setCheckState(QtCore.Qt.Unchecked)
            tempCheckBox.stateChanged.connect(self.enableWidgetFromCheckbox)
            self.robotTable.setCellWidget(index, 0, tempCheckBox)
            self.robotTable.setItem(index, 1, QtWidgets.QTableWidgetItem(ipText[index]))
            self.robotTable.setItem(index, 2, QtWidgets.QTableWidgetItem(nameText[index]))
            self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(typeText[index]))
            tempCombo = QtWidgets.QComboBox()
            argLines = argumentString.split("|")
            tempCombo.addItems(argLines)
            self.robotTable.setCellWidget(index, 4, tempCombo)
            self.robotTable.setItem(index, 5, QtWidgets.QTableWidgetItem("Unknown"))

        self.IPS = []
        self.IPS = self.makeListFromTable("robotaddresslist")
        self.updateMasterCombobox()

        #Update the dictionary
        self.updateLists()
        self.flushCommand()
        self.updateMasterCombobox()

        for index, string in enumerate(tempMasterList):

            if string in self.IPS:
                string = "Roscore at:" + string
            self.comboboxMasterList[index].setCurrentIndex(self.comboboxMasterList[index].findText(string))


    #Remakes the list of enabled robots every time a checkbox is changed
    def enableWidgetFromCheckbox(self):
        self.ENABLE = self.makeListFromTable("enablelist")
        self.setLaunchEnable(self.checkConnectionAvailable())

        #Sets colors to the robots based on status
        self.colorsTableRows()

        #Checks to see if the current number of enabled robots exceeds the set maximum
        self.checkMaxSSH(self.calcEnable())


    #Colors the rows in the robot-table based on robot status and if the robot is enabled
    def colorsTableRows(self):
        for i, statusEnable, statusFound, master in zip(range(len(self.ENABLE)),self.ENABLE, self.CONNECTION_STATUS, self.MASTER_TYPE):

            #If the computer is communicating to a remote master
            if master != "No ROS Settings" and master != "Master" and master != "Master and Launch":
                indexMasterIP = self.IPS.index(master)

            #The computer is its own master
            else:
                indexMasterIP = i


            if statusEnable == "True" and statusFound == "Found" and ((master == "No ROS Settings" or master == "Master" or master == "Master and Launch") \
                or ((self.MASTER_TYPE[indexMasterIP] == "Master" or self.MASTER_TYPE[indexMasterIP] == "Master and Launch")
                    and (self.ENABLE[indexMasterIP] == "True" and self.CONNECTION_STATUS[indexMasterIP] == "Found"))):

                #Green
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(154, 255, 154)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(154, 255, 154)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(154, 255, 154)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(154, 255, 154)))

                if master == "Master":

                    #Purple
                    self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(138, 43, 226)))
                    self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(138, 43, 226)))
                    self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(138, 43, 226)))
                    self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(138, 43, 226)))

                elif master == "Master and Launch":

                    #Green/Purple
                    gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(200, 200))
                    gradient.setColorAt(0, QtGui.QColor(154, 255, 154))
                    gradient.setColorAt(1, QtGui.QColor(138, 43, 226))

                    self.robotTable.item(i, 1).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 2).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 3).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 5).setBackground(QtGui.QBrush(gradient))

                #If the computer is supposed to be a master of some other computer
                elif self.IPS[i] in self.MASTER_TYPE:

                    #If the other computer is enabled
                    if self.ENABLE[self.MASTER_TYPE.index(self.IPS[i])] == "True":

                        #Yellow
                        self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))

            #If the computer is disabled
            elif statusEnable == "False":

                #Red
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(204, 51, 51)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(204, 51, 51)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(204, 51, 51)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(204, 51, 51)))

            #If the computer is not found or (its master is not enabled or found)
            elif statusFound != "Found" or (self.ENABLE[indexMasterIP] != "True" or self.CONNECTION_STATUS[indexMasterIP] != "Found"):

                #Yellow
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))

            #All other weird cases
            else:
                #Yellow
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))


    #Opens an Adjust Argument Window for the user to load into the listed robots
    def adjustArgsWindow(self):
        if self.threadStillRunning == 'no':
            self.updateLists()
            self.argsdialog = Adjust_Arguments(self.IPS, self.DICT_TYPES)
            self.argsdialog.saveArgs.connect(self.writeNewArgs)
            self.argsdialog.show()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "warning", self.threadStillRunning)


    #Appends the list of arguments to the argumentlist text field
    @QtCore.pyqtSlot(list)
    def writeNewArgs(self, argsResumeList):

        for index, x in enumerate(argsResumeList):
            self.robotTable.cellWidget(index, 4).clear()
            argLines = x.split("|")
            self.robotTable.cellWidget(index, 4).addItems(argLines)


    #Takes the data from the text fields in the Main Window and loads them into the backend data structures for processing
    def updateLists(self):
        self.setTableSize()

        try:
             #Clearing backend data structures
            self.IPS = []
            self.USERS = []
            self.TYPES = []
            self.DICT_TYPES = {}
            self.CONNECTION_STATUS = []
            self.ARGS = []
            self.ENABLE = []
            self.MASTER_TYPE = []

            #Populate backend lists
            self.IPS = self.makeListFromTable("robotaddresslist")
            self.USERS = self.makeListFromTable("robotnamelist")
            self.TYPES = self.makeListFromTable("robottypelist")
            self.CONNECTION_STATUS = self.makeListFromTable("connectionstatuslist")
            self.ARGS = self.makeListFromTable("argumentlist")
            self.ENABLE = self.makeListFromTable("enablelist")
            self.MASTER_TYPE = self.makeListFromTable("masterlist")

            # Checks to see if the application should allow the other functions to be active or not
            self.enableWidgetFromCheckbox()

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
                temp = line.split(" ")[-1].strip()

                return temp
            
        #If the MaxSessions variable was not found return the default number of sessions
        return 10


    #Checks to see if the user is trying to connect to more robots than there sshd_config file will allow
    def checkMaxSSH(self, numOfIPS):

        if numOfIPS != 0 and self.maxSSHIgnore != True:
            mType = self.calcMasterLaunch()
            if (numOfIPS+mType) > int(self.maxSSH):
                self.maxSSHIgnore = True
                message = "Your combined number of enabled robots and \"Master and Launch\" ROS Settings has exceeded your maximum number of concurrent SSH connections." \
                          "\nPlease update your ssh configuration file at:\n/etc/ssh/sshd_config\nand add or update" \
                          " the line:\nMaxSessions "+str((numOfIPS+mType))+"\n" \
                          "\nCurrent Maximum: "+str(self.maxSSH)+"\nNeeded Maximum: "+str((numOfIPS+mType))
                temp = QtWidgets.QMessageBox.warning(self, "Warning", message)


    #Helper function to catch the signal generated by successfully generating a new RSA key
    @QtCore.pyqtSlot(int)
    def rsaConfirm(self, value):
        self.RSA = value
        privateKeyFile = os.path.expanduser('~/.ssh/multikey')
        self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)


    #Opens a dialog to allow the user to specify their preferred RSA Key
    def findRSA(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Find your RSA Key")
        try:

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


    #Checks to see if there is a valid RSA key set, returns True or False
    def rsaCheck(self):

        path = self.rsaPath.text().strip()
        #RSA key that the User pointed to through a command file
        if os.path.exists(os.path.expanduser(path)):
            privateKeyFile = os.path.expanduser(path)
            self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)
            self.RSA = True
            return True

        # RSA Key made through the application
        elif os.path.exists(os.path.expanduser('~/.ssh/multikey')):
            privateKeyFile = os.path.expanduser('~/.ssh/multikey')
            self.myKey = paramiko.RSAKey.from_private_key_file(privateKeyFile)
            self.rsaPath.setText('~/.ssh/multikey')
            return True

        #No RSA key found in command file or in default location
        else:
            self.rsaPath.setText("No RSA Key Found")
            return False


    #Checks to see if all listed robots have been found by the user's computer and checks their ROS status. Returns if the program should allow the user to use more features
    def checkConnectionAvailable(self):
        connectionAvailable = True
        if self.robotTable.rowCount() == 0:
            connectionAvailable = False

        for i, statusEnable,statusFound, master in zip(range(len(self.IPS)),self.ENABLE,self.CONNECTION_STATUS, self.MASTER_TYPE):

            #If this computer is listening to a master
            if master != "No ROS Settings" and master != "Master" and master != "Master and Launch":
                indexMasterIP = self.IPS.index(master)

            #This computer is independent
            else:
                indexMasterIP = i

            #If the computer is enabled
            if statusEnable == "True":

                    #If the computer is not found
                    if statusFound != "Found":
                        connectionAvailable = False

                    #If the computer is bound to a master that is not enabled, found, or set to have valid ROS Settings
                    elif (master != "No ROS Settings" and master != "Master" and master != "Master and Launch") \
                            and ((self.ENABLE[indexMasterIP] != "True" or self.CONNECTION_STATUS[indexMasterIP] != "Found")
                            or (self.MASTER_TYPE[indexMasterIP] != "Master" and self.MASTER_TYPE[indexMasterIP] != "Master and Launch")):
                        connectionAvailable = False

        #If all computers are disabled
        if self.calcEnable() == 0:
            connectionAvailable = False

        return connectionAvailable


    #Locks and unlocks several functions after all enabled robots have been found and have valid ROS Settings
    def setLaunchEnable(self, available):

        if self.masterSetEnable:
            self.robotTable.setEnabled(not available)
            self.editlistsbutton.setEnabled(not available)
            self.pingrobotsbutton.setEnabled(not available)
            self.buttontransfer.setEnabled(not available)
            self.bashrcbutton.setEnabled(not available)
            self.argumentbutton.setEnabled(not available)
            self.rsacheckbox.setEnabled(not available)
            self.spinpackage.setEnabled(not available)
            self.lineUsername.setEnabled(not available)
            self.linePassword.setEnabled(not available)
            self.rsaPath.setEnabled(not available)
            self.launchMasterButton.setEnabled(not available)

        else:
            self.editlistsbutton.setEnabled(True)
            self.pingrobotsbutton.setEnabled(True)
            self.robotTable.setEnabled(True)
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
            self.linePassword.setEnabled(available)
            self.findRSAButton.setEnabled(available)
            self.rsaPath.setEnabled(available)
            self.childLaunchWindow.lineDebugCommand.setEnabled(available)
            self.launchTypeButton.setEnabled(available)
            self.launchMasterButton.setEnabled(available)


    #Returns True if no ROSMasters are needed or if there are masters running when needed, False otherwise
    def checkMastersRunning(self):

        tempList = []
        for index in self.masterWorkerList:
            tempList.append(self.masterWorkerList[index].IP)

        for i, statusEnable, master in zip(range(len(self.IPS)),self.ENABLE, self.MASTER_TYPE):

            #If the computer is enabled and this computer is listening to a master
            if statusEnable == "True" and master != "No ROS Settings" and master != "Master" and master != "Master and Launch":
                indexMasterIP = self.IPS.index(master)
                IP = self.IPS[indexMasterIP]
                if IP not in tempList:
                    return False
        return True


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


    #Updates the master comboboxes when new robots are added or removed
    def updateMasterCombobox(self):
        while self.comboboxMasterList != []:
            obj = self.comboboxMasterList.pop(0)
            obj.deleteLater()

        for currentIndex, currentIp in enumerate(self.IPS):
            tempCombo = QtWidgets.QComboBox()
            tempCombo.addItem("No ROS Settings")
            tempCombo.addItem("Master")
            tempCombo.addItem("Master and Launch")
            for index, ip in enumerate(self.IPS):
                if currentIp != ip:
                    tempCombo.addItem("Roscore at:"+ ip)

            tempCombo.currentIndexChanged.connect(self.checkMasterDependencies)
            self.robotTable.setCellWidget(currentIndex, 6, tempCombo)
            self.comboboxMasterList.append(tempCombo)


    #Remakes the list of rosmasters every time a "ROSMASTER Settings" combobox is changed
    def checkMasterDependencies(self):
        self.MASTER_TYPE = self.makeListFromTable("masterlist")
        self.setLaunchEnable(self.checkConnectionAvailable())
        self.colorsTableRows()

        #Checks to see if the current number of enabled robots with master types exceeds the set maximum
        self.checkMaxSSH(self.calcEnable())


    #Load data from a .csv file separated by commas (,)
    def browseForFile(self):
        if self.threadStillRunning == 'no':
            tempMasterList = []

            # Open a dialog box where the user can select an existing file
            filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Find your Robotlist file", filter="csv (*.csv *.)")

            # Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]
            if self.STRINGOFPATH:
                partsOfPath = self.STRINGOFPATH.split("/")
                actualFileName = partsOfPath[-1]

                # Clear the text fields
                self.robotTable.setRowCount(0)

                # Open the file and display the file name in the "selectedfilename" label
                self.selectedfilename.setText("Current File: " + actualFileName)

                try:
                    rFile = open(self.STRINGOFPATH, "rU")
                    listOfLines = rFile.readlines()
                    index = 0

                    # Until a blank line or EOF is encountered
                    for line in listOfLines:

                        line = line.strip().split(",")

                        if line[0] == "RSA":
                            self.rsaPath.setText(line[1])
                            self.rsaCheck()

                        elif line[0] == "GITUSER":
                            self.lineUsername.setText(line[1])

                        elif line[0] != "" and line[0] != "#####":
                            # Add the basic robot data
                            self.robotTable.insertRow(index)

                            tempCheckBox = QtWidgets.QCheckBox()
                            tempCheckBox.setCheckState(QtCore.Qt.Unchecked)
                            if line[0] == "True":
                                tempCheckBox.setCheckState(QtCore.Qt.Checked)
                            tempCheckBox.stateChanged.connect(self.enableWidgetFromCheckbox)
                            self.robotTable.setCellWidget(index, 0, tempCheckBox)
                            self.robotTable.setItem(index, 1, QtWidgets.QTableWidgetItem(line[1]))
                            self.robotTable.setItem(index, 2, QtWidgets.QTableWidgetItem(line[2]))
                            self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(line[3]))

                            tempCombo = QtWidgets.QComboBox()

                            # If arguments were not saved with this robot
                            if line[4] == "No Args":
                                tempCombo.addItem("No Args Selected")
                                self.robotTable.setCellWidget(index, 4, tempCombo)

                            # If arguments were saved with this robot
                            else:
                                argLines = line[4].strip().split("|")
                                tempCombo.addItems(argLines)
                                self.robotTable.setCellWidget(index, 4, tempCombo)

                            tempMasterList.append(line[5].strip())

                            self.robotTable.setItem(index, 5, QtWidgets.QTableWidgetItem("Unknown"))
                            index += 1

                    rFile.close()

                    self.IPS = []
                    self.IPS = self.makeListFromTable("robotaddresslist")
                    self.updateMasterCombobox()

                    #REDESIGN: self.ENABLE list not updated in time for for-loop
                    self.updateLists()

                    for index, string in enumerate(tempMasterList):

                        if string in self.IPS:
                            string = "Roscore at:"+string
                        self.comboboxMasterList[index].setCurrentIndex(self.comboboxMasterList[index].findText(string))

                    self.updateLists()
                    self.flushCommand()

                except:
                    e = sys.exc_info()[0]
                    print("Browsing File Error: %s" % e)

        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)


    #Save the current data from the Main Window's text fields to a .csv file
    def saveToFile(self):

        #If there is data to be saved
        if self.robotTable.rowCount() != 0:

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

                    if str(self.rsaPath.text()) != "No RSA Key Found":
                        rFile.write("RSA,"+str(self.rsaPath.text())+"\n")

                    if str(self.lineUsername.text()) != "":
                        rFile.write("GITUSER,"+str(self.lineUsername.text())+"\n")

                    rFile.write("#####\n")

                    #Append to the file based on if the robot is saved with arguments or not
                    for x in range(len(self.IPS)):

                        #If the robot has arguments to be saved with
                        if self.ARGS[x] != "No Args Selected":
                            rFile.write(self.ENABLE[x]+","+self.IPS[x]+","+self.USERS[x]+","+self.TYPES[x]+","+self.ARGS[x] +","+ self.MASTER_TYPE[x] +"\n")

                        #If the robot does not have arguments to be saved with
                        else:
                            rFile.write(self.ENABLE[x]+","+self.IPS[x] + "," + self.USERS[x] + "," + self.TYPES[x] + ",No Args," + self.MASTER_TYPE[x] + "\n")
                    rFile.close()

            except:
                e = sys.exc_info()[0]
                print("Save to File Error: %s" % e)

        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No robot data found to save")


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

                    plainText = ""

                    plainText += self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].toPlainText()
                    rFile.write(plainText)
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
                lines = ""

                for line in listOfLines:

                    lines += line
                plaintext.appendPlainText(lines)
                rFile.close()
        except:
            e = sys.exc_info()[0]
            print("Load Command Error: %s" % e)


    #Checks to see if there is robot data to save or ping
    def pingCheck(self):

        allDisabled = False
        numberDisable = 0
        for statusEnable in self.ENABLE:
            if statusEnable == "False":
                numberDisable += 1
        if numberDisable == len(self.ENABLE):
            allDisabled = True

        #If there is data
        if self.robotTable.rowCount() != 0 and allDisabled == False:
            return True

        #If there is no data
        else:
            if self.robotTable.rowCount() == 0:
                QtWidgets.QMessageBox.warning(self, "Warning", "No robot data found")

            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "No robot(s) enabled")

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
            tempGitRepoWidget.setPlaceholderText("Use http:// here")
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

        if tempDirectoryPath:
            tempDirTest = tempDirectoryPath.split('/')

            if tempDirTest[1] == "home":
                directoryPath = "~/"
                lastPartDirectoryPath = tempDirectoryPath.split('/')[3:]

            else:
                directoryPath = "/"
                lastPartDirectoryPath = tempDirectoryPath.split('/')[1:]

            for i in range(len(lastPartDirectoryPath)):
                directoryPath = directoryPath + lastPartDirectoryPath[i] + "/"

            self.linePathParentPackage[n].setText(directoryPath)


    #Handler function to launch one or more threads that perform git commands
    def gitCopyRepo(self):
        self.ERRORTEXT = ""

        if self.spinpackage.value() == 0:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Zero Repositories set")

        else:


            if self.lineUsername.text().strip() == "":
                self.ERRORTEXT += "\nMissing remote Git Username\n"

            if self.linePassword.text().strip() == "":
                self.ERRORTEXT += "\nMissing remote Git Username\n"

            index = 0
            while index < self.spinpackage.value():

                if self.linePathParentPackage[index].text().strip() == "":
                    self.ERRORTEXT += "\nMissing Destination Directory for repository: "+ str(index+1) +"\n"

                if self.linePathGitRepoList[index].text().strip() == "":
                    self.ERRORTEXT += "\nMissing Remote Repository URL for repository: " + str(index+1) +"\n"
                index += 1

            if self.ERRORTEXT == "":
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "Uncommitted changes will be saved using \"git stash\"")
                self.checkPasswordLaunchThread("git")

            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", self.ERRORTEXT)


    #Handler function to launch the rosmasters
    def launchMaster(self):
        if (self.calcMaster()+self.calcMasterLaunch()) == 0:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "No ROS MASTERS have been set/Enabled")
        else:
            self.masterSetEnable = True
            self.checkPasswordLaunchThread("masters")


    #Handler function to launch one or more threads that perform launch commands
    def launchCommands(self):
        if self.checkMastersRunning():
            self.checkPasswordLaunchThread("commands")
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "One or more ROSMASTERs is not running, please close and relaunch the ROSCORE window")


    #Handler function to launch one or more threads that perform launch commands on a single type
    def launchThisType(self):
        if self.checkMastersRunning():
            self.checkPasswordLaunchThread("type")
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "One or more ROSMASTERs is not running, please close and relaunch the ROSCORE window")


    #Handler function to launch one or more threads that perform ping commands
    def pingTest(self):

        #If there is data to ping
        if self.pingCheck():
            self.checkPasswordLaunchThread("ping")


    #Handler function to launch one or more threads that perform commands to update the .bashrc file
    def updateBashrc(self):
        self.checkPasswordLaunchThread("bashrc")


    #Returns a boolean value if the application is running in type only mode
    def currentTabCheck(self, string, index):
        correctType = True
        if string == "type":
            correctType = False
            currentType = self.tabCommands.tabText(self.tabCommands.currentIndex())
            if self.TYPES[index] == currentType:
                correctType = True
        return correctType


    #Sets flags bases on the type of thread to be run and if the RSA checkbox is selected
    def checkPasswordLaunchThread(self, commandType):
        self.updateLists()

        #If the ping button was pushed
        if commandType == "ping" :
                self.launchThread(commandType,"rsa")

        #If the rsacheckbox is selected
        elif self.rsacheckbox.isChecked():

            #If the proper RSA key is present on the user's machine at: ~/.ssh
            if self.RSA:
                if commandType == "masters":
                    self.masterThread("rsa")
                else:
                    self.launchThread(commandType,"rsa")

            #The user does not have a correct RSA created on their machine
            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning","RSA Key not found")

        #If the command is to be executed via password logins
        else:
            enableIPS = []
            enableUSERS = []

            for index, ip, user in zip(range(len(self.IPS)),self.IPS,self.USERS):

                if commandType == "masters":
                    if self.ENABLE[index] == "True" and self.currentTabCheck(commandType,index) and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                        enableIPS.append(ip)
                        enableUSERS.append(user)
                else:
                    if self.ENABLE[index] == "True" and self.currentTabCheck(commandType,index) and self.MASTER_TYPE[index] != "Master":
                        enableIPS.append(ip)
                        enableUSERS.append(user)

            self.passwordWindow = Password_Window(enableIPS,enableUSERS,commandType)
            self.passwordWindow.savePasswords.connect(self.updatePassword)
            self.passwordWindow.exitWindow.connect(self.termCheck)
            self.passwordWindow.show()
            self.passwordWindow.key.connect(self.rsaConfirm)


    #Saves the entered passwords from the password window to the backend data structure
    @QtCore.pyqtSlot(dict,str)
    def updatePassword(self, passwordList, commandType):
        self.PASSWORDS = {}
        self.PASSWORDS = passwordList.copy()

        if commandType == "masters":
            self.masterThread("password")
        else:
            self.launchThread(commandType, "password")


    #Create and launch one or more threads to do different commands
    def launchThread(self, threadType, passwordType):
        self.ERRORTEXT = ""
        try:

            #If there are no currently running threads
            if self.threadStillRunning == 'no':
                self.refreshLaunchWindow(threadType)
                
                #If the user is transferring files to multiple robots
                if threadType == "git":
                    for index in range(len(self.IPS)):
                        if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found":
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
                                                               str(self.lineUsername.text()), str(self.linePassword.text()),
                                                               threadMakeOptionList,self.PASSWORDS[self.IPS[index]], self.myKey)
                            elif passwordType == "rsa":
                                worker = SSH_Transfer_File_Worker(index, self.IPS[index], self.USERS[index],
                                                               threadPackageList, threadGitRepoList,
                                                               str(self.lineUsername.text()), str(self.linePassword.text()),
                                                               threadMakeOptionList, None, self.myKey)

                            #Create the worker
                            worker.terminalSignal.connect(self.writeInOwnedTerminal)
                            worker.finishThread.connect(self.killThread)
                            worker.moveToThread(tempThread)
                            worker.start.emit()
                            self.workerList[index] = worker
                            self.threadList[index] = tempThread
                    self.threadStillRunning = 'Git repository synchronisation still running'
                    self.childLaunchWindow.show()

                #If the user is launching commands
                elif threadType == "commands" or threadType == "type":
                    for index in range(len(self.IPS)):

                        if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and self.currentTabCheck(threadType,index) and self.MASTER_TYPE[index] != "Master":
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

                                        #replace the $variable in  the string
                                        newReplacedLine = newReplacedLine.replace(tempArgument.split(':')[0].split("/")[0],
                                                                                  ':'.join(tempArgument.split(':')[1:]))

                                        #replace the $argument name in the string if there is one
                                        if len(tempArgument.split(':')[0].split("/")) == 2:
                                            newReplacedLine = newReplacedLine.replace("$"+tempArgument.split(':')[0].split("/")[1],':'.join(tempArgument.split(':')[1:]))
                                    commandLinesArgsList.append(newReplacedLine)
                                else:
                                    commandLinesArgsList.append(line)

                            #RSA checkbox test
                            if passwordType == "password":
                                worker = Launch_Worker(index, self.IPS[index], self.USERS[index], commandLinesArgsList,
                                                       self.PASSWORDS[self.IPS[index]], self.myKey)
                            elif passwordType == "rsa":
                                worker = Launch_Worker(index, self.IPS[index], self.USERS[index], commandLinesArgsList,
                                                       None, self.myKey)

                            #Create the worker
                            worker.terminalSignal.connect(self.writeInOwnedTerminal)
                            worker.finishThread.connect(self.killThread)
                            worker.moveToThread(tempThread)
                            worker.start.emit()
                            self.workerList[index] = worker
                            self.threadList[index] = tempThread
                    self.threadStillRunning = 'Launch files still running'
                    self.childLaunchWindow.show()

                #If the user is pinging the listed robots
                elif threadType == "ping":
                    self.childLaunchWindow.lineDebugCommand.setEnabled(False)
                    for index in range(len(self.IPS)):
                        if self.ENABLE[index] == "True":
                            tempThread = QtCore.QThread()
                            tempThread.start()

                            #Create the worker
                            worker = Ping_Worker(index, self.IPS[index])
                            worker.pingSignal.connect(self.pingWriteInOwnedTerminal)
                            worker.finishThread.connect(self.killThread)
                            worker.moveToThread(tempThread)
                            worker.start.emit()
                            self.workerList[index] = worker
                            self.threadList[index] = tempThread
                    self.threadStillRunning = 'Pings still running'
                    self.childLaunchWindow.show()

                #If the user is updating the .bashrc files of the listed robots
                elif threadType == "bashrc":
                    for index in range(len(self.IPS)):
                        if self.ENABLE[index]=="True" and self.CONNECTION_STATUS[index] == "Found" and self.MASTER_TYPE[index] != "":
                            tempThread = QtCore.QThread()
                            tempThread.start()

                            tempMasterString = self.MASTER_TYPE[index]

                            if tempMasterString == "Master" or tempMasterString == "Master and Launch":
                                tempMasterString = self.IPS[index]

                            #RSA checkbox test
                            if passwordType == "password":
                                worker = Bashrc_Worker(index, self.IPS[index], self.USERS[index], tempMasterString,self.PASSWORDS[self.IPS[index]], self.myKey)
                            elif passwordType == "rsa":
                                worker = Bashrc_Worker(index, self.IPS[index], self.USERS[index], tempMasterString, None, self.myKey)

                            #Create the worker
                            worker.finishThread.connect(self.killThread)
                            worker.terminalSignal.connect(self.writeInOwnedTerminal)
                            worker.moveToThread(tempThread)
                            worker.start.emit()
                            self.workerList[index] = worker
                            self.threadList[index] = tempThread
                    self.threadStillRunning = 'Bashrc still running'
                    self.childLaunchWindow.show()

            #If a previous set of threads have not finished running
            else:
                temp = QtWidgets.QMessageBox.warning(self,"Warning", self.threadStillRunning)

        except paramiko.AuthenticationException:
            temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                         "Failed to connect to robot(s), please check your data and passwords")


    #Create and launch one or more threads to run roscore
    def masterThread(self, passwordType):
        self.ERRORTEXT = ""
        try:

            #If there are no currently running threads
            if self.masterThreadStillRunning == 'no':
                self.refreshLaunchWindow("masters")

                for index in range(len(self.IPS)):
                    if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                        tempThread = QtCore.QThread()
                        tempThread.start()

                        # RSA checkbox test
                        if passwordType == "password":
                            worker = ROSMASTER_Worker(index, self.IPS[index], self.USERS[index], self.PASSWORDS[self.IPS[index]], self.myKey)
                        elif passwordType == "rsa":
                            worker = ROSMASTER_Worker(index, self.IPS[index], self.USERS[index], None, self.myKey)

                        #Create the worker
                        worker.finishThread.connect(self.masterKillThread)
                        worker.terminalSignal.connect(self.masterWriteInOwnedTerminal)
                        worker.moveToThread(tempThread)
                        worker.start.emit()
                        self.masterWorkerList[index] = worker
                        self.masterThreadList[index] = tempThread

                self.masterThreadStillRunning = 'Masters still running'
                self.childRoscoreWindow.show()

            #If a previous set of threads have not finished running
            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", self.masterThreadStillRunning)

        except paramiko.AuthenticationException:
            temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                         "Failed to connect to masters(s), please check your data and passwords")


    #Cleans the Launch Window of previous data and prepares new tabs for the new list of robots
    def refreshLaunchWindow(self,commands):

        if commands == "masters":

            while self.childRoscoreWindow.tab_Launch.count() != 0:
                try:
                    obj = self.masterTerminalList.pop(self.IPS.index(str(self.childRoscoreWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                    obj = self.masterLayoutTerminalList.pop(self.IPS.index(str(self.childRoscoreWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                    obj = self.masterWidgetTerminalList.pop(self.IPS.index(str(self.childRoscoreWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                except:
                    pass
                self.childRoscoreWindow.tab_Launch.removeTab(0)

        else:
            while self.childLaunchWindow.tab_Launch.count() != 0:
                try:
                    obj = self.terminalList.pop(self.IPS.index(str(self.childLaunchWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                    obj = self.layoutTerminalList.pop(self.IPS.index(str(self.childLaunchWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                    obj = self.widgetTerminalList.pop(self.IPS.index(str(self.childLaunchWindow.tab_Launch.tabText(0))))
                    obj.deleteLater()
                except:
                    pass
                self.childLaunchWindow.tab_Launch.removeTab(0)


        for index, IP in enumerate(self.IPS):

            if self.ENABLE[index] == "True" and commands == "ping":
                tempLayout = QtWidgets.QVBoxLayout()
                tempWidget = QtWidgets.QWidget()
                tempTerminal = QtWidgets.QPlainTextEdit()
                tempTerminal.setReadOnly(True)
                tempLayout.addWidget(tempTerminal, 0)
                tempWidget.setLayout(tempLayout)
                self.widgetTerminalList[index] = tempWidget
                self.layoutTerminalList[index] = tempLayout
                self.terminalList[index] = tempTerminal
                self.childLaunchWindow.tab_Launch.addTab(tempWidget, str(IP))

            elif self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and commands == "masters" \
                    and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):

                tempLayout = QtWidgets.QVBoxLayout()
                tempWidget = QtWidgets.QWidget()
                tempTerminal = QtWidgets.QPlainTextEdit()
                tempTerminal.setReadOnly(True)
                tempLayout.addWidget(tempTerminal, 0)
                tempWidget.setLayout(tempLayout)
                self.masterWidgetTerminalList[index] = tempWidget
                self.masterLayoutTerminalList[index] = tempLayout
                self.masterTerminalList[index] = tempTerminal
                self.childRoscoreWindow.tab_Launch.addTab(tempWidget, str(IP))


            elif self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and commands != "masters" and self.currentTabCheck(commands,index) and self.MASTER_TYPE[index] != "Master":
                tempLayout = QtWidgets.QVBoxLayout()
                tempWidget = QtWidgets.QWidget()
                tempTerminal = QtWidgets.QPlainTextEdit()
                tempTerminal.setReadOnly(True)
                tempLayout.addWidget(tempTerminal, 0)
                tempWidget.setLayout(tempLayout)
                self.widgetTerminalList[index] = tempWidget
                self.layoutTerminalList[index] = tempLayout
                self.terminalList[index] = tempTerminal
                self.childLaunchWindow.tab_Launch.addTab(tempWidget, str(IP))


    #Allows the user to send commands to the remote robots for unexpected terminal requests
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


    #Visually updates the ROSCORE Window tabs to display feedback from the ROSMASTERS
    @QtCore.pyqtSlot(int, str)
    def masterWriteInOwnedTerminal(self, ipIndex, data):
        self.masterTerminalList[ipIndex].appendPlainText(data)


    #Visually updates the Launch Window tabs to display feedback from pinging the robots
    @QtCore.pyqtSlot(int, str, int)
    def pingWriteInOwnedTerminal(self, ipIndex, data, pingResult):
        try:
            self.terminalList[ipIndex].appendPlainText(data)
            if pingResult == 0:
                self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Found"))
            else:
                self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Not Found"))
            self.updateLists()
        except:
            e = sys.exc_info()[0]
            print( "Ping Error: %s" % e )


    #Terminates the calling thread
    @QtCore.pyqtSlot(int, str)
    def killThread(self, ipIndex, eMessage):
        self.ERRORTEXT = ""

        #Append a failed terminal's error string to the master error string
        if eMessage != "":
            self.ERRORTEXT += "\n"+eMessage +"\n"

        del self.workerList[ipIndex]
        self.threadList[ipIndex].quit()
        self.threadList[ipIndex].wait()
        del self.threadList[ipIndex]

        for index in range(self.childLaunchWindow.tab_Launch.count()):
            if self.childLaunchWindow.tab_Launch.tabText(index) == self.IPS[ipIndex]:
                self.childLaunchWindow.tab_Launch.setTabText(index, self.IPS[ipIndex]+" (Finished)")
        
        #Display the finish message box based on the threads that were running
        if self.workerList == {} and self.threadList == {}:
            if self.threadStillRunning == 'Bashrc still running':
                temp = QtWidgets.QMessageBox.information(self.childLaunchWindow, "Information",
                                                         "Bashrc Update Finished\n" + self.ERRORTEXT)
            elif self.threadStillRunning == 'Pings still running':
                self.setLaunchEnable(self.checkConnectionAvailable())
                temp = QtWidgets.QMessageBox.information(self.childLaunchWindow, "Information", "Ping Test Finished\n" + self.ERRORTEXT)
            elif self.threadStillRunning == 'Git repository synchronisation still running':
                temp = QtWidgets.QMessageBox.information(self.childLaunchWindow, "Information",
                                                         "Git Repo Cloning Finished\n" + self.ERRORTEXT)
            elif self.threadStillRunning == 'Launch files still running':
                temp = QtWidgets.QMessageBox.information(self.childLaunchWindow, "Information",
                                                         "Finished Executing Commands\n" + self.ERRORTEXT)
            self.childLaunchWindow.show()
            self.threadStillRunning = 'no'
        self.updateLists()


    #Terminates the calling thread
    @QtCore.pyqtSlot(int, str)
    def masterKillThread(self, ipIndex, eMessage):
        self.ERRORTEXT = ""

        # Append a failed terminal's error string to the master error string
        if eMessage != "":
            self.ERRORTEXT += "\n" + eMessage + "\n"

        del self.masterWorkerList[ipIndex]
        self.masterThreadList[ipIndex].quit()
        self.masterThreadList[ipIndex].wait()
        del self.masterThreadList[ipIndex]

        for index in range(self.childRoscoreWindow.tab_Launch.count()):
            if self.childRoscoreWindow.tab_Launch.tabText(index) == self.IPS[ipIndex]:
                self.childRoscoreWindow.tab_Launch.setTabText(index, self.IPS[ipIndex] + " (Finished)")

        # Display the finish message box based on the threads that were running
        if self.masterWorkerList == {} and self.masterThreadList == {}:
            temp = QtWidgets.QMessageBox.information(self.childRoscoreWindow, "Information", "ROSCOREs shutdown\n" + self.ERRORTEXT)
            self.childRoscoreWindow.show()
            self.masterThreadStillRunning = 'no'
        self.updateLists()


    #Helper function to interrupt the correct threads
    @QtCore.pyqtSlot(str)
    def termCheck(self, window):
        self.maxSSHIgnore = False
        if window == "launch":
            self.interruptRemainingThreads(window)

        elif window == "masters":
            self.interruptRemainingThreads(window)
            self.masterSetEnable = False
            self.setLaunchEnable(True)

        elif window == "pass" and self.masterSetEnable == True:
            self.masterSetEnable = False
            self.setLaunchEnable(True)


    #Terminates the currently selected tab/thread
    def terminateCurrentThread(self, flag):
        if flag == "masters":
            IP_text = str(self.childRoscoreWindow.tab_Launch.tabText(self.childRoscoreWindow.tab_Launch.currentIndex()))
            if "Finished" not in IP_text:
                workerKey = self.IPS.index(IP_text)
                self.masterWorkerList[workerKey].stopSignal = True
                if self.masterThreadStillRunning == 'Masters still running':
                    try:
                        self.masterWorkerList[workerKey].channel.send("\x03\n")
                        self.masterWorkerList[workerKey].channel.close()
                    except:
                        pass

        else:
            IP_text = str(self.childLaunchWindow.tab_Launch.tabText(self.childLaunchWindow.tab_Launch.currentIndex()))
            if "Finished" not in IP_text:
                workerKey = self.IPS.index(IP_text)
                self.workerList[workerKey].stopSignal = True
                if self.threadStillRunning == 'git repository synchronisation still running' or self.threadStillRunning == 'bashrc still running' or self.threadStillRunning == 'Launch files still running':
                    try:
                        self.workerList[workerKey].channel.send("\x03\n")
                        self.workerList[workerKey].channel.close()
                    except:
                        pass


    #Interrupts any currently running threads
    def interruptRemainingThreads(self, flag):
        if flag == "masters":
            for workerKey in self.masterWorkerList.keys():
                self.masterWorkerList[workerKey].stopSignal = True
                if self.masterThreadStillRunning == 'Masters still running':
                    try:
                        self.masterWorkerList[workerKey].channel.send("\x03\n")
                        self.masterWorkerList[workerKey].channel.close()
                    except:
                        pass

        else:
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
        self.interruptRemainingThreads("launch")
        self.interruptRemainingThreads("masters")

        canExit = False
        if self.workerList == {} and self.threadList == {}:
            canExit = True
        if canExit:
            event.accept()  #let the window close
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning + "\nThe threads are shutting down, just wait a little bit and try one more time!")
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
