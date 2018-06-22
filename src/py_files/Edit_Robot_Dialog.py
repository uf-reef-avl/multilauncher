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
	save = QtCore.pyqtSignal(list, list, list, list, list)

	#Initializes and defines the Robot Editing Dialog box
	def __init__(self, parent = None):
		super(Edit_Robot_Dialog, self).__init__(parent)
		self.setupUi(self)
		self.setModal(True)
		self.IPS = []

		#Paring buttons to functions
		self.addRobotButton.clicked.connect(self.addRobot)
		self.deleteRobotButton.clicked.connect(self.removeRobot)
		self.modifyRobotButton.clicked.connect(self.modifyRobot)
		self.robotTable.cellDoubleClicked.connect(self.loadEditor)
		self.saveAndExitButton.clicked.connect(self.closeWindow)

		#Corrects the column header sizes
		self.resizeEvent(self.setTableSize())


	#Corrects the column header sizes
	def setTableSize(self):
		self.robotTable.setColumnWidth(0, self.width()/5)
		self.robotTable.setColumnWidth(1, self.width()/5)
		self.robotTable.setColumnWidth(2, self.width()/5)
		self.robotTable.setColumnWidth(3, self.width()/5)
		self.robotTable.setColumnWidth(4, self.width()/5)



	#Checks to see if there is a robot that already exists with the same IP Address,
	#statements that return True mean that the user is adding a valid new robot,
	#statements that return False mean that the user has tried to add a robot whose IP Address already exists as another robot's IP Address
	def ipCheck(self):
		rows = self.robotTable.rowCount()

		#If there is no robots in the list
		if self.robotTable.rowCount() == 0:
			return True

		#If there is only one robot in the list
		elif rows == 1:
			text = self.robotTable.item(0, 1).text()
			text2 = self.ipEdit.text().strip()
			if text2 == text:
				return False
			else:
				return True

		#There is more than one robot in the list
		else:
			text2 = self.ipEdit.text().strip()
			for x in range(self.robotTable.rowCount()):
				text = self.robotTable.item(x,1).text()
				if text2 == text:
					return False
		return True


	#Attempts to add a new robot to the robot table based on the input in the three text fields
	def addRobot(self):

		#If the new robot has an original IP Address
		if self.ipCheck():

			#If the three text fields all have some data
			if self.ipEdit.text().strip() != "" and self.nameEdit.text().strip() != "" and self.typeEdit.text().strip() != "":
				x = self.robotTable.rowCount()
				self.robotTable.insertRow(x)
				self.robotTable.setItem(x, 0, QtWidgets.QTableWidgetItem("True"))
				self.robotTable.setItem(x, 1, QtWidgets.QTableWidgetItem(self.ipEdit.text().strip()))
				self.IPS.append(self.ipEdit.text().strip())
				self.robotTable.setItem(x, 2, QtWidgets.QTableWidgetItem(self.nameEdit.text().strip()))
				self.robotTable.setItem(x, 3, QtWidgets.QTableWidgetItem(self.typeEdit.text().strip()))
				self.robotTable.setItem(x, 4, QtWidgets.QTableWidgetItem("No ROS Settings"))
				self.resultLabel.setText("Result: Successfully added new robot.")
			else:
				self.resultLabel.setText("Result: Error in adding new robot, one or more fields are left blank.")
		else:
			self.resultLabel.setText("Result: Error in adding new robot, cannot have matching IP addresses.")


	#Removes the selected robot from the robot table
	def removeRobot(self):
		self.IPS.pop(self.robotTable.currentRow())
		self.robotTable.removeRow(self.robotTable.currentRow())


	#Modifies the currently selected robot with the data in the three input fields
	def modifyRobot(self):
		if not self.ipCheck():

			#If the three input fields all have some data
			if self.ipEdit.text().strip() != "" and self.nameEdit.text().strip() != "" and self.typeEdit.text().strip() != "":
				for index, string in enumerate(self.IPS):

					#If this is the robot to be modified
					if string == self.ipEdit.text().strip():
						self.robotTable.setItem(index, 2, QtWidgets.QTableWidgetItem(self.nameEdit.text().strip()))
						self.robotTable.setItem(index, 3, QtWidgets.QTableWidgetItem(self.typeEdit.text().strip()))
						self.resultLabel.setText("Result: Successfully modified robot.")
						break

			else:
				self.resultLabel.setText("Result: Error in modifying selected robot. One of the input fields is blank.")
		else:
			self.resultLabel.setText("Result: A robot with that IP address does not currently exist.")


	#Loads the currently selected robot's IP Address, Name, and Type into the three input fields
	def loadEditor(self):
		x = self.robotTable.currentRow()
		self.ipEdit.setText(self.robotTable.item(x,1).text())
		self.nameEdit.setText(self.robotTable.item(x,2).text())
		self.typeEdit.setText(self.robotTable.item(x,3).text())


	#Saves the current robot table to underlying data-structures that are passed back to the main.py for processing
	def closeWindow(self):

		enableText = []
		ipText = []
		nameText = []
		typeText = []
		masterText = []

		for x in range(self.robotTable.rowCount()):

			enableText.append(self.robotTable.item(x,0).text())
			ipText.append(self.robotTable.item(x,1).text())
			nameText.append(self.robotTable.item(x,2).text())
			typeText.append(self.robotTable.item(x,3).text())
			masterText.append(self.robotTable.item(x,4).text())

		#Sends the data out to main.py
		self.save.emit(enableText,ipText,nameText,typeText, masterText)
		self.close()
		self.deleteLater()
