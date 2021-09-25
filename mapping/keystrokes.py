#!/bin/python3

#################################################
# HARDCODED DEFINITIONS
###
INPUTS=  [0,0,1,0,0,0,1,0]
MEMORIES=[1,1,1,1,1,0,1,1]
__TESTING=True

#################################################
# IMPORTS
###

from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
from panaremote import request as panarequest
from mapping.midi import MessageParse
from mapping.midi import Actions

from threading import Timer

#################################################
# GLOBAL UTILITIES
###

class pyautonope(object):
    def __init__(self):
        pass

    def __call__(self,*args,**kwargs):
        return self

    def __repr__(self,*args,**kwargs):
        return ''

    def __getattribute__(self,*args,**kwargs):
        return self
if __TESTING:
    pyautogui=pyautonope()
    def dprint(*args):
        print(*args)
else:
    import pyautogui
    def dprint(*args):
        pass


#################################################
# BASE VARIABLE DEFINITIONS
###

_NOTIMER=pyautonope()

_ACTIVE=0b1
_SELECTED=0b10
_LIVE=0b100

#Modes
_RESET=lambda a,b: a
_OR=lambda a,b: a|b
_XOR=lambda a,b: a^b

_TIMERTAKE=3.0
_BASE_NOTE_INPUT=56

_BASEVALUES=[
    INPUTS[:],
    MEMORIES[:],
    [[0]*8]*6
] # The duplicate is actually unimportant

_COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}

#################################################
# UTILITIES
###

def noteToPos(note):
    i,j=note%8,7-note//8
    vars.lastpress=(i,j)
    return i,j

#################################################
# GLOBAL VARIABLE OBJECT
###
class demvars():
    def __init__(self):
        self.page=0

        self.interface_nb=1
        self.output=None
        self.BASE_NOTE_MASTERM=48   # Marked for deletion
        self.BASE_NOTE_ARM_TAKE=89  # Marked for deletion

        self.listchange=[]
        self.lastpress=(None,None) #Does only account for the 8x8
        self.selected_pulse=(None,None)
        self.live_pulse=(None,None)
        self.list_vp=[]
        self.list_shutter_open=[]

        self.timertake=_NOTIMER
        self.INPUTS=[i*_ACTIVE for i in INPUTS]
        self.MEMORIES=[i*_ACTIVE for i in MEMORIES]
        self.PAGE_COLORS=[
            [
                self.INPUTS,
                self.MEMORIES,
                [[0]*8 for i in range(6)]
            ]
        ]

        self.VALUES=self.PAGE_COLORS[0] # Marked for deletion

        self.takearmed=False

        #self.COLORPLUGS={0:_COLORS["yellow"],1:_COLORS["green"],2:_COLORS["blinking_green"],3:_COLORS["red"]}
        self.PLUGCOLORS={
            0:                          _COLORS["yellow"],
            _ACTIVE:                    _COLORS["green"],
            _SELECTED:                  _COLORS["blinking_yellow"],
            _LIVE:                      _COLORS["red"],
            _ACTIVE|_SELECTED:          _COLORS["blinking_green"],
            _ACTIVE|_LIVE:              _COLORS["red"],
            _SELECTED|_LIVE:            _COLORS["blinking_red"],
            _ACTIVE|_SELECTED+_LIVE:    _COLORS["blinking_red"]
        }

    # Should do it in a similar way, cant find it
    def addChange(self,i,j,value,reset=True): #mode=_OR
        "Do a value change, store the change for update"
        if i==None or j==None:
            return
        self.listchange+=[[i,j,value,reset]]

    def applyChanges(self):
        "Apply all changes"
        allch=set()
        for i,j,v,r in self.listchange:
            allch.add((i,j))
            if r:
                self.VALUES[j][i]=_BASEVALUES[j][i]|v
                #print("({}:{}) - Action:{} Base:{} Effect:{} Color:{}".format(i,j,v,_BASEVALUES[j][i],_BASEVALUES[j][i]|v,self.PLUGCOLORS[_BASEVALUES[j][i]|v]))
            else:
                self.VALUES[j][i]|=v
        self.listchange=[]

        for i,j in allch: # I feel like I'm doing this twice
            self.light(i,j,self.PLUGCOLORS[self.VALUES[j][i]])

        # self.
    def findit(self,col,row):
        "All index start at zero"
        return _BASE_NOTE_INPUT+col-8*row

    def lightcolor(self,col,row,color):
        self.light(col,row,val=_COLORS[color])

    def light(self,col,row,val=1):
        self.lightnote(self.findit(col,row),val)

    def lightnote(self,note,val=1):
        self.output.send(mido.Message("note_on",note=note,velocity=val))

    def updateRange(self,listNotes):
        "Update a list of notes"
        for i,j in listN:
            pass

    def updateinput(self,toupdate=range(8)): # Marked for deletion
        "Update the inputline"
        for i in toupdate:
            self.light(i,0,self.PLUGCOLORS[self.INPUTS[i]])

    def updatemasterm(self,toupdate=range(8)): # Marked for deletion
        "Update the selected master memory"
        for i in toupdate:
            self.light(i,1,self.PLUGCOLORS[self.MEMORIES[i]])

