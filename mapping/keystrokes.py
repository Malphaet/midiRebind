#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser

from mapping.midi import MessageParse
from mapping.midi import Actions

__TESTING=True

if __TESTING:
    class pyautonope(object):
        def __init__(self):
            pass

        def __call__(self,*args,**kwargs):
            return self

        def __repr__(self,*args,**kwargs):
            return ''

        def __getattribute__(self,*args,**kwargs):
            return self

    pyautogui=pyautonope()
else:
    import pyautogui

INPUTS=  [0,0,1,0,0,0,1,0]
MEMORIES=[1,1,1,0,0,0,0,0]


_ACTIVE=0b1
_SELECTED=0b10
_LIVE=0b100

_BASEVALUES=[
    INPUTS[:],
    MEMORIES[:],
    [[0]*8]*6
]
class demvars():
    def __init__(self):
        self.interface_nb=1
        self.output=None
        self.BASE_NOTE_INPUT=56
        self.BASE_NOTE_MASTERM=48

        self.listchange=[]
        self.lastpress=None #Does only account for the 8x8
        self.selected_pulse=(None,None)

        self.live_input=None
        self.selected_input=0
        #
        self.live_memory=None
        self.selected_memory=None

        self.INPUTS=[i*_ACTIVE for i in INPUTS]
        self.MEMORIES=[i*_ACTIVE for i in MEMORIES]

        self.VALUES=[self.INPUTS,self.MEMORIES,[[0]*8]*6]


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

    # Should do it in a similar way, cant find it
    def addChange(self,i,j,value,reset=False):
        "Do a value change, store the change for update"
        if i==None or j==None:
            return
        # self.listold+=[[i,j,self.VALUES[j][i]]]
        # if value==None:
        # if reset:
        #     value=_BASEVALUES[j][i]
        # else:
        #     value=self.VALUES[]
        self.listchange+=[[i,j,_BASEVALUES[j][i],reset]]
        # print(self.listchange)


    def appyChanges(self):
        "Apply all changes"
        allch=set()
        for i,j,v,r in self.listchange:
            allch.add((i,j))
            if r:
                self.VALUES[j][i]=_BASEVALUES[j][i]|v
                print(_BASEVALUES[j][i]|v,_BASEVALUES[j][i])
            else:
                self.VALUES[j][i]|=v
        self.listchange=[]

        for i,j in allch: # I feel like I'm doing this twice
            # print(i,j,self.COLORPLUGS[self.VALUES[j][i]])
            self.light(i,j,self.COLORPLUGS[self.VALUES[j][i]])

        # self.
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

    def updatemasterm(self,toupdate=range(8)):
        "Update the selected master memory"
        for i in toupdate:
            self.light(i,1,self.PLUGCOLORS[self.MEMORIES[i]])

vars=demvars()

def _onload(self):
    "Send a reset colors"
    import time,sys
    vars.output=self.outputs[vars.interface_nb]
    for i in range(64):
        vars.lightnote(i,0)

    vars.updateinput()
    vars.updatemasterm()


def switchinput(trigger,val,note,*params): #COULD DO WITH A CLASS AND .change(i,j,val)
    "Switch to the desired layer i1"
    i=note-vars.BASE_NOTE_INPUT
    toup=[vars.selected_input,i]
    vars.lastpress=(i,1)

    vars.INPUTS[vars.selected_input]=INPUTS[vars.selected_input]
    vars.selected_input=i
    vars.INPUTS[vars.selected_input]|=_SELECTED
    if vars.live_input:
        vars.INPUTS[vars.live_input]|=_LIVE

    vars.updateinput(toup)

    pyautogui.hotkey("i",str(i+1))

def takeall(trigger,val,note,*params):
    "Take all TA"
    if vars.live_input!=None:
        vars.INPUTS[vars.live_input]=INPUTS[vars.live_input]
        toup=[vars.live_input,vars.selected_input]
    else:
        toup=[vars.selected_input]

    vars.live_input=vars.selected_input
    vars.INPUTS[vars.selected_input]|=_SELECTED
    vars.INPUTS[vars.live_input]|=_LIVE
    vars.updateinput(toup)

    pyautogui.hotkey("t","a")

def switchmastermemory(trigger,val,note,*params):
    "Switch to the desired master memory M1"
    i=note-vars.BASE_NOTE_MASTERM
    vars.lastpress=(i,1)

    vars.addChange(*vars.selected_pulse,0,reset=True) # Reset this to base
    vars.selected_pulse=(i,1)
    vars.addChange(*vars.lastpress,_SELECTED,reset=True) # Add a selection

    # vars.selected_memory=i
    # vars.addChange()
    vars.appyChanges()
    pyautogui.hotkey("m",str(i))

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["switchinput"]=switchinput
        self.functionlist["mastermemory"]=switchmastermemory
        self.functionlist["takeall"]=takeall
