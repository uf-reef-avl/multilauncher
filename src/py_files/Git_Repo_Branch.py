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
import Git_Repo_Branch_Design
import os
import subprocess


#This class creates and runs the Git Repo Branch Dialog window
class Git_Repo_Branch(QtWidgets.QDialog, Git_Repo_Branch_Design.Ui_Dialog):

    #Sets up to emit the data when closing the Dialog box
    branches = QtCore.pyqtSignal(list)

    #Definition of the Git Repo Branch Dialog window
    def __init__(self, repoList, packageList, catkinList, user, password, parent=None):
        super(Git_Repo_Branch, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.repos = repoList
        self.packages = packageList
        self.catkins = catkinList
        self.userID = user
        self.repoPassword = password

        #Connecting buttons
        self.checkAllButton.clicked.connect(self.enableAndDisable)
        self.gitFetchButton.clicked.connect(self.fetchBranches)
        self.confirmTransferButton.clicked.connect(self.closeWindow)

        self.fetchBarValue = 0

        #Make a temporary directory to use for checking remote branches
        subprocess.call("mkdir -p ~/MultilauncherGitTemp", shell=True)

        #Dynamically populate the Git Repo Branch dialog based on the number of repositories
        for index, repo, package, catkin in zip(range(len(self.repos)),self.repos,self.packages,self.catkins):
            tempRepo = QtWidgets.QLabel(self)
            tempRepo.setText(repo)
            tempPackage = QtWidgets.QLabel(self)
            tempPackage.setText(package)
            tempCatkin = QtWidgets.QLabel(self)
            tempCatkin.setText(catkin)
            tempComboBox = QtWidgets.QComboBox(self)
            tempComboBox.addItem("master")
            tempCheckBox = QtWidgets.QCheckBox(self)
            tempCheckBox.setCheckState(QtCore.Qt.Checked)

            self.repoTable.insertRow(index)
            self.repoTable.setCellWidget(index, 0, tempCheckBox)
            self.repoTable.setCellWidget(index, 1, tempPackage)
            self.repoTable.setCellWidget(index, 2, tempRepo)
            self.repoTable.setCellWidget(index, 3, tempCatkin)
            self.repoTable.setCellWidget(index, 4, tempComboBox)


    #Begin process of contacting remote repositories to determine the number of branches that exist for each repoitory
    def fetchBranches(self):
        repoList = []

        #Add only checked repositories
        for index in range(self.repoTable.rowCount()):
            if self.repoTable.cellWidget(index, 0).checkState() == 2:
                repoList.append(self.repoTable.cellWidget(index, 2).text())

        #If there are remote repositories to check
        if len(repoList) != 0:
            self.updateComboBoxes(repoList)

        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", "No remote repositories selected")


    #Updates the comboboxes for each remote repository based on the number of branches available in the remote repository
    def updateComboBoxes(self, repoList):

        for repo in repoList:

            self.fetchBarValue = 0
            self.fetchBar.setValue(self.fetchBarValue)
            combo = QtWidgets.QComboBox(self)
            combo.addItem("master")

            if os.path.exists(os.path.expanduser("~/MultilauncherGitTemp/.git")):
                subprocess.call("rm -rf ~/MultilauncherGitTemp/.git", shell=True)

            self.updateFetchBar(25)

            adjustedRepo = repo[:str(repo).find("//")+2]+str(self.userID)+":"+str(self.repoPassword)+"@"+repo[str(repo).find("//")+2:]

            subprocess.call( "cd ~/MultilauncherGitTemp; git init -q; git remote add MultilauncherGitRemote "+str(adjustedRepo)+"; git fetch MultilauncherGitRemote -q ", shell=True)

            self.updateFetchBar(25)

            process = subprocess.Popen( "cd ~/MultilauncherGitTemp; git branch -r", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            self.updateFetchBar(25)

            result = process.communicate()

            data = result[0].split("\n")

            for line in data:
                if line != "":
                    option = line[str(line).find("Remote/")+7:]
                    if option != "master":
                        combo.addItem(option)

            self.fetchBar.setValue(100)
            index = self.findComboBox(repo)
            if index != -1:
                self.repoTable.setCellWidget(index, 4, combo)


    #Used to update the progress bar in the Git Repo Branch Dialog to provide visual feedback to the user
    def updateFetchBar(self, updateAmount):
        self.fetchBarValue += updateAmount / self.repoTable.rowCount()
        self.fetchBar.setValue(self.fetchBarValue)


    #Used to find the correct index of a repository's combobox
    def findComboBox(self, repo):

        for index in range(self.repoTable.rowCount()):
            text = self.repoTable.cellWidget(index, 2).text()
            if repo == text:
                return index
        return -1


    #Used to detect when the window size is changed
    def resizeEvent(self, QResizeEvent):
        self.setTableSize()


    #Corrects the column header sizes
    def setTableSize(self):
        self.repoTable.setColumnWidth(0, self.width() / 5.2)
        self.repoTable.setColumnWidth(1, self.width() / 5.2)
        self.repoTable.setColumnWidth(2, self.width() / 5.2)
        self.repoTable.setColumnWidth(3, self.width() / 5.2)
        self.repoTable.setColumnWidth(4, self.width() / 5.2)


    #Enables/Disables all listed repositories
    def enableAndDisable(self):

        index = 0

        if self.repoTable.cellWidget(0,0).checkState() == QtCore.Qt.Unchecked:
            while index < self.repoTable.rowCount():
                self.repoTable.cellWidget(index, 0).setCheckState(QtCore.Qt.Checked)
                index+=1
        else:
            while index < self.repoTable.rowCount():
                self.repoTable.cellWidget(index, 0).setCheckState(QtCore.Qt.Unchecked)
                index+=1


    #Closes the repository dialog, emits the list of branches back to the Main Window, and deletes the temporary directory
    def closeWindow(self):

        branchList = []
        for index in range(self.repoTable.rowCount()):
            branchList.append(self.repoTable.cellWidget(index, 4).currentText())

        self.branches.emit(branchList)

        if os.path.exists(os.path.expanduser("~/MultilauncherGitTemp")):
            subprocess.call("rm -rf ~/MultilauncherGitTemp", shell=True)

        self.close()
        self.deleteLater()


    # Catches all attempts to close the dialog
    def closeEvent(self, event):
        event.accept()