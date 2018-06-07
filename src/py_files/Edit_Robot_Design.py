# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Edit_Robot_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_robotEditDialog(object):
    def setupUi(self, robotEditDialog):
        robotEditDialog.setObjectName("robotEditDialog")
        robotEditDialog.resize(822, 341)
        self.gridLayout_2 = QtWidgets.QGridLayout(robotEditDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.robotTable = QtWidgets.QTableWidget(robotEditDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.robotTable.sizePolicy().hasHeightForWidth())
        self.robotTable.setSizePolicy(sizePolicy)
        self.robotTable.setLineWidth(1)
        self.robotTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.robotTable.setObjectName("robotTable")
        self.robotTable.setColumnCount(3)
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
        self.robotTable.horizontalHeader().setDefaultSectionSize(150)
        self.robotTable.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.robotTable, 0, 1, 1, 3)
        self.deleteRobotButton = QtWidgets.QPushButton(robotEditDialog)
        self.deleteRobotButton.setAutoDefault(False)
        self.deleteRobotButton.setObjectName("deleteRobotButton")
        self.gridLayout_2.addWidget(self.deleteRobotButton, 0, 4, 1, 1)
        self.selectedLabel = QtWidgets.QLabel(robotEditDialog)
        self.selectedLabel.setObjectName("selectedLabel")
        self.gridLayout_2.addWidget(self.selectedLabel, 1, 0, 1, 1)
        self.ipEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.ipEdit.setObjectName("ipEdit")
        self.gridLayout_2.addWidget(self.ipEdit, 1, 1, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.nameEdit.setObjectName("nameEdit")
        self.gridLayout_2.addWidget(self.nameEdit, 1, 2, 1, 1)
        self.typeEdit = QtWidgets.QLineEdit(robotEditDialog)
        self.typeEdit.setObjectName("typeEdit")
        self.gridLayout_2.addWidget(self.typeEdit, 1, 3, 1, 1)
        self.addRobotButton = QtWidgets.QPushButton(robotEditDialog)
        self.addRobotButton.setAutoDefault(False)
        self.addRobotButton.setObjectName("addRobotButton")
        self.gridLayout_2.addWidget(self.addRobotButton, 2, 1, 1, 1)
        self.resultLabel = QtWidgets.QLabel(robotEditDialog)
        self.resultLabel.setWordWrap(True)
        self.resultLabel.setObjectName("resultLabel")
        self.gridLayout_2.addWidget(self.resultLabel, 2, 2, 2, 2)
        self.saveAndExitButton = QtWidgets.QPushButton(robotEditDialog)
        self.saveAndExitButton.setAutoDefault(False)
        self.saveAndExitButton.setObjectName("saveAndExitButton")
        self.gridLayout_2.addWidget(self.saveAndExitButton, 2, 4, 1, 1)

        self.retranslateUi(robotEditDialog)
        QtCore.QMetaObject.connectSlotsByName(robotEditDialog)

    def retranslateUi(self, robotEditDialog):
        _translate = QtCore.QCoreApplication.translate
        robotEditDialog.setWindowTitle(_translate("robotEditDialog", "Dialog"))
        item = self.robotTable.horizontalHeaderItem(0)
        item.setText(_translate("robotEditDialog", "Robot\'s Ip Address"))
        item = self.robotTable.horizontalHeaderItem(1)
        item.setText(_translate("robotEditDialog", "Robot\'s Name/User"))
        item = self.robotTable.horizontalHeaderItem(2)
        item.setText(_translate("robotEditDialog", "Robot\'s Type/Configuration"))
        self.deleteRobotButton.setText(_translate("robotEditDialog", "Delete Robot"))
        self.selectedLabel.setText(_translate("robotEditDialog", "Selected:"))
        self.addRobotButton.setText(_translate("robotEditDialog", "Add Robot"))
        self.resultLabel.setText(_translate("robotEditDialog", "Result:"))
        self.saveAndExitButton.setText(_translate("robotEditDialog", "Save and Exit"))

