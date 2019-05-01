class BasicMessageParse(object):
    """Classic System Specific Midi Message as Hex (BasicSyHexParse).
    Uses one method, parseMidi to parse the message and return a BasicMapping object with the mapping of the message inside"""

    def __init__(self):
        '''Basic init'''
        self._mapping={"value":None,"type":None} # A barebone initialisation, unusable, it will need to be overridden to work

    def parseMidi(self,message):
        """Take a midi SyxEx message and return a BasicMapping (there can be many children of BasicMapping to take more properly care of the cases)"""
        return BasicMapping(self._mapping)

class BasicMapping(object):
    """A basic reading of the message, propreties are initialised depending on the way the SyEx message is formed,
    this objet will need the configuration to read and understand the message
    """
    def __init__(self,dictmapping):
        'Barebone init'
        self._mapping=dictmapping

    def 
