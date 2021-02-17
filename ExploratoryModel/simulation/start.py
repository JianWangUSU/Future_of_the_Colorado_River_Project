from components import Network, Reservoir, User, River, LakePowell, LakeMead
from tools import DataExchange, plots
import components.PolicyControl as plc
import pandas as pd
from tools import ReleaseTemperature, SensitivityAnalysis
import datetime


############ 1. create a network
n = Network(name="Exploratory Colorado River Network")
# setup planning horizon, inflow traces and demand traces
n.setupPeriods(40*12, 113, 1)

# create Lake Powell Object
Powell = LakePowell.LakePowell("Powell", None)
# add Powell to network
n.add_node(Powell)
# initialize Powell variables
Powell.setupPeriodsandTraces()

# create Lake Mead Object
Mead = LakeMead.LakeMead("Mead", Powell)
# add Mead to network
n.add_node(Mead)
# initialize Mead variables
Mead.setupPeriodsandTraces()

# create lower basin (LB) and Mexico user.
LBM = User.LBMexico("LBMEXICO", Mead)
# add User to network
n.add_node(LBM)
# initialize User variables
LBM.setupPeriodsandTraces()

# create lower basin (LB) and Mexico user.
UB = User.UB("UB", Powell)
# add User to network
n.add_node(UB)
# initialize User variables
UB.setupPeriodsandTraces()

# create a combined upper basin (UB) and lower basin (LB) user.
# UBLB = User.User("UBLB")
# add User to network
# n.add_node(UBLB)
# initialize User variables
# UBLB.setupPeriodsandTraces()

############ 2. load data
# relative folder path
filePath = "../data/"

# read Lake Powell data
# zvPowell includes Lake Powell elevation-storage-area data from CRSS
fileName = "zvPowell.csv"
# read data from zvPowell.csv to Powell object
DataExchange.readEleStoArea(Powell, filePath + fileName)
# inflowPowell includes Lake Powell inflow data
fileName = "inflowPowell.csv"
DataExchange.readInflow(Powell, filePath + fileName)
# PowellReleaseTable.csv includes Lake Powell monthly release table, currently used in CRSS
fileName = "PowellReleaseTable.csv"
DataExchange.readPowellReleaseTable(Powell, filePath + fileName)
# otherdataPowell.csv includes other Powell information, such as start storage, minimum and maximum storages, etc.
fileName = "otherdataPowell.csv"
DataExchange.readOtherData(Powell, filePath + fileName)
# PrecipEvapPowell.csv includes Lake Powell monthly precipitation rate and evaporation rate.
fileName = "PrecipEvapPowell.csv"
DataExchange.readPrecipEvap(Powell, filePath + fileName)
fileName = "PowellPeriodicNetEvap.csv"
DataExchange.readPowellPeriodicNetEvapCoef(Powell, filePath + fileName)
fileName = "PeriodicNetEvapTable.csv"
DataExchange.readPowellPeriodicNetEvapTable(Powell, filePath + fileName)
fileName = "EqualizationLine.csv"
DataExchange.readUpEqualizationTier(Powell, filePath + fileName)
fileName = "ShiftedEQLine.csv"
DataExchange.readShiftedEQLine(Powell, filePath + fileName)
fileName = "ForecastEOWYSPowell.csv"
DataExchange.readCRSSForecastEOWYSPowell(Powell, filePath + fileName)
fileName = "ForecastPowellInflow.csv"
DataExchange.readCRSSForecastPowellInflow(Powell, filePath + fileName)
fileName = "ForecastPowellRelease.csv"
DataExchange.readCRSSForecastPowellRelease(Powell, filePath + fileName)
fileName = "PowellMaxTurbineQ.csv"
DataExchange.readMaxTurbineQ(Powell, filePath + fileName)
fileName = "PowellTailwaterTable.csv"
DataExchange.readTailwaterTable(Powell, filePath + fileName)
fileName = "PowellComputeRunoffSeasonRelease.csv"
DataExchange.readCRSSPowellComputeRunoffSeasonRelease(Powell, filePath + fileName)
fileName = "PowellComputeFallSeasonRelease.csv"
DataExchange.readCRSSPowellComputeFallSeasonRelease(Powell, filePath + fileName)
fileName = "PariaInflow.csv"
DataExchange.readPariaInflow(Powell, filePath + fileName)


