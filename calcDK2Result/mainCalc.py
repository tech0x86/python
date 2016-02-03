from numpy import *
import os
import csv
import codecs
import matplotlib.pyplot as plt

#experiment name
experimentName = "SDKTW0Pred0L"
SearchCSVFilePath = "/Users/kento24n452/Data/Result/"
ValidMinRMSESens = 1
ValidLatencySens = 28



class CustomFormat(csv.excel):
    quoting   = csv.QUOTE_ALL

#search result CSV file
#return fileName Array
def searchCSVFile():
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
            if ext == ".csv" and experimentName in fileName:
                print CSVFileCounter, ":", file
                fileArray.append(filePathAndName)
                fileNameArray.append(fileName)
                CSVFileCounter += 1
    return fileNameArray

def writeResultData(*data):
    print "///write Result data///"
    tempArray = []
    fn = experimentName + "Result.csv"
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
            tempArray = []
    csvFile.close()
    print "write done:" , fn


def readCSVData(filenameArray):
    print "///read LinInt CSV///"
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
    #print results
    return results

def calcStatictic(result):
    validResult = []

    RMSEArray = []
    minRMSEArray = []
    aveLatencyArray = []

    i = 0
    count = 0
    #result num
    for exp in result:
        if exp[1] > ValidMinRMSESens:
            print "invalid result! minRMSE: ", exp[1]
        elif abs(exp[2] - ValidLatencySens) > 5 :
            print "invalid result! latency: ", exp[2]

        else:
            validResult.append(exp)
            print exp
            RMSEArray.append(exp[0])
            minRMSEArray.append(exp[1])
            aveLatencyArray.append(exp[2])
            count +=1
        i+=1
    print minRMSEArray

    print "valid data num: ", count, "total: ", i

    print "///////average///////"
    print "RMSE", average(RMSEArray)
    print "min RMSE", average(minRMSEArray)
    print "ave latency:", average(aveLatencyArray)

    print "//////Standard daviation/////"
    print "RMSE", std(RMSEArray)
    print "min RMSE", std(minRMSEArray)
    print "ave latency:", std(aveLatencyArray)




if __name__ == "__main__":
    print "///mainFunc///"
    data = searchCSVFile()
    result = readCSVData(data)
    calcStatictic(result)


