# -*- coding: utf-8 -*-
__author__ = 'kento24n452'
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


#######parameters########
SearchCSVFilePath = "/Users/kento24n452/GitHub/python/CSVcontrol/CmpCSV"
CSVFileName = []
SaveGraphPath = "Graph/"
linearIntRealDegArray = []
linearIntVirDegArray = []
myPredArray = []
speedArray = []
accelerationArray = []
#FPS in CmpCSV
framePerSecond = 1000.0
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
    selectNum = int(raw_input())
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
    print "///Calc Values///"
    xMinRmse = -10
    xMaxRmse = 40 + 1
    RMSEArray = []
    #setting Fontsize to all Graph
    plt.rcParams['font.size'] = 17

    #indicater   0:not show, 1: show()
                        #0:Degree, 1:Diff, 2:Velocity, 3:Accel, 4:RMSE,
                        #5:no latency Diff and V, 6:Moment latency and V
    pltGraphStateArray = [1, 0, 0, 0, 0,
                          0, 0]
    saveGraphPathAndName = SaveGraphPath + CSVFileName[0]
    noLatencyVirCam = []

    calcVelocityFromRealCam()
    if pltGraphStateArray[2]:
        plotVelocityGraph(speedArray)
        plt.show()
    plt.clf()
    #scaling real cam after calc speed
    calcRealCamScale()

    print "-----------%s----------" %CSVFileName[0]
    #### Degree ####
    if pltGraphStateArray[0]:
        plotTwoElementGraph(linearIntRealDegArray, "Real", linearIntVirDegArray, "Virtual", "", 20)
        #emf, eps, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff
        plt.savefig(saveGraphPathAndName + "Deg.eps")
        plt.savefig(saveGraphPathAndName + "Deg.ps")
        plt.show()
    plt.clf()
    #### Difference ####
    diff = calcDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray)
    if pltGraphStateArray[1]:
        plotDiffGraph(diff)
        plt.show()
        plt.savefig(saveGraphPathAndName + "Diff.png")
    plt.clf()
    AbsDiffSTD = std(calcABSDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray))
    #standard deviation
    print "AbsDiffSTD: %f" %AbsDiffSTD
    AbsDiffSTDE = AbsDiffSTD/sqrt(len(linearIntRealDegArray))
    #standard error
    print "AbsDiffSTDE: %f" %AbsDiffSTDE
    #### RMSE ####

    if pltGraphStateArray[2]:
        plotVelocityGraph(speedArray)
        plt.show()
    plt.clf()
    calcAccFromVelocity()
    if pltGraphStateArray[3]:
        plotAccelGraph(accelerationArray)
        plt.show()
    plt.clf()
    print "RMSE: %f" %calcRMSE(linearIntRealDegArray, linearIntVirDegArray, 0)
    for i in range(xMinRmse, xMaxRmse):
        rmse = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, i)
        RMSEArray.append(rmse)
    print "Min RMSE :%f" % min(RMSEArray)
    latency = RMSEArray.index(min(RMSEArray)) + xMinRmse
    print "latency: %d ms" % latency
    if pltGraphStateArray[4]:
        plotRMSEGraph(RMSEArray, xMinRmse, xMaxRmse)
        plt.savefig(saveGraphPathAndName + "RMSE.eps")
        plt.savefig(saveGraphPathAndName + "RMSE.ps")
        plt.show()
    plt.clf()

    #create no late VirCam Azmith
    j = 0
    while j < len(linearIntVirDegArray) - latency:
        noLatencyVirCam.append(linearIntVirDegArray[latency + j])
        j += 1
    calcLatency(linearIntRealDegArray, noLatencyVirCam)
    NoLateDiff = calcDiffOfDeg(linearIntRealDegArray, noLatencyVirCam)
    #plotTwoElementGraph(linearIntRealDegArray, "real", noLatencyVirCam, "noLateVir", "", 20)
    if pltGraphStateArray[5]:
        plotNoLateDiffAndVelocityGraph(NoLateDiff, speedArray)
        plt.savefig(saveGraphPathAndName + "NoLateDiff+V.eps")
        plt.savefig(saveGraphPathAndName + "NoLateDiff+V.ps")
        plt.show()
    plt.clf()

    momentLatency = calcMomentLatency()
    if pltGraphStateArray[6]:
        plotMomentLatencyAndVelocity(momentLatency, speedArray, latency)
        plt.savefig(saveGraphPathAndName + "MomentLatency+V.eps")
        plt.savefig(saveGraphPathAndName + "MomentLatency+V.ps")
        plt.show()
    plt.clf()

