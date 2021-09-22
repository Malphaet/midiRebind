#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
import pyautogui

from mapping.midi import MessageParse
from mapping.midi import Actions

BASE_NOTE=56

def presskey(val,note,*params):
    "Press the given keys"
    pass#print(val,note,params)

def switchinput(val,note,*params):
    "Switch to the desired layer"
    topress=note-BASE_NOTE+1
    print(val,note)
    pyautogui.hotkey("i",str(topress))

def takeall():
    "TA"
    pass

def mastermemory():
    "M1"
# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        self.functionlist["presskey"]=presskey
        self.functionlist["switchinput"]=switchinput
