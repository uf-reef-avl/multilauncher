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
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.instructionslabel = QtWidgets.QLabel(Dialog)
        self.instructionslabel.setObjectName("instructionslabel")
        self.verticalLayout.addWidget(self.instructionslabel)
        self.rsaProgressBar = QtWidgets.QProgressBar(Dialog)
        self.rsaProgressBar.setProperty("value", 24)
        self.rsaProgressBar.setObjectName("rsaProgressBar")
        self.verticalLayout.addWidget(self.rsaProgressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonCancel = QtWidgets.QPushButton(Dialog)
        self.buttonCancel.setAutoDefault(False)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.buttonGenerateKey = QtWidgets.QPushButton(Dialog)
        self.buttonGenerateKey.setAutoDefault(False)
        self.buttonGenerateKey.setObjectName("buttonGenerateKey")
        self.horizontalLayout.addWidget(self.buttonGenerateKey)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 3, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.buttonCancel, self.buttonGenerateKey)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.instructionslabel.setText(_translate("Dialog", "When generating the RSA Key the ownership of the ~/.ssh directory on the \n"
" remote machine will be set to the remote user and the file permissions will be set to default"))
        self.buttonCancel.setText(_translate("Dialog", "Cancel"))
        self.buttonGenerateKey.setText(_translate("Dialog", "Generate Key"))

