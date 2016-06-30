#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'kento24n452'
"""#
This program automatically calcs AveLatency, RMSE, MinRMSE.
1: observe folder by watchdog
2: load proper image
3: use modified conventional method
"""#

import time
from numpy import *
import os
import cv2
import csv
import codecs
import matplotlib.pyplot as plt

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


########Constance#########
#FLAME_MS = 5000.0/IMG_NUM
FLAME_MS = 5000.0/2461
#use it when read from csv data
#DEG_PER_PIX = 48.4555/(656*0.9756097)
#0.07386509146341
DEG_PER_PIX = 48.4555/656.0

###grobal variable###
# indicate index pos area in img
CENTER_DEG = 0
EXIST_AREA = [0, 1000]
#must be initialized before use #
FIRST_DETECT_EDGE_FLAG = False
calcCenterDegFlag = False
realDegArray = []
virDegArray = []
linearIntRealDegArray = []
linearIntVirDegArray = []


#####File NAME and directory structure in recorder PC######
"""#
cam
-Experiment name
--"[Experiment name][R][00000].png"
--"[Experiment name][V][00000].png"
Experiment name: [Render][TW][0 or 1][Pred][0 or 1][L or R]
"""#
# base directory(same to autoMain.py directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))
#experiment name
commonImageFilename = "RealVSRealNo2"
#imageFolder = "/Users/kento24n452/Data/testData/SDKTW0Pred0/"
imageFolder = "/Users/kento24n452/Data/cam/RealVSRealNo2/"

fnR = imageFolder + commonImageFilename + "R"
fnV = imageFolder + commonImageFilename + "V"
CSVFileName = "CSV/" + commonImageFilename + "No"
CSVResultFileName = "CSV/Result/" + commonImageFilename + "No"

