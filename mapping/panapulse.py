from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
from mapping.midi import MessageParse
from mapping.midi import Actions
import sys

from mapping.utils import doublepress
###########################
# FUNCTION DEFINES

_VERBOSE=4

nopeF=lambda x:None
def printl(label=""):
    def _pl(*args):
        print(label,*args)
    return _pl

eprint=printl("[mPH:ERROR]")
dprint=nopeF
ddprint=nopeF
iprint=nopeF
wprint=nopeF
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

from mapping import midiPageHandler

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
    handler.addInterfaceOut(self.interfaceOut(1))
    IOInterface=midiPageHandler.IOInterface(handler)

    #vars.output=self.outputs[vars.interface_nb]

def pagepress(trigger,val,note,*params):
    "A key was pressed on the pagebuttons area"
    try:
        # print(handler._noteToPos[note])
        handler.noteReceived(note,val)
    except TypeError as e:
        eprint("[Error] : Unassigned pagebutton {} - Note {:2} ({:3})".format(trigger,note,val))
        eprint(e)

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
