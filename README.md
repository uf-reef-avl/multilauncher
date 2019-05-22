NOTICE: This version of multilauncher is up-to-date as of May 22nd, 2019.  Future versions of Multilauncher can be found at: http://192.168.1.101/avl-summer-19/multilauncher


**MULTILAUNCHER**
=================

The Multilauncher utility facilitates connecting to multiple remote machines,
git clone/pulling multiple remote repositories, transferring local files, and
executing a series of commands simultaneously across multiple remote machines.


**Table of Contents**
---------------------

1. [Prerequisites](#Prerequisites)

2. [Installation](#Installation)

3. [Important Notes Before Running](#Important Notes Before Running)

4. [Running the Application](#Running the Application)

    A. [File Browser/RoboData](#File Browser/RoboData)
        
     1. [Adding Robots from a .csv File](#Adding Robots from a csv File)
     
     2. [Saving the Current List of Robots to a .csv File](#Saving the Current List of Robots to a csv File)
     
     3. [Enabling and Disabling Listed Robots](#Enabling and Disabling Listed Robots)
     
     4. [Adding/Removing Robots Manually](#Adding/Removing Robots Manually)
     
     5. [Updating the SSH MaxSessions Variable](#Updating the SSH MaxSessions Variable)
     
     6. [Adjusting Robot Arguments](#Adjusting Robot Arguments)
     
     7. [Pinging the Listed Robots](#Pinging the Listed Robots)

     8. [Update ROSMASTER URI IP in the ~/.bashrc on the Remote Robots](#Update ROSMASTER URI IP in the bashrc on the Remote Robots)

    B. [Local File/Git Repository](#Local File/Git Repository)
     
     1. [Transferring Local Files](#Transferring Local Files)
     
     2. [Pulling Repositories](#Pulling Repositories)
        
    C. [Command Editor](#Command Editor)
     
     1. [Preparing Commands for Robots](#Preparing Commands for Robots)
     
     2. [Adding Commands from a .txt File](#Adding Commands from a txt File)
     
     3. [Saving the Current List of Commands to a .txt File](#Saving the Current List of Commands to a txt File) 
    
    D. [Passwords and Using RSA Keys](#Passwords and Using RSA Keys)
    
     1. [Password Window](#Password Window)
     
     2. [Generating RSA Keys](#Generating RSA Keys)
    
    E. [Launching](#Launching)

5. [Built With](#Built With)

6. [Authors](#Authors)

7. [Acknowledgements](#Acknowledgements)


<a name="Prerequisites"/>

**Prerequisites**
-----------------

- If you are missing any of these prerequisites type "sudo apt update" into the terminal to prepare for installing the
    required software.

- Git
    
    If not already installed, install git on the machine running the Multilauncher utility.
    
    Check for git by typing "git --version" into the terminal.
    
    If git is not present type "sudo apt install git".
    
    More information what git is and how it works can be found at [https://git-scm.com/docs].

- openssh-server

    If not already installed, install openssh-client on both the machine running the Multilauncher utility and the remote machines.
    
    Type "sudo apt install openssh-server" into the terminal to install openssh.

    More information what openssh is and how it works can be found at [https://www.openssh.com/].
    
- pip / pip3

    pip is required for Python 2 distributions while pip3 is required for Python 3 distributions.
    
    pip:
    
    Type "sudo apt install python-pip" into the terminal.
    
    Check the installation of pip with "pip --version".
    
    pip3:
    
    Type "sudo apt install python3-pip" into the terminal.
    
    Check the installation of pip3 with "pip3 --version".

    More information on how to use pip or pip3 are found at [https://pip.pypa.io/en/stable/user_guide/].
    
- paramiko

    Type "pip install paramiko" or "pip3 install paramiko" into the terminal.

    More information what paramiko is and how it works can be found at [http://www.paramiko.org/index.html].


<a name="Installation"/>

**Installation**
----------------

1. Pull this repository to your local machine.

    git clone http://REEF180_SRV/AVL-Summer-18/multilauncher.git

2. Navigate to the repository and launch the Multilauncher executable at ~/path/to/directory/Multilauncher/dist/


<a name="Important Notes Before Running"/>

**Important Notes Before Running**
----------------------------------

- Make sure all computers are on the same network.

- Check that port 11311 is allowed through the firewall on ROSMASTER machines (if not type: sudo ufw allow 11311).


<a name="Running the Application"/>

**Running the Application**
---------------------------

- Once the the Multilauncher is running, the Main Window will be displayed.

- Some of Multilauncher's functions will be deactivated until valid data is present in the Robot Table and
	when the listed computers/robots have all been successfully found/pinged as denoted in the Connection Status column.


**File Browser/RoboData** <a name="File Browser/RoboData"/>


**Adding Robots from a .csv File:** <a name="Adding Robots from a csv File"/>

- From the Main Window, click on the Find Robotlist file button and a FileDialog window will be displayed.
    Navigate to your (.csv) file is located and click Open.
	

**Saving the Current List of Robots to a .csv File:** <a name="Saving the Current List of Robots to a csv File"/>

- From the Main Window, click on the Save Current Data to File button and a FileDialog window will be displayed.
    Navigate to where you want your .csv to be saved, give the file a name, and click Save.


**Enabling and Disabling Listed Robots:** <a name="Enabling and Disabling Listed Robots"/>

- From the Main Window clicking on a checkbox listed in the robot table's Enabled column will alternate the checked status of a individual 
    robot between Enabled (checked) and Disabled (unchecked).

- Clicking on the Enable/Disable All button will alternate all Enabled checkboxes listed in 
    the robot table between Enabled (checked) and Disabled (unchecked).


**Adding/Removing Robots Manually:** <a name="Adding/Removing Robots Manually"/>

- From the Main Window, click on the Add/Edit/Remove Robots button to bring up the EditRobot dialog window.

- Add a new robot: Type the robot's IP address into the first textfield under the New/Selected: IP Address label,
                  the robot's user/host name in the middle textfield under the New/Selected: Robot Name label, 
                  the robot's type/model in the last textfield under the New/Selected: Robot Type label, and
			      finally click on the Add Robot button to add the new robot to the robot table.
                  A message will appear next to the result label informing you if the operation was successful or how it might have failed.

- Modify a robot: Click on any of the intended robot's table entries to load the selected robot's data into the three 
    New/Selected textfields under the table. Overwrite the current values in the textfields and click on the 
    Modify Robot button to update the entry in the robot table.


- Remove a robot: Click on any of the intended robot's table entries and then click the Delete Robot button.
	
	Warning!: If you have multiple robots listed in the robot table and have selected one, clicking the Delete Robot button multiple times
				will delete the currently selected robot, then each of the robots above the original deletion, and finally the ones under the original deletion.
				
    Example: Robots listed in the order of: 1, 2, 3, 4, 5.  
              If 3 is selected first and the Delete Robot button is clicked multiple times it will 
              delete in this order: 3, 2, 1, 4, 5. 

- Save the current list of robots in the robot table to the Main Window by clicking the Save and Exit button.


**Updating the SSH MaxSessions Variable:** <a name="Updating the SSH MaxSessions Variable"/>

- The default number of simultaneous ssh connections is 10, if the combined number of enabled robots and Masters exceed
    this amount (or the amount set by the MaxSessions variable) you will need to update the MaxSessions variable in the /etc/ssh/sshd_config file.

- From the Main Window, clicking on the Update MaxSessions button will bring up a information dialog box that
    prompts the user for root credentials through PolicyKit to perform the needed file operation on the /etc/ssh/sshd_config file.


**Adjusting Robot Arguments:** <a name="Adjusting Robot Arguments"/>

- From the Main Window and after successfully pinging the listed robots, click on the Adjust Arguments button to open
    the Adjust Arguments dialog window.

- Arguments are grouped together based on robot type.

- The top part of the Argument Window lists the different types of robots and contains a spinbox that controls how many 
    arguments are required for each robot type.
    
- The bottom part of the Argument Window displays the listed robots grouped together as a series of trees each containing
    a single type, the robots that are of that type, and the required number of arguments for each robot of that type.

- Red lines in the Argument Column indicate missing arguments for that robot and green lines indicate acknowledged 
    arguments.  It is up to the user to make sure the arguments themselves are correct.
    
- Save the current list of robot arguments in the argument tree to the Main Window by clicking the Save button.


**Pinging the Listed Robots:** <a name="Pinging the Listed Robots"/>

- From the Main Window, click on the Ping Robots button to begin pinging the robots listed in the robot table.  
    
- Each tab displays the current status of pinging each listed robot's IP address from the robot table.  
    
- If the IP address has been found a found message will be displayed in the associated tab while IP addresses 
    that have not been found will continue to ping up to a set number of times (default is 30 attempts).

- Pinging threads can be interrupted/closed individually or all at the same time by clicking the 
    Stop Current Thread and Stop all unfinished threads buttons respectively.  
    
- Once all IP addresses have been found, reached the ping limit, or been interrupted
    by the user, an information dialog box will display an acknowledgement that the ping operation is finished.
    
- If all IP addresses have been successfully found the application will unlock the remaining buttons and features
    in the Main Window.

    Warning!: Closing the Launch Window before all threads have finished terminates the running threads.


**Update ROSMASTER URI IP in the ~/.bashrc on the Remote Robots:** <a name="Update ROSMASTER URI IP in the bashrc on the Remote Robots"/>

- From the Main Window and after successfully pinging the listed robots, click the Update .bashrc button.  
    This will either bring up the Password Window for processing passwords for each robot or if the Use RSA Key checkbox 
    is currently checked the application will skip the Password Window and go straight into starting the Launch Window.  
    
- Please refer to the section [Passwords and Using RSA Keys](#Passwords and Using RSA Keys) for more detailed information on the Password
    Window and RSA checkbox.

    Warning!: Closing the Launch Window before all threads have finished terminates the running threads.


**Local File/Git Repository** <a name="Local File/Git Repository"/>


**Transferring Local Files:** <a name="Transferring Local Files"/>

- To transfer local files to remote machines please follow this sequence of steps.

1. From the Main Window and after successfully pinging the listed robots, select the number of files that need to be transferred
    to the remote machines with the Select Number of Repositories spinbox.  (If you need 2 files for turtlebots and 
    3 for quadcopters you would set the spinbox to 5).

2. Either press the Parent Package Directory button to bring up the Specify the Package Directory window where you 
    can select your destination for the file or manually type the destination directory into the corresponding 
    text field under the Destination column.

3. Manually type the local file's location into the corresponding text field under the Local/Repository column.

4. Select the type of robot this file transfer operation should be performed on in the corresponding spinbox under the Robot Type column.


    Adjusting the value in the Catkin Option column does not affect transferring files only pulling repositories.
    
5. When all the files are ready to be transferred to the remote robots, click the Transfer Local Files(s) to Remote Machines button.
    This will bring up the Transfer Local File Confirm window which displays an overview of what files will go where and on which type of
    remote machines.
    
6. If the listed file transfers are correct, pressing the Confirm and Transfer button will either bring up the 
    Password Window for processing passwords for each robot or if the Use RSA Key checkbox is currently checked the
    application will skip the Password Window and go straight into starting the Launch Window.
    
- Please refer to the section [Passwords and Using RSA Keys](#Passwords and Using RSA Keys) for more detailed 
    information on the Password Window and RSA checkbox.

    Warning!: Closing the Launch Window before all threads have finished terminates the running threads.


**Pulling Repositories:** <a name="Pulling Repositories"/>

- To pull repositories please follow this sequence of steps.

1. From the Main Window and after successfully pinging the listed robots, select the number of repositories that need to be pulled
    from remote repositories with the Select Number of Repositories spinbox.  (If you need 2 packages for turtlebots and 
    3 for quadcopters you would set the spinbox to 5)

2. Either press the Parent Package Directory button to bring up the Specify the Package Directory window where you 
    can select your destination for the remote repository or manually type the destination directory into the 
    corresponding text field under the Destination column.

3. Manually type the remote repository URL into the corresponding text field under the Local File/Repository column.

4. Select the type of robot this git pull operation should be performed on in the corresponding spinbox under the Robot Type column.

5. Select the Catkin operation that should be performed on this directory  in the corresponding spinbox under the Catkin Option column.
    The No make option is considered the default option and does not perform a catkin_make or catkin build operation.
        
6. When all the packages are ready to be transferred to the remote robots, click the Transfer Files button.
    This will either bring up the Password Window for processing passwords for each robot or if the
    Use RSA Key checkbox is currently checked the application will skip the Password Window and go straight into starting the
    Launch Window.  
    
- Please refer to the section [Passwords and Using RSA Keys](#Passwords and Using RSA Keys) for more detailed 
    information on the Password Window and RSA checkbox.

    Warning!: Closing the Launch Window before all threads have finished terminates the running threads.


**Command Editor** <a name="Command Editor"/>

**Preparing Commands for Robots:** <a name="Preparing Commands for Robots"/>

- From the Main Window and after successfully pinging the listed robots, the tabbed section of the Command Editor will display
    one tab per listed robot type from the Robot's Type/Configuration column.
    
- Within each tab is a textfield that can be edited manually or loaded from a .txt file and is used to send a series of
    commands to the remote robots.

- Some commandline style commands are valid for use through the Command Editor.


**Adding Commands from a .txt File:** <a name="Adding Commands from a txt File"/>

- From the Main Window, click on the Load Commands File button and the Find your command file window will be displayed.
    Navigate to your commands.txt file is located and click Open.

    Note about loading commands from a file: The application will only load the commands for machine types present in
    the .txt file.
	

**Saving the Current List of Commands to a .txt File:** <a name="Saving the Current List of Commands to a txt File"/>

- From the Main Window, click on the Save Current Data to File button and the Choose a Name for Your File window will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click Save.

    Note about saving commands to a file: The application will save all commands present in all tabs to the .txt file.


**Passwords and Using RSA Keys** <a name="Passwords and Using RSA Keys"/>

**Password Window:** <a name="Password Window"/>

- When the Password Window is displayed, the center will list all of the remote machines with a corresponding textfield
    for password entry.

- To continue all password fields must be filled (Passwords are not checked for correctness in this window).

- Clicking the Submit and Continue button will submit the remote machine and password pairs back to the program for processing.


**Generating RSA Keys:** <a name="Generating RSA Keys"/>

- To search for a existing RSA Key on the your local machine click the Find RSA Key button to bring up the Find Your RSA Key window.
    Navigate to where the existing RSA Key is then select and open the file to load its location into the Multilauncher.
    The location of the RSA Key in use is denoted by the Current RSA Key Path: label.

- To generate a new set of RSA keys click on the Generate Key button from the Main Window. This will bring up the 
    Password Window. After submitting the passwords for all the listed machines, the Generate RSA Key Window will be displayed.
    Clicking on the Generate Key button will begin the process for creating a new private/public RSA Key pair and
    then pushing the public key to the remote machines.

- The Use RSA Key checkbox is used when a RSA key has been successfully pushed to all the enabled remote machines
    and allows the user to skip the password step for various functions.


**Launching** <a name="Launching"/>

- To launch only a single type/configuration of the listed robots click the Launch Current Type button. This will 
    either bring up the Password Window for processing passwords for each robot or if the Use RSA Key checkbox
    is currently checked the application will skip the Password Window and will launch all robots that share the 
    type/configuration of the currently active tab in the Command Editor.
    
- To launch the ROSMASTER threads listed in the ROSMASTER Settings, click the Launch Masters button. This will either bring up the 
    Password Window for processing passwords for each robot or if the Use RSA Key checkbox
    is currently checked the application will skip the Password Window and go straight into starting the ROSCORE Window.  

- To launch all enabled robots of all types click the Launch All button. 
    This will either bring up the Password Window for processing passwords for each robot or if the Use RSA Key checkbox
    is currently checked the application will skip the Password Window and go straight into starting the Launch Window.  
    
- Please refer to the section [Passwords and Using RSA Keys](#Passwords and Using RSA Keys) for more detailed 
    information on the Password Window and RSA checkbox.

<a name="Built With"/>

**Built With**
--------------

- Python 2.7

- Paramiko 2.4.1

- PyQt 5.5.1

- QtDesigner


<a name="Authors"/>

**Authors**
-----------

- Matthew Hovatter: Co-Author

- Paul Buzaud: Co-Author


<a name="Acknowledgements"/>

**Acknowledgements**
--------------------

- Paramiko