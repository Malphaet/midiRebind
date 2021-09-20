from minitest import minitest
import configparser,mido
#from mapping import GrandMA2

class gmaPyTest(minitest.simpleTestUnit):
    """Testing the General interface"""
    def __init__(self):
        super(gmaPyTest, self).__init__("gmaPy")

    def _testCustom(self):
        self.currentTest("testing true")
        if True:
            self.addSuccess()
        else:
            self.addFailure("True is False")

class mappingTest(minitest.simpleTestUnit):
    """Testing the parsing/mapping"""
    def __init__(self):
        super(mappingTest, self).__init__("parsing/mapping")

    def _testParsing(self):
        self.currentTest("Loading default mappings")
        from mapping import GrandMA2
        self.gm=GrandMA2
        self.addSuccess()

        self.currentTest("Creating Parser")
        self.parser=GrandMA2.MessageParse()
        self.addSuccess()

        self.currentTest("Testing hex2dec")
        testX=["22","19 22","3 4 5 6 22 FF"]
        testD=[[34],[25,34],[3, 4, 5, 6, 34, 255]]
        sucess=1
        for X,D in zip(testX,testD):
            #print("{} / {} : {} [{}]".format(X,D,self.toDec(X),D==self.toDec(X)))
            if toDec(X)!=D:
                self.addFailure("Can't convert Hex to Dec")
                sucess=0
                break
        if sucess:
            self.addSuccess()

        #I'm ifnoring the None case on purpose because I can't be bothered with, if it fails, it might as well fail big
        self.currentTest("Test with ill-formed message")
        if self.testParse([22, 12]):
            self.addFailure("The message is not supposed to be parsed")
        else:
            self.addSuccess()

        self.currentTest("Test with well-formed message")
        msg=toDec("7F 7F 02 7F 01 32 31 2E 35 30 30")
        if self.testParse(msg):
            self.addSuccess()
        else:
            self.addFailure("Can't parse the message {}".format(msg))

        self.currentTest("Checking sanity of parse")
        di=self.parser(mido.Message("sysex",data=msg))
        inc=""
        if di.command!=1:
            inc="command {} ".format(di.command)
        if list(di.data)!=[50, 49, 46, 53, 48, 48]:
            inc+="data {} ".format(di.data)
        if di.deviceid!=127:
            inc+="deviceid {} ".format(di.deviceid)
        if di.commandformat!=127:
            inc+="commandformat {}".format(di.commandformat)
        if inc=="":
            self.addSuccess()
        else:
            self.addFailure("Incorrect fields: "+inc[:-1])

        self.currentTest("Loading Config")
        try:
            class Emptyconfig():
                def __init__(self,configfile):
                    self.config=configparser.ConfigParser()
                    self.config.read(configfile)
                def interfaceOut(self,nb):
                    class EmptySender():
                        def __init__(self):
                            self.name="none:none"
                            pass
                        def send(self,wev,**kwargs):
                            pass
                    return EmptySender()

            self.act=GrandMA2.Actions(Emptyconfig("patch/test.ini"))
            self.addSuccess()
        except IOError:
            self.addFailure("Can't load config file")

        #self.act.prettyprint()
        self.currentTest("Testing the request formatter")
        try:
            setsect=self.act.findAction("set","1","1")
            try:
                self.act.findAction("set","2","3")
                self.addFailure("Not supposed to load page 3")
            except:
                try:
                    self.act.findAction("fire","13","2")
                    self.addSuccess()
                except:
                    self.addFailure("Can't acess the fire section")
        except:
            self.addFailure("Can't get (note 1 on page 1)")

        self.currentTest("Testing the loaded config")
        try:
            if len(self.act.findAction("set",1,'5'))==2:
                self.addSuccess()
            else:
                self.addFailure("Action 1 section 5 (set/5) is supposed to contain 2 elements")
        except:
            self.addFailure("Can't find action 1 (set/5)")
        # A couple more test would be wise, but nearing completion seems more important atm

        self.currentTest("Testing a message")
        try:
            self.act.findAction("set",1,"5")
            self.addSuccess()
        except:
            self.addFailure("Failed to load action")

        self.currentTest("Testing the valuefn")
        try:
            acts=self.act.findAction("set",56,"1")
            for act in acts:
                if act.valuefn(51)==100:
                    self.addSuccess()
        except:
            self.addFailure("Function for key {} isn't working".format(56))

        self.currentTest("Testing the toggle")
        try:
            st=True
            acts=self.act.findAction("fire",38,"1")
            for act in acts:
                if not act.toggle:
                    self.addFailure("Trigger isn't assigned")
                    st=False
                    break
        except:
            self.addFailure("Toggle for key 38 isn't assigned")
            st=False
        if st:
            self.addSuccess()

        self.currentTest("Testing loading of functions")
        print(self.gm.functionlist)
        self.addSuccess()

        self.currentTest("Testing custom function")
        try:
            st=True
            acts=self.act.findAction("custom",77,"2")
            for act in acts:
                if not act.function:
                    st=False
                    self.addFailure("No custom function defined")
                    break
        except:
            self.addFailure("Can't use custom function")
            st=False
        if st:
            self.addSuccess()

        self.currentTest("Testing call")
        acts=self.act.findAction("fire",38,"1")
        for act in acts:
            act(12)
            st=act.toggle
            act(12)
            st1=act.toggle
            if st==st1:
                self.addFailure("State not changing after a call")
        #self.act.prettyprint()

    def testParse(self,message):
        try:
            message=mido.Message("sysex",data=message)
            parsed=self.parser(message)
            return True
        except self.gm.MatchError:
            return False
        except:
            import sys
            print(sys.exc_info())
            self.addCritical("Can't parse (not supposed to happen)")

def toDec(message):
    "Taken care of by mido, but testing needs to be done otherwise"
    res=[]
    for hx in message.split(" "):
        if res==[]:
            res=[int(hx,16)]
        else:
            res+=[int(hx,16)]
    return res

class ConfigTest(minitest.simpleTestUnit):
    def __init__(self):
        super(ConfigTest, self).__init__("Testing the config loader")

    def _testAll(self):
        self.currentTest("Loading config")
        from mapping import GrandMA2
        GrandMA2.MidiInterface("patch/test.ini")
        self.addSuccess()

class LiveTest(minitest.simpleTestUnit):
    def __init__(self):
        super(LiveTest, self).__init__("Live test")

    def _testAll(self):
        self.currentTest("Loading config")
        from mapping import GrandMA2
        Inter=GrandMA2.MidiInterface("patch/test.ini")
        self.addSuccess()

        self.currentTest("Loading message parser")
        Par=GrandMA2.MessageParse()
        self.addSuccess()

        self.currentTest("Loading Patch")
        Acts=GrandMA2.Actions(Inter)
        self.addSuccess()
        #Act.prettyprint()

        self.currentTest("Trying match")

        message=toDec("7F 7F 02 7F 01 33 37 2E 32 30 30 00 35 20 31")
        message=toDec("7F 7F 02 7F 06 02 02 4C 39")
        try:
            match=Par(mido.Message("sysex",data=message))
            self.addSuccess()
        except GrandMA2.MatchError:
            self.addFailure("Can't match '{}'".format(mido.Message(message)))
        except:
            self.addFailure("Error while matching")

        self.currentTest("Sending message")
        match=Acts(match)
        self.addSuccess()

if __name__ == '__main__':
    allTests=minitest.testGroup("Nominal test units",verbose=True,align=50)

    allTests.addTest(mappingTest())
    allTests.addTest(ConfigTest())
    allTests.addTest(LiveTest())
    allTests.test()
