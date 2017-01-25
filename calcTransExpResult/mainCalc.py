### This is a program for statiscally calculating DK2 transition experiment result###
### add plot errorbar-graph function, Turkey HSD Test
### 16/1/25

from numpy import *
import os
import csv
import codecs
import matplotlib.pyplot as plt
from statsmodels.stats.multicomp import pairwise_tukeyhsd

#experimentName = "SDK14RightD20"
# RealVSRealD20: [deg]
# index=0: real vs real, 1~4: Left, 5~9: Right
experimentNameArray = ["RealVSRealD20",
                       "SDK044LeftT0P0D20_4", "SDK044LeftT0P1D20_2", "SDK044LeftT1P1D20_3", "SDK14LeftD20_4",
                       "SDK044RightT0P0D20", "SDK044RightT0P1D20", "SDK044RightT1P1D20", "SDK14RightD20_2"
                       ]

##Min RMSE: real vs virtual in static
#preExperimentMinRMSEArray = [0.137]
#preExperimentMinRMSEErrorArray = [0.0]


#experimentName = "SDK044LeftT0P0D20_4"
#experimentName = "RealVSRealD20"
SearchCSVFilePath = "/Users/kento24n452/Data/Result/Transition/"
SaveCSVFilePath = "/Users/kento24n452/GitHub/python/calcTransExpResult/StatsCSV/"
ValidMinRMSESens = 2
ValidLatencySens = 4

figSize = [20, 15] #X,Y cm


class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL

#search result CSV file
#return fileName Array
def searchCSVFile(searchName):
    print "///search Result CSV files///"
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
            if ext == ".csv" and searchName in fileName:
                #print CSVFileCounter, ":", file
                fileArray.append(filePathAndName)
                fileNameArray.append(fileName)
                CSVFileCounter += 1
        print "CSV file num",CSVFileCounter
    return fileNameArray

def writeResultData(counter, *data):
    print "///write Result data///"
    tempArray = []
    fn = SaveCSVFilePath + experimentNameArray[counter] + "StatsResult.csv"
    #get URI with optional setting
    csvFile = codecs.open(fn, "w", "utf-8")
    #disignate format
    writer = csv.writer(csvFile,CustomFormat() )

    # Write Linaer Interpolation Real and Virtual data (ms)
    # data num of Real and Vir are same
    for result in data:
        for num in result:
            for x in num:
                tempArray.append(x)
            writer.writerow(tempArray)
            #print tempArray
            tempArray = []


    csvFile.close()
    print "write done:" , fn

#return array[3]: RMSE, Min RMSE, Latency
def readCSVData(filenameArray):
    print "///read Each Experiment Result CSV///"
    i = 0

    results = []
    while i < len(filenameArray):
        # RMSE, Min RMSE, Latency
        tmp = []
        fn = SearchCSVFilePath + filenameArray[i] + ".csv"
        csvFile = codecs.open(fn, "rb","utf-8")
        reader = csv.reader(csvFile, CustomFormat())
        for row in reader:
            tmp.append(float(row[0]))
            tmp.append(float(row[1]))
            tmp.append(float(row[2]))
        results.append(tmp)
        i+=1
    #print "Experiment count", len(results)
    return results


#return result[ array[]*6 ]: RMSE, Min RMSE, Latency, Stats RMSE, Stats Min, Stats Latency
def readStatsCSVData(filename):
    print "///read Stats result CSV///"
    i = 0
    RMSE = []
    minRMSE = []
    latency = []
    #[]:ave, std, stde
    statsRMSE = []
    statsMinRMSE = []
    statsLatency = []
    fn = SaveCSVFilePath + filename + "StatsResult.csv"
    csvFile = codecs.open(fn, "rb","utf-8")
    reader = csv.reader(csvFile, CustomFormat())
    for row in reader:
        RMSE.append(float(row[0]))
        minRMSE.append(float(row[1]))
        latency.append(float(row[2]))
        if i < 3:
            statsRMSE.append(float(row[3]))
            statsMinRMSE.append(float(row[4]))
            statsLatency.append(float(row[5]))
        i += 1
    result = [RMSE, minRMSE, latency, statsRMSE, statsMinRMSE, statsLatency]
    #print result
    return result



