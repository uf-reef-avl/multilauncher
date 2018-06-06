#
# File: Launch_Window.py
# Author: Paul Buzaud
#
# Created:
#

from PyQt5 import QtWidgets
import Launch_Window_Design

#Creates Launch Window used in all multi-threading functions
class Launch_Window(QtWidgets.QDialog, Launch_Window_Design.Ui_Dialog):

	#Definition of the Launch Window
	def __init__(self, parent=None):
		super(Launch_Window, self).__init__(parent)
		self.setupUi(self)
		self.setModal(True)

