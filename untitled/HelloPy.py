__author__ = 'kento24n452'
# -*- coding: utf-8 -*-
##apply multibyte code##

import datetime
import sys
#my module
import testmod

def test():
    testInteger = 100
    print "関数：testを呼び出しました"
    print testInteger + 100


# taple :kind of list. you cant change element.
def getToday():
    today = datetime.datetime.today()
    value = (today.year, today.month, today.day)
    print value
    print value[0]
    print value[1]
    print value[2]


# List: you can change element
def listCtrl():
    testList = ['py', 'th', 'on']
    print testList.index('th')
    testList.append('plus')
    for i in testList:
        print i

#Use {}. Format is {'key':'valueE'}
def dictionaly():
    test_dict_1 = {'YEAR': '2010', 'MONTH': '1', 'DAY': '20'}
    print test_dict_1
    print '================================='
    for i in test_dict_1:
        print i
        print test_dict_1[i]
        print '--------------------------------'

    #Export val from dic using Key
    print test_dict_1['YEAR']
    #use "get func" to pick up val,and return optional char if not found.
    print test_dict_1.get('MONTHs','403 not found')
    #add key and val
    test_dict_1['secound'] = '114'
    print test_dict_1['secound']

    #del key and val
    del test_dict_1['YEAR']
    print test_dict_1

    #print only key
    print test_dict_1.keys()

    #Confirm what key dic have. Return T or F
    print test_dict_1.has_key('YEAR')

#Use command line func. Execute from termminal and input Arg
def commandLine():

    param = sys.argv

    print param

    print u"First Arg：" + param[1]
    print u"Second Arg：" + param[2]
    print u"Third Arg：" + param[3]

def escape():
    for i in range(100):
        print i
        if i == 21:
            print "reach 21 exit program"
            sys.exit()

#Use if func. "elif" is "Else if"
def conditionalBranch():
    value = 2
    value2 =3

    if value == 1 or value2 == 3:
        print unicode("AA")
    elif value ==2:
        print unicode("val=2")
    else:
        pass

#Use while func
def whileFunc():
    counter = 0
    while counter <10:
        counter += 1
        print counter
        if counter == 5:
            #break statement
            break

def rangeLoop():
    for i in range(2,9):
        print u"%d-%s" %(i,"count")

def outputFile():
    obj = open("py.text","w")
    print >> obj , "python string"

def exceptionTest():
    print "startCal"

    try:
        x = 100 + "200"
    except:
        print "error"
    finally:
        print "done"
    print x

def callModule():
    testclass1 = testmod.testclass()
    testclass1.testmethod("nyaa")
    from testmod import testclass
    testclass2 = testclass()
    testclass2.testmethod("gyaa")


# like  main function. If load this module oneself, __name__ contains __main__.
if __name__ == "__main__":
    print "mainFunc"
    #    test()
    #   getToday()
    #dictionaly()
    #commandLine
    #escape()
    #conditionalBranch()
    #whileFunc()
    #rangeLoop()
    #outputFile()
    #exceptionTest()
    callModule()






