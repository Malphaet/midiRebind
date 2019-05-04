# gmaPy
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

[set/1] #Patches layer 1 patch:2 would patch layer 2 and so on
1 = 1/cc/10 #Send (midi) control change (10) with value mapped to the fader (1) value (fader 1 => cc 10) on output 1
5-50 = 1/cc/11 #Map the faders 5-50 to the control change 11-45 (Straight patch) on output 1
57-67 = 1/cc/12-32 # Will map linearly 57 to 12; 58 to 14 etc on output 1
56 = 2/note/152 #Map fader 56 to note 152 on output 2
56/cond = lambda x: x==50 # Function choosing conditions on the value to send
[fire] #No layer specified
13 = 1/note/10
15 = 1/cc/44/127 #Send control change with value 127
17-27 = cc/45/127 # Send control change 45-55 with value 127
38 = 1/cc/65/124;2/cc/79/100;note/25 (Stack the action to link to)

# Adding another mapping interface
*
