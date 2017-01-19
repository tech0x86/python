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
#SearchCSVFilePath = "/Users/kento24n452/GitHub/python/transitionExperimentImage/"
SearchCSVFilePath ="/Users/kento24n452/Data/CSV/Rotation/"
CSVFileName = []
SaveGraphPath = "Graph/"
linearIntRealDegArray = []
linearIntVirDegArray = []
myPredArray = []
speedArray = []
accelerationArray = []
#Graph size
figSize = [8.1, 5.3] #X,Y cm
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
    tmp = []
    counter = 0
    delay = 0 #ms
    for row in reader:
        linearIntRealDegArray.append(float(row[0]))
        tmp.append(float(row[1]))
        #linearIntVirDegArray.append(float(row[1]))
        if counter > delay - 1:
            linearIntVirDegArray.append(tmp.pop(0))
        else:
            linearIntVirDegArray.append(0.0)
        counter +=1
    print "RealCam ElementNum = %d" %len(linearIntRealDegArray)
    print "VirCam ElementNum = %d" %len(linearIntVirDegArray)
    print "LinInt CSV read done"

def writeData(name, data1, data2, data3):
    print "///write CmpCSV data///"
    tempArray = []
    i = 0
    fn = "CSV/"+ CSVFileName[0] + name + ".csv"
    #get URI with optional setting
    csvFile = codecs.open(fn, "w", "utf-8")
    #disignate format
    writer = csv.writer(csvFile,CustomFormat() )

    # Write Linaer Interpolation Real and Virtual data (ms)
    # data num of Real and Vir are same
    while i < len(data1):
        tempArray.append(data1[i])
        tempArray.append(data2[i])
        tempArray.append(data3[i])
        #tempArray.append(data4[i])
        #tempArray.append(data5[i])
        writer.writerow(tempArray)
        tempArray = []
        i +=1
    csvFile.close()
    print "write done:" , fn


########Calc value##########

