from mapping import BasicMessageParse,BasicAction
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

#An Action object MUST be included in the file.
#Called first with a config file, will be callable to launch an action with the matched regex as an argument
class Action(BasicAction):
    """The list of action to perform when a message is read"""
    def __init__(self,config):
        """Parse the config and ready all return actions"""
        # Load config, in a near future, the config will be preloaded beforehand, but for right now, practicallity will prevail
        self.config=configparser.ConfigParser()
        self.config.read(config)
        self.sections={}
        # Parse config & check sanity
        if "interface" not in self.config:
            raise IOError #You must define an interface to connect to

        # Create all the call setups
        for elt in self.config.sections():
            if elt !="interface":
                if "/" in elt:
                    selt=elt.split("/")
                    if selt[0] not in self.sections:
                        self.sections[selt[0]]={}
                    self.sections[selt[0]].update({selt[1]:self.config[elt]})
                else:
                    if elt in self.sections:
                        if "*" not in self.sections[elt]:
                            self.sections[elt]["*"]=self.config[elt]
                            # This means you will override any "/x" config
                    else:
                        self.sections[elt]={"*":self.config[elt]}


        # Populate all the function calls with the data of the config sections
        for elt in self.sections: #Going in every section
            for group in self.sections[elt]: # Going in every sub-group
                conf,self.sections[elt][group]=self.sections[elt][group],{} #Replacing the links to the config with the real dict of links
                for key in conf: # Reading every mapping and liking it to the appropriate Trigger
                    if "/" in key: # There is a condition to an action
                        note,ctype=key.split("/")
                        if "-" in note:
                            nmin,nmax=note.split("-")
                            for i in range(nmin,nmax):
                                conf.sections[elt][group][i].condition(ctype,conf[key])
                        else:
                            conf.sections[elt][group][note].condition(ctype,conf[key])
                    elif "-" in key: # There is a range of values to map
                        nmin,nmax=key.split("-")
                        for i in range(nmin,nmax):
                            conf.sections[elt][group][i]=MidiTrigger() #Do a different trigger for every ; and link to a different interface for every n/
                    else: # Nothing fancy
                        self.sections[elt][group][key]=MidiTrigger()

    def format(self,command,number,page):
        "Format a match to call the correct action"
        try:
            return self.sections[command][page]
        except:
            return self.sections[command]["*"]

    def __call__(self,match):
        """Launch the action depending on the config, the config format is supposed to be as canon as possible
        but since the actual implementation is custom made... go wild ?"""
        # Try a predefined action
        pass

class MidiTrigger(object):
    """A midi trigger, will do a specific action when called"""
    def __init__(self,interface,message):
        self.output=interface
        self.message=message
        self.cond=False
    def __call__(self,val):
        """Execute the call if the condition is true"""
        pass

    def condition(self,ctype,funct):
        """Affect a specific action (usually a condition) to the execution of the event"""
        pass

class MatchError(Exception):
    pass
