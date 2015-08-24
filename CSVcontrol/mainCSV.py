__author__ = 'kento24n452'
# -*- coding: utf-8 -*-
import csv
import codecs
from numpy import *
import matplotlib.pyplot as plt
import sys
import os.path

######parameters########
IMG_NUM = 2070
FLAME_MS = 5000.0/IMG_NUM
#use it when read from csv data
#DEG_PER_PIX = 48.4555/(656*0.9756097)
DEG_PER_PIX = 48.4555/656.0
#0.07386509146341
CENTER_DEG = 0

#CSV file name, Graph title name, Expetiment name
FILE_NAME = "OWDemoTW0Pred0"
LIN_INT_FN = "CmpCSV/" + FILE_NAME + "LinearInt.csv"

#Graph, CSV
FILE_PATH = "VRSJCsvData/"
SAVE_FILE_PATH ="Graph/"

#Image name without 4digi number
IMG_FILE_NAME = "EX23TW00"

###grobal variable###
realDegArray = []
virDegArray = []
linearIntRealDegArray = []
linearIntVirDegArray = []
RMSEArray = []
calcCenterDegFlag = False
RMSEResultVal = []

########CSV operate##########
class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL
    #delimiter = '\t'

def readCSVData():

    print "///read data from CSV///"
    print "/read RealCamArray/"
    filename = FILE_PATH + FILE_NAME + "R.csv"
    csvFile = codecs.open(filename, "rb","utf-8")
    try:
        len(csvFile)
    except:
        print "open csv file Error!"
        exit(1)
    reader = csv.reader(csvFile,CustomFormat())
    for row in reader:
        #read data as string from csv file
        calcCenterDeg(row[0], row[1], int(row[2]))
        deg = calcCamDeg(row[0], row[1], int(row[2]))
        realDegArray.append(deg)

    print "EleNum = %d" %len(realDegArray)
    #print realDegArray

    # Initialize Flag
    global calcCenterDegFlag
    calcCenterDegFlag = False
    print "/read VirtualCamArray/"
    filename = FILE_PATH + FILE_NAME + "V.csv"
    csvFile = codecs.open(filename, "rb","utf-8")
    reader = csv.reader(csvFile,CustomFormat())

    for row in reader:
        #read data as string from csv file
        calcCenterDeg(row[0], row[1], int(row[2]))
        deg = calcCamDeg(row[0], row[1], int(row[2]))
        virDegArray.append(deg)

    print "EleNum = %d" %len(virDegArray)
    #print virDegArray
    print "read done"

def readLinearIntCSVData():
    print "///read LinInt CSV///"
    csvFile = codecs.open(LIN_INT_FN, "rb","utf-8")
    reader = csv.reader(csvFile, CustomFormat())
    for row in reader:
        linearIntRealDegArray.append(float(row[0]))
        linearIntVirDegArray.append(float(row[1]))
    print "RealCam ElementNum = %d" %len(linearIntRealDegArray)
    print "VirCam ElementNum = %d" %len(linearIntVirDegArray)
    print "LinInt CSV read done"

#check if exist Linear Interpolation CSV file
def checkExistLinIntCSV():
    if os.path.isfile(LIN_INT_FN) == True:
        print "Exist CSV file!."
        return 1
    else:
        return 0

#read data from LineDetect Module
def readData():
    #add new directory which has .py file
    sys.path.append("../LineDetect/")
    import main
    print "///read data from Module///"
    #captured image file name
    #/home/Data/
    filePathVir = "../../../Data/cam/" + FILE_NAME + "V/"
    filePathReal = "../../../Data/cam/" + FILE_NAME + "R/"
    print "/read RealCamData/"
    fn = filePathReal + IMG_FILE_NAME
    i = 0
    #create instance
    lineDetectClassR = main.lineDetect()

    if os.path.isfile(fn + "0000.png") == False:
        print fn + "0000.png"
        print "open image error!"
        exit(0)

    elif os.path.isfile(fn + str(IMG_NUM - 1) + ".png") == False:
        print fn + str(IMG_NUM - 1) + ".png"
        print "MAX image number error!"
        exit(0)

    while i < IMG_NUM:
        # dataArray[0]:edge[0], dA[1]:edge[1], dA[2]:width
        dataArray = lineDetectClassR.main(i, fn)
        calcCenterDeg(dataArray[0], dataArray[1], dataArray[2])
        deg = calcCamDeg(dataArray[0], dataArray[1], dataArray[2])
        realDegArray.append(deg)
        i += 1
    print "EleNum = %d" %len(realDegArray)
    #print realDegArray

    print "/read VirtualCamData/"
    # Initialize Flag
    global calcCenterDegFlag
    calcCenterDegFlag = False
    i = 0
    fn = filePathVir + IMG_FILE_NAME

    if os.path.isfile(fn + "0000.png") == False:
        print fn + "0000.png"
        print "open image error!"
        exit(0)
    #create instance
    lineDetectClassV = main.lineDetect()

    while i < IMG_NUM:
        dataArray = lineDetectClassV.main(i, fn)
        calcCenterDeg(dataArray[0], dataArray[1], dataArray[2])
        deg = calcCamDeg(dataArray[0], dataArray[1], dataArray[2])
        virDegArray.append(deg)
        i += 1
    print "EleNum = %d" %len(virDegArray)
    #print virDegArray
    print "read done"
    return 1

