import xlwt
import datetime
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
import numpy as np

"""
This file is used to import and export data
"""

# read elevation volume area data
def readEleStoArea(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.z = reservoir.basicData.elevation.values  # in feet
    reservoir.v = reservoir.basicData.storage.values  # in acre-feet
    reservoir.a = reservoir.basicData.area.values  # in acre

# read signpost data
def readPearceFerrySignpost(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.Mead_Storage = reservoir.basicData.storage.values*1000000  # in acre-feet
    reservoir.inflow_demand = reservoir.basicData.inflow_demand.values*1000000   # in acre-feet

    # print(reservoir.Mead_Storage)
    # print(reservoir.inflow_demand)

# read other basic data
def readOtherData(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.bankRates = reservoir.basicData.bank.values[0]  # in percentage of change in volume
    reservoir.minOutflow = reservoir.basicData.minRelease.values[0]  # in percentage of change in volume
    reservoir.maxElevation = reservoir.basicData.maxElevation.values[0]  # in feet
    reservoir.minElevation = reservoir.basicData.minElevation.values[0]  # in feet
    reservoir.initElevation = reservoir.basicData.initialElevation.values[0]  # in feet
    reservoir.maxStorage = reservoir.elevation_to_volume(reservoir.maxElevation)  # in acre feet
    reservoir.minStorage = reservoir.elevation_to_volume(reservoir.minElevation)  # in acre feet
    reservoir.initStorage = reservoir.elevation_to_volume(reservoir.initElevation)  # in acre feet
    reservoir.targetSpace = reservoir.basicData.targetSpace.values[0]  # in acre-feet

# read other basic data
def readPrecipEvap(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.evapRates = reservoir.basicData.evaporation.values  # in feet
    reservoir.precipRates = reservoir.basicData.precipiation.values  # in feet

# read inflows
def readInflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    temp = reservoir.basicData.inflow.values  # in acre-feet
    length = len(temp)

    for i in range(0, reservoir.inflowTraces):
        index = i * 12
        for j in range(0, reservoir.periods):
            if index >= length - 1:
                reservoir.inflow[i][j] = temp[index]
                index = 0
            else:
                reservoir.inflow[i][j] = temp[index]
                index = index + 1

    # for i in range(0, reservoir.inflowTraces):
    #     for j in range(0, reservoir.periods):
    #         print(reservoir.inflow[i][j])

# PowellReleaseTable
def readPowellReleaseTable(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    # index 0:7 MAF; 1:7.48 MAF; 2: 8.23 MAF; 3: 9 MAF; 4: 9.5 MAF; 5: 10.5 MAF; 6: 11 MAF; 7: 12 MAF; 8: 13 MAF; 9: 14 MAF

    reservoir.PowellmonthlyRelease = np.zeros([10, 12])

    reservoir.PowellmonthlyRelease[0] = reservoir.basicData.s1.values  # in acre-feet
    reservoir.PowellmonthlyRelease[1] = reservoir.basicData.s2.values  # in acre-feet
    reservoir.PowellmonthlyRelease[2] = reservoir.basicData.s3.values  # in acre-feet
    reservoir.PowellmonthlyRelease[3] = reservoir.basicData.s4.values  # in acre-feet
    reservoir.PowellmonthlyRelease[4] = reservoir.basicData.s5.values  # in acre-feet
    reservoir.PowellmonthlyRelease[5] = reservoir.basicData.s6.values  # in acre-feet
    reservoir.PowellmonthlyRelease[6] = reservoir.basicData.s7.values  # in acre-feet
    reservoir.PowellmonthlyRelease[7] = reservoir.basicData.s8.values  # in acre-feet
    reservoir.PowellmonthlyRelease[8] = reservoir.basicData.s9.values  # in acre-feet
    reservoir.PowellmonthlyRelease[9] = reservoir.basicData.s10.values  # in acre-feet

# read depletion data
def readDepletion(user, filePath):
    user.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(user.basicDataFile))
    user.basicData = pd.read_csv(os.path.basename(user.basicDataFile))
    os.chdir(pwd)

    user.upDepletion = np.zeros([6, user.periods])
    user.downDepletion = np.zeros([6, user.periods])
    # 0:baseline; 1:Scenario B; 2: Scenario C1; 3: Scenario C2; 4: Scenario D1; 5: Scenario D2
    user.upDepletion[0] = user.basicData.TotalUpper0.values #in feet
    user.downDepletion[0] = user.basicData.TotalLowerMexico0.values #in acre-feet
    user.upDepletion[1] = user.basicData.TotalUpper1.values #in feet
    user.downDepletion[1] = user.basicData.TotalLowerMexico1.values #in acre-feet
    user.upDepletion[2] = user.basicData.TotalUpper2.values #in feet
    user.downDepletion[2] = user.basicData.TotalLowerMexico2.values #in acre-feet
    user.upDepletion[3] = user.basicData.TotalUpper3.values #in feet
    user.downDepletion[3] = user.basicData.TotalLowerMexico3.values #in acre-feet
    user.upDepletion[4] = user.basicData.TotalUpper4.values #in feet
    user.downDepletion[4] = user.basicData.TotalLowerMexico4.values #in acre-feet
    user.upDepletion[5] = user.basicData.TotalUpper5.values #in feet
    user.downDepletion[5] = user.basicData.TotalLowerMexico5.values #in acre-feet

# export data to xls
def exportData(reservoir, path):
    # begining time
    begtime = datetime.datetime(2020, 1, 1)

    f = xlwt.Workbook(encoding='utf-8')
    sheet1 = f.add_sheet(u'elevation', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.elevation.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet1.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet1.write(0, j+1, "Run " +str(j))
            sheet1.write(i+1, j+1, reservoir.elevation[j][i])

    sheet2 = f.add_sheet(u'inflow', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.totalinflow.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet2.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet2.write(0, j+1, "Run " +str(j))
            sheet2.write(i+1, j+1, reservoir.totalinflow[j][i])

    sheet3 = f.add_sheet(u'release', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.outflow.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet3.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet3.write(0, j+1, "Run " +str(j))
            sheet3.write(i+1, j+1, reservoir.outflow[j][i])

    sheet4 = f.add_sheet(u'evaporation', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.evaporation.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet4.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet4.write(0, j+1, "Run " +str(j))
            sheet4.write(i+1, j+1, reservoir.evaporation[j][i])

    sheet5 = f.add_sheet(u'precipitation', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.precipitation.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet5.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet5.write(0, j+1, "Run " +str(j))
            sheet5.write(i+1, j+1, reservoir.precipitation[j][i])

    sheet6 = f.add_sheet(u'changeinBank', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.changeBankStorage.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet6.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet6.write(0, j+1, "Run " +str(j))
            sheet6.write(i+1, j+1, reservoir.changeBankStorage[j][i])

    sheet7 = f.add_sheet(u'storage', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.storage.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet7.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet7.write(0, j+1, "Run " +str(j))
            sheet7.write(i+1, j+1, reservoir.storage[j][i])

    sheet8 = f.add_sheet(u'spill', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.spill.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet8.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet8.write(0, j+1, "Run " +str(j))
            sheet8.write(i+1, j+1, reservoir.spill[j][i])

    for i in range (0, reservoir.inflowTraces):
        for j in range (0, reservoir.periods):
            startStorage = 0
            if j == 0:
                startStorage = reservoir.initStorage
            else:
                startStorage = reservoir.storage[i][j - 1]

            temp = startStorage - reservoir.storage[i][j] + reservoir.totalinflow[i][j] + reservoir.precipitation[i][j] - reservoir.evaporation[i][j] - reservoir.outflow[i][j] - reservoir.spill[i][j] - reservoir.changeBankStorage[i][j]
            reservoir.balance[i][j] = temp

    sheet9 = f.add_sheet(u'balance', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.balance.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet9.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet9.write(0, j+1, "Run " +str(j))
            sheet9.write(i+1, j+1, reservoir.balance[j][i])

    sheetArea = f.add_sheet(u'area', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.area.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheetArea.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheetArea.write(0, j+1, "Run " +str(j))
            sheetArea.write(i+1, j+1, reservoir.area[j][i])

    sheet10 = f.add_sheet(u'upDepletion', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.upDepletion.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet10.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet10.write(0, j+1, "Run " +str(j))
            sheet10.write(i+1, j+1, reservoir.upDepletion[j][i])

    sheet11 = f.add_sheet(u'downDepletion', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.downDepletion.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet11.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet11.write(0, j+1, "Run " +str(j))
            sheet11.write(i+1, j+1, reservoir.downDepletion[j][i])

    if reservoir.name == "Powell":
        sheet12 = f.add_sheet(u'upShortage', cell_overwrite_ok=True)  # create sheet
        [h, l] = reservoir.upShortage.shape  # h is row，l is column
        time = begtime
        for i in range(l):
            sheet12.write(i+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for j in range(h):
                sheet12.write(0, j+1, "Run " +str(j))
                sheet12.write(i+1, j+1, reservoir.upShortage[j][i])
    elif reservoir.name == "Mead":
        sheet12 = f.add_sheet(u'downShortage', cell_overwrite_ok=True)  # create sheet
        [h, l] = reservoir.downShortage.shape  # h is row，l is column
        time = begtime
        for i in range(l):
            sheet12.write(i+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for j in range(h):
                sheet12.write(0, j+1, "Run " +str(j))
                sheet12.write(i+1, j+1, reservoir.downShortage[j][i])

    # other metrics
    [h, l] = reservoir.inflow.shape  # h is row，l is column
    UBshortagePercent = 0
    LBshortagePercent = 0
    SevereUBShortage = 0
    SevereLBShortage = 0
    indexI = 0
    indexJ = 0
    Powell3525 = 0
    Mead1135 = 0
    Mead1025 = 0
    for i in range(h):
        for j in range(l):
            if reservoir.name == "Powell":
                if reservoir.upShortage[i][j] > 0:
                    UBshortagePercent = UBshortagePercent + 1
                    shortage = reservoir.upShortage[i][j]
                    if shortage > SevereUBShortage:
                        SevereUBShortage = shortage
                if reservoir.elevation[i][j] < 3525:
                    Powell3525 = Powell3525 + 1
            elif reservoir.name == "Mead":
                if reservoir.downShortage[i][j] > 0:
                    LBshortagePercent = LBshortagePercent + 1
                    shortage = reservoir.downShortage[i][j]
                    if shortage > SevereLBShortage:
                        SevereLBShortage = shortage
                        indexI = i
                        indexJ = j
                if reservoir.elevation[i][j] > 1135:
                    Mead1135 = Mead1135 + 1
                if reservoir.elevation[i][j] < 1025:
                    Mead1025 = Mead1025 + 1

    if reservoir.name == "Powell":
        UBshortagePercent = UBshortagePercent / h / l
        Powell3525 = Powell3525 / h / l

        print("UB shortage months percentage: {:.2%}".format(UBshortagePercent))
        print("UB severe shortage: "+str(SevereUBShortage) + "(af)")
        print("POWELL elevation < 3525 ft: {:.2%}".format(Powell3525))

    elif reservoir.name == "Mead":
        LBshortagePercent = LBshortagePercent / h / l
        Mead1135 = Mead1135 / h / l
        Mead1025 = Mead1025 / h / l

        print("LB shortage months percentage: {:.2%}".format(LBshortagePercent))
        print("LB severe shortage: "+str(SevereLBShortage) + "(af)" + " inflowTrace:" +str(indexI) + " Months:" +str(indexJ))
        print("MEAD elevation > 1135 ft: {:.2%}".format(Mead1135))
        print("MEAD elevation < 1025 ft: {:.2%}".format(Mead1025))

    if reservoir.name == "Powell":
        sheet13 = f.add_sheet(u'otherMetrics', cell_overwrite_ok=True)  # create sheet

        sheet13.write(0, 0, str("UB Shortage Percentage:"))
        sheet13.write(0, 1, str("UB Severe Shortage:"))
        sheet13.write(0, 2, str("POWELL 3525 Percentage:"))

        sheet13.write(1, 0, UBshortagePercent)
        sheet13.write(1, 1, SevereUBShortage)
        sheet13.write(1, 2, Powell3525)
    elif reservoir.name == "Mead":
        sheet13 = f.add_sheet(u'otherMetrics', cell_overwrite_ok=True)  # create sheet

        sheet13.write(0, 0, str("LB Shortage Percentage:"))
        sheet13.write(0, 1, str("LB Severe Shortage:"))
        sheet13.write(0, 2, str("MEAD 1135 Percentage:"))
        sheet13.write(0, 3, str("MEAD 1025 Percentage:"))

        sheet13.write(1, 0, LBshortagePercent)
        sheet13.write(1, 1, SevereLBShortage)
        sheet13.write(1, 2, Mead1135)
        sheet13.write(1, 3, Mead1025)

    f.save(path)

# read elevation volume area data
def readCRSSrelease(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssRelease = reservoir.basicData.Run0.values  # in feet

def exportDSresults(dstools, path):
    f = xlwt.Workbook(encoding='utf-8')

    xlen = len(dstools.demandRange)
    ylen = len(dstools.inflowRange)
    zlen = len(dstools.initSorage)

    for k in range(0, zlen):
        name = str (dstools.initSorage[k])
        newSheet = f.add_sheet(str(name), cell_overwrite_ok=True)  # create sheet
        for i in range (0, xlen):
            newSheet.write(i+1, 0, str(dstools.demandRange[i]))
            for j in range (0, ylen):
                newSheet.write(0, j+1, str(dstools.inflowRange[j]))
                newSheet.write(i+1, j+1, dstools.results[i][j][k])

    f.save(path)

