#!/bin/python3
###########################
# IMPORTS
import mido
###########################
# FUNCTION DEFINES

_VERBOSE=4

nopeF=lambda *x:None
def printl(label=""):
    def _pl(*args):
        print(label,*args)
    return _pl

eprint=printl("[mPH:ERROR]")
dprint,ddprint,iprint,wprint=nopeF,nopeF,nopeF,nopeF

if _VERBOSE>=1:
    wprint=printl("[mPH:WARNING]")
if _VERBOSE>=2:
    iprint=printl("[mPH:INFO]")
if _VERBOSE>=3:
    dprint=printl("[mPH:DEBUG]")
if _VERBOSE>=4:
    ddprint=printl("[mPH:DDEBUG]")

###########################
# CLASS DEFINES
class IOInterface():
    "Handle the IO actions between an external script and a midiPageHandler interface"
    def __init__(self,pagehandler,externalProgram):
        self._pageHandler=pagehandler
        self._listActionsH={}
        self._listActionsIO={}
        self._pageHandler._IOInterface=self
        self._externalProgram=externalProgram

    def addActionIO(self,matchName,action):
        """Associate a function to a match to a message received
            [Handler] -> Action -> [externalP]
        """
        self._listActionsIO[matchName]=action

    def addActionH(self,name,action):
        """Associate a function to match to a handler action
            [externalP] -> Action -> [Handler]
        """
        self._listActionsH[name]=action

    def receiveAction(self,typeM,messageMatch,*args):
        """Acknoledge a message and do the appropriate actions
            [externalP] -> messageReceived -> Action -> [Handler]
        """
        try:
            dprint("Received the command {} from the pulse ({})".format(typeM,messageMatch))
            self._listActionsIO[typeM](messageMatch,*args)
        except KeyError:
            wprint("The message type doesn't exits",typeM)
        self._pageHandler.sendAction(typeM,messageMatch,*args)

    def receiveNote(self,note,val):
        """Acknoledge a control received and do the appropriate actions
            [internalMidiAction] -> [Handler]
        """
        self.handler.noteReceived(note,val)

    def sendAction(self,name,*args):
        """An action is to be sent to the external Program
            [Handler] -> [externalP]
        """
        dprint("Sending command {} with args {} to the pulse".format(name,args))
        try:
            self._listActionsIO[name](*args)
        except KeyError:
            print(self._listActionsH)
            wprint("Can't send action request",name)

    def toHandler(self,commandname,*args,**kwargs):
        "Send directly an action to the handler"
        self._pageHandler.receiveAction(commandname,*args,**kwargs)

    def toExternalProgram(self,commandname,*args,**kwargs):
        "Send directly a message to the pulse"
        self._externalProgram.receiveCommand(commandname,*args,**kwargs)

class IOInterfacePulse(IOInterface):
    "Specialised pulse interface"

    def __init__(self,pagehandler,pulseModule,externalProgram):
        super(IOInterfacePulse,self).__init__(pagehandler,externalProgram)
        self._pulseModule=pulseModule
        # Commands that should be sent to the pulse
        # self.addActionIO("LAYERINP",self._externalProgram.changeLayer)
        # self.addActionIO("TAKEALL",self._externalProgram.takeAll)
        # self.addActionIO("LOADMM",self._externalProgram.loadMM)
        # self.addActionIO("QUICKF",self._externalProgram.quickFrame)
        # self.addActionIO("FREEZE",self._externalProgram.freezeScreenAll)
        # self.addActionIO("SCRNUPD",self._externalProgram.updateFinishedAll)

    def receiveMessage(self,command,*args,**kwargs):
        """A message was received from the pulse and will be redirected to the controller
        """
        dprint("Using RM/Forb")
        # self._pageHandler.receiveAction(command,*args,**kwargs)
        self._pulseModule.receiveCommand(command,*args,**kwargs)

    def receiveCommand(self,command,*args,**kwargs):
        "A message was received from the handler and will be redirected to the pulse"
        dprint("Using RC/Forb")
        self._externalProgram.receiveMessage(command,*args,**kwargs)


