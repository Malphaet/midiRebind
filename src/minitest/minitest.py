#!/usr/bin/env python

# Copyleft (c) 2016 Cocobug All Rights Reserved.
try:
    from blessings import Terminal
except:
    class Terminal():
        "Just output empty strings"
        def __init__(self):
            pass
        def __repr__(self):
            return ""
        def __eq__(self,ot):
            return False
        def __str__(self):
            return ""
        def __getattr__(self,attr):
            return Color()

    class Color():
        def __init__(self):
            pass
        def __str__(self):
            return ""
        def __call__(self,attr):
            return attr
        def __getattr__(self,attr):
            return attr


import types,string,traceback,sys

__all__ =["testGroup","testUnit"]

SUCCESS_STATUS=1
FAILURE_STATUS=2
WARNING_STATUS=4
CRITICAL_STATUS=8

class testCoreOutOfTests(IndexError):
    pass

class testGroup(object):
    """TestGroup, group a number of testUnit, exec them and print the results"""
    def __init__(self,name="",terminal=None,prefix="",verbose=False,align=0):
        self._tests=[]
        self.name=name
        self.t=terminal
        self.prefix=prefix
        (self.t)
        if self.t==None:
            self.t=Terminal()
        self.results=[]
        self.status_modules={
            "success":0,
            "total":0,
            "warning":0,
            "critical":0,
            "failure":0
        }
        self.success_text= self.t.green("success")
        self.failure_text=self.t.bright_red("failure")
        self.warning_text=self.t.bright_yellow("warning")
        self.critical_text=self.t.white_on_red("critical")
        self.verbose=verbose
        self.align=align


    def addTest(self,testUnit):
        self._tests.append(testUnit)
        return self

    def test(self):
        "Execute all tests, some options might exist at some point"
        module_success,module_total=0,0

        print(self.prefix+"+ Executing test group "+self.pretty_group(self.name))
        oldprefix=self.prefix
        self.prefix+="|  "
        self.results=[]

        for test in self._tests:
            try:
                list_status,total,log_results=self.print_result(test.test())
            except Exception as e:
                print(self.t.bright_red("[ERROR] An unhandled error occured during the execution of the tests"))
                raise(e)
                # for l in e:
                #     print(l)
                list_status,total,log_results=self.print_result([])

            print(self.pretty_subtests(test.name,list_status,total))

            if list_status["success"]+list_status["warning"]==total:
                self.status_modules["success"]+=1
            self.status_modules["total"]+=1
            for log in log_results:
                print(log)
            self.results.append([self,SUCCESS_STATUS,""])
        self.prefix=oldprefix

        print(self.pretty_group_result(self.status_modules,self.status_modules["total"]))
        return self.results

    def get_status(self):
        "Get the status of every module, if no test was run, should return an empty dict"
        return self.status_modules

    def print_result(self,table):
        "Get the array of success/failures and print according to the options (still none yet)"
        total=len(table)
        success=0
        results_array=[]
        nb=0
        list_status={
            "success":0,
            "failure":0,
            "warning":0,
            "critical":0
        }
        for item,status,infos in table:
            nb+=1
            if status==SUCCESS_STATUS:
                list_status["success"]+=1
            elif status==WARNING_STATUS:
                list_status["warning"]+=1
            elif status==CRITICAL_STATUS:
                list_status["critical"]+=1
            else:
                list_status["failure"]+=1
            if self.verbose or status!=SUCCESS_STATUS:
                results_array.append(self.pretty_result(status,nb,item,infos))
        return list_status,total,results_array


    def pretty_group_result(self,module_status,total):
        "Prettyfying the result of the batch of tests"
        bloc=self.prefix+"+ Done "
        return bloc+self.pretty_group(self.name)+self.pretty_dots(bloc,len(self.name))+self.pretty_successrate(module_status,total)

    def pretty_name(self,item):
        "Just a pretty way of showing the name of a test"
        try:
            return item.__name__.strip("<>")
        except:
            return str(item)

    def pretty_subtests(self,name,success,total):
        "Pretty way of showing the result of the group of tests"
        bloc=self.prefix+"testing "+ self.pretty_test(name)
        return bloc+self.pretty_dots(bloc)+self.pretty_successrate(success,total)

    def pretty_result(self,status,nb,item,infos):
        "Just a pretty way of showing the result of one test"
        bloc=self.prefix+" * "+" ["+str(nb)+"] "+self.pretty_name(item)
        if status==CRITICAL_STATUS:
            pbloc=self.prefix+" * "+" ["+str(nb)+"] "+self.t.bold_bright_red(self.pretty_name(item))
        else:
            pbloc=bloc
        return pbloc+self.pretty_dots(bloc)+self.pretty_status(status)+self.pretty_info(infos)

    def pretty_dots(self,bloc,padding=0):
        lenbloc=len(bloc)+padding
        if (self.align>lenbloc+2):
            dots="."*(self.align-lenbloc)
        else:
            dots=".."
        return dots

    def pretty_info(self,infos):
        "Prettyfy the additional infos"
        if infos=="":
            return ""
        return self.t.italic(" ("+str(infos)+")")

    def pretty_status(self,status):
        "Prettyfy the status of the test"
        if status==SUCCESS_STATUS:
            return self.success_text
        elif status==FAILURE_STATUS:
            return self.failure_text
        elif status==WARNING_STATUS:
            return self.warning_text
        else:
            return self.critical_text

    def pretty_group(self,name):
        "Prettify the name of the testGroup"
        return self.t.bold(name)

    def pretty_test(self,test):
        "Prettify the name of the testUnit"
        return test

    def pretty_successrate(self,success,total):
        warnings=""
        if success["success"]==total:
            wrap=self.t.green
            txt=self.success_text
        elif success["success"]+success["warning"]==total:
            wrap=self.t.yellow
            txt=self.warning_text
            warnings=" ({} warnings)".format(str(success["warning"]))
        elif success["critical"]!=0:
            wrap=self.t.white_on_red
            txt=self.critical_text
        else:
            wrap=self.t.bright_red
            txt=self.failure_text
        return wrap(txt+" ["+str(success["success"]+success["warning"])+"/"+str(total)+"]"+warnings)

    def __str__(self):
        return self.name

