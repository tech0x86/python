__author__ = 'kento24n452'
# -*- coding: utf-8 -*-
###########
'''#
Description
This programe aims to calculate and create graphs from a compensated and interpolated CSV file.
The CSV is composed two column and appx 5000 rows.
Column[0] means index degree in real world steped in 1ms.
Column[1] means virtual one.
#'''

import os, os.path
import csv
import codecs
from numpy import *
import matplotlib.pyplot as plt
import sys

#######parameters########
SearchCSVFilePath = "/Users/kento24n452/GitHub/python/CSVcontrol/CmpCSV"
CSVFileName = []
SaveGraphPath = "Graph/"
linearIntRealDegArray = []
linearIntVirDegArray = []
RMSEArray = []
RMSEResultVal = []

######CSV operate######

class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL
    #delimiter = '\t'

#return file path + CSVfilename of selected index
def searchCSVFile():
    print "///search CSV files///"
    fileArray =[]
    fileNameArray = []
    CSVFileCounter = 0
    for root, dirs, files in os.walk(SearchCSVFilePath):
        #print "Root", root
        #print "Dir", dirs
        #print "Files", files
        for file in files:
            filePathAndName = os.path.join(root, file)
            fileName, ext = os.path.splitext(file)
            if ext == ".csv":
                print CSVFileCounter, ":", file
                fileArray.append(filePathAndName)
                fileNameArray.append(fileName)
                CSVFileCounter += 1
    print "Input FileNumber:"
    selectNum = 0#int(raw_input())
    csvFile = fileArray[selectNum]
    print csvFile
    CSVFileName.append(fileNameArray[selectNum])
    print CSVFileName[0]
    return fileArray[selectNum]

def readCSVData(filename):
    print "///read LinInt CSV///"
    csvFile = codecs.open(filename, "rb","utf-8")
    reader = csv.reader(csvFile, CustomFormat())
    for row in reader:
        linearIntRealDegArray.append(float(row[0]))
        linearIntVirDegArray.append(float(row[1]))
    print "RealCam ElementNum = %d" %len(linearIntRealDegArray)
    print "VirCam ElementNum = %d" %len(linearIntVirDegArray)
    print "LinInt CSV read done"


########Calc value##########

# Control values. RMSE, MinRMSE, AveDiff, ABSAveDiff, ABSStdDiff, ABSStdeDiff, Latency
def controlCalcVal():
    xMinRmse = -10
    xMaxRmse = 40 + 1
    print "///Calc Values///"
    saveGraphPathAndName = SaveGraphPath + CSVFileName[0]

    print "-----------%s----------" %CSVFileName[0]

    #### Degree ####
    plotDegGraph(linearIntRealDegArray,"Real")
    plotDegGraph(linearIntVirDegArray,"Virtual")
    plt.savefig(saveGraphPathAndName + "RealAndVirtualDeg.png")
    plt.show()
    plt.clf()
    #### Difference ####
    diff = calcDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray)
    plotDiffGraph(diff)
    plt.savefig(saveGraphPathAndName + "Diff.png")
    plt.show()
    plt.clf()
    AbsDiffSTD = std(calcABSDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray))
    #standard deviation
    print "AbsDiffSTD: %f" %AbsDiffSTD
    AbsDiffSTDE = AbsDiffSTD/sqrt(len(linearIntRealDegArray))
    #standard error
    print "AbsDiffSTDE: %f" %AbsDiffSTDE
    #### RMSE ####
    print "RMSE: %f" %calcRMSE(linearIntRealDegArray,linearIntVirDegArray,0)
    for i in range(xMinRmse, xMaxRmse):
        rmse = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, i)
        RMSEArray.append(rmse)
    print "Min RMSE :%f" % min(RMSEArray)
    #index start at 0, RMSE start at - 20ms. So, offset needed.
    #Index of Min RMSE is latency
    latency = RMSEArray.index(min(RMSEArray)) + xMinRmse
    RMSEResultVal.append(latency)
    RMSEResultVal.append(min(RMSEArray))
    print "latency: %d ms" % latency
    plotRMSEGraph(RMSEArray, xMinRmse, xMaxRmse)
    plt.savefig(saveGraphPathAndName + "RMSE.png")
    plt.show()
    plt.clf()