class midiPageHandler(object):
    "Page Handler, with some methods to manage a midi remote more easily"

    def __init__(self,table,pages=1):
        """The noteArray contains a list of virtual lines and the corresponding notes"""
        self._posToNote=[]
        self._noteToPos=[]
        self._basevalues=[] # Store states given by the system or the machine
        self._activebasevalues=[] # Store the values of the active page
        self._changedbasevalues=[] # Store the active values, not yet updated
        self._heightV=0
        self._widthV=0
        self._IOInterface=None
        self.newListChanges()
        self._listPossibleValues={None:0b0}
        self.possibleStatus={}
        self.__maxV=0b1
        self._page=0
        self._maxpages=pages
        self._maxN=0
        self._makeNotes(table)
        self.initValues()

    ###################
    # Important methods for Access
    def addStatusPos(self,statusName,linecol,page=None):
        "Apply a status to a position, applied when applyChanges is called"

    def getColorPos(self,linecol):
        "Get the active color from a position"

    def listNoteChanges(self):
        "Yield the list of (note,value) to update"
        for pos in self.listChanges():
            yield self.posToNote(pos),self.colorFrom(pos)

    def noteReceived(self,note,val):
        "A note has been received, do the appropriate actions"
        pass

    ####################
    # Manage attributes
    def _makeNotes(self,table):
        "Make the note conversion tables and update everything"
        self._heightV,self._widthV=len(table),len(table[0])
        for i,j in self.allIndexes():
            self._maxN=max(table[i][j],self._maxN)
        self._noteToPos=[(None,None)]*(self._maxN+1)
        self._posToNote=[[table[i][j] for j in range(self._widthV)] for i in range(self._heightV)]
        for i,j in self.allIndexes():
            self._noteToPos[table[i][j]]=(i,j)

    def initValues(self):
        "Init all tables with default values"
        self._basevalues=[[[0 for i in range(self._widthV)] for j in range(self._heightV)] for k in range(self._maxpages)]
        self._activebasevalues=self._basevalues[self._page]
        self._changedbasevalues=[[0 for i in range(self._widthV)] for j in range(self._heightV)]

    def _updateSize(self):
        "Not the best way to add the table, but sometimes necessary"
        self._heightV=len(self._activebasevalues)
        if self._heightV:
            self._widthV=len(self._activebasevalues[0])
        else:
            self._widthV=0

    def addPossibleValues(self,values):
        "Add a possible value in the dict"
        if len(values)!=1:
            for value in values:
                self.addPossibleValues([value])
            return
        value=values[0]
        if value in self._listPossibleValues:
            wprint("Value {} is already in the dictionnaty of possible values")
            return False
        else:
            self._listPossibleValues[value]=self.__maxV
            self.__maxV*=2
            return True

    # def makeAssociationTable(self):
    #     "Make a table to contain all associations"
    #     self.statusList=statusList
    #     self.maxStatus=max(self.statusList.values())
        # for status in range(self.maxStatus*2-1):
        #     self.statusAssociation[status]=default
    # def addAssociation(self,status,color):
    #     "Add an association of status and color, must be used after makeAssociationTable"

    def listStatus(self):
        "Return the list of all values"
        return self._listPossibleValues

    def newChangedValues(self):
        "Copy the values of the active values into the changeValues"
        for i,j in self.allIndexes():
            self._changedbasevalues[i][j]=self._activebasevalues[i][j]

    ####################
    # Page Changes
    def changePage(self,page):
        "Try to change page, warning all pending changes will be lost"
        try:
            self._activebasevalues=self._basevalues[page]
            self.newListChanges()
            self.newChangedValues()
            self._redrawPageChange(self._page,page)
            self._page=page
        except KeyError as e:
            eprint("Can't set active page to ({})".format(page))
            print(e)

    def _redrawPageChange(self,page1,page2):
        "Add each different value between the two pages to the list of redraw"
        if page1==page2: # Do nothing
            return
        for i,j in self.allIndexes():
            if self._changedbasevalues[i][j]!=self._activebasevalues[i][j]:
                self.addChange((i,j))

    ####################
    # Manage attributes
    def fullRedraw(self,redrawAll=False):
        "Redraw every changed value"
        if redrawAll: # Trigger a full redraw of everything
            for i,j in self.allIndexes():
                self.addChange((i,j))
            return
        for i,j in self.allIndexes():
            if self._changedbasevalues[i][j]!=self._activebasevalues[i][j]:
                self.addChange((i,j))

    ####################
    # Modifiers methods

    def statusId(self,namestatus):
        "Return the id of a state"
        if type(namestatus) in (list,tuple):
            if len(namestatus)>=1:
                return self.statusId(namestatus[0])|self.statusId(namestatus[1:])
            return 0
        return self._listPossibleValues[namestatus]

    # def addStatus(self,linecol,status):
    #     "Add a status by name to a position"
    #     self.addStatusId(linecol,self.statusId(status))

    def addStatus(self,linecol,*statuses):
        "Add a list of statuses by name to a position"
        # if type(statuses)==str:
        #     self.addStatusId(linecol,self.statusId(statuses))
        for status in statuses:
            self.addStatusId(linecol,self.statusId(status))


    def removeStatus(self,linecol,*liststatus):
        "Remove a list of status, by name"
        for status in liststatus:
            self.removeStatusId(linecol,self.statusId(status))

    def addStatusId(self,linecol,statusId):
        "Add a status by name to a position"
        self.addChange(linecol)
        self._changedbasevalues[linecol[0]][linecol[1]]|=statusId

    def removeStatusId(self,linecol,statusId):
        "Remove a status by name to a position ONLY WORK WITH 1bit"
        self.addChange(linecol)
        if (self._changedbasevalues[linecol[0]][linecol[1]]&statusId):
            self._changedbasevalues[linecol[0]][linecol[1]]-=statusId

    def hasStatus(self,statusId):
        "Check if a status is present"
        if (self._changedbasevalues[linecol[0]][linecol[1]]&statusId):
            return True
        return False
    ####################
    # Value Access methods
    def addChange(self,linecol):
        "Add a change to be acted"
        self._changes.add(linecol)

    def listChanges(self):
        "Yield the list of position to be updated"
        for change in self._changes:
            yield change

    def newListChanges(self):
        "Add a new list of changes"
        self._changes=set()

    def applyChanges(self):
        "Apply all changes and erase them, then reload another _changedbasevalues"
        for i,j in self.listChanges():
            self._activebasevalues[i][j]=self._changedbasevalues[i][j]
        #self.newListChanges()

    def colorFrom(self,linecol):
        "Obtain color from the linecol"
        return (self.possibleStatus[self.getTableElt(self._activebasevalues,linecol)])

    def posToNote(self,linecol):
        return self.noteFrom(linecol)

    def noteFrom(self,linecol):
        "Obtain note from the linecol"
        return self.getTableElt(self._posToNote,linecol)

    ######################
    # Table utilities
    def getTableElt(self,table,linecol):
        "Get an element from a table, either _line or _basevalues"
        return table[linecol[0]][linecol[1]]

    def getTableLine(self,table,line):
        "Get a line from a table"
        return table[line]

    def getTableColumn(self,table,col):
        "Get a column from a table"
        return [table[i][col] for i in range(len(table))]

    def setTableElt(self,table,linecol,val):
        "Set an element in a table (No notifications)"
        table[linecol[0]][linecol[1]]=val

    def setTableLine(self,table,line,value):
        "Change a line in a table (No notifications) (no copy())"
        table[line]=value

    def setTableColumn(self,table,col,values):
        "Change a column to a specific list of values (No notifications)"
        for i in range(len(values)):
            table[i][col]=values[i]


    ####################
    # Operator definitions

    ####################
    # I/O Utilities
    def allIndexes(self):
        "Yield all (x,y) tuples of positions for the active table"
        for i in range(self._heightV):
            for j in range(self._widthV):
                yield (i,j)

    def __repr__(self):
        "Give a small representation of the handler"
        return 'midiPageHandler@{} ({})({}x{})'.format(id(self),self._page,self._heightV,self._widthV)

    def prettyPrint(self,table=None):
        "Give a nice print"
        lineM='[{:3}] '*self._widthV
        sep = "*"+'------'*(self._widthV)+"*"
        if table==None:
            table=self._activebasevalues
        print(sep)
        print('   '+self.__repr__())
        print(sep)
        for line in table:
            if type(line[0])==int:
                print(" "+lineM.format(*line))
            else:
                print(sep)
                for elt in line:
                    print(" "+lineM.format(*elt))
        print(sep)


