# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Multilauncher.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1345, 785)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setHorizontalSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setHorizontalSpacing(1)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.loadcommandsbutton = QtWidgets.QPushButton(self.centralwidget)
        self.loadcommandsbutton.setObjectName("loadcommandsbutton")
        self.gridLayout_4.addWidget(self.loadcommandsbutton, 2, 0, 1, 1)
        self.commands = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commands.sizePolicy().hasHeightForWidth())
        self.commands.setSizePolicy(sizePolicy)
        self.commands.setMinimumSize(QtCore.QSize(610, 0))
        self.commands.setObjectName("commands")
        self.gridLayout_4.addWidget(self.commands, 1, 0, 1, 3)
        self.savecommandsbutton = QtWidgets.QPushButton(self.centralwidget)
        self.savecommandsbutton.setObjectName("savecommandsbutton")
        self.gridLayout_4.addWidget(self.savecommandsbutton, 3, 0, 1, 1)
        self.rsacheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.rsacheckbox.setObjectName("rsacheckbox")
        self.gridLayout_4.addWidget(self.rsacheckbox, 3, 2, 1, 1)
        self.launchbutton = QtWidgets.QPushButton(self.centralwidget)
        self.launchbutton.setObjectName("launchbutton")
        self.gridLayout_4.addWidget(self.launchbutton, 2, 2, 1, 1)
        self.commandeditorlabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.commandeditorlabel.setFont(font)
        self.commandeditorlabel.setObjectName("commandeditorlabel")
        self.gridLayout_4.addWidget(self.commandeditorlabel, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
        self.commandFileLable = QtWidgets.QLabel(self.centralwidget)
        self.commandFileLable.setObjectName("commandFileLable")
        self.gridLayout_4.addWidget(self.commandFileLable, 0, 2, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_4, 2, 2, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(-1, -1, 0, 0)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.robotaddress = QtWidgets.QLabel(self.centralwidget)
        self.robotaddress.setObjectName("robotaddress")
        self.gridLayout.addWidget(self.robotaddress, 3, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.argumentlist = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.argumentlist.sizePolicy().hasHeightForWidth())
        self.argumentlist.setSizePolicy(sizePolicy)
        self.argumentlist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.argumentlist.setReadOnly(True)
        self.argumentlist.setObjectName("argumentlist")
        self.gridLayout.addWidget(self.argumentlist, 4, 4, 1, 1)
        self.connectionstatus = QtWidgets.QLabel(self.centralwidget)
        self.connectionstatus.setObjectName("connectionstatus")
        self.gridLayout.addWidget(self.connectionstatus, 3, 5, 1, 1, QtCore.Qt.AlignHCenter)
        self.editlistsbutton = QtWidgets.QPushButton(self.centralwidget)
        self.editlistsbutton.setObjectName("editlistsbutton")
        self.gridLayout.addWidget(self.editlistsbutton, 5, 1, 1, 1)
        self.pingrobotsbutton = QtWidgets.QPushButton(self.centralwidget)
        self.pingrobotsbutton.setObjectName("pingrobotsbutton")
        self.gridLayout.addWidget(self.pingrobotsbutton, 5, 5, 1, 1)
        self.filesearchbutton = QtWidgets.QPushButton(self.centralwidget)
        self.filesearchbutton.setObjectName("filesearchbutton")
        self.gridLayout.addWidget(self.filesearchbutton, 1, 4, 1, 1)
        self.argumentlabel = QtWidgets.QLabel(self.centralwidget)
        self.argumentlabel.setObjectName("argumentlabel")
        self.gridLayout.addWidget(self.argumentlabel, 3, 4, 1, 1, QtCore.Qt.AlignHCenter)
        self.robotlistsavebutton = QtWidgets.QPushButton(self.centralwidget)
        self.robotlistsavebutton.setObjectName("robotlistsavebutton")
        self.gridLayout.addWidget(self.robotlistsavebutton, 1, 5, 1, 1)
        self.argumentbutton = QtWidgets.QPushButton(self.centralwidget)
        self.argumentbutton.setObjectName("argumentbutton")
        self.gridLayout.addWidget(self.argumentbutton, 5, 4, 1, 1)
        self.connectionstatuslist = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectionstatuslist.sizePolicy().hasHeightForWidth())
        self.connectionstatuslist.setSizePolicy(sizePolicy)
        self.connectionstatuslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.connectionstatuslist.setReadOnly(True)
        self.connectionstatuslist.setObjectName("connectionstatuslist")
        self.gridLayout.addWidget(self.connectionstatuslist, 4, 5, 1, 1)
        self.robottypelist = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.robottypelist.sizePolicy().hasHeightForWidth())
        self.robottypelist.setSizePolicy(sizePolicy)
        self.robottypelist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.robottypelist.setReadOnly(True)
        self.robottypelist.setObjectName("robottypelist")
        self.gridLayout.addWidget(self.robottypelist, 4, 3, 1, 1)
        self.selectedfilename = QtWidgets.QLabel(self.centralwidget)
        self.selectedfilename.setObjectName("selectedfilename")
        self.gridLayout.addWidget(self.selectedfilename, 1, 3, 1, 1)
        self.robotnamelist = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.robotnamelist.sizePolicy().hasHeightForWidth())
        self.robotnamelist.setSizePolicy(sizePolicy)
        self.robotnamelist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.robotnamelist.setReadOnly(True)
        self.robotnamelist.setObjectName("robotnamelist")
        self.gridLayout.addWidget(self.robotnamelist, 4, 2, 1, 1)
        self.robotaddresslist = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.robotaddresslist.sizePolicy().hasHeightForWidth())
        self.robotaddresslist.setSizePolicy(sizePolicy)
        self.robotaddresslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.robotaddresslist.setReadOnly(True)
        self.robotaddresslist.setObjectName("robotaddresslist")
        self.gridLayout.addWidget(self.robotaddresslist, 4, 1, 1, 1)
        self.robottype = QtWidgets.QLabel(self.centralwidget)
        self.robottype.setObjectName("robottype")
        self.gridLayout.addWidget(self.robottype, 3, 3, 1, 1, QtCore.Qt.AlignHCenter)
        self.robotname = QtWidgets.QLabel(self.centralwidget)
        self.robotname.setObjectName("robotname")
        self.gridLayout.addWidget(self.robotname, 3, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.filebrowsinglabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setKerning(True)
        self.filebrowsinglabel.setFont(font)
        self.filebrowsinglabel.setObjectName("filebrowsinglabel")
        self.gridLayout.addWidget(self.filebrowsinglabel, 1, 1, 1, 1, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 3)
        self.verticalScrollBar = QtWidgets.QScrollBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.verticalScrollBar.sizePolicy().hasHeightForWidth())
        self.verticalScrollBar.setSizePolicy(sizePolicy)
        self.verticalScrollBar.setMinimumSize(QtCore.QSize(20, 0))
        self.verticalScrollBar.setSizeIncrement(QtCore.QSize(0, 100))
        self.verticalScrollBar.setBaseSize(QtCore.QSize(0, 100))
        self.verticalScrollBar.setMaximum(99)
        self.verticalScrollBar.setSingleStep(0)
        self.verticalScrollBar.setSliderPosition(0)
        self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.verticalScrollBar.setInvertedAppearance(False)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.gridLayout.addWidget(self.verticalScrollBar, 4, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 3)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout_2.setContentsMargins(0, 0, 0, -1)
        self.gridLayout_2.setHorizontalSpacing(1)
        self.gridLayout_2.setVerticalSpacing(30)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label, 0, QtCore.Qt.AlignHCenter)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4, 0, QtCore.Qt.AlignHCenter)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3, 0, QtCore.Qt.AlignHCenter)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_4.setStretch(2, 1)
        self.horizontalLayout_4.setStretch(3, 1)
        self.horizontalLayout_4.setStretch(4, 1)
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.remotegitpasswordlabel = QtWidgets.QLabel(self.centralwidget)
        self.remotegitpasswordlabel.setObjectName("remotegitpasswordlabel")
        self.gridLayout_8.addWidget(self.remotegitpasswordlabel, 2, 2, 1, 1, QtCore.Qt.AlignRight)
        self.lineUsername = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineUsername.sizePolicy().hasHeightForWidth())
        self.lineUsername.setSizePolicy(sizePolicy)
        self.lineUsername.setObjectName("lineUsername")
        self.gridLayout_8.addWidget(self.lineUsername, 1, 3, 1, 1)
        self.numofpackageslabel = QtWidgets.QLabel(self.centralwidget)
        self.numofpackageslabel.setObjectName("numofpackageslabel")
        self.gridLayout_8.addWidget(self.numofpackageslabel, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        self.linePasswordn = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linePasswordn.sizePolicy().hasHeightForWidth())
        self.linePasswordn.setSizePolicy(sizePolicy)
        self.linePasswordn.setObjectName("linePasswordn")
        self.gridLayout_8.addWidget(self.linePasswordn, 2, 3, 1, 1)
        self.spinpackage = QtWidgets.QSpinBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinpackage.sizePolicy().hasHeightForWidth())
        self.spinpackage.setSizePolicy(sizePolicy)
        self.spinpackage.setProperty("value", 0)
        self.spinpackage.setObjectName("spinpackage")
        self.gridLayout_8.addWidget(self.spinpackage, 0, 3, 1, 1)
        self.fileTransferLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.fileTransferLabel.setFont(font)
        self.fileTransferLabel.setObjectName("fileTransferLabel")
        self.gridLayout_8.addWidget(self.fileTransferLabel, 0, 0, 3, 1, QtCore.Qt.AlignHCenter)
        self.remotegituserlabel = QtWidgets.QLabel(self.centralwidget)
        self.remotegituserlabel.setObjectName("remotegituserlabel")
        self.gridLayout_8.addWidget(self.remotegituserlabel, 1, 2, 1, 1, QtCore.Qt.AlignRight)
        self.gridLayout_2.addLayout(self.gridLayout_8, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.masterurilable = QtWidgets.QLabel(self.centralwidget)
        self.masterurilable.setObjectName("masterurilable")
        self.horizontalLayout.addWidget(self.masterurilable, 0, QtCore.Qt.AlignRight)
        self.masteruriline = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.masteruriline.sizePolicy().hasHeightForWidth())
        self.masteruriline.setSizePolicy(sizePolicy)
        self.masteruriline.setObjectName("masteruriline")
        self.horizontalLayout.addWidget(self.masteruriline)
        self.bashrcbutton = QtWidgets.QPushButton(self.centralwidget)
        self.bashrcbutton.setObjectName("bashrcbutton")
        self.horizontalLayout.addWidget(self.bashrcbutton)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.scrollareapackage = QtWidgets.QScrollArea(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(250)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollareapackage.sizePolicy().hasHeightForWidth())
        self.scrollareapackage.setSizePolicy(sizePolicy)
        self.scrollareapackage.setWidgetResizable(True)
        self.scrollareapackage.setObjectName("scrollareapackage")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 688, 73))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 20, 351, 141))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridpackage = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridpackage.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridpackage.setObjectName("gridpackage")
        self.gridpackage.setColumnStretch(0, 1)
        self.scrollareapackage.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollareapackage, 2, 0, 1, 1)
        self.buttontransfer = QtWidgets.QPushButton(self.centralwidget)
        self.buttontransfer.setObjectName("buttontransfer")
        self.gridLayout_2.addWidget(self.buttontransfer, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 1, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_2, 2, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem2, 1, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.filesearchbutton, self.robotlistsavebutton)
        MainWindow.setTabOrder(self.robotlistsavebutton, self.robotaddresslist)
        MainWindow.setTabOrder(self.robotaddresslist, self.robotnamelist)
        MainWindow.setTabOrder(self.robotnamelist, self.robottypelist)
        MainWindow.setTabOrder(self.robottypelist, self.argumentlist)
        MainWindow.setTabOrder(self.argumentlist, self.connectionstatuslist)
        MainWindow.setTabOrder(self.connectionstatuslist, self.editlistsbutton)
        MainWindow.setTabOrder(self.editlistsbutton, self.argumentbutton)
        MainWindow.setTabOrder(self.argumentbutton, self.pingrobotsbutton)
        MainWindow.setTabOrder(self.pingrobotsbutton, self.spinpackage)
        MainWindow.setTabOrder(self.spinpackage, self.lineUsername)
        MainWindow.setTabOrder(self.lineUsername, self.linePasswordn)
        MainWindow.setTabOrder(self.linePasswordn, self.scrollareapackage)
        MainWindow.setTabOrder(self.scrollareapackage, self.buttontransfer)
        MainWindow.setTabOrder(self.buttontransfer, self.masteruriline)
        MainWindow.setTabOrder(self.masteruriline, self.bashrcbutton)
        MainWindow.setTabOrder(self.bashrcbutton, self.commands)
        MainWindow.setTabOrder(self.commands, self.loadcommandsbutton)
        MainWindow.setTabOrder(self.loadcommandsbutton, self.savecommandsbutton)
        MainWindow.setTabOrder(self.savecommandsbutton, self.launchbutton)
        MainWindow.setTabOrder(self.launchbutton, self.rsacheckbox)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.loadcommandsbutton.setText(_translate("MainWindow", "Load Commands File"))
        self.savecommandsbutton.setText(_translate("MainWindow", "Save Current Commands"))
        self.rsacheckbox.setText(_translate("MainWindow", "Use RSA Key"))
        self.launchbutton.setText(_translate("MainWindow", "Launch All"))
        self.commandeditorlabel.setText(_translate("MainWindow", "Command Editor"))
        self.commandFileLable.setText(_translate("MainWindow", "Current File:"))
        self.robotaddress.setText(_translate("MainWindow", "Robot\'s IP Address"))
        self.connectionstatus.setText(_translate("MainWindow", "Connection Status"))
        self.editlistsbutton.setText(_translate("MainWindow", "Add/Edit/Remove Robots"))
        self.pingrobotsbutton.setText(_translate("MainWindow", "Ping Robots"))
        self.filesearchbutton.setText(_translate("MainWindow", "Find Robotlist file"))
        self.argumentlabel.setText(_translate("MainWindow", "Arguments"))
        self.robotlistsavebutton.setText(_translate("MainWindow", "Save Current Data to File"))
        self.argumentbutton.setText(_translate("MainWindow", "Adjust Arguments"))
        self.selectedfilename.setText(_translate("MainWindow", "Current File: "))
        self.robottype.setText(_translate("MainWindow", "Robot\'s Type/Configuration"))
        self.robotname.setText(_translate("MainWindow", "Robot\'s Name/User"))
        self.filebrowsinglabel.setText(_translate("MainWindow", "File Browsing"))
        self.label.setText(_translate("MainWindow", "Destination Directory"))
        self.label_4.setText(_translate("MainWindow", "Remote Repository"))
        self.label_3.setText(_translate("MainWindow", "Robot Type"))
        self.label_5.setText(_translate("MainWindow", "Catkin Option"))
        self.remotegitpasswordlabel.setText(_translate("MainWindow", "Remote Git Password"))
        self.numofpackageslabel.setText(_translate("MainWindow", "Select Number of Packages"))
        self.fileTransferLabel.setText(_translate("MainWindow", "File Transfer"))
        self.remotegituserlabel.setText(_translate("MainWindow", "Remote Git Username"))
        self.masterurilable.setText(_translate("MainWindow", "ROS MASTER URI IP ADDRESS:"))
        self.bashrcbutton.setText(_translate("MainWindow", "Update .bashrc"))
        self.buttontransfer.setText(_translate("MainWindow", "Transfer File(s)"))

