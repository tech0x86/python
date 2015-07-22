__author__ = 'kento24n452'
# -*- coding: utf-8 -*-
import csv
import codecs
from numpy import *
import matplotlib.pyplot as plt
import sys
import os.path

#csv file
FILE_NAME = "UchizawaKawara1pcAccel2"
FILE_PATH = ""

########CSV operate##########
class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL
    #delimiter = '\t'

def readCSVData():
    print "///read data from CSV///"
    filename = FILE_PATH + FILE_NAME + ".csv"
    print filename
    csvFile = codecs.open(filename, "rb","utf-8")
    counter = 0
    dataNum =1000000
    # X Y Z
    numArray = [500, 500, 500]
    dataArray = [[],[],[]]

    reader = csv.reader(csvFile,CustomFormat())
    #main loop
    for row in reader:
        if counter >= dataNum:
            break
        if len(row) != 3:
            print "invalid data"
            dataArray[0].append(numArray[0])
            dataArray[1].append(numArray[1])
            dataArray[2].append(numArray[2])
        else :
            #read data as string from csv file
            numArray = extractInt(row)
            if numArray == -1:
                if counter > 100:
                    break
            else:
                dataArray[0].append(numArray[0])
                dataArray[1].append(numArray[1])
                dataArray[2].append(numArray[2])
        counter += 1
    print "EleNum = %d" %len(dataArray[0])
    #print realDegArray
    print "read done"
    #print dataArray
    return dataArray

def extractInt(array):
    #print "///extract num///"
    #X, Y, Z
    intArray = [0,0,0]
    i = 0
    #array[0] is composed "X:nnn".X is char(X,Y,Z),n is num.
    while i < 3:
        #extract nnn
        try:
            intArray[i] = int(array[i][2:])
        except:
            print "read row error"
            return -1
        i += 1
    #print intArray
    return intArray


#######Plot Graph##########

def plotGraph(point, name):
    print "///plotGraph///"
    #setting Fontsize to all Graph
    plt.rcParams['font.size'] = 17
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = name)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[count]", fontsize = 20)
    plt.ylabel("Value[]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    #plt.hlines(0, -100, 10000, linestyles="-")
    #plt.ylim(-20,20)
    #plt.xlim(0,5000)
    plt.title(FILE_NAME, fontsize = 20 )
    plt.savefig(FILE_NAME + ".png")

if __name__ == "__main__":
    print "///mainFunc///"
    #print os.path.isfile("KurimotoKawara1pcAccel.csv")
    twoDimArray = readCSVData()
    plotGraph(twoDimArray[0], "X")
    plotGraph(twoDimArray[1], "Y")
    plotGraph(twoDimArray[2], "Z")
    plt.show()
