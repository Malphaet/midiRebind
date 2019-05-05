from mapping.base import BasicMessageParse,BasicAction,MatchError
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
        self.outputs={} #Have every output in a dict THIS PART IS SUPPOSEDLY ALREADY TAKEN CARE OF

        # Very cheesy way to figure out notes from control, I should find a better way, but I can't be bothered to
        self.dec10=[str(x) for x in range(10)]

        # Parse config & check sanity
        if "interface" not in self.config:
            raise IOError #You must define an interface to connect to

        #TODO WARNING; THIS IS SUPPOSEED TO BE TAKEN CARE BY THE FUNCTION CALLING Action()
        self.outputs={1:self.config["interface"]["output1"], 2:self.config["interface"]["output2"]}

        self.populateSections()
        #self.prettyprint()

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
                note,atype=key.split("/")
                if "-" in note:
                    nmin,nmax=note.split("-")
                    nmin,nmax=int(nmin),int(nmax)
                    for i in range(nmin,nmax):
                        for trigger in (keys[int(i)]):
                            trigger.addspecial(atype,conf[key])
                else:
                    for trigger in keys[int(note)]:
                        trigger.addspecial(atype,conf[key])
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
        #Check if there are multiple actions to do
        if ';' in action:
            allactions=[]
            for a in action.split(";"):
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
            intensity,interfaceout=int(intensity),int(interfaceout)
        except:
            print("Config key {} is incorrect, values {} can't be unpacked".format(key,action))
        try:
            return [MidiTrigger(self.outputs[interfaceout],midiaction,self.findNote(key,startkey,stopkey,note),intensity)]
        except (KeyError):
            print("Can't find interface {} for note {} action {}, legal interfaces are {}".format(interfaceout,note,action,[i for i in self.outputs.keys()]))
            return [] #This choice is not necessary the best, but I figure it's easier that forcing the config to be perfect
        except ValueError:
            print("Incorrect values given to the midi message {}".format(action))
            return []

    def findNote(self,key,startkey,stopkey,note):
        "Find the note to bind to the received one"
        if startkey!=stopkey: #do an interpolation over the values
            if "-" in note: #there is a range to interpolate over to
                nmin,nmax=note.split("-")
                nmin,nmax=int(nmin),int(nmax)
            else:
                nmin=int(note)
                nmax=nmin+stopkey-startkey #Just do the interpolation linearly
            if nmax-nmin!=stopkey-startkey:
                pad=int((nmax-nmin)/(stopkey-startkey))
            else:
                pad=1
            return nmin+(key-startkey)*pad
        return int(note)

    def findAction(self,command,number,page):
        "Find the correct Action when a command is received"
        try:
            return self.sections[command][str(page)][int(number)]
        except:
            return self.sections[command]["*"][int(number)]

    def __call__(self,match):
        """Launch the action depending on the config, the config format is supposed to be as canon as possible
        but since the actual implementation is custom made... go wild ?"""
        # Try a predefined action
        pass

    def __repr__(self):
        return(self.sections)

    def prettyprint(self):
        for sect in self.sections:
            for subsect in self.sections[sect]:
                print("[{}] > {}".format(sect,subsect))
                for elt in self.sections[sect][subsect]:
                    print("  {} : {}".format(elt,self.sections[sect][subsect][elt]))

FTrue=lambda x: True
RecognisedMessagesTypes={
    "note":["note_on","note","velocity"],
    "sysex":["sysex","data"],
    "cc":["control_change","control","value"],
    "on":["note_on","note","velocity"],
    "off":["note_off","note","velocity"],
    "pc":["program_change","program"]}

class MidiTrigger(object):
    """A midi trigger, will do a specific action when called"""
    def __init__(self,interface,messagetype,value,intensity):
        self.output=interface
        self.messagetype=messagetype
        self.value=value
        self.intensity=intensity
        self.valuefn=None
        message=RecognisedMessagesTypes[messagetype]
        attributes={}
        self.toggle=None
        attributes[message[1]]=value
        self.valuetype={message[1]:0}
        try:
            attributes[message[2]]=intensity
        except IndexError:
            pass

        self.message=mido.Message(RecognisedMessagesTypes[messagetype][0],**attributes)

    def __call__(self,val):
        """Execute the call if the condition is true"""
        #for cond in self.conditions:
        #    if not cond(val):
        #        return #A condition isn't met, returning
        if self.valuefn:
            val=self.valuefn(val)
        if self.toggle!=None:
            if self.toggle:
                val=self.valtrue
            else:
                val=self.valfalse

        print(val)
        self.message.copy()
        return self.sendmessage()

    def sendmessage(self):
        print("SENDING: ")
        print(self.message)

    def addspecial(self,typ,val):
        """Affect a specific action (usually a condition) to the execution of the event"""
        if typ == "val":
            self.addvalfn(val)
        elif typ == "toggle":
            valt,valf=val.split("/")
            self.addstate(int(valt),int(valf))

    def addvalfn(self,fn):
        "Add a special function to calculate the value"
        try:
            self.valuefn=eval(fn)
            #print(self.valuegn(42))
        except:
            print("Cant evaluate funtion {}".format(fn))

    def addstate(self,valtrue,valfalse):
        "The message will now send two state values intead"
        self.toggle=True
        self.valtrue=valtrue
        self.valfalse=valfalse

    def __repr__(self):
        return "<MT>({}/{}/{})@{}".format(self.messagetype,self.value,self.intensity,self.output)
