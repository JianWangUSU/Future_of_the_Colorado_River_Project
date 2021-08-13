from components import Network, Reservoir, User, River, LakePowell, LakeMead
from tools import DataExchange, plots
import components.PolicyControl as plc
import components.ReleaseFunction as rf

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

# create rivers and add them to the network
RiverAbvPowell = River.River("RiverAbvPowell", UB, Powell)
n.add_link(RiverAbvPowell)
RiverbetweenPowellMead = River.River("RiverbetweenPowellMead", Powell, Mead)
n.add_link(RiverbetweenPowellMead)
RiverbelowMead = River.River("RiverbelowMead", Mead, LBM)
n.add_link(RiverbelowMead)

# create a combined upper basin (UB) and lower basin (LB) user.
# UBLB = User.User("UBLB")
# add User to network
# n.add_node(UBLB)
# initialize User variables
# UBLB.setupPeriodsandTraces()

# DataExchange.readElevationResults(Powell, Mead)

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
# Read Lower Basin Phreatophytes, NativeVegetation,
# PhreatophytesImperialToNIB, OverDeliveryToMexico, YumaOperations.WelltonMohawkBypassFlows
fileName = "LBM_OtherDemand.csv"
DataExchange.readOtherDepletion(LBM, filePath + fileName)

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

### 3. run sensitivity analysis
if True:
    filePath = "../tools/results/SensitivityAnalysis.xls"

    starttime = datetime.datetime.now()
    # 2 dimensional plot for Lake Mead, require higher resolution, small steps values
    ### Lake Mead inflow and release
    # SensitivityAnalysis.SA_EmptyAndFull(Mead, filePath)
    # SensitivityAnalysis.SA_YearsTo1025_DCP(Mead, filePath)
    # SensitivityAnalysis.SA_YearsTo3525(Powell, filePath)
    # SensitivityAnalysis.SA_EmptyAndFullPowellMead(Powell, Mead, filePath)

    # 2 dimensional plot for Lake Powell and Lake Mead, require higher resolution, small steps values
    ### Lake Powell inflow and Lake Mead release
    filePath1 = "../tools/results/5.35 UB demand/SensitivityAnalysis-ADP.xls"
    filePath2 = "../tools/results/5.35 UB demand/SensitivityAnalysis-DCP.xls"
    filePath3 = "../tools/results/5.35 UB demand/SensitivityAnalysis-DCP-0.4.xls"
    filePath4 = "../tools/results/5.35 UB demand/SensitivityAnalysis-DCP-0.8.xls"
    filePath5 = "../tools/results/5.35 UB demand/SensitivityAnalysis-DCP-1.2.xls"
    filePath6 = "../tools/results/4.5 UB demand/SensitivityAnalysis-ADP.xls"
    filePath7 = "../tools/results/4.5 UB demand/SensitivityAnalysis-DCP.xls"
    filePath8 = "../tools/results/4.5 UB demand/SensitivityAnalysis-DCP-0.4.xls"
    filePath9 = "../tools/results/4.5 UB demand/SensitivityAnalysis-DCP-0.8.xls"
    filePath10 = "../tools/results/4.5 UB demand/SensitivityAnalysis-DCP-1.2.xls"
    MAFtoAF = 1000000

    # Sensitivity analysis
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath1, 2, 0, 5.35 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath2, 0, 0, 5.35 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath3, 1, 0.4, 5.35 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath4, 1, 0.8, 5.35 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath5, 1, 1.2, 5.35 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath6, 2, 0, 4.5 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath7, 0, 0, 4.5 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath8, 1, 0.4, 4.5 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath9, 1, 0.8, 4.5 * MAFtoAF)
    SensitivityAnalysis.SensitivityAnalysisPowellMead_12MAF_Delivery(Powell, Mead, filePath10, 1, 1.2, 4.5 * MAFtoAF)

    # extract information
    filePath11 = "../tools/results/SensitivityAnalysisTo12maf_5.35.xls"
    filePath12 = "../tools/results/SensitivityAnalysisTo12maf_4.5.xls"
    DataExchange.extractSensitivityInforamtion(filePath11, filePath1, filePath2, filePath3, filePath4, filePath5)
    DataExchange.extractSensitivityInforamtion(filePath12, filePath6, filePath7, filePath8, filePath9, filePath10)

    # plots
    # Figure 4.2, 4.3, 4.4, A.2, A.3 and A.4
    DataExchange.readSAResultsAndPlot(filePath11)
    DataExchange.readSAResultsAndPlot(filePath12)

    endtime = datetime.datetime.now()
    print("Sensitivity Analysis time:" + str(endtime - starttime))

