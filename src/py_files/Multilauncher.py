#
# File: Multilauncher.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created: Summer 2018
#

from PyQt5 import QtCore, QtGui, QtWidgets
from Adjust_Arguments import Adjust_Arguments
from Password_Window import Password_Window
import MultilauncherDesign
from Launch_Window import Launch_Window
from Workers import SSH_Transfer_File_Worker, Bashrc_Worker, Launch_Worker, Ping_Worker, ROSMASTER_Worker
from Edit_Robot_Dialog import Edit_Robot_Dialog
from Generate_Key import Generate_Key
import os
import paramiko
import sys
import subprocess
import signal
import re

ansiEscape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')


#This class creates the Main Window of the application
class Multilauncher(QtWidgets.QMainWindow, MultilauncherDesign.Ui_MainWindow):

    #Initializes and defines the Multilauncher Window
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Handles interrupts
        signal.signal(signal.SIGINT, self.terminateApp)
        signal.signal(signal.SIGTERM, self.terminateApp)
        self.timerThread = QtCore.QThread()
        self.timerThread.start()
        self.timer = QtCore.QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(lambda: None)
        self.timer.moveToThread(self.timerThread)

        #Initial RSA Key checking
        self.myKey = ""
        self.RSA = self.rsaCheck()

        #Reading in the MaxSessions variable if it exists
        self.maxSSH = self.getMaxSSH()

        #Used to block the execution of certain functions if True
        self.maxSSHIgnore = False

        #Signifies if the ROSCORE Window is running
        self.masterIsRunning = False

        #Signifies if there have been changes in the robot table data
        self.saved = True

        #Used to warn the user about setting the number of remote repositories potentially too high
        self.largeNumOfRepos = False

        #modify the ui to add the tab widget
        del self.commands
        self.tabCommands = QtWidgets.QTabWidget()
        self.gridLayout_4.addWidget(self.tabCommands, 3, 0, 1, 3)

        #Paring buttons to functions
        self.filesearchbutton.clicked.connect(self.loadFile)
        self.pingrobotsbutton.clicked.connect(self.pingTest)
        self.bashrcbutton.clicked.connect(self.updateBashrc)
        self.robotlistsavebutton.clicked.connect(self.saveToFile)
        self.spinpackage.valueChanged.connect(self.reloadPackage)
        self.launchbutton.clicked.connect(self.launchCommands)
        self.buttontransfer.clicked.connect(self.gitCopyRepo)
        self.savecommandsbutton.clicked.connect(self.saveCommands)
        self.loadcommandsbutton.clicked.connect(self.loadCommands)
        self.argumentbutton.clicked.connect(self.adjustArgsWindow)
        self.editlistsbutton.clicked.connect(self.editRobots)
        self.findRSAButton.clicked.connect(self.findRSA)
        self.launchTypeButton.clicked.connect(self.launchThisType)
        self.launchMasterButton.clicked.connect(self.launchMaster)
        self.checkAllButton.clicked.connect(self.enableAndDisable)
        self.updateMaxSessionButton.clicked.connect(self.setMaxSessions)
        self.generateRSAKeyButton.clicked.connect(self.genKey)

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
        self.directoryPaths = []
        self.remoteURLs = []

        #Creates the Launch Window used in pinging and executing selected commands
        self.childLaunchWindow = Launch_Window()
        self.childLaunchWindow.window = "launch"
        self.childLaunchWindow.buttonStopThread.clicked.connect(lambda state, arg = "launch":self.interruptRemainingThreads(arg))
        self.childLaunchWindow.lineDebugCommand.returnPressed.connect(self.sendDebugCommand)
        self.childLaunchWindow.stopCurrentThread.clicked.connect(lambda state, arg = "launch":self.terminateCurrentThread(arg))
        self.childLaunchWindow.closeThreads.connect(self.termCheck)
        self.childLaunchWindow.saveTerminalOutput.clicked.connect(lambda state, arg = "launch":self.saveTerminalOutput(arg))
        self.childLaunchWindow.tab_Launch.removeTab(0)
        self.childLaunchWindow.tab_Launch.removeTab(0)

        #Data structures for the dynamic Launch Window
        self.layoutTerminalList = {}
        self.widgetTerminalList = {}
        self.terminalList = {}
        self.threadList = {}
        self.workerList = {}
        self.threadStillRunning = 'no'

        #Creates the ROSCORE Window used to manage/observe running roscores
        self.childRoscoreWindow = Launch_Window()
        self.childRoscoreWindow.setWindowTitle("ROSCORE Window")
        self.childRoscoreWindow.window = "masters"
        self.childRoscoreWindow.setModal(False)
        self.childRoscoreWindow.buttonStopThread.clicked.connect(lambda state, arg = "masters":self.interruptRemainingThreads(arg))
        self.childRoscoreWindow.lineDebugCommand.hide()
        self.childRoscoreWindow.stopCurrentThread.clicked.connect(lambda state, arg = "masters":self.terminateCurrentThread(arg))
        self.childRoscoreWindow.closeThreads.connect(self.termCheck)
        self.childRoscoreWindow.saveTerminalOutput.clicked.connect(lambda state, arg = "masters":self.saveTerminalOutput(arg))
        self.childRoscoreWindow.tab_Launch.removeTab(0)
        self.childRoscoreWindow.tab_Launch.removeTab(0)

        #Data structures for the dynamic ROSCORE Window
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


    #Used to detect when the window size is changed
    def resizeEvent(self, QResizeEvent):
        self.setTableSize()


    #Corrects the column header sizes
    def setTableSize(self):
        self.robotTable.setColumnWidth(0, self.width()/7.2)
        self.robotTable.setColumnWidth(1, self.width()/7.2)
        self.robotTable.setColumnWidth(2, self.width()/7.2)
        self.robotTable.setColumnWidth(3, self.width()/7.2)
        self.robotTable.setColumnWidth(4, self.width()/7.2)
        self.robotTable.setColumnWidth(5, self.width()/7.2)
        self.robotTable.setColumnWidth(6, self.width()/7.2)


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


    #Enables/Disables all listed robots
    def enableAndDisable(self):
        if len(self.ENABLE) == 0:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "No robots to enable")
        else:
            flag = self.ENABLE[0]
            if flag == "True":

                for index, string in enumerate(self.ENABLE):
                    self.robotTable.cellWidget(index, 0).setCheckState(QtCore.Qt.Unchecked)

            else:

                for index, string in enumerate(self.ENABLE):
                    self.robotTable.cellWidget(index, 0).setCheckState(QtCore.Qt.Checked)

        self.updateLists()


    #Runs the Edit Robot Dialog Window if there are no other threads running
    def editRobots(self):
        if self.threadStillRunning == 'no':
            self.updateLists()
            self.robotEditDialog = Edit_Robot_Dialog(self)
            self.robotEditDialog.save.connect(self.updateListsFromDialog)
            self.loadTable()
            self.robotEditDialog.show()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)


    #Loads the Edit Robot Dialog's table from the robot table in the Main Window
    def loadTable(self):
        self.updateLists()

        #If there is data to be loaded into the editing table
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
            if listName == "Enabled":

                # Append all data in the column
                for y in range(self.robotTable.rowCount()):
                    if self.robotTable.cellWidget(y,0).checkState() == 2:
                        tempList.append("True")
                    else:
                        tempList.append("False")

            elif listName == "ROSMASTER Settings":

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

            elif listName == "Arguments":

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
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in compiling lists: %s" % e)


    #Loads the text fields in the Main Window from the Edit Robot Dialog's robot table
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

            # tempWidget = QtWidgets.QWidget()
            # tempLayout = QtWidgets.QHBoxLayout(tempWidget)
            # tempLayout.addWidget(tempCheckBox)
            # tempLayout.setAlignment(QtCore.Qt.AlignHCenter)
            # tempWidget.setLayout(tempLayout)

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
        self.IPS = self.makeListFromTable("Robot's IP Address")
        self.updateMasterCombobox()

        #Update the dictionary
        self.updateLists()
        self.flushCommand()
        self.updateMasterCombobox()

        for index, string in enumerate(tempMasterList):

            #If a match has been found
            if string in self.IPS:
                string = "Roscore at:" + string
            self.comboboxMasterList[index].setCurrentIndex(self.comboboxMasterList[index].findText(string))

        self.saved = False


    #Remakes the list of enabled robots every time a checkbox is changed
    def enableWidgetFromCheckbox(self):
        self.ENABLE = self.makeListFromTable("Enabled")
        self.setLaunchEnable(self.checkConnectionAvailable())

        #Sets colors to the robots based on their status
        self.colorsTableRows()


    #Colors the rows in the robot-table based on robot status and if the robot is enabled
    def colorsTableRows(self):
        for i, statusEnable, statusFound, master in zip(range(len(self.ENABLE)),self.ENABLE, self.CONNECTION_STATUS, self.MASTER_TYPE):

            #If the computer is communicating to a remote master
            if master != "No ROS Settings" and master != "Master" and master != "Master and Launch":
                indexMasterIP = self.IPS.index(master)

            #The computer is its own master
            else:
                indexMasterIP = i

            #If the remote machine is enabled, found, and (is not dependent on another machine in its ROS Settings)
            # or (the machine it needs to talk to is set properly and (that other machine is enabled and found))
            if statusEnable == "True" and statusFound == "Found" and ((master == "No ROS Settings" or master == "Master" or master == "Master and Launch") \
                or ((self.MASTER_TYPE[indexMasterIP] == "Master" or self.MASTER_TYPE[indexMasterIP] == "Master and Launch")
                    and (self.ENABLE[indexMasterIP] == "True" and self.CONNECTION_STATUS[indexMasterIP] == "Found"))):

                #Green
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(100, 255, 100)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(100, 255, 100)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(100, 255, 100)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(100, 255, 100)))

                if master == "Master":

                    #Light Blue
                    self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(30, 220, 230)))
                    self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(30, 220, 230)))
                    self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(30, 220, 230)))
                    self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(30, 220, 230)))

                elif master == "Master and Launch":

                    #Light Blue/Green
                    gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(200, 200))
                    gradient.setColorAt(0, QtGui.QColor(30, 220, 230))
                    gradient.setColorAt(1, QtGui.QColor(100, 255, 100))

                    self.robotTable.item(i, 1).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 2).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 3).setBackground(QtGui.QBrush(gradient))
                    self.robotTable.item(i, 5).setBackground(QtGui.QBrush(gradient))

                #If the remote machine is supposed to be a master of some other machine
                elif self.IPS[i] in self.MASTER_TYPE:

                    #If the other remote machine is enabled
                    if self.ENABLE[self.MASTER_TYPE.index(self.IPS[i])] == "True":

                        #Yellow
                        self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                        self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))

            #If the remote machine is disabled
            elif statusEnable == "False":

                #White
                self.robotTable.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                self.robotTable.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                self.robotTable.item(i, 3).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                self.robotTable.item(i, 5).setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

            #If the remote machine is not found or (its master is not enabled or found)
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
            self.argsDialog = Adjust_Arguments(self.IPS, self.DICT_TYPES)
            self.argsDialog.saveArgs.connect(self.writeNewArgs)
            self.argsDialog.show()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)


    #Appends the list of arguments to the Arguments text field
    @QtCore.pyqtSlot(list)
    def writeNewArgs(self, argsResumeList):
        for index, x in enumerate(argsResumeList):
            self.robotTable.cellWidget(index, 4).clear()
            argLines = x.split("|")
            self.robotTable.cellWidget(index, 4).addItems(argLines)
        self.saved = False


    #Takes the data from the robot table in the Main Window and loads them into the backend data structures for processing
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
            self.MASTER_TYPE = []

            #Populate backend lists
            self.IPS = self.makeListFromTable("Robot's IP Address")
            self.USERS = self.makeListFromTable("Robot's Name/User")
            self.TYPES = self.makeListFromTable("Robot's Type/Configuration")
            self.CONNECTION_STATUS = self.makeListFromTable("Connection Status")
            self.ARGS = self.makeListFromTable("Arguments")
            self.ENABLE = self.makeListFromTable("Enabled")
            self.MASTER_TYPE = self.makeListFromTable("ROSMASTER Settings")

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

                #If the text matches a key in the types dictionary
                if text in self.DICT_TYPES.keys():
                    index = combo.findText(text)
                    combo.setCurrentIndex(index)

            #Check the status of the robots
            self.setLaunchEnable(self.checkConnectionAvailable())

            # Sets colors to the robots based on their status
            self.colorsTableRows()

        except:
            e = sys.exc_info()[0]
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in updating backend lists: %s" % e)


    #Gets the maximum number of concurrent SSH sessions based on the user's MaxSessions variable in sshd_config
    def getMaxSSH(self):

        #Open the file and search for the MaxSessions variable
        actualFileName = "/etc/ssh/sshd_config"
        rFile = open(actualFileName, "r")
        listOfLines = rFile.readlines()
        for line in listOfLines:
            if "MaxSessions" in line:
                temp = line.split(" ")[-1].strip()
                rFile.close()
                return int(temp)

        #If the MaxSessions variable was not found return the default number of sessions
        rFile.close()
        return 10


    #Checks to see if the user is trying to connect to more robots than there sshd_config file will allow
    def maxSSHCheck(self):

        sessions = self.calcEnable() + self.calcMasterLaunch()
        if sessions > self.maxSSH:
            self.maxSSHIgnore = True
            message = "Your combined number of enabled robots and \"Master and Launch\" ROS Settings has exceeded your maximum number of concurrent SSH connections." \
                      "\nPlease update your ssh configuration file at:\n/etc/ssh/sshd_config\nand add or update" \
                      " the line:\nMaxSessions "+str(sessions)+"\n" \
                      "\nCurrent Maximum: "+str(self.maxSSH)+"\nNeeded Maximum: "+str(sessions)
            temp = QtWidgets.QMessageBox.warning(self, "Warning", message)


    #Updates the MaxSessions variable in sshd_config
    def setMaxSessions(self):
        self.maxSSH = self.getMaxSSH()
        actualFileName = "/etc/ssh/sshd_config"
        sessions = self.calcEnable()+self.calcMasterLaunch()

        #If the number of simultaneous SSH sessions exceeds the value set in the MaxSessions variable
        if sessions > self.maxSSH:
            result = subprocess.call("grep -q MaxSessions " + actualFileName, shell=True)

            #If the MaxSessions variable was found
            if result == 0:
                command = "pkexec sed -i \'s/MaxSessions [0-9][0-9]*/MaxSessions "+str(sessions)+"/\' "+actualFileName
                subprocess.call(command, shell=True)

            #If the MaxSessions variable was not found
            elif result == 1:
                command = "pkexec sed -i \"$ a MaxSessions "+str(sessions)+"\" "+actualFileName
                subprocess.call(command, shell=True)
            self.maxSSH = sessions

        else:
            temp = QtWidgets.QMessageBox.information(self, "Information", "The current required number of ssh sessions: ("
                                                 +str(sessions)+") does not exceed the value of MaxSessions found in /etc/ssh/sshd_config: ("+str(self.maxSSH)+")")


    #Lets the application continue if the MaxSessions variable in sshd_config is greater than or equal to the number of needed SSH sessions
    def continueProgram(self):
        self.maxSSHCheck()

        #If the MaxSessions variable has been corrected
        if not self.maxSSHIgnore:
            return True
        else:
            self.maxSSHIgnore = False
            return False


    #Calls the Generate_Key.py to generate a new rsa key
    def rsaGeneration(self, ipList, userList):
        self.keyWindow = Generate_Key(ipList, userList, self.PASSWORDS)
        self.keyWindow.show()
        self.keyWindow.rsaKey.connect(self.rsaConfirm)


    #Helper function to catch the signal generated by successfully generating a new RSA key
    @QtCore.pyqtSlot(bool)
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
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in setting up RSA Key: Selected file not a Private RSA Key")


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


    #Locks and unlocks several functions after all enabled robots have been found and have valid ROS Settings or if ROSMASTERs are running
    def setLaunchEnable(self, available):

        #If the ROSCORE Window is running
        if self.masterIsRunning:
            self.robotTable.setEnabled(not available)
            self.editlistsbutton.setEnabled(not available)
            self.pingrobotsbutton.setEnabled(not available)
            self.buttontransfer.setEnabled(not available)
            self.bashrcbutton.setEnabled(not available)
            self.argumentbutton.setEnabled(not available)
            self.spinpackage.setEnabled(not available)
            self.lineUsername.setEnabled(not available)
            self.linePassword.setEnabled(not available)
            self.launchMasterButton.setEnabled(not available)
            self.generateRSAKeyButton.setEnabled(not available)
            self.checkAllButton.setEnabled(not available)
            self.updateMaxSessionButton.setEnabled(not available)
            self.findRSAButton.setEnabled(not available)

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
            self.childLaunchWindow.lineDebugCommand.setEnabled(available)
            self.launchTypeButton.setEnabled(available)
            self.launchMasterButton.setEnabled(available)
            self.generateRSAKeyButton.setEnabled(available)
            self.checkAllButton.setEnabled(True)
            self.updateMaxSessionButton.setEnabled(True)


    #Returns True if ROSMASTERS are not needed or if there are masters running when needed, False otherwise
    def mastersRunningCheck(self):

        tempList = []
        for index in self.masterWorkerList:
            tempList.append(self.masterWorkerList[index].IP)

        for i, statusEnable, master in zip(range(len(self.IPS)),self.ENABLE, self.MASTER_TYPE):

            #If the remote machine is enabled and is listening to a master
            if statusEnable == "True" and master != "No ROS Settings" and master != "Master" and master != "Master and Launch":
                indexMasterIP = self.IPS.index(master)
                IP = self.IPS[indexMasterIP]
                if IP not in tempList:
                    return False
        return True


    #Flushes the tabbed command terminal in the Main Window
    def flushCommand(self):

        #Reset the command terminal
        while self.tabCommands.count() != 0:
            obj = self.plaintextCommandDict[self.tabCommands.tabText(0)]
            obj.deleteLater()
            obj = self.layoutCommandList.pop(0)
            obj.deleteLater()
            obj = self.widgetCommandList.pop(0)
            obj.deleteLater()
            self.tabCommands.removeTab(0)
        self.plaintextCommandDict.clear()

        #Prime the command terminal to have a tab for every robot type/configuration
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


    #Updates the master combobox when new robots are added or removed
    def updateMasterCombobox(self):

        #Reset the master combobox
        while self.comboboxMasterList != []:
            obj = self.comboboxMasterList.pop(0)
            obj.deleteLater()

        #For every listed robot in the robot table
        for currentIndex, currentIp in enumerate(self.IPS):
            tempCombo = QtWidgets.QComboBox()
            tempCombo.addItem("No ROS Settings")
            tempCombo.addItem("Master")
            tempCombo.addItem("Master and Launch")

            #Adds every other possible IP that is not the current IP
            for index, ip in enumerate(self.IPS):

                if currentIp != ip:
                    tempCombo.addItem("Roscore at:"+ ip)

            tempCombo.currentIndexChanged.connect(self.checkMasterDependencies)
            self.robotTable.setCellWidget(currentIndex, 6, tempCombo)
            self.comboboxMasterList.append(tempCombo)


    #Remakes the list of ROSMASTERs every time a "ROSMASTER Settings" combobox is changed
    def checkMasterDependencies(self):
        self.MASTER_TYPE = self.makeListFromTable("ROSMASTER Settings")
        self.setLaunchEnable(self.checkConnectionAvailable())
        self.colorsTableRows()
        self.saved = False


    #Load data from a .csv file separated by commas (,)
    def loadFile(self):
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
                    rFile = open(self.STRINGOFPATH, "r")
                    listOfLines = rFile.readlines()
                    index = 0

                    # Until a blank line or EOF is encountered
                    for line in listOfLines:

                        line = line.strip().split(",")

                        #If a RSA Key location was saved
                        if line[0] == "RSA":
                            self.rsaPath.setText(line[1])
                            self.rsaCheck()

                        #If a username for a remote git repository was saved
                        elif line[0] == "GITUSER":
                            self.lineUsername.setText(line[1])

                        #If the current line from the file is valid data
                        elif line[0] != "" and line[0] != "#####":

                            #Add the basic robot data
                            self.robotTable.insertRow(index)

                            tempCheckBox = QtWidgets.QCheckBox()
                            tempCheckBox.setCheckState(QtCore.Qt.Unchecked)

                            #If the current robot was saved as enabled
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
                    self.IPS = self.makeListFromTable("Robot's IP Address")
                    self.updateMasterCombobox()

                    #REDESIGN: self.ENABLE list not updated in time for for-loop
                    self.updateLists()

                    for index, string in enumerate(tempMasterList):

                        #If the saved link to a ROSMASTER exists in the listed IPs
                        if string in self.IPS:
                            string = "Roscore at:"+string
                        self.comboboxMasterList[index].setCurrentIndex(self.comboboxMasterList[index].findText(string))

                    self.updateLists()
                    self.flushCommand()
                    self.saved = True

                except:
                    e = sys.exc_info()[0]
                    temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error when loading robotlist: %s" % e)

        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", self.threadStillRunning)


    #Save the current data from the Main Window's text fields to a .csv file
    def saveToFile(self):

        #If there is data to be saved
        if self.robotTable.rowCount() != 0:
            string = self.selectedfilename.text()
            name = string [14:]

            filePath = QtWidgets.QFileDialog.getSaveFileName(self,"Choose a name for your file", directory = name, filter = "csv (*.csv *.)")

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

                    #If there is a set location for a RSA Key listed
                    if str(self.rsaPath.text()) != "No RSA Key Found":
                        rFile.write("RSA,"+str(self.rsaPath.text())+"\n")

                    #If there is a username for a remote git repository listed
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
                    self.saved = True

            except:
                e = sys.exc_info()[0]
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in saving robot data to file: %s" % e)

        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No robot data found to save")


    #Save the current list of commands from the Command Editor text field to a .txt file
    def saveCommands(self):

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

                #If the user is making a new .txt file
                else:
                    rFile = open(self.STRINGOFPATH + ".txt", "w")

                plainText = ""

                for index in range(self.tabCommands.count()):
                    self.tabCommands.setCurrentIndex(index)
                    plainText += ("#####\nTYPE: "+self.tabCommands.tabText(self.tabCommands.currentIndex())+"\n")
                    plainText += self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].toPlainText()
                    plainText += "\n"

                rFile.write(plainText)
                rFile.close()

        except:
            e = sys.exc_info()[0]
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in saving commands to command file: %s" % e)


    #Loads commands into the Command Editor text field from a .txt file
    def loadCommands(self):

        #Prompt the user for a file selection
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Find your command file", filter = "txt (*.txt *.)")
        try:

            #Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]
            if self.STRINGOFPATH:
                partsOfPath = self.STRINGOFPATH.split("/")
                actualFileName = partsOfPath[-1]
                self.commandFileLable.setText("Current File: "+actualFileName)

                rFile = open(self.STRINGOFPATH, "r")
                listOfLines = rFile.readlines()
                rFile.close()

                #Flags to control the logical flow of appending the commands to the appropriate tabs
                typeFlag = False
                foundFlag = False

                #Until the end of the list
                for line in listOfLines:

                    #If the current line is denotes a new type of robot
                    if line == "#####\n":

                        typeFlag = True
                        foundFlag = False

                    #If their is a new type of robot to be addressed
                    elif typeFlag:

                        typeFlag = False
                        robotType = line[6:-1]

                        #Look through all command tabs
                        for index in range(self.tabCommands.count()):
                            self.tabCommands.setCurrentIndex(index)

                            #If the tab text matches the type of robot currently being looked for
                            if str(self.tabCommands.tabText(self.tabCommands.currentIndex())) == robotType:

                                #Clear the tab
                                self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].clear()
                                foundFlag = True
                                break

                    #If the robot type has been found
                    elif foundFlag:

                        #Load the command into the tab
                        self.plaintextCommandDict[self.tabCommands.tabText(self.tabCommands.currentIndex())].appendPlainText(line.strip())

        except:
            e = sys.exc_info()[0]
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Error in loading commands from command file: %s" % e)


    #Saves the terminal output of the current window
    def saveTerminalOutput(self, window):

        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Choose a name for your file", filter="txt (*.txt *.)")

        try:

            #Test to see if the user selected a valid path or canceled
            self.STRINGOFPATH = filePath[0]
            if self.STRINGOFPATH:
                partsOfPath = self.STRINGOFPATH.split("/")
                actualFileName = partsOfPath[-1]

                #If the user is overwriting an existing .txt file
                if actualFileName[-1] == "t":
                    rFile = open(self.STRINGOFPATH, "w")

                #If the user is making a new .txt file
                else:
                    rFile = open(self.STRINGOFPATH + ".txt", "w")

                if window == "masters":
                    for index , value in enumerate(self.masterTerminalList):

                        rFile.write("###############################################\n")
                        string = self.masterTerminalList[value].toPlainText()
                        rFile.write(string+"\n")

                elif window == "launch":
                    for index , value in enumerate(self.terminalList):

                        rFile.write("###############################################\n")
                        string = self.terminalList[value].toPlainText()
                        rFile.write(string+"\n")

                rFile.close()

        except:
            e = sys.exc_info()[0]
            temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                                 "Error in saving terminal output to file: %s" % e)


    #Checks to see if there is robot data to save or ping
    def pingCheck(self):

        allDisabled = False
        numberDisable = 0
        for statusEnable in self.ENABLE:
            if statusEnable == "False":
                numberDisable += 1

        #If all the listed robots in the robot table are disabled
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


    #Updates the File Transfer section when the user changes the number of packages to transfer
    def reloadPackage(self):

        #Warns the user about setting the number of remote repositories in the spinbox to a high number
        if self.spinpackage.value() > 20 and self.largeNumOfRepos == False:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "This program may slow down when transferring a large number of remote repositories")
            self.largeNumOfRepos = True

        #If the user is going to pull from more repositories than previously set
        if len(self.directoryPaths) < self.spinpackage.value():
            index = len(self.directoryPaths)

            while index < self.spinpackage.value():

                self.directoryPaths.append("")
                self.remoteURLs.append("")

                index += 1

        x = 0
        #Clears the File Transfer section
        while self.linePathParentPackage != []:

            self.directoryPaths[x] = self.linePathParentPackage.__getitem__(0).text().strip()
            self.remoteURLs[x] = self.linePathGitRepoList.__getitem__(0).text().strip()

            obj = self.linePathParentPackage.pop(0)
            obj.deleteLater()
            obj = self.linePathGitRepoList.pop(0)
            obj.deleteLater()
            obj = self.comboRobotTypeList.pop(0)
            obj.deleteLater()
            obj = self.buttonDirectoryPackageList.pop(0)
            obj.deleteLater()
            obj = self.comboMakeList.pop(0)
            obj.deleteLater()
            x+=1


        #Adds widgets to the File Transfer section based on the number of packages listed in the spinbox
        for index in range(self.spinpackage.value()):
            tempPackageWidget = QtWidgets.QLineEdit()
            tempGitRepoWidget = QtWidgets.QLineEdit()

            #If there is data that was previously at this index
            if index < len(self.directoryPaths) and self.directoryPaths[index] != "":
                tempPackageWidget.setText(self.directoryPaths[index])
                tempGitRepoWidget.setText(self.remoteURLs[index])

            #If this is a new remote repository listing
            else:
                tempGitRepoWidget.setPlaceholderText("Use http:// here")

            tempRobotTypeWidget = QtWidgets.QComboBox()
            tempMakeWidget = QtWidgets.QComboBox()
            tempMakeWidget.addItems(["no make", "catkin_make", "catkin_build"])
            typeNames = []
            for typeName in self.TYPES:

                #If the currently indexed robot has a different type than in the typeNames list
                if typeName not in typeNames:
                    typeNames.append(typeName)
            tempRobotTypeWidget.addItems(typeNames)
            tempPackageDirectoryWidget = QtWidgets.QPushButton()
            tempPackageDirectoryWidget.setText("Parent Package Directory")
            tempPackageDirectoryWidget.clicked.connect(lambda state, arg = index:self.specifyPackagePath(arg))
            self.linePathParentPackage.append(tempPackageWidget)
            self.linePathGitRepoList.append(tempGitRepoWidget)
            self.comboRobotTypeList.append(tempRobotTypeWidget)
            self.buttonDirectoryPackageList.append(tempPackageDirectoryWidget)
            self.comboMakeList.append(tempMakeWidget)
            self.gridpackage.addWidget(tempPackageDirectoryWidget, index, 0)
            self.gridpackage.addWidget(tempPackageWidget, index, 1)
            self.gridpackage.addWidget(tempGitRepoWidget, index, 2)
            self.gridpackage.addWidget(tempRobotTypeWidget, index, 3)
            self.gridpackage.addWidget(tempMakeWidget, index, 4)
            self.gridpackage.setColumnStretch(0,1)
            self.gridpackage.setColumnStretch(1,1)
            self.gridpackage.setColumnStretch(2,1)
            self.gridpackage.setColumnStretch(3,1)
            self.gridpackage.setColumnStretch(4,1)


    #Creates the specified package path for cloning the remote repos
    def specifyPackagePath(self, n):
        tempDirectoryPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Specify the Package Directory")

        #If the directory path exists
        if tempDirectoryPath:
            tempDirTest = tempDirectoryPath.split('/')

            #Correcting the directory path
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

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():
            self.ERRORTEXT = ""

            #If there are no remote repositories listed
            if self.spinpackage.value() == 0:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "Zero Repositories set")

            else:

                #If the username for the remote repositories is blank
                if self.lineUsername.text().strip() == "":
                    self.ERRORTEXT += "\nMissing remote Git Username\n"

                #If the password for the remote repositories is blank
                if self.linePassword.text().strip() == "":
                    self.ERRORTEXT += "\nMissing remote Git Username\n"

                index = 0
                while index < self.spinpackage.value():

                    #If the destination for the currently indexed remote repository is blank
                    if self.linePathParentPackage[index].text().strip() == "":
                        self.ERRORTEXT += "\nMissing Destination Directory for repository: "+ str(index+1) +"\n"

                    #If the url for the currently indexed remote repository is blank
                    if self.linePathGitRepoList[index].text().strip() == "":
                        self.ERRORTEXT += "\nMissing Remote Repository URL for repository: " + str(index+1) +"\n"
                    index += 1

                #If there were no blank entries
                if self.ERRORTEXT == "":
                    temp = QtWidgets.QMessageBox.information(self, "Information", "Uncommitted changes will be saved using \"git stash\"")
                    self.checkPasswordLaunchThread("git")

                #If there was a blank entry somewhere
                else:
                    temp = QtWidgets.QMessageBox.warning(self, "Warning", self.ERRORTEXT)


    #Handler function to launch the ROSMASTERs
    def launchMaster(self):

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():

            #If there are not ROSMASTERs set
            if (self.calcMaster()+self.calcMasterLaunch()) == 0:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "No ROS MASTERS have been set/Enabled")

            #Launch the relevant ROSMASTERs
            else:
                self.masterIsRunning = True
                self.checkPasswordLaunchThread("masters")


    #Handler function to launch one or more threads that perform launch commands
    def launchCommands(self):

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():

            #If the relevant ROSMASTERs are running
            if self.mastersRunningCheck():
                self.checkPasswordLaunchThread("commands")

            #If one or more ROSMASTERs are not running
            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "One or more ROSMASTERs is not running, please close and relaunch the ROSCORE Window")


    #Handler function to launch one or more threads that perform launch commands on a single type
    def launchThisType(self):

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():

            #If the relevant ROSMASTERs are running
            if self.mastersRunningCheck():
                self.checkPasswordLaunchThread("type")

            #If one or more ROSMASTERs are not running
            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "One or more ROSMASTERs is not running, "
                                                                      "please check your ROSMASTER Settings and relaunch the ROSCORE Window")


    #Handler function to launch one or more threads that perform ping commands
    def pingTest(self):

        #If there is data to ping
        if self.pingCheck():
            self.checkPasswordLaunchThread("ping")


    #Handler function to launch one or more threads that perform commands to update the .bashrc file
    def updateBashrc(self):

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():
            flag = 0

            for index, string in enumerate(self.MASTER_TYPE):

                #If the currently indexed robot is enabled and has its ROSMASTER Settings to something other than "No ROS Settings"
                if self.ENABLE[index] == "True" and string != "No ROS Settings":
                    flag = 1
                    break

            #If there are no ROS Settings to change
            if flag == 0:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "No ROS Settings to change")

            #Update the .bashrc of the relevant robots
            else:
                self.checkPasswordLaunchThread("bashrc")


    #Handler function to generate a new RSA Key
    def genKey(self):

        #If there is no problem with the number of ssh sessions
        if self.continueProgram():
            self.checkPasswordLaunchThread("genKey")


    #Returns a boolean value if the application is running in type only mode
    def currentTabCheck(self, command, index):
        correctType = True
        if command == "type":
            currentType = self.tabCommands.tabText(self.tabCommands.currentIndex())
            if self.TYPES[index] == currentType:
                correctType = True
            else:
                correctType = False
        return correctType


    #Sets flags based on the type of thread to be run and if the RSA Checkbox is selected
    def checkPasswordLaunchThread(self, commandType):
        self.updateLists()

        # If the ping button was pushed
        if commandType == "ping":
            self.launchThread(commandType, "rsa")

        #If the Generate RSA Key button was not pushed and the RSA Checkbox is selected
        elif commandType != "genKey" and self.rsacheckbox.isChecked():

            #If the proper RSA key is present on the user's machine at: ~/.ssh
            if self.RSA:

                #If the Launch Masters button was pushed
                if commandType == "masters":
                    self.masterThread("rsa")

                #All other command types
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

                    #If the currently indexed robot is enabled and its ROSMASTER Settings are set to be a type of Master
                    if self.ENABLE[index] == "True" and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                        enableIPS.append(ip)
                        enableUSERS.append(user)

                elif commandType == "bashrc":

                    #If the currently indexed robot is enabled and has some ROSMASTER Settings other than "No ROS Settings"
                    if self.ENABLE[index] == "True" and self.MASTER_TYPE[index] != "No ROS Settings":
                        enableIPS.append(ip)
                        enableUSERS.append(user)

                elif commandType == "genKey":

                    #If the currently indexed robot is enable
                    if self.ENABLE[index] == "True":
                        enableIPS.append(ip)
                        enableUSERS.append(user)

                else:

                    #If the currently indexed robot is enabled and its ROSMASTER Settings are not set to "Master"
                    if self.ENABLE[index] == "True" and self.currentTabCheck(commandType,index) and self.MASTER_TYPE[index] != "Master":
                        enableIPS.append(ip)
                        enableUSERS.append(user)

            if len(enableIPS) != 0:
                #Setup and display the Password Window
                self.passwordWindow = Password_Window(enableIPS,enableUSERS,commandType)
                self.passwordWindow.savePasswords.connect(self.updatePassword)
                self.passwordWindow.exitWindow.connect(self.termCheck)
                self.passwordWindow.show()

            else:
                temp = QtWidgets.QMessageBox.warning(self, "Warning", "No valid and enabled robots to login to")


    #Saves the entered passwords from the Password Window to the backend data structure
    @QtCore.pyqtSlot(dict,str)
    def updatePassword(self, passwordList, commandType):
        self.PASSWORDS = {}
        self.PASSWORDS = passwordList.copy()

        #If the Launch Masters button was pushed
        if commandType == "masters":
            self.masterThread("password")

        #All other command types
        else:
            self.launchThread(commandType, "password")


    #Create and launch one or more threads to do different commands
    def launchThread(self, threadType, passwordType):
        self.ERRORTEXT = ""
        try:

            #If there are no currently running threads
            if self.threadStillRunning == 'no':
                self.refreshWindow(threadType)

                #If the user is transferring files to multiple robots
                if threadType == "git":
                    for index in range(len(self.IPS)):

                        #If the currently indexed robot is enabled and found
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

                            #RSA Checkbox test
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
                    self.largeNumOfRepos = False

                #If the user is launching commands
                elif threadType == "commands" or threadType == "type":
                    for index in range(len(self.IPS)):

                        #If the currently indexed robot is enabled, found, and their ROSMASTER Settings is not set to "Master"
                        if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and self.currentTabCheck(threadType,index) and self.MASTER_TYPE[index] != "Master":
                            tempThread = QtCore.QThread()
                            tempThread.start()

                            commandLinesList = str(self.plaintextCommandDict[self.TYPES[index]].toPlainText()).split("\n")

                            #Replacing the arguments in command lines
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

                                        #Replace the $variable in the string
                                        newReplacedLine = newReplacedLine.replace(tempArgument.split(':')[0].split("/")[0],
                                                                                  ':'.join(tempArgument.split(':')[1:]))

                                        #Replace the $argument name in the string if there is one
                                        if len(tempArgument.split(':')[0].split("/")) == 2:
                                            newReplacedLine = newReplacedLine.replace("$"+tempArgument.split(':')[0].split("/")[1],':'.join(tempArgument.split(':')[1:]))
                                    commandLinesArgsList.append(newReplacedLine)
                                else:
                                    commandLinesArgsList.append(line)

                            #RSA Checkbox test
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

                    if self.workerList != {}:
                        self.threadStillRunning = 'Launch files still running'
                        self.childLaunchWindow.show()
                    else:
                        temp = QtWidgets.QMessageBox.warning(self, "Warning", "No valid and enabled robots to login to")

                #If the user is pinging the listed robots
                elif threadType == "ping":
                    self.childLaunchWindow.lineDebugCommand.setEnabled(False)
                    for index in range(len(self.IPS)):

                        #If the currently indexed robot is enabled
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

                        #If the currently indexed robot is enabled, found, and has some ROS Settings to update
                        if self.ENABLE[index]=="True" and self.CONNECTION_STATUS[index] == "Found" and self.MASTER_TYPE[index] != "No ROS Settings":

                            tempThread = QtCore.QThread()
                            tempThread.start()

                            tempMasterString = self.MASTER_TYPE[index]

                            #If the currently indexed robot is a ROSMASTER
                            if tempMasterString == "Master" or tempMasterString == "Master and Launch":
                                tempMasterString = self.IPS[index]

                            #RSA Checkbox test
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

                #If the user in generating a RSA key
                elif threadType == "genKey":
                    enableIPS = []
                    enableUSERS = []

                    for index, ip, user in zip(range(len(self.IPS)), self.IPS, self.USERS):

                            #If the currently indexed robot is enabled and found
                            if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found":
                                enableIPS.append(ip)
                                enableUSERS.append(user)

                    self.rsaGeneration(enableIPS, enableUSERS)

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
                self.refreshWindow("masters")

                for index in range(len(self.IPS)):

                    #If the currently indexed robot is enabled, found, and is set to be either a "Master" or a "Master and Launch"
                    if self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                        tempThread = QtCore.QThread()
                        tempThread.start()

                        # RSA Checkbox test
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
    def refreshWindow(self,commands):

        #If ROSMASTERs are to be launched
        if commands == "masters":

            #Reset the ROSCORE Window
            for index, term, layout, widget in zip(range(len(self.masterTerminalList.keys())),
                                                   self.masterTerminalList.items(),self.masterLayoutTerminalList.items(), self.masterWidgetTerminalList.items()):
                term[1].deleteLater()
                layout[1].deleteLater()
                widget[1].deleteLater()
                self.childRoscoreWindow.tab_Launch.removeTab(0)

            self.masterTerminalList.clear()
            self.masterLayoutTerminalList.clear()
            self.masterWidgetTerminalList.clear()

        #Any other type of launch
        else:

            #Reset the Launch Window
            for index, term, layout, widget in zip(range(len(self.terminalList.keys())),
                                                   self.terminalList.items(),self.layoutTerminalList.items(), self.widgetTerminalList.items()):
                term[1].deleteLater()
                layout[1].deleteLater()
                widget[1].deleteLater()
                self.childLaunchWindow.tab_Launch.removeTab(0)

            self.terminalList.clear()
            self.layoutTerminalList.clear()
            self.widgetTerminalList.clear()


        for index, IP in enumerate(self.IPS):

            #If the currently indexed robot is enabled and the Ping Robots button is pushed
            if self.ENABLE[index] == "True" and commands == "ping":
                self.addToLaunchWindow(index,IP)

            #If the currently indexed robot is enabled, the robot is found, the Launch Masters button is pushed,
            # and the robot's ROS Settings are set to "Master" or "Master and Launch"
            elif self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and commands == "masters" \
                    and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                self.addToRoscoreWindow(index,IP)

            #If the currently indexed robot is enabled, the robot is found, the Update .bashrc button is pushed,
            # and the robot's ROS Settings are set to "Master" or "Master and Launch"
            elif self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and commands == "bashrc" \
                 and (self.MASTER_TYPE[index] == "Master" or self.MASTER_TYPE[index] == "Master and Launch"):
                self.addToLaunchWindow(index, IP)

            # If the currently indexed robot is enabled, the robot is found, the any other button is pushed,
            # and the robot's ROS Settings are not set to "Master"
            elif self.ENABLE[index] == "True" and self.CONNECTION_STATUS[index] == "Found" and (commands != "masters" and commands != "bashrc") \
                    and self.currentTabCheck(commands,index) and self.MASTER_TYPE[index] != "Master":
                self.addToLaunchWindow(index,IP)


    #Adds the currently indexed robot to the Launch Window
    def addToLaunchWindow(self, index, IP):
        tempLayout = QtWidgets.QVBoxLayout()
        tempWidget = QtWidgets.QWidget()
        tempTerminal = QtWidgets.QTextEdit()
        tempTerminal.setReadOnly(True)
        tempLayout.addWidget(tempTerminal, 0)
        tempWidget.setLayout(tempLayout)
        self.widgetTerminalList[index] = tempWidget
        self.layoutTerminalList[index] = tempLayout
        self.terminalList[index] = tempTerminal
        self.childLaunchWindow.tab_Launch.addTab(tempWidget, str(IP))


    #Adds the currently indexed robot to the ROSCORE Window
    def addToRoscoreWindow(self, index, IP):
        tempLayout = QtWidgets.QVBoxLayout()
        tempWidget = QtWidgets.QWidget()
        tempTerminal = QtWidgets.QTextEdit()
        tempTerminal.setReadOnly(True)
        tempLayout.addWidget(tempTerminal, 0)
        tempWidget.setLayout(tempLayout)
        self.masterWidgetTerminalList[index] = tempWidget
        self.masterLayoutTerminalList[index] = tempLayout
        self.masterTerminalList[index] = tempTerminal
        self.childRoscoreWindow.tab_Launch.addTab(tempWidget, str(IP))


    #Allows the user to send commands to the remote robots for unexpected terminal requests to un-terminated threads
    def sendDebugCommand(self):
        debugCommand = self.childLaunchWindow.lineDebugCommand.text().strip()
        self.childLaunchWindow.lineDebugCommand.clear()
        ipText = str(self.childLaunchWindow.tab_Launch.tabText(self.childLaunchWindow.tab_Launch.currentIndex()))
        ipKey = self.IPS.index(ipText)
        self.workerList[ipKey].channel.send(debugCommand + "\n")


    #Visually updates the Launch Window tabs to display feedback from the robots
    @QtCore.pyqtSlot(int, list)
    def writeInOwnedTerminal(self, ipIndex, data):
        self.dataConvert(ipIndex, data, "launch")


    #Visually updates the ROSCORE Window tabs to display feedback from the ROSMASTERs
    @QtCore.pyqtSlot(int, list)
    def masterWriteInOwnedTerminal(self, ipIndex, data):
        self.dataConvert(ipIndex, data, "masters")


    #Visually updates the Launch Window tabs to display feedback from pinging the robots
    @QtCore.pyqtSlot(int, str, int)
    def pingWriteInOwnedTerminal(self, ipIndex, data, pingResult):

        self.terminalList[ipIndex].insertPlainText(data)
        self.terminalList[ipIndex].moveCursor(QtGui.QTextCursor.End)

        #If the remote machine was found
        if pingResult == 0:
            self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Found"))

        #If the remote machine was not found
        else:
            self.robotTable.setItem(ipIndex, 5, QtWidgets.QTableWidgetItem("Not Found"))
        self.updateLists()


    #Helper function to remove certain types of escape characters
    def removeCharacters(self, data):

        data = data.replace(r'\x1B[K', "")

        return data


    #Determines if there are escape sequences in the current line and if they are of a certain type
    # Returns True if the line is processed here and False if the line needs to be examined by another function
    def lineCheck(self, start, stop, line, term):

        #No escape sequences found
        if start == -1 and stop == -1:

            cursor = term.textCursor()
            cursor.insertText(line)
            term.moveCursor(QtGui.QTextCursor.End)
            return True

        #If there is an escape sequence but not one that is based on font colors or bold escape sequences
        elif stop == -1:

            cursor = term.textCursor()

            #This line is to be hidden
            if line[start + 1:start + 4] == ']2;':
                cursor.insertText("\n")
                term.moveCursor(QtGui.QTextCursor.End)
                return True

            #Some other escape sequence
            else:
                temp = ansiEscape.sub('', line[start:])
                temp = self.removeCharacters(temp)
                cursor.insertText(temp)
                cursor.insertText("\n")
                term.moveCursor(QtGui.QTextCursor.End)
                return True

        return False


    #Sets the format of the current terminal for the current text sequence
    def setFormat(self, escapeSequence, term):

        # Bold
        if escapeSequence == "[1m":
            term.setFontWeight(75)

        # Reset to Default
        elif escapeSequence == "[0m":
            term.setFontWeight(50)
            term.setTextColor((QtGui.QColor(0, 0, 0)))

        # Red
        elif escapeSequence == "[31m" or escapeSequence == "[0;31m" or escapeSequence == "[01;31m":
            term.setTextColor((QtGui.QColor(175, 0, 0)))

        # Green
        elif escapeSequence == "[32m" or escapeSequence == "[0;32m" or escapeSequence == "[01;32m":
            term.setTextColor((QtGui.QColor(0, 175, 0)))

        # Yellow
        elif escapeSequence == "[33m" or escapeSequence == "[01;33m":
            term.setTextColor((QtGui.QColor(175, 175, 0)))

        # Blue
        elif escapeSequence == "[34m" or escapeSequence == "[0;34m" or escapeSequence == "[01;34m":
            term.setTextColor((QtGui.QColor(0, 0, 175)))

        # Magenta
        elif escapeSequence == "[35m" or escapeSequence == "[0;35m" or escapeSequence == "[01;35m":
            term.setTextColor((QtGui.QColor(175, 0, 175)))

        # Cyan
        elif escapeSequence == "[36m" or escapeSequence == "[0;36m" or escapeSequence == "[01;36m":
            term.setTextColor((QtGui.QColor(0, 175, 175)))


    #Appends formatted text to the terminal
    def addTextWithFormat(self, start, stop, line, term):

        #If the current format is to be extended pass this current line
        if stop == -1:
            stop = len(line)

        cursor = term.textCursor()
        cursor.insertText(line[start:stop])
        term.moveCursor(QtGui.QTextCursor.End)


    #Converts the data into the proper format for displaying in a window
    def dataConvert(self, ipIndex, data, flag):

        #If the data is from the ROSCORE Window
        if flag == "masters":
            term = self.masterTerminalList[ipIndex]

        else:
            term = self.terminalList[ipIndex]

        #For every line received
        for line in data:
            index = 0
            start = 0
            stop = 0

            #While not at the end of the current line
            while index < len(line):

                #Find the next escape sequence (if one exists)
                start = line.find("\x1B", start)
                stop = line.find("m", start)

                #If the escape sequence is special or if none exist in this line
                if self.lineCheck(start, stop, line, term):
                    break

                #Adjust for saving the escape code
                start += 1
                stop += 1

                #print "escapeSequence: "+ str(line[start:stop])

                escapeSequence = line[start:stop]

                #Set the terminal's format based on the escape sequence
                self.setFormat(escapeSequence, term)

                #Setup for the (possibly) next escape sequence
                index = stop
                start = stop

                #Look for the next escape sequence if one exists
                # Also used to find the length of the text that will be modified by the current terminal format if
                # there are no more format escape sequences
                stop = line.find("\x1B", start)

                #If there are not consecutive escape sequences
                if start != stop:
                    self.addTextWithFormat(start, stop, line, term)

                #If there are no more escape sequences
                if stop == -1:
                    break


    #Terminates the calling Launch Window thread
    @QtCore.pyqtSlot(int, str)
    def killThread(self, ipIndex, eMessage):

        #Append a failed terminal's error string to the master error string
        if eMessage != "":
            self.ERRORTEXT += "\n"+eMessage +"\n"

        #Terminates the thread
        del self.workerList[ipIndex]
        self.threadList[ipIndex].quit()
        self.threadList[ipIndex].wait()
        del self.threadList[ipIndex]

        #Appends "(Finished)" to visually denote a terminated thread
        for index in range(self.childLaunchWindow.tab_Launch.count()):
            if self.childLaunchWindow.tab_Launch.tabText(index) == self.IPS[ipIndex]:
                self.childLaunchWindow.tab_Launch.setTabText(index, self.IPS[ipIndex]+" (Finished)")
                self.terminalList[ipIndex].insertPlainText(eMessage)
                self.terminalList[ipIndex].moveCursor(QtGui.QTextCursor.End)

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
                                                         "Git Repo Cloning/Pulling Finished\n" + self.ERRORTEXT)

            elif self.threadStillRunning == 'Launch files still running':
                temp = QtWidgets.QMessageBox.information(self.childLaunchWindow, "Information",
                                                         "Finished Executing Commands\n" + self.ERRORTEXT)
            self.threadStillRunning = 'no'
        self.updateLists()


    #Terminates the calling ROSMASTER thread
    @QtCore.pyqtSlot(int, str)
    def masterKillThread(self, ipIndex, eMessage):

        #Append a failed terminal's error string to the master error string
        if eMessage != "":
            self.ERRORTEXT += "\n" + eMessage + "\n"

        #Terminates the thread
        del self.masterWorkerList[ipIndex]
        self.masterThreadList[ipIndex].quit()
        self.masterThreadList[ipIndex].wait()
        del self.masterThreadList[ipIndex]

        #Appends "(Finished)" to visually denote a terminated thread
        for index in range(self.childRoscoreWindow.tab_Launch.count()):
            if self.childRoscoreWindow.tab_Launch.tabText(index) == self.IPS[ipIndex]:
                self.childRoscoreWindow.tab_Launch.setTabText(index, self.IPS[ipIndex] + " (Finished)")
                self.masterTerminalList[ipIndex].insertPlainText(eMessage)
                self.masterTerminalList[ipIndex].moveCursor(QtGui.QTextCursor.End)

        # Display the finish message box based on the threads that were running
        if self.masterWorkerList == {} and self.masterThreadList == {}:
            temp = QtWidgets.QMessageBox.information(self.childRoscoreWindow, "Information", "ROSCOREs shutdown\n" + self.ERRORTEXT)
            self.masterThreadStillRunning = 'no'
        self.updateLists()


    #Helper function to interrupt the correct threads
    @QtCore.pyqtSlot(str)
    def termCheck(self, window):

        #If the window to be closed is a Launch Window
        if window == "launch":
            self.interruptRemainingThreads(window)

        #If the window to be closed is a ROSMASTER Window
        elif window == "masters":
            self.interruptRemainingThreads(window)
            self.masterIsRunning = False
            self.setLaunchEnable(True)

        #If the Password Window is closed prematurely and ROSMASTERs were to be run
        elif window == "pass" and self.masterIsRunning == True:
            self.masterIsRunning = False
            self.setLaunchEnable(True)


    #Terminates the currently selected tab/thread
    def terminateCurrentThread(self, flag):

        #If the thread that is being interrupted is a ROSMASTER thread
        if flag == "masters":
            ipText = str(self.childRoscoreWindow.tab_Launch.tabText(self.childRoscoreWindow.tab_Launch.currentIndex()))

            #If the thread is not already terminated
            if "Finished" not in ipText:
                workerKey = self.IPS.index(ipText)
                self.masterWorkerList[workerKey].stopSignal = True
                try:
                    self.masterWorkerList[workerKey].channel.send("\x03\n")
                    self.masterWorkerList[workerKey].channel.close()
                except:
                    pass

        #Interrupt a non-ROSMASTER thread
        else:
            ipText = str(self.childLaunchWindow.tab_Launch.tabText(self.childLaunchWindow.tab_Launch.currentIndex()))

            #If the thread is not already terminated
            if "Finished" not in ipText:
                workerKey = self.IPS.index(ipText)
                self.workerList[workerKey].stopSignal = True

                #If not a ping thread
                if self.threadStillRunning == 'git repository synchronisation still running' or self.threadStillRunning == 'bashrc still running' or self.threadStillRunning == 'Launch files still running':
                    try:
                        self.workerList[workerKey].channel.send("\x03\n")
                        self.workerList[workerKey].channel.close()
                    except:
                        pass


    #Interrupts any currently running threads
    def interruptRemainingThreads(self, flag):

        #If the threads that are being interrupted are ROSMASTER threads
        if flag == "masters":

            for workerKey in self.masterWorkerList.keys():
                self.masterWorkerList[workerKey].stopSignal = True
                try:
                    self.masterWorkerList[workerKey].channel.send("\x03\n")
                    self.masterWorkerList[workerKey].channel.close()
                except:
                    pass

        #Interrupting all other types of threads
        else:
            for workerKey in self.workerList.keys():
                self.workerList[workerKey].stopSignal = True

                #If not a ping thread
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

        # If there are threads running
        if self.workerList != {} and self.threadList != {} and self.masterWorkerList != {} and self.masterThreadList != {}:
            temp = QtWidgets.QMessageBox.warning(self, "Warning",
                                                 self.threadStillRunning + "\nThe threads are shutting down, just wait a little bit and try one more time!")
            event.ignore()

        # If there are no threads running
        else:

            #Has to be closed manually since this window is not modal and could still be open when closing the program
            self.childRoscoreWindow.close()

            #If the current session has recently been saved or reset
            if self.saved:
                self.timerThread.quit()
                self.timerThread.wait()
                event.accept()  #let the window close

            #If there are unsaved changes
            else:
                reply = QtWidgets.QMessageBox.question(self, 'Message', "Exit Without Saving?",
                                                       QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

                #The User does not want to save their changes
                if reply == QtWidgets.QMessageBox.Yes:
                    self.timerThread.quit()
                    self.timerThread.wait()
                    event.accept()

                #Cancel quiting the application
                else:
                    event.ignore()


    #Helper function to catch certain signals and redirect the flow of the program to closeEvent
    def terminateApp(self, arg1, arg2):
        self.close()
