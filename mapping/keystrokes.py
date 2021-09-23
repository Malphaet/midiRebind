#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
import pyautogui

from mapping.midi import MessageParse
from mapping.midi import Actions

INPUTS=  [0,0,1,0,0,0,1,0]
MEMORIES=[1,1,1,0,0,0,0,0]


_ACTIVE=0b1
_SELECTED=0b10
_LIVE=0b100

class demvars():
    def __init__(self):
        self.interface_nb=1
        self.output=None
        self.BASE_NOTE_INPUT=56
        self.BASE_NOTE_MASTERM=48

        self.live_input=None
        self.selected_input=0
        #
        # self.active_memory=None
        # self.selected_memory=None

        self.INPUTS=[i*_ACTIVE for i in INPUTS]
        self.MEMORIES=[i*_ACTIVE for i in MEMORIES]

        self.COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}
        self.COLORPLUGS={0:self.COLORS["yellow"],1:self.COLORS["green"],2:self.COLORS["blinking_green"],3:self.COLORS["red"]}
        self.PLUGCOLORS={
            0:                          self.COLORS["yellow"],
            _ACTIVE:                    self.COLORS["green"],
            _SELECTED:                  self.COLORS["blinking_yellow"],
            _LIVE:                      self.COLORS["red"],
            _ACTIVE|_SELECTED:          self.COLORS["blinking_green"],
            _ACTIVE|_LIVE:              self.COLORS["red"],
            _SELECTED|_LIVE:            self.COLORS["blinking_red"],
            _ACTIVE|_SELECTED+_LIVE:    self.COLORS["blinking_red"]
        }

    def findit(self,col,row):
        "All index start at zero"
        return self.BASE_NOTE_INPUT+col-8*row

    def lightcolor(self,col,row,color):
        self.light(col,row,val=self.COLORS[color])

    def light(self,col,row,val=1):
        self.lightnote(self.findit(col,row),val)

    def lightnote(self,note,val=1):
        self.output.send(mido.Message("note_on",note=note,velocity=val))

    def updateinput(self,toupdate=range(8)):
        "Update the inputline"
        for i in toupdate:
            self.light(i,0,self.PLUGCOLORS[self.INPUTS[i]])

    def updatemasterm(self):
        "Update the selected master memory"

VARS=demvars()

def _onload(self):
    "Send a reset colors"
    import time,sys
    VARS.output=self.outputs[VARS.interface_nb]
    for i in range(64):
        VARS.lightnote(i,0)

    VARS.updateinput()
    VARS.updatemasterm()

    # sys.exit()


def switchinput(trigger,val,note,*params): #HARDCODED COLORS ARE BAD
    "Switch to the desired layer i1"
    i=note-VARS.BASE_NOTE_INPUT
    toup=[VARS.selected_input,i]

    VARS.INPUTS[VARS.selected_input]=INPUTS[VARS.selected_input]
    VARS.selected_input=i
    VARS.INPUTS[VARS.selected_input]|=_SELECTED
    if VARS.live_input:
        VARS.INPUTS[VARS.live_input]|=_LIVE

    VARS.updateinput(toup)

    #pyautogui.hotkey("i",str(topress))

def takeall(trigger,val,note,*params):
    "Take all TA"
    if VARS.live_input!=None:
        VARS.INPUTS[VARS.live_input]=INPUTS[VARS.live_input]
        toup=[VARS.live_input,VARS.selected_input]
    else:
        toup=[VARS.selected_input]

    VARS.live_input=VARS.selected_input
    VARS.INPUTS[VARS.selected_input]|=_SELECTED
    VARS.INPUTS[VARS.live_input]|=_LIVE
    VARS.updateinput(toup)

    #pyautogui.hotkey("t","a")

def mastermemory(trigger,val,note,*params):
    "Switch to the desired master memory M1"
    topress=note-BASE_NOTE_MASTERM+1


    #pyautogui.hotkey("m",str(topress))

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["switchinput"]=switchinput
        self.functionlist["mastermemory"]=mastermemory
        self.functionlist["takeall"]=takeall
