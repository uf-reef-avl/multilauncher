# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/matthewh/multilauncher/src/ui_files/Edit_Robot_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_robotEditDialog(object):
    def setupUi(self, robotEditDialog):
        robotEditDialog.setObjectName("robotEditDialog")
        robotEditDialog.resize(1189, 477)
        self.gridLayout_2 = QtWidgets.QGridLayout(robotEditDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(robotEditDialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.label_3 = QtWidgets.QLabel(robotEditDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.typeEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.typeEdit.setObjectName("typeEdit")
        self.gridLayout_2.addWidget(self.typeEdit, 2, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(robotEditDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.nameEdit.setObjectName("nameEdit")
        self.gridLayout_2.addWidget(self.nameEdit, 2, 1, 1, 1)
        self.ipEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.ipEdit.setObjectName("ipEdit")
        self.gridLayout_2.addWidget(self.ipEdit, 2, 0, 1, 1)
        self.modifyRobotButton = QtWidgets.QPushButton(robotEditDialog)
        self.modifyRobotButton.setAutoDefault(False)
        self.modifyRobotButton.setObjectName("modifyRobotButton")
        self.gridLayout_2.addWidget(self.modifyRobotButton, 3, 1, 1, 1)
        self.addRobotButton = QtWidgets.QPushButton(robotEditDialog)
        self.addRobotButton.setAutoDefault(False)
        self.addRobotButton.setObjectName("addRobotButton")
        self.gridLayout_2.addWidget(self.addRobotButton, 3, 0, 1, 1)
        self.robotTable = QtWidgets.QTableWidget(robotEditDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.robotTable.sizePolicy().hasHeightForWidth())
        self.robotTable.setSizePolicy(sizePolicy)
        self.robotTable.setLineWidth(1)
        self.robotTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.robotTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.robotTable.setObjectName("robotTable")
        self.robotTable.setColumnCount(5)
        self.robotTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.robotTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.robotTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.robotTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.robotTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.robotTable.setHorizontalHeaderItem(4, item)
        self.robotTable.horizontalHeader().setDefaultSectionSize(150)
        self.robotTable.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.robotTable, 0, 0, 1, 3)
        self.resultLabel = QtWidgets.QLabel(robotEditDialog)
        self.resultLabel.setWordWrap(True)
        self.resultLabel.setObjectName("resultLabel")
        self.gridLayout_2.addWidget(self.resultLabel, 5, 0, 2, 3)
        self.deleteRobotButton = QtWidgets.QPushButton(robotEditDialog)
        self.deleteRobotButton.setAutoDefault(False)
        self.deleteRobotButton.setObjectName("deleteRobotButton")
        self.gridLayout_2.addWidget(self.deleteRobotButton, 3, 2, 1, 1)
        self.saveAndExitButton = QtWidgets.QPushButton(robotEditDialog)
        self.saveAndExitButton.setAutoDefault(False)
        self.saveAndExitButton.setObjectName("saveAndExitButton")
        self.gridLayout_2.addWidget(self.saveAndExitButton, 4, 2, 1, 1)

        self.retranslateUi(robotEditDialog)
        QtCore.QMetaObject.connectSlotsByName(robotEditDialog)

    def retranslateUi(self, robotEditDialog):
        _translate = QtCore.QCoreApplication.translate
        robotEditDialog.setWindowTitle(_translate("robotEditDialog", "Edit Robots"))
        self.label.setText(_translate("robotEditDialog", "New/Selected: IP Address"))
        self.label_3.setText(_translate("robotEditDialog", "New/Selected: Robot Type"))
        self.label_2.setText(_translate("robotEditDialog", "New/Selected: Robot Name"))
        self.modifyRobotButton.setText(_translate("robotEditDialog", "Modify Robot"))
        self.addRobotButton.setText(_translate("robotEditDialog", "Add Robot"))
        item = self.robotTable.horizontalHeaderItem(0)
        item.setText(_translate("robotEditDialog", "Enabled"))
        item = self.robotTable.horizontalHeaderItem(1)
        item.setText(_translate("robotEditDialog", "Robot\'s Ip Address"))
        item = self.robotTable.horizontalHeaderItem(2)
        item.setText(_translate("robotEditDialog", "Robot\'s Name/User"))
        item = self.robotTable.horizontalHeaderItem(3)
        item.setText(_translate("robotEditDialog", "Robot\'s Type/Configuration"))
        item = self.robotTable.horizontalHeaderItem(4)
        item.setText(_translate("robotEditDialog", "ROS Settings"))
        self.resultLabel.setText(_translate("robotEditDialog", "Result:"))
        self.deleteRobotButton.setText(_translate("robotEditDialog", "Delete Robot"))
        self.saveAndExitButton.setText(_translate("robotEditDialog", "Save and Exit"))