class testUnit(object):
    """A very basic test unit, only test() is mandatory
        test(): should return a list of [function,status,infos]
        Function added as test should raise error if incorect (assert is your friend),
            you can customise the test unit in any way that the field info become actually informative
        The whole class can (should) be modified to hold the test environement
        """
    def __init__(self,name):
        "The name if the name of the group of test executed"
        self._tests=[]
        self.name=name
        self.results=[]
        self.verbose=False

    def __str__(self):
        return self.name

    def addTest(self,test):
        "Add a function to the test unit"
        self._tests.append(test)
        return self

    def test(self):
        "Execute all tests"
        self.results=[]
        for test in self._tests:
            try:
                test()
                self.addResult(test,SUCCESS_STATUS,'')
            except Exception as e:
                self.addResult(test,FAILURE_STATUS,e)
        return self.results

    def addResult(self,testName,status,info):
        self.results.append([testName,status,info])

class simpleTestUnit(testUnit):
    """Very simple test function, it tries to autodetect tests and add them and batch test them,
    this is not default behavior and should not be expected from other functions
    The very usage of this self.list_ongoing_tests makes the class non embetted effect protected and non-thread-friendly
    Note that using list_ongoing_tests and addResult together can lead to unpredictable results, use addSuccess and addFailure instead"""

    def __init__(self,name):
        super(simpleTestUnit, self).__init__(name)
        self.results=[]
        self.list_ongoing_tests=[]
        self.userTests=[]
        self._simpleTestList=[]

    def currentTest(self,name=None,nonDestructive=False):
        """Set the current test by calling it with an argument or get it with no arguments or None (this is a malpractice and I don't care)
        When using the nonDestructive tag don't forget to actually finish the test at some point, consider never using it"""
        if name==None:
            try:
                if nonDestructive:
                    return self.list_ongoing_tests[-1]
                else:
                    return self.list_ongoing_tests.pop()
            except IndexError:
                raise testCoreOutOfTests
        else:
            return self.list_ongoing_tests.append(name)


    def addSuccess(self,nonDestructive=False):
        "Mark the success of the current test (named in the function by self.currentTest)"
        self.addResult(self.currentTest(nonDestructive=nonDestructive),SUCCESS_STATUS,"")

    def addFailure(self,msg,nonDestructive=False):
        "Mark the failure of the current test"
        self.addResult(self.currentTest(nonDestructive=nonDestructive),FAILURE_STATUS,msg)

    def addCritical(self,name,msg=""):
        self.addResult(name,CRITICAL_STATUS,msg)

    def addWarning(self,msg="",nonDestructive=False):
        self.addResult(self.currentTest(nonDestructive=nonDestructive),WARNING_STATUS,msg)

    def test(self):
        """User can add functions to be tested in userTests,
            the functions should use self.addSuccess() and self.addFailure("") to keep track of the results
            test() will then proceed to autodetect all other tests"""

        self.results=[]
        self._simpleTestList=self.userTests[:]

        for method in dir(self):
            if method.startswith("_test"):
                method=getattr(self,method)
                if isinstance(method,types.FunctionType) or isinstance(method,types.MethodType):
                    self._simpleTestList.append(method)

        try:
            for fonct in self._simpleTestList:
                fonct()
        except testCoreOutOfTests:
            self.criticalTraceback()
        except Exception as e:
            if len(self.list_ongoing_tests)>0:
                if self.verbose==False:
                    self.addFailure(e)
                else:
                    raise e
            else:
                #self.criticalTraceback() #This is an arguable choice
                self.addResult("minitest.py:error",CRITICAL_STATUS,e)

        return self.results

    def criticalTraceback(self):
        exc,funct,tb=sys.exc_info()
        code=tb.tb_frame.f_code
        self.addCritical("minitest.py:critical","fatal error {} line {} ({}@{})".format(exc.__name__,code.co_firstlineno,code.co_name,code.co_filename))
        # #print(traceback.extract_stack()[0])
        # # print(stack.name)
        # for stack in traceback.extract_stack():
        #     # print(dir(frame))
        #     self.addCritical("core:critical","{} line {} ({})".format(stack.name,stack.lineno,stack.filename))
