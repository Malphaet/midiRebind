from __future__ import print_function
import urllib3 as urllib
import mido
import threading,time
#import urllib2

import re,sys
try:
    import Tkinter as tk
except:
    import tkinter as tk

_status=threading.Lock()
_waittime=0.7
_username = 'admin1'
_password = 'panasonic'
http = urllib.PoolManager()
headers = urllib.make_headers(basic_auth='{}:{}'.format(_username,_password))
reinp=re.compile('INPUT&nbsp;(?P<np>\w+)')
debug=True

def makeURL(ip,cmd):
    url = 'http://{}/cgi-bin/proj_ctl.cgi?key={}&lang=e&osd=off'.format(ip,cmd)
    return url

def makeSTATUS(ip):
    url='http://{}/cgi-bin/get_osd.cgi?lang=e'.format(ip)
    return url

def openURL(cmd):
    try:
        url=cmd
        r = http.request('GET', url, headers=headers, timeout=2.5)
        return r.data.decode("utf-8")
    except Exception as e:
        if isinstance(e,urllib.exceptions.HTTPError):
            print(" [Error] Can't reach address: {}".format(url),file=sys.stderr)
            print(e)
        return None

def openSTATUS(cmd):
    text=openURL(cmd)
    sh,osd,inp="Off","Off",""
    if text==None:
        return None
    if text.find("SHUTTER ON")>=0:
        sh="On"
    if text.find("ON SCREEN ON")>=0:
        osf="On"
    inp=reinp.search(text).groups()[0]
    return sh,osd,inp

def dprint(st):
    if debug:
        print(st,file=sys.stderr)

ip="192.168.0.8"
shutter_on=makeURL(ip,"shutter_on")
shutter_off=makeURL(ip,"shutter_off")
status=makeSTATUS(ip)

class VP(object):
    """Class to acess a VP."""
    def __init__(self, ip):
        super(VP, self).__init__()
        self.ip = ip
        print("Initialing {}".format(ip),file=sys.stderr)
        self.st_shutter=None
        self.st_osd=None
        self.st_input=None
        self.shutter_on=makeURL(ip,"shutter_on")
        self.shutter_off=makeURL(ip,"shutter_off")
        self.status=makeSTATUS(ip)
        self.requesting=False
        self.getStatus()
        if self.st_shutter==None:
            print(" [{}] Unreachable".format(ip),file=sys.stderr)
        else:
            print(" [{}] Connected".format(ip),file=sys.stderr)

    def shutterOn(self):
        _status.acquire()
        s=openURL(self.shutter_on)
        time.sleep(_waittime)
        if s!=None:
            self.st_shutter='On'
        _status.release()

    def shutterOff(self):
        _status.acquire()
        s=openURL(self.shutter_off)
        time.sleep(_waittime)
        if s!=None:
            self.st_shutter='Off'
        _status.release()


    def getStatus(self):
        _status.acquire()
        try:
            stat=openSTATUS(self.status)
        except AttributeError as e:
            print("[PRM:ERROR] Can't get status of vp",str(self))
            stat=None

        if stat==None:
            stat=None,None,None
        self.st_shutter,self.st_osd,self.st_input=stat
        _status.release()
        return stat

    def __str__(self):
        return self.ip

    def strStatus(self):
        if self.st_osd!=None:
            return 'OSD: {} - INPUT: {}'.format(self.st_osd,self.st_input)
        else:
            return 'Host: {} OFFLINE'.format(self.ip)

if __name__ == '__main__':
    try:
        cmd=sys.argv[1]
        if cmd=="on":
            openURL(shutter_on)
        elif cmd=="off":
            openURL(shutter_off)
        elif cmd=="status":
            print('Shutter: {}\nOSD: {}\nINPUT: {}'.format(*openSTATUS(status)))
    except:
        openURL(shutter_off)
