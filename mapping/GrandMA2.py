from mapping import BasicMessageParse,BasicAction
import mido
import re

commandlist={1:"go",2:"stop",3:"resume",4:"timed_go",6:"set",7:"fire",11:"go_off"}
#A MessageParse object MUST be included in the file, the rest is implementation Specific
class MessageParse(BasicMessageParse):
    """Parsing of a gma SyEx message this parser is used once and will return a different Action object every time it is called"""

    def __init__(self):
        #super(Parse, self).__init__() #The init here is irrelevant
        #The data is converted from hex to decimal for readability and usability
        self._mapping = {"deviceid":127, #Will usually be 127 for ALL
        "commandformat":127, #1 is general lighting format, 2 is moving light format and 127 is ALL
        "command":None, #from 1 to 7 plus 11 (off)
        "data":None #The actual data
        }
        self.pattern=re.compile("240 127 (?P<deviceid>\d+) 0?2 (?P<commandformat>\d+) (?P<command>\d+) (?P<data>[\d+ ]+) 247")
        self._commandlist=commandlist

    def __call__(self,message):
        "Parse the message and depending on the type, return a different action"
        match=re.match(self.pattern,message)
        if match:
            # Matched
            return match
        else:
            raise MatchError
            return


class Action(BasicAction):
    """The list of action to perform when a message is read"""
    def __init__(self):
        pass

    def __call__(self,config):
        pass

class MatchError(Exception):
    pass
    #def __init__(self):
    #    super(MatchError, self).__init__()