if __name__ == '__main__':
    term=Terminal()
    mainClasses=testGroup("Main Classes",term,verbose=True,align=40)
    subclass=testGroup("Subgroup",term,"| ",verbose=True,align=40)

    mainTest=testUnit("lambda functions")
    mainTest.addTest(lambda :True)
    mainTest.addTest(lambda :True)
    lambdaTest=testUnit("incorrect lambdas")
    lambdaTest.addTest(lambda x:True)
    lambdaTest.addTest(lambda x,y:True)

    class newTestUnit(testUnit):
        """Just a custom test Class, simple and easyest ?"""
        def __init__(self):
            super(newTestUnit, self).__init__("custom test")

        def test(self):
            self.results=[]

            # Now all the customs test happen, and are append to the results
            potatoe=[]
            try:  # You are supposed to fail this step
                if potatoe[1]==2:
                    self.addResult("empty_table",self.FAILURE_STATUS,"Non empty array")
            except:
                self.addResult("empty_table",SUCCESS_STATUS,"")
            potatoe.append([2]*2) # Not try protected, but could be if a bug was a possibility

            try:
                goodinit=True
                for e in potatoe:
                    if e==3:
                        goodinit=False
                        self.addResult("init_table",FAILURE_STATUS,"Wrong elements")
                if goodinit:
                    self.addResult("init_table",SUCCESS_STATUS,"")
            except:
                self.addResult("init_table",FAILURE_STATUS,"???")

            return self.results

    class anotherTest(simpleTestUnit):
        """docstring for anotherTest."""
        def __init__(self):
            super(anotherTest, self).__init__("YET ANOTHER TEST")

        def _testCustom(self):
            self.currentTest("testing true")
            if True:
                self.addSuccess()
            else:
                self.addFailure("True is False")

            self.currentTest("additions:simple")
            if 1+3==4:
                self.addSuccess()
            else:
                self.addFailure("1+3 != 4")

            self.currentTest("error")
            if False:
                self.addSuccess()
            else:
                self.addFailure("Supposed to fail")

            self.currentTest("overload")
            self.addSuccess()
            self.addFailure("Supposed to overload")


        def _testAnotherCustomTest(self):
            """Please note that the order of execution is entirely dependant on dir()
            and you should never rely on it for the order of the tests"""

            self.currentTest("warning:notext")
            self.addWarning()
            self.currentTest("warning:custom")
            self.addWarning("warning")
            self.addCritical("critical:critical","very bad things happened")
    mainTest.test()
    lambdaTest.test()

    mainClasses.addTest(lambdaTest)
    subclass.addTest(mainTest)
    mainClasses.addTest(subclass)
    mainClasses.addTest(newTestUnit())
    mainClasses.addTest(anotherTest())
    mainClasses.test()
