# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Transfer_Local_File_Design.ui'
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
        self.fileTable = QtWidgets.QTableWidget(Dialog)
        self.fileTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.fileTable.setObjectName("fileTable")
        self.fileTable.setColumnCount(3)
        self.fileTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.fileTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileTable.setHorizontalHeaderItem(2, item)
        self.fileTable.horizontalHeader().setDefaultSectionSize(180)
        self.fileTable.horizontalHeader().setStretchLastSection(True)
        self.fileTable.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.fileTable, 2, 0, 1, 2)
        self.confirmTransferButton = QtWidgets.QPushButton(Dialog)
        self.confirmTransferButton.setMinimumSize(QtCore.QSize(445, 0))
        self.confirmTransferButton.setAutoDefault(False)
        self.confirmTransferButton.setObjectName("confirmTransferButton")
        self.gridLayout.addWidget(self.confirmTransferButton, 3, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        item = self.fileTable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Destination"))
        item = self.fileTable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Selected Files"))
        item = self.fileTable.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Remote Machine Type"))
        self.confirmTransferButton.setText(_translate("Dialog", "Confirm and Transfer"))
        self.label.setText(_translate("Dialog", "Select which files you want to move to the remote machines."))

