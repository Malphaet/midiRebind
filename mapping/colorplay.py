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

A=[[3,3,3,0],[3,0,0,3],[3,0,0,3],[3,3,3,0],[3,0,0,3],[3,0,0,3],[3,3,3,0]]
B=[[1,1,1,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[1,1,1,0]]
C=[[1,1,1,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]]
D=[[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,1,1,0]]

E=[[3,0,3],[3,3,3]]+[[3,0,3]]*3
F=[[0,1,0],[1,0,1],[1,1,1]]+[[1,0,1]]*2
G=[[1,0,1]]*2+[[0,1,0]]+[[1,0,1]]*2
SPACE3=[[0,0]]*5
SPACE7=[[0,0,0]]*7

WORD=[A,B,C,D,SPACE7]
WORD2=[E,F,G,SPACE3]

def makeword(table):
    final=[[] for i in range(8)]

    for letter in table:
        linef=[]
        for i in range(len(letter)):
            linef=letter[i]+[0]
            final[i]+=linef
    return final

BIGWORD=makeword(WORD2)

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


    def normalize(i,dec,width,loop):
        new=i-dec
        # if i==0:
        #     print(i,dec,new,new%(width+0))
        if new>width:
            if not loop:
                return -1
            else:
                return new%(width+0)
        elif new<0:
            if not loop:
                return -1
            else:
                while new<0: # Pretty shit implementation
                    new+=width
                return new
        return new


    def makematrix(matrix,decx=0,decy=0,loop=False):
        "Shift a matrix and return the 8x8 to print"
        width,height=len(matrix[0]),len(matrix)
        toprint=[[0]*8 for i in range(8)]
        # print(width)

        for i in range(8):
            for j in range(8):
                new_x=normalize(i,decx,width,loop)
                #new_y=normalize(j,decy,height,loop)
                new_y=j
                if new_x<0 or new_y<0:
                    color=0
                else:
                    try:
                        color=matrix[new_y][new_x]
                    except IndexError:
                        color=0
                toprint[j][i]=color
        return toprint

    def printmatrix(newmatrix,oldmatrix=None):
        "Print and 8x8 matrix"
        for i in range(8):
            for j in range(8):
                if oldmatrix:
                    if oldmatrix[j][i]!=newmatrix[j][i]:
                        VARS.light(i,j,newmatrix[j][i])
                else:
                    VARS.light(i,j,newmatrix[j][i])
            time.sleep(0.01)

    def clearmatrix(matrix,decx,decy,loop=False):
        pass

    newmat=None
    for i in range(200):
        oldmat,newmat=newmat,makematrix(BIGWORD,-i,0,True)
        printmatrix(newmat,oldmat)
        time.sleep(0.04)

    # for j in range(0,10):
    #      time.sleep(0.3)
    #      printmatrix(BIGWORD)
    # #     print("E")
    #     for i in range(64):
    #         VARS.lightnote(i,0)
    #     time.sleep(0.2)
    #
    #     printmatrix(BIGWORD,0,0)
    #     time.sleep(0.01)

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
