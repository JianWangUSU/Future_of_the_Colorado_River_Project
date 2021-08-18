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

# extract rule based simulation results
def extractSimulationInforamtion(filePathComparison, filePath_Powell_CRSS, filePath_Mead_CRSS,
                                 filePath_Powell_s1, filePath_Mead_s1, filePath_Powell_s2, filePath_Mead_s2,
                                 filePath_Powell_s3, filePath_Mead_s3, filePath_Powell_s4, filePath_Mead_s4,
                                 filePath_Powell_s5, filePath_Mead_s5, filePath_Powell_s6, filePath_Mead_s6):

    print("Extracting Data from simulation results...")

    MAFtoAF = 1000000

    # =====Extract data=====
    cols = [48,95]
    PowellElevation_CRSS = pd.read_excel(filePath_Powell_CRSS, sheet_name='elevation', header=None, usecols=cols, skiprows=1)
    MeadElevation_CRSS = pd.read_excel(filePath_Mead_CRSS, sheet_name='elevation', header=None, usecols=cols, skiprows=1)
    UBAnnualShortages_CRSS  = pd.read_excel(filePath_Powell_CRSS, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_CRSS  = pd.read_excel(filePath_Mead_CRSS, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    PowellElevation_ADP_s1 = pd.read_excel(filePath_Powell_s1, sheet_name='elevation', header=None, usecols=cols, skiprows=1)
    MeadElevation_ADP_s1 = pd.read_excel(filePath_Mead_s1, sheet_name='elevation', header=None, usecols=cols, skiprows=1)
    UBAnnualShortages_ADP_s1  = pd.read_excel(filePath_Powell_s1, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s1 = pd.read_excel(filePath_Mead_s1, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    UBAnnualShortages_ADP_s2  = pd.read_excel(filePath_Powell_s2, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s2 = pd.read_excel(filePath_Mead_s2, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    UBAnnualShortages_ADP_s3  = pd.read_excel(filePath_Powell_s3, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s3 = pd.read_excel(filePath_Mead_s3, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    UBAnnualShortages_ADP_s4  = pd.read_excel(filePath_Powell_s4, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s4 = pd.read_excel(filePath_Mead_s4, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    UBAnnualShortages_ADP_s5  = pd.read_excel(filePath_Powell_s5, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s5 = pd.read_excel(filePath_Mead_s5, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    UBAnnualShortages_ADP_s6  = pd.read_excel(filePath_Powell_s6, sheet_name='UBShortage_Y', header=None, usecols=cols, skiprows=1)
    LBMAnnualShortages_ADP_s6 = pd.read_excel(filePath_Mead_s6, sheet_name='LB&MShortage_Y', header=None, usecols=cols, skiprows=1)

    # sum of 25years average shortage, 25 years of total demand - total shortage, convert from af to maf
    UB_Demand_25Y = 133608597.38
    LBM_Demand_25Y = 225043156.39

    Strategy1_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s1.loc[0:24, 48].sum())/MAFtoAF
    Strategy1_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s1.loc[0:24, 48].sum())/MAFtoAF
    Strategy2_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s2.loc[0:24, 48].sum())/MAFtoAF
    Strategy2_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s2.loc[0:24, 48].sum())/MAFtoAF
    Strategy3_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s3.loc[0:24, 48].sum())/MAFtoAF
    Strategy3_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s3.loc[0:24, 48].sum())/MAFtoAF
    Strategy4_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s4.loc[0:24, 48].sum())/MAFtoAF
    Strategy4_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s4.loc[0:24, 48].sum())/MAFtoAF
    Strategy5_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s5.loc[0:24, 48].sum())/MAFtoAF
    Strategy5_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s5.loc[0:24, 48].sum())/MAFtoAF
    Strategy6_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_ADP_s6.loc[0:24, 48].sum())/MAFtoAF
    Strategy6_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_ADP_s6.loc[0:24, 48].sum())/MAFtoAF

    CRSS_Run47_UB = (UB_Demand_25Y - UBAnnualShortages_CRSS.loc[0:24, 48].sum())/MAFtoAF
    CRSS_Run47_LBM = (LBM_Demand_25Y - LBMAnnualShortages_CRSS.loc[0:24, 48].sum())/MAFtoAF
    Ideal_Run47_UB = UB_Demand_25Y/MAFtoAF
    Ideal_Run47_LBM = LBM_Demand_25Y/MAFtoAF

    # sum of 19years average shortage, 25 years of total demand - total shortage, convert from af to maf
    UB_Demand_19Y = 100680981.43
    LBM_Demand_19Y = 170917356

    Strategy1_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s1.loc[0:24, 95].sum())/MAFtoAF
    Strategy1_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s1.loc[0:24, 95].sum())/MAFtoAF
    Strategy2_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s2.loc[0:24, 95].sum())/MAFtoAF
    Strategy2_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s2.loc[0:24, 95].sum())/MAFtoAF
    Strategy3_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s3.loc[0:24, 95].sum())/MAFtoAF
    Strategy3_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s3.loc[0:24, 95].sum())/MAFtoAF
    Strategy4_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s4.loc[0:24, 95].sum())/MAFtoAF
    Strategy4_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s4.loc[0:24, 95].sum())/MAFtoAF
    Strategy5_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s5.loc[0:24, 95].sum())/MAFtoAF
    Strategy5_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s5.loc[0:24, 95].sum())/MAFtoAF
    Strategy6_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_ADP_s6.loc[0:24, 95].sum())/MAFtoAF
    Strategy6_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_ADP_s6.loc[0:24, 95].sum())/MAFtoAF

    CRSS_Run94_UB = (UB_Demand_19Y - UBAnnualShortages_CRSS.loc[0:24, 95].sum())/MAFtoAF
    CRSS_Run94_LBM = (LBM_Demand_19Y - LBMAnnualShortages_CRSS.loc[0:24, 95].sum())/MAFtoAF
    Ideal_Run94_UB = UB_Demand_19Y/MAFtoAF
    Ideal_Run94_LBM = LBM_Demand_19Y/MAFtoAF

    # create excel
    f = xlwt.Workbook(encoding='utf-8')
    decimal_style = xlwt.XFStyle()
    decimal_style.num_format_str = '0.0'

    # =====sheet 1=====
    sheet1 = f.add_sheet(u'PowellElevation', cell_overwrite_ok=True)  # create sheet
    [period, inflows] = PowellElevation_CRSS.shape  # h is row，l is column

    sheet1.write(0, 2, "CRSS_RUN47")
    sheet1.write(0, 3, "ADP_RUN47")
    sheet1.write(0, 4, "CRSS_RUN94")
    sheet1.write(0, 5, "ADP_RUN94")
    sheet1.write(0, 6, "Min Power Pool")

    # begining time
    begtime = datetime.datetime(2020, 1, 1)
    time = begtime
    for t in range(period + 12):
        sheet1.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        sheet1.write(t+1, 1, str(time.strftime("%Y")))
        time = time + relativedelta(months=+1)
        sheet1.write(t+1, 6, 3490, decimal_style)

    for t in range(period):
        sheet1.write(t + 13, 2, PowellElevation_CRSS.iat[t,0], decimal_style)
        sheet1.write(t + 13, 3, PowellElevation_ADP_s1.iat[t,0], decimal_style)
        sheet1.write(t + 13, 4, PowellElevation_CRSS.iat[t,1], decimal_style)
        sheet1.write(t + 13, 5, PowellElevation_ADP_s1.iat[t,1], decimal_style)

    # =====sheet 2=====
    sheet2 = f.add_sheet(u'MeadElevation', cell_overwrite_ok=True)  # create sheet
    [period, inflows] = MeadElevation_CRSS.shape  # h is row，l is column

    sheet2.write(0, 2, "CRSS_RUN47")
    sheet2.write(0, 3, "ADP_RUN47")
    sheet2.write(0, 4, "CRSS_RUN94")
    sheet2.write(0, 5, "ADP_RUN94")
    sheet2.write(0, 6, "Lowest DCP trigger")

    # begining time
    begtime = datetime.datetime(2020, 1, 1)
    time = begtime
    for t in range(period + 12):
        sheet2.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        sheet2.write(t+1, 1, str(time.strftime("%Y")))
        time = time + relativedelta(months=+1)
        sheet2.write(t+1, 6, 1025, decimal_style)

    for t in range(period):
        sheet2.write(t + 13, 2, MeadElevation_CRSS.iat[t,0], decimal_style)
        sheet2.write(t + 13, 3, MeadElevation_ADP_s1.iat[t,0], decimal_style)
        sheet2.write(t + 13, 4, MeadElevation_CRSS.iat[t,1], decimal_style)
        sheet2.write(t + 13, 5, MeadElevation_ADP_s1.iat[t,1], decimal_style)

    # =====sheet 3=====
    sheet3 = f.add_sheet(u'TotalShortage', cell_overwrite_ok=True)  # create sheet
    [period, inflows] = UBAnnualShortages_CRSS.shape  # h is row，l is column
    # print(UBAnnualShortages_CRSS)

    sheet3.write(0, 2, "CRSS_RUN47")
    sheet3.write(0, 3, "ADP_RUN47")
    sheet3.write(0, 4, "CRSS_RUN94")
    sheet3.write(0, 5, "ADP_RUN94")

    # begining time
    begtime = datetime.datetime(2020, 1, 1)
    time = begtime
    for t in range(period + 1):
        sheet3.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        sheet3.write(t+1, 1, str(time.strftime("%Y")))
        time = time + relativedelta(months=+12)

    for t in range(period):
        CRSS47 = (UBAnnualShortages_CRSS.iat[t,0] + LBMAnnualShortages_CRSS.iat[t,0])/MAFtoAF
        ADP47 = (UBAnnualShortages_ADP_s1.iat[t,0] + LBMAnnualShortages_ADP_s1.iat[t,0])/MAFtoAF
        CRSS94 = (UBAnnualShortages_CRSS.iat[t,1] + LBMAnnualShortages_CRSS.iat[t,1])/MAFtoAF
        ADP94 = (UBAnnualShortages_ADP_s1.iat[t,1] + LBMAnnualShortages_ADP_s1.iat[t,1])/MAFtoAF

        sheet3.write(t + 2, 2, CRSS47, decimal_style)
        sheet3.write(t + 2, 3, ADP47, decimal_style)
        sheet3.write(t + 2, 4, CRSS94, decimal_style)
        sheet3.write(t + 2, 5, ADP94, decimal_style)

    # =====sheet 4=====
    sheet4 = f.add_sheet(u'Tradeoffs', cell_overwrite_ok=True)  # create sheet

    sheet4.write(0, 1, "UB_47")
    sheet4.write(0, 2, "LBM_47")
    sheet4.write(0, 3, "UB_94")
    sheet4.write(0, 4, "LBM_94")

    sheet4.write(1, 0, "ADP_Strtegy1")
    sheet4.write(2, 0, "ADP_Strtegy2")
    sheet4.write(3, 0, "ADP_Strtegy3")
    sheet4.write(4, 0, "ADP_Strtegy4")
    sheet4.write(5, 0, "ADP_Strtegy5")
    sheet4.write(6, 0, "ADP_Strtegy6")
    sheet4.write(7, 0, "CRSS")
    sheet4.write(8, 0, "IDEAL")

    sheet4.write(1, 1, Strategy1_Run47_UB, decimal_style)
    sheet4.write(1, 2, Strategy1_Run47_LBM, decimal_style)
    sheet4.write(2, 1, Strategy2_Run47_UB, decimal_style)
    sheet4.write(2, 2, Strategy2_Run47_LBM, decimal_style)
    sheet4.write(3, 1, Strategy3_Run47_UB, decimal_style)
    sheet4.write(3, 2, Strategy3_Run47_LBM, decimal_style)
    sheet4.write(4, 1, Strategy4_Run47_UB, decimal_style)
    sheet4.write(4, 2, Strategy4_Run47_LBM, decimal_style)
    sheet4.write(5, 1, Strategy5_Run47_UB, decimal_style)
    sheet4.write(5, 2, Strategy5_Run47_LBM, decimal_style)
    sheet4.write(6, 1, Strategy6_Run47_UB, decimal_style)
    sheet4.write(6, 2, Strategy6_Run47_LBM, decimal_style)
    sheet4.write(7, 1, CRSS_Run47_UB, decimal_style)
    sheet4.write(7, 2, CRSS_Run47_LBM, decimal_style)
    sheet4.write(8, 1, Ideal_Run47_UB, decimal_style)
    sheet4.write(8, 2, Ideal_Run47_LBM, decimal_style)

    sheet4.write(1, 3, Strategy1_Run94_UB, decimal_style)
    sheet4.write(1, 4, Strategy1_Run94_LBM, decimal_style)
    sheet4.write(2, 3, Strategy2_Run94_UB, decimal_style)
    sheet4.write(2, 4, Strategy2_Run94_LBM, decimal_style)
    sheet4.write(3, 3, Strategy3_Run94_UB, decimal_style)
    sheet4.write(3, 4, Strategy3_Run94_LBM, decimal_style)
    sheet4.write(4, 3, Strategy4_Run94_UB, decimal_style)
    sheet4.write(4, 4, Strategy4_Run94_LBM, decimal_style)
    sheet4.write(5, 3, Strategy5_Run94_UB, decimal_style)
    sheet4.write(5, 4, Strategy5_Run94_LBM, decimal_style)
    sheet4.write(6, 3, Strategy6_Run94_UB, decimal_style)
    sheet4.write(6, 4, Strategy6_Run94_LBM, decimal_style)
    sheet4.write(7, 3, CRSS_Run94_UB, decimal_style)
    sheet4.write(7, 4, CRSS_Run94_LBM, decimal_style)
    sheet4.write(8, 3, Ideal_Run94_UB, decimal_style)
    sheet4.write(8, 4, Ideal_Run94_LBM, decimal_style)

    f.save(filePathComparison)



