#!/usr/bin/python3
#
# File: Workers.py
# Authors: Matthew Hovatter and Paul Buzaud
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
import getpass


class Manual_Timeout_Exception(Exception):
	"""Used to handle specific timeouts"""


#Creates and runs the SSH_Transfer_File_Worker class and its methods
class SSH_Transfer_File_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, list)
	finishThread = QtCore.pyqtSignal(int,str)


	#Definition of a SSH_Transfer_File_Worker
	def __init__(self, ipIndex, IP, user, parentPackageDirList, gitRepoList, gitUsername, gitPassword, makeOption, password, branches,key):
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
		self.myKey = key
		self.finishMessage = ""
		self.skip = False
		self.buffer = ""
		self.branchList = branches
		self.branchFlag = -1
		self.start.connect(self.run)


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
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

			for index in range(len(self.gitRepoList)):
				if self.stopSignal:
					break

				self.prepPath(index)

				self.prepRepo(index)

				#If there wasn't a problem with the retrieving data from the remote git repository
				if not self.skip:

					#catkin make option
					if self.makeOption[index] == 1:

						self.prepCatkin(index)
						self.channel.send('catkin_make\n')
						self.waitFinishCommand()

					#catkin build option
					elif self.makeOption[index] == 2:

						self.prepCatkin(index)
						self.channel.send('catkin build\n')
						self.waitFinishCommand()


		except paramiko.ssh_exception.AuthenticationException:

			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to password mismatch"

			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to missing RSA key"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not having ssh installed or is unreachable (firewall)"

		except Manual_Timeout_Exception:
			self.finishMessage = self.IP + " Error: Connection to the remote host has been lost due to the remote host not responding within " + str(
				SSH_TIMEOUT) + " seconds"

		except:
			e = sys.exc_info()[0]
			self.finishMessage = self.IP + " SSH Error: An unhandled error has occurred: %s" % e

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Corrects some incorrect user input and/or appends a src directory to hold the local repository
	def prepPath(self, index):

		tempList = self.parentPackageDirList[index].split('/')
		if tempList[-1] != '':
			self.parentPackageDirList[index] = str(self.parentPackageDirList[index] + "/")

		#If a catkin option was selected for this repo
		if self.makeOption[index] != 0:
			if "src" not in tempList:
				self.parentPackageDirList[index] = str(self.parentPackageDirList[index] + "src/")


	#Sets up a new local repo or overrides the local existing repo with the remote one
	def prepRepo(self,index):
		self.channel.send('mkdir -p ' + self.parentPackageDirList[index] + '\n')
		self.waitFinishCommand()
		self.channel.send('cd ' + self.parentPackageDirList[index] + '\n')
		self.waitFinishCommand()

		packageName = self.gitRepoList[index].split('/')[-1]
		if ".git" in packageName:
			packageName = packageName[:-4]

		self.channel.send('cd ' + packageName + '/.git\n')

		#This result tells the program if the desired repository is already present on the remote machine or not
		flag = self.waitFinishCommand()

		#New local repo
		if flag == "no file":

			self.channel.send("mkdir " + str(packageName) + "; cd " + str(packageName) + "; git init; git remote add " +
							  str(packageName) + " "+ self.gitRepoList[index] + "; git fetch " + str(packageName)+ " " + str(self.branchList[index]) +
							  "; git checkout -b " + str(self.branchList[index]) + "; git pull " + str(packageName) + " " + str(self.branchList[index]) +'\n')

			#This result tells the program if the git pull operation was successful or not
			flag = self.waitFinishCommand()

			#Successful git clone
			if flag == "done" or flag == "HEAD":
				self.channel.send('cd ' + self.parentPackageDirList[index] + '\n')
				self.waitFinishCommand()
			else:
				self.skip = True

		#Existing repository on remote machine
		else:

			self.channel.send('cd ..; git stash\n')
			self.waitFinishCommand()

			self.branchFlag = index
			self.channel.send("git branch\n")

			#This result tells the program which version of "git checkout" to use
			flag = self.waitFinishCommand()

			self.channel.send("git " + str(flag) + " " + str(self.branchList[index]) + "; git pull " + str(self.gitRepoList[index]) + " "+str(self.branchList[index]) + "\n")
			self.waitFinishCommand()

			self.channel.send('cd ' + self.parentPackageDirList[index] + '\n')
			self.waitFinishCommand()


	#Sets up for catkin make or build
	def prepCatkin(self, index):

		tempList = self.parentPackageDirList[index].split('/')
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

			try:

				data = self.channel.recv(4096).decode("utf-8")

			except socket.timeout:

				# Ping to see if the remote machine is still receiving
				response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

				# If the remote machine was pinged successfully
				if response == 0:
					continue

				else:
					raise Manual_Timeout_Exception

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

			elif self.branchFlag != -1:
				if str(self.branchList[self.branchFlag]) in data:
					self.branchFlag = -1
					return "checkout"
				else:
					self.branchFlag = -1
					return "checkout -b"

			elif "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")

			elif "No such file or directory" in data:
				return "no file"

			elif "Checking connectivity... done" in data:
				return "done"

			elif "FETCH_HEAD" in data:
				return "HEAD"

			elif self.user + "@" in data:
				break


