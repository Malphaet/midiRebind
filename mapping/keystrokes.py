#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
import pyautogui

from mapping.midi import MessageParse
from mapping.midi import Actions

BASE_NOTE_INPUT=56
BASE_NOTE_MASTERM=48

def presskey(val,note,*params):
    "Press the given keys"
    pass#print(val,note,params)

def switchinput(val,note,*params):
    "Switch to the desired layer i1"
    topress=note-BASE_NOTE_INPUT+1
    pyautogui.hotkey("i",str(topress))

def takeall(val,note,*params):
    "Take all TA"
    pyautogui.hotkey("t","a")

def mastermemory(val,note,*params):
    "Switch to the desired master memory M1"
    topress=note-BASE_NOTE_MASTERM+1
    pyautogui.hotkey("m",str(topress))

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        self.functionlist["presskey"]=presskey
        self.functionlist["switchinput"]=switchinput
        self.functionlist["mastermemory"]=mastermemory
        self.functionlist["takeall"]=takeall
