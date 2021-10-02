from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
from mapping.midi import MessageParse
from mapping.midi import Actions


_COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}

#################################################
# GLOBAL CONTROL
###

#import midiPageHandler
#create a var thingy

def _onload(self):
    "Send a reset colors"
    import time,sys
    #vars.output=self.outputs[vars.interface_nb]

def pagepress(trigger,val,note,*params):
    "A key was pressed on the pagebuttons area"
    #i,j=noteToPos(note)
    try:
        pass
        #_ACTIONS[vars.page][i+8*j](trigger,i,j,val,*params)
        # dprint("[Info] : Action received ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))
    except TypeError as e:
        eprint("[Error] : Unassigned pagebutton ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))
        eprint(e)

####################################################
#  INTERFACE DEFINITION
#####

class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["pagepress"]=pagepress
