**MULTILAUNCHER**
=================

A utility that facilitates connecting to multiple remote computers/robots,
downloading remote repositories to those remote computers, and
executing a series of commands simultaneously on the computers.

**Table of Contents**
---------------------

1. [Installation](#Installation)
2. [Important Notes Before Running](#Important Notes Before Running)
3. [Running the Application](#Running the Application)
    A. [File Browser](#File Browser)
    B. [File Transfer](#File Transfer)
    C. [Command Editor](#Command Editor)
    D. [Passwords and Using RSA KEYS](#Passwords and Using RSA KEYS)
    
4. [Developer Tips](#Developer Tips)
5. [Built With](#Built With)
6. [Authors](#Authors)
7. [License](#License)



<a name="Installation"/>

**Installation**
----------------

1. If not already installed, install openssh-client on both the machine running this executable and the remote robots.

2. Pull this repository to your local machine.

3. Navigate to the repository and launch the Multilauncher executable at ~/path/to/directory/Multilaunch/dist/.




<a name="Important Notes Before Running"/>


**Important Notes Before Running**
----------------------------------

-Make sure all computers are on the same network.

-Check that port 11311 is allowed through the firewall on the ROSMASTER machine (if not type: sudo ufw allow 11311).

-If you intend to work with more than 10 computers go to the directory at "/etc/ssh/sshd_config" and
	find/add the "MaxSessions" variable and set it equal to or greater than the number of computers to be used.
	A warning will popup if you add more than the "MaxSessions" number of computers to the list of robots.


<a name="Running the Application"/>


**Running the Application**
---------------------------

-Once the the Multilauncher is running, the MainWindow will be displayed.

-A majority of the Multilauncher's functions will be deactivated until valid data is present in the textfields and
	when the listed computers/robots have all been successfully pinged as denoted in the Connection Status textfield.



**File Browser** <a name="File Browser"/>


**Adding/Removing Robots Manually:**

-From the MainWindow, click on the "Add/Edit/Remove Robots" button to bring up the EditRobot dialog window.

**-Add a new robot:** Type the robot's IP address into the first textfield to the right of the "Selected" label,
                  the robot's user/host name in the middle textfield, the robot's type/model in the last textfield, and
			      finally click on the "Add Robot" button to add the new robot to the robot table.
                  A message will appear next to the "result" label informing you if the operation was successful or how it might have failed.
	
**-Remove a robot:** Click on any of the intended robot's table entries and then click the "Delete Robot" button.
				 To help identify the robot to be deleted its data will be loaded into the three textfields under the table.
	
	Warning!: If you have multiple robots listed in the robot table and have selected one, clicking the "Delete Robot" button multiple times
				will delete the currently selected robot, then the robots above the original deletion, and finally the ones under the original deletion.
				
    Example: Robots listed in the order of: 1, 2, 3, 4, 5.  
              If 3 is selected first and the "Delete Robot" button is clicked multiple times it will 
              delete in this order: 3, 2, 1, 4, 5. 

**-Save the current list of robots in the robot table to the MainWindow:** Click the "Save and Exit" button.


**Adding Robots via a .csv File:**

-From the MainWindow, click on the "Find Robotlist file" button and a FileDialog window will be displayed.
    Navigate to your robotlist.csv file is located and click "Open".
	

**Saving the Current List of Robots to a .csv File:**

-From the MainWindow, click on the "Save Current Data to File" button and a FileDialog window will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click "Save".


**Pinging the Listed Robots:**

-From the MainWindow, click on the "Ping Robots" button to begin pinging the robots listed under "Robot's IP Address".  
    
-Each tab displays the current status of pinging each listed IP address.  
    
-If the IP address has been found a found message will be displayed in the associated tab while IP addresses 
    that have not been found will continue to ping up to a set number of times (default is 100 times).
    
-All pinging threads can be interrupted and closed by clicking the "Stop all unfinished threads" button.  
    
-Once all IP addresses have been found, reached the ping limit, or been interrupted
    by the user a information dialog box will display an acknowledgement that the ping operation is finished.
    
-If all IP addresses have been successfully found the application will "unlock" the remaining buttons and textfields
    in the MainWindow
        
    Warning!: Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
              from editing the listed robots or performing any other thread based function.
              Warnings will be displayed if attempting to run one of these functions.


**Adjusting Robot Arguments:**

-From the MainWindow and after successfully pinging the listed robots, click on the "Adjust Arguments" button to open
    the Adjust Arguments dialog window.

-Argument requirements are grouped together based on robot type.

-The top part of the ArgumentWindow lists the different types of robots listed in the MainWindow and contains a spinbox
    that controls how many arguments are required for each robot type.
    
-The bottom part of the ArgumentWindow displays the listed robots grouped together as a series of trees each containing
    a single type, the robots that are of that type, and the required number of arguments for each robot of that type.

-Red lines in the Argument Column indicate missing arguments for that robot and green lines indicate acknowledged 
    arguments.  It is up to the user to make sure the arguments themselves are correct.
    
**-Save the current list of robot arguments in the argument tree to the MainWindow:** Click the "Save" button.


**File Transfer** <a name="File Transfer"/>


**Transferring Repositories:**

-To prevent re-entering data multiple times please follow this sequence of steps.

1. From the MainWindow and after successfully pinging the listed robots, select the number of that need to be pulled
    from remote repositories with the "Select number of Packages" spinbox.  (If you need 3 packages for turtlebots and 
    2 for quadcopters you would set the spinbox to 5)

2. Use the "Parent Package Directory" button to use a FileDialog window to select your destination for the remote repository or
    manually type the destination directory into the corresponding text field under "Destination Directory".

3. Manually type the remote repository into the corresponding text field under "Remote Repository".

4. Select the type of robot this git pull operation should be performed on in the corresponding spinbox under "Robot Type".

5. Select the Catkin operation that should be performed on this directory  in the corresponding spinbox under "Catkin Option".
    "no make" is the default option and does not perform a catkin make or build operation.
    
6. Repeat steps 2-5 until all packages are setup for transfer.
    
7. When all the packages are ready to be transferred to the remote robots, click the "Transfer Files" button.
    This will either bring up the PasswordWindow for processing passwords for each robot or if the
    "Use RSA Key" checkbox is currently checked the application will skip the PasswordWindow and go straight into starting the
    LaunchWindow.  
    
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and RSA checkbox.

    
    Warning!: Changing the number of packages in the "Select Number of Packages" spinbox will reset all previously set
              data for "Destination Directory", "Remote Repository", "Robot Type", and "Catkin Option" columns.

    Warning!: Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
              from editing the listed robots or performing any other thread based function.
              Warnings will be displayed if attempting to run one of these functions.


**Update ROS MASTER URI IP in the ~/.bashrc on the Remote Robots:**

-From the MainWindow and after successfully pinging the listed robots, type the desired IP address into the 
    "ROS MASTER URI IP ADDRESS" textfield and click the "Update .bashrc" button.  This will either bring up 
    the PasswordWindow for processing passwords for each robot or if the "Use RSA Key" checkbox is currently checked
    the application will skip the PasswordWindow and go straight into starting the LaunchWindow.  
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and RSA checkbox.

    Warning!: Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
              from editing the listed robots or performing any other thread based function.
              Warnings will be displayed if attempting to run one of these functions.


**Command Editor** <a name="Command Editor"/>


**Preparing Commands for Robots:**

-From the MainWindow and after successfully pinging the listed robots, the tabbed section of the Command will display
    one tab per listed robot type from the "Robot's Type/Configuration" list.
    
-Within each tab is a textfield that can be edited manually and is used to save and send a series of commands to the remote robots.

-A majority of commandline style commands are valid for use with the Command Editor.


**Adding Commands via a .txt File:**

-From the MainWindow, click on the "Load Commands File" button and a FileDialog window will be displayed.
    Navigate to your commands.txt file is located and click "Open".

    Note about loading commands from a file: The application will only load the commands present in the .txt file
    to the currently selected tab.
	

**Saving the Current List of Commands to a .txt File:**

-From the MainWindow, click on the "Save Current Data to File" button and a FileDialog window will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click "Save".

    Note about saving commands to a file: The application will only save the commands present in the currently selected
    tab to the .txt file.


**Launching the Listed Robots and Commands:**

-From the MainWindow and after commands have been entered into the tabbed textfields, click the "Launch All" button. 
    This will either bring up the PasswordWindow for processing passwords for each robot or if the "Use RSA Key" checkbox
    is currently checked the application will skip the PasswordWindow and go straight into starting the LaunchWindow.  
    
-Please refer to the section Passwords and Using RSA Keys for more detailed information on the PasswordWindow and RSA checkbox.

    Warning!: Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
              from editing the listed robots or performing any other thread based function.
              Warnings will be displayed if attempting to run one of these functions.


**Passwords and Using RSA KEYS** <a name="Passwords and Using RSA KEY"/>


-The "Use RSA Key" checkbox is used when a RSA key has been successfully pushed to all the remote robots and is used
    to skip entering in all robot passwords for every launch.  


**PasswordWindow:**

-When the PasswordWindow is displayed, the center will list all of the remote robots with a corresponding textfield
    for password entry.

-To either launch the commands or generate a new RSA key all password fields must be filled (Correct is optional).

-Clicking the "Launch the Command" button starts the process of remote SSH'ing and sending the commands to the robots.

-Clicking the "Generate RSA Key" button brings up the GenerateRSAKeyWindow.

    Warning!: Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
              from editing the listed robots or performing any other thread based function.
              Warnings will be displayed if attempting to run one of these functions.


**GenerateRSAKeyWindow:**

-To generate a new set of RSA keys, enter the username and password of the computer running this application into
    the appropriate textfields and click on the "Generate Key" button.
    
    Warning!: When generating the RSA Key the ownership of the ~/.ssh directory on the remote machine will be set
              to the user and the file permissions will be set to default.


<a name="Developer Tips"/>


**Developer Tips**
------------------

Just Don't


<a name="Built With"/>


**Built With**
--------------

-PyCharm: IDE used

-QtDesigner: Used to create base .ui files


<a name="Author"/>


**Authors**
-----------

-Matthew Hovatter: Co-Author

-Paul Buzaud: Co-Author


<a name="License"/>


**License**
-----------