#################################################
# ON LOAD ACTIONS
###
vars=demvars()

def _onload(self):
    "Send a reset colors"
    import time,sys
    vars.output=self.outputs[vars.interface_nb]
    #Load the remote control on some VPs
    # loadVPs(["192.168.0.8"])

    # Cleaning the arm
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,2)

    vars.updateinput()
    vars.updatemasterm()

#################################################
# GLOBAL CONTROL
###

def controllpress(trigger,val,note,*params):
    pass

def pagepress(trigger,val,note,*params):
    "Analise a press on the pagebuttons"
    i,j=noteToPos(note)
    try:
        _ACTIONS[0][i+8*j](trigger,i,j,val,*params)
    except TypeError as e:
        dprint("[Error] : Unassigned action ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))

#################################################
# PULSE CONTROL
###

def switchinput(trigger,i,j,val,*params): ## Marked for deletion
    "Switch to the desired layer i1"

    # These two lines could be better done
    vars.lastpress=(i,j)

    vars.addChange(*vars.selected_pulse,0,reset=True) # Reset this to base
    vars.selected_pulse=(i,0)

    vars.addChange(*vars.lastpress,_SELECTED,reset=True) # Add a selection
    vars.addChange(*vars.live_pulse,_LIVE,reset=False)

    vars.applyChanges()
    pyautogui.hotkey("i",str(i+1))

def takeall(trigger,val,note,*params):
    "Take all TA"

    if not vars.takearmed:
        return
    # unarmtake()
    vars.addChange(*vars.live_pulse,0)
    vars.live_pulse=vars.selected_pulse
    vars.addChange(*vars.selected_pulse,_SELECTED|_LIVE)
    vars.applyChanges()

    pyautogui.hotkey("t","a")

def switchmastermemory(trigger,i,j,val,*params): # Marked for deletion
    "Switch to the desired master memory M1"
    vars.lastpress=(i,j)

    vars.addChange(*vars.selected_pulse,0,reset=True) # Reset this to base
    vars.selected_pulse=(i,1)
    vars.addChange(*vars.lastpress,_SELECTED,reset=True) # Add a selection
    vars.addChange(*vars.live_pulse,_LIVE,reset=False)

    vars.applyChanges()
    pyautogui.hotkey("m",str(i+1))


def unarmtake():
    "Unarm the take button"
    # vars.timertake.cancel()
    vars.takearmed=False
    vars.timertake=_NOTIMER
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,2)

def armtake(trigger,val,note,*params):
    "Arm the take button, unarm after a short while"
    vars.timertake.cancel()
    vars.timertake=Timer(_TIMERTAKE, unarmtake)
    vars.takearmed=True
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,1) # First and only blinking value
    vars.timertake.start()



#################################################
# VIDEOPROJECTOR CONTROL
###

def loadVPs(listVP):
    "Load the VP list"
    try:
        vars.list_vp=[openVP()]
        vars.list_shutter_open=[i.st_shutter=='On' for i in vars.list_vp]
        print(vars.list_shutter_open)
    except Exception as e:
        print("[panaRemote] An unexpected error occured while operating the videoprojector")
        print(e)


def openVP(adress):
    return panarequest.VP('192.168.0.8')

def panaShut():
    pass

def panaOpen():
    pass

def panaToggle():
    pass

def vpcontroll(trigger,val,note,*params):
    "Receive a vp vpcontroll trigger"


#################################################
# ACTION ASSIGNEMENT
#####

_ACTIONS=[
    [None]*64
]

for i in range(7):
    _ACTIONS[0][i]=switchinput
    _ACTIONS[0][i+8]=switchmastermemory


####################################################
#  INTERFACE DEFINITION
#####

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["pagepress"]=pagepress
        self.functionlist["controllpress"]=controllpress

        self.functionlist["switchinput"]=switchinput
        self.functionlist["mastermemory"]=switchmastermemory
        self.functionlist["takeall"]=takeall
        self.functionlist["armtake"]=armtake
        self.functionlist['vpcontroll']=vpcontroll
