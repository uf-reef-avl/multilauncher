# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Password_Window_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(901, 440)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 881, 360))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayoutWidget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(190, 160, 160, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridPasswords = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridPasswords.setObjectName("gridPasswords")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 2, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_password = QtWidgets.QLabel(Dialog)
        self.label_password.setObjectName("label_password")
        self.verticalLayout.addWidget(self.label_password)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_generate_RSA = QtWidgets.QPushButton(Dialog)
        self.button_generate_RSA.setObjectName("button_generate_RSA")
        self.horizontalLayout_2.addWidget(self.button_generate_RSA)
        self.launchButton = QtWidgets.QPushButton(Dialog)
        self.launchButton.setObjectName("launchButton")
        self.horizontalLayout_2.addWidget(self.launchButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_password.setText(_translate("Dialog", "In order to launch the command,  specify the devices\'s password or generate a rsa key:"))
        self.button_generate_RSA.setText(_translate("Dialog", "Generate Rsa key"))
        self.launchButton.setText(_translate("Dialog", "Launch the command"))

