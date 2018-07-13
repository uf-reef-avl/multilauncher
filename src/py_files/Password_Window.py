#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created: Summer 2018
#


import Password_Window_Design
from PyQt5 import QtCore, QtWidgets


#Creates and runs the Password Window and its methods
class Password_Window(QtWidgets.QDialog, Password_Window_Design.Ui_Dialog):

    #Variables for emitting a signal containing the list of passwords
    savePasswords = QtCore.pyqtSignal(dict,str)
    exitWindow = QtCore.pyqtSignal(str)

    #Definition of the Password Window
    def __init__(self, ipList, userList, commandType, parent = None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.ipList = ipList
        self.userList = userList
        self.commandType = commandType
        self.linePasswords = []
        self.labelIPS = []
        self.labelUSERS = []
        self.PASSWORDS = {}
        self.terminalRefreshSeconds = 0.5

        #Sets up the dynamic list of robots and corresponding text fields for entering passwords
        self.area = QtWidgets.QWidget()
        self.area.setLayout(self.gridPasswords)
        self.scrollArea.setWidget(self.area)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        #Paring buttons to functions
        self.launchButton.clicked.connect(self.closeWindow)

        #Dynamically populate the Password Window based on the number of robots
        for index, IP, USER in zip(range(len(self.ipList)),self.ipList,self.userList):
            tempLabelIP = QtWidgets.QLabel(self)
            tempLabelIP.setText(IP)
            tempLabelUser = QtWidgets.QLabel(self)
            tempLabelUser.setText(USER)
            tempLinePassword = QtWidgets.QLineEdit(self)
            tempLinePassword.setEchoMode(QtWidgets.QLineEdit.Password)
            self.linePasswords.append(tempLinePassword)
            self.labelIPS.append(tempLabelIP)
            self.labelUSERS.append(tempLabelUser)
            self.gridPasswords.addWidget(tempLabelIP, index, 0)
            self.gridPasswords.addWidget(tempLabelUser, index, 1)
            self.gridPasswords.addWidget(tempLinePassword, index, 2)


    #Saves the list of passwords for the robots and returns True if successful, False if one or more passwords are missing
    def saveData(self):
        save = True
        error = ""
        self.PASSWORDS = {}
        for index,linePassword in enumerate(self.linePasswords):
           if str(linePassword.text().strip()) == "":
               eMessage = "The password of " + str(self.labelUSERS[index].text()) +" has not been set"
               error += "\n"+eMessage +"\n"
               save = False
           self.PASSWORDS[str(self.labelIPS[index].text().strip())] = str(linePassword.text().strip())

        #If all robots have passwords entered
        if save is True:
          return save

        #If one or more robots is missing a password
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", error)
            return save


    #Closes the Password Window and emits the password list back to Main
    def closeWindow(self):
        if self.saveData():
            self.setResult(1)
            self.savePasswords.emit(self.PASSWORDS, self.commandType)
            self.close()
            self.deleteLater()


    # Catches all attempts to close the window
    def closeEvent(self, event):
        if self.result() == 0:
            self.exitWindow.emit("pass")
        event.accept()