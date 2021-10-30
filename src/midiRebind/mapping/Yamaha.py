# mypy: ignore-errors

from src.midiRebind.mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface

commandlist={127:"DCA",55:"IN",84:"MIX",101:"MATRICE",115:"MASTER",336:"MASTER2",122:"PAGE",53:"MUTE",893:"CUE"}
# Doc says 11 is go_off, test says otherwise

#A MessageParse object MUST be included in the file, the rest is implementation Specific
class MessageParse(BasicMessageParse):
    """Parsing of a Yamaha SyEx message this parser is used once \
    and will return a different Action object every time it is called"""

    def __init__(self):
        #The data is converted from hex to decimal for readability and usability by mido
        self.typebit=0 # 6th number, usually 0. 1 is DCA and pages. 2 is second master.
        self.command=None # 7th number. The command sent
        self.data=None #The actual data

        self._commandlist=commandlist

    def __call__(self,message):
        "Parse the message and return either a match or raise an error"
        if message.type=="sysex":
            message=message.data
        else:
            raise MatchError("Message is not sysex")
        try:
            self.typebit=message[5]
            self.command=message[6]+message[5]*127
            self.data=message[7:]
            return self
        except:
            raise MatchError("Can't parse the data {}".format(message))

    def __str__(self):
        return "<MessageParse>[type:{}/cmd:{}/data:{}]".format(\
        self.typebit,self.command,self.data)

def makeInt(table):
    "Take the weird tuple from 00,00 to 6,127 and make a number from 0 to 127"
    return int((table[0]*127+table[1])/8)

# An Action object MUST be included in the file.
class Actions(BasicActions):
    """The list of action to perform when a message is read"""
    def __init__(self, interface):
        super(Actions, self).__init__(interface)

    # This funtion is MANDATORY, it makes the link between MessageParse and Action
    def __call__(self,match):
        "Make the link between the regex and the action"
        # print(int(match.command))
        action=commandlist[int(match.command)]
        id,value=1,1
        page=0 # Yamaha consoles don't use pages in a way that is relevant to us
        #"DCA",55:"IN",84:"MIX",101:"MATRICE",115:"MASTER",82:"MASTER2",51:"PAGE"
        if action in ["IN","MIX","MATRICE","MASTER","MASTER2"]:
            data=match.data
            #print(data[6:8],makeInt(data[6:8]))
            value=makeInt(data[7:])
            id=int(data[3]) # Just mapped from 0 to 127
        elif action == "DCA":
            pass
        elif action=="CUE":
            data=match.data
            value=int(data[8])*127
            id=int(data[3])
        elif action=="MUTE":
            data=match.data
            id=int(data[3])
            value=int(data[8])*127
        elif action=="PAGE":
            data=match.data
            id=int(data[3])
            value=int(data[8])
        else:
            return
        try:
            # print(action,id,value,data)
            listact=self.findAction(action,id,page)
            for act in listact:
                 act(value)
        except:
            # No action linked to the trigger
            pass

# Same as above, import BasicMidiInterface as MidiInterface could be used instead
# MidiInterface(config)
MidiInterface=BasicMidiInterface
