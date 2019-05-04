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
        self.outputs={} #Have every output in a dict
        self.dec10=[str(x) for x in range(10)]
        # Parse config & check sanity
        if "interface" not in self.config:
            raise IOError #You must define an interface to connect to
        self.populateSections()
        print self.sections

    def populateSections(self):
        "Create all the call setups"
        for elt in self.config.sections():
            if elt !="interface":
                if "/" in elt:
                    selt=elt.split("/")
                    if selt[0] not in self.sections:
                        self.sections[selt[0]]={}
                    self.sections[selt[0]].update({selt[1]:self.makeTriggers(self.config[elt])})
                else:
                    if elt in self.sections:
                        if "*" not in self.sections[elt]:
                            self.sections[elt]["*"]=self.makeTriggers(self.config[elt])
                            # This means you will override any "/x" config
                    else:
                        self.sections[elt]={"*":self.makeTriggers(self.config[elt])}

    def makeTriggers(self,conf):
        "Take a section of a config and put all triggers in a dict"
        keys={}
        for key in conf: # Reading every mapping and liking it to the appropriate Trigger
            if "/" in key: # There is a condition to an action
                note,ctype=key.split("/")
                if "-" in note:
                    nmin,nmax=note.split("-")
                    nmin,nmax=int(nmin),int(nmax)
                    for i in range(nmin,nmax):
                        pass#keys[i].condition(ctype,conf[key])
                else:
                    pass#keys[note].condition(ctype,conf[key])
            elif "-" in key: # There is a range of values to map
                nmin,nmax=key.split("-")
                nmin,nmax=int(nmin),int(nmax)
                for i in range(nmin,nmax):
                    keys[i]=self.makeAllKeys(i,conf[key],startkey=nmin,stopkey=nmax) #Do a different trigger for every ; and link to a different interface for every n/
            else: # Nothing fancy
                keys[int(key)]=self.makeAllKeys(int(key),conf[key])
        return keys

    def makeAllKeys(self,key,action,startkey=0,stopkey=0):
        """Make all the actions associated with the key
        startkey and stopkey indicate if an interpolation over the values is to be made"""
        #print key,action,startkey,stopkey
        #Check if there are multiple actions to do
        if ';' in action:
            allactions=[]
            for a in action.split(";"):
                #print a
                allactions+=self.makeAllKeys(key,a,startkey,stopkey)
            return allactions
        try:
            pack=action.split("/")
            if len(pack)==4:
                interfaceout,midiaction,note,intensity=pack
            elif len(pack)==2:
                midiaction,note=pack
                interfaceout,intensity=1,127
            elif len(pack)==3:
                if pack[0][0] not in self.dec10:
                    midiaction,note,intensity=pack
                    interfaceout=1
                else:
                    interfaceout,midiaction,note=pack
                    intensity=127
            else:
                raise ValueError
            #print "io:{} act:{} note:{} int:{}".format(interfaceout,midiaction,note,intensity)
            intensity,interfaceout=int(intensity),int(interfaceout)
        except:
            print("Config key {} is incorrect, values {} can't be unpacked".format(key,action))


        return [MidiTrigger(interfaceout,midiaction,note,self.findIntensity(key,startkey,stopkey,note))]

    def findIntensity(self,key,startkey,stopkey,note):
        if startkey!=stopkey: #do an interpolation over the values
            if "-" in note: #there is a range to interpolate over to
                nmin,nmax=note.split("-")
                nmin,nmax=int(nmin),int(nmax)
            else:
                nmin=int(note)
                nmax=nmin+stopkey-startkey #Just do the interpolation linearly
            if nmax-nmin!=stopkey-startkey:
                pad=(nmax-nmin)/(stopkey-startkey)
            else:
                pad=1
            return nmin+(key-startkey)*pad
        return int(note)
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

FTrue=lambda x: True

class MidiTrigger(object):
    """A midi trigger, will do a specific action when called"""
    def __init__(self,interface,messagetype,value,intensity):
        self.output=interface
        self.messagetype=messagetype
        self.value=value
        self.intensity=intensity
        self.condition=FTrue

    def __call__(self,val):
        """Execute the call if the condition is true"""
        pass

    def condition(self,ctype,funct):
        """Affect a specific action (usually a condition) to the execution of the event"""
        pass

    def __repr__(self):
        return "MidiTrigger({}/{}/{})@{}".format(self.messagetype,self.value,self.intensity,self.output)

class MatchError(Exception):
    pass
