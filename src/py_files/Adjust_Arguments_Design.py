# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Adjust_Arguments_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1050, 843)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollareaRobotType = QtWidgets.QScrollArea(Dialog)
        self.scrollareaRobotType.setMaximumSize(QtCore.QSize(16777215, 200))
        self.scrollareaRobotType.setWidgetResizable(True)
        self.scrollareaRobotType.setObjectName("scrollareaRobotType")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1030, 198))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayoutWidget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(310, 30, 160, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridRobotType = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridRobotType.setObjectName("gridRobotType")
        self.scrollareaRobotType.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollareaRobotType, 0, 0, 1, 1)
        self.treeRobotType = QtWidgets.QTreeWidget(Dialog)
        self.treeRobotType.setColumnCount(3)
        self.treeRobotType.setObjectName("treeRobotType")
        self.treeRobotType.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        self.treeRobotType.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.treeRobotType, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonCancel = QtWidgets.QPushButton(Dialog)
        self.buttonCancel.setAutoDefault(False)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.buttonSave = QtWidgets.QPushButton(Dialog)
        self.buttonSave.setAutoDefault(False)
        self.buttonSave.setObjectName("buttonSave")
        self.horizontalLayout.addWidget(self.buttonSave)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.treeRobotType.headerItem().setText(0, _translate("Dialog", "Type Column"))
        self.treeRobotType.headerItem().setText(1, _translate("Dialog", "Argument Column"))
        self.treeRobotType.headerItem().setText(2, _translate("Dialog", "Argument Column"))
        self.buttonCancel.setText(_translate("Dialog", "Cancel"))
        self.buttonSave.setText(_translate("Dialog", "Save"))

