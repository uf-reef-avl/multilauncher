**MULTILAUNCHER**
=================

A utility that facilitates connecting to multiple remote computers/robots,
downloading remote repositories to those remote computers, and
executing a series of commands simultaneously on remote machines

**Table of Contents**
---------------------

1. [Installation](#Installation)

2. [Important Notes Before Running](#Important Notes Before Running)

3. [Running the Application](#Running the Application)

    A. [File Browser/RoboData](#File Browser/RoboData)
        
     1. [Adding Robots via a .csv File](#Adding Robots via a csv File)
     
     2. [Saving the Current List of Robots to a .csv File](#Saving the Current List of Robots to a csv File)
     
     3. [Enabling and Disabling Listed Robots](#Enabling and Disabling Listed Robots)
     
     4. [Adding/Removing Robots Manually](#Adding/Removing Robots Manually)
     
     5. [Updating the MaxSessions Variable](#Updating the MaxSessions Variable)
     
     4. [Pinging the Listed Robots](#Pinging the Listed Robots)
     
     5. [Adjusting Robot Arguments](#Adjusting Robot Arguments)
    
    B. [Git Repository](#Git Repository)
     
     1. [Pulling Repositories](#Pulling Repositories)
     
     2. [Update ROS MASTER URI IP in the ~/.bashrc on the Remote Robots](#Update ROS MASTER URI IP in the bashrc on the Remote Robots)
   
    C. [Command Editor](#Command Editor)
     
     1. [Preparing Commands for Robots](#Preparing Commands for Robots)
     
     2. [Adding Commands via a .txt File](#Adding Commands via a txt File)
     
     3. [Saving the Current List of Commands to a .txt File](#Saving the Current List of Commands to a txt File)
     
    D. [Launching](#Launching)
    
    E. [Passwords and Using RSA KEYS](#Passwords and Using RSA KEYS)
    
     1. [PasswordWindow](#PasswordWindow)
     
     2. [GenerateRSAKeyWindow](#GenerateRSAKeyWindow)
    
4. [Developer Tips](#Developer Tips)

5. [Built With](#Built With)

6. [Authors](#Authors)

7. [License](#License)



<a name="Installation"/>


**Installation**
----------------

1. If not already installed, install openssh-client on both the machine running this executable and the remote machines.

2. Pull this repository to your local machine.

3. Navigate to the repository and launch the Multilauncher executable at ~/path/to/directory/multilaunch/dist/.


<a name="Important Notes Before Running"/>


**Important Notes Before Running**
----------------------------------

-Make sure all computers are on the same network.

-Check that port 11311 is allowed through the firewall on the ROSMASTER machine (if not type: sudo ufw allow 11311).

-If you intend to work with more than 10 computers go to the directory at "/etc/ssh/sshd_config" and
	find/add the "MaxSessions" variable and set it equal to or greater than the number of computers to be used or
	use the "Update MaxSessions" button from the MainWindow.
	A warning will popup if you add more than the "MaxSessions" number of computers to the list of robots.


<a name="Running the Application"/>


**Running the Application**
---------------------------

-Once the the Multilauncher is running, the MainWindow will be displayed.

-A majority of the Multilauncher's functions will be deactivated until valid data is present in the Robot Table and
	when the listed computers/robots have all been successfully pinged as denoted in the Connection Status column.



**File Browser/RoboData** <a name="File Browser/RobotData"/>


**Enabling and Disabling Listed Robots:** <a name="Enabling and Disabling Listed Robots"/>

-From the MainWindow clicking on a checkbox listed in the robot table will alternate the checked status of a individual 
    robot between checked (Enabled) and unchecked (Disabled)

-Clicking on the "Enable/Disable All" button will alternate all "Enabled" checkboxes listed in 
    the robot table between checked (Enabled) and unchecked (Disabled)


**Adding/Removing Robots Manually:** <a name="Adding/Removing Robots Manually"/>

-From the MainWindow, click on the "Add/Edit/Remove Robots" button to bring up the EditRobot dialog window.

-Add a new robot: Type the robot's IP address into the first textfield under the "New/Selected: IP Address" label,
                  the robot's user/host name in the middle textfield under the "New/Selected: Robot Name" label, 
                  the robot's type/model in the last textfield under the "New/Selected: Robot Type" label, and
			      finally click on the "Add Robot" button to add the new robot to the robot table.
                  A message will appear next to the "result" label informing you if the operation was successful or how it might have failed.

-Modify a robot: Click on any of the intended robot's table entries to load the selected robot's data into the three "New/Selected" textfields under the table.
                 Retype the relevant values into textfields and click on the "Modify Robot" button to update the entry in the robot table.


-Remove a robot: Click on any of the intended robot's table entries and then click the "Delete Robot" button.
				 To help identify the robot to be deleted its data will be loaded into the three "New/Selected" textfields under the table.
	
	Warning!: If you have multiple robots listed in the robot table and have selected one, clicking the "Delete Robot" button multiple times
				will delete the currently selected robot, then the robots above the original deletion, and finally the ones under the original deletion.
				
    Example: Robots listed in the order of: 1, 2, 3, 4, 5.  
              If 3 is selected first and the "Delete Robot" button is clicked multiple times it will 
              delete in this order: 3, 2, 1, 4, 5. 

-Save the current list of robots in the robot table to the MainWindow by clicking the "Save and Exit" button.


**Updating the MaxSessions Variable:** <a name="Updating the MaxSessions Variable"/>

-From the MainWindow, clicking on the "Update MaxSessions" button will either bring up a information dialog when your
    combined number of enabled robots and their "ROSMASTER Settings" does not exceed the value set in the MaxSessions
    variable or prompt the user for root credentials through PolicyKit to perform file operations in the /etc/ssh/sshd_config file.


**Adding Robots via a .csv File:** <a name="Adding Robots via a csv File"/>

-From the MainWindow, click on the "Find Robotlist file" button and a FileDialog window will be displayed.
    Navigate to your robotlist.csv file is located and click "Open".
	

**Saving the Current List of Robots to a .csv File:** <a name="Saving the Current List of Robots to a csv File"/>

-From the MainWindow, click on the "Save Current Data to File" button and a FileDialog window will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click "Save".


**Pinging the Listed Robots:** <a name="Pinging the Listed Robots"/>

-From the MainWindow, click on the "Ping Robots" button to begin pinging the robots listed in the robot table.  
    
-Each tab displays the current status of pinging each listed robot's IP address from the robot table.  
    
-If the IP address has been found a found message will be displayed in the associated tab while IP addresses 
    that have not been found will continue to ping up to a set number of times (default is 100 times).

-All pinging threads can be interrupted and closed individually or all at the same time by clicking the 
    "Stop Current Thread" and "Stop all unfinished threads" buttons respectively.  
    
-Once all IP addresses have been found, reached the ping limit, or been interrupted
    by the user, a information dialog box will display an acknowledgement that the ping operation is finished.
    
-If all IP addresses have been successfully found the application will "unlock" the remaining buttons and features
    in the MainWindow

    Warning!: Closing the LaunchWindow before all threads have finished terminates the running threads.


**Adjusting Robot Arguments:** <a name="Adjusting Robot Arguments"/>

-From the MainWindow and after successfully pinging the listed robots, click on the "Adjust Arguments" button to open
    the Adjust Arguments dialog window.

-Argument requirements are grouped together based on robot type.

-The top part of the ArgumentWindow lists the different types of robots and contains a spinbox that controls how many 
    arguments are required for each robot type.
    
-The bottom part of the ArgumentWindow displays the listed robots grouped together as a series of trees each containing
    a single type, the robots that are of that type, and the required number of arguments for each robot of that type.

-Red lines in the Argument Column indicate missing arguments for that robot and green lines indicate acknowledged 
    arguments.  It is up to the user to make sure the arguments themselves are correct.
    
-Save the current list of robot arguments in the argument tree to the MainWindow by clicking the "Save" button.


**Git Repository** <a name="Git Repository"/>


**Pulling Repositories:** <a name="Pulling Repositories"/>

-To pull repositories please follow this sequence of steps.

1. From the MainWindow and after successfully pinging the listed robots, select the number of that need to be pulled
    from remote repositories with the "Select number of Packages" spinbox.  (If you need 3 packages for turtlebots and 
    2 for quadcopters you would set the spinbox to 5)

2. Use the "Parent Package Directory" button to use a FileDialog window to select your destination for the remote repository or
    manually type the destination directory into the corresponding text field under "Destination Directory".

3. Manually type the remote repository URL into the corresponding text field under "Remote Repository".

4. Select the type of robot this git pull operation should be performed on in the corresponding spinbox under "Robot Type".

5. Select the Catkin operation that should be performed on this directory  in the corresponding spinbox under "Catkin Option".
    "no make" is the default option and does not perform a catkin make or build operation.
        
6. When all the packages are ready to be transferred to the remote robots, click the "Transfer Files" button.
    This will either bring up the PasswordWindow for processing passwords for each robot or if the
    "Use RSA Key" checkbox is currently checked the application will skip the PasswordWindow and go straight into starting the
    LaunchWindow.  
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and RSA checkbox.

    Warning!: Closing the LaunchWindow before all threads have finished terminates the running threads.


**Update ROS MASTER URI IP in the ~/.bashrc on the Remote Robots:** <a name="Update ROS MASTER URI IP in the bashrc on the Remote Robots"/>

-From the MainWindow and after successfully pinging the listed robots, click the "Update .bashrc" button.  
    This will either bring up the PasswordWindow for processing passwords for each robot or if the "Use RSA Key" checkbox 
    is currently checked the application will skip the PasswordWindow and go straight into starting the LaunchWindow.  
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and RSA checkbox.

    Warning!: Closing the LaunchWindow before all threads have finished terminates the running threads.


**Command Editor** <a name="Command Editor"/>


**Preparing Commands for Robots:** <a name="Preparing Commands for Robots"/>

-From the MainWindow and after successfully pinging the listed robots, the tabbed section of the Command will display
    one tab per listed robot type from the "Robot's Type/Configuration" column.
    
-Within each tab is a textfield that can be edited manually and is used to send a series of commands to the remote robots.

-A majority of commandline style commands are valid for use with the Command Editor.


**Adding Commands via a .txt File:** <a name="Adding Commands via a txt File"/>

-From the MainWindow, click on the "Load Commands File" button and a FileDialog window will be displayed.
    Navigate to your commands.txt file is located and click "Open".

    Note about loading commands from a file: The application will only load the commands present in the .txt file
    to the currently selected tab.
	

**Saving the Current List of Commands to a .txt File:** <a name="Saving the Current List of Commands to a txt File"/>

-From the MainWindow, click on the "Save Current Data to File" button and a FileDialog window will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click "Save".

    Note about saving commands to a file: The application will only save the commands present in the currently selected
    tab to the .txt file.


**Launching** <a name="Launching"/>


-To launch all enabled robots of all types, click the "Launch All" button. 
    This will either bring up the PasswordWindow for processing passwords for each robot or if the "Use RSA Key" checkbox
    is currently checked the application will skip the PasswordWindow and go straight into starting the LaunchWindow.  
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and the RSA checkbox.


**Passwords and Using RSA KEYS** <a name="Passwords and Using RSA KEYS"/>


-The "Use RSA Key" checkbox is used when a RSA key has been successfully pushed to all the remote robots and allows the user
    to skip entering in all robot passwords for every launch.


**PasswordWindow:** <a name="PasswordWindow"/>

-When the PasswordWindow is displayed, the center will list all of the remote robots with a corresponding textfield
    for password entry.

-To either launch the commands all password fields must be filled (Correct is optional).

-Clicking the "Launch the Command" button starts the process of remote SSH'ing and sending the commands to the robots.



**GenerateRSAKeyWindow:** <a name="GenerateRSAKeyWindow"/>

-To generate a new set of RSA keys click on the "Generate Key" button from the MainWindow.
    
    Warning!: When generating the RSA Key the ownership of the ~/.ssh directory on the remote machine will be set
              to the user and the file permissions will be set to default.


<a name="Developer Tips"/>


**Developer Tips**
------------------

-


<a name="Built With"/>


**Built With**
--------------

-Python 2.7: Version of Python

-PyCharm: IDE used

-QtDesigner: Used to create base .ui files


<a name="Authors"/>


**Authors**
-----------

-Matthew Hovatter: Co-Author

-Paul Buzaud: Co-Author


<a name="License"/>


**License**
-----------