#Creates and runs the Transfer_Local_File_Worker class and its methods
class Transfer_Local_File_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, list)
	finishThread = QtCore.pyqtSignal(int,str)


	#Definition of a SSH_Transfer_File_Worker
	def __init__(self, ipIndex, IP, user, parentPackageDirList, localList, password, key):
		super(Transfer_Local_File_Worker, self).__init__()
		self.ipIndex = ipIndex
		self.IP = IP
		self.user = user
		self.password = password
		self.parentPackageDirList = parentPackageDirList
		self.localList = localList
		self.terminalRefreshSeconds = 0.75
		self.stopSignal = False
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""
		self.start.connect(self.run)


	#This function connects to the remote robot and performs a git pull operation on the selected remote repository
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

			#Pull the selected directory and push it to the desired location on the remote robot
			self.channel = ssh.invoke_shell()
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

			for index in range(len(self.localList)):
				if self.stopSignal:
					break

				string = []

				try:

					# FIXME rsync problem: can't find directory when not shelled
					# if self.password is not None:
					# 	subprocess.check_output(["sshpass", "-p", str(self.password), "rsync", "-r", str(self.localList[index]), self.user+"@"+self.IP+":"+str(self.parentPackageDirList[index])])
					# else:
					# 	subprocess.check_output(["rsync", "-r", str(self.localList[index]), self.user+"@"+self.IP+":"+str(self.parentPackageDirList[index])])


					if self.password is not None:
						subprocess.check_output("sshpass -p \"" + str(self.password) + "\" rsync -v -r " + str(
							self.localList[index]) + " " + self.user + "@" + self.IP + ":" + str(
							self.parentPackageDirList[index]), stderr=subprocess.STDOUT, shell=True)
					else:
						subprocess.check_output(
							"rsync -v -r " + str(self.localList[index]) + " " + self.user + "@" + self.IP + ":" + str(
								self.parentPackageDirList[index]), stderr=subprocess.STDOUT, shell=True)


					string.append("Successfully transferred: " + str(self.localList[index]) + "\nto destination: " + str(self.parentPackageDirList[index]) + "\n\n")
					self.terminalSignal.emit(self.ipIndex, string)

				except subprocess.CalledProcessError as exc:
					string.append("Error when transferring: "+str(self.localList[index])+" "+str(exc.output)+"\n")
					self.terminalSignal.emit(self.ipIndex, string)

		except paramiko.ssh_exception.AuthenticationException:

			ssh.close()
			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to password mismatch"

			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to missing RSA key"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not being verified"
			ssh.close()

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not having ssh installed or is unreachable (firewall)"
			ssh.close()

		except:
			e = sys.exc_info()
			self.finishMessage = self.IP + " SSH Error: An unhandled error has occurred: %s" % str(e)
		ssh.close()

		#Closing the thread
		self.finishThread.emit(self.ipIndex, self.finishMessage)


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
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""
		self.start.connect(self.run)


	#This function connects to the remote robot and executes the user's list of commands
	@QtCore.pyqtSlot()
	def run(self):

		ssh = paramiko.SSHClient()

		#Creating a password or rsa key based ssh connection
		try:

			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.password is not None:
				ssh.connect(self.IP, 22, username = self.user, password = self.password, allow_agent = False, look_for_keys = False)
			else:
				ssh.connect(self.IP, 22, username = self.user, pkey = self.myKey)

			self.channel = ssh.invoke_shell()
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

			#Execute the list of commands
			for i in self.commandList:
				if self.stopSignal:
					break
				self.channel.send(str(i)+ '\n')
				self.waitFinishCommand()

			#Allows the user to send additional commands like a terminal until closed
			while True:
				if self.stopSignal:
					break
				self.waitFinishCommand()

		except paramiko.ssh_exception.AuthenticationException:
			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to password mismatch"

			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to missing RSA key"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not having ssh installed or is unreachable (ex: Firewall blocking the connection)"

		except Manual_Timeout_Exception:
			self.finishMessage = self.IP + " Error: Connection to the remote host has been lost due to the remote host not responding within " + str(
				SSH_TIMEOUT) + " seconds"

		except:
			e = sys.exc_info()[0]
			self.finishMessage = self.IP + " SSH Error: An unhandled error has occurred: %s" % e

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break

			time.sleep(self.terminalRefreshSeconds)

			try:

				data = self.channel.recv(4096).decode("utf-8")

			except socket.timeout:

				# Ping to see if the remote machine is still receiving
				response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

				# If the remote machine was pinged successfully
				if response == 0:
					continue

				else:
					raise Manual_Timeout_Exception

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
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""
		self.start.connect(self.run)


	# This function connects to the remote robot and executes roscore command
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
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

			self.channel.send('roscore\n')
			self.waitFinishCommand()

			while True:
				if self.stopSignal:
					break
				self.waitFinishCommand()


		except paramiko.ssh_exception.AuthenticationException:

			if self.password:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to password mismatch"

			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to missing RSA key"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not having ssh installed or is unreachable (firewall)"

		except Manual_Timeout_Exception:
			self.finishMessage = self.IP + " Error: Connection to the remote host has been lost due to the remote host not responding within " + str(
				SSH_TIMEOUT) + " seconds"

		except:
			e = sys.exc_info()[0]
			self.finishMessage = self.IP + " SSH Error: An unhandled error has occurred: %s" % e

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break

			time.sleep(self.terminalRefreshSeconds)

			try:

				data = self.channel.recv(4096).decode("utf-8")

			except socket.timeout:

				# Ping to see if the remote machine is still receiving
				response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

				# If the remote machine was pinged successfully
				if response == 0:
					continue

				else:
					raise Manual_Timeout_Exception

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
		self.myKey = key
		self.finishMessage = ""
		self.buffer = ""
		self.start.connect(self.run)


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
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

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
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to password mismatch"

			elif self.password is None:
				self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to missing RSA key"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = self.IP + " SSH Error: Attempt to ssh to remote host failed due to the remote host not having ssh installed or is unreachable (firewall)"

		except Manual_Timeout_Exception:
			self.finishMessage = self.IP + " Error: Connection to the remote host has been lost due to the remote host not responding within " + str(
				SSH_TIMEOUT) + " seconds"

		except:
			e = sys.exc_info()[0]
			self.finishMessage = self.IP + " SSH Error: An unhandled error has occurred: %s" % e

		#finish thread
		ssh.close()
		self.finishThread.emit(self.ipIndex, self.finishMessage)


	#Loops indefinitely until the current set of commands has been fully executed or if the user has interrupted the threads
	def waitFinishCommand(self):
		while True:
			if self.stopSignal:
				break

			time.sleep(self.terminalRefreshSeconds)

			try:

				data = self.channel.recv(4096).decode("utf-8")

			except socket.timeout:

				# Ping to see if the remote machine is still receiving
				response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

				# If the remote machine was pinged successfully
				if response == 0:
					continue

				else:
					raise Manual_Timeout_Exception

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
		self.stopSignal = False
		self.responseString = ""
		self.errorString = ""
		self.start.connect(self.run)


	#This function pings the robot
	@QtCore.pyqtSlot()
	def run(self):

		#Ping until you reach the set maximum number of pings
		for x in range(NUM_OF_PINGS):

			#If the user has pressed the stop unfinished threads button
			if self.stopSignal:
				break

			#The actual ping message sent and the response back
			response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

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
		self.finishMessage = ""
		self.error = False
		self.terminalRefreshSeconds = 0.75
		self.start.connect(self.run)


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
			self.channel.get_transport().set_keepalive(KEEPALIVE)
			self.channel.settimeout(SSH_TIMEOUT)

			if self.checkForKey():

				#Update the progress bar
				self.updateValue.emit(15)

				#Pushes the public key to the remote robot
				self.pushKey()

			#If the public key is present of remote machine
			if self.error is False:
				self.finishMessage = "V - " + self.IP + ": RSA Public Key is set up"

			#If an error occurs, append the error string to the finishMessage
			else:
				self.finishMessage = "X - " + self.IP + ": RSA Public Key is not set up, permissions to push the public key may be denied"


		except paramiko.ssh_exception.AuthenticationException:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to password mismatch"

		except paramiko.ssh_exception.BadHostKeyException:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to the remote host not being verified"

		except paramiko.ssh_exception.NoValidConnectionsError:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to the remote host not having ssh installed or is unreachable (firewall)"

		except Manual_Timeout_Exception:
			self.finishMessage = "X - Error in connecting to: " + self.IP + " the remote host did not respond within " + str(SSH_TIMEOUT) + " seconds"

		except:
			e = sys.exc_info()
			self.finishMessage = "X - Error in connecting to: " + self.IP + " due to an unhandled error: %s" % e

		#Finish thread
		self.ssh.close()
		self.finishThread.emit(self.IP, self.finishMessage, self.error)


	#Checks the remote machine to see if the public key is already present on the remote machine
	def checkForKey(self):

		rFile = open("/home/" + str(getpass.getuser()) + "/.ssh/multikey.pub", "r")
		listOfLines = rFile.readlines()
		rFile.close()
		listOfLines = listOfLines[0].splitlines()
		pubKey = listOfLines[0]

		self.channel.send("grep -c \""+ str(pubKey) +"\" ~/.ssh/authorized_keys \n")

		#Update the progress bar
		self.updateValue.emit(15)

		if self.waitFinishCheck():
			return True
		else:
			return False


	#Loops indefinitely until the checking commands have finished executing
	def waitFinishCheck(self):
		while True:

			time.sleep(self.terminalRefreshSeconds)

			try:

				data = self.channel.recv(4096).decode("utf-8")
				result = data.split("\n")[-2]

			except socket.timeout:

				#Ping to see if the remote machine is still receiving
				response = os.system("ping -c1 -W 3 " + self.IP + " 2>&1 >/dev/null")

				#If the remote machine was pinged successfully
				if response == 0:
					continue

				else:
					raise Manual_Timeout_Exception

			if "Permission denied" in data:
				self.error = True
				return True

			#There is no /.ssh/ directory or a copy of the public key present on the remote machine
			if "No such file or directory" in data or int(result) == 0:
				return True

			#One or more copies of the public key are present on the remote machine
			elif int(result) >= 1:
				return False


	#Pushes the public RSA key to the remote robots
	def pushKey(self):

		#Push the new key to the remote machine
		copy = "sshpass -p \"" + str(self.password + "\" ssh-copy-id -i ~/.ssh/multikey.pub " + str(self.user + "@" + str(self.IP)))
		subprocess.call(copy, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)

		#Update the progress bar
		self.updateValue.emit(15)

		#Confirm that the public key is on the remote machine
		self.checkForKey()

		#Update the progress bar
		self.updateValue.emit(15)
