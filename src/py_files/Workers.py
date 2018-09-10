#!/usr/bin/python2.7
#
# File: Workers.py
# Authors: Paul Buzaud and Matthew Hovatter
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


from PyQt5 import QtCore
import os
import paramiko
import time
import logging
import sys
import subprocess
import socket

import Xlib.support.connect as xlib_connect


#logging.basicConfig(level=logging.DEBUG)
logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())

PING_TIMEOUT = 15

#Creates and runs the SSH_Transfer_File_Worker class and its methods
class SSH_Transfer_File_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, list)
	finishThread = QtCore.pyqtSignal(int,str)


	#Definition of a SSH_Transfer_File_Worker
	def __init__(self, ipIndex, IP, user, parentPackageDirList, gitRepoList, gitUsername, gitPassword, makeOption, password, key):
		super(SSH_Transfer_File_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.user = user
		self.password = password
		self.parentPackageDirList = parentPackageDirList
		self.gitRepoList = gitRepoList
		self.gitUsername = gitUsername
		self.gitPassword = gitPassword
		self.makeOption = makeOption
		self.terminalRefreshSeconds = 0.75
		self.stopSignal = False
		self.start.connect(self.run)
		self.myKey = key
		self.finishMessage = ""
		self.skip = False
		self.buffer = ""

	#This function connects to the remote robot and performs a git pull operation on the selected remote repository
	@QtCore.pyqtSlot()
	def run(self):

		ssh = paramiko.SSHClient()

		#Creating a password or rsa key based ssh connection
		try:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.password is not None:
				ssh.connect(self.IP, 22, username=self.user, password=self.password, allow_agent=False,look_for_keys=False)
			else:
				ssh.connect(self.IP, 22, username=self.user, pkey = self.myKey)

			#Pull the selected directory and push it to the desired location on the remote robot, catkin operations optional
			self.channel = ssh.invoke_shell()
			for i in range(len(self.gitRepoList)):
				if self.stopSignal:
					break

				self.prepPath(i)

				self.prepRepo(i)

				#If there wasn't a problem with the retrieving data from the remote git repository
				if not self.skip:

					#catkin make option
					if self.makeOption[i] == 1:

						self.prepCatkin(i)
						self.channel.send('catkin_make\n')
						self.waitFinishCommand()

					#catkin build option
					elif self.makeOption[i] == 2:

						self.prepCatkin(i)
						self.channel.send('catkin build\n')
						self.waitFinishCommand()


		except paramiko.ssh_exception.AuthenticationException:
			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not having ssh installed or is unreachable (firewall)"

		except:
			e = sys.exc_info()[0]
			print("GitRepo Error: %s" % e)

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Corrects some incorrect user input and/or appends a src directory to hold the local repository
	def prepPath(self, i):

		tempList = self.parentPackageDirList[i].split('/')
		if tempList[-1] != '':
			self.parentPackageDirList[i] = str(self.parentPackageDirList[i] + "/")

		#If a catkin option was selected for this repo
		if self.makeOption[i] != 0:
			if "src" not in tempList:
				self.parentPackageDirList[i] = str(self.parentPackageDirList[i] + "src/")


	#Sets up a new local repo or overrides the local existing repo with the remote one
	def prepRepo(self,i):

		self.channel.send('mkdir -p ' + self.parentPackageDirList[i] + '\n')
		self.waitFinishCommand()
		self.channel.send('cd ' + self.parentPackageDirList[i] + '\n')
		self.waitFinishCommand()

		packageName = self.gitRepoList[i].split('/')[-1]
		if ".git" in packageName:
			packageName = packageName[:-4]

		self.channel.send('cd ' + packageName + '\n')
		flag = self.waitFinishCommand()

		# New local repo
		if flag == "no file":
			self.channel.send('git clone ' + self.gitRepoList[i] + '\n')
			flag = self.waitFinishCommand()

			# Successful git clone
			if flag == "done":
				self.channel.send('cd ' + self.parentPackageDirList[i] + '\n')
				self.waitFinishCommand()
			else:
				self.skip = True

		# Existing local repo
		else:
			self.channel.send('git stash\n')
			self.waitFinishCommand()

			self.channel.send('git pull\n')
			self.waitFinishCommand()

			self.channel.send('cd ' + self.parentPackageDirList[i] + '\n')
			self.waitFinishCommand()


	#Sets up for catkin make or build
	def prepCatkin(self, i):

		tempList = self.parentPackageDirList[i].split('/')
		index = tempList.index("src")
		toSrc = tempList[:index]
		path = ""
		for string in toSrc:
			path += (string + "/")

		self.channel.send('cd ' + path + '\n')
		self.waitFinishCommand()


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break

			time.sleep(self.terminalRefreshSeconds)
			data = self.channel.recv(1024).decode("utf-8")

			splitData = data.split("\n")
			splitData[0] = self.buffer + splitData[0]
			buffed = splitData[-1]

			if buffed != "":
				if buffed[-1] != "\r":
					self.buffer = buffed
				else:
					self.buffer = ""
			else:
				self.buffer = ""

			self.terminalSignal.emit(self.ipIndex, splitData[:-1])

			if 'Username for ' in data:
				self.channel.send(self.gitUsername + '\n')

			elif 'Password for ' in data:
				self.channel.send(self.gitPassword + '\n')

			elif "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()

			if "No such file or directory" in data:
				return "no file"

			elif "Checking connectivity... done" in data:
				return "done"

			if self.user + "@" in data:
				break


#Creates and runs the Launch_Worker class and its methods
class Launch_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, list)
	finishThread = QtCore.pyqtSignal(int,str)


	#Definition of a Launch_Worker
	def __init__(self, ipIndex, IP, user, commandList, password, key):
		super(Launch_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.user = user
		self.password = password
		self.commandList = commandList
		self.terminalRefreshSeconds = 0.75
		self.stopSignal = False
		self.start.connect(self.run)
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""
		self.x11 = False

	#This function connects to the remote robot and executes the user's list of commands
	@QtCore.pyqtSlot()
	def run(self):

		ssh = paramiko.SSHClient()

		#Creating a password or rsa key based ssh connection
		try:

			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.password is not None:
				ssh.connect(self.IP, 22, username=self.user, password=self.password, allow_agent=False, look_for_keys=False)
			else:
				ssh.connect(self.IP, 22, username=self.user, pkey = self.myKey)

			#Execute the list of commands
			self.channel = ssh.invoke_shell()

			# local_x11_display = xlib_connect.get_display(os.environ['DISPLAY'])
			# local_x11_socket = xlib_connect.get_socket(*local_x11_display[:3])

			# transport = ssh.get_transport()
			# session = transport.open_session()
            #
			# session.request_x11()
			# self.channel = transport.accept()

			for i in self.commandList:
				if self.stopSignal:
					break
				self.channel.send(str(i)+ '\n')
				self.waitFinishCommand()

			while True:
				if self.stopSignal:
					break
				self.waitFinishCommand()


		except paramiko.ssh_exception.AuthenticationException:
			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not having ssh installed or is unreachable (firewall)"

		except:
			True

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break
			time.sleep(self.terminalRefreshSeconds)
			data = self.channel.recv(1024).decode("utf-8")

			splitData = data.split("\n")
			splitData[0] = self.buffer + splitData[0]
			buffed = splitData[-1]

			if buffed != "":
				if buffed[-1] != "\r":
					self.buffer = buffed
				else:
					self.buffer = ""
			else:
				self.buffer = ""

			self.terminalSignal.emit(self.ipIndex, splitData[:-1])

			if '[sudo]' in data and self.password is not None:
				self.channel.send(self.password + '\n')
				self.waitFinishCommand()
				break

			elif '[Y/n]' in data:
				self.channel.send('Y\n')
				self.waitFinishCommand()
				break

			elif '[y/N]' in data:
				self.channel.send('y\n')
				self.waitFinishCommand()
				break

			elif "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()

			elif self.user + "@" in data:
				break


#Creates and runs the ROSMASTER_Worker class and its methods
class ROSMASTER_Worker(QtCore.QObject):

	# Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, list)
	finishThread = QtCore.pyqtSignal(int, str)

	# Definition of a Launch_Worker
	def __init__(self, ipIndex, IP, user, password, key):
		super(ROSMASTER_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.user = user
		self.password = password
		self.terminalRefreshSeconds = 0.75
		self.stopSignal = False
		self.start.connect(self.run)
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""


	# This function connects to the remote robot and executes the user's list of commands
	@QtCore.pyqtSlot()
	def run(self):

		ssh = paramiko.SSHClient()

		#Creating a password or rsa key based ssh connection
		try:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.password is not None:
				ssh.connect(self.IP, 22, username=self.user, password=self.password, allow_agent=False,
							look_for_keys=False)
			else:
				ssh.connect(self.IP, 22, username=self.user, pkey=self.myKey)

			#Execute the roscore command
			self.channel = ssh.invoke_shell()
			self.channel.send('roscore\n')
			self.waitFinishCommand()

			while True:
				if self.stopSignal:
					break
				self.waitFinishCommand()



		except paramiko.ssh_exception.AuthenticationException:
			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not having ssh installed or is unreachable (firewall)"

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break

			time.sleep(self.terminalRefreshSeconds)
			data = self.channel.recv(1024).decode("utf-8")

			splitData = data.split("\n")
			splitData[0] = self.buffer + splitData[0]
			buffed = splitData[-1]

			if buffed != "":
				if buffed[-1] != "\r":
					self.buffer = buffed
				else:
					self.buffer = ""
			else:
				self.buffer = ""


			self.terminalSignal.emit(self.ipIndex, splitData[:-1])

			if '[sudo]' in data and self.password is not None:
				self.channel.send(self.password + '\n')
				self.waitFinishCommand()
				break

			elif '[Y/n]' in data:
				self.channel.send('Y\n')
				self.waitFinishCommand()
				break

			elif '[y/N]' in data:
				self.channel.send('y\n')
				self.waitFinishCommand()
				break

			elif "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()

			elif self.user + "@" in data:
				break


#Creates and runs the Bashrc_Worker class and its methods
class Bashrc_Worker(QtCore.QObject):

	#Preparing for starting and closing signals
	start = QtCore.pyqtSignal()
	finishThread = QtCore.pyqtSignal(int,str)
	terminalSignal = QtCore.pyqtSignal(int, list)


	#Definition of a Bashrc_Worker
	def __init__(self, ipIndex, IP, user, masterIP, password, key):
		super(Bashrc_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.user = user
		self.password = password
		self.masterIP = masterIP
		self.terminalRefreshSeconds = 0.75
		self.stopSignal = False
		self.start.connect(self.run)
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""

	#This function connects to the remote robot and updates their .bashrc file
	@QtCore.pyqtSlot()
	def run(self):

		ssh = paramiko.SSHClient()

		#Creating a password or rsa key based ssh connection
		try:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.password is not None:
				ssh.connect(self.IP, 22, username=self.user, password=self.password, allow_agent=False,look_for_keys=False)
			else:
				ssh.connect(self.IP, 22, username=self.user, pkey=self.myKey)

			#Start sending the commands to update the remote robot's .bashrc
			self.channel = ssh.invoke_shell()
			self.channel.send('sed -i -E "/export ROS_MASTER_URI=http:\/\/[A-Za-z0-9.]+:11311/d" ~/.bashrc\n')
			self.waitFinishCommand()
			self.channel.send('sed -i -E "/export ROS_HOSTNAME=[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/d" ~/.bashrc\n')
			self.waitFinishCommand()
			self.channel.send('sed -i "/export ROS_HOSTNAME=localhost/d" ~/.bashrc\n')
			self.waitFinishCommand()
			self.channel.send(' echo export ROS_HOSTNAME='+self.IP+' >> ~/.bashrc\n')
			self.waitFinishCommand()
			self.channel.send(' echo export ROS_MASTER_URI=http://' + self.masterIP + ':11311 >> ~/.bashrc\n')
			self.waitFinishCommand()

		except paramiko.ssh_exception.AuthenticationException:
			if self.password:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to talk to robot failed due to remote host not having ssh installed or is unreachable (firewall)"

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break
			time.sleep(self.terminalRefreshSeconds)
			data = self.channel.recv(1024).decode("utf-8")

			splitData = data.split("\n")
			splitData[0] = self.buffer + splitData[0]
			buffed = splitData[-1]

			if buffed != "":
				if buffed[-1] != "\r":
					self.buffer = buffed
				else:
					self.buffer = ""
			else:
				self.buffer = ""

			self.terminalSignal.emit(self.ipIndex, splitData[:-1])

			if "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()
			elif self.user + "@" in data:
				break


#Creates and runs the Ping_Worker class and its methods
class Ping_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	pingSignal = QtCore.pyqtSignal(int, str, int)
	finishThread = QtCore.pyqtSignal(int,str)


	#Definition of a Ping_Worker
	def __init__(self, ipIndex,IP):
		super(Ping_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.start.connect(self.run)
		self.stopSignal = False
		self.responseString = ""
		self.errorString = ""


	#This function pings the robot
	@QtCore.pyqtSlot()
	def run(self):

		#Ping until you reach the set maximum number of pings
		for x in range(PING_TIMEOUT):

			#If the user has pressed the stop unfinished threads button
			if self.stopSignal:
				break

			#The actual ping message sent and the response back
			response = os.system("ping -c1 " + self.IP + " 2>&1 >/dev/null")

			#If the robot was pinged successfully and found
			if response == 0:
				self.responseString = "Found IP: "+self.IP

				#Display the status to the tab terminal
				self.pingSignal.emit(self.ipIndex, self.responseString, response)
				break

			elif response == 512:
				self.responseString = "Unknown host: "+self.IP
				self.errorString = "Unknown host: "+self.IP

				# Display the status to the tab terminal
				self.pingSignal.emit(self.ipIndex, self.responseString, response)
				break

			#If the robot has yet to be found
			else:
				self.responseString = "--- "+self.IP +" ping statistics --- \n 1 packets transmitted, 0 received, 100% packet loss, time 0ms"

				#Display the status to the tab terminal
				self.pingSignal.emit(self.ipIndex, self.responseString,response)

		#Close the thread
		self.finishThread.emit(self.ipIndex, self.errorString)


#Creates and runs the GenKey_Worker class and its methods
class GenKey_Worker(QtCore.QObject):

	#Preparing for starting and closing signals
	start = QtCore.pyqtSignal()
	finishThread = QtCore.pyqtSignal(str, str, bool)
	updateValue = QtCore.pyqtSignal(int)

	#Definition of a GenKey_Worker
	def __init__(self, IP, user, password):
		super(GenKey_Worker, self).__init__()
		self.IP = IP
		self.user = user
		self.password = password
		self.start.connect(self.run)
		self.finishMessage = ""
		self.error = False
		self.sleepTime = 1


	#This function connects to the remote robot and pushes the new RSA key
	@QtCore.pyqtSlot()
	def run(self):

		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			self.ssh.connect(self.IP, 22, username=self.user,
							 password=self.password, allow_agent=False, look_for_keys=False)

			#Create the shell for the current index
			self.channel = self.ssh.invoke_shell()
			self.channel.settimeout(1.0)

			#Changes the remote robot's .ssh directory permissions to the user remote user
			self.launchChmod()

			#Pushes the public key to the remote robot
			self.launchPushKey()

		except paramiko.ssh_exception.AuthenticationException:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to password mismatch"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to the remote host not having ssh installed or is unreachable (firewall)"

		#Finish thread
		self.ssh.close()
		self.finishThread.emit(self.IP, self.finishMessage, self.error)


	#Changes the remote robot's directory permissions to be able to push a public key to the .ssh directory
	def launchChmod(self):

		# update the progress bar
		self.updateValue.emit(10)

		# ssh into the device
		self.channel.send("ssh " + str(self.user + "@" + str(self.IP + '\n')))
		self.waitFinishCommandChmod()

		# check if the ssh to the device worked properly
		if self.error is False:
			# if the ssh command worked then do the permissions modification to the file

			# update the progress bar
			self.updateValue.emit(12)

			# change the owner of ssh directory
			self.channel.send('sudo chown -R ' + str(self.user) + ' ~/.ssh/\n')
			self.waitFinishCommandChmod()

			# update the progress bar
			self.updateValue.emit(8)

			# change the owner of ssh directory
			self.channel.send('sudo chgrp -R ' + str(self.user) + ' ~/.ssh/\n')
			self.waitFinishCommandChmod()

			# update the progress bar
			self.updateValue.emit(10)

			# change the permission of the authorized key file
			self.channel.send('sudo chmod 700 ~/.ssh\n')
			self.waitFinishCommandChmod()

			# update the progress bar
			self.updateValue.emit(10)

			# change the permission of ssh directory
			self.channel.send('sudo chmod 600 ~/.ssh/authorized_keys\n')
			self.waitFinishCommandChmod()


	#Loops indefinitely until the Chmod commands have finished executing or if the user has interrupted the current shell
	def waitFinishCommandChmod(self):
		while True:

			#Wait a little bit
			time.sleep(self.sleepTime)

			#Retrieve the data from the shell
			data = str(self.channel.recv(1024).decode("utf-8"))

			#Check the possible different end of commands and adapt the behaviour
			if self.error is True:
				break

			elif '[sudo]' in data:
				self.channel.send(self.password + "\n")
				self.waitFinishCommandChmod()
				break

			elif "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommandChmod()
				break

			elif "password:" in data:
				self.channel.send(self.password + "\n")
				self.waitFinishCommandChmod()
				break

			#If the password is wrong and the user cannot ssh to the device change the boolean error
			elif "Permission denied" in data:
				self.channel.send("\x03\n")
				self.error = True
				self.finishMessage = "X - " + self.IP + ": Wrong Password \n"
				break

			elif "passphrase for key" in data:
				self.channel.send("\n")
				self.waitFinishCommandChmod()
				break

			elif self.user+ "@" in data:
				break


	#Pushes the public RSA key to the remote robots
	def launchPushKey(self):
		# update the progress bar
		self.updateValue.emit(10)

		# create the public keys and send it to the right device
		copy = "sshpass -p \"" + str(self.password + "\" ssh-copy-id -i ~/.ssh/multikey " + str(self.user + "@" + str(self.IP))) + "\n"
		subprocess.call(copy, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)

		# update the progress bar
		self.updateValue.emit(15)

		# wait for the end of the command and check for possible error like : the ip device is wrong or the user device is wrong
		self.waitFinishCommandKey("Permission denied", self.user + "@")

		# update the progress bar
		self.updateValue.emit(10)

		# If an error occurs, append the error string to the finishMessage
		if self.error is False:
			self.finishMessage = "V - " + self.IP + ": RSA Public Key set up"


	#Loops indefinitely until the RSA key has been setup or if the user has interrupted the shell
	def waitFinishCommandKey(self, errorString, endString):
		while True:
			try:
				# wait a little bit
				time.sleep(self.sleepTime)

				# retrieve the data from the thread shell
				data = str(self.channel.recv(1024).decode("utf-8"))
				# if an error has already occurs finish the thread
				if self.error is True:
					break

				# check the possible error during the process and append error message to the output string
				elif errorString in data:
					if errorString == "Permission denied":
						self.channel.send("\x03\n")
					self.error = True
					break

				# check the possible different end of commands
				elif "continue connecting (yes/no)" in data:
					self.channel.send("yes\n")
					self.waitFinishCommandKey(errorString, endString)
					break

				elif "password:" in data:
					self.channel.send(self.password + "\n")
					self.waitFinishCommandKey(errorString, endString)
					break

				elif '[sudo]' in data:
					self.channel.send(self.password + "\n")
					self.waitFinishCommandChmod()
					break

				elif endString in data:
					break

				elif self.user + "@" in data:
					break

			except socket.timeout:
				break

