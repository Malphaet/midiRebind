###########################
# IMPORTS

###########################
# FUNCTION DEFINES

_VERBOSE=4

nopeF=lambda x:None
def printL(label=""):
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

class midiPageHandler(self):
    "Page Handler, with some methods to manage a midi remote more easily"

    def __init__(self,noteArray,control):
        """The noteArray contains a list of virtual lines and the corresponding notes"""
        self._modifier=[]
        self._basevalues=[]

        self._activemodifier=[]
        self._activebasevalues=[]
        self._changes=[]
        self._listPossibleValues={"none":0x0}
        self._page=0

    def addPossibleValue(self,value):
        "Add a possible value in the dict"

    def __call__(self,page,linecol):
        "Return the value of the table at the active linecol & page"
        v1=getTableElt(self._basevalues[page],linecol)
        v2=getTableElt(self._modifier[page],linecol)
        if len(linecol)==1 or linecol[1]==None:
            return [v1[i]|v2[i] for i in range(len(v1))]
        return v1|v2

    def changePage(self,page):
        "Try to change page"
        try:
            self._activemodifier=self._modifier[page]
            self._activebasevalues=self._basevalues[page]
            self.fullRedraw(self.page,page)
            self._page=page
        except KeyError as e:
            eprint("Can't change active page to ({})".format(page))
            print(e)

    def fullRedraw(self):
        "Add each different value between the two pages to the list of redraw"
        for i in range(self._modifier):
            for j in range(self._modifier):
                if self._activelines

    def changeBaseValues(self,linecol,val):
        """Change the base values and add a notice
        Usually one of the base states, not a modifier"""

    def changeModifiers(self,linecol,val):
        "Add a modifier to a position, add a notice if changed"


    def addChange(self,linecol):
        "Add a change to be acted"

    def listChanges(self):
        "Yield the list of position to be updated"

    def getTableElt(self,table,linecol):
        "Get an element from a table, either _line or _basevalues"
        if len(linecol)==1: # Return a specific line
            return table[linecol[0]]
        if linecol[0]==None: # Return a single column, pretty awkward
            return [table[i][linecol[1]] for i in range(len(table))]
        if linecol[1]==None: # Return a single line
            return table[linecol[0]]
        return table[linecol[0],linecol[1]]

    def setTableElt(self,table,linecol,value):
        "Set an element in a table, DOEN'T NOTIFIES"

    def __getelement__(self,linecol):
        "Obtain the value associated with a position"




    def __setelement__(self,linecol,setas):
        "Element"
        if len(linecol)==1 or linecol[1]==None: #Replace an entire line
            self._lines[linecol[0]]=setas
            self._lastchange=[]
