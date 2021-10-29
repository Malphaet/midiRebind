#!/bin/python
# Mini debugging tool, will get his own project at some point


__DEBUG_LISTING={}
######################
# The listing is supposed to be composed of :
# DEBUG[MODULE][SCOPE][FUNCTIONS]=(usage,cputimeused)

def debugListing(function,scope=None):
    "Add a function to the debug listing, on a custom category"
    _name,_usage=function.__name__,0
    __DEBUG_LISTING[_name]=[_usage,0]
    def returnFunction(*args,**kwargs):
        _usage+=1
        __DEBUG_LISTING[_name]=[_usage,0]
        function(*args,**kwargs)
    return returnFunction
