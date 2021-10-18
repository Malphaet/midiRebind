#!/bin/python3
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
from mapping.midi import MessageParse
from mapping.midi import Actions
import sys

from mapping.utils import doublepress
from pythonAnalogWay import bindings
###########################
# FUNCTION DEFINES

_VERBOSE=4

nopeF=lambda *x:None
def printl(label=""):
    def _pl(*args):
        print(label,*args)
    return _pl

eprint=printl("[mPH:ERROR]")
dprint,ddprint,iprint,wprint=nopeF,nopeF,nopeF,nopeF
bindings.dprint,bindings.ddprint,bindings.iprint=nopeF,nopeF,nopeF

if _VERBOSE>=1:
    wprint=printl("[mPH:WARNING]")
if _VERBOSE>=2:
    iprint=printl("[mPH:INFO]")
if _VERBOSE>=3:
    dprint=printl("[mPH:DEBUG]")
if _VERBOSE>=4:
    ddprint=printl("[mPH:DDEBUG]")


_COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}

#################################################
# GLOBAL CONTROL
###

# try:
from mapping import midiPageHandler
# except:
#     from
handler=midiPageHandler.AkaiAPCMini()
class pulseLink(object):
    """Link between lights, messages and states
    Receives messages from the pulse and adjust states"""
    def __init__(self):
        pass

    def message(self):
        pass

def _onload(self):
    "Send a reset colors"
    import time,sys
    try:
        HOSTS=[["127.0.0.1",3000]] # Test server
        #HOSTS=[["192.168.0.140",10500]] # Test server
        
        # The socket remote controller
        controllerPulse1=bindings.analogController(*HOSTS[0])

        # Adding the midi interface to the controller
        handler.addInterfaceOut(self.interfaceOut(1))

        # The pulse module, bound to 3 lines
        modulePulse=handler.addModule(midiPageHandler.pulseRackController,[4,1,2])

        # The IO interface between the pulse and the controller, one IO is necessary per auxilliary application
        IOInterface=midiPageHandler.IOInterfacePulse(handler,modulePulse,controllerPulse1)
        
        # Finishing initialising the controller (Should be done in a thread to avoid locking)
        controllerPulse1.addFeedbackInterface(IOInterface)
        controllerPulse1.connectionSequence()
        #controllerPulse.keepPinging()
    except ConnectionRefusedError:
        eprint("The connection to the pulse failed, check your settings and try again ({})".format(HOSTS))

    
def pagepress(trigger,val,note,*params):
    "A key was pressed on the pagebuttons area"
    try:
        # print(handler._noteToPos[note])
        handler.noteReceived(note,val)
    except TypeError as e:
        eprint("[Error] : Unassigned pagebutton {} - Note {:2} ({:3})".format(trigger,note,val))
        eprint(e)
    except SystemExit as e:
        eprint("The Pulse requested a SystemExit (likely due to a connection interrupted), please check your settings")

@doublepress
def quitpress(trigger,val,note,*params):
    # handler.
    print("Quitting...")
    sys.exit()

####################################################
#  INTERFACE DEFINITION
#####

class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["pagepress"]=pagepress
        self.functionlist["quitpress"]=quitpress
