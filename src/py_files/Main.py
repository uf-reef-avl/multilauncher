#!/usr/bin/python2.7
#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
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


from PyQt5 import QtWidgets
from Multilauncher import Multilauncher
import sys


#Creates and runs the Main Window
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Multilauncher()
    form.showMaximized()
    sys.exit(app.exec_())


#Calls main
if __name__ == '__main__':
    main()