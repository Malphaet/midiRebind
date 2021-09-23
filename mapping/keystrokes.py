#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
import pyautogui

from mapping.midi import MessageParse
from mapping.midi import Actions

PLUGGED=[0,0,1,0,0,0,1,0]

class demvars():
    def __init__(self):
        self.interface_nb=1
        self.output=None
        self.BASE_NOTE_INPUT=56
        self.BASE_NOTE_MASTERM=48
        self.BASE_COLORS=[  [1,1,1,1,1,1,1,1],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0]
        ]
        self.active_input=None
        self.PLUGGED=PLUGGED
        self.COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}
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

VARS=demvars()

A=[[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,0]]
B=[[1,1,1,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[1,1,1,0]]
C=[[1,1,1,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]]
D=[[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,1,1,0]]

WORD=[A,B,C,D]

def makeword(table):
    final=[[] for i in range(8)]

    for letter in table:
        linef=[]
        for i in range(len(letter)):
            linef=letter[i]+[0]
            final[i]+=linef
    return final

BIGWORD=makeword(WORD)

def _onload(self):
    "Send a reset colors"
    import time,sys
    VARS.output=self.outputs[VARS.interface_nb]
    for i in range(64):
        VARS.lightnote(i,0)

    def printletter(letter):
        for i in range(4):
            for j in range(7):
                VARS.light(i,j,letter[j][i])

    def printmatrix(matrix,decx=0,decy=0):
        maxi,maxj=len(matrix[0]),len(matrix)
        for i in range(8):
            for j in range(8):
                try:
                    VARS.light(i,j,BIGWORD[j-decy][i+decx])
                except IndexError:
                    pass
            time.sleep(0.01)


    for j in range(20):
        for i in range(64):
            VARS.lightnote(i,0)
        time.sleep(0.05)

        printmatrix(BIGWORD,j,0)
        time.sleep(0.01)

    # while 1:
    #     for k in range(4):
    #         printletter(WORD[k])
    #         time.sleep(0.5)
    sys.exit()


def presskey(trigger,val,note,*params):
    "Press the given keys"
    pass#print(val,note,params)

def switchinput(trigger,val,note,*params):
    "Switch to the desired layer i1"
    topress=VARS.findit(note-VARS.BASE_NOTE_INPUT+1,0)

    VARS.active_input=topress

    for trigger in trigger.parent.findAction('note_on',note,"*"):
        print(trigger.value,trigger.intensity)
    #pyautogui.hotkey("i",str(topress))

def takeall(trigger,val,note,*params):
    "Take all TA"
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
        self.functionlist["presskey"]=presskey
        self.functionlist["switchinput"]=switchinput
        self.functionlist["mastermemory"]=mastermemory
        self.functionlist["takeall"]=takeall
