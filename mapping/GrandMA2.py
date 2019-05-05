from mapping.base import BasicMessageParse,BasicAction,MatchError,BasicMidiInterface
import mido
import re,configparser

commandlist={1:"go",2:"stop",3:"resume",4:"timed_go",6:"set",7:"fire",11:"go_off"}
#A MessageParse object MUST be included in the file, the rest is implementation Specific
class MessageParse(BasicMessageParse):
    """Parsing of a gma SyEx message this parser is used once and will return a different Action object every time it is called"""

    def __init__(self):
        #The init here is irrelevant
        #The data is converted from hex to decimal for readability and usability by mido
        self._mapping = {"deviceid":127, #Will usually be 127 for ALL
        "commandformat":127, #1 is general lighting format, 2 is moving light format and 127 is ALL
        "command":None, #from 1 to 7 plus 11 (off)
        "data":None #The actual data
        }
        self.pattern=re.compile("240 127 (?P<deviceid>\d+) 0?2 (?P<commandformat>\d+) (?P<command>\d+) (?P<data>[\d+ ]+) 247") #The regex that will map the SysEx message
        self._commandlist=commandlist

    def __call__(self,message):
        "Parse the message and return either a match or raise an error"
        match=re.match(self.pattern,message)
        if match:
            return match
        else:
            raise MatchError

# This funtion is MANDATORY, it makes the link between MessageParse and Action
def CallAction(match,ActionObj):
    "Make the link between the regex and the action"
    pass

# An Action object MUST be included in the file.
# Interitance and method override can be used, but aren't needed here
# Action(config)
Action=BasicAction

# Same as above, import BasicMidiInterface as MidiInterface could be used instead
# MidiInterface(config)
MidiInterface=BasicMidiInterface
