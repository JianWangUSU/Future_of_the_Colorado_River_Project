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

    user1.DepletionNormal = np.zeros([6, user1.periods])
    user2.DepletionNormal = np.zeros([6, user1.periods])
    # 0:baseline; 1:Scenario B; 2: Scenario C1; 3: Scenario C2; 4: Scenario D1; 5: Scenario D2
    user1.DepletionNormal[0] = user1.basicData.TotalUpper0.values #in feet
    user2.DepletionNormal[0] = user1.basicData.TotalLowerMexico0.values #in acre-feet
    user1.DepletionNormal[1] = user1.basicData.TotalUpper1.values #in feet
    user2.DepletionNormal[1] = user1.basicData.TotalLowerMexico1.values #in acre-feet
    user1.DepletionNormal[2] = user1.basicData.TotalUpper2.values #in feet
    user2.DepletionNormal[2] = user1.basicData.TotalLowerMexico2.values #in acre-feet
    user1.DepletionNormal[3] = user1.basicData.TotalUpper3.values #in feet
    user2.DepletionNormal[3] = user1.basicData.TotalLowerMexico3.values #in acre-feet
    user1.DepletionNormal[4] = user1.basicData.TotalUpper4.values #in feet
    user2.DepletionNormal[4] = user1.basicData.TotalLowerMexico4.values #in acre-feet
    user1.DepletionNormal[5] = user1.basicData.TotalUpper5.values #in feet
    user2.DepletionNormal[5] = user1.basicData.TotalLowerMexico5.values #in acre-feet

# It's for LB and Mexico only
def readOtherDepletion(user, filePath):
    user.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(user.basicDataFile))
    user.basicData = pd.read_csv(os.path.basename(user.basicDataFile))
    os.chdir(pwd)

    user.OtherDepletion = np.zeros([user.periods])
    user.OtherDepletion = user.basicData.LBMOtherDemand.values #in acre-feet

# read results to generate box-whisker plot
def readElevationResults(Powell, Mead):
    filePath = "../results/BoxWhiskerData.xls"

    df1 = pd.read_excel(filePath, sheet_name='PowellCRSS', header=None)
    df2 = pd.read_excel(filePath, sheet_name='PowellADP', header=None)
    df3 = pd.read_excel(filePath, sheet_name='MeadCRSS', header=None)
    df4 = pd.read_excel(filePath, sheet_name='MeadADP', header=None)

    # print(df1.T)
    # print(df2.T)
    # print(df1.iat[0, 1])

    plots.box_whisker(Powell, df1, df2)
    plots.box_whisker(Mead, df3, df4)

# read sensitivity results
def readSAResultsAndPlot():
    # filePath = "../tools/results/SensitivityAnalysisTo12maf_5.35.xls"
    filePath = "../tools/results/SensitivityAnalysisTo12maf_4.5.xls"

    DCP = pd.read_excel(filePath, sheet_name='DCP', header=None, skiprows=1)
    DCPplus12 = pd.read_excel(filePath, sheet_name='DCPplus12', header=None, skiprows=1)
    DCPplus8 = pd.read_excel(filePath, sheet_name='DCPplus8', header=None, skiprows=1)
    DCPplus4 = pd.read_excel(filePath, sheet_name='DCPplus4', header=None, skiprows=1)
    ADP = pd.read_excel(filePath, sheet_name='ADP', header=None, skiprows=1)
    Paleo = pd.read_excel(filePath, sheet_name='Paleo', header=None, skiprows=1)
    Depletion = pd.read_excel(filePath, sheet_name='Depletion', header=None, skiprows=2)
    TemperatureMIN = pd.read_excel(filePath, sheet_name='MinTemp', header=None, skiprows=2)
    TemperatureMAX = pd.read_excel(filePath, sheet_name='MaxTemp', header=None, skiprows=2)
    DepletionStorage = pd.read_excel(filePath, sheet_name='DepletionStorage', header=None, skiprows=1)

    # print(df1.T)
    # print(df2.T)
    # print(df1.iat[0, 1])

    plots.plotYearsto12maf(DCP, DCPplus12, DCPplus8, DCPplus4, ADP, Paleo,
                           Depletion, TemperatureMIN, TemperatureMAX, DepletionStorage)

