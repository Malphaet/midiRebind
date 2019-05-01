from mapping import BasicMessageParse,BasicAction
import mido

#A MessageParse object MUST be included in the file, the rest is implementation Specific
class MessageParse(BasicMessageParse):
    """Parsing of a gma SyEx message"""

    def __init__(self, arg):
        #super(Parse, self).__init__() #The init here is irrelevant
        self._mapping = arg

class Action(BasicAction):
    """The list of action to perform when a message is read"""
    def __init__(self):
        pass

    def resolve(self,config):
        pass
