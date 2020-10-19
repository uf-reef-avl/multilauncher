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
        Dialog.resize(971, 482)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.instructionslabel = QtWidgets.QLabel(Dialog)
        self.instructionslabel.setAlignment(QtCore.Qt.AlignCenter)
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
        Dialog.setWindowTitle(_translate("Dialog", "Generate RSA Key"))
        self.instructionslabel.setText(_translate("Dialog", "<html><head/><body><p align=\"center\">When generating a new RSA key the following occurs:</p><p align=\"center\">1. The &quot;~/.ssh&quot; directory, &quot;multikey&quot;, and &quot;multikey.pub&quot; RSA keys are created if not already present on the local machine.</p><p align=\"center\">2. The RSA keys are added to the local ssh-agent\'s keyring if not automatically added by the operating system.</p><p align=\"center\">3. The &quot;multikey.pub&quot; is added to the &quot;authorized_keys&quot; file on the remote machine(s) if the public key is not already present.</p></body></html>"))
        self.buttonCancel.setText(_translate("Dialog", "Cancel"))
        self.buttonGenerateKey.setText(_translate("Dialog", "Generate Key"))

