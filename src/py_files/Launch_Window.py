#
# File: Launch_Window.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created:
#

from PyQt5 import QtWidgets, QtCore
import Launch_Window_Design

#Creates Launch Window used in all multi-threading functions
class Launch_Window(QtWidgets.QDialog, Launch_Window_Design.Ui_Dialog):

	closeThreads = QtCore.pyqtSignal(str)

	#Definition of the Launch Window
	def __init__(self, parent=None):
		super(Launch_Window, self).__init__(parent)
		self.setupUi(self)
		self.setModal(True)
		self.window = ""


	#Catches all attempts to close the window if there are threads still running
	def closeEvent(self, event):
		self.closeThreads.emit(self.window)
		event.accept()