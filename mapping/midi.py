from mapping.base import BasicMessageParse,BasicActions,MatchError,BasicMidiInterface
import mido
import configparser

#A MessageParse object MUST be included in the file, the rest is implementation Specific
class MessageParse(BasicMessageParse):
    """Parsing of a midi message this parser is used once and will return a different Action object every time it is called"""

    def __init__(self):
        #The data is converted from hex to decimal for readability and usability by mido
        self.type=None #note_off note_on control_change program_change sysex (technically all the others but we don't care much for it)
        self.channel=0 #0 by default, but can be anything
        self.note=None #0 - 127 (it will be the program in program_change etc...)
        self.value=None #The actual value, sometimes None

    def __call__(self,message):
        "Parse the message and return either a match or raise an error"
        self.type=message.type
        try:
            if message.type=="note_off" or message.type=="note_on":
                self.channel=message.channel
                self.note=message.note
                self.value=message.velocity
            elif message.type=="control_change":
                self.channel=message.channel
                self.note=message.control
                self.value=message.value
            elif message.type=="program_change":
                self.channel=message.channel
                self.note=message.program
                self.value=None
            else:
                raise MatchError("Message is not either note_off, note_on, control_change or program_change")
            return self
        except:
            raise MatchError("Can't parse the data {}".format(message))

    def __str__(self):
        return "<MessageParse>[ty:{}/note:{}/value:{}]@{}".format(self.type,self.note,self.value,self.channel)
# An Action object MUST be included in the file.
class Actions(BasicActions):
    """The list of action to perform when a message is read"""
    def __init__(self, interface):
        super(Actions, self).__init__(interface)

    # This funtion is MANDATORY, it makes the link between MessageParse and Action
    def __call__(self,match):
        "Make the link between the regex and the action"
        id,value,page="1","1","*"
        try:
            listact=self.findAction(match.type,match.note,"*")
            for act in listact:
                act(match.value)
        except:
            # No action linked to the trigger
            pass

# MidiInterface(config)
MidiInterface=BasicMidiInterface