# Control values. RMSE, MinRMSE, AveDiff, ABSAveDiff, ABSStdDiff, ABSStdeDiff, Latency
def controlCalcVal():
    print "///Calc Values///"
    xMinRmse = -10
    xMaxRmse = 40 + 1
    RMSEArray = []
    #setting Fontsize to all Graph
    plt.rcParams['font.size'] = 8
    #plt.rcParams['font.family'] = "Helvetica"
    plt.rcParams['axes.linewidth'] = 0.5 #軸の太さを設定。目盛りは変わらない

    #indicater   0:not show, 1: show()
                        #0:Degree, 1:Diff, 2:Velocity, 3:Accel, 4:RMSE,
                        #5:Remaining Diff and V, 6:Moment latency and V, 7:Instantaneous latency and Deg(pixel
                        #8:Instantaneous latency + Real, 9:Remaining Diff + Real
    #pltGraphStateArray = [1, 0, 0, 0, 1,
     #                     1, 1, 0, 1, 1]
    pltGraphStateArray = [1, 0, 0, 0, 0,
                          0, 0, 0, 0, 1]

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
        plt.show()
    plt.clf()
    #### Difference ####
    diff = calcDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray)
    if pltGraphStateArray[1]:
        plotDiffGraph(diff)
        plt.savefig(saveGraphPathAndName + "Diff.eps")
        plt.show()
    plt.clf()
    AbsDiffSTD = std(calcABSDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray))
    #standard deviation
    print "AbsDiffSTD: %f" %AbsDiffSTD
    AbsDiffSTDE = AbsDiffSTD/sqrt(len(linearIntRealDegArray))
    #standard error
    print "AbsDiffSTDE: %f" %AbsDiffSTDE


    if pltGraphStateArray[2]:
        plotVelocityGraph(speedArray)
        plt.show()
    plt.clf()
    calcAccFromVelocity()
    if pltGraphStateArray[3]:
        plotAccelGraph(accelerationArray)
        plt.show()
    plt.clf()
    #### RMSE ####
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
        plt.show()
    plt.clf()

    #create no late VirCam Azimuth
    j = 0
    while j < len(linearIntVirDegArray) - latency:
        noLatencyVirCam.append(linearIntVirDegArray[latency + j])
        j += 1
    #verify?
    #calcLatency(linearIntRealDegArray, noLatencyVirCam)
    NoLateDiff = calcDiffOfDeg(linearIntRealDegArray, noLatencyVirCam)
    #plotTwoElementGraph(linearIntRealDegArray, "real", noLatencyVirCam, "noLateVir", "", 20)
    if pltGraphStateArray[5]:
        plotNoLateDiffAndVelocityGraph(NoLateDiff, speedArray)
        plt.savefig(saveGraphPathAndName + "NoLateDiff+V.eps")
        plt.show()
    plt.clf()

    momentLatency = calcMomentLatency()
    #print "momentLatencyNum:",len(momentLatency)
    if pltGraphStateArray[6]:
        plotMomentLatencyAndVelocity(momentLatency, speedArray, latency)
        plt.savefig(saveGraphPathAndName + "MomentLatency+V.eps")
        plt.show()
    plt.clf()

    #### moment Latency and Degree ####
    #calcMomentLatencyAtDeg(momentLatency, pltGraphStateArray[7], latency)

    #5:no latency Diff and V, 6:Moment latency and V, 7:Moment latency and Deg(pixel
    #   8:moment latency + Real, 9: no late Diff + Real


    if pltGraphStateArray[8]:
        plotMomentLatencyAndReal(momentLatency, linearIntRealDegArray, latency)
        plt.savefig(saveGraphPathAndName + "MomentLatency+Real.eps")
        plt.show()
    plt.clf()

    if pltGraphStateArray[9]:
        plotNoLateDiffAndRealGraph(NoLateDiff, linearIntRealDegArray)
        plt.savefig(saveGraphPathAndName + "NoLateDiff+Real.eps")
        plt.show()
    plt.clf()

    #expand time reso to 0.01ms in Real
    linearInt2RealDegArray = calcLinearInt()
    #expand time reso to 0.01ms in Virtual
    discreteVirCamArray = [linearIntVirDegArray[0]]

    j = 1
    while j < len(linearIntVirDegArray):
        k = 1
        while k < 100:
            discreteVirCamArray.append("NA")
            k+=1
        discreteVirCamArray.append(linearIntVirDegArray[j])
        j+=1
    print "discreteVirCamArray num", len(discreteVirCamArray)

    #calcLatency2(linearInt2RealDegArray, discreteVirCamArray, latency)


# calc RealCamDeg scale to fit virtual.
# present scale is real > virtual.
def calcRealCamScale():
    print "///calc real Cam scale///"
    scaleBandStep = 0.001
    scale = 1.00
    i = 1
    scaledRealCamDeg = []
    latency = calcLatency(linearIntRealDegArray, linearIntVirDegArray)
    minRMSE = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, latency)
    while i < 500:
        tmpScaledRealCamDeg = scaledRealCamDeg
        if i==1:
            tmpScaledRealCamDeg = linearIntRealDegArray
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
            print "find scale:", ratio + scaleBandStep, " minRMSE:", minRMSE
            global linearIntRealDegArray
            linearIntRealDegArray = tmpScaledRealCamDeg
            break
        i += 1
    return tmpScaledRealCamDeg

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

#calc latency more resolution
#ave latanecy >= 1
def calcLatency2(base, comparison, aveLatency):
    print "///calc latency///"
    scanArea = 50
    minusShift = (aveLatency * 100) - scanArea# x0.01ms
    plusShift = (aveLatency * 100) + scanArea + 1
    calcArray = []
    #index start at 0, shift start at - 10ms. So, offset needed.
    #Index of Min RMSE is latency
    #example: 900 ~ 1100 lantency:10ms
    for i in range(minusShift, plusShift):
        print "RMSE step:", i,
        rmse = calcRMSE2(base, comparison, i)
        calcArray.append(rmse)
    latency = calcArray.index(min(calcArray)) + minusShift
    latency /= 100.0
    print "Min RMSE:", min(calcArray), "deg"
    print "latency:", latency, "ms"


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
        ave = sum/i
        rmse = math.sqrt(ave)

    #shift virCam to future
    elif shiftNum > 0:
        while i < scanNum - shiftNum:
             diff = virCamArray[i + shiftNum] - realCamArray[i]
             pow = math.pow(diff, 2)
             sum += pow
             i += 1
        ave = sum/i
        rmse = math.sqrt(ave)

    #shift realCam to future
    elif shiftNum < 0:
       shiftNum *= -1
       while i < scanNum - shiftNum:
            diff = virCamArray[i] - realCamArray[i + shiftNum]
            pow = math.pow(diff, 2)
            sum += pow
            i += 1
       ave = sum/i
       rmse = math.sqrt(ave)

    return rmse