# calc RealCamDeg scale to fit virtual.
# present scale is real > virtual.
def calcRealCamScale():
    print "///calc real Cam scale///"
    scaleBandStep = 0.001
    scale = 1.00
    i = 1
    latency = calcLatency(linearIntRealDegArray, linearIntVirDegArray)
    minRMSE = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, latency)
    while i < 500:
        scaledRealCamDeg = []
        j = 0
        while j < len(linearIntRealDegArray):
            ratio = scale - (scaleBandStep * i)
            scaledVal = linearIntRealDegArray[j] * ratio
            scaledRealCamDeg.append(scaledVal)
            j += 1
        tmpRMSE = calcRMSE(scaledRealCamDeg, linearIntVirDegArray, latency)
        if tmpRMSE < minRMSE:
            minRMSE = tmpRMSE
        else:
            print "find scale:", ratio, " RMSE:", minRMSE
            global linearIntRealDegArray
            linearIntRealDegArray = scaledRealCamDeg
            break
        i += 1
    return scaledRealCamDeg

#calc latency and each RMSE when shifted.
def calcLatency(base, comparison):
    print "///calc latency///"
    minusShift = 10
    plusShift = 100 + 1
    calcArray = []
    #index start at 0, shift start at - 10ms. So, offset needed.
    #Index of Min RMSE is latency
    for i in range(-minusShift, plusShift):
        rmse = calcRMSE(base, comparison, i)
        calcArray.append(rmse)
    latency = calcArray.index(min(calcArray)) - minusShift
    print "Min RMSE:", min(calcArray), "deg"
    print "latency:", latency, "ms"
    return latency

# calc RMSE
def calcRMSE(realCamArray, virCamArray, shiftNum):
    i = 0
    sum = 0.0
    rmse = 0.0

    if len(realCamArray) > len(virCamArray):
        scanNum = len(virCamArray)
    else:
        scanNum = len(realCamArray)


    if shiftNum == 0:
        while i < scanNum:
            diff = virCamArray[i] - realCamArray[i]
            pow = math.pow(diff, 2)
            sum += pow
            i += 1
        ave = sum/scanNum
        rmse = math.sqrt(ave)

    #shift virCam to future
    elif shiftNum > 0:
        while i < scanNum - shiftNum:
             diff = virCamArray[i + shiftNum] - realCamArray[i]
             pow = math.pow(diff, 2)
             sum += pow
             i += 1
        ave = sum/scanNum
        rmse = math.sqrt(ave)

    #shift realCam to future
    elif shiftNum < 0:
       shiftNum *= -1
       while i < scanNum - shiftNum:
            diff = virCamArray[i] - realCamArray[i + shiftNum]
            pow = math.pow(diff, 2)
            sum += pow
            i += 1
       ave = sum/scanNum
       rmse = math.sqrt(ave)

    return rmse

# Calc Average Difference between Real and Vir
def calcDiffOfDeg(realCamArray, virCamArray):
    print "///calc Difference///"
    i = 0
    diff = 0.0
    diffArray = []

    if len(realCamArray) > len(virCamArray):
        scanNum = len(virCamArray)
    else:
        scanNum = len(realCamArray)
    #print scanNum
    while i < scanNum:
        diffArray.append(virCamArray[i] - realCamArray[i])
        diff += diffArray[i]
        i += 1
    diff /= scanNum
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

#calc velocity from real cam azmith
def calcVelocityFromRealCam():
    i = 1
    speedArray.append(0.0)
    sumSpeed = 0.0
    while i < len(linearIntRealDegArray):
        #calc deg/second
        speed = linearIntRealDegArray[i] - linearIntRealDegArray[i-1]
        speed *= framePerSecond
        sumSpeed += math.fabs(speed)
        speedArray.append(speed)
        i += 1
    #calcSmoothing(speedArray, 10)
    #plt.clf()
    #plotGraph(calcSmoothing(speedArray, 30),"smooth")
    #plt.show()
    print "average velocity[deg/s]: " , sumSpeed/len(speedArray)
    print "max velocity[deg/s]: ", max(max(speedArray), math.fabs(min(speedArray)))