# return index array of invalid data
def detectInvalidData(result):
    # result num
    # find invalid index
    latencyArray = []
    MinRMSEArray = []
    indexArray = []
    validData = []


    # summarize
    # exp[3]: RMSE, Min RMSE, Latency
    for exp in result:
        latencyArray.append(exp[2])
        MinRMSEArray.append(exp[1])
    midLatency = median(latencyArray)
    midMinRMSE = median(MinRMSEArray)

    #detect Invailid data index
    index = 0
    for exp in result:
        invalidFlag = 0

        # latency check
        if abs(exp[2] - midLatency) > ValidLatencySens:
            print "invalid Latency: ", exp[2]
            invalidFlag = 1

        # min RMSE check
        if abs(exp[1] - midMinRMSE) > ValidMinRMSESens:
            print "invalid min RMSE: ", exp[1]
            invalidFlag = 1

        if invalidFlag == 1:
            indexArray.append(index)

        else:
            validData.append(exp)
        index += 1

    #print "invalid data count: ", len(indexArray)
    #print "invalid data index: ", indexArray
    #print "valid data count: ", len(validData)
    #print validData
    return validData


def calcStatictic(counter, validData):

    RMSEArray = []
    minRMSEArray = []
    aveLatencyArray = []

    #[3]: average, standard daviation, standard error
    statsRMSE = []
    statsMinRMSE = []
    statsLatency = []


    #result num
    #RMSE, Min RMSE, Latency
    for exp in validData:
        #print exp
        RMSEArray.append(exp[0])
        minRMSEArray.append(exp[1])
        aveLatencyArray.append(exp[2])

    dataCount = len(validData)

    statsRMSE.append(round(average(RMSEArray), 2))
    statsRMSE.append(round(std(RMSEArray), 3))
    statsRMSE.append(round(statsRMSE[1]/sqrt(dataCount), 3))

    statsMinRMSE.append(round(average(minRMSEArray), 2))
    statsMinRMSE.append(round(std(minRMSEArray), 3))
    statsMinRMSE.append(round(statsMinRMSE[1]/sqrt(dataCount), 3))

    statsLatency.append(round(average(aveLatencyArray), 2))
    statsLatency.append(round(std(aveLatencyArray), 3))
    statsLatency.append(round(statsLatency[1]/sqrt(sqrt(dataCount)), 3))

    data = [RMSEArray, minRMSEArray, aveLatencyArray, statsRMSE, statsMinRMSE, statsLatency]

    col = setDataForCSV(data)
    writeResultData(counter, col)

    print "///", experimentNameArray[counter]
    print "valid data num: ", dataCount
    print "Average, Standard deviation, Standard error"
    print "RMSE[mm]:", statsRMSE
    print "min RMSE[mm]:", statsMinRMSE
    print "ave latency[ms]:", statsLatency

# return colom data
#(0<= i<= n)
#////CSV Format Below
# RMSEi, MinRMSEi, aveLatencyi, AveRMSE, Ave MinRMSE, AveLateny
# RMSEi, MinRMSEi, aveLatencyi, StdRMSE, Std MinRMSE, StdLateny
# RMSEn, MinRMSEn, aveLatencyn
def setDataForCSV(*data):
    print "//set CSV for writer//"
    colom = []
    for result in data:
        #print "result:",result
        #print "result[0]== RMSEArray:", result[0]
        #print "result[0][0]== RMSE val:", result[0]
        i = 0
        tmpCol = []
        while i < len(result[0]):
            j=0
            tmpCol = []

            # 6 colum
            if i < 3:
                while j < 6:
                    tmpCol.append(result[j][i])
                    #print "tmp1", tmpCol
                    j += 1
            # 3 colum
            else:
                while j < 3:
                    tmpCol.append(result[j][i])
                    #print "tmp2", tmpCol
                    j += 1
            i += 1
            #print "tmpCol", tmpCol
            colom.append(tmpCol)
    return colom

