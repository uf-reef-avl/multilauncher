#!/usr/bin/python3
# File: Launch_Window.py
# Author: Matthew Hovatter and Paul Buzaud
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
			self.stopCurrentThread.setEnabled(True)
		else:
			self.lineDebugCommand.setEnabled(False)
			self.stopCurrentThread.setEnabled(False)


	#Catches all attempts to close the window
	def closeEvent(self, event):
		self.closeThreads.emit(self.window)
		event.accept()