# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Generate_Key_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(704, 432)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.rsaProgressBar = QtWidgets.QProgressBar(Dialog)
        self.rsaProgressBar.setProperty("value", 24)
        self.rsaProgressBar.setObjectName("rsaProgressBar")
        self.gridLayout_2.addWidget(self.rsaProgressBar, 1, 0, 1, 1)
        self.gridSpecifyUserPassword = QtWidgets.QGridLayout()
        self.gridSpecifyUserPassword.setObjectName("gridSpecifyUserPassword")
        self.labelUsername = QtWidgets.QLabel(Dialog)
        self.labelUsername.setObjectName("labelUsername")
        self.gridSpecifyUserPassword.addWidget(self.labelUsername, 0, 0, 1, 1)
        self.labelPassword = QtWidgets.QLabel(Dialog)
        self.labelPassword.setObjectName("labelPassword")
        self.gridSpecifyUserPassword.addWidget(self.labelPassword, 1, 0, 1, 1)
        self.lineEditPassword = QtWidgets.QLineEdit(Dialog)
        self.lineEditPassword.setObjectName("lineEditPassword")
        self.gridSpecifyUserPassword.addWidget(self.lineEditPassword, 1, 1, 1, 1)
        self.lineEditUsername = QtWidgets.QLineEdit(Dialog)
        self.lineEditUsername.setObjectName("lineEditUsername")
        self.gridSpecifyUserPassword.addWidget(self.lineEditUsername, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridSpecifyUserPassword, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonCancel = QtWidgets.QPushButton(Dialog)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.buttonGenerateKey = QtWidgets.QPushButton(Dialog)
        self.buttonGenerateKey.setObjectName("buttonGenerateKey")
        self.horizontalLayout.addWidget(self.buttonGenerateKey)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.instructionslabel = QtWidgets.QLabel(Dialog)
        self.instructionslabel.setObjectName("instructionslabel")
        self.gridLayout_2.addWidget(self.instructionslabel, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEditUsername, self.lineEditPassword)
        Dialog.setTabOrder(self.lineEditPassword, self.buttonCancel)
        Dialog.setTabOrder(self.buttonCancel, self.buttonGenerateKey)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.labelUsername.setText(_translate("Dialog", "Enter your admin username"))
        self.labelPassword.setText(_translate("Dialog", "Enter your admin password"))
        self.buttonCancel.setText(_translate("Dialog", "Cancel"))
        self.buttonGenerateKey.setText(_translate("Dialog", "Generate Key"))
        self.instructionslabel.setText(_translate("Dialog", "Enter your admin password and username to generate the RSA Key \n"
"\n"
"(When generating the RSA Key the ownership of the ~/.ssh directory on the \n"
" remote machine will be set to the user and the file permissions will be set to default)"))

