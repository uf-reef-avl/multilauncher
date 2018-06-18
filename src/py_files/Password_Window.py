#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created:
#


import Password_Window_Design
from Generate_Key import Generate_Key
from PyQt5 import QtCore, QtGui, QtWidgets


#Creates and runs the Password Window and its methods
class Password_Window(QtWidgets.QDialog, Password_Window_Design.Ui_Dialog):

    #Variables for emitting a signal containing the list of passwords and if a RSA Key has been generated
    savePasswords = QtCore.pyqtSignal(dict,str)
    key = QtCore.pyqtSignal(bool)

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
        self.launchButton.clicked.connect(self.close_window)
        self.button_generate_RSA.clicked.connect(self.RSA_generation)

        #Dynamically populate the Password Window based on the number of robots
        for index, IP, USER in zip(range(len(self.ipList)),self.ipList,self.userList):
            tempLabelIP = QtWidgets.QLabel(self)
            tempLabelIP.setText(IP)
            tempLabelUser = QtWidgets.QLabel(self)
            tempLabelUser.setText(USER)
            tempLinePassword = QtWidgets.QLineEdit(self)
            self.linePasswords.append(tempLinePassword)
            self.labelIPS.append(tempLabelIP)
            self.labelUSERS.append(tempLabelUser)
            self.gridPasswords.addWidget(tempLabelIP, index, 0)
            self.gridPasswords.addWidget(tempLabelUser, index, 1)
            self.gridPasswords.addWidget(tempLinePassword, index, 2)
            #self.gridPasswords.

    #Saves the list of passwords for the robots and returns True if successful, False if one or more passwords are missing
    def saveData(self):
        save = True
        error = ""
        self.PASSWORDS = {}
        for index,linePassword in enumerate(self.linePasswords):
           if str(linePassword.text().strip()) == "":
               eMessage = "The password of " + str(self.labelUSERS[index].text()) +" has not be set"
               error += "\n"+eMessage +"\n"
               #temp = QtWidgets.QMessageBox.warning(self, "Warning", "the password of " + str(self.labelIPS[index].text()) +" has not be set")
               save = False
               #break
           self.PASSWORDS[str(self.labelIPS[index].text().strip())] = str(linePassword.text().strip())

        #If all robots have passwords entered
        if save is True:
          return save

        #If one or more robots is missing a password
        else:
            temp = QtWidgets.QMessageBox.warning(self, "Warning", error)
            return save


    #Closes the Password Window and emits the password list back to Main
    def close_window(self):
        if self.saveData():
            self.savePasswords.emit(self.PASSWORDS, self.commandType)
            self.close()
            self.deleteLater()


    #Calls the Generate_Key.py to generate a new rsa key
    def RSA_generation(self):
        if self.saveData():
            self.keyWindow = Generate_Key(self.ipList,self.userList,self.PASSWORDS)
            self.keyWindow.show()
            self.keyWindow.rsaKey.connect(self.chainSignal)


    #Fowards the signal signifying if a new rsa was successfully made
    @QtCore.pyqtSlot(bool)
    def chainSignal(self, value):
        self.key.emit(value)
