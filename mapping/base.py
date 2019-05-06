# This is the basic mapping of a midi message, all subsequent messages must either be children of this or implement those methods
import configparser
import mido,re

class BasicMidiInterface(object):
    "Basic midi interface"
    def __init__(self,configfile):
        "Try to open the defined interfaces in the config"

        self.config=configparser.ConfigParser()
        self.config.read(configfile)

        # Parse config & check sanity
        if "interface" not in self.config:
            raise IOError #You must define an interface to connect to

        self.input=""
        self.outputs={}
        #self.outchannels #not as of now, maybe later
        outputmatch=re.compile("output(?P<outnb>\d+)")
        for elt in self.config["interface"]:
            if elt=="input":
                self.input=self.openin(self.config["interface"][elt])
            else:
                match=outputmatch.match(elt)
                if match:
                    nb=match.group('outnb')
                    self.outputs[int(nb)]=self.openout(self.config["interface"][elt])
                #self.outputs.append(self.config["interface"][elt])

    def interfaceIn(self,number=1):
        "Return the input interface, as of now number as no use"
        return self.input

    def interfaceOut(self,number):
        "Return the output interface related to the number given"
        return self.outputs[int(number)]

    def openin(self,name):
        "Try and open an output interface"
        try:
            o=mido.open_input(name)
        except:
            print("[ERROR] Impossible to open input {} (available are {})".format(name,mido.get_input_names()))
            o=None
        return o
    def openout(self,name):
        "Try and open an input interface"
        try:
            o=mido.open_output(name)
        except:
            print("[ERROR] Impossible to open output {} (available are {})".format(name,mido.get_output_names()))
            o=None
        return o
    def __delete__(self):
        try:
            for i in self.outputs:
                i.close()
            self.input.close
        except:
            pass


class BasicMessageParse(object):
    """Classic System Specific Midi Message as Hex (BasicSyHexParse).
    Uses one method, parseMidi to parse the message and return a BasicMapping object with the mapping of the message inside"""

    def __init__(self):
        '''Basic init'''
        self._mapping={"value":None,"type":None} # A barebone initialisation, unusable, it will need to be overridden to work

    def __call__(self,message):
        """Take a midi SyxEx message and return a BasicAction (there can be many children of BasicAction to take more properly care of the cases)"""
        return BasicMapping(self._mapping)

class BasicActions(object):
    """The list of action to perform when a message is read"""
    def __init__(self,midiInterface):
        """Parse the config and ready all return actions"""
        # Load config, in a near future, the config will be preloaded beforehand, but for right now, practicallity will prevail
        self.config=midiInterface.config
        self.interface=midiInterface
        self.sections={}
        #self.outputs={} #Have every output in a dict THIS PART IS SUPPOSEDLY ALREADY TAKEN CARE OF

        # Very cheesy way to figure out notes from control, I should find a better way, but I can't be bothered to
        self.dec10=[str(x) for x in range(10)]

        # Parse config & check sanity
        if "interface" not in self.config:
            raise IOError #You must define an interface to connect to

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
                    if i not in keys:
                        keys[i]=[]
                    keys[i]+=self.makeAllKeys(i,conf[key],startkey=nmin,stopkey=nmax) #Do a different trigger for every ; and link to a different interface for every n/
            else: # Nothing fancy
                if int(key) not in keys:
                    keys[int(key)]=[]
                keys[int(key)]+=self.makeAllKeys(int(key),conf[key])
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
            print("[WARNING] Config key {} is incorrect, values {} can't be unpacked".format(key,action))
        try:
            return [BasicMidiTrigger(self.interface.interfaceOut(int(interfaceout)),midiaction,self.findNote(key,startkey,stopkey,note),intensity)]
        except (KeyError):
            print("[WARNING] Can't find interface {} for note {} action {}, legal interfaces are {}".format(interfaceout,note,action,[i for i in self.interface.output.keys()]))
            return [] #This choice is not necessary the best, but I figure it's easier that forcing the config to be perfect
        except ValueError:
            print("[WARNING] Incorrect values given to the midi message {}".format(action))
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

class MatchError(Exception):
    pass

class BasicMidiTrigger(object):
    """A midi trigger, will do a specific action when called"""
    def __init__(self,interface,messagetype,value,intensity):
        self.output=interface
        self.messagetype=messagetype
        self.value=value
        self.intensity=intensity
        self.interface=interface
        self.valuefn=None
        message=RecognisedMessagesTypes[messagetype]
        attributes={}
        self.toggle=None
        attributes[message[1]]=value
        try:
            attributes[message[2]]=intensity
            self.valuetype={message[2]:0}
        except IndexError:
            self.valuetype={}

        self.message=mido.Message(RecognisedMessagesTypes[messagetype][0],**attributes)

    def __call__(self,val):
        """Change the value (if necessary) and send the message"""
        self.changevalue(val)
        return self.sendmessage()

    def changevalue(self,val):
        "Change the value (depending on the toggles etc...)"
        #for cond in self.conditions:
        #    if not cond(val):
        #        return #A condition isn't met, returning
        change=self.value
        if self.valuefn:
            change=self.valuefn(val)
        if self.toggle!=None:
            if self.toggle:
                change=self.valtrue
            else:
                change=self.valfalse
        if change!=self.value and change != None and change !="":
            self.value=change
            self.valuetype[list(self.valuetype)[0]]=change
            self.message=self.message.copy(**self.valuetype)

    def sendmessage(self):
        if self.toggle!=None:
            self.toggle=not self.toggle
        #print("SENDING:",self.message) #TODO Add Verbose option
        self.interface.send(self.message)

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
            print("[ERROR] Cant evaluate funtion {}".format(fn))

    def addstate(self,valtrue,valfalse):
        "The message will now send two state values intead"
        self.toggle=True
        self.valtrue=valtrue
        self.valfalse=valfalse

    def __repr__(self):
        return "<MT>({}/{}/{})@{}".format(self.messagetype,self.value,self.intensity,self.output)
