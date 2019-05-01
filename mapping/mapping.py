# This is the basic mapping of a midi message, all subsequent messages must either be children of this or implement those methods

class BasicMessageParse(object):
    """Classic System Specific Midi Message as Hex (BasicSyHexParse).
    Uses one method, parseMidi to parse the message and return a BasicMapping object with the mapping of the message inside"""

    def __init__(self):
        '''Basic init'''
        self._mapping={"value":None,"type":None} # A barebone initialisation, unusable, it will need to be overridden to work

    def __call__(self,message):
        """Take a midi SyxEx message and return a BasicAction (there can be many children of BasicAction to take more properly care of the cases)"""
        return BasicMapping(self._mapping)

class BasicAction(object):
    """A basic reading of the message, propreties are initialised depending on the way the SyEx message is formed,
    this objet will need the configuration to read and understand the message"""

    def __init__(self,dictmapping):
        'Barebone init'
        self._mapping=dictmapping

    def __call__(self,config):
        """Resolve the current action, all actions will be performed depending on what's inside the mapping and the config"""
        pass
