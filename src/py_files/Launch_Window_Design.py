# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/matthewh/multilauncher/src/ui_files/Launch_Window_Design.ui'
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
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.debugLabel = QtWidgets.QLabel(Dialog)
        self.debugLabel.setObjectName("debugLabel")
        self.horizontalLayout.addWidget(self.debugLabel)
        self.lineDebugCommand = QtWidgets.QLineEdit(Dialog)
        self.lineDebugCommand.setObjectName("lineDebugCommand")
        self.horizontalLayout.addWidget(self.lineDebugCommand)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.stopCurrentThread = QtWidgets.QPushButton(Dialog)
        self.stopCurrentThread.setAutoDefault(False)
        self.stopCurrentThread.setObjectName("stopCurrentThread")
        self.horizontalLayout_2.addWidget(self.stopCurrentThread)
        self.buttonStopThread = QtWidgets.QPushButton(Dialog)
        self.buttonStopThread.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonStopThread.setAutoDefault(False)
        self.buttonStopThread.setObjectName("buttonStopThread")
        self.horizontalLayout_2.addWidget(self.buttonStopThread)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 1, 1, 1)
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
        self.gridLayout.addWidget(self.tab_Launch, 1, 1, 1, 1)
        self.saveTerminalOutput = QtWidgets.QPushButton(Dialog)
        self.saveTerminalOutput.setAutoDefault(False)
        self.saveTerminalOutput.setObjectName("saveTerminalOutput")
        self.gridLayout.addWidget(self.saveTerminalOutput, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.tab_Launch.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Launch Window"))
        self.debugLabel.setText(_translate("Dialog", "Command Line:"))
        self.stopCurrentThread.setText(_translate("Dialog", "Stop Current Thread"))
        self.buttonStopThread.setText(_translate("Dialog", "Stop All Unfinished Threads"))
        self.tab_Launch.setTabText(self.tab_Launch.indexOf(self.tab), _translate("Dialog", "Tab 1"))
        self.tab_Launch.setTabText(self.tab_Launch.indexOf(self.tab_2), _translate("Dialog", "Tab 2"))
        self.saveTerminalOutput.setText(_translate("Dialog", "Save Terminal Output"))

