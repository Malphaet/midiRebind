import mido

# Load the config and return an action class
class Binding(object):
    """Binding class, simple binding between note and actions"""

    def __init__(self, config):
        self.config=config
        self.loadConfig()

    def loadConfig(self):
        pass
        #Detect config error
        #Bind all actions to a return message
        #Make a easy list to acess list of actions
    def read(gmaMessage):
        """Read the gmaMessage and return a list of action"""
        #Readmessage
        #Parse message with config
        #Handle Errors
        #Return Action or ActionList that can be .run
        return ActionList()

class ActionList(object):
    """List of action to play after a message is receaved"""

    def __init__(self,list):
        """Takes the list of actions detected and """
        pass

class Action(object):
    """Action itself, a mapper for the midi library"""

    def __init__(self,actiontype):
        """Take one action and bind the correct midi message"""
        self.actiontype=actiontype