# read Lake Mead data, similar to Powell data.
fileName = "zvMead.csv"
DataExchange.readEleStoArea(Mead, filePath + fileName)
fileName = "inflowMead.csv"
DataExchange.readInflow(Mead, filePath + fileName)
fileName = "otherdataMead.csv"
DataExchange.readOtherData(Mead, filePath + fileName)
fileName = "PrecipEvapMead.csv"
DataExchange.readPrecipEvap(Mead, filePath + fileName)
fileName = "dsMeadTable.csv"
DataExchange.readPearceFerrySignpost(Mead, filePath + fileName)
fileName = "SurplusRelease.csv"
DataExchange.readMeadSurplusRelease(Mead, filePath + fileName)
fileName = "SumCurrentDemandMead.csv"
DataExchange.readCRSSDemandBelowMead(Mead, filePath + fileName)
fileName = "CRSSMohaveHavasu.csv"
DataExchange.readCRSSMohaveHavasu(Mead, filePath + fileName)

# read User data
# depletion.csv includes UB, LB depletion (demand) schedules.
fileName = "depletion.csv"
# read data from depletion.csv to User object
DataExchange.readDepletion(UB, LBM, filePath + fileName)

# set up depletion data, copy depletion data to Lake Powell and Lake Mead
# Powell.setupDepletion(UBLB)
# Mead.setupDepletion(UBLB)

# read CRSS release information, only used for validation purpose
fileName = "CRSSPowellOutflow.csv"
DataExchange.readCRSSoutflow(Powell, filePath + fileName)
fileName = "CRSSMeadOutflow.csv"
DataExchange.readCRSSoutflow(Mead, filePath + fileName)
fileName = "CRSSPowellInflow.csv"
DataExchange.readCRSSinflow(Powell, filePath + fileName)
fileName = "CRSSMeadInflow.csv"
DataExchange.readCRSSinflow(Mead, filePath + fileName)
fileName = "CRSSPowellElevation.csv"
DataExchange.readCRSSelevation(Powell, filePath + fileName)
fileName = "CRSSMeadElevation.csv"
DataExchange.readCRSSelevation(Mead, filePath + fileName)
fileName = "CRSSMeadInterveInflow.csv"
DataExchange.readCRSSIntereveinflow(Mead, filePath + fileName)
fileName = "ForecastMeadRelease.csv"
DataExchange.readCRSSForecastMeadRelease(Mead, filePath + fileName)
fileName = "ForecastEOWYSMead.csv"
DataExchange.readCRSSForecastEOWYSMead(Mead, filePath + fileName)
fileName = "SNWPDiversionTotalDepletionRequested.csv"
DataExchange.readCRSSSNWPDiversionTotalDepletionRequested(Mead, filePath + fileName)
fileName = "CRSSLBMXbankBalance.csv"
DataExchange.readCRSSBankAccount(LBM, filePath + fileName)
fileName = "CRSSUBMonthShort.csv"
DataExchange.readCRSSubShortage(Powell, filePath + fileName)

# read temperature profile data before calculation
profile_path = "../data/depth_temperature.csv"
DataExchange.readDepthProfileForTemp(profile_path)

### 4. run decision scaling
if False:
    filePath = "../tools/results/SensitivityAnalysis.xls"

    starttime = datetime.datetime.now()
    # 2 dimensional plot for Lake Mead, require higher resolution, small steps values
    ### Lake Mead inflow and release
    # SensitivityAnalysis.SA_EmptyAndFull(Mead, filePath)

    # 2 dimensional plot for Lake Powell and Lake Mead, require higher resolution, small steps values
    ### Lake Powell inflow and Lake Mead release
    SensitivityAnalysis.SA_EmptyAndFullPowellMead(Powell, Mead, filePath)

    endtime = datetime.datetime.now()
    print(" time:" + str(endtime - starttime))

    # 2 dimensional plot
    # DecisionScaling.DS_EmptyAndFullPowellMead2(Powell, Mead)
    # SensitivityAnalysis.DS_EmptyAndFullPowellMead(Powell, Mead)

    # 5 dimensional plot
    # DecisionScaling.MultiUncertaintiesAnalysis(Powell, Mead)

    # 3 dimensional plot
    # DecisionScaling.MultiUncertaintiesAnalysis_3d(Powell, Mead)