class pulseRackController(object):
    """Receive controls over a specific range and map them to commands to send"""
    def __init__(self,returnInterface,ranges={j:j for j in range(3)}):
        self.ranges=ranges
        self.returnRanges={i:j for j,i in ranges.items()}
        self.lineNames=["Layer1","Layer2","MasterMemory"]#"Commands"
        self.returnByName={i:j for i,j in zip(self.lineNames,ranges.values())}
        self.realByName={i:j for i,j in zip(self.lineNames,ranges.keys())}
        _ALL_MESSAGE_TYPES=[
            "STATUS","LAYERINP","TAKE","TAKEALL","LOADMM","QUICKF"
        ]
        self.returnInterface=returnInterface
        self.output=None
        self.poslastpressed=(0,0)
        self.idlastlayerpressed=[0,0] # Live/Prev
        self.lastlayerpressed=[[0,0],[0,0]] # Live/preview : Layer1,Layer2
        self.idlastmemorypressed=0
        self.offset=0   # Offset on the lines

    def initColorLines(self):
        "Give an initial color the base lines"
        for line in self.returnRanges.values():
            for col in range(8):
                self.returnInterface.addStatus((line,col),"Inactive")
        self.returnInterface.applyChanges()
        self.returnInterface.applyColors()

    def pressReceived(self,linecol,val):
        """Received an order from the controller, the order must be associated 
        with an actual command and send it to the IOController"""
        try:
            line,col=linecol
            trueline=self.ranges[line]
            if trueline==0: # It's a press on layer A
                self.sendLayerInp(0,1,trueline+1,col+1)
                # print("L1")
            elif trueline==1: # It's a press on layer B
                self.sendLayerInp(0,1,trueline+1,col+1)
                # print("L2")
            elif trueline==2: # It's a memory press
                self.sendMemoryChange(col,1) # MEMORY TO PREVIEW
                # print('MM')
            # elif trueline==3: # It's a livememorypress
            #     # @doublepress 
            #     self.sendMemoryChange(col,0)
            # elif trueline==3:
            #     self.specialPress(trueline,col)
            else:
                pass # The pulse only takes 3 lines
        except KeyError as e:
            wprint("An error occured while the pulse rack module was processing order",e)

    def receiveCommand(self,command,match,*args,**kwargs):
        "Received a command from the external program"
        dprint("Received a command from the external program",command,match)
        if command=="LAYERINP":
            self.receiveLayerInp(match)
        elif command=="DETECTED":
            self.receiveDetected(match)

    def specialPress(self,line,col):
        "Press on the special line"
        # _SPECIAL_COLONS={
        #     0:black1,
        #     1:black2,
        #     3:freeze1,
        #     4:freeze2,
        #     6:takeAll,
        # }
        # if col==0: # It's a black1
        #     pass
        # elif col==1: # It's a black2
        #     pass
        # elif coll=3: # It's a 
        # elif col==6: # It's a Freeze
        #     pass
        # elif col==7:
        #     pass

    def sendLayerInp(self,screen,liveprev,layer,idinput):
        """Send a message to the pulse: Layer input change
            screen: 0
            liveprev: 0 Live / 1 Prev
            layer: 0(Frame) 1Pip1 2Pip2
            idinput: 0(Black) 1Input1 etc..
        """
        self.returnInterface._IOInterface.toExternalProgram("LAYERINP",screen,liveprev,layer,idinput) 
        self.returnInterface._IOInterface.toExternalProgram("SCRNUPD")

    def receiveLayerInp(self,match):
        "Received a message from the Pulse: Layer input was changed"
        screen,ProgPrev,layer,src=[int(i) for i in match.group("postargs").split(",")]
        theorical_line=layer-1 # The line it should be if it was indexed at 0
        # dprint("LIVEPREV",screen,ProgPrev,theorical_line,src)
        if theorical_line not in (0,1) or screen!=0 or ProgPrev not in (0,1):
            return
        self.idlastlayerpressed[ProgPrev]=theorical_line
        realline=self.returnRanges[theorical_line] # The actual line on the handler
        realsrc=src-1
        if ProgPrev==1:
            color="Selected"
        elif ProgPrev==0:
            color="Live"
        else:
            color=None
        #dprint("INPUT {src} is {st}({color}) on {scr}".format(src=src,st=ProgPrev,color=color,scr=layer))

        self.returnInterface.removeStatus((realline,self.lastlayerpressed[ProgPrev][theorical_line]),color)
        if realsrc!=-1: 
            self.returnInterface.addStatus((realline,realsrc),color)
        else:
            realsrc=0 # It's a black input
        self.lastlayerpressed[ProgPrev][theorical_line]=realsrc
        
        self.returnInterface.applyChanges() 
        self.returnInterface.applyColors()

    def receiveDetected(self,match):
        "An input is detected on a position, update the controller"
        src,plugtype,status=match.group("postargs").split(",")
        dprint("An input is detected by the handler Layer:{},plugtype:{},status:{}".format(src,plugtype,status))
        if status=='1':
            for i in range(2):
                self.returnInterface.addStatus((self.returnRanges[i],int(src)),"Active")
        elif status=="0":
            for i in range(2):
                self.returnInterface.removeStatus((self.returnRanges[i],int(src)),"Active")
        self.returnInterface.applyChanges()
        self.returnInterface.applyColors()


    def sendMemoryChange(self,memory,liveprev):
        """Adjust the color and info of a memory press (take or preview)
        Should be Green if defined and Yellow if not, selecting makes it prev
        screenF,memory,screenT,ProgPrev,filter
        """
        self.returnInterface._IOInterface.toExternalProgram("LOADMM",0,memory,0,liveprev,0)

    def __repr__(self):
        return("PulseRackController{} ({self.idlastlayerpressed},{self.idlastmemorypressed})".format(list(self.ranges.keys()),self=self))