### 4. run rule based simulation model and export results
if True:
    # Policy check
    # count = 0
    # index = 0
    # for p in range(len(plc.LakePowellPolicyList)):
    #     if plc.LakePowellPolicyList[p] == True:
    #         index = p
    #         count = count + 1
    # if count == 0:
    #     print('\033[91m' + "Warning: No Policy for Lake Powell is selected, please check PolicyControl.py!" + '\033[0m')
    #     exit()
    # elif count > 1:
    #     print(
    #         '\033[91m' + "Warning: Two or more policies for Lake Powell are selected, please please check PolicyControl.py!" + '\033[0m')
    #     exit()
    # else:
    #     print(str(plc.LakePowellPolicyListNames[index]) + " for Lake Powell is selected!")
    #
    # count = 0
    # index = 0
    # for p in range(len(plc.LakeMeadPolicyList)):
    #     if plc.LakeMeadPolicyList[p] == True:
    #         index = p
    #         count = count + 1
    # if count == 0:
    #     print('\033[91m' + "Warning: No Policy for Lake Mead is selected, please check PolicyControl.py!" + '\033[0m')
    #     exit()
    # elif count > 1:
    #     print(
    #         '\033[91m' + "Warning: Two or more policies for Lake Mead are selected, please please check PolicyControl.py!" + '\033[0m')
    #     exit()
    # else:
    #     print(str(plc.LakeMeadPolicyListNames[index]) + " for Lake Mead is selected!")

    filePath_Powell_CRSS = "../results/Powell_CRSS.xls"
    filePath_Mead_CRSS = "../results/Mead_CRSS.xls"
    filePath_Powell_s1 = "../results/Powell_s1.xls"
    filePath_Mead_s1 = "../results/Mead_s1.xls"
    filePath_Powell_s2 = "../results/Powell_s2.xls"
    filePath_Mead_s2 = "../results/Mead_s2.xls"
    filePath_Powell_s3 = "../results/Powell_s3.xls"
    filePath_Mead_s3 = "../results/Mead_s3.xls"
    filePath_Powell_s4 = "../results/Powell_s4.xls"
    filePath_Mead_s4 = "../results/Mead_s4.xls"
    filePath_Powell_s5 = "../results/Powell_s5.xls"
    filePath_Mead_s5 = "../results/Mead_s5.xls"
    filePath_Powell_s6 = "../results/Powell_s6.xls"
    filePath_Mead_s6 = "../results/Mead_s6.xls"

    for i in range(7):
        print("=====================================")

        if i == 0:
            plc.setPowellPolicy("CRSS_Powell")
            plc.setMeadPolicy("CRSS_Mead")

            print("CRSS simulation (replication) start!")
        else:
            plc.setPowellPolicy("Equalization")
            plc.setMeadPolicy("ADP_DemandtoInflow")
            rf.strategyIndex = i

            print("ADP simulation, strategy " + str(i) +" start!")

        # run reservoir simulation
        n.simulation()
        # run reservoir release model
        ReleaseTemperature.simulateResTemp(Powell)
        # post processing about Release at Compact point
        Powell.CalcualteFlowAtCompactPoint()

        print("Exporting Data...")

        if i == 0:
            DataExchange.exportData(Powell, filePath_Powell_CRSS)
            DataExchange.exportData(Mead, filePath_Mead_CRSS)

            print("CRSS simulation (replication) end!")

            ### Figure 4.1 and A.1
            date_series = pd.date_range(start=n.begtime, periods=n.periods, freq="M")
            # plotsIndex = [0,40,80,100]
            plotsIndex = [0, 40, 80]
            for j in range(len(plotsIndex)):
                i = plotsIndex[j]
                title = "Lake Powell (Run" + str(i) + ")"
                plots.plot_Elevations_Flows_CRSS_Exploratory_Powell(date_series, Powell.crssStorage[i],
                                                                    Powell.crssInflow[i],
                                                                    Powell.crssOutflow[i], Powell.crssElevation[i],
                                                                    Powell.storage[i], Powell.totalinflow[i],
                                                                    Powell.outflow[i], Powell.elevation[i], title)
                title = "Lake Mead (Run" + str(i) + ")"
                plots.plot_Elevations_Flows_CRSS_Exploratory_Mead(date_series, Mead.crssStorage[i], Mead.crssInflow[i],
                                                                  Mead.crssOutflow[i], Mead.crssElevation[i],
                                                                  Mead.storage[i], Mead.totalinflow[i],
                                                                  Mead.outflow[i], Mead.elevation[i], title)
        elif i == 1:
            DataExchange.exportData(Powell, filePath_Powell_s1)
            DataExchange.exportData(Mead, filePath_Mead_s1)
            print("ADP simulation, strategy " + str(i) + " end!")
        elif i == 2:
            DataExchange.exportData(Powell, filePath_Powell_s2)
            DataExchange.exportData(Mead, filePath_Mead_s2)
            print("ADP simulation, strategy " + str(i) + " end!")
        elif i == 3:
            DataExchange.exportData(Powell, filePath_Powell_s3)
            DataExchange.exportData(Mead, filePath_Mead_s3)
            print("ADP simulation, strategy " + str(i) + " end!")
        elif i == 4:
            DataExchange.exportData(Powell, filePath_Powell_s4)
            DataExchange.exportData(Mead, filePath_Mead_s4)
            print("ADP simulation, strategy " + str(i) + " end!")
        elif i == 5:
            DataExchange.exportData(Powell, filePath_Powell_s5)
            DataExchange.exportData(Mead, filePath_Mead_s5)
            print("ADP simulation, strategy " + str(i) + " end!")
        elif i == 6:
            DataExchange.exportData(Powell, filePath_Powell_s6)
            DataExchange.exportData(Mead, filePath_Mead_s6)
            print("ADP simulation, strategy " + str(i) + " end!")