#calc Acceleration from speedArray. store those in accelerationArray[]
def calcAccFromVelocity():
    i = 1
    sumAcc = 0.0
    accelerationArray.append(0.0)
    while i < len(speedArray):
        #calc deg/second
        acc = speedArray[i] - speedArray[i-1]
        accelerationArray.append(acc)
        sumAcc += math.fabs(acc)
        i += 1
    print "average Acceleration[deg/s^2]: ", sumAcc/len(accelerationArray)
    print "max Acceleration[deg/s^2]: ", max(max(accelerationArray),math.fabs(min(accelerationArray)))

# make array smoothing between interval
def calcSmoothing(array, interval):
    # X..Y
    i = 0
    if interval == 0:
        return array
    resultArray=[]
    while len(array) > i + interval:
        print i
        startVal = array[i]
        endVal = array[i + interval]
        diff = endVal - startVal
        j = 0
        while j < interval:
            smoothVal = startVal + (diff * j) / float(interval)
            resultArray.append(smoothVal)
            j += 1
        i += interval
    print len(resultArray)
    return resultArray


# base data is real cam azmith. First, set delay time(around dozens millisecond).
# And using this delay time, delay real cam data as virtual azmith
# Now, you implicate "my prediction".
# prediction time length means "update" prediction time.
# (ex 13.3ms prediction time is predict head pose in 13.3ms future.
# In this interval, predict it 75 times in a second
# In this data, head pose is deg, prediction method is linear interpolation using speed and interval
# In myPred, x(t) = v0 * t + x0, using delayArray

def createMyPred(predtime, delay):
    delay = 26
    predtime = 9
    i = 0
    j = 0
    #deg/ms
    speed = 0.0
    delayData = []
    presentPos = 0.0
    predPos = 0.0
    # create delayed data
    while i < delay:
        delayData.append(0.0)
        i += 1
    i = 0
    while i < len(linearIntRealDegArray):
        delayData.append(linearIntRealDegArray[i])
        i += 1
    # loop while data end in 5sec
    while j < len(linearIntRealDegArray):
        #update speed
        if predtime == 0:
            predPos = delayData[j]

        elif j % predtime == 0:
            sumSpeed = 0
            for k in range(predtime):
                sumSpeed += speedArray[j-k]
            aveSpeed = sumSpeed/predtime
            #speed = speedArray[j] / framePerSecond
            speed = aveSpeed / framePerSecond
            presentPos = delayData[j]
        else:
            predPos = speed * ((j % predtime) + predtime) + presentPos

        myPredArray.append(predPos)
        j += 1
    print len(myPredArray)
    plt.clf()
    title = " Delay[ms]:" + str(delay) + " Pred[ms]:" + str(predtime)
    plotTwoElementGraph(linearIntRealDegArray, "Real", myPredArray, "myPred", title,20)
    calcLatency(linearIntRealDegArray, myPredArray)
    #plt.show()
    plt.clf()

def calcMomentLatency():
    i = 0
    scanNum = 50
    latencyArray = []
    tmpLatency = []
    #scan real data
    while i < len(linearIntRealDegArray) :
        j = 0
        diffArray = []
        diffArrayIntv = []
        while j < scanNum and i - j > -1 :
            diffArray.append(math.fabs(linearIntVirDegArray[i] - linearIntRealDegArray[i - j]))
            j += 1
        latency = diffArray.index(min(diffArray))

        #calc over compensate time
        if latency == 0:
            j = 0
            while j < scanNum and i + j < len(linearIntRealDegArray) :
                diffArrayIntv.append(math.fabs(linearIntVirDegArray[i] - linearIntRealDegArray[i + j]))
                j += 1
                latency = -diffArrayIntv.index(min(diffArrayIntv))

        #deal with error latency
        tmpLatency.append(latency)
        if latency > median(tmpLatency) + 5 or latency < median(tmpLatency) - 5:
            if len(latencyArray) > 1:
                latency = latencyArray[i - 1]
        if len(tmpLatency) > 50:
            tmpLatency.pop(0)
        latencyArray.append(latency)
        i += 1
    return latencyArray

#######Plot Graph##########

