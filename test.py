from minitest import minitest
#from mapping import GrandMA2

allTests=minitest.testGroup("Nominal test units",verbose=True,align=50)

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
        testD=["34","25 34","3 4 5 6 34 255"]
        sucess=1
        for X,D in zip(testX,testD):
            #print("{} / {} : {} [{}]".format(X,D,self.toDec(X),D==self.toDec(X)))
            if self.toDec(X)!=D:
                self.addFailure("Can't convert Hex to Dec")
                sucess=0
                break
        if sucess:
            self.addSuccess()

        #I'm ifnoring the None case on purpose because I can't be bothered with, if it fails, it might as well fail big
        self.currentTest("Test with ill-formed message")
        if self.testParse("22 12"):
            self.addFailure("The message is not supposed to be parsed")
        else:
            self.addSuccess()

        self.currentTest("Test with well-formed message")
        msg=self.toDec("F0 7F 7F 02 7F 01 32 31 2E 35 30 30 F7")
        if self.testParse(msg):
            self.addSuccess()
        else:
            self.addFailure("Can't parse the message {}".format(msg))

        self.currentTest("Checking sanity of parse")
        di=(self.parser(msg).groupdict())
        inc=""
        if di["command"]!="1":
            inc="command "
        if di["data"]!="50 49 46 53 48 48":
            inc+="data "
        if di["deviceid"]!="127":
            inc+="deviceid "
        if di["commandformat"]!="127":
            inc+="commandformat"
        if inc=="":
            self.addSuccess()
        else:
            self.addFailure("Incorrect fields: "+inc[:-1])

        self.currentTest("Testing Config")
        try:
            self.act=GrandMA2.Action("patch/default.ini")
            self.addSuccess()
        except IOError:
            self.addFailure("Can't load config file")

        self.currentTest("Testing the formatter")
        try:
            setsect=self.act.format("set","1","1")
            try:
                self.act.format("set","2","3")
                self.addFailure("Not supposed to load page 3")
            except:
                try:
                    self.act.format("fire","2","11")
                    self.addSuccess()
                except:
                    self.addFailure("Can't acess the fire section")
        except:
            self.addFailure("Can't get (set 1 on page 1)")



    def testParse(self,message):
        try:
            parsed=self.parser(message)
            return True
        except self.gm.MatchError:
            return False
        except:
            self.addCritical("Can't parse (not supposed to happen)")

    def toDec(self,message):
        "Taken care of by mido, but testing needs to be done otherwise"
        res=None
        for hx in message.split(" "):
            if res==None:
                res=str(int(hx,16))
            else:
                res+=" "+str(int(hx,16))
        return res
allTests.addTest(mappingTest())
allTests.test()
