import os
import pandas as pd
import math



filePath = "../data/tempData/"
filename1 = "LAKEPOWELL2001-2020.csv"
filename2 = "gc_releae_temps - from 2001.csv"


class TempData:
    day = None
    month = None
    year = None
    temp = None

class EleData:
    day = None
    month = None
    year = None
    elevation = None

# read data
def readHisTemp(filePath, tempdata):
    basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(basicDataFile))
    basicData = pd.read_csv(os.path.basename(basicDataFile))
    os.chdir(pwd)
    tempdata.day = basicData.day.values
    tempdata.month = basicData.month.values
    tempdata.year = basicData.year.values
    tempdata.temp = basicData.temp.values

def readHisElevation(filePath, eledata):
    basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(basicDataFile))
    basicData = pd.read_csv(os.path.basename(basicDataFile))
    os.chdir(pwd)
    eledata.day = basicData.day.values
    eledata.month = basicData.month.values
    eledata.year = basicData.year.values
    eledata.elevation = basicData.elevation.values

def main():

    eledata = EleData()
    tempdata = TempData()

    readHisElevation(filePath + filename1, eledata)
    readHisTemp(filePath + filename2,tempdata)

    length = len(eledata.month)
    mm = 0
    count = 0
    ele = 0
    for i in range(length):
        if eledata.month[i] != mm:
            mm = eledata.month[i]
            yyyy = eledata.year[i]

            if i != 0:
                print(ele/count)

            print(str(mm) + "/" + str(yyyy), end=" ")


            # reset data
            count = 1
            ele = eledata.elevation[i]
        else:
            ele  = ele + eledata.elevation[i]
            count = count + 1

    print(ele / count)

    length = len(tempdata.month)
    mm = 0
    count = 0
    temp = 0
    for i in range(length):
        if tempdata.month[i] != mm:
            mm = tempdata.month[i]
            yyyy = tempdata.year[i]

            if i != 0:
                print(temp/count)
            print(str(mm) + "/" + str(yyyy), end=" ")

            # reset data
            count = 1
            temp = tempdata.temp[i]
        else:
            temp  = temp + tempdata.temp[i]
            count = count + 1

    print(temp / count)


if __name__ == '__main__':
    main()


