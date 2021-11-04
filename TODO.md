# Big list of big stuff to do
* Move all projects/subprojects to src/
* Make all tests
* Clean up the code and the TODO
* Make the code more readable
* Create a keystrokes.py with all the keystrokes loaded from a config file

# Adding another mapping interface
* TODO: Explain it better than just "look at the ones I made"

# Improvements
* Better note / cc / pc notation
* Add Fade (in ms) from one value to another
* Have a way to know last value for the note/cc (the last one sent/received)
* Make toggles a function modifying a variable/state and sending result
* Allow for a multi-in interfaces
* TODO: More testing for null interface out
* URGENT : /funct with an existing trigger might not work, should be with an empty trigger anyway.
* Add asynchronous mode ?
* URGENT : Crash when assigning to an existing trigger
* TODO: Async and Disconnection protect for VPs
* TODO: Disconnect: 'NoneType' object has no attribute 'groups' : Should handle disconnect & Crashes
* TODO: Color and un-color VP as it connects
* TODO: Unified verbose printing & usage

* TODO: Pagehandler: make a note handler
* TODO: Color management, get colors associated to all statuses
* TODO: General decorators @armtake

* URGENT : Fix the connection issue
* TODO: More explicit midi output/input connection error (and backup or exit)
* TODO: CLEAN CONNECTION TO A RACK, ANYTHING BUT THIS CLUSTERF*CK
* TODO: Connect the IOHandler with handler, binding and vice-versa, check some.
* TODO : Clean this step : Do a better IO handler
* URGENT : Error on non-existing patch is incorrect (win)
* URGENT : line 341, in POSTMATCH_SCRNUPD /  if match.group("postargs")[-1]=="1" trigger out of range on incorrect formatted return args (no args)
* TODO: Get rid of match.group("postargs").split
* TODO: Asyncio lib to clean up the whole pyAnalogWay (which was neat but cumbersome)
* TODO: Use logging instead of this clusterfk
* TODO: Sysexit not working
* URGENT: Network interruption not working
* TODO: Empty triggers should give a little more info
* TODO: Clean up the whole IO handler