class AkaiAPCMini(midiPageHandler):
    "A specific implementation of the page handler"

    def __init__(self):
        super(AkaiAPCMini,self).__init__([[i+(7-j)*8 for i in range(8)] for j in range(8)]+[[i for i in range(64,72)],[i for i in range(82,90)]])
        # Add the two control lines
        self.initValues()

        self.colors={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}
        self.addPossibleValues(("Inactive","Active","Selected","Live"))
        _INACTIVE,_ACTIVE,_LIVE,_SELECTED=self.statusId("Inactive"),self.statusId("Active"),self.statusId("Live"),self.statusId("Selected")

        self.possibleStatus={
            0:                          self.colors["black"],
            _INACTIVE:                  self.colors["yellow"],
            _ACTIVE:                    self.colors["green"],
            _LIVE:                      self.colors["red"],
            _SELECTED:                  self.colors["black"], # Selecting empty does nothing

            _INACTIVE|_SELECTED:        self.colors["blinking_yellow"],
            _ACTIVE|_SELECTED:          self.colors["blinking_green"],
            _LIVE|_SELECTED:            self.colors["blinking_red"],

            _ACTIVE|_LIVE:              self.colors["red"],
            _INACTIVE|_LIVE:            self.colors["red"], # Debatable

            _ACTIVE|_INACTIVE:          self.colors["green"],#Just active

            _ACTIVE|_LIVE|_SELECTED:    self.colors["blinking_red"],
            _ACTIVE|_INACTIVE|_LIVE:    self.colors["red"], #Just live active
            _ACTIVE|_INACTIVE|_SELECTED:self.colors["blinking_green"], #Just selected active
            _INACTIVE|_LIVE|_SELECTED:  self.colors["blinking_red"], # Very debatable

            _ACTIVE|_LIVE|_INACTIVE|_SELECTED:self.colors["blinking_red"] #Just live active selected
        }

        self.listModules=[[None]*8] # Only one page and 8x8 for now
        
        ###########
        # For debug purposes coloring all neutral to be able to skip initialisation
        # for j in range(5):
        #     for i in range(8):
        #         self.addStatus((j,i),"Inactive")
        
        # for j in range(8):
        #     for i in range(8):
        #         self.addStatus((j,i),None)

    def noteReceived(self,note,val):
        line,col=self._noteToPos[note]
        try:
            self.listModules[self._page][line].pressReceived((line,col),val)
        except AttributeError as e:
            wprint("No module loaded for Line {line}: {e}".format(line=line,e=e))
            wprint("List of modules available on page {page} is : {modules}".format(page=self._page,modules=self.listModules[self._page]))

    def addModule(self,rackmodule,rangeActive):
        "Add a module to the controller, the range of control must be specified"
        module=rackmodule(self,{i:j for i,j in zip(rangeActive,range(len(rangeActive)))})
        for i in rangeActive:
            self.listModules[self._page][i]=module
        return module

    def addInterfaceOut(self,interfaceOut):
        "Add one interface to send midi messages to, could be done another way"
        self.output=interfaceOut
        self.applyChanges()
        self.applyColors()

    def applyColors(self):
        'Apply all the colorchanges'
        for note,val in self.listNoteChanges():
            self.lightnote(note,val)

    def lightcolor(self,col,row,color):
        self.light(col,row,val=_COLORS[color])

    def light(self,col,row,val=1):
        self.lightnote(self.findit(col,row),val)

    def lightnote(self,note,val=1):
        self.output.send(mido.Message("note_on",note=note,velocity=val))

    # def receiveAction(self,action,*args,**kwargs):
    #     "Receive an action from the pulse and transmit it to the handler"
    #     dprint("ACTION TO BE HANDLED",action,args,kwargs)
        # Do the changing of the light if layer press etc.
        # Only hard part is knowing where