def getext(filename):
    return os.path.splitext(filename)[-1].lower()

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if getext(event.src_path) in ('.jpg','.png','.txt'):
            print('%s has been created.' % event.src_path)
            #get timestamp

            print "Timestamp", os.stat(event.src_path).st_mtime
            for line in open('text.txt', 'r'):
                print line
            print "num: ", len(event.src_path)
            # search char from back
            index = event.src_path.rfind("/")
            print "index: ", index
            filename = event.src_path[index + 1:]
            print "filename: ", filename
            print "name: ", filename[:filename.rfind(".")]


    def on_modified(self, event):
        if event.is_directory:
            return
        if getext(event.src_path) in ('.jpg','.png','.txt'):
            print('%s has been modified.' % event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        if getext(event.src_path) in ('.jpg','.png','.txt'):
            print('%s has been deleted.' % event.src_path)

def handleEvent():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, BASEDIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


#check if exist Cmp Deg CSV file
def checkExistCSV(count):
    fn = CSVFileName + str(count)+ ".csv"
    if os.path.exists("CSV") == False:
        print "make directory"
        os.mkdir("CSV")
    if os.path.isfile(fn) == True:
        print "Exist Cmp CSV file! ", fn
        return 1
    else:
        return 0
#check if exist Result CSV file
# RMSE, MinRMSE, Latency
def checkExistResultCSV(count):
    fn = CSVResultFileName + str(count)+ "Result.csv"
    if os.path.exists("CSV") == False:
        print "make CSV directory"
        os.mkdir("CSV")

    if os.path.exists("CSV/Result") == False:
        print "make CSV/Result directory"
        os.mkdir("CSV/Result")

    if os.path.isfile(fn) == True:
        print "Exist Reseult CSV file! ", fn
        return 1
    else:
        return 0


################# DTECT EDGE ####################
#load png img from directory. Count is img number.
def loadImage(count, filePathAndName):
    ext = ".png"
    counter = 0
    if count == 0:
        counter = 1
    #0~4
    for i in range(5):
        #pow(x,y): x ^ y
        if count / pow(10,i) >= 1:
            counter += 1
    #make 0 * N
    digit = "0" * (5 - counter)

    loadPath = filePathAndName + digit + str(count) + ext
    #print loadPath
    #load img as gray scale
    im_gray = cv2.imread(loadPath,0)
    try:
        len(im_gray)
    except:
        print "open image error!"
        exit(1)
    return im_gray

def convert2BinaryImage(im_gray):
    # グレースケール画像を2値画像に変換. set threthould
    mask = im_gray > 70
    # 背景画像と同じサイズの配列生成
    im_bi = zeros((im_gray.shape[0],im_gray.shape[1]),uint8)
    # Trueの部分（背景）は白塗り
    im_bi[mask] = 255
    return im_bi

# detect Edge Xpos from Edge image
def scanEdgePos(im):
    #print "///scan Edge Pos///"
    firstExistAreaSens = 300
    existAreaSens = 100
    edgePos = []
    centerXPos = int(len(im[0])/2)
    #print EXIST_AREA[0], EXIST_AREA[1]

    if FIRST_DETECT_EDGE_FLAG == False:
        # scan this area at first
        global EXIST_AREA
        EXIST_AREA[0] = centerXPos - firstExistAreaSens
        EXIST_AREA[1] = centerXPos + firstExistAreaSens
        global FIRST_DETECT_EDGE_FLAG
        FIRST_DETECT_EDGE_FLAG = True
    i = EXIST_AREA[0]
    while i < EXIST_AREA[1] and i < len(im[0]):
        # white is 255, black is 0
        if im[0][i] == 255:
            edgePos.append(calcMidXPosOfVertLine(im, i))
            #skip scanned pixels or error pixels
            i += 3
        else:
            i += 1
    # update exist area
    if len(edgePos) == 2:
        centerXPos = int(round((edgePos[1] + edgePos[0]) / 2))
        global EXIST_AREA
        EXIST_AREA[0] = centerXPos - existAreaSens
        EXIST_AREA[1] = centerXPos + existAreaSens
        return edgePos
    else:
        return -1

#calc midian X Pos of  vertical edge line
def calcMidXPosOfVertLine(im, edgePos):
    #print "///calc Midian XPos///"
    scanSens = 3
    i = 1
    j = edgePos - scanSens
    edegXPosArray = []
    if j < 0:
        j = 0

    #scan Y Pos
    while i < len(im):
        #scan X pos. edgePos - sens < X < edgePos + sens
        j = edgePos - scanSens
        while  j < edgePos + scanSens or j < len(im[0]):
            if im[i][j] == 255:
                edegXPosArray.append(j)
                break
            j += 1
        i += 1
    #print round(np.median(edegXPosArray))
    return round(median(edegXPosArray))


#judge whether valid img or not by counting white pixel
def detectValidImage(im_bi):
    counter = 0
    i = 0
    # Scan Y=0, x=0 to xSize.
    while i < len(im_bi[0]):
        if im_bi[0][i] == 255:
            counter += 1
        i += 1
    if counter < 5 or 200 < counter :
        #print "invalid img!" , counter
        return -1
    else:
        return 1


def detectLine(i, filePathAndName):
    width = 0
    #[0] edge[0], [1] edge[1], [2] width
    dataArray = [0, 0, 0]
    #main loop
    im_gray = loadImage(i, filePathAndName)
    im_bi = convert2BinaryImage(im_gray)
    #cv2.imwrite("saveImg/BinaryV" + str(i) + ".bmp",im_bi)
    if detectValidImage(im_bi) == 1:
        im_edge = cv2.Canny(im_bi,50,150,apertureSize = 3)
        #cv2.imwrite("saveImg/EdgeV" + str(i) + ".bmp",im_edge)
        edgeArray = scanEdgePos(im_edge)
        if edgeArray == -1:
            #print "invalid edge image!"
            width = -1
        else:
            dataArray[0] = edgeArray[0]
            dataArray[1] = edgeArray[1]
            width = edgeArray[1] - edgeArray[0]
            dataArray[2] = width
            #print edgeArray[0]
            #print i, width, edgeArray[0], edgeArray[1]
    # if img is invalid img,
    return dataArray

#################END  DTECT EDGE ####################


#########Calc Azmith[deg]#############

# Set center deg
def calcCenterDeg(leftEdge, rightEdge, width):
    if calcCenterDegFlag == False:
        #check whether valid data
        if 15 < width and width < 40:
            print "find cente degree", leftEdge + width/2.0
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

#secoundary calc center deg
#UPDATE linearIntDegArray
def calcCenterDeg2():
    print "calc center @2nd"
    realCenter = average(linearIntRealDegArray)
    virCenter = average(linearIntVirDegArray)
    virOffset = realCenter - virCenter

    i=0
#   global linearIntRealDegArray
    while i < len(linearIntRealDegArray):
        linearIntRealDegArray[i] -= realCenter
        i+=1
    i=0
#    global linearIntVirDegArray
    while i < len(linearIntVirDegArray):
        linearIntVirDegArray[i] -= virCenter + virOffset
        i+=1


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

#image filename ex) [experiment name]R, start number ex) 0 or 2070
#Return end number of image sequence
def searchImage(fn, startNum):
    digitNum = 5
    counter = startNum
    ext = ".png"

    prevTimestamp = 0
    checkTimeSens = 10 #second

    while counter < 100000:# not over 100k
        number = str( "0" * (digitNum - len(str(counter))) )
        checkFilename = fn + number + str(counter) + ext
        #print checkFilename

        if os.path.isfile(checkFilename) == False:
            print "file dose not exist!", checkFilename
            return counter - 1

        if prevTimestamp == 0:
            prevTimestamp = os.stat(checkFilename).st_mtime

        timestamp = os.stat(checkFilename).st_mtime
        diff = abs(prevTimestamp - timestamp)

        if diff > checkTimeSens:
            print "detect another sequence image!"
            print "end sequence Num: ", counter - 1, "diff: ",diff
            return counter - 1

        prevTimestamp = timestamp
        counter += 1

def controlReadImgData():
    startNum = 0
    seqCount = 0
    endNum = 0
    #expResult = []# 2D array constructed (RMSE,MinRMSE@0.01ms,AveLatency@0.01ms)

    while seqCount < 99:
        expResult = []
        initialize()
        #result CSV file does NOT exist
        if checkExistResultCSV(seqCount) == 0:
            #CSV file exist
            if checkExistCSV(seqCount):
                readCSVData(seqCount)
                startNum = searchImage(fnR, startNum) + 1
            #result csv & csv file do not exist. read img
            else:
                endNum = searchImage(fnR, startNum)
                if endNum + 1 == startNum:
                    print "End sequence experiment Data!",seqCount
                    break
                global FLAME_MS
                FLAME_MS = 5000.0 / (endNum - startNum)
                print "FPS: ", (endNum - startNum) / 5.0
                readData(startNum, endNum)
                calcVirLinearInt(virDegArray)
                calcVirLinearInt(realDegArray)
                calcLinearInt(linearIntRealDegArray, realDegArray)
                calcLinearInt(linearIntVirDegArray, virDegArray)
                writeCmpDegData(seqCount)
                startNum = endNum + 1
            expResult.append(controlCalcVal())
            writeResultData(seqCount, expResult)
        else: #result file exist
            startNum = searchImage(fnR, startNum) + 1
        seqCount += 1


#read img data from LineDetect Module
def readData(startNum, EndNum):

    print "startNum: ", startNum,"endNum", EndNum
    counter = startNum

    print "///read Real Cam Data///"
    while counter < EndNum + 1:
        #dataArray[0]:edge[0], dA[1]:edge[1], dA[2]:width
        dataArray = detectLine(counter, fnR)
        calcCenterDeg(dataArray[0], dataArray[1], dataArray[2])
        deg = calcCamDeg(dataArray[0], dataArray[1], dataArray[2])
        realDegArray.append(deg)
        counter += 1
    print "EleNum = %d" %len(realDegArray)

    print "///read Virtual Cam Data///"
    # Initialize Flag
    global calcCenterDegFlag
    calcCenterDegFlag = False
    global FIRST_DETECT_EDGE_FLAG
    FIRST_DETECT_EDGE_FLAG = False
    counter = startNum
    while counter < EndNum + 1:
        dataArray = detectLine(counter, fnV)
        calcCenterDeg(dataArray[0], dataArray[1], dataArray[2])
        deg = calcCamDeg(dataArray[0], dataArray[1], dataArray[2])
        virDegArray.append(deg)
        counter += 1
    print "EleNum = %d" %len(virDegArray)

    print "real: ", len(realDegArray),"vir: ", len(virDegArray)
    if len(realDegArray) != len(virDegArray):
        print "Real cam data num and Vir cam data num are not same!!"
        exit(1)
    print "read done"
    return 1

def initialize():
    #must be initialize before use #
    print "initialize Flag!"
    global FIRST_DETECT_EDGE_FLAG
    FIRST_DETECT_EDGE_FLAG = False
    global calcCenterDegFlag
    calcCenterDegFlag = False
    global realDegArray
    realDegArray = []
    global virDegArray
    virDegArray = []
    global linearIntRealDegArray
    linearIntRealDegArray = []
    global linearIntVirDegArray
    linearIntVirDegArray = []


class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL
#    delimiter = "¥t"

#read CSV file(row[0]:real IntP deg, row[1]: virtual IntP deg)
def readCSVData(count):
    fn = CSVFileName + str(count) + ".csv"
    csvFile = codecs.open(fn, "rb","utf-8")
    reader = csv.reader(csvFile, CustomFormat())
    for row in reader:
        linearIntRealDegArray.append(float(row[0]))
        linearIntVirDegArray.append(float(row[1]))
    print "Done Read IntP CSV File! Num = %d" %len(linearIntVirDegArray)


#output data to CSV file
def writeCmpDegData(seqCount):
    print "///write CmpCSV data///"
    tempArray = []
    i = 0
    fn = CSVFileName + str(seqCount) + ".csv"

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

def writeResultData(count, *data):
    print "///write Result data///"
    tempArray = []
    fn = CSVResultFileName + str(count) + "Result.csv"
    #get URI with optional setting
    csvFile = codecs.open(fn, "w", "utf-8")
    #disignate format
    writer = csv.writer(csvFile,CustomFormat() )

    # Write Linaer Interpolation Real and Virtual data (ms)
    # data num of Real and Vir are same
    i = 0
    for result in data:
        for num in result:
            for x in num:
                tempArray.append(x)
            writer.writerow(tempArray)
            tempArray = []
        i+=1
    csvFile.close()
    print "write done:" , fn



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
    print "NAPos" ,detectNAPos(array,0)

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

# calc Liner Interpolation,
# and store it to linerInt array in **0.01ms** order
def calcLinearInt2():
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
    print "real Cam in [0.01]ms:", len(linearIntDegArray)
    #print linearIntDegArray
    return linearIntDegArray

#########END Calc Linear Interpolation############


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

#graph fot verification
def plotTwoElementGraph(point1, name1, point2, name2):
    print "///plot Two Graph///"
    ylim = 20
    #plt.figure(figsize = (figSize[0]/2.54, figSize[1]/2.54))#inch
    x1 = linspace(0, len(point1), len(point1))
    plt.plot(x1, point1, label = name1)
    x2 = linspace(0, len(point2), len(point2))
    plt.plot(x2, point2, label = name2, linestyle="--")

    #plt.legend(loc = 'upper right') # show data label
    #plt.xlabel("Time[ms]")
    #plt.ylabel("Azmith[deg]")
    #draw dashed line. (y[range], -x length, x length , style)
    plt.hlines(0, -100, 10000, linestyles = "-", lw = 0.5)
    plt.ylim(-ylim, ylim)
    plt.xlim(0, 1000)
    plt.grid(True)

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


#calc latency more resolution
#ave latanecy >= 1
def calcLatency2(base, comparison, aveLatency):
    print "///calc latency///"
    scanArea = 50
    minusShift = (aveLatency * 100) - scanArea# x0.01ms
    plusShift = (aveLatency * 100) + scanArea + 1
    calcArray = []
    resultArray = [0,0]# MinRMSE, latency
    #index start at 0, shift start at - 10ms. So, offset needed.
    #Index of Min RMSE is latency
    #example: 900 ~ 1100 lantency:10ms
    for i in range(minusShift, plusShift):
        print "RMSE step:", i,
        rmse = calcRMSE2(base, comparison, i)
        calcArray.append(rmse)
    latency = calcArray.index(min(calcArray)) + minusShift
    latency /= 100.0
    print ""
    #print "Min RMSE:", min(calcArray), "deg"
    #print "latency:", latency, "ms"

    resultArray[0] = min(calcArray)
    resultArray[1] = latency
    return resultArray


def controlCalcVal():
    #### RMSE ####
    xMinRmse = -10
    xMaxRmse = 40 + 1
    RMSEArray = []
    resultArray = [0,0,0]#RMSE, MinRMSE, RemError

    calcRealCamScale()
    rmse = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, 0)
    resultArray[0] = rmse

    #print "Modified RMSE: %f" %rmse
    for i in range(xMinRmse, xMaxRmse):
        rmse = calcRMSE(linearIntRealDegArray, linearIntVirDegArray, i)
        RMSEArray.append(rmse)
    #print "Min RMSE@1ms :%f" % min(RMSEArray)
    latency = RMSEArray.index(min(RMSEArray)) + xMinRmse
    print "latency: %d ms" % latency

    #expand time reso to 0.01ms in Real
    linearInt2RealDegArray = calcLinearInt2()
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

    tmpArray = calcLatency2(linearInt2RealDegArray, discreteVirCamArray, latency)
    #tmpArray = [1,1]
    resultArray[1] = tmpArray[0]# Min RMSE
    resultArray[2] = tmpArray[1]# Latency @0.01ms
    print "/////////////////////////"
    print "RMSE[deg]: ",resultArray[0],"Min RMSE[deg]: ", resultArray[1],"aveLatency[ms]: ",resultArray[2]
    print "/////////////////////////"
    return resultArray


if __name__ == "__main__":
    print "///mainFunc///"
    controlReadImgData()