# calc RMSE in 0.01 ms
def calcRMSE2(realCamArray, virCamArray, shiftNum):
    i = 0
    sum = 0.0
    rmse = 0.0
    counter = 0
    scanNum = len(realCamArray)
    #shiftNum = aveLatency - 1
    #store val in discrete Array
    # Num:500k step 0.01ms

    if shiftNum == 0:
        while i < scanNum:
            if virCamArray[i] != "NA":
                diff = virCamArray[i] - realCamArray[i]
                pow = math.pow(diff, 2)
                sum += pow
                counter +=1
            i += 1
        ave = sum/counter
        rmse = math.sqrt(ave)

    #shift virCam to future
    elif shiftNum > 0:
        while i < scanNum - shiftNum:
             if virCamArray[i + shiftNum] != "NA":
                diff = virCamArray[i + shiftNum] - realCamArray[i]
                pow = math.pow(diff, 2)
                sum += pow
                counter +=1
             i += 1
        ave = sum/counter
        rmse = math.sqrt(ave)

    #shift realCam to future
    elif shiftNum < 0:
       shiftNum *= -1
       while i < scanNum - shiftNum:
            if virCamArray[i] != "NA":
                diff = virCamArray[i] - realCamArray[i + shiftNum]
                pow = math.pow(diff, 2)
                sum += pow
                counter += 1
            i += 1
       ave = sum/counter
       rmse = math.sqrt(ave)

    return rmse


# calc Liner Interpolation,
# and store it to linerInt array in 1ms order
def calcLinearInt():
    print "///calc LinearInt///"
    linearIntDegArray = []
    framePerMS = 100
    counter = 1
    y1My0 = 0.0
    # Set same value until first CamFlame
    # Fill head-array with data between 0ms to Nms until valid data
    # math.floor : remove Fig below 1st decimal place

    whileCounter = 0
    linearIntDegArray.append(0.0)
    #0-1.00 step 0.01
    while whileCounter < framePerMS:
        linearIntDegArray.append(linearIntRealDegArray[0])
        whileCounter += 1
        #print "ms: %d" % whileCounter

    #main loop. calc while elementNum
    while counter < len(linearIntRealDegArray) -1 :
        x0 = framePerMS * (counter + 1)
        x = x0 + 1

        #sub loop. loop while  x < (omited x1)
        while x <= framePerMS * (counter + 2) :
            #y1 - y0
            y1My0 = linearIntRealDegArray[int(counter + 1)] - linearIntRealDegArray[int(counter)]
            #calc Liner Interpolation
            linerInt = linearIntRealDegArray[int(counter)]
            # x1 - x0
            x1Mx0 = framePerMS
            linerInt += (x - x0) * y1My0 / x1Mx0
            linearIntDegArray.append(linerInt)
            #print "ms: %d" % x  ,
            #print linerInt ,
            #print "count: %d" % counter
            x += 1
        counter += 1
    #print "LinearInt Calc done. count = %d" % counter
    print "real Cam in 0.01ms", len(linearIntDegArray)
    #print linearIntDegArray
    return linearIntDegArray

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

#calc velocity from real cam Azimuth
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



# base data is real cam Azimuth. First, set delay time(around dozens millisecond).
# And using this delay time, delay real cam data as virtual Azimuth
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
        threthould = 5
        if latency > median(tmpLatency) + threthould or latency < median(tmpLatency) - threthould:
            if len(latencyArray) > 1:
                latency = latencyArray[i - 1]
        if len(tmpLatency) > 50:
            tmpLatency.pop(0)
        latencyArray.append(latency)
        i += 1
    return latencyArray

