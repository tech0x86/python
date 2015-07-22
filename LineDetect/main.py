__author__ = 'kento24n452'
# -*- coding: utf-8 -*-
import numpy as np
import pylab as plt
import cv2

# indicate index pos area in img
EXIST_AREA = [0, 1000]
FIRST_DETECT_EDGE_FLAG = False
IMG_NUM = 500


def bgr2rbg(im):
    b,g,r = cv2.split(im)
    im = cv2.merge([r,g,b])
    return im


#load png img from directory. Count is img number.
def loadImage(count, filePathAndName):
    #EX23TW000000.png
    ext = ".png"
    counter = 0
    if count == 0:
        counter = 1
    #0~3
    for i in range(4):
        #pow(x,y): x ^ y
        if count / pow(10,i) >= 1:
            counter += 1
    #make 0 * N
    digit = "0" * (4 - counter)

    loadPath = filePathAndName + digit + str(count) + ext
    print loadPath
    #load img as gray scale
    im_gray = cv2.imread(loadPath,0)
    try:
        len(im_gray)
    except:
        print "open image error!"
        exit(1)
    return im_gray

def convert2BinaryImage(im_gray):
    # グレースケール画像を2値画像に変換
    mask = im_gray > 122
    # 背景画像と同じサイズの配列生成
    im_bi = np.zeros((im_gray.shape[0],im_gray.shape[1]),np.uint8)
    # Trueの部分（背景）は白塗り
    im_bi[mask] = 255
    return im_bi

#judge whether valid img or not by counting white pixel
def detectValidImage(im_bi):
    counter = 0
    i = 0
    # Scan Y=0, x=0 to xSize.
    while i < len(im_bi[0]):
        if im_bi[0][i] == 255:
            counter += 1
        i += 1
    if counter < 5 or 50 < counter :
        print "invalid!"
        return -1
    else:
        return 1

# detect Edge Xpos from Edge image
def scanEdgePos(im):
    #print "///scan Edge Pos///"
    firstExistAreaSens = 50
    existAreaSens = 50
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
    while i < EXIST_AREA[1] or i < len(im[0]):
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
    return round(np.median(edegXPosArray))



def main():
    centerPosArray = []
    width = 0
    prevCenterPos = 300
    i = 0
    #main loop
    fileName = "EX23TW00"
    filePathVir = "../cam/EX23TW0V/"
    fn =  filePathVir + fileName
    while i < IMG_NUM:
        im_gray = loadImage(i, fn)
        im_bi = convert2BinaryImage(im_gray)
        #cv2.imwrite("saveImg/BinaryV" + str(i) + ".bmp",im_bi)
        if detectValidImage(im_bi) == 1:
            im_edge = cv2.Canny(im_bi,50,150,apertureSize = 3)
            #cv2.imwrite("saveImg/EdgeV" + str(i) + ".bmp",im_edge)
            edgeArray = scanEdgePos(im_edge)
            if edgeArray == -1:
                width = -1
                centerPosArray.append(prevCenterPos)
            else:
                width = edgeArray[1] - edgeArray[0]
                centerPos = (edgeArray[0] + 1 +edgeArray[1])/2
                prevCenterPos = centerPos
                print centerPos
                centerPosArray.append(centerPos)
                #print i, width, edgeArray[0], edgeArray[1]
        # if img is invalid img,
        else:
            width = -1
            centerPosArray.append(prevCenterPos)
        i += 1
    x = np.linspace(0, len(centerPosArray), len(centerPosArray))
    plt.plot(x, centerPosArray)
    plt.show()

class lineDetect:
    # should be init ed global when create instance
    def __init__(self):
        print "init!"
        global EXIST_AREA
        EXIST_AREA = [0, 1000]
        global FIRST_DETECT_EDGE_FLAG
        FIRST_DETECT_EDGE_FLAG = False


    def main(self, i, filePathAndName):
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
                print "invalid edge image!"
                width = -1
            else:
                dataArray[0] = edgeArray[0]
                dataArray[1] = edgeArray[1]
                width = edgeArray[1] - edgeArray[0]
                dataArray[2] = width
                print edgeArray[0]
                #print i, width, edgeArray[0], edgeArray[1]
        # if img is invalid img,
        return dataArray



if __name__ == '__main__':
    main()
