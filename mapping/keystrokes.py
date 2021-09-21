#!/bin/python3

# import pyautogui
from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import re,configparser
import pyautogui

from mapping.midi import MessageParse
from mapping.midi import Actions

def presskey(val,*params):
    "Press the given keys"
    # print("Pressing key {}, params {}".format(val,params))
    try:
        print(params)
        pyautogui.write(params)
    except Exception as e:
        print(e)
        pyautogui.write("CC")

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        self.functionlist["presskey"]=presskey