if True:
    filePath_Powell_CRSS = "../results/Powell_CRSS.xls"
    filePath_Mead_CRSS = "../results/Mead_CRSS.xls"
    filePath_Powell_s1 = "../results/Powell_s1.xls"
    filePath_Mead_s1 = "../results/Mead_s1.xls"
    filePath_Powell_s2 = "../results/Powell_s2.xls"
    filePath_Mead_s2 = "../results/Mead_s2.xls"
    filePath_Powell_s3 = "../results/Powell_s3.xls"
    filePath_Mead_s3 = "../results/Mead_s3.xls"
    filePath_Powell_s4 = "../results/Powell_s4.xls"
    filePath_Mead_s4 = "../results/Mead_s4.xls"
    filePath_Powell_s5 = "../results/Powell_s5.xls"
    filePath_Mead_s5 = "../results/Mead_s5.xls"
    filePath_Powell_s6 = "../results/Powell_s6.xls"
    filePath_Mead_s6 = "../results/Mead_s6.xls"

    # extract information
    filePathComparison = "../results/Comparison.xls"
    DataExchange.extractSimulationInforamtion(filePathComparison, filePath_Powell_CRSS, filePath_Mead_CRSS,
                                              filePath_Powell_s1, filePath_Mead_s1, filePath_Powell_s2, filePath_Mead_s2,
                                              filePath_Powell_s3, filePath_Mead_s3, filePath_Powell_s4, filePath_Mead_s4,
                                              filePath_Powell_s5, filePath_Mead_s5, filePath_Powell_s6, filePath_Mead_s6)

    # Read and plot results (post-processing)
    # Figures 4.5, 4.6, A.5, and A.6
    DataExchange.readSimulationResultsAndPlotNew()

    # # run reservoir simulation
    # n.simulation()
    # # run reservoir release model
    # ReleaseTemperature.simulateResTemp(Powell)
    # # post processing about Release at Compact point
    # Powell.CalcualteFlowAtCompactPoint()

if False:
    # run reservoir simulation
    n.simulation()
    # run reservoir release model
    ReleaseTemperature.simulateResTemp(Powell)
    # post processing about Release at Compact point
    Powell.CalcualteFlowAtCompactPoint()

    filePath = "../results/"

    # Powell.xls will store all Lake Powell results.
    name = 'Powell.xls'
    # exports results to  ExploratoryModel --> results folder.
    DataExchange.exportData(Powell, filePath + name)
    # Mead.xls will store all Lake Powell results.
    name = 'Mead.xls'
    # exports results to ExploratoryModel --> results folder.
    DataExchange.exportData(Mead, filePath + name)


### 5. Figure 4.1 and A.1
# if plc.CRSS_Powell == True and plc.CRSS_Mead == True:
#     date_series = pd.date_range(start= n.begtime, periods=n.periods, freq="M")
#     # plotsIndex = [0,40,80,100]
#     plotsIndex = [0, 40, 80]
#     for j in range(len(plotsIndex)):
#         i = plotsIndex[j]
#         title = "Lake Powell (Run" + str(i) +")"
#         plots.plot_Elevations_Flows_CRSS_Exploratory_Powell(date_series, Powell.crssStorage[i], Powell.crssInflow[i],
#                                                             Powell.crssOutflow[i], Powell.crssElevation[i],
#                                                             Powell.storage[i], Powell.totalinflow[i],
#                                                             Powell.outflow[i], Powell.elevation[i], title)
#         title = "Lake Mead (Run" + str(i) +")"
#         plots.plot_Elevations_Flows_CRSS_Exploratory_Mead(date_series, Mead.crssStorage[i], Mead.crssInflow[i],
#                                                           Mead.crssOutflow[i], Mead.crssElevation[i],
#                                                           Mead.storage[i], Mead.totalinflow[i],
#                                                           Mead.outflow[i], Mead.elevation[i], title)
        # title = "Equalization (Run" + str(i) +")"
        # plots.Equalization(date_series,Powell.crssStorage[i]/Powell.maxStorage-Mead.crssStorage[i]/Mead.maxStorage,Powell.storage[i]/Powell.maxStorage- Mead.storage[i]/Mead.maxStorage,title)

# others. Generate results for AMP white paper
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