def plotTwoElementGraph(point1, name1, point2, name2, title, ylim):
    print "///plot Two Graph///"
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x1 = linspace(0, len(point1), len(point1))
    plt.plot(x1, point1, label = name1)
    x2 = linspace(0, len(point2), len(point2))
    plt.plot(x2, point2, label = name2, linestyle="--")

    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 20)
    plt.ylabel("Azmith[deg]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles = "-")
    plt.ylim(-ylim, ylim)
    plt.xlim(0, 1000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + title, fontsize = 20 )

def plotGraph(point, name):
    print "///plotGraph///"
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = name)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 20)
    #plt.ylabel("Azmith[deg]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles="-")
    #plt.ylim(-20,20)
    plt.xlim(0,1000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + " Real and Virtual Azmith", fontsize = 20 )

def plotNoLateDiffAndVelocityGraph(point1,point2):
    print "///plotNolateDiffAndVelo///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(point1, "g",)
    ax2.plot(point2, 'b', linestyle="--")
    fs_label = 20
    ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    ax1.set_ylabel('Difference of Azmith[deg]', fontsize = fs_label)
    ax1.set_xlim(0, 1000)
    #invert range to (min,max)
    ax1.set_ylim(-1, 1)

    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-250, 250)
    plt.hlines(0, -100, 10000, linestyles="-")
    ax1.grid(True)


def plotMomentLatencyAndVelocity(momentLatency, velocity, latency):
    print "///plot Moment Late And Velocity Graph///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(momentLatency, "g",)
    ax2.plot(velocity, 'b', linestyle="--")
    fs_label = 20
    ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    ax1.set_ylabel('Latency at the each moment[ms]', fontsize = fs_label)
    ax1.set_xlim(0, 1000)
    ax1.set_ylim(0, 35)

    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-250, 250)
    plt.hlines(0, -100, 10000, linestyle="-")
    ax1.grid(True)

def plotDegGraph(point, name):
    print "///plotDegGraph///"
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = name)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 20)
    plt.ylabel("Azmith[deg]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(-20,20)
    plt.xlim(0, 1000)
    plt.title(CSVFileName[0] + " Real and Virtual Azmith", fontsize = 20 )
    plt.grid(True)

def plotDiffGraph(point):
    print "///plotDiffGraph///"

    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = "Difference", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 18)
    plt.ylabel("Difference of Azmith[deg]", fontsize = 18)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(-1, 1)
    plt.xlim(0, 1000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + " Difference Azmith", fontsize = 20 )

def plotRMSEGraph(point, xmin, xmax):
    print "///plotRMSEGraph///"
    minRMSE = min(point)
    latency = point.index(min(point)) + xmin
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(xmin, xmax - 1, len(point))
    plt.plot(x, point, label = "RMSE", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Shift Time[ms]", fontsize = 20)
    plt.ylabel("RMSE[deg]:Real and Virtual", fontsize = 20)
    plt.vlines(0, -10, 50, linestyles="-")
    plt.vlines(latency, -10, 2, linestyles="--", colors="red", linewidth=2)
    annotateData = str(round(minRMSE, 2)) + "deg, " + str(latency) + "ms"
    plt.annotate(annotateData,
            xy=(latency, 2), xycoords='data',
            xytext=(+10, +30), textcoords='offset points', fontsize=17,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    plt.ylim(0,5)
    plt.grid(True)
    #plt.title(CSVFileName[0] + "Shift Time and RMSE", fontsize = 20 )

def plotVelocityGraph(point):
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = "Velocity", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 18)
    plt.ylabel("Velocity[deg/s]", fontsize = 18)
    plt.hlines(0, -100, 10000, linestyles="-")
    #plt.ylim(-5,5)
    plt.xlim(0,1000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + " Speed", fontsize = 20 )


def plotAccelGraph(point):
    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(x, point, label = "Acceleration", linewidth=2)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 18)
    plt.ylabel("Acceleration[deg/s^2]", fontsize = 18)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.xlim(0, 1000)
    plt.grid(True)
#    plt.title(CSVFileName[0] + " Accel", fontsize = 20 )


if __name__ == "__main__":
    print "Calc & Create main Func"
    csvFile = searchCSVFile()
    readCSVData(csvFile)
    controlCalcVal()
    #createMyPred(10,26)