def calcMomentLatencyAtDeg(momentLatency, plotIndicater, latency):
    degPerPixel = 0.073848247
    #turntable degree range +/-
    degBand = 20
    sum =0.0
    #pixelBand = 271
    eleNum = (degBand * 2) + 1
    #[0]-[40] -20~0~20 len:41
    momentLatencyAtDeg = [[] for j in range(eleNum)]
    momentLatencyAtDegAve = [0 for j in range(eleNum)]
    momentLatencyAtDegSTDE = [0 for j in range(eleNum)]

    i=0
    #calc momentLatency each Deg
    while i < len(linearIntRealDegArray):
        deg = int(round(linearIntRealDegArray[i], 0))
        index = deg + degBand
        momentLatencyAtDeg[index].append(momentLatency[i])
        sum += momentLatency[i]
        i += 1

    index = 0
    while index < eleNum:
        # if valid data
        if len(momentLatencyAtDeg[index]) > 0:
            momentLatencyAtDegAve[index] = mean(momentLatencyAtDeg[index])
            momentLatencyAtDegSTDE[index] = std(momentLatencyAtDeg[index]) / sqrt(len(momentLatencyAtDeg[index]))
        index += 1
    x = linspace(-degBand/degPerPixel, degBand/degPerPixel, eleNum)
    print "ave moment latency:", sum/i


    #print momentLatencyAtDegAve
    if plotIndicater:
        writeData("LatencyAndDeg",x,momentLatencyAtDegAve, momentLatencyAtDegSTDE)
        plotMomentLatencyAndDegGraph(momentLatencyAtDegAve, momentLatencyAtDegSTDE, latency, degBand)
        plt.savefig(SaveGraphPath + CSVFileName[0] + "MomentLatencyAndPixel.eps")
        plt.savefig(SaveGraphPath + CSVFileName[0] + "MomentLatencyAndPixel.ps")
        plt.show()
        plt.clf()

#######Plot Graph##########

def plotTwoElementGraph(point1, name1, point2, name2, title, ylim):
    print "///plot Two Graph///"
    plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    x1 = linspace(0, len(point1), len(point1))
    plt.plot(x1, point1, label = name1)
    x2 = linspace(0, len(point2), len(point2))
    plt.plot(x2, point2, label = name2, linestyle="--")

    #plt.legend(loc = 'upper right') # show data label
    #plt.xlabel("Time[ms]")
    #plt.ylabel("Azimuth[deg]")
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles = "-", lw = 0.5)
    plt.ylim(-ylim, ylim)
    plt.xlim(0, 5000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + title, fontsize = 20 )

def plotDiffGraph(point):
    print "///plotDiffGraph///"

    #linspace(開始値，終了値，分割数)”で，線形数列を作成。
    x = linspace(0, len(point), len(point))
    plt.plot(point, label = "Difference", linewidth=1)
    plt.legend(loc = 'upper right') # show data label
    plt.xlabel("Time[ms]", fontsize = 18)
    plt.ylabel("Difference of Azimuth[deg]", fontsize = 18)
    plt.hlines(0, -100, 10000, linestyles="-")
    #plt.ylim(-1, 1)
    plt.xlim(0, 5000)
    plt.grid(True)
    #plt.title(CSVFileName[0] + " Difference Azimuth", fontsize = 20 )

#(b)
def plotRMSEGraph(point, xmin, xmax):
    print "///plotRMSEGraph///"
    plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    minRMSE = min(point)
    latency = point.index(min(point)) + xmin
    x = linspace(xmin, xmax - 1, len(point))
    plt.plot(x, point, label = "RMSE",linestyle = ":", color = "m")
    #plt.legend(loc = 'upper right') # show data label
    #plt.xlabel("Shift Time[ms]")
    #plt.ylabel("RMSE[deg]:Real and Virtual")
    plt.vlines(0, -10, 50, linestyles="-", lw = 0.5)
    plt.vlines(latency, -10, 2, linestyles="--", colors="red", linewidth=0.5)
    #
    '''
    annotateData = str(round(minRMSE, 2)) + "deg, " + str(latency) + "ms"

    plt.annotate(annotateData,
            xy=(latency, 2), xycoords='data',
            xytext=(0, +30), textcoords='offset points', fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    '''
    #
    plt.ylim(0,5)
    plt.grid(True)
    #plt.title(CSVFileName[0] + "Shift Time and RMSE", fontsize = 20 )