### 5. run the model
if True:
    # Policy check
    count = 0
    index = 0
    for p in range(len(plc.LakePowellPolicyList)):
        if plc.LakePowellPolicyList[p] == True:
            index = p
            count = count + 1
    if count == 0:
        print('\033[91m' + "Warning: No Policy for Lake Powell is selected, please check PolicyControl.py!" + '\033[0m')
        exit()
    elif count > 1:
        print(
            '\033[91m' + "Warning: Two or more policies for Lake Powell are selected, please please check PolicyControl.py!" + '\033[0m')
        exit()
    else:
        print(str(plc.LakePowellPolicyListNames[index]) + " for Lake Powell is selected!")

    count = 0
    index = 0
    for p in range(len(plc.LakeMeadPolicyList)):
        if plc.LakeMeadPolicyList[p] == True:
            index = p
            count = count + 1
    if count == 0:
        print('\033[91m' + "Warning: No Policy for Lake Mead is selected, please check PolicyControl.py!" + '\033[0m')
        exit()
    elif count > 1:
        print(
            '\033[91m' + "Warning: Two or more policies for Lake Mead are selected, please please check PolicyControl.py!" + '\033[0m')
        exit()
    else:
        print(str(plc.LakeMeadPolicyListNames[index]) + " for Lake Mead is selected!")

    # run reservoir simulation
    n.simulation()
    # run reservoir release model
    ReleaseTemperature.simulateResTemp(Powell)
    # post processing about Release at Compact point
    Powell.CalcualteFlowAtCompactPoint()

### 6. export results
    filePath = "../results/"

    # Powell.xls will store all Lake Powell results.
    name = 'Powell.xls'
    # exports results to  ExploratoryModel --> results folder.
    DataExchange.exportData(Powell, filePath + name)
    # Mead.xls will store all Lake Powell results.
    name = 'Mead.xls'
    # exports results to ExploratoryModel --> results folder.
    DataExchange.exportData(Mead, filePath + name)

### 7. plot CRSS validation results
if plc.CRSS_Powell == True and plc.CRSS_Mead == True:
    date_series = pd.date_range(start= n.begtime, periods=n.periods, freq="M")
    # plotsIndex = [0,40,80,100]
    plotsIndex = [0, 40, 80]
    for j in range(len(plotsIndex)):
        i = plotsIndex[j]
        title = "Lake Powell (Run" + str(i) +")"
        plots.plot_Elevations_Flows_CRSS_Exploratory_Powell(date_series, Powell.crssStorage[i], Powell.crssInflow[i],
                                                            Powell.crssOutflow[i], Powell.crssElevation[i],
                                                            Powell.storage[i], Powell.totalinflow[i],
                                                            Powell.outflow[i], Powell.elevation[i], title)
        title = "Lake Mead (Run" + str(i) +")"
        plots.plot_Elevations_Flows_CRSS_Exploratory_Mead(date_series, Mead.crssStorage[i], Mead.crssInflow[i],
                                                          Mead.crssOutflow[i], Mead.crssElevation[i],
                                                          Mead.storage[i], Mead.totalinflow[i],
                                                          Mead.outflow[i], Mead.elevation[i], title)
        # title = "Equalization (Run" + str(i) +")"
        # plots.Equalization(date_series,Powell.crssStorage[i]/Powell.maxStorage-Mead.crssStorage[i]/Mead.maxStorage,Powell.storage[i]/Powell.maxStorage- Mead.storage[i]/Mead.maxStorage,title)

