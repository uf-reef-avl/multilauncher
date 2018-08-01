#!/usr/bin/python2.7
#
# File: Main.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created: Summer 2018
#

from PyQt5 import QtWidgets
from Multilaunch import Multilaunch
import sys


#Creates and runs the Main Window
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Multilaunch()
    form.showMaximized()
    sys.exit(app.exec_())


#Calls main
if __name__ == '__main__':
    main()