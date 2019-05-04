# midiRebind
Get/send midi commands to a GrandMA but can be configured to bind any custom SysEx message
To do so add a custom patch (or use a currently defined one, but chances are patches made for one SysEx won't work on another) and add a parser in the mapping directory

# Depends
* Mostly mido (pip install mido) for the midi binding and blessings for the testing (pip install blessings)
* test.py depends on the submodule minitest witch also depends on blessings but is not necessary

# Config Syntax

* [interface] : All important information concerning the midi interface
  * input : Choose which Midi interface to listen to
  * output1 : Choose which Midi interface to output to; an arbitrary number can be specified that way
  * inputchanel : Which midi channel to listen to
  * outputchannel1 : Which midi channel to output to
  * mapping : The python file in mapping to setup all the mapping between input and output
* [set/1] patch the first layer of set commands, what is defined as the first layer is in the mapping file
  * Basic usage : incomming note = interface/commandtype/note/intensity
  * Exemples:
    * 5-50 = 1/cc/11 #Map the faders 5-50 to the control change 11-45 (Straight patch) on output 1
    * 57-67 = 1/cc/12-32 # Will map linearly 57 to 12; 58 to 14 etc on output 1
    * 56 = 2/note/152 #Map fader 56 to note 152 on output 2
  * Advanced usage: Can add logic to the notes. NB: they must be defined first
    * 56/cond = lambda x: x==50 # Function choosing conditions on the value to send
    * 57/toggle = 0/127: Toggle the val between 127 and 0 every time the note is received

# Adding another mapping interface
* Good luck
