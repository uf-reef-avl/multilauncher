#!/usr/bin/python3
# File: Adjust_Arguments.py
# Authors: Paul Buzaud and Matthew Hovatter
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


import Adjust_Arguments_Design
from PyQt5 import QtCore, QtGui, QtWidgets


#This window is used to set the arguments which will be replaced in the commands lines
class Adjust_Arguments(QtWidgets.QDialog, Adjust_Arguments_Design.Ui_Dialog):
    saveArgs = QtCore.pyqtSignal(list)


    #Definition of the Adjust_Arguments terminal
    def __init__(self, ipList, dictTypes, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        
        #Initialise the useful values of the current case
        self.dictTypes = dictTypes
        self.ipList = ipList
        self.argumentResume = ''
        self.spinTypeDict = {}
        self.labelTypeDict = {}
        self.argumentList = []

        #Connect every button to their correct slot
        self.treeRobotType.itemDoubleClicked.connect(self.editItem)
        self.treeRobotType.itemChanged.connect(self.changeArgument)
        self.buttonSave.clicked.connect(self.saveArguments)
        self.buttonCancel.clicked.connect(self.cancelArguments)

        #Initialise the area where the user can change the number of argument for each robot type
        self.area = QtWidgets.QWidget()
        self.area.setLayout(self.gridRobotType)
        self.scrollareaRobotType.setWidget(self.area)
        self.scrollareaRobotType.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollareaRobotType.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        #Initialise the spinboxes and labels of every robot type
        for index, robotType in enumerate(self.dictTypes.keys()):
            tempLabel = QtWidgets.QLabel(self)
            tempLabel.setText("Number of arguments for the robotType : "+ robotType)
            tempSpin = QtWidgets.QSpinBox(self)
            if self.dictTypes[robotType][2][0] != "No Args Selected":
                numberOfArg = dictTypes[robotType][2][0].split('|')
                tempSpin.setValue(len(numberOfArg))
            else:
                tempSpin.setValue(0)
            tempSpin.valueChanged.connect(self.updateTree)
            self.spinTypeDict[robotType] = tempSpin
            self.labelTypeDict[robotType] =tempLabel
            self.gridRobotType.addWidget(tempLabel, index, 0)
            self.gridRobotType.addWidget(tempSpin, index, 1)

        #Initiliase the tree widget where the user will be able to set the arguments
        self.updateTree()


    #Used to detect when the window size is changed
    def resizeEvent(self, QResizeEvent):
        self.setTableSize()


    #Corrects the column header sizes
    def setTableSize(self):
        self.treeRobotType.setColumnWidth(0, self.width() / 3.3)
        self.treeRobotType.setColumnWidth(1, self.width() / 3.3)
        self.treeRobotType.setColumnWidth(2, self.width() / 3.3)


    #Updates and displays the current list of robots with their assigned arguments
    def updateTree(self):

        #Delete all the previous items which populated the tree
        self.treeRobotType.clear()

        #Loop on all robotType
        for robotType in self.dictTypes.keys():

            #Create the top robot type item
            tempTypeItem = QtWidgets.QTreeWidgetItem()
            tempTypeItem.setText(0,robotType)

            #Loop over all IPs who are of this type
            for index,IP,USER in zip(range(len(self.dictTypes[robotType][0])),self.dictTypes[robotType][0],self.dictTypes[robotType][1]):

                #Create the IP child of the current robot type
                tempIpUserItem = QtWidgets.QTreeWidgetItem()
                tempIpUserItem.setText(0,IP)

                #Check if there is already some arguments setup for the IP address in the Main Window
                #Loop over the number of arguments setup by the user for the current robot type
                for indexArg in range(self.spinTypeDict[robotType].value()):
                    tempArgument = QtWidgets.QTreeWidgetItem()


                    #If there are no arguments already setup just create the number of arguments defined by the spinbox for this IP
                    if self.dictTypes[robotType][2][0] == "No Args Selected":
                        tempArgument.setText(0, "$"+str(indexArg))
                        tempArgument.setText(1, '')
                        tempArgument.setText(2, '')
                        tempArgument.setExpanded(True)
                        tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(200, 50, 50)))
                        tempIpUserItem.addChild(tempArgument)

                    #If there are arguments already setup just check if the new item can be created with these already setup arguments
                    elif len(self.dictTypes[robotType][2][index].split('|'))-1 >= indexArg:

                        argumentLine = self.dictTypes[robotType][2][index]
                        tempArgumentList = argumentLine.split("|")
                        onlyArgTextColumn = tempArgumentList[indexArg].replace('#', ':')
                        onlyArgText =':'.join(onlyArgTextColumn.split(':')[1:])
                        onlyVariableText = onlyArgTextColumn.split(':')[0]
                        onlyVariableList = onlyVariableText.split('/')
                        if len(onlyVariableList ) == 2:
                            tempArgument.setText(1, onlyVariableList[1])
                        tempArgument.setText(0,onlyVariableList[0])
                        tempArgument.setText(2, onlyArgText)
                        if onlyArgText.strip() == "":
                            tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(200, 50, 50)))

                        else:
                            tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(100, 255, 100)))
                        tempIpUserItem.addChild(tempArgument)

                    #Else just create a new empty argument item
                    else:
                        tempArgument.setText(0, "$" + str(indexArg))
                        tempArgument.setText(1, '')
                        tempArgument.setText(2, '')
                        tempArgument.setExpanded(True)
                        tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(200, 50, 50)))
                        tempIpUserItem.addChild(tempArgument)

                tempTypeItem.addChild(tempIpUserItem)

            self.treeRobotType.addTopLevelItem(tempTypeItem)

        #Change the tree graphic property
        self.treeRobotType.expandAll()


    #This function lets the user modify the arguments slot in column 1 by double clicking on it
    def editItem(self, item, column):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        if (column != 1 and column != 2) or str(item.text(0))[0] != "$":
            item.setFlags(item.flags()  & ~QtCore.Qt.ItemIsEditable)


    #Create the list of arguments which will populate the comboboxes in Main Window
    def createArgumentResume(self):
        self.argumentList[:] = []


        #Loop over the list of all IPs
        for index, IP in enumerate(self.ipList):

            #Loop over the robot type item in the tree widget to gather all the robot types
            for topItemTypeIndex in range(self.treeRobotType.topLevelItemCount()):
                topItemType  = self.treeRobotType.topLevelItem(topItemTypeIndex)

                #Loop over the IP item in each robot type
                for itemIpIndex in range(topItemType.childCount()):
                    itemIp = topItemType.child(itemIpIndex)

                    #Compare the IP item with the IP of the complete IP list in order to find the IP key (index)
                    if IP == itemIp.text(0):
                        self.argumentResume = ""

                        if itemIp.childCount() != 0:
                            
                            #Register all the arguments for the current IP and add it to the resume
                            for itemArgIndex in range(itemIp.childCount()):
                                itemArg = itemIp.child(itemArgIndex)

                                if itemArgIndex != itemIp.childCount()-1:

                                    if itemArg.text(1).strip() == "":
                                        self.argumentResume = self.argumentResume + str(itemArg.text(0))+":"+ str(itemArg.text(2).strip())+'|'

                                    else:
                                        self.argumentResume = self.argumentResume + str(itemArg.text(0))+"/"+  itemArg.text(1).strip() + ":" + str(itemArg.text(2).strip()) + '|'

                                else:

                                    if itemArg.text(1).strip() == "":
                                        self.argumentResume = self.argumentResume + str(itemArg.text(0)) +":"+ str(itemArg.text(2).strip())

                                    else:
                                        self.argumentResume = self.argumentResume + str(itemArg.text(0)) + "/" + itemArg.text(1).strip() + ":" + str(itemArg.text(2).strip())

                            self.dictTypes[topItemType.text(0)][2][itemIpIndex] = self.argumentResume

                        else:
                            self.argumentResume = "No Args Selected"
                        self.argumentList.append(self.argumentResume)


    #Updates the the argument lines in the Argument terminal to red if there is an argument missing
    # or green if the argument is found. It also updates the temporary dictionary and the variable name for every argument of the same robot type
    def changeArgument(self, item, column):
        self.treeRobotType.itemChanged.disconnect()
        duplicateName = False

        if str(item.text(0)[0].strip()) == '$':

            if column == 1:

                rowArgument = item.parent().indexOfChild(item)

                for index in range(item.parent().childCount()):
                    if item.parent().child(index).text(1).strip() == item.text(1) and index != rowArgument:
                        duplicateName = True
                        item.setText(1, "")

                if not duplicateName:
                    parentItemType = item
                    while parentItemType.parent() != None:
                        parentItemType = parentItemType.parent()

                    for ipItemIndex in range(parentItemType.childCount()):
                        ipItem = parentItemType.child(ipItemIndex)

                        if item != ipItem:
                            ipItem.child(rowArgument).setText(1, item.text(column))


            #If the argument is blank
            if str(item.text(2).strip()) == '':

                #Red
                item.setBackground(2, QtGui.QBrush(QtGui.QColor(200, 50, 50)))

            #Argument is not blank
            else:

                #Green
                item.setBackground(2, QtGui.QBrush(QtGui.QColor(100, 255, 100)))

        self.treeRobotType.itemChanged.connect(self.changeArgument)
        if not duplicateName:
            self.createArgumentResume()

        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "Can't have arguments with the same name")


    #Check if there is still a new argument which is empty. Return "" if there is no error otherwise return IP and argument name with the string:"still empty"
    def checkArguments(self):
        errorString = ""

        #Loop through the tree
        for topItemTypeIndex in range(self.treeRobotType.topLevelItemCount()):
            topItemType = self.treeRobotType.topLevelItem(topItemTypeIndex)

            #Loop through all robots for the indexed robot type
            for itemIpIndex in range(topItemType.childCount()):
                itemIp = topItemType.child(itemIpIndex)
                if itemIp.childCount() != 0:

                    #Loop through all arguments for the indexed robot
                    for itemArgIndex in range(itemIp.childCount()):
                        itemArg = itemIp.child(itemArgIndex)
                        if str(itemArg.text(2)) == "":
                            errorString = errorString +str(topItemType.text(0))+" "+ str(itemIp.text(0)) +" "+ str(itemArg.text(0))+" still empty \n"

        return errorString


    #Save all current arguments in the resume and send it to the Main Window, if there is still an empty new argument send a warning
    def saveArguments(self):
        argumentsWellformed = self.checkArguments()
        if argumentsWellformed == "":
            self.createArgumentResume()
            self.saveArgs.emit(self.argumentList)
            self.close()
            self.deleteLater()
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", argumentsWellformed)


    #Close and kill the window
    def cancelArguments(self):
        self.close()
        self.deleteLater()