# for section 4.3
def readSimulationResultsAndPlot():
    filePath = "../results/Comparison0325.xls"

    # Run 47 (Mid-20th century drought)
    PowellElevations47 = pd.read_excel(filePath, sheet_name='RUN47', header=None, usecols=[1,2,3,6], skiprows=3, nrows=312)
    MeadElevations47 = pd.read_excel(filePath, sheet_name='RUN47', header=None, usecols=[1,4,5,7], skiprows=3, nrows=312)
    TotalShortages47 = pd.read_excel(filePath, sheet_name='RUN47', header=None, usecols=[18,25,26], skiprows=3, nrows=26)
    DepletionTradeOff47 = pd.read_excel(filePath, sheet_name='Trade-offs-47', header=None, usecols=[23,24], skiprows=3, nrows=8)

    # Run 94 (Millinium drought)
    PowellElevations94 = pd.read_excel(filePath, sheet_name='RUN94', header=None, usecols=[1,2,3,6], skiprows=3, nrows=243)
    MeadElevations94 = pd.read_excel(filePath, sheet_name='RUN94', header=None, usecols=[1,4,5,7], skiprows=3, nrows=243)
    TotalShortages94 = pd.read_excel(filePath, sheet_name='RUN94', header=None, usecols=[18,25,26], skiprows=3, nrows=20)
    DepletionTradeOff94 = pd.read_excel(filePath, sheet_name='Trade-offs-94', header=None, usecols=[23,24], skiprows=3, nrows=8)

    # print(df1.T)
    # print(df2.T)
    # print(df1.iat[0, 1])

    plots.ElvationComparison(PowellElevations47, MeadElevations47, TotalShortages47, DepletionTradeOff47,
                             PowellElevations94, MeadElevations94, TotalShortages94, DepletionTradeOff94)

# export data to xls
def exportData(reservoir, path):
    # begining time
    begtime = datetime.datetime(2021, 1, 1)

    StarCell = "B"
    EndCell = "DJ"

    decimal_style = xlwt.XFStyle()
    decimal_style.num_format_str = '0'
    decimal_style1 = xlwt.XFStyle()
    decimal_style1.num_format_str = '0.0'

    f = xlwt.Workbook(encoding='utf-8')
    sheet1 = f.add_sheet(u'elevation', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.elevation.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet1.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet1.write(0, i+1, "Run " +str(i))
            sheet1.write(t+1, i+1, reservoir.elevation[i][t], decimal_style)

        colindex = 1
        sheet1.write(0, inflowTraces + colindex, "Min")
        formula = "MIN(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet1.write(0, inflowTraces + colindex, "Ave")
        formula = "AVERAGE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet1.write(0, inflowTraces + colindex, "Max")
        formula = "MAX(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet1.write(0, inflowTraces + colindex, "10th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.1)"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet1.write(0, inflowTraces + colindex, "50th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.5)"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet1.write(0, inflowTraces + colindex, "90th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.9)"
        sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        if reservoir.name == "Powell":
            sheet1.write(0, inflowTraces + colindex, "Count3490")
            formula = "COUNTIF(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", \"<3490\")"
            sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula))
        if reservoir.name == "Mead":
            sheet1.write(0, inflowTraces + colindex, "Count1025")
            formula = "COUNTIF(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", \"<1025\")"
            sheet1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula))

    sheet2 = f.add_sheet(u'inflow', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.totalinflow.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet2.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet2.write(0, i+1, "Run " +str(i))
            sheet2.write(t+1, i+1, reservoir.totalinflow[i][t])

    sheet33 = f.add_sheet(u'outflow', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.outflow.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet33.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet33.write(0, i+1, "Run " +str(i))
            sheet33.write(t+1, i+1, reservoir.outflow[i][t])

    sheet3 = f.add_sheet(u'release', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.release.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet3.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet3.write(0, i+1, "Run " +str(i))
            sheet3.write(t+1, i+1, reservoir.release[i][t])

    sheet4 = f.add_sheet(u'evaporation', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.evaporation.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet4.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet4.write(0, i+1, "Run " +str(i))
            sheet4.write(t+1, i+1, reservoir.evaporation[i][t],decimal_style)

    sheet5 = f.add_sheet(u'precipitation', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.precipitation.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet5.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet5.write(0, i+1, "Run " +str(i))
            sheet5.write(t+1, i+1, reservoir.precipitation[i][t])

    sheet6 = f.add_sheet(u'changeinBank', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.changeBankStorage.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet6.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet6.write(0, i+1, "Run " +str(i))
            sheet6.write(t+1, i+1, reservoir.changeBankStorage[i][t],decimal_style)

    sheet7 = f.add_sheet(u'storage', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.storage.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet7.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet7.write(0, i+1, "Run " +str(i))
            sheet7.write(t+1, i+1, reservoir.storage[i][t])

    sheet8 = f.add_sheet(u'spill_M', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.spill.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet8.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet8.write(0, i+1, "Run " +str(i))
            sheet8.write(t+1, i+1, reservoir.spill[i][t],decimal_style)

        colindex = 1
        sheet8.write(0, inflowTraces + colindex, "Min")
        formula = "MIN(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8.write(0, inflowTraces + colindex, "Ave")
        formula = "AVERAGE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8.write(0, inflowTraces + colindex, "Max")
        formula = "MAX(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8.write(0, inflowTraces + colindex, "10th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.1)"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8.write(0, inflowTraces + colindex, "50th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.5)"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8.write(0, inflowTraces + colindex, "90th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.9)"
        sheet8.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

    sheet8_1 = f.add_sheet(u'spill_Y', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.spill.shape  # h is row，l is column
    time = begtime
    for t in range(int(Periods/12)):
        sheet8_1.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(years=+1)
        for i in range(inflowTraces):
            sheet8_1.write(0, i+1, "Run " +str(i))
            sheet8_1.write(t+1, i+1, sum(reservoir.spill[i][t*12:t*12+12]),decimal_style)

        colindex = 1
        sheet8_1.write(0, inflowTraces + colindex, "Min")
        formula = "MIN(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8_1.write(0, inflowTraces + colindex, "Ave")
        formula = "AVERAGE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8_1.write(0, inflowTraces + colindex, "Max")
        formula = "MAX(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +")"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8_1.write(0, inflowTraces + colindex, "10th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.1)"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8_1.write(0, inflowTraces + colindex, "50th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.5)"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

        colindex = colindex + 1
        sheet8_1.write(0, inflowTraces + colindex, "90th")
        formula = "PERCENTILE(" + StarCell + str(t+2) + ":"+ EndCell + str(t+2) +", 0.9)"
        sheet8_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula),decimal_style)

    for t in range (0, reservoir.inflowTraces):
        for i in range (0, reservoir.periods):
            startStorage = 0
            if i == 0:
                startStorage = reservoir.initStorage
            else:
                startStorage = reservoir.storage[t][i - 1]

            temp = startStorage - reservoir.storage[t][i] + reservoir.totalinflow[t][i] + reservoir.precipitation[t][i] \
                   - reservoir.evaporation[t][i] - reservoir.outflow[t][i] - reservoir.changeBankStorage[t][i]
            reservoir.balance[t][i] = temp

    sheet9 = f.add_sheet(u'balance', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.balance.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet9.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet9.write(0, i+1, "Run " +str(i))
            sheet9.write(t+1, i+1, reservoir.balance[i][t],decimal_style)

    sheetArea = f.add_sheet(u'area', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = reservoir.area.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheetArea.write(t+1, 0, str(time.strftime("%b %Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheetArea.write(0, i+1, "Run " +str(i))
            sheetArea.write(t+1, i+1, reservoir.area[i][t],decimal_style)

    if reservoir.name == "Powell":
        sheet10 = f.add_sheet(u'UBDepletionSchedule', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.relatedUser.DepletionNormal.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet10.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for i in range(inflowTraces):
                sheet10.write(0, i+1, "Run " +str(i))
                sheet10.write(t+1, i+1, reservoir.relatedUser.DepletionNormal[i][t],decimal_style)

    if reservoir.name == "Mead":
        sheet11 = f.add_sheet(u'LB&MDepletionSchedule', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.relatedUser.DepletionNormal.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet11.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for i in range(inflowTraces):
                sheet11.write(0, i+1, "Run " +str(i))
                sheet11.write(t+1, i+1, reservoir.relatedUser.DepletionNormal[i][t],decimal_style)

    if reservoir.name == "Powell":
        sheet12 = f.add_sheet(u'UBShortage_M', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.UBShortage.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet12.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for i in range(inflowTraces):
                sheet12.write(0, i+1, "Run " +str(i))
                sheet12.write(t+1, i+1, reservoir.UBShortage[i][t],decimal_style)

            colindex = 1
            sheet12.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

        sheet12_1 = f.add_sheet(u'UBShortage_Y', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.UBShortage.shape  # h is row，l is column
        time = begtime
        for t in range(int(Periods/12)):
            sheet12_1.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet12_1.write(0, i+1, "Run " +str(i))
                temp = sum(reservoir.UBShortage[i][t*12:t*12+12])
                if temp < 0:
                    temp = 0
                sheet12_1.write(t+1, i+1, temp, decimal_style)

            colindex = 1
            sheet12_1.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

        sheet13 = f.add_sheet(u'ReleaseTemp', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.releaseTemperature.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet13.write(t + 1, 0, str(time.strftime("%m" + "/" + "%Y")))
            time = time + relativedelta(months=+1)
            for i in range(inflowTraces):
                sheet13.write(0, i + 1, "Run " + str(i))
                sheet13.write(t + 1, i + 1, reservoir.releaseTemperature[i][t],decimal_style1)

        sheet13_1 = f.add_sheet(u'SummerReleaseTemp', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.summerReleaseTemperature.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet13_1.write(t + 1, 0, str(time.strftime("%m" + "/" + "%Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet13_1.write(0, i + 1, "Run " + str(i))
                sheet13_1.write(t + 1, i + 1, reservoir.summerReleaseTemperature[i][t], decimal_style1)

            colindex = 1
            sheet13_1.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

            colindex = colindex + 1
            sheet13_1.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

            colindex = colindex + 1
            sheet13_1.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

            colindex = colindex + 1
            sheet13_1.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

            colindex = colindex + 1
            sheet13_1.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

            colindex = colindex + 1
            sheet13_1.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet13_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style1)

        sheet14 = f.add_sheet(u'CPRelease', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.CPRelease.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet14.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet14.write(0, i+1, "Run " +str(i))
                sheet14.write(t+1, i+1, reservoir.CPRelease[i][t],decimal_style)

        sheet15 = f.add_sheet(u'CPRelease_10Y', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.CPRelease_10Y.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet15.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet15.write(0, i+1, "Run " +str(i))
                sheet15.write(t+1, i+1, reservoir.CPRelease_10Y[i][t],decimal_style)

            colindex = 1
            sheet15.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet15.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet15.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet15.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet15.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet15.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet15.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

        sheet16 = f.add_sheet(u'TotalDepletion', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.release.shape  # h is row，l is column
        totalDepletion = np.zeros([inflowTraces, Periods])

        for i in range(inflowTraces):
            for t in range(Periods):
                # total delivery = UB demand - shortages + Mead release
                totalDepletion[i][t] = reservoir.relatedUser.DepletionNormal[0][t] \
                                       - reservoir.UBShortage[i][t] \
                                       + reservoir.downReservoir.relatedUser.DepletionNormal[0][t] \
                                       - reservoir.downReservoir.LBMShortage[i][t]

        time = begtime
        for t in range(int(Periods/12)):
            sheet16.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet16.write(0, i+1, "Run " +str(i))
                sheet16.write(t+1, i+1, sum(totalDepletion[i][t*12:(t+1)*12]), decimal_style)

        sheet17 = f.add_sheet(u'TotalDelivery', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.release.shape  # h is row，l is column
        totalDepletion = np.zeros([inflowTraces, Periods])

        for i in range(inflowTraces):
            for t in range(Periods):
                # total delivery = UB demand - shortages + Mead release
                totalDepletion[i][t] = reservoir.relatedUser.DepletionNormal[0][t] \
                                       - reservoir.UBShortage[i][t] \
                                       + reservoir.downReservoir.outflow[i][t]

        time = begtime
        for t in range(int(Periods/12)):
            sheet17.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet17.write(0, i+1, "Run " +str(i))
                sheet17.write(t+1, i+1, sum(totalDepletion[i][t*12:(t+1)*12]), decimal_style)

        sheet18 = f.add_sheet(u'TotalStorage', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.release.shape  # h is row，l is column
        totalStorage = np.zeros([inflowTraces, Periods])

        for i in range(inflowTraces):
            for t in range(Periods):
                # crss shortages are negative values
                totalStorage[i][t] = reservoir.storage[i][t] + reservoir.downReservoir.storage[i][t]

        time = begtime
        for t in range(int(Periods/12)):
            sheet18.write(t + 1, 0, str(time.strftime("%Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet18.write(0, i + 1, "Run " + str(i))
                sheet18.write(t + 1, i + 1, totalStorage[i][(t+1)*12-1], decimal_style)

    elif reservoir.name == "Mead":
        sheet12 = f.add_sheet(u'LB&MShortage_M', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.LBMShortage.shape  # h is row，l is column
        time = begtime
        for t in range(Periods):
            sheet12.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(months=+1)
            for i in range(inflowTraces):
                sheet12.write(0, i+1, "Run " +str(i))
                sheet12.write(t+1, i+1, reservoir.LBMShortage[i][t],decimal_style)

            colindex = 1
            sheet12.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet12.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

        sheet12_1 = f.add_sheet(u'LB&MShortage_Y', cell_overwrite_ok=True)  # create sheet
        [inflowTraces, Periods] = reservoir.LBMShortage.shape  # h is row，l is column
        time = begtime
        for t in range(int(Periods/12)):
            sheet12_1.write(t+1, 0, str(time.strftime("%b %Y")))
            time = time + relativedelta(years=+1)
            for i in range(inflowTraces):
                sheet12_1.write(0, i+1, "Run " +str(i))
                temp = sum(reservoir.LBMShortage[i][t*12:t*12+12])
                if temp < 0:
                    temp = 0
                sheet12_1.write(t+1, i+1, temp, decimal_style)

            colindex = 1
            sheet12_1.write(0, inflowTraces + colindex, "Min")
            formula = "MIN(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "Ave")
            formula = "AVERAGE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "Max")
            formula = "MAX(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ")"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "10th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.1)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "50th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.5)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

            colindex = colindex + 1
            sheet12_1.write(0, inflowTraces + colindex, "90th")
            formula = "PERCENTILE(" + StarCell + str(t + 2) + ":" + EndCell + str(t + 2) + ", 0.9)"
            sheet12_1.write(t + 1, inflowTraces + colindex, xlwt.Formula(formula), decimal_style)

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

def readPariaInflow(reservoir, filePath):
    reservoir.basicDataFile = filePath
    pwd = os.getcwd()
    os.chdir(os.path.dirname(reservoir.basicDataFile))
    reservoir.basicData = pd.read_csv(os.path.basename(reservoir.basicDataFile))
    os.chdir(pwd)
    reservoir.PariaInflow = np.transpose(reservoir.basicData.values)

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

# multi dimensional sensitivity analysis
def exportMSAresults(path, Inflows, Releases, YearstToEmpty, YearsToFull, EOPHStorage, tabName):

    # np.round(Inflows, 1)
    # np.round(Releases, 1)
    # np.round(YearstToEmpty, 0)
    # np.round(YearsToFull, 0)

    f = xlwt.Workbook(encoding='utf-8')
    decimal_style = xlwt.XFStyle()
    decimal_style.num_format_str = '0'

    sheet1 = f.add_sheet(tabName, cell_overwrite_ok=True)  # create sheet
    [releaseLen, inflowLen] = YearstToEmpty.shape  # h is row，l is column

    for r in range(releaseLen):
        sheet1.write(1, r+2, str(Releases[r]))
        for i in range(inflowLen):
            sheet1.write(i+2, 1, str(Inflows[i]))
            sheet1.write(i+2, r+2, str(YearstToEmpty[r][i]))

    sheet1.write(0, 2, "Release")
    sheet1.write(2, 0, "Inflow")

    sheet2 = f.add_sheet(u'YearsToFull', cell_overwrite_ok=True)  # create sheet
    [releaseLen, inflowLen] = YearsToFull.shape  # h is row，l is column
    for r in range(releaseLen):
        sheet2.write(1, r+2, str(Releases[r]))
        for i in range(inflowLen):
            sheet2.write(i+2, 1, str(Inflows[i]))
            sheet2.write(i+2, r+2, str(YearsToFull[r][i]))

    sheet2.write(0, 2, "Release")
    sheet2.write(2, 0, "Inflow")

    sheet3 = f.add_sheet(u'EOPHStorage', cell_overwrite_ok=True)  # create sheet
    [releaseLen, inflowLen] = EOPHStorage.shape  # h is row，l is column
    for r in range(releaseLen):
        sheet3.write(1, r+2, str(Releases[r]))
        for i in range(inflowLen):
            sheet3.write(i+2, 1, str(Inflows[i]))
            sheet3.write(i+2, r+2, str(EOPHStorage[r][i]))

    sheet3.write(0, 2, "Release")
    sheet3.write(2, 0, "Inflow")

    f.save(path)

# multi dimensional sensitivity analysis
def exportMSAresults2(path, inflowRange1, YearsTo12maf, TotalDelivery,
                      CombinedStorage, PowellReleaseTempMAX, PowellReleaseTempMIN):
    begtime = datetime.datetime(2021, 1, 1)
    f = xlwt.Workbook(encoding='utf-8')
    decimal_style = xlwt.XFStyle()
    decimal_style.num_format_str = '0'

    sheet1 = f.add_sheet(u'totaldelivery', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = TotalDelivery.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet1.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet1.write(0, i+1, round(inflowRange1[i],2))
            sheet1.write(t+1, i+1, TotalDelivery[i][t], decimal_style)

    sheet2 = f.add_sheet(u'YearsTo12MAF', cell_overwrite_ok=True)  # create sheet
    [inflowTraces] = YearsTo12maf.shape
    for i in range(inflowTraces):
        sheet2.write(0, i+1, round(inflowRange1[i],2))
        sheet2.write(1, i+1, YearsTo12maf[i], decimal_style)

    sheet3 = f.add_sheet(u'combinedStorage', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = CombinedStorage.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet3.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet3.write(0, i+1, round(inflowRange1[i],2))
            sheet3.write(t+1, i+1, CombinedStorage[i][t], decimal_style)

    sheet4 = f.add_sheet(u'SummerReleaseTemperatureMAX', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = PowellReleaseTempMAX.shape  # h is row，l is column
    time = begtime
    years = int(Periods/12)

    summerTempMAX = np.zeros([inflowTraces, years])
    for i in range(inflowTraces):
        for t in range(int(Periods/12)):
            # Jun Jul Aug Sep
            summerTempMAX[i][t] \
                = sum(PowellReleaseTempMAX[i][t * 12 + 5:t * 12 + 9]) \
                  / len(PowellReleaseTempMAX[i][t * 12 + 5:t * 12 + 9])

    for t in range(years):
        sheet4.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+12)
        for i in range(inflowTraces):
            sheet4.write(0, i+1, round(inflowRange1[i],2))
            sheet4.write(t+1, i+1, summerTempMAX[i][t], decimal_style)

    sheet5 = f.add_sheet(u'SummerReleaseTemperatureMIN', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = PowellReleaseTempMIN.shape  # h is row，l is column
    time = begtime
    years = int(Periods/12)

    summerTempMIN = np.zeros([inflowTraces, years])
    for i in range(inflowTraces):
        for t in range(int(Periods/12)):
            # Jun Jul Aug Sep
            summerTempMIN[i][t] \
                = sum(PowellReleaseTempMIN[i][t * 12 + 5:t * 12 + 9]) \
                  / len(PowellReleaseTempMIN[i][t * 12 + 5:t * 12 + 9])

    for t in range(years):
        sheet5.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+12)
        for i in range(inflowTraces):
            sheet5.write(0, i+1, round(inflowRange1[i],2))
            sheet5.write(t+1, i+1, summerTempMIN[i][t], decimal_style)

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