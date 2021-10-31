#!/bin/python3

#################################################
# HARDCODED DEFINITIONS
###

_LIST_VPS=["192.168.0.8"]
__TESTING=False

#################################################
# IMPORTS
###

from src.midiRebind.mapping.base import BasicMidiInterface
import mido
from src.midiRebind.panaremote import request as panarequest

from threading import Timer

#################################################
# GLOBAL UTILITIES
###

class pyautonope(object):
    def __init__(self):
        pass

    def __call__(self,*args,**kwargs):
        return self

    def __repr__(self,*args,**kwargs):
        return ''

    def __getattr__(self,*args,**kwargs):
        return self

class fakeRemote(pyautonope):
    def __init__(self):
        self.st_shutter="Off"
        self.st_osd="Off"
        self.st_input="SDI"

    def shutterOn(self):
        self.st_shutter='On'

    def shutterOff(self):
        self.st_shutter='Off'

    def __getattr__(self,name):
        return self

if __TESTING:
    pyautogui=pyautonope()
    #import pyautogui
    panarequest=fakeRemote()
    def dprint(*args):
        print(*args)
else:
    import pyautogui
    def dprint(*args):
        pass


#################################################
# BASE VARIABLE DEFINITIONS
###

_NOTIMER=pyautonope()
_NOACTION=_NOTIMER

_INACTIVE=0b1
_ACTIVE=0b10
_SELECTED=0b100
_LIVE=0b1000

INPUTS=  [_INACTIVE,_INACTIVE,_ACTIVE,_INACTIVE,_INACTIVE,_INACTIVE,_ACTIVE,_INACTIVE]
MEMORIES=[_ACTIVE,_ACTIVE,_ACTIVE,_ACTIVE,_ACTIVE,_INACTIVE,_ACTIVE,_ACTIVE]

#Modes
_RESET=lambda a,b: a
_OR=lambda a,b: a|b
_XOR=lambda a,b: a^b

_TIMERTAKE=3.0
_BASE_NOTE_INPUT=56
_BASE_NOTE_CTRL=82

_BASEVALUES=[
    INPUTS[:],
    MEMORIES[:],
    [0]*8,
    [0]*8,
    [0]*8,
    [0]*8,
    [0]*8,
    [0]*8
] # The duplicate is actually unimportant

_COLORS={"black":0,"green":1,"blinking_green":2,"red":3,"blinking_red":4,"yellow":5,"blinking_yellow":6}

##
dprint("[Info] Config loading done")

#################################################
# UTILITIES
###

def noteToPos(note):
    i,j=note%8,7-note//8
    vars.lastpress=(i,j)
    return i,j

#################################################
# GLOBAL VARIABLE OBJECT
###
class demvars():
    def __init__(self):
        self.page=0

        self.interface_nb=1
        self.output=None
        self.BASE_NOTE_MASTERM=48   # Marked for deletion
        self.BASE_NOTE_ARM_TAKE=89  # Marked for deletion

        self.listchange=[]
        self.lastpress=(None,None) #Does only account for the 8x8
        self.selected_pulse=(None,None)
        self.live_pulse=(None,None)

        self.list_vp=[]
        self.nb_vp=0
        # self.list_shutter_open=[]

        self.timertake=_NOTIMER
        self._BASEVALUES=[[i for i in _BASEVALUES[j]] for j in range(8)]

        self.INPUTS=self._BASEVALUES[0][:]     # INCREDIBLY UNSAFE
        self.MEMORIES=self._BASEVALUES[1][:]   # INCREDIBLY UNSAFE
        self.PAGE_VALUES=[
            [
                self.INPUTS,
                self.MEMORIES
            ] + [[0]*8 for i in range(6)]
        ]

        self.ACTIVE_VALUES=self.PAGE_VALUES[self.page] # Marked for deletion

        self.takearmed=False
        self.doublepressed_timer={}
        self.doublepressed_prot={}
        #self.COLORPLUGS={0:_COLORS["yellow"],1:_COLORS["green"],2:_COLORS["blinking_green"],3:_COLORS["red"]}
        #_INACTIVE _ACTIVE _SELECTED _LIVE
        self.PLUGCOLORS={
            0:                          _COLORS["black"],
            _INACTIVE:                  _COLORS["yellow"],
            _ACTIVE:                    _COLORS["green"],
            _LIVE:                      _COLORS["red"],
            _SELECTED:                  _COLORS["black"], # Selecting empty does nothing

            _INACTIVE|_SELECTED:        _COLORS["blinking_yellow"],
            _ACTIVE|_SELECTED:          _COLORS["blinking_green"],
            _LIVE|_SELECTED:            _COLORS["blinking_red"],

            _ACTIVE|_LIVE:              _COLORS["red"],
            _INACTIVE|_LIVE:            _COLORS["red"], # Debatable

            _ACTIVE|_INACTIVE:          _COLORS["green"],#Just active

            _ACTIVE|_LIVE|_SELECTED:    _COLORS["blinking_red"],
            _ACTIVE|_INACTIVE|_LIVE:    _COLORS["blinking_red"], #Just live active
            _ACTIVE|_INACTIVE|_SELECTED:_COLORS["blinking_green"], #Just selected active
            _INACTIVE|_LIVE|_SELECTED:    _COLORS["blinking_red"], # Very debatable

            _ACTIVE|_LIVE|_INACTIVE|_SELECTED:_COLORS["blinking_red"] #Just live active selected
        }

        for i in range(_ACTIVE|_LIVE|_INACTIVE|_SELECTED):
            if i not in self.PLUGCOLORS:
                print("[WARNING] : Case {:b} doesn't have a color by default".format(i))
                self.PLUGCOLORS[i]=_COLORS["black"]

    # Should do it in a similar way, cant find it
    def addChange(self,i,j,value,reset=True): #mode=_OR
        "Do a value change, store the change for update"
        if i==None or j==None:
            return
        self.listchange+=[[i,j,value,reset]]

    def applyChanges(self):
        "Apply all changes"
        allch=set()
        for i,j,v,r in self.listchange:
            allch.add((i,j))
            if r:
                self.ACTIVE_VALUES[j][i]=vars._BASEVALUES[j][i]|v    # There must be a way not to use this
                #print("({}:{}) - Action:{} Base:{} Effect:{} Color:{}".format(i,j,v,_BASEVALUES[j][i],_BASEVALUES[j][i]|v,self.PLUGCOLORS[_BASEVALUES[j][i]|v]))
            else:
                self.ACTIVE_VALUES[j][i]|=v
        self.listchange=[]

        for i,j in allch: # I feel like I'm doing this twice
            self.light(i,j,self.PLUGCOLORS[self.ACTIVE_VALUES[j][i]])

        # self.
    def findit(self,col,row):
        "All index start at zero"
        return _BASE_NOTE_INPUT+col-8*row

    def lightcolor(self,col,row,color):
        self.light(col,row,val=_COLORS[color])

    def light(self,col,row,val=1):
        self.lightnote(self.findit(col,row),val)

    def lightnote(self,note,val=1):
        self.output.send(mido.Message("note_on",note=note,velocity=val))

    def updateRange(self,listNotes):
        "Update a list of notes"
        for i,j in listN:
            pass

    def updateinput(self,toupdate=range(8)): # Keep it for now to separate MM from IN just in case
        "Update the inputline"
        for i in toupdate:
            self.light(i,0,self.PLUGCOLORS[self.INPUTS[i]])

    def updatemasterm(self,toupdate=range(8)): # Marked for deletion
        "Update the selected master memory"
        for i in toupdate:
            self.light(i,1,self.PLUGCOLORS[self.MEMORIES[i]])

    def updatevp(self,toupdate=range(8)): #Marked for deletion
        for i in toupdate:
            self.light(i,7,self.PLUGCOLORS[self.ACTIVE_VALUES[7][i]])
#################################################
# ON LOAD ACTIONS
###
vars=demvars()

def _onload(self):
    "Send a reset colors"
    vars.output=self.outputs[vars.interface_nb]
    #Load the remote control on some VPs
    loadVPs(_LIST_VPS)

    # Cleaning the arm
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,2)

    vars.updateinput()
    vars.updatemasterm()
    vars.updatevp()

#################################################
# GLOBAL CONTROL
###

def pressKeys(*keys):
    "Press a key sequence"
    def _action(trigger,i,j,val,*params):
        pyautogui.hotkey(*keys)
    return _action

def controllpress(trigger,val,note,*params):
    "A key was pressed on the control area"
    i=note-_BASE_NOTE_CTRL
    if i==0:
        # pyautogui.hotkey("ctrl","fn","S")
        return
    else:
        # try:
        #     _ACTIONS[vars.page][i+8*j](trigger,i,j,val,*params)
        #     # dprint("[Info] : Action received ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))
        # except TypeError as e:
        dprint("[Error] : Unassigned control ({}) - Note {:2} ({:3})".format(i,note,val))

def pagepress(trigger,val,note,*params):
    "A key was pressed on the pagebuttons area"
    i,j=noteToPos(note)
    try:
        _ACTIONS[vars.page][i+8*j](trigger,i,j,val,*params)
        # dprint("[Info] : Action received ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))
    except TypeError as e:
        dprint("[Error] : Unassigned pagebutton ({}:{}) - Note {:2} ({:3})".format(i,j,note,val))
        dprint(e)

#################################################
# PULSE CONTROL
###

def switchinput(trigger,i,j,val,*params): ## Marked for deletion
    "Switch to the desired layer i1"
    # These two lines could be better done
    vars.lastpress=(i,j)

    vars.addChange(*vars.selected_pulse,0,reset=True) # Reset this to base
    vars.selected_pulse=(i,0)

    vars.addChange(*vars.lastpress,_SELECTED,reset=True) # Add a selection
    vars.addChange(*vars.live_pulse,_LIVE,reset=False)

    vars.applyChanges()
    pyautogui.hotkey("i",str(i+1))

def takeall(trigger,val,note,*params):
    "Take all TA"
    if not vars.takearmed:
        return
    # unarmtake()
    vars.addChange(*vars.live_pulse,0)
    vars.live_pulse=vars.selected_pulse
    vars.addChange(*vars.selected_pulse,_SELECTED|_LIVE)
    vars.applyChanges()

    pyautogui.hotkey("t","a")

def switchmastermemory(trigger,i,j,val,*params): # Marked for deletion
    "Switch to the desired master memory M1"
    vars.lastpress=(i,j)

    vars.addChange(*vars.selected_pulse,0,reset=True) # Reset this to base
    vars.selected_pulse=(i,1)
    vars.addChange(*vars.lastpress,_SELECTED,reset=True) # Add a selection
    vars.addChange(*vars.live_pulse,_LIVE,reset=False)

    vars.applyChanges()
    pyautogui.hotkey("m",str(i+1))


def unarmtake():
    "Unarm the take button"
    # vars.timertake.cancel()
    vars.takearmed=False
    vars.timertake=_NOTIMER
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,2)

def armtake(trigger,val,note,*params):
    "Arm the take button, unarm after a short while"
    vars.timertake.cancel()
    vars.timertake=Timer(_TIMERTAKE, unarmtake)
    vars.takearmed=True
    vars.lightnote(vars.BASE_NOTE_ARM_TAKE,1) # First and only blinking value
    vars.timertake.start()


#################################################
# VIDEOPROJECTOR CONTROL
###
def switchvp(trigger,i,j,val,*params):
    "Gestion of the VP actions"
    # 0-3 VP1 // 4-7 VP2
    vp_i,vp_act=i//4,i%4
    try:
        if vp_act==0: # Opening
            panaOpen([vars.list_vp[vp_i]])
        elif vp_act==1: # Closing
            panaShut([vars.list_vp[vp_i]])
        elif vp_act==2: # Switch
            panaToggle([vars.list_vp[vp_i]])
        else:
            return
        updateVPLights()
        vars.updatevp()
        # print(vars.list_vp)
    except IndexError:
        dprint("[Warning] VP number {} isn't defined".format(vp_i+1))
    except Exception as e:
        print(e)

def loadVPs(listVP):
    "Load the VP list"
    try:
        vars.list_vp=[openVP(VP) for VP in listVP]
        vars.nb_vp=len(vars.list_vp)
        updateVPLights()
        # list_shutter_open=[VP.st_shutter=='On' for VP in vars.list_vp]
        # dprint(vars.list_vp,listVP,vars.nb_vp)
    except Exception as e:
        print("[panaRemote] An unexpected error occured while operating the videoprojector")
        print(e)


def updateVPLights():
    "Update the status of VPs"
    list_shutter_open=[]
    for vp_i in range(min(2,vars.nb_vp)):
        vars.list_vp[vp_i].getStatus()
        status=vars.list_vp[vp_i].st_shutter=='On'
        dprint("[Info] Shutter of VP({}@{}) is {}".format(vp_i,vars.list_vp[vp_i].ip,vars.list_vp[vp_i].st_shutter))
        vars.ACTIVE_VALUES[7][0+4*vp_i]=_ACTIVE     # Might not be a good idea to do it this way
        vars.ACTIVE_VALUES[7][1+4*vp_i]=_LIVE       # Might not be a good idea to do it this way
        vars.ACTIVE_VALUES[7][2+4*vp_i]=_INACTIVE   # Might not be a good idea to do it this way
        if status:
            vars.ACTIVE_VALUES[7][1+4*vp_i]|=_SELECTED
        else:
            vars.ACTIVE_VALUES[7][0+4*vp_i]|=_SELECTED


def deactivate(name,note=None,color=None):
    "Reset the press count of a button"
    def _timedDesactivation():
        # print("Deactivating: ",name)
        vars.doublepressed_timer[name].cancel()
        vars.doublepressed_prot[name]=False
        vars.doublepressed_timer[name]=_NOTIMER
        if note!=None:
            #if color==None: color=BASECOLOR[Note]
            vars.lightnote(note,color)

    return _timedDesactivation

def doublepress(funct):#Note,color vars.lightnote(vars.BASE_NOTE_ARM_TAKE,1)
    "Offer a doublepress protection to a function"
    # print("Building doublepress protection for",funct.__name__)
    vars.doublepressed_prot[funct.__name__]=False
    vars.doublepressed_timer[funct.__name__]=_NOTIMER
    def _doubleProtected(*args,**kwargs):
        if vars.doublepressed_prot[funct.__name__]:
            # print("Launching function",funct.__name__,args,kwargs)
            vars.doublepressed_prot[funct.__name__]=False
            vars.doublepressed_timer[funct.__name__].cancel()
            funct(*args,**kwargs)
        else:
            # print("Launching the timer for",funct.__name__,args,kwargs)
            vars.doublepressed_timer[funct.__name__].cancel()
            vars.doublepressed_timer[funct.__name__]=Timer(_TIMERTAKE, deactivate(funct.__name__))
            vars.doublepressed_prot[funct.__name__]=True
            vars.doublepressed_timer[funct.__name__].start()
    return _doubleProtected

def openVP(adress):
    return panarequest.VP(adress)

@doublepress
def panaShut(listVP):
    for vp in listVP:
        vp.shutterOn()

@doublepress
def panaOpen(listVP):
    for vp in listVP:
        vp.shutterOff()

@doublepress
def panaToggle(listVP):
    for vp in listVP:
        if vp.st_shutter=="On":
            vp.shutterOff()
        elif vp.st_shutter=="Off":
            vp.shutterOn()

dprint("[Info] Function loading done")

#################################################
# ACTION ASSIGNEMENT
#####

_ACTIONS=[
    [_NOACTION]*64
]
def _pos(i,j):
    return i+8*j #_BASE_NOTE_INPUT+8-i-j*8

for i in range(8):
    _ACTIONS[0][i+8*0]=switchinput
    _ACTIONS[0][i+8*1]=switchmastermemory
    _ACTIONS[0][i+8*7]=switchvp
#
# _ACTIONS[0][0+7*8]=panaOpen
# _ACTIONS[0][1+7*8]=panaShut
# _ACTIONS[0][2+7*8]=panaToggle

# _ACTIONS[0][_pos(1,5)]=pressKeys("up")
# _ACTIONS[0][_pos(0,6)]=pressKeys("left")
# _ACTIONS[0][_pos(1,6)]=pressKeys("down")
# _ACTIONS[0][_pos(2,6)]=pressKeys("right")

dprint("[Info] Action loading done")

####################################################
#  INTERFACE DEFINITION
#####

# MidiInterface(config)
class MidiInterface(BasicMidiInterface):
    "Adding a couple of custom functions"

    def __init__(self,configfile):
        super(MidiInterface,self).__init__(configfile)
        _onload(self)
        self.functionlist["pagepress"]=pagepress
        self.functionlist["controllpress"]=controllpress

        # self.functionlist["switchinput"]=switchinput
        # self.functionlist["mastermemory"]=switchmastermemory
        # self.functionlist['vpcontroll']=vpcontroll

        self.functionlist["takeall"]=takeall
        self.functionlist["armtake"]=armtake
