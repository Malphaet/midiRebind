###########################
# IMPORTS

###########################
# FUNCTION DEFINES

_VERBOSE=4

nopeF=lambda x:None
def printl(label=""):
    def _pl(*args):
        print(label,*args)
    return _pl

eprint=printl("[mPH:ERROR]")
dprint=nopeF
ddprint=nopeF
iprint=nopeF
wprint=nopeF
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
        self._changes=set()
        self._listPossibleValues={None:0b0}
        self.__maxV=0b0
        self._page=0
        self._maxpages=pages
        self._maxN=0
        self._makeNotes(table)

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

    def addPossibleValue(self,value):
        "Add a possible value in the dict"
        if value in self._listPossibleValues:
            wprint("Value {} is already in the dictionnaty of possible values")
            return False
        else:
            self.__maxV*=2
            self._listPossibleValues[value]=self.__maxV
            return True

    def newChangedValues(self):
        "Copy the values of the active values into the changeValues"
        for i,j in self.allIndexes():
            self._changedbasevalues[i][j]=self._activebasevalues[i][j]

    ####################
    # Page Changes
    def changePage(self,page):
        "Try to change page"
        try:
            self._activebasevalues=self._basevalues[page]
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
            pass

    ####################
    # Value Access methods
    def addChange(self,linecol):
        "Add a change to be acted"
        self._changes.add(linecol)

    def listChanges(self):
        "Yield the list of position to be updated"
        for change in self._changes:
            yield change

    def applyChanges(self):
        "Apply all changes and erase them, then reload another _changedbasevalues"
        pass

    #####################
    # Value modification methods
    def addModifier(self,linecol,modifier):
        "Add the modifier to the list of pending changes"
        pass

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

class AkaiAPCMini(midiPageHandler):
    "A specific implementation of the page handler"

    def __init__(self):
        super(AkaiAPCMini,self).__init__([[i+(7-j)*8 for i in range(8)] for j in range(8)])
        # Add the two control lines
        self.initValues()
        self._updateSize()
        # self.changePage(0)

if __name__ == '__main__':
    ak=AkaiAPCMini()
    ak.prettyPrint(ak._posToNote)
    # print(ak._posToNote)
    print(ak.getTableElt(ak._posToNote,(5,5)))
    (ak.setTableElt(ak._posToNote,(5,5),66))
    print(ak.getTableElt(ak._posToNote,(5,5)))
    #
    print(ak.getTableLine(ak._posToNote,4))
    (ak.setTableLine(ak._posToNote,4,[i*5 for i in range(8)]))
    print(ak.getTableLine(ak._posToNote,4))

    print(ak.getTableColumn(ak._posToNote,4))
    (ak.setTableColumn(ak._posToNote,4,[i*3 for i in range(8)]))
    print(ak.getTableColumn(ak._posToNote,4))

    # getTableColumn(self,table,col)