#output data to CSV file
def writeData():
    print "///write CmpCSV data///"
    tempArray = []
    i = 0
    fn = "CmpCSV/" + FILE_NAME + "LinearInt.csv"
    #get URI with optional setting
    csvFile = codecs.open(fn, "w", "utf-8")
    #disignate format
    writer = csv.writer(csvFile,CustomFormat() )

    # Write Linaer Interpolation Real and Virtual data (ms)
    # data num of Real and Vir are same
    while i < len(linearIntRealDegArray):
        tempArray.append(linearIntRealDegArray[i])
        tempArray.append(linearIntVirDegArray[i])
        writer.writerow(tempArray)
        tempArray = []
        i +=1
    csvFile.close()
    print "write done:" , fn

#########Calc Azmith[deg]#############

# Set center deg
def calcCenterDeg(leftEdge, rightEdge, width):
    if calcCenterDegFlag == False:
        #check whether valid data
        if 10 < width and width < 40:
            sum = float(leftEdge) + float(rightEdge)
            ave = sum / 2
            deg = ave * DEG_PER_PIX
            #allow to write global Value
            global CENTER_DEG
            #set center Deg
            CENTER_DEG = deg
            #print "centerDeg %f" %CENTER_DEG
            global calcCenterDegFlag
            calcCenterDegFlag = True

#calculate Cam Azmith[deg]. Invalid data is converted to "NA"
def calcCamDeg(leftEdge, rightEdge, width):
    if calcCenterDegFlag == False:
        return 0

    #if valid data,
    elif 10 < width and width < 40:
        sum =  float(leftEdge) + float(rightEdge)
        ave = sum/2
        deg = ave * DEG_PER_PIX
        return deg - CENTER_DEG

    else:
        return "NA"

# detect head of NA Pos in array from present Pos.
def detectNAPos(array, presentPos):
    NAPos = presentPos
#    array = [0,4,5,"NA",7]

    while NAPos < len(array):
        if array[NAPos] == "NA":
            #print "detect NA at %d" %NAPos
            break
        NAPos += 1

    return NAPos

# detect tail of NA Pos in array from head of NA Pos
def detectNAEndPos(array, NAStartPos):
    NAEndPos = NAStartPos

    while NAEndPos < len(array):
        if array[NAEndPos] != "NA":
            #print "End NA at %d" % (NAEndPos - 1)
            break
        NAEndPos += 1

    return NAEndPos

#########Calc Linear Interpolation############

# calc Linear Interpolation of VirtualCam Deg array[camFlame]
def calcVirLinearInt(array):
    print "///calc VirLinearInt///"
    counter = 0

    #main loop. calc while end of elementNum
    while counter < len(array):
        NAPos = detectNAPos(array, counter)
        x0 = NAPos - 1
        x1 = detectNAEndPos(array, NAPos)

        #deal with over array
        if x1 > len(array) - 1:
            while NAPos < len(array):
                #fill rests of array with last valid data
                array[NAPos] = array[NAPos - 1]
                print "Last NA Pos %d" % NAPos
                NAPos += 1
            break

        x = x0 + 1
        # x1 - x0
        x1Mx0 = x1 - x0
        #
        '''
        print "x0:%d" %x0 ,
        print "x1:%d" %x1 ,
        print "deg[x0]:%1.2f"%array[int(x0)] ,
        print "deg[x1]:%1.2f"%array[int(x1)]
        '''
        #
        # y1 - y0
        y1My0 = float(array[int(x1)]) - float(array[int(x0)])

        #sub loop.
        while x < x1:
            #calc Liner Interpolation
            linearInt = array[int(x0)]
            linearInt += (x - x0) * y1My0 / x1Mx0
            array[x] = linearInt
            #print "ms: %d" % x  ,
            #print linerInt ,
            #print "count: %d" % counter
            x += 1
            counter += 1
        counter += 1

    print "VirLinearInt Calc done. count = %d" %counter
    print len(array)
    #print array

