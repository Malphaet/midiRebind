from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
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


# An Action object MUST be included in the file.
class Actions(BasicActions):
    """The list of action to perform when a message is read"""
    def __init__(self, interface):
        super(Actions, self).__init__(interface)

    # This funtion is MANDATORY, it makes the link between MessageParse and Action
    def __call__(self,match):
        "Make the link between the regex and the action"
        action=commandlist[int(match.group('command'))]
        id,value="1","1"
        if action=="set":
            data=match.group("data")
            data=data.split(" ")
            page=int(data[1])
            id=int(data[0])
            # value=int(data[2])/128+int(data[3])/1.28 the percent value
            value=int(data[3]) # Just mapped from 0 to 127
        elif action=="fire":
            id=int(match.group("data")) # Can only be from 0 to 255 ?
            value=""
        #print(action,id,page)
        try:
            listact=self.findAction(action,id,page)
            for act in listact:
                act(value)
        except:
            # No action linked to the trigger
            pass


# Same as above, import BasicMidiInterface as MidiInterface could be used instead
# MidiInterface(config)
MidiInterface=BasicMidiInterface