_TEST=True
if __name__ == '__main__':
    ak=AkaiAPCMini()
    ak.prettyPrint(ak._posToNote)

    for i,v in ak._listPossibleValues.items():
        print("{}:{:b}".format(i,v))
    ak.addStatus((2,1),"Active","Selected","Live")
    ak.addStatusId((5,5),ak.statusId("Active"))
    ak.addStatusId((5,5),ak.statusId("Selected"))
    ak.addStatusId((5,7),ak.statusId("Live"))
    ak.prettyPrint(ak._changedbasevalues)
    ak.prettyPrint(ak._activebasevalues)
    ak.applyChanges()
    ak.prettyPrint(ak._activebasevalues)
    ak.removeStatusId((2,1),ak.statusId("Active"))
    ak.prettyPrint(ak._changedbasevalues)
    ak.removeStatusId((2,1),ak.statusId("Selected"))
    ak.prettyPrint(ak._changedbasevalues)
    ak.removeStatusId((2,1),ak.statusId("Live"))
    ak.prettyPrint(ak._changedbasevalues)
    ak.removeStatus((5,5),"Active","Selected")
    ak.prettyPrint(ak._changedbasevalues)

    print(ak.statusId(("Active","Selected","Live")))

    ak.addStatus((3,3),"Active")
    ak.addStatus((3,3),"Active")
    ak.removeStatus((3,3),"Active")
    ak.removeStatus((3,3),"Active")
    ak.addStatus((3,3),"Active","Selected")
    ak.removeStatus((3,3),"Active")
    ak.addStatus((3,3),"Active","Live")
    ak.removeStatus((3,3),"Live")
    ak.prettyPrint(ak._changedbasevalues)
    ak.prettyPrint(ak._activebasevalues)
    ak.applyChanges()
    ak.prettyPrint(ak._activebasevalues)
    print(ak._changes)

    for note,val in ak.listNoteChanges():
        print (note,val)
    print(ak.colorFrom((3,3)),ak.noteFrom((3,3)))