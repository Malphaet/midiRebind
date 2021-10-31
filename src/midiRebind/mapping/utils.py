#!/bin/python

from threading import Timer

################
# Print Functions

##############
#Classes

class emptyClass(object):
    def __init__(self):
        pass

    def __call__(self,*args,**kwargs):
        return self

    def __repr__(self,*args,**kwargs):
        return ''

    def __getattr__(self,*args,**kwargs):
        return self

class emptyVars():
    def __init__(self):
        self.doublepressed_timer={}
        self.doublepressed_prot={}
        
    def lightnote(self,note,val):
        "Note to light"
        print("Should light",note,val)
################
# Decorators

__DEFAULT_VARS=emptyVars()

def doublepress(funct,vars=__DEFAULT_VARS):#Note,color vars.lightnote(vars.BASE_NOTE_ARM_TAKE,1)
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

def deactivate(name,note=None,color=None,vars=__DEFAULT_VARS):
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

##############
# Definitions
_NOTIMER=emptyClass()
_EMPTYVARS=emptyVars()
_TIMERTAKE=5