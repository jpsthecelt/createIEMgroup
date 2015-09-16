# createIEMgroup
An example I developed for a particular Airline, using either python or powershell to create groups in BF from names in a text file

An example of how it is used (see docs subdirectory for .gif of resulting console <note that it shows a different
number of member computers, b/c it was taken before member computers 'reported back in'; also, sorry for the
misspelling of the group name>):

$ createIEMcomputerGroup.py MyBlahGrojp computer_group_members.txt -u adminMO -p adminmo

The response XML about the action that I invoked comes back and tells me that the computer group name/ID is
MyBlahGrojp with ID# 5965 (XML is not displaying in G/H properly)

The python version uses the excellent requests library (note that as of this date, running the script will 'complain' 
that 'an unverified HTTP request is being made'.  This can be quiesced by modifying the code, but it's better if you
change the code to use an actual SSL token if you do something like this in a production environment).

Note that there are two versions, here, one in python (in which I originally developed, to 'prove the concept', and
powershell, which is what the customer asked for).

[So, see the part of my blog called 'Lesson 5' at: https://www.ibm.com/developerworks/community/blogs/edgeCity/?lang=en
for some of the thinking behind 'why I did it this way']

-jps