def extractSensitivityInforamtion(filePath, filePath_ADP, filePath_DCP, filePath_DCP_04, filePath_DCP_08, filePath_DCP_12):
    filePath_Paleo = "../tools/results/PaleoInput.xls"

    f = xlwt.Workbook(encoding='utf-8')
    decimal_style = xlwt.XFStyle()
    decimal_style.num_format_str = '0.0'

    # =====sheet 1=====
    # ADP_YearsTo12MAF = pd.read_excel(filePath_ADP, sheet_name='YearsTo12MAF', header=None, skiprows=1)
    DCP_YearsTo12MAF = pd.read_excel(filePath_DCP, sheet_name='YearsTo12MAF', header=None)
    # print(DCP_YearsTo12MAF)

    sheet1 = f.add_sheet(u'DCP', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = DCP_YearsTo12MAF.shape  # h is row，l is column
    sheet1.write(0, 0, "inflow")
    sheet1.write(0, 1, "yearsto12maf")

    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        DCP_YearsTo12MAF[i] = DCP_YearsTo12MAF[i].astype(float)
        sheet1.write(i+1, 0, DCP_YearsTo12MAF[i][0], decimal_style)
        sheet1.write(i+1, 1, DCP_YearsTo12MAF[i][1], decimal_style)

    # =====sheet 2=====
    DCP12_YearsTo12MAF = pd.read_excel(filePath_DCP_12, sheet_name='YearsTo12MAF', header=None)
    # print(DCP12_YearsTo12MAF)

    sheet2 = f.add_sheet(u'DCPplus12', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = DCP12_YearsTo12MAF.shape  # h is row，l is column
    sheet2.write(0, 0, "inflow")
    sheet2.write(0, 1, "yearsto12maf")

    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        DCP12_YearsTo12MAF[i] = DCP12_YearsTo12MAF[i].astype(float)
        sheet2.write(i+1, 0, DCP12_YearsTo12MAF[i][0], decimal_style)
        sheet2.write(i+1, 1, DCP12_YearsTo12MAF[i][1], decimal_style)

    # =====sheet 3=====
    DCP8_YearsTo12MAF = pd.read_excel(filePath_DCP_08, sheet_name='YearsTo12MAF', header=None)

    sheet3 = f.add_sheet(u'DCPplus8', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = DCP8_YearsTo12MAF.shape  # h is row，l is column
    sheet3.write(0, 0, "inflow")
    sheet3.write(0, 1, "yearsto12maf")

    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        DCP8_YearsTo12MAF[i] = DCP8_YearsTo12MAF[i].astype(float)
        sheet3.write(i+1, 0, DCP8_YearsTo12MAF[i][0], decimal_style)
        sheet3.write(i+1, 1, DCP8_YearsTo12MAF[i][1], decimal_style)

    # =====sheet 4=====
    DCP4_YearsTo12MAF = pd.read_excel(filePath_DCP_04, sheet_name='YearsTo12MAF', header=None)

    sheet4 = f.add_sheet(u'DCPplus4', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = DCP4_YearsTo12MAF.shape  # h is row，l is column
    sheet4.write(0, 0, "inflow")
    sheet4.write(0, 1, "yearsto12maf")

    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        DCP4_YearsTo12MAF[i] = DCP4_YearsTo12MAF[i].astype(float)
        sheet4.write(i+1, 0, DCP4_YearsTo12MAF[i][0], decimal_style)
        sheet4.write(i+1, 1, DCP4_YearsTo12MAF[i][1], decimal_style)

    # =====sheet 5=====
    ADP_YearsTo12MAF = pd.read_excel(filePath_ADP, sheet_name='YearsTo12MAF', header=None)

    # ADP needs special post processing, Nan means won't drop down to 12 maf forever
    # We set it as 30 years in values, which will labeled as ">40 years"
    sheet5 = f.add_sheet(u'ADP', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = ADP_YearsTo12MAF.shape  # h is row，l is column
    [items, inflows_DCP] = DCP_YearsTo12MAF.shape  # h is row，l is column
    sheet5.write(0, 0, "inflow")
    sheet5.write(0, 1, "yearsto12maf")

    # ADP
    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        ADP_YearsTo12MAF[i] = ADP_YearsTo12MAF[i].astype(float)
        sheet5.write(i+1, 0, ADP_YearsTo12MAF[i][0], decimal_style)
        sheet5.write(i+1, 1, ADP_YearsTo12MAF[i][1], decimal_style)

    # fill the NAN
    for i in range(inflows, inflows_DCP):
        # convert to float 64, otherwise will have export problem.
        DCP_YearsTo12MAF[i] = DCP_YearsTo12MAF[i].astype(float)
        sheet5.write(i+1, 0, DCP_YearsTo12MAF[i][0], decimal_style)
        sheet5.write(i+1, 1, 30.0, decimal_style)

    # =====sheet 6=====
    Paleo = pd.read_excel(filePath_Paleo, sheet_name='Paleo', header=None)

    sheet6 = f.add_sheet(u'Paleo', cell_overwrite_ok=True)  # create sheet
    [items, inflows] = Paleo.shape  # h is row，l is column
    sheet6.write(0, 0, "min inflow")
    sheet6.write(0, 1, "years")

    for i in range(inflows):
        # convert to float 64, otherwise will have export problem.
        Paleo[i] = Paleo[i].astype(float)
        sheet6.write(i+1, 0, Paleo[i][0], decimal_style)
        sheet6.write(i+1, 1, Paleo[i][1], decimal_style)

    # =====sheet 7=====
    cols = [6, 21, 36]
    Depletion_DCP = pd.read_excel(filePath_DCP, sheet_name='totaldelivery_annual', header=None, skiprows=1, usecols=cols)
    Depletion_ADP = pd.read_excel(filePath_ADP, sheet_name='totaldelivery_annual', header=None, skiprows=1, usecols=cols)
    Depletion_DCP12 = pd.read_excel(filePath_DCP_12, sheet_name='totaldelivery_annual', header=None, skiprows=1, usecols=cols)

    # print(Depletion_DCP)
    # print(Paleo)
    # print(Depletion_DCP.shape)

    sheet7 = f.add_sheet(u'Depletion', cell_overwrite_ok=True)  # create sheet
    sheet7.write(0, 2, "DCP")
    sheet7.write(0, 5, "ADP")
    sheet7.write(0, 8, "DCP+1.2")
    sheet7.write(1, 1, 6)
    sheet7.write(1, 2, 9)
    sheet7.write(1, 3, 12)
    sheet7.write(1, 4, 6)
    sheet7.write(1, 5, 9)
    sheet7.write(1, 6, 12)
    sheet7.write(1, 7, 6)
    sheet7.write(1, 8, 9)
    sheet7.write(1, 9, 12)

    [years, inflows] = Depletion_DCP.shape  # h is row，l is column
    # print(years)

    for t in range(years):
        sheet7.write(t+2, 0, t+2021)

    for i in cols:
        # convert to float 64, otherwise will have export problem.
        Depletion_DCP[i] = Depletion_DCP[i].astype(float)
        Depletion_ADP[i] = Depletion_ADP[i].astype(float)
        Depletion_DCP12[i] = Depletion_DCP12[i].astype(float)

        # print(Depletion_DCP[i])

    for t in range(years):
        sheet7.write(t+2, 1, Depletion_DCP[cols[0]][t], decimal_style)
        sheet7.write(t+2, 2, Depletion_DCP[cols[1]][t], decimal_style)
        sheet7.write(t+2, 3, Depletion_DCP[cols[2]][t], decimal_style)

        sheet7.write(t+2, 4, Depletion_ADP[cols[0]][t], decimal_style)
        sheet7.write(t+2, 5, Depletion_ADP[cols[1]][t], decimal_style)
        sheet7.write(t+2, 6, Depletion_ADP[cols[2]][t], decimal_style)

        sheet7.write(t+2, 7, Depletion_DCP12[cols[0]][t], decimal_style)
        sheet7.write(t+2, 8, Depletion_DCP12[cols[1]][t], decimal_style)
        sheet7.write(t+2, 9, Depletion_DCP12[cols[2]][t], decimal_style)

    # =====sheet 8=====
    cols = [6, 21, 36]
    MaxTemp_DCP = pd.read_excel(filePath_DCP, sheet_name='SummerReleaseTemperatureMAX', header=None, skiprows=1, usecols=cols)
    MaxTemp_ADP = pd.read_excel(filePath_ADP, sheet_name='SummerReleaseTemperatureMAX', header=None, skiprows=1, usecols=cols)
    MaxTemp_DCP12 = pd.read_excel(filePath_DCP_12, sheet_name='SummerReleaseTemperatureMAX', header=None, skiprows=1, usecols=cols)

    sheet8 = f.add_sheet(u'MaxTemp', cell_overwrite_ok=True)  # create sheet
    sheet8.write(0, 2, "DCP")
    sheet8.write(0, 5, "ADP")
    sheet8.write(0, 8, "DCP+1.2")
    sheet8.write(1, 1, 6)
    sheet8.write(1, 2, 9)
    sheet8.write(1, 3, 12)
    sheet8.write(1, 4, 6)
    sheet8.write(1, 5, 9)
    sheet8.write(1, 6, 12)
    sheet8.write(1, 7, 6)
    sheet8.write(1, 8, 9)
    sheet8.write(1, 9, 12)

    [years, inflows] = MaxTemp_DCP.shape  # h is row，l is column
    # print(years)

    for t in range(years):
        sheet8.write(t+2, 0, t+2021)

    for i in cols:
        # convert to float 64, otherwise will have export problem.
        MaxTemp_DCP[i] = MaxTemp_DCP[i].astype(float)
        MaxTemp_ADP[i] = MaxTemp_ADP[i].astype(float)
        MaxTemp_DCP12[i] = MaxTemp_DCP12[i].astype(float)

        # print(Depletion_DCP[i])

    for t in range(years):
        sheet8.write(t+2, 1, MaxTemp_DCP[cols[0]][t], decimal_style)
        sheet8.write(t+2, 2, MaxTemp_DCP[cols[1]][t], decimal_style)
        sheet8.write(t+2, 3, MaxTemp_DCP[cols[2]][t], decimal_style)

        sheet8.write(t+2, 4, MaxTemp_ADP[cols[0]][t], decimal_style)
        sheet8.write(t+2, 5, MaxTemp_ADP[cols[1]][t], decimal_style)
        sheet8.write(t+2, 6, MaxTemp_ADP[cols[2]][t], decimal_style)

        sheet8.write(t+2, 7, MaxTemp_DCP12[cols[0]][t], decimal_style)
        sheet8.write(t+2, 8, MaxTemp_DCP12[cols[1]][t], decimal_style)
        sheet8.write(t+2, 9, MaxTemp_DCP12[cols[2]][t], decimal_style)

    # =====sheet 9=====
    cols = [6, 21, 36]
    MinTemp_DCP = pd.read_excel(filePath_DCP, sheet_name='SummerReleaseTemperatureMIN', header=None, skiprows=1, usecols=cols)
    MinTemp_ADP = pd.read_excel(filePath_ADP, sheet_name='SummerReleaseTemperatureMIN', header=None, skiprows=1, usecols=cols)
    MinTemp_DCP12 = pd.read_excel(filePath_DCP_12, sheet_name='SummerReleaseTemperatureMIN', header=None, skiprows=1, usecols=cols)

    sheet9 = f.add_sheet(u'MinTemp', cell_overwrite_ok=True)  # create sheet
    sheet9.write(0, 2, "DCP")
    sheet9.write(0, 5, "ADP")
    sheet9.write(0, 8, "DCP+1.2")
    sheet9.write(1, 1, 6)
    sheet9.write(1, 2, 9)
    sheet9.write(1, 3, 12)
    sheet9.write(1, 4, 6)
    sheet9.write(1, 5, 9)
    sheet9.write(1, 6, 12)
    sheet9.write(1, 7, 6)
    sheet9.write(1, 8, 9)
    sheet9.write(1, 9, 12)

    [years, inflows] = MaxTemp_DCP.shape  # h is row，l is column
    # print(years)

    for t in range(years):
        sheet9.write(t+2, 0, t+2021)

    for i in cols:
        # convert to float 64, otherwise will have export problem.
        MinTemp_DCP[i] = MinTemp_DCP[i].astype(float)
        MinTemp_ADP[i] = MinTemp_ADP[i].astype(float)
        MinTemp_DCP12[i] = MinTemp_DCP12[i].astype(float)

        # print(Depletion_DCP[i])

    for t in range(years):
        sheet9.write(t+2, 1, MinTemp_DCP[cols[0]][t], decimal_style)
        sheet9.write(t+2, 2, MinTemp_DCP[cols[1]][t], decimal_style)
        sheet9.write(t+2, 3, MinTemp_DCP[cols[2]][t], decimal_style)

        sheet9.write(t+2, 4, MinTemp_ADP[cols[0]][t], decimal_style)
        sheet9.write(t+2, 5, MinTemp_ADP[cols[1]][t], decimal_style)
        sheet9.write(t+2, 6, MinTemp_ADP[cols[2]][t], decimal_style)

        sheet9.write(t+2, 7, MinTemp_DCP12[cols[0]][t], decimal_style)
        sheet9.write(t+2, 8, MinTemp_DCP12[cols[1]][t], decimal_style)
        sheet9.write(t+2, 9, MinTemp_DCP12[cols[2]][t], decimal_style)

    # =====sheet 10=====
    cols = [6, 21, 36]
    SteadyStateDelivery_DCP = pd.read_excel(filePath_DCP, sheet_name='totaldelivery_annual', header=None, skiprows=40, usecols=cols)
    SteadyStateDelivery_ADP = pd.read_excel(filePath_ADP, sheet_name='totaldelivery_annual', header=None, skiprows=40, usecols=cols)
    SteadyStateDelivery_DCP12 = pd.read_excel(filePath_DCP_12, sheet_name='totaldelivery_annual', header=None, skiprows=40, usecols=cols)
    SteadyStateDelivery_DCP08 = pd.read_excel(filePath_DCP_08, sheet_name='totaldelivery_annual', header=None, skiprows=40, usecols=cols)
    SteadyStateDelivery_DCP04 = pd.read_excel(filePath_DCP_04, sheet_name='totaldelivery_annual', header=None, skiprows=40, usecols=cols)

    EOPHStorage_DCP = pd.read_excel(filePath_DCP, sheet_name='combinedStorage', header=None, skiprows=480, usecols=cols)
    EOPHStorage__ADP = pd.read_excel(filePath_ADP, sheet_name='combinedStorage', header=None, skiprows=480, usecols=cols)
    EOPHStorage__DCP12 = pd.read_excel(filePath_DCP_12, sheet_name='combinedStorage', header=None, skiprows=480, usecols=cols)
    EOPHStorage__DCP08 = pd.read_excel(filePath_DCP_08, sheet_name='combinedStorage', header=None, skiprows=480, usecols=cols)
    EOPHStorage__DCP04 = pd.read_excel(filePath_DCP_04, sheet_name='combinedStorage', header=None, skiprows=480, usecols=cols)

    colHead = ['EOPH storage','steady state delivery (6 inflow)','EOPH storage',
               'steady state delivery (9 inflow)','EOPH storage','steady state delivery (12 inflow)']

    rowHead = ['DCP','ADP','DCP+1.2','DCP+0.8','DCP+0.4']

    sheet10 = f.add_sheet(u'DepletionStorage', cell_overwrite_ok=True)  # create sheet

    for j in range(len(colHead)):
        sheet10.write(0, j+1, colHead[j])

    for i in range(len(rowHead)):
        sheet10.write(i+1, 0, rowHead[i])

    # for i in range()
    [EOPH, inflows] = EOPHStorage_DCP.shape  # h is row，l is column

    for i in cols:
        # convert to float 64, otherwise will have export problem.
        SteadyStateDelivery_DCP[i] = SteadyStateDelivery_DCP[i].astype(float)
        SteadyStateDelivery_ADP[i] = SteadyStateDelivery_ADP[i].astype(float)
        SteadyStateDelivery_DCP12[i] = SteadyStateDelivery_DCP12[i].astype(float)
        SteadyStateDelivery_DCP08[i] = SteadyStateDelivery_DCP08[i].astype(float)
        SteadyStateDelivery_DCP04[i] = SteadyStateDelivery_DCP04[i].astype(float)

        EOPHStorage_DCP[i] = EOPHStorage_DCP[i].astype(float)
        EOPHStorage__ADP[i] = EOPHStorage__ADP[i].astype(float)
        EOPHStorage__DCP12[i] = EOPHStorage__DCP12[i].astype(float)
        EOPHStorage__DCP08[i] = EOPHStorage__DCP08[i].astype(float)
        EOPHStorage__DCP04[i] = EOPHStorage__DCP04[i].astype(float)

    MAFTOAF = 1000000
    sheet10.write(1, 1, EOPHStorage_DCP[cols[0]][0]/MAFTOAF, decimal_style)
    sheet10.write(1, 3, EOPHStorage_DCP[cols[1]][0]/MAFTOAF, decimal_style)
    sheet10.write(1, 5, EOPHStorage_DCP[cols[2]][0]/MAFTOAF, decimal_style)
    sheet10.write(1, 2, SteadyStateDelivery_DCP[cols[0]][0], decimal_style)
    sheet10.write(1, 4, SteadyStateDelivery_DCP[cols[1]][0], decimal_style)
    sheet10.write(1, 6, SteadyStateDelivery_DCP[cols[2]][0], decimal_style)

    sheet10.write(2, 1, EOPHStorage__ADP[cols[0]][0]/MAFTOAF, decimal_style)
    sheet10.write(2, 3, EOPHStorage__ADP[cols[1]][0]/MAFTOAF, decimal_style)
    sheet10.write(2, 5, EOPHStorage__ADP[cols[2]][0]/MAFTOAF, decimal_style)
    sheet10.write(2, 2, SteadyStateDelivery_ADP[cols[0]][0], decimal_style)
    sheet10.write(2, 4, SteadyStateDelivery_ADP[cols[1]][0], decimal_style)
    sheet10.write(2, 6, SteadyStateDelivery_ADP[cols[2]][0], decimal_style)

    sheet10.write(3, 1, EOPHStorage__DCP12[cols[0]][0]/MAFTOAF, decimal_style)
    sheet10.write(3, 3, EOPHStorage__DCP12[cols[1]][0]/MAFTOAF, decimal_style)
    sheet10.write(3, 5, EOPHStorage__DCP12[cols[2]][0]/MAFTOAF, decimal_style)
    sheet10.write(3, 2, SteadyStateDelivery_DCP12[cols[0]][0], decimal_style)
    sheet10.write(3, 4, SteadyStateDelivery_DCP12[cols[1]][0], decimal_style)
    sheet10.write(3, 6, SteadyStateDelivery_DCP12[cols[2]][0], decimal_style)

    sheet10.write(4, 1, EOPHStorage__DCP08[cols[0]][0]/MAFTOAF, decimal_style)
    sheet10.write(4, 3, EOPHStorage__DCP08[cols[1]][0]/MAFTOAF, decimal_style)
    sheet10.write(4, 5, EOPHStorage__DCP08[cols[2]][0]/MAFTOAF, decimal_style)
    sheet10.write(4, 2, SteadyStateDelivery_DCP08[cols[0]][0], decimal_style)
    sheet10.write(4, 4, SteadyStateDelivery_DCP08[cols[1]][0], decimal_style)
    sheet10.write(4, 6, SteadyStateDelivery_DCP08[cols[2]][0], decimal_style)

    sheet10.write(5, 1, EOPHStorage__DCP04[cols[0]][0]/MAFTOAF, decimal_style)
    sheet10.write(5, 3, EOPHStorage__DCP04[cols[1]][0]/MAFTOAF, decimal_style)
    sheet10.write(5, 5, EOPHStorage__DCP04[cols[2]][0]/MAFTOAF, decimal_style)
    sheet10.write(5, 2, SteadyStateDelivery_DCP04[cols[0]][0], decimal_style)
    sheet10.write(5, 4, SteadyStateDelivery_DCP04[cols[1]][0], decimal_style)
    sheet10.write(5, 6, SteadyStateDelivery_DCP04[cols[2]][0], decimal_style)

    f.save(filePath)

# read sensitivity results
def readSAResultsAndPlot(filePath, FigureNames):
    # filePath = "../tools/results/SensitivityAnalysisTo12maf_5.35.xls"
    # filePath = "../tools/results/SensitivityAnalysisTo12maf_4.5.xls"

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
                           Depletion, TemperatureMIN, TemperatureMAX, DepletionStorage, FigureNames)

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

def readSimulationResultsAndPlotNew():
    filePath = "../results/Comparison.xls"

    # Run 47 (Mid-20th century drought)
    PowellElevations47 = pd.read_excel(filePath, sheet_name='PowellElevation', header=None, usecols=[1,2,3,6], skiprows=1, nrows=312)
    MeadElevations47 = pd.read_excel(filePath, sheet_name='MeadElevation', header=None, usecols=[1,2,3,6], skiprows=1, nrows=312)
    TotalShortages47 = pd.read_excel(filePath, sheet_name='TotalShortage', header=None, usecols=[1,2,3], skiprows=1, nrows=26)
    DepletionTradeOff47 = pd.read_excel(filePath, sheet_name='Tradeoffs', header=None, usecols=[1,2], skiprows=1, nrows=8)

    # Run 94 (Millinium drought)
    PowellElevations94 = pd.read_excel(filePath, sheet_name='PowellElevation', header=None, usecols=[1,4,5,6], skiprows=1, nrows=243)
    MeadElevations94 = pd.read_excel(filePath, sheet_name='MeadElevation', header=None, usecols=[1,4,5,6], skiprows=1, nrows=243)
    TotalShortages94 = pd.read_excel(filePath, sheet_name='TotalShortage', header=None, usecols=[1,4,5], skiprows=1, nrows=20)
    DepletionTradeOff94 = pd.read_excel(filePath, sheet_name='Tradeoffs', header=None, usecols=[3,4], skiprows=1, nrows=8)

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
    decimal_style1 = xlwt.XFStyle()
    decimal_style1.num_format_str = '0.0'

    sheet1 = f.add_sheet(u'totaldelivery', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = TotalDelivery.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet1.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet1.write(0, i+1, round(inflowRange1[i],1), decimal_style1)
            sheet1.write(t+1, i+1, TotalDelivery[i][t], decimal_style)

    sheet11 = f.add_sheet(u'totaldelivery_annual', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = TotalDelivery.shape  # h is row，l is column
    TotalDelivery_annual = np.zeros([inflowTraces, int(Periods/12)])
    for i in range(inflowTraces):
        for t in range(int(Periods/12)):
            # in maf
            TotalDelivery_annual[i][t] = sum(TotalDelivery[i][t*12:t*12+12])/1000000

    time = begtime
    for t in range(int(Periods/12)):
        sheet11.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+12)
        for i in range(inflowTraces):
            sheet11.write(0, i+1, round(inflowRange1[i],1), decimal_style1)
            sheet11.write(t+1, i+1, TotalDelivery_annual[i][t], decimal_style1)

    sheet2 = f.add_sheet(u'YearsTo12MAF', cell_overwrite_ok=True)  # create sheet
    [inflowTraces] = YearsTo12maf.shape
    for i in range(inflowTraces):
        if math.isnan(YearsTo12maf[i]):
            continue
        else:
            sheet2.write(0, i, round(inflowRange1[i],1), decimal_style1)
            sheet2.write(1, i, YearsTo12maf[i], decimal_style1)

    sheet3 = f.add_sheet(u'combinedStorage', cell_overwrite_ok=True)  # create sheet
    [inflowTraces, Periods] = CombinedStorage.shape  # h is row，l is column
    time = begtime
    for t in range(Periods):
        sheet3.write(t+1, 0, str(time.strftime("%m"+"/"+"%Y")))
        time = time + relativedelta(months=+1)
        for i in range(inflowTraces):
            sheet3.write(0, i+1, round(inflowRange1[i],1), decimal_style1)
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
            sheet4.write(0, i+1, round(inflowRange1[i],1), decimal_style1)
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
            sheet5.write(0, i+1, round(inflowRange1[i],1), decimal_style1)
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