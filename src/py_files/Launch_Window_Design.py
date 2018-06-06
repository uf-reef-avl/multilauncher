# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Launch_Window_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(886, 604)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLaunch = QtWidgets.QVBoxLayout()
        self.verticalLaunch.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLaunch.setObjectName("verticalLaunch")
        self.tab_Launch = QtWidgets.QTabWidget(Dialog)
        self.tab_Launch.setObjectName("tab_Launch")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tab_Launch.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_Launch.addTab(self.tab_2, "")
        self.verticalLaunch.addWidget(self.tab_Launch)
        self.gridLayout.addLayout(self.verticalLaunch, 0, 0, 1, 1)
        self.buttonStopThread = QtWidgets.QPushButton(Dialog)
        self.buttonStopThread.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonStopThread.setObjectName("buttonStopThread")
        self.gridLayout.addWidget(self.buttonStopThread, 2, 0, 1, 1)
        self.lineDebugCommand = QtWidgets.QLineEdit(Dialog)
        self.lineDebugCommand.setObjectName("lineDebugCommand")
        self.gridLayout.addWidget(self.lineDebugCommand, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tab_Launch.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.tab_Launch.setTabText(self.tab_Launch.indexOf(self.tab), _translate("Dialog", "Tab 1"))
        self.tab_Launch.setTabText(self.tab_Launch.indexOf(self.tab_2), _translate("Dialog", "Tab 2"))
        self.buttonStopThread.setText(_translate("Dialog", "Stop all the unfinished thread"))