def plotNoLateDiffAndVelocityGraph(point1,point2):
    print "///plotNolateDiffAndVelo///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file

    fig = plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(point1, "g",)
    ax2.plot(point2, 'b', linestyle="--")
    fs_label = 8
    #ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    #ax1.set_ylabel('Difference of Azimuth[deg]', fontsize = fs_label)
    ax1.set_xlim(0, 1000)
    #invert range to (min,max)
    ax1.set_ylim(-1, 1)
    #ax1.set_ylim(-5, 5)
    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-250, 250)
    plt.hlines(0, -100, 10000, linestyles="-", lw =0.5)
    ax1.grid(True)

def plotNoLateDiffAndRealGraph(diff, real):
    print "///plotNolateDiffAndReal///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file

    fig = plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(diff, "g",)
    ax2.plot(real, 'b',)
    fs_label = 8
    #ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    #ax1.set_ylabel('Difference of Azimuth[deg]', fontsize = fs_label)
    ax1.set_xlim(0, 5000)
    #invert range to (min,max)
    ax1.set_ylim(-1, 1)
    #ax1.set_ylim(-5, 5)
    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-20, 20)
    plt.hlines(0, -100, 10000, linestyles="-", lw =0.5)
    ax1.grid(True)


def plotMomentLatencyAndVelocity(momentLatency, velocity, latency):
    print "///plot Moment Late And Velocity Graph///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file

    fig = plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(momentLatency, "g",)
    #plt.hlines(latency, -100, 10000, linestyles="-", color ="red",lw =0.5)

    ax2.plot(velocity, 'b', linestyle="--")
    fs_label = 8
    #ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    #ax1.set_ylabel('Latency at the each moment[ms]', fontsize = fs_label)
    ax1.set_xlim(0, 1000)
    ax1.set_ylim(-10, 10)
#    ax1.set_ylim(0, 35)


    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-250, 250)
    plt.hlines(0, -100, 10000, linestyle="-", lw =0.5)
    ax1.grid(True)


def plotMomentLatencyAndReal(momentLatency, real, latency):
    print "///plot Moment Late And real Graph///"
    #In 2axis graph, it is hard to paste label. therefore, use eazy draw to ps file

    fig = plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    ax1.plot(momentLatency, "r")
    ax2.plot(real, 'b')
    fs_label = 8
    #ax1.set_xlabel('Time[ms]', fontsize = fs_label)
    #ax1.set_ylabel('Latency at the each moment[ms]', fontsize = fs_label)
    ax1.set_xlim(0, 1000)
    ax1.set_ylim(-10, 35)
    #ax1.set_ylim(-10, 10)
    #plt.hlines(latency, -100, 10000, linestyles="-", color ="red",lw =0.5)

    #ax2.set_ylabel('Angular Velocity[deg/s]', fontsize = fs_label)
    ax2.set_ylim(-20, 20)
    plt.hlines(0, -100, 10000, linestyle="-", lw =0.5)

    ax1.grid(True)




#moment latency is y axis, Azimuth is x axis
def plotMomentLatencyAndDegGraph(aveLatency, stdeLatency, latency, band):
    print "///plotMomentLatencyAndDegGraph///"
    degPerPixel = 0.073848247
    xRange = band/degPerPixel
    x = linspace(-xRange, xRange, (band * 2) + 1)

    yerr1 = stdeLatency #lower
    yerr2 = stdeLatency # upper bound

    fig = plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    ax = fig.add_subplot(111)
    ax.errorbar(x, aveLatency, yerr = [yerr1, yerr2],
                fmt='.', label = "latency")
    ax.set_xlim(-xRange, xRange)
    ax.set_ylim(latency - 3, latency + 3)


    #plt.legend(loc = 'upper right') # show data label
    #plt.xlabel("Azimuth[deg]", fontsize = 20)
    #plt.ylabel("latency at the each the moment[ms]", fontsize = 20)
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(latency, -10000, 10000, linestyles="-", color ="red",lw =0.5)
    #plt.title(CSVFileName[0] + " Latency and Azimuth", fontsize = 20 )
    plt.grid(True)


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




