#
# File: Edit_Robot_Dialog.py
# Author: Matthew Hovatter
#
# Created:
#



from PyQt5 import QtCore, QtWidgets
import Edit_Robot_Design


#This class creates and runs the Robot Editing Dialog box
class Edit_Robot_Dialog(QtWidgets.QDialog, Edit_Robot_Design.Ui_robotEditDialog):

    #Sets up to receive the data when closing the Dialog box
	save = QtCore.pyqtSignal(list, list, list)

	#Initializes and defines the Robot Editing Dialog box
	def __init__(self, parent = None):
		super(Edit_Robot_Dialog, self).__init__(parent)
		self.setupUi(self)
		self.setModal(True)

		#Paring buttons to functions
		self.addRobotButton.clicked.connect(self.addRobot)
		self.deleteRobotButton.clicked.connect(self.removeRobot)
		self.robotTable.cellDoubleClicked.connect(self.loadEditor)
		self.saveAndExitButton.clicked.connect(self.closeWindow)


	#Checks to see if there is a robot that already exists with the same IP Address,
	#statements that return True mean that the user is adding a valid new robot,
	#statements that return False mean that the user has tried to
	#add a robot whose IP Address already exists as another robot's IP Address
	def ipCheck(self):
		rows = self.robotTable.rowCount()

		#If there is no robots in the list
		if self.robotTable.rowCount() == 0:
			return True

		#If there is only one robot in the list
		elif rows == 1:
			text = self.robotTable.item(0, 0).text()
			text2 = self.ipEdit.text().strip()
			if text2 == text:
				return False
			else:
				return True

		#There is more than one robot in the list
		else:
			text2 = self.ipEdit.text().strip()
			for x in range(self.robotTable.rowCount()):
				text = self.robotTable.item(x,0).text()
				if text2 == text:
					return False
		return True


	#Attempts to add a new robot to the robot table based on the input in the three text fields
	def addRobot(self):
		check = self.ipCheck()

		#If the new robot has an original IP Address
		if check:
			#If the three text fields all have some data
			if self.ipEdit.text().strip() != "" and self.nameEdit.text().strip() != "" and self.typeEdit.text().strip() != "":
				x = self.robotTable.rowCount()
				self.robotTable.insertRow(x)
				self.robotTable.setItem(x, 0, QtWidgets.QTableWidgetItem(self.ipEdit.text().strip()))
				self.robotTable.setItem(x, 1, QtWidgets.QTableWidgetItem(self.nameEdit.text().strip()))
				self.robotTable.setItem(x, 2, QtWidgets.QTableWidgetItem(self.typeEdit.text().strip()))
				self.resultLabel.setText("Result: Successfully added new robot")
			else:
				self.resultLabel.setText("Result: Error in adding new robot, one or more fields are left blank")
		else:
			self.resultLabel.setText("Result: Error in adding new robot, cannot have matching IP addresses")


	#Removes the selected robot from the robot table
	def removeRobot(self):
		self.robotTable.removeRow(self.robotTable.currentRow())


	#Loads the currently selected robot's IP Address, Name, and Type into the three text fields
	def loadEditor(self):
		x = self.robotTable.currentRow()
		self.ipEdit.setText(self.robotTable.item(x,0).text())
		self.nameEdit.setText(self.robotTable.item(x,1).text())
		self.typeEdit.setText(self.robotTable.item(x,2).text())


	#Saves the current robot table to underlying data-structures that are passed back to the main.py for processing
	def closeWindow(self):

		ipText = []
		nameText = []
		typeText = []

		for x in range(self.robotTable.rowCount()):
			ipText.append(self.robotTable.item(x,0).text())
			nameText.append(self.robotTable.item(x,1).text())
			typeText.append(self.robotTable.item(x,2).text())

		#Sends the data out to main.py
		self.save.emit(ipText,nameText,typeText)
		self.close()
		self.deleteLater()
