# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Git_Repo_Branch_Design.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(919, 697)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.confirmTransferButton = QtWidgets.QPushButton(Dialog)
        self.confirmTransferButton.setAutoDefault(False)
        self.confirmTransferButton.setObjectName("confirmTransferButton")
        self.gridLayout.addWidget(self.confirmTransferButton, 3, 1, 1, 1)
        self.fetchBar = QtWidgets.QProgressBar(Dialog)
        self.fetchBar.setProperty("value", 0)
        self.fetchBar.setObjectName("fetchBar")
        self.gridLayout.addWidget(self.fetchBar, 1, 0, 1, 2)
        self.checkAllButton = QtWidgets.QPushButton(Dialog)
        self.checkAllButton.setAutoDefault(False)
        self.checkAllButton.setObjectName("checkAllButton")
        self.gridLayout.addWidget(self.checkAllButton, 2, 0, 1, 1)
        self.repoTable = QtWidgets.QTableWidget(Dialog)
        self.repoTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.repoTable.setObjectName("repoTable")
        self.repoTable.setColumnCount(6)
        self.repoTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.repoTable.setHorizontalHeaderItem(5, item)
        self.repoTable.horizontalHeader().setDefaultSectionSize(145)
        self.repoTable.horizontalHeader().setStretchLastSection(True)
        self.repoTable.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.repoTable, 0, 0, 1, 2)
        self.gitFetchButton = QtWidgets.QPushButton(Dialog)
        self.gitFetchButton.setAutoDefault(False)
        self.gitFetchButton.setObjectName("gitFetchButton")
        self.gridLayout.addWidget(self.gitFetchButton, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Git Repo Branch Confirm"))
        self.confirmTransferButton.setText(_translate("Dialog", "Confirm and Transfer"))
        self.checkAllButton.setText(_translate("Dialog", "Check/Uncheck All Repositories"))
        item = self.repoTable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Enabled"))
        item = self.repoTable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Destination"))
        item = self.repoTable.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Repository URL"))
        item = self.repoTable.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Catkin Option"))
        item = self.repoTable.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Available Branches"))
        item = self.repoTable.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "Remote Machine Type"))
        self.gitFetchButton.setText(_translate("Dialog", "Git Fetch Branches from Selected Repositories"))
        self.label.setText(_translate("Dialog", "Select which branches you want to Git Pull to the remote machines."))