# 8. Generate results for AMP white paper
if False:
    filePath = "../results/"

    # name1 = 'PowellReleaseTempDNF.xls'
    # name2 = 'PowellReleaseTemp2000.xls'
    # name3 = 'PowellReleaseTemp1576.xls'
    # path1 = "../data/Comp0_KGW_DNF_Baseline_UB_NoCap_KeySlots.csv"
    # path2 = "../data/Comp0_2000_Resample_Baseline_UB_NoCap_KeySlots.csv"
    # path3 = "../data/Comp0_1576_Resample_Baseline_UB_NoCap_KeySlots.csv"
    # labels_HYDRO = ["DNF","2000","1576"]
    # title = "Average Summer Temperature (Baseline Operation)"

    name1 = 'PowellReleaseTemp_DNF_BASE.xls'
    name2 = 'PowellReleaseTemp_DNF_FMF.xls'
    name3 = 'PowellReleaseTemp_DNF_FPF.xls'
    path1 = "../data/Comp0_KGW_DNF_Baseline_UB_NoCap_KeySlots.csv"
    path2 = "../data/FMF-A1_DNF_KeySlots.csv"
    path3 = "../data/FPF_DNF_KeySlots.csv"
    labels_OP = ["Baseline","FMF","FPF"]
    labels_HR = " DNF"
    title = "Average Summer Temperature"

    name4 = 'PowellReleaseTemp_2000_BASE.xls'
    name5 = 'PowellReleaseTemp_2000_FMF.xls'
    name6 = 'PowellReleaseTemp_2000_FPF.xls'
    path4 = "../data/Comp0_2000_Resample_Baseline_UB_NoCap_KeySlots.csv"
    path5 = "../data/FMF-A1_2000_KeySlots.csv"
    path6 = "../data/FPF_2000_KeySlots.csv"
    title46 = "Average Summer Temperature (2000)"

    name7 = 'PowellReleaseTemp_1576_BASE.xls'
    name8 = 'PowellReleaseTemp_1576_FMF.xls'
    name9 = 'PowellReleaseTemp_1576_FPF.xls'
    path7 = "../data/Comp0_1576_Resample_Baseline_UB_NoCap_KeySlots.csv"
    path8 = "../data/FMF-A1_1576_KeySlots.csv"
    path9 = "../data/FPF_1576_KeySlots.csv"
    title79 = "Average Summer Temperature"

    titles = ["A: DNF Baseline","D: FMF-A1 DNF","G: FPF DNF","B: 2000 Resample Baseline","E: FMF-A1 2000","H: FPF 2000","C: 1576 Resample Baseline","F: FMF-A1 1576","I: FPF 1576"]
    titleForEachInflow = ["DNF Hydrology","2000 Hydrology","1576 Hydrology"]

    # read temperature profile data before calculation
    profile_path = "../data/depth_temperature.csv"
    dataExchange.readDepthProfileForTemp(profile_path)

    data1 = dataExchange.exportReleaseTemperature(Powell, path1, filePath+name1)
    data2 = dataExchange.exportReleaseTemperature(Powell, path2, filePath+name2)
    data3 = dataExchange.exportReleaseTemperature(Powell, path3, filePath+name3)
    data4 = dataExchange.exportReleaseTemperature(Powell, path4, filePath+name4)
    data5 = dataExchange.exportReleaseTemperature(Powell, path5, filePath+name5)
    data6 = dataExchange.exportReleaseTemperature(Powell, path6, filePath+name6)
    data7 = dataExchange.exportReleaseTemperature(Powell, path7, filePath+name7)
    data8 = dataExchange.exportReleaseTemperature(Powell, path8, filePath+name8)
    data9 = dataExchange.exportReleaseTemperature(Powell, path9, filePath+name9)

    results1 = dataExchange.exportDetailedDottyPlot(Powell, path1, path2, path3)
    results2 = dataExchange.exportDetailedDottyPlot(Powell, path4, path5, path6)
    results3 = dataExchange.exportDetailedDottyPlot(Powell, path7, path8, path9)

    # plots.dottyPlotforAveReleaseTempforEachInflow(data7, data8, data9, labels_OP, title)
    plots.dottyPlotforAveReleaseTemp31(data1, data2, data3, data4, data5, data6, data7, data8, data9, labels_OP, titleForEachInflow)
    plots.dottyPlotforAveReleaseTempRange31(results1, results2, results3, labels_OP, titleForEachInflow)

    # plots.dottyPlotforReleaseTempRangeForEachInflow(results2[0], results2[1], results2[2], labels_OP, titleForEachInflow)

    plots.dottyPlotforAveReleaseTemp33(data1, data2, data3, data4, data5, data6, data7, data8, data9,titles)
    plots.dottyPlotforReleaseTempRange33(results1, results2, results3, titles)
    plots.ReleaseTempRangePercentage33(results1, results2, results3, titles)


def ReleasePolicyCheck():
    count = 0
    index = 0
    for p in range(len(plc.LakePowellPolicyList)):
        if plc.LakePowellPolicyList[p] == True:
            index = p
            count = count + 1
    if count == 0:
        print('\033[91m' + "Warning: No Policy for Lake Powell is selected, please check PolicyControl.py!" + '\033[0m')
        exit()
    elif count > 1:
        print(
            '\033[91m' + "Warning: Two or more policies for Lake Powell are selected, please please check PolicyControl.py!" + '\033[0m')
        exit()
    else:
        print(str(plc.LakePowellPolicyListNames[index]) + " for Lake Powell is selected!")

    count = 0
    index = 0
    for p in range(len(plc.LakeMeadPolicyList)):
        if plc.LakeMeadPolicyList[p] == True:
            index = p
            count = count + 1
    if count == 0:
        print('\033[91m' + "Warning: No Policy for Lake Mead is selected, please check PolicyControl.py!" + '\033[0m')
        exit()
    elif count > 1:
        print(
            '\033[91m' + "Warning: Two or more policies for Lake Mead are selected, please please check PolicyControl.py!" + '\033[0m')
        exit()
    else:
        print(str(plc.LakeMeadPolicyListNames[index]) + " for Lake Mead is selected!")