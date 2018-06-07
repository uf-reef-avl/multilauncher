**MULTILAUNCHER**
-----------------

A utility that facilitates connecting to multiple remote computers/robots,
downloading remote repositories to those remote computers, and
executing a series of commands simultaneously on the computers.


**Installation**
----------------





**Important notes before running**
----------------------------------

-Make sure all computers are on the same network.

-Check that port 11311 is allowed through the firewall on the rosmaster machine (if not type: sudo ufw allow 11311).

-If you intend to work with more than 10 computers go to the directory at "/etc/ssh/sshd_config" and
	find/add the "MaxSessions" variable and set it equal to or greater than the number of computers to be used.
	A warning will popup if you add more than the "MaxSessions" number of computers to the list of robots.


**Running the Application**
--------------------------

-Once the the Multilauncher is running, the MainWindow will be displayed.

-A majority of the Multilauncher's functions will be deactivated until valid data is present in the textfields and
	when the listed computers/robots have all been successfully pinged as denoted in the Connection Status textfield.


**Adding/Removing Robots Manually:**

-From the MainWindow, click on the "Add/Edit/Remove Robots" button to bring up the EditRobot dialog-box.

**-Add a new robot:** Type the robot's IP address into the first textfield to the right of the "Selected" label,
                  the robot's user/host name in the middle textfield, the robot's type/model in the last textfield, and
			      finally click on the "Add Robot" button to add the new robot to the robot table.
                  A message will appear next to the "result" label informing you if the operation was successful or how it might have failed.
	
**-Remove a robot:** Click on any of the intended robot's table entries and then click the "Delete Robot" button.
				 To help identify the robot to be deleted its data will be loaded into the three textfields under the table.
	
   **-!Warning!** If you have multiple robots listed in the robot table and have selected one, clicking the "Delete Robot" button multiple times
				will delete the currently selected robot, then the robots above the original deletion, and finally the ones under the original deletion.
				
   **-Example:** Robots listed in the order of: 1, 2, 3, 4, 5.  
              If 3 is selected first and the "Delete Robot" button is clicked multiple times it will 
              delete in this order: 3, 2, 1, 4, 5. 

**-Save the current list of robots in the robot table to the MainWindow:** Click the "Save and Exit" button.


**Adding Robots via a .csv File:**

-From the MainWindow, click on the "Find Robotlist file" button and a FileDialog box will be displayed.
    Navigate to your robotlist.csv file is located and click "Open".
	

**Saving the Current List of Robots to a .csv File:**

-From the MainWindow, click on the "Save Current Data to File" button and a FileDialog box will be displayed.
    Navigate to where you want your .csv to reside, give the file a name, and click "Save".


**Pinging the Listed Robots:**

-From the MainWindow, click on the "Ping Robots" button to begin pinging the robots listed under "Robot's IP Address".  
    This will bring up the LaunchWindow containing a tab for every IP address listed,
    a deactivated Debug commandline, and a "Stop all unfinished threads" button.  
    
-Each tab displays the current status of pinging each listed IP address.  
    
-If the IP address has been found a found message will be displayed in the associated tab while IP addresses 
    that have not been found will continue to ping up to a set number of times (default is 100 times).
    
-All pinging threads can be interrupted and closed by clicking the "Stop all unfinished threads" button.  
    
-Once all IP addresses have been found, reached the ping limit, or been interrupted
    by the user a information dialog box will display an acknowledgement that the ping operation is finished.
    
-If all IP addresses have been successfully found the application will "unlock" the remaining buttons and textfields
    in the MainWindow
        
**-!Warning!** Closing the LaunchWindow before all threads have finished does not terminate the threads and prevents you 
             from editing the listed robots or performing any other thread based function.
             Warnings will be displayed if attempting one of these functions.


**Adjusting Robot Arguments:**

-From the MainWindow and after successfully pinging






**Developer tips**
------------------