# calc Liner Interpolation,
# and store it to linerInt array in 1ms order
def calcLinearInt(linearIntDegArray, camDegArray):
    print "///calc LinearInt///"
    #Start Deg Pos at 0ms. same to first deg data
    linearIntDegArray.append(camDegArray[0])

    #counter will go 0 to element num of camDegArray - 1
    counter = 0

    # Set same value until first CamFlame
    # Fill head-array with data between 0ms to Nms until valid data
    # math.floor : remove Fig below 1st decimal place
    whileCounter = 0
    while whileCounter < math.floor(FLAME_MS):
        linearIntDegArray.append(camDegArray[0])
        whileCounter += 1
        #print "ms: %d" % whileCounter

    #main loop. calc while elementNum
    while counter + 1 < len(camDegArray):
        x0 = FLAME_MS * (counter + 1)
        x = int(math.floor(x0) + 1)

        #sub loop. loop while  x < (omited x1)
        while x <= int( math.floor(FLAME_MS * (counter + 2)) ):
            #y1 - y0
            y1My0 = camDegArray[int(counter + 1)] - camDegArray[int(counter)]
            #calc Liner Interpolation
            linerInt = camDegArray[int(counter)]
            # x1 - x0
            x1Mx0 = FLAME_MS
            linerInt += (x - x0) * y1My0 / x1Mx0
            linearIntDegArray.append(linerInt)
            #print "ms: %d" % x  ,
            #print linerInt ,
            #print "count: %d" % counter
            x += 1
        counter += 1
    print "LinearInt Calc done. count = %d" % counter
    print len(linearIntDegArray)
    #print linearIntDegArray

########Calc value##########

# Control values. RMSE, MinRMSE, AveDiff, ABSAveDiff, ABSStdDiff, ABSStdeDiff, Latency
def controlCalcVal():
    xMinRmse = -10
    xMaxRmse = 40 + 1
    print "///Calc Values///"
    print "-----------%s----------" %FILE_NAME
    diff = calcDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray)
    plotDiffGraph(diff)
    plt.savefig(FILE_PATH + SAVE_FILE_PATH + FILE_NAME + "Diff2.png")
    #plt.show()
    plt.clf()
    AbsDiffSTD = std(calcABSDiffOfDeg(linearIntRealDegArray, linearIntVirDegArray))
    #standard deviation
    print "AbsDiffSTD: %f" %AbsDiffSTD
    AbsDiffSTDE = AbsDiffSTD/sqrt(len(linearIntRealDegArray))
    #standard error
    print "AbsDiffSTDE: %f" %AbsDiffSTDE
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
    plt.savefig(FILE_PATH + SAVE_FILE_PATH + FILE_NAME + "RMSE2.png")
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

def plotGraph(point, name):
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
    #plt.title(FILE_NAME + " Real and Virtual Azmith", fontsize = 20 )

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
    plt.title(FILE_NAME + " Difference Azmith", fontsize = 20 )


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
    #plt.title(FILE_NAME + "Shift Time and RMSE", fontsize = 20 )


if __name__ == "__main__":
    print "///mainFunc///"
    if checkExistLinIntCSV() == 0:
        readData()
        calcVirLinearInt(virDegArray)
        calcLinearInt(linearIntRealDegArray, realDegArray)
        calcLinearInt(linearIntVirDegArray, virDegArray)
        writeData()
    else:
        readLinearIntCSVData()
    '''#
    plotGraph(linearIntRealDegArray, "Real")
    plotGraph(linearIntVirDegArray, "Virtual")
    plt.savefig(FILE_PATH + SAVE_FILE_PATH + FILE_NAME + "RealAndVirtual2.png")
    plt.show()
    plt.clf() #delete graph
    controlCalcVal()
    #'''
