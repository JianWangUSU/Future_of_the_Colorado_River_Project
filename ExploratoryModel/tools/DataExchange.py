import xlwt
import datetime
from dateutil.relativedelta import relativedelta
import os
import pandas as pd
import numpy as np
from tools import ReleaseTemperature
import math
from tools import plots

"""
This file is used to import data and export results
"""

# a template for inputting data to the reservoir
def readResDataTemplate(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)

    # x is user defined property, y is the value name defined in csv file
    reservoir.x = reservoir.basicData.y.values

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

def readTailwaterTable(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.Tailwater_Outflow = reservoir.basicData.Outflow.values  # in cfs
    reservoir.Tailwater_Elevation = reservoir.basicData.Twelevation.values  # in feet

def readMaxTurbineQ(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.MaxTurbineQ_Head = reservoir.basicData.Head.values  # in feet
    reservoir.MaxTurbineQ_TurbineCapacity = reservoir.basicData.TurbineCapacity.values  #acre-feet/month

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
    reservoir.minRelease = reservoir.basicData.minRelease.values[0]  # in percentage of change in volume
    reservoir.maxRelease = reservoir.basicData.maxRelease.values[0]  # in percentage of change in volume
    reservoir.maxElevation = reservoir.basicData.maxElevation.values[0]  # in feet
    reservoir.minElevation = reservoir.basicData.minElevation.values[0]  # in feet
    reservoir.initElevation = reservoir.basicData.initialElevation.values[0]  # in feet
    reservoir.maxStorage = reservoir.elevation_to_volume(reservoir.maxElevation)  # in acre feet
    reservoir.minStorage = reservoir.elevation_to_volume(reservoir.minElevation)  # in acre feet
    reservoir.initStorage = reservoir.elevation_to_volume(reservoir.initElevation)  # in acre feet
    reservoir.targetSpace = reservoir.basicData.targetSpace.values[0]  # in acre-feet

    if reservoir.name == "Powell":
        # UBRuleCurveData.ReservoirData in CRSS
        reservoir.inactiveCapacityStorage = 3997162
        reservoir.liveCapacityStorage = 24322000
    if reservoir.name == "Mead":
        # UBRuleCurveData.ReservoirData in CRSS
        reservoir.inactiveCapacityStorage = 0
        reservoir.liveCapacityStorage = 27620000

# read other basic data
def readPrecipEvap(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.evapRates = reservoir.basicData.evaporation.values  # in feet
    reservoir.precipRates = reservoir.basicData.precipiation.values  # in feet


# read other basic data
def readPowellPeriodicNetEvapCoef(LakePowell, filePath):
    LakePowell.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(LakePowell.basicDataFile))
    LakePowell.basicData = pd.read_csv(os.path.basename(LakePowell.basicDataFile))
    os.chdir(pwd)
    LakePowell.grossEvapCoef = LakePowell.basicData.GrossEvapCoefficient.values  # in  (feet/month)
    LakePowell.riverEvapCoef = LakePowell.basicData.RiverEvapCoefficient.values  # in  (feet/month)
    LakePowell.streamsideCoef = LakePowell.basicData.StreamsideCoefficient.values  # in  (feet/month-F)
    LakePowell.terranceCoef = LakePowell.basicData.TerraceCoefficient.values  # in (F)
    LakePowell.averageAirTemp = LakePowell.basicData.AverageAirTemperature.values  # in  (feet/month-F)
    LakePowell.averagePrecip = LakePowell.basicData.AveragePrecipitation.values  # in  (feet/month)

def readPowellPeriodicNetEvapTable(LakePowell, filePath):
    LakePowell.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(LakePowell.basicDataFile))
    LakePowell.basicData = pd.read_csv(os.path.basename(LakePowell.basicDataFile))
    os.chdir(pwd)
    LakePowell.PNETableElevation = LakePowell.basicData.elevation.values  # in  (feet)
    LakePowell.PNETableRiverArea = LakePowell.basicData.riverArea.values  # in  (acre)
    LakePowell.PNETableStreamsideArea = LakePowell.basicData.StreamsideArea.values  # in (acre)
    LakePowell.PNETableTerranceArea = LakePowell.basicData.TerranceArea.values  # in (acre)

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


# read inflows
def readUpEqualizationTier(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.upperTier = reservoir.basicData.UpEqualizationTier.values  # in acre-feet
    length = len(reservoir.upperTier)
    for i in range (0, length):
        reservoir.upperTier[i] = reservoir.upperTier[i]*1000
        # reservoir.upperTier[i] = reservoir.volume_to_elevation(reservoir.upperTier[i]*1000)
        # print(reservoir.upperTier[i])

# read inflows
def readShiftedEQLine(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ShiftedEQLine = reservoir.basicData.ShiftedEQLine.values  # in acre-feet
    length = len(reservoir.ShiftedEQLine)
    for i in range (0, length):
        reservoir.ShiftedEQLine[i] = reservoir.ShiftedEQLine[i]*1000

# read Mead Surplus Release
def readMeadSurplusRelease(Mead, filePath):
    Mead.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(Mead.basicDataFile))
    Mead.basicData = pd.read_csv(os.path.basename(Mead.basicDataFile))
    os.chdir(pwd)
    Mead.SurplusRelease = Mead.basicData.MonthSurplusRelease.values  # in acre-feet

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
def readDepletion(user1, user2, filePath):
    user1.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(user1.basicDataFile))
    user1.basicData = pd.read_csv(os.path.basename(user1.basicDataFile))
    os.chdir(pwd)

    user1.Depletion = np.zeros([6, user1.periods])
    user2.Depletion = np.zeros([6, user1.periods])
    # 0:baseline; 1:Scenario B; 2: Scenario C1; 3: Scenario C2; 4: Scenario D1; 5: Scenario D2
    user1.Depletion[0] = user1.basicData.TotalUpper0.values #in feet
    user2.Depletion[0] = user1.basicData.TotalLowerMexico0.values #in acre-feet
    user1.Depletion[1] = user1.basicData.TotalUpper1.values #in feet
    user2.Depletion[1] = user1.basicData.TotalLowerMexico1.values #in acre-feet
    user1.Depletion[2] = user1.basicData.TotalUpper2.values #in feet
    user2.Depletion[2] = user1.basicData.TotalLowerMexico2.values #in acre-feet
    user1.Depletion[3] = user1.basicData.TotalUpper3.values #in feet
    user2.Depletion[3] = user1.basicData.TotalLowerMexico3.values #in acre-feet
    user1.Depletion[4] = user1.basicData.TotalUpper4.values #in feet
    user2.Depletion[4] = user1.basicData.TotalLowerMexico4.values #in acre-feet
    user1.Depletion[5] = user1.basicData.TotalUpper5.values #in feet
    user2.Depletion[5] = user1.basicData.TotalLowerMexico5.values #in acre-feet

# export data to xls
def exportData(reservoir, path):
    # begining time
    begtime = datetime.datetime(2021, 1, 1)

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

    # sheet11 = f.add_sheet(u'test1', cell_overwrite_ok=True)  # create sheet
    # [h, l] = reservoir.totalinflow.shape  # h is row，l is column
    # time = begtime
    # for i in range(l):
    #     sheet11.write(i+1, 0, str(time.strftime("%b %Y")))
    #     time = time + relativedelta(months=+1)
    #     for j in range(h):
    #         sheet11.write(0, j+1, "Run " +str(j))
    #         sheet11.write(i+1, j+1, reservoir.testSeries1[j][i])
    #
    # sheet12 = f.add_sheet(u'test2', cell_overwrite_ok=True)  # create sheet
    # [h, l] = reservoir.totalinflow.shape  # h is row，l is column
    # time = begtime
    # for i in range(l):
    #     sheet12.write(i+1, 0, str(time.strftime("%b %Y")))
    #     time = time + relativedelta(months=+1)
    #     for j in range(h):
    #         sheet12.write(0, j+1, "Run " +str(j))
    #         sheet12.write(i+1, j+1, reservoir.testSeries2[j][i])
    #
    # sheet13 = f.add_sheet(u'test3', cell_overwrite_ok=True)  # create sheet
    # [h, l] = reservoir.totalinflow.shape  # h is row，l is column
    # time = begtime
    # for i in range(l):
    #     sheet13.write(i+1, 0, str(time.strftime("%b %Y")))
    #     time = time + relativedelta(months=+1)
    #     for j in range(h):
    #         sheet13.write(0, j+1, "Run " +str(j))
    #         sheet13.write(i+1, j+1, reservoir.testSeries3[j][i])

    sheet2 = f.add_sheet(u'inflow', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.totalinflow.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet2.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet2.write(0, j+1, "Run " +str(j))
            sheet2.write(i+1, j+1, reservoir.totalinflow[j][i])

    sheet33 = f.add_sheet(u'outflow', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.outflow.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet33.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet33.write(0, j+1, "Run " +str(j))
            sheet33.write(i+1, j+1, reservoir.outflow[j][i])

    sheet3 = f.add_sheet(u'release', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.release.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet3.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet3.write(0, j+1, "Run " +str(j))
            sheet3.write(i+1, j+1, reservoir.release[j][i])

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

            temp = startStorage - reservoir.storage[i][j] + reservoir.totalinflow[i][j] + reservoir.precipitation[i][j] \
                   - reservoir.evaporation[i][j] - reservoir.outflow[i][j] - reservoir.changeBankStorage[i][j]
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
    [h, l] = reservoir.relatedUser.Depletion.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet10.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet10.write(0, j+1, "Run " +str(j))
            sheet10.write(i+1, j+1, reservoir.relatedUser.Depletion[j][i])

    sheet11 = f.add_sheet(u'downDepletion', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.relatedUser.Depletion.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet11.write(i+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet11.write(0, j+1, "Run " +str(j))
            sheet11.write(i+1, j+1, reservoir.relatedUser.Depletion[j][i])

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

    sheet13 = f.add_sheet(u'ReleaseTemp', cell_overwrite_ok=True)  # create sheet
    [h, l] = reservoir.elevation.shape  # h is row，l is column
    time = begtime
    for i in range(l):
        sheet13.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for j in range(h):
            sheet13.write(0, j+1, "Run " +str(j))
            sheet13.write(i+1, j+1, reservoir.releaseTemperature[j][i])

    # other metrics
    # [h, l] = reservoir.inflow.shape  # h is row，l is column
    # UBshortagePercent = 0
    # LBshortagePercent = 0
    # SevereUBShortage = 0
    # SevereLBShortage = 0
    # indexI = 0
    # indexJ = 0
    # Powell3525 = 0
    # Mead1135 = 0
    # Mead1025 = 0
    # for i in range(h):
    #     for j in range(l):
    #         if reservoir.name == "Powell":
    #             if reservoir.upShortage[i][j] > 0:
    #                 UBshortagePercent = UBshortagePercent + 1
    #                 shortage = reservoir.upShortage[i][j]
    #                 if shortage > SevereUBShortage:
    #                     SevereUBShortage = shortage
    #             if reservoir.elevation[i][j] < 3525:
    #                 Powell3525 = Powell3525 + 1
    #         elif reservoir.name == "Mead":
    #             if reservoir.downShortage[i][j] > 0:
    #                 LBshortagePercent = LBshortagePercent + 1
    #                 shortage = reservoir.downShortage[i][j]
    #                 if shortage > SevereLBShortage:
    #                     SevereLBShortage = shortage
    #                     indexI = i
    #                     indexJ = j
    #             if reservoir.elevation[i][j] > 1135:
    #                 Mead1135 = Mead1135 + 1
    #             if reservoir.elevation[i][j] < 1025:
    #                 Mead1025 = Mead1025 + 1
    #
    # if reservoir.name == "Powell":
    #     UBshortagePercent = UBshortagePercent / h / l
    #     Powell3525 = Powell3525 / h / l
    #
    #     print("UB shortage months percentage: {:.2%}".format(UBshortagePercent))
    #     print("UB severe shortage: "+str(SevereUBShortage) + "(af)")
    #     print("POWELL elevation < 3525 ft: {:.2%}".format(Powell3525))
    #
    # elif reservoir.name == "Mead":
    #     LBshortagePercent = LBshortagePercent / h / l
    #     Mead1135 = Mead1135 / h / l
    #     Mead1025 = Mead1025 / h / l
    #
    #     print("LB shortage months percentage: {:.2%}".format(LBshortagePercent))
    #     print("LB severe shortage: "+str(SevereLBShortage) + "(af)" + " inflowTrace:" +str(indexI) + " Months:" +str(indexJ))
    #     print("MEAD elevation > 1135 ft: {:.2%}".format(Mead1135))
    #     print("MEAD elevation < 1025 ft: {:.2%}".format(Mead1025))
    #
    # if reservoir.name == "Powell":
    #     sheet13 = f.add_sheet(u'otherMetrics', cell_overwrite_ok=True)  # create sheet
    #
    #     sheet13.write(0, 0, str("UB Shortage Percentage:"))
    #     sheet13.write(0, 1, str("UB Severe Shortage:"))
    #     sheet13.write(0, 2, str("POWELL 3525 Percentage:"))
    #
    #     sheet13.write(1, 0, UBshortagePercent)
    #     sheet13.write(1, 1, SevereUBShortage)
    #     sheet13.write(1, 2, Powell3525)
    # elif reservoir.name == "Mead":
    #     sheet13 = f.add_sheet(u'otherMetrics', cell_overwrite_ok=True)  # create sheet
    #
    #     sheet13.write(0, 0, str("LB Shortage Percentage:"))
    #     sheet13.write(0, 1, str("LB Severe Shortage:"))
    #     sheet13.write(0, 2, str("MEAD 1135 Percentage:"))
    #     sheet13.write(0, 3, str("MEAD 1025 Percentage:"))
    #
    #     sheet13.write(1, 0, LBshortagePercent)
    #     sheet13.write(1, 1, SevereLBShortage)
    #     sheet13.write(1, 2, Mead1135)
    #     sheet13.write(1, 3, Mead1025)

    f.save(path)


def readCRSSPowellComputeRunoffSeasonRelease(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.PowellComputeRunoffSeasonRelease = np.transpose(reservoir.basicData.values)

def readCRSSPowellComputeFallSeasonRelease(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.PowellComputeFallSeasonRelease = np.transpose(reservoir.basicData.values)

def readCRSSoutflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssOutflow = np.transpose(reservoir.basicData.values)

def readCRSSelevation(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssElevation = np.transpose(reservoir.basicData.values)

    length, width = reservoir.crssElevation.shape
    for i in range(0, length):
        for j in range(0, width):
            reservoir.crssStorage[i][j] = reservoir.elevation_to_volume(reservoir.crssElevation[i][j])

def readCRSSinflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssInflow = np.transpose(reservoir.basicData.values)

def readCRSSForecastEOWYSPowell(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ForecastEOWYSPowell = np.transpose(reservoir.basicData.values)

def readCRSSForecastPowellInflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ForecastPowellInflow = np.transpose(reservoir.basicData.values)

def readCRSSForecastPowellRelease(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ForecastPowellRelease = np.transpose(reservoir.basicData.values)

def readCRSSForecastEOWYSMead(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ForecastEOWYSMead = np.transpose(reservoir.basicData.values)

def readCRSSForecastMeadRelease(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.ForecastMeadRelease = np.transpose(reservoir.basicData.values)

def readCRSSSNWPDiversionTotalDepletionRequested(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.SNWPDiversionTotalDepletionRequested = np.transpose(reservoir.basicData.values)

def readCRSSIntereveinflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssInterveInflow = np.transpose(reservoir.basicData.values)

def readCRSSBankAccount(user, filePath):
    user.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(user.basicDataFile))
    user.basicData = pd.read_csv(os.path.basename(user.basicDataFile))
    os.chdir(pwd)
    temp = np.transpose(user.basicData.values)
    [inflowTraces, periods] = user.CRSSbankBalance.shape  # h is row，l is column
    for i in range(inflowTraces):
        for t in range(periods):
            currentYear = math.floor(t / 12.0)
            if currentYear == 0:
                increment = (temp[i][currentYear] - user.initialBlance)/12.0
            else:
                increment = (temp[i][currentYear] - temp[i][currentYear-1])/12.0

            user.CRSSbankPutTake[i][t] = increment

            if t == 0:
                user.CRSSbankBalance[i][t] = user.initialBlance + increment
            else:
                user.CRSSbankBalance[i][t] = user.CRSSbankBalance[i][t - 1] + increment


def readCRSSubShortage(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssUBshortage = np.transpose(reservoir.basicData.values)

def readCRSSDemandBelowMead(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssDemandBelowMead = np.transpose(reservoir.basicData.values)

def readCRSSMohaveHavasu(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.crssMohaveHavasu = np.transpose(reservoir.basicData.values)

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


def readOutsideElevationForTemp(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    return np.transpose(reservoir.basicData.values)

# read elevation volume area data
def readDepthProfileForTemp(filePath):
    basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(basicDataFile))
    basicData = pd.read_csv(os.path.basename(basicDataFile))
    os.chdir(pwd)
    ReleaseTemperature.D = basicData.DEPTH.values  # in feet
    ReleaseTemperature.P_JAN = basicData.JAN.values  # in degree C
    ReleaseTemperature.P_FEB = basicData.FEB.values  # in degree C
    ReleaseTemperature.P_MAR = basicData.MAR.values  # in degree C
    ReleaseTemperature.P_APR = basicData.APR.values  # in degree C
    ReleaseTemperature.P_MAY = basicData.MAY.values  # in degree C
    ReleaseTemperature.P_JUN = basicData.JUN.values  # in degree C
    ReleaseTemperature.P_JUL = basicData.JUL.values  # in degree C
    ReleaseTemperature.P_AUG = basicData.AUG.values  # in degree C
    ReleaseTemperature.P_SEP = basicData.SEP.values  # in degree C
    ReleaseTemperature.P_OCT = basicData.OCT.values  # in degree C
    ReleaseTemperature.P_NOV = basicData.NOV.values  # in degree C
    ReleaseTemperature.P_DEC = basicData.DEC.values  # in degree C

def exportReleaseTemperature(reservoir, datapath, resultpath):
    # begining time
    begtime = datetime.datetime(2021, 1, 1)

    # end of month elevation
    # elevations = reservoir.crssElevation

    elevations = readOutsideElevationForTemp(reservoir, datapath)

    [inflowTraces, periods] = elevations.shape
    print(resultpath)
    print(elevations.shape)
    # average month elevation
    aveElevations = np.zeros([inflowTraces, periods])

    # calculate average elevation for each month
    for i in range(inflowTraces):
        for t in range(periods):
            if t == 0:
                aveElevations[i][t] = elevations[i][t]
            else:
                aveElevations[i][t] = (elevations[i][t]+elevations[i][t-1])/2.0

    # release through penstock when elevation > 3490
    releaseTemp = np.zeros([inflowTraces, periods])
    # release through river outlet when release temperature > 20
    releaseTemp2 = np.zeros([inflowTraces, periods])
    for i in range(inflowTraces):
        for t in range(periods):
            month = reservoir.para.determineMonth(t)
            # releaseTemp[i][j] = waterTemperature.getReleaseTemp(month, reservoir.crssElevation[i][j])
            releaseTemp[i][t] = ReleaseTemperature.getReleaseTempGivenElevationRangeNEW(month, aveElevations[i][t])
            # releaseTemp[i][t] = waterTemperature.getReleaseTempGivenElevationRange(month, aveElevations[i][t])

            # if releaseTemp[i][t] >= 20:
            #     releaseTemp2[i][t] = waterTemperature.getReleaseTempWhenReleaesfromOutlet(month, aveElevations[i][t])
            # else:
            #     releaseTemp2[i][t] = releaseTemp[i][t]

    f = xlwt.Workbook(encoding='utf-8')
    # sheet1 = f.add_sheet(u'elevation', cell_overwrite_ok=True)  # create sheet
    # time = begtime
    # for t in range(periods):
    #     sheet1.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
    #     time = time + relativedelta(months=+1)
    #     for i in range(inflowTraces):
    #         sheet1.write(0, i+1, "Run " +str(i))
    #         sheet1.write(t+1, i+1, aveElevations[i][t])

    sheet2 = f.add_sheet(u'ReleaseTemp', cell_overwrite_ok=True)  # create sheet
    # sheet21 = f.add_sheet(u'ReleaseTempTrigger', cell_overwrite_ok=True)  # create sheet

    time = begtime
    for t in range(periods):
        sheet2.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet2.write(0, i+1, "Run " +str(i))
            sheet2.write(t+1, i+1, releaseTemp[i][t])

    # for t in range(periods):
    #     sheet21.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
    #     time = time + relativedelta(months=+1)
    #     for i in range(inflowTraces):
    #         sheet21.write(0, i+1, "Run " +str(i))
    #         sheet21.write(t+1, i+1, releaseTemp2[i][t])

    # dotty plot
    # calculate summer temperature for each year (JUL, AUG. SEP)
    years = int(periods / 12)
    summerTemp = np.zeros([inflowTraces, years])
    for i in range(inflowTraces):
        for t in range(years):
            # JUL AUG SEP
            # summerTemp[i][t] = sum(releaseTemp[i][t * 12 + 6:t * 12 + 9]) / len(releaseTemp[i][t * 12 + 6:t * 12 + 9])
            # Jun, Jul, Aug, Sep
            summerTemp[i][t] = sum(releaseTemp[i][t*12+5:t*12+9]) / len(releaseTemp[i][t*12+5:t*12+9])

    time = begtime
    # sheet22 = f.add_sheet(u'summerTemp', cell_overwrite_ok=True)  # create sheet
    # for t in range(years):
    #     sheet22.write(t+1, 0, str(time.strftime("%Y")))
    #     time = time + relativedelta(months=+12)
    #     for i in range(inflowTraces):
    #         sheet22.write(0, i+1, "Run " +str(i))
    #         sheet22.write(t+1, i+1, summerTemp[i][t])

    # determine duration of time (percentile) at certain level over different years
    DurationOverYears_17 = np.zeros([inflowTraces, years])
    DurationOverYears_17to20 = np.zeros([inflowTraces, years])
    DurationOverYears_20 = np.zeros([inflowTraces, years])

    # count years
    for i in range(inflowTraces):
        for t in range(periods):
            year = int(math.floor(t / 12))
            if releaseTemp[i][t] < 17:
                DurationOverYears_17[i][year] = DurationOverYears_17[i][year] + 1
            elif releaseTemp[i][t] > 20:
                DurationOverYears_20[i][year] = DurationOverYears_20[i][year] + 1
            else:
                DurationOverYears_17to20[i][year] = DurationOverYears_17to20[i][year] + 1

    # count consecutive years
    for i in range(inflowTraces):
        for t in range(years):
            if t > 0:
                DurationOverYears_17[i][t] = DurationOverYears_17[i][t] + DurationOverYears_17[i][t - 1]
                DurationOverYears_20[i][t] = DurationOverYears_20[i][t] + DurationOverYears_20[i][t - 1]
                DurationOverYears_17to20[i][t] = DurationOverYears_17to20[i][t] + DurationOverYears_17to20[i][t - 1]

    # calculate percentage
    for i in range(inflowTraces):
        for t in range(years):
            DurationOverYears_17[i][t] = DurationOverYears_17[i][t] / (t * 12 + 12)
            DurationOverYears_20[i][t] = DurationOverYears_20[i][t] / (t * 12 + 12)
            DurationOverYears_17to20[i][t] = DurationOverYears_17to20[i][t] / (t * 12 + 12)
    # sheet3 = f.add_sheet(u'Duration17', cell_overwrite_ok=True)  # create sheet
    # [inflowTraces, periods] = DurationOverYears_17.shape  # inflowTraces is row，periods is column
    # time = begtime
    # for i in range(periods):
    #     sheet3.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
    #     time = time + relativedelta(months=+12)
    #     for t in range(inflowTraces):
    #         sheet3.write(0, t+1, "Run " +str(t))
    #         sheet3.write(i+1, t+1, DurationOverYears_17[t][i])
    #
    # sheet4 = f.add_sheet(u'Duration17to20', cell_overwrite_ok=True)  # create sheet
    # [inflowTraces, periods] = DurationOverYears_17to20.shape  # inflowTraces is row，periods is column
    # time = begtime
    # for i in range(periods):
    #     sheet4.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
    #     time = time + relativedelta(months=+12)
    #     for t in range(inflowTraces):
    #         sheet4.write(0, t+1, "Run " +str(t))
    #         sheet4.write(i+1, t+1, DurationOverYears_17to20[t][i])
    #
    # sheet5 = f.add_sheet(u'Duration20', cell_overwrite_ok=True)  # create sheet
    # [inflowTraces, periods] = DurationOverYears_20.shape  # inflowTraces is row，periods is column
    # time = begtime
    # for i in range(periods):
    #     sheet5.write(i+1, 0, str(time.strftime("%m"+"/"+"%Y")))
    #     time = time + relativedelta(months=+12)
    #     for t in range(inflowTraces):
    #         sheet5.write(0, t+1, "Run " +str(t))
    #         sheet5.write(i+1, t+1, DurationOverYears_20[t][i])

    # average summer temperature across all inflow traces
    AvesummerTemp = np.zeros([years])
    for t in range(years):
        totalTemp = 0
        for i in range(inflowTraces):
            totalTemp = totalTemp + summerTemp[i][t]
        AvesummerTemp[t] = totalTemp/inflowTraces

        # AvesummerTemp[t] = sum(summerTemp[t][0:inflowTraces]) / len(summerTemp[t][0:inflowTraces])
        # print(str(AvesummerTemp[t]) + " " + str(summerTemp[0][t]))

    AveTempForPeriod = np.zeros([years, years])
    # length of years (x axis)
    for m in range(years):
        # years (y axis)
        for t in range(years):
            if m == 0:
                # year 1 has 40 points, Run 25 has the lowest reservoir elevation
                AveTempForPeriod[m][t] = AvesummerTemp[t]
            else:
                # year 2 has 39 points, year 3 has 38 points....
                if t + m >= years:
                    break

                AveTempForPeriod[m][t] = sum(AvesummerTemp[t:t + m + 1]) / len(AvesummerTemp[t:t + m + 1])

    # for m in range(years):
    #     # points in a single year
    #     for t in range(years):
    #         if m == 0:
    #             # year 1 has 40 points, Run 25 has the lowest reservoir elevation
    #             AveTempForPeriod[m][t] = AvesummerTemp[t]
    #         else:
    #             # year 2 has 39 points, year 3 has 38 points....
    #             if t + m >= periods / 12:
    #                 break
    #
    #             AveTempForPeriod[m][t] = sum(AvesummerTemp[t:t + m + 1]) / len(AvesummerTemp[t:t + m + 1])

    # sheet6 = f.add_sheet(u'aveSummerTemp', cell_overwrite_ok=True)  # create sheet
    # time = begtime
    # [h] = AvesummerTemp.shape
    # for t in range(h):
    #     sheet6.write(t+1, 0, str(time.strftime("%Y")))
    #     time = time + relativedelta(months=+12)
    #     sheet6.write(0, 1, "averageSummerTemp")
    #     sheet6.write(t+1, 1, AvesummerTemp[t])

    # sheet7 = f.add_sheet(u'Dotty', cell_overwrite_ok=True)  # create sheet
    # time = begtime
    # [h,l] = AveTempForPeriod.shape
    # for t in range(h):
    #     sheet7.write(t+1, 0, str(time.strftime("%Y")))
    #     time = time + relativedelta(months=+12)
    #     for i in range(l):
    #         sheet7.write(0, i+1, "Run " + str(i))
    #         sheet7.write(t+1, i+1, AveTempForPeriod[i][t])

    f.save(resultpath)

    return AveTempForPeriod

def exportDetailedDottyPlot(reservoir, datapath1, datapath2, datapath3):
    # begining time
    begtime = datetime.datetime(2021, 1, 1)

    # end of month elevation
    # elevations = reservoir.crssElevation

    elevations1 = readOutsideElevationForTemp(reservoir, datapath1)
    result1 = ReleaseTemperature.CalculateTempForEachInflowTrace(reservoir, elevations1)
    elevations2 = readOutsideElevationForTemp(reservoir, datapath2)
    result2 = ReleaseTemperature.CalculateTempForEachInflowTrace(reservoir, elevations2)
    elevations3 = readOutsideElevationForTemp(reservoir, datapath3)
    result3 = ReleaseTemperature.CalculateTempForEachInflowTrace(reservoir, elevations3)

    return [result1,result2,result3]