# calc RMSE
def calcRMSE(realCamArray, virCamArray, shiftNum):
    i = 0
    sum = 0.0
    rmse = 0.0

    if len(realCamArray) != len(virCamArray):
        return "RMSE error"

    if shiftNum == 0:
        while i < len(realCamArray):
            diff = virCamArray[i] - realCamArray[i]
            pow = math.pow(diff, 2)
            sum += pow
            i += 1
        ave = sum/len(realCamArray)
        rmse = math.sqrt(ave)

    #shift virCam to future
    elif shiftNum > 0:
        while i < len(realCamArray) - shiftNum:
             diff = virCamArray[i + shiftNum] - realCamArray[i]
             pow = math.pow(diff, 2)
             sum += pow
             i += 1
        ave = sum/len(realCamArray)
        rmse = math.sqrt(ave)

    #shift realCam to future
    elif shiftNum < 0:
       shiftNum *= -1
       while i < len(realCamArray) - shiftNum:
            diff = virCamArray[i] - realCamArray[i + shiftNum]
            pow = math.pow(diff, 2)
            sum += pow
            i += 1
       ave = sum/len(realCamArray)
       rmse = math.sqrt(ave)

    return rmse

# Calc Average Difference between Real and Vir
def calcDiffOfDeg(realCamArray, virCamArray):
    print "///calc Difference///"
    i = 0
    diff = 0.0
    diffArray = []
    while i < len(realCamArray):
        diffArray.append(virCamArray[i] - realCamArray[i])
        diff += diffArray[i]
        i += 1
    diff /= len(realCamArray)
    print "Diff:%1.4f" %diff
    return diffArray

# Calc Average ABS Diff between Real and Vir
def calcABSDiffOfDeg(realCamArray, virCamArray):
    print "///calc ABS Difference///"
    i = 0
    AbsDiff = 0.0
    AbsDiffArray = []
    while i < len(realCamArray):
        AbsDiffArray.append(math.fabs(virCamArray[i] - realCamArray[i]))
        AbsDiff += AbsDiffArray[i]
        i += 1
    AbsDiff /= len(realCamArray)

    print "Ave ABS Diff:%1.4f" %AbsDiff
    return AbsDiffArray

#######Plot Graph##########

def plotDegGraph(point, name):
    print "///plotGraph///"
    #setting Fontsize to all Graph
    plt.rcParams['font.size'] = 17
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = name)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 20)
    plt.ylabel("Azmith[deg]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(-20,20)
    plt.xlim(0,5000)
    plt.title(CSVFileName[0] + " Real and Virtual Azmith", fontsize = 20 )

def plotDiffGraph(point):
    print "///plotDiffGraph///"

    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = "Difference", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 18)
    plt.ylabel("Azmith[deg]", fontsize = 18)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(-5,5)
    plt.xlim(0,5000)
    plt.title(CSVFileName[0] + " Difference Azmith", fontsize = 20 )


def plotRMSEGraph(point, xmin, xmax):
    print "///plotRMSEGraph///"

    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(xmin, xmax - 1, len(point))
    plt.plot(x, point, label = "RMSE", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Shift Time[ms]", fontsize = 20)
    plt.ylabel("RMSE[deg]", fontsize = 20)
    plt.vlines(0, -10, 50, linestyles="-")
    plt.vlines(RMSEResultVal[0], -10, 2, linestyles="-", colors="red", linewidth=2)
    annotateData = str(round(RMSEResultVal[1],2)) + "deg, " + str(RMSEResultVal[0]) + "ms"
    plt.annotate(annotateData,
            xy=(RMSEResultVal[0], 2), xycoords='data',
            xytext=(+10, +30), textcoords='offset points', fontsize=17,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    plt.ylim(0,5)
    plt.title(CSVFileName[0] + "Shift Time and RMSE", fontsize = 20 )


if __name__ == "__main__":
    print "Calc & Create main Func"
    csvFile = searchCSVFile()
    readCSVData(csvFile)
    controlCalcVal()