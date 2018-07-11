#
# File: Adjust_Arguments.py
# Author: Paul Buzaud
#
# Created:
#



import Adjust_Arguments_Design
from PyQt5 import QtCore, QtGui, QtWidgets



#This window is used to set the arguments which will be replaced in the commands lines
class Adjust_Arguments(QtWidgets.QDialog, Adjust_Arguments_Design.Ui_Dialog):
    saveArgs = QtCore.pyqtSignal(list)


    #Definition of the Adjust_Arguments terminal
    def __init__(self,ipList, dictTypes, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        #initialise the useful values of the current case
        self.dictTypes = dictTypes
        self.ipList = ipList
        self. argumentResume = ''
        self.spinTypeDict = {}
        self.labelTypeDict = {}
        self.argumentList = []

        #connect every button to his correct slot
        self.treeRobotType.itemClicked.connect(self.editItem)
        self.treeRobotType.itemChanged.connect(self.changeArgument)
        self.buttonSave.clicked.connect(self.saveArguments)
        self.buttonCancel.clicked.connect(self.cancelArguments)

        #initialise the area where the user can change the number of argument for each robot type
        self.area = QtWidgets.QWidget()
        self.area.setLayout(self.gridRobotType)
        self.scrollareaRobotType.setWidget(self.area)
        self.scrollareaRobotType.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollareaRobotType.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        for index, type in enumerate(self.dictTypes.keys()):
            tempLabel = QtWidgets.QLabel(self)
            tempLabel.setText("Number of arguments for the type : "+ type)
            tempSpin = QtWidgets.QSpinBox(self)
            if self.dictTypes[type][2][0] != "No Args Selected":
                numberOfArg = dictTypes[type][2][0].split('|')
                tempSpin.setValue(len(numberOfArg))
            else:
                tempSpin.setValue(0)
            tempSpin.valueChanged.connect(self.updateTree)
            self.spinTypeDict[type] = tempSpin
            self.labelTypeDict[type] =tempLabel
            self.gridRobotType.addWidget(tempLabel, index, 0)
            self.gridRobotType.addWidget(tempSpin, index, 1)

        #initiliase the tree widget where the user will be able to set the arguments
        self.updateTree()


    # Used to detect when the window size is changed
    def resizeEvent(self, QResizeEvent):
        self.setTableSize()


    # Corrects the column header sizes
    def setTableSize(self):
        self.treeRobotType.setColumnWidth(0, self.width() / 3.2)
        self.treeRobotType.setColumnWidth(1, self.width() / 3.2)
        self.treeRobotType.setColumnWidth(2, self.width() / 3.2)


    #Updates and displays the current list of robots with their assigned arguments
    def updateTree(self):

        #delete all the previous item which populated the tree
        self.treeRobotType.clear()

        #loop on all type
        for type in self.dictTypes.keys():

            #create the top type item
            tempTypeItem = QtWidgets.QTreeWidgetItem()
            tempTypeItem.setText(0,type)

            #loop on all IP who are of this type
            for index,IP,USER in zip(range(len(self.dictTypes[type][0])),self.dictTypes[type][0],self.dictTypes[type][1]):

                #create the IP child of the current type
                tempIpUserItem = QtWidgets.QTreeWidgetItem()
                tempIpUserItem.setText(0,IP)

                #check if there is already some arguments setup for the IP address in the MainWindow
                #loop on the number of argument setup by the user for the current type
                for indexArg in range(self.spinTypeDict[type].value()):
                    tempArgument = QtWidgets.QTreeWidgetItem()


                    #if there is no argument already setup just create the right number of argument defined by the spinbox for this IP
                    if self.dictTypes[type][2][0] == "No Args Selected":
                        tempArgument.setText(0, "$"+str(indexArg))
                        tempArgument.setText(1, '')
                        tempArgument.setText(2, '')
                        tempArgument.setExpanded(True)
                        tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(204, 51, 51)))
                        tempIpUserItem.addChild(tempArgument)

                    #if there is argument already setup just check if the new item can be created with these already setup arguments
                    elif len(self.dictTypes[type][2][index].split('|'))-1 >= indexArg:

                        argumentLine = self.dictTypes[type][2][index]
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
                            tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(204, 51, 51)))

                        else:
                            tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(154, 255, 154)))
                        tempIpUserItem.addChild(tempArgument)

                    #else just create a new empty argument item
                    else:
                        tempArgument.setText(0, "$" + str(indexArg))
                        tempArgument.setText(1, '')
                        tempArgument.setText(2, '')
                        tempArgument.setExpanded(True)
                        tempArgument.setBackground(2, QtGui.QBrush(QtGui.QColor(204, 51, 51)))
                        tempIpUserItem.addChild(tempArgument)

                tempTypeItem.addChild(tempIpUserItem)

            self.treeRobotType.addTopLevelItem(tempTypeItem)

        #change the tree graphic property
        self.treeRobotType.expandAll()
        self.treeRobotType.setColumnWidth(0, 500)


    #This function let the user modify the arguments slot in column 1 by double clicking on it
    def editItem(self, item, column):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        if (column != 1 and column != 2) or str(item.text(0))[0] != "$":
            item.setFlags(item.flags()  & ~QtCore.Qt.ItemIsEditable)


    #Create the text of arguments which will populate the QPlainText in MainWindow
    def createArgumentResume(self):
        self.argumentList[:] = []


        #loop on the Ip global MainWindow
        for index, IP in enumerate(self.ipList):

            #loop on the type item in the tree widget to gather all the type
            for topItemTypeIndex in range(self.treeRobotType.topLevelItemCount()):
                topItemType  = self.treeRobotType.topLevelItem(topItemTypeIndex)

                #loop on the IP item in each type
                for itemIpIndex in range(topItemType.childCount()):
                    itemIp = topItemType.child(itemIpIndex)

                    #compare the IPItem with IP of the global MainWindow list in order to find the IP key (index)
                    if IP == itemIp.text(0):
                        self.argumentResume = ""
                        if itemIp.childCount() != 0:
                            #register all the argument for the current IP and add it to the resume
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
    # or green if the argument is found. It also updates the temporary dictionary and the variable name for every argumen of the same type
    def changeArgument(self, item, column):

        if str(item.text(0)[0].strip()) == '$':
            if column == 1:
                rowArgument = item.parent().indexOfChild(item)
                parentItemType = item
                while(parentItemType.parent() != None ):
                    parentItemType = parentItemType.parent()
                for ipItemIndex in range(parentItemType.childCount()):
                    ipItem = parentItemType.child(ipItemIndex)
                    if(item != ipItem):
                        ipItem.child(rowArgument).setText(1,item.text(column))

            if str(item.text(2).strip()) == '':
                item.setBackground(2, QtGui.QBrush(QtGui.QColor(204, 51, 51)))
            else:
                item.setBackground(2, QtGui.QBrush(QtGui.QColor(154, 255, 154)))
        self.createArgumentResume()


    #Check if there is still a new argument which is empty. Return "" if there is no error otherwise return IP and argument name with the string:"still empty"
    def checkArguments(self):
        errorString = ""
        for topItemTypeIndex in range(self.treeRobotType.topLevelItemCount()):
            topItemType = self.treeRobotType.topLevelItem(topItemTypeIndex)
            for itemIpIndex in range(topItemType.childCount()):
                itemIp = topItemType.child(itemIpIndex)
                if itemIp.childCount() != 0:
                    for itemArgIndex in range(itemIp.childCount()):
                        itemArg = itemIp.child(itemArgIndex)
                        if str(itemArg.text(2)) == "":
                            errorString = errorString +str(topItemType.text(0))+" "+ str(itemIp.text(0)) +" "+ str(itemArg.text(0))+" still empty \n"

        return errorString


    #Save all current arguments in the resume and send it to the main window. If there is still an empty nw arguement do nothing and send a warning
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