#check if exist Cmp Deg CSV file
def checkExistenceOfStatsCSV(name):
    print "check existence:", name
    fn = SaveCSVFilePath + name + "StatsResult.csv"

    if os.path.exists("StatsCSV") == False:
        print "make directory"
        os.mkdir("StatsCSV")

    if os.path.isfile(fn) == True:
        print "Exist StatsCSV file! ", fn
        return 1
    else:
        return 0

def setDataForTurkey(totalResult):
    minRMSE = []
    latency = []

    i = 0
    for exp in totalResult:
        # skip Verify Experiment result
        if i != 0:
            minRMSE.append(exp[1])
            latency.append(exp[2])
            #print "min RMSE", exp[1]
        i += 1

def setDataForErrorGraph(totalResult):
    aveMinRMSE = []
    stdeMinRMSE = []
    aveLatency = []
    stdeLatency = []
    result = []

    for exp in totalResult:
        #exp[5] == Stats latency(ave, std, stde)
        #exp[5][0] == ave latency
        aveMinRMSE.append(exp[4][0])
        stdeMinRMSE.append(exp[4][2])
        aveLatency.append(exp[5][0])
        stdeLatency.append(exp[5][2])
    #print "ave latency array", aveLatency
    result.append(aveMinRMSE)
    result.append(stdeMinRMSE)
    result.append(aveLatency)
    result.append(stdeLatency)
    # min RMSE(ave, stde), latency(ave, stde)

    print "ave min RMSE, stde min RMSE, ave latency, stde latency"
    print result
    return result

def plotLatencyErrorBarGraph(valueArray, errorArray):
    print "///plot latency error bar graph///"
    x = linspace(1, len(valueArray), len(valueArray))
    plt.figure(figsize=(figSize[0] / 2.54, figSize[1] / 2.54))  # inch

    plt.bar(x, valueArray,align="center", color = "green")
    plt.errorbar(x, valueArray, yerr = errorArray,lw = 1,color = "black", capsize=5)

    plt.xlim(1 -1, len(valueArray) +1)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(-3, 40)
    plt.grid(True)
    plt.savefig("latencyErrorGraph.eps")
    plt.show()
    plt.clf()


def plotMinRMSEErrorBarGraph(valueArray, errorArray):
    print "///plot min RMSE error bar graph///"
    x = linspace(1, len(valueArray), len(valueArray))
    plt.figure(figsize=(figSize[0] / 2.54, figSize[1] / 2.54))  # inch

    plt.bar(x, valueArray,align="center", color = "green")
    plt.errorbar(x, valueArray, yerr = errorArray,lw = 1,color = "black", capsize=5)

    plt.xlim(1 -1, len(valueArray) +1)
    plt.hlines(0, -100, 10000, linestyles="-")
    plt.ylim(0, 1.6)
    plt.grid(True)
    plt.savefig("minRMSEErrorGraph.eps")
    plt.show()
    plt.clf()


if __name__ == "__main__":
    print "///mainFunc///"
    resultOfExperimentSeries = []

    i = 0
    for name in experimentNameArray:
        # statical CSV file found
        if checkExistenceOfStatsCSV(name):
            resultOfExperimentSeries.append(readStatsCSVData(name))
        else:
            data = searchCSVFile(name)
            result = readCSVData(data)
            validData = detectInvalidData(result)
            resultOfExperimentSeries.append( calcStatictic(i, validData) )
        i += 1

    twoGraphData = setDataForErrorGraph(resultOfExperimentSeries)
    # (value array, error array)
    #plotMinRMSEErrorBarGraph(twoGraphData[0], twoGraphData[1])
    #plotLatencyErrorBarGraph(twoGraphData[2], twoGraphData[3])
    setDataForTurkey(resultOfExperimentSeries)
