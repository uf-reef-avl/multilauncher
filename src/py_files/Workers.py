#
# File: Workers.py
# Author: Paul Buzaud and Matthew Hovatter
#
# Created:
#

from PyQt5 import QtCore
import os
import paramiko
import time
import logging
import sys

logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())

PING_TIMEOUT = 100

#Creates and runs the SSH_Transfer_File_Worker class and its methods
class SSH_Transfer_File_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, str)
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
				self.channel.send('mkdir -p ' + self.parentPackageDirList[i] + '\n')
				self.waitFinishCommand()
				self.channel.send('cd ' + self.parentPackageDirList[i] + '\n')
				self.waitFinishCommand()

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

		except paramiko.ssh_exception.SSHException:
			if self.password:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

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
			flag = self.waitFinishCommand()

			#If the local repository has been changed
			if flag != "No local changes to save":
				self.channel.send('git checkout master\n')
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
			self.terminalSignal.emit(self.ipIndex, data)

			if 'Username for ' in data:
				self.channel.send(self.gitUsername + '\n')

			if 'Password for ' in data:
				self.channel.send(self.gitPassword + '\n')

			if "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()

			if "No such file or directory" in data:
				return "no file"

			elif "No local changes to save" in data:
				return "No local changes to save"

			elif "Checking connectivity... done" in data:
				return "done"

			if self.user + "@" in data:
				break

#Creates and runs the Launch_Worker class and its methods
class Launch_Worker(QtCore.QObject):

	#Variables for emitting starting, displaying status, and closing signals
	start = QtCore.pyqtSignal()
	terminalSignal = QtCore.pyqtSignal(int, str)
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


	#This function connects to the remote robot and executes the user's list of commands
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

			#Execute the list of commands
			self.channel = ssh.invoke_shell()
			for i in self.commandList:
				if self.stopSignal:
					break
				self.channel.send(str(i)+ '\n')
				self.waitFinishCommand()

		except paramiko.ssh_exception.SSHException:
			if self.password:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

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
			self.terminalSignal.emit(self.ipIndex, data)

			if '[sudo]' in data and self.password is not None:
				self.channel.send(self.password + '\n')
				self.waitFinishCommand()
				break

			if '[Y/n]' in data:
				self.channel.send('Y\n')
				self.waitFinishCommand()
				break

			if '[y/N]' in data:
				self.channel.send('y\n')
				self.waitFinishCommand()
				break

			if "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()
			if self.user + "@" in data:
				break


#Creates and runs the Bashrc_Worker class and its methods
class Bashrc_Worker(QtCore.QObject):

	#Preparing for starting and closing signals
	start = QtCore.pyqtSignal()
	finishThread = QtCore.pyqtSignal(int,str)
	terminalSignal = QtCore.pyqtSignal(int, str)


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
			self.channel.send(' echo export ROS_MASTER_URI=http://'+self.masterIP+':11311 >> ~/.bashrc\n')
			self.waitFinishCommand()
			self.channel.send(' echo export ROS_HOSTNAME='+self.IP+' >> ~/.bashrc\n')
			self.waitFinishCommand()

		except paramiko.ssh_exception.SSHException:
			if self.password:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to password mismatch"
			elif self.password is None:
				self.finishMessage = self.IP+" SSH Error: Attempt to talk to robot failed due to missing RSA key on remote robot"

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
			self.terminalSignal.emit(self.ipIndex, data)
			if "continue connecting (yes/no)" in data:
				self.channel.send("yes\n")
				self.waitFinishCommand()
			if self.user + "@" in data:
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
			response = os.system("ping -c1 " + self.IP)

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
