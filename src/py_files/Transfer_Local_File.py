#
# File: Git_Repo_Branch.py
# Author: Matthew Hovatter
#
# Created: Summer 2018
#
# Copyright 2018 FIRSTNAME LASTNAME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from PyQt5 import QtCore, QtWidgets
import Transfer_Local_File_Design

#This class creates and runs the Git Repo Branch Dialog window
class Transfer_Local_File(QtWidgets.QDialog, Transfer_Local_File_Design.Ui_Dialog):

    #Sets up to emit the data when closing the Dialog box
    confirm = QtCore.pyqtSignal(bool)

    #Definition of the Git Repo Branch Dialog window
    def __init__(self, fileList, packageList, typeList, parent=None):
        super(Transfer_Local_File, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.fileList = fileList
        self.packages = packageList
        self.types = typeList

        #Connecting button
        self.confirmTransferButton.clicked.connect(self.closeWindow)

        #Dynamically populate the Transfer Local File dialog based on the number of files to be transferred
        for index, files, package, remoteType in zip(range(len(self.fileList)),self.fileList,self.packages, self.types):
            tempFile = QtWidgets.QLabel(self)
            tempFile.setText(files)
            tempPackage = QtWidgets.QLabel(self)
            tempPackage.setText(package)
            tempType = QtWidgets.QLabel(self)
            tempType.setText(remoteType)

            self.fileTable.insertRow(index)
            self.fileTable.setCellWidget(index, 0, tempPackage)
            self.fileTable.setCellWidget(index, 1, tempFile)
            self.fileTable.setCellWidget(index, 2, tempType)


    #Used to detect when the window size is changed
    def resizeEvent(self, QResizeEvent):
        self.setTableSize()


    #Corrects the column header sizes
    def setTableSize(self):
        self.fileTable.setColumnWidth(0, self.width() / 3.2)
        self.fileTable.setColumnWidth(1, self.width() / 3.2)
        self.fileTable.setColumnWidth(2, self.width() / 3.2)


    #Closes the repository dialog
    def closeWindow(self):
        self.confirm.emit(True)
        self.close()
        self.deleteLater()


    # Catches all attempts to close the dialog
    def closeEvent(self, event):
        event.accept()