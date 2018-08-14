#
# File: Launch_Window.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created: Summer 2018
#

from PyQt5 import QtWidgets, QtCore
import Launch_Window_Design

#Creates Launch Window used in all non-ROSMASTER multi-threading functions
class Launch_Window(QtWidgets.QDialog, Launch_Window_Design.Ui_Dialog):

	closeThreads = QtCore.pyqtSignal(str)

	#Definition of the Launch Window
	def __init__(self, parent=None):
		super(Launch_Window, self).__init__(parent)
		self.setupUi(self)
		self.setModal(True)
		self.window = ""
		self.tab_Launch.currentChanged.connect(self.debugEnable)


	@QtCore.pyqtSlot(int)
	def debugEnable(self, index):
		ipText = str(self.tab_Launch.tabText(index))
		if " (Finished)" not in ipText:
			self.lineDebugCommand.setEnabled(True)
		else:
			self.lineDebugCommand.setEnabled(False)


	#Catches all attempts to close the window
	def closeEvent(self, event):
		self.closeThreads.emit(self.window)
		event.accept()