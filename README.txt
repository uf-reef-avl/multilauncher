A utiltiy that facilitates connecting to multiple remote computers/robots,
downloading remote repositories to those remote computeres, and
executing a series of commands simultaneously on the computers.


Installation
------------





Important notes before running
------------------------------

-Make sure all computers are on the same network.

-Check that port 11311 is allowed through the firewall on the rosmaster machine (if not type: sudo ufw allow 11311).

-If you intend to work with more than 10 computers go to the directory at "/etc/ssh/sshd_config" and
	find/add the MaxSessions variable and set it equal to or greater than the number of computers to be used.
	A warning will popup if you add more than the MaxSessions number of computers to the list of robots.


Running the Application
-----------------------






Developer tips
--------------




