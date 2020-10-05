from components import Network, Reservoir, User, River, LakePowell, LakeMead
from tools import dataExchange, plots
from decisionScaling import DStools
import components.policyControl as plc
import pandas as pd

### 1. create a network
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

# create a combined upper basin (UB) and lower basin (LB) user.
UBLB = User.User("UBLB")
# add User to network
n.add_node(UBLB)
# initialize User variables
UBLB.setupPeriodsandTraces()

### 2. load data
# relative folder path
filePath = "../data/"

# read Lake Powell data
# zvPowell includes Lake Powell elevation-storage-area data from CRSS
fileName = "zvPowell.csv"
# read data from zvPowell.csv to Powell object
dataExchange.readEleStoArea(Powell,filePath + fileName)
# inflowPowell includes Lake Powell inflow data
fileName = "inflowPowell.csv"
dataExchange.readInflow(Powell,filePath + fileName)
# PowellReleaseTable.csv includes Lake Powell release table
fileName = "PowellReleaseTable.csv"
dataExchange.readPowellReleaseTable(Powell,filePath + fileName)
# otherdataPowell.csv includes other Powell information, such as start storage, minimum and maximum storages, etc.
fileName = "otherdataPowell.csv"
dataExchange.readOtherData(Powell,filePath + fileName)
# PrecipEvapPowell.csv includes Lake Powell monthly precipitation rate and evaporation rate.
fileName = "PrecipEvapPowell.csv"
dataExchange.readPrecipEvap(Powell,filePath + fileName)
fileName = "PowellPeriodicNetEvap.csv"
dataExchange.readPowellPeriodicNetEvapCoef(Powell, filePath + fileName)
fileName = "PeriodicNetEvapTable.csv"
dataExchange.readPowellPeriodicNetEvapTable(Powell, filePath + fileName)
fileName = "EqualizationLine.csv"
dataExchange.readUpEqualizationTier(Powell, filePath + fileName)
fileName = "ShiftedEQLine.csv"
dataExchange.readShiftedEQLine(Powell, filePath + fileName)
fileName = "ForecastEOWYSPowell.csv"
dataExchange.readCRSSForecastEOWYSPowell(Powell,filePath + fileName)
fileName = "ForecastPowellInflow.csv"
dataExchange.readCRSSForecastPowellInflow(Powell,filePath + fileName)
fileName = "ForecastPowellRelease.csv"
dataExchange.readCRSSForecastPowellRelease(Powell,filePath + fileName)
fileName = "PowellMaxTurbineQ.csv"
dataExchange.readMaxTurbineQ(Powell,filePath + fileName)
fileName = "PowellTailwaterTable.csv"
dataExchange.readTailwaterTable(Powell,filePath + fileName)
fileName = "PowellComputeRunoffSeasonRelease.csv"
dataExchange.readCRSSPowellComputeRunoffSeasonRelease(Powell,filePath + fileName)
fileName = "PowellComputeFallSeasonRelease.csv"
dataExchange.readCRSSPowellComputeFallSeasonRelease(Powell,filePath + fileName)

# read Lake Mead data, similar to Powell data.
fileName = "zvMead.csv"
dataExchange.readEleStoArea(Mead, filePath + fileName)
fileName = "inflowMead.csv"
dataExchange.readInflow(Mead, filePath + fileName)
fileName = "otherdataMead.csv"
dataExchange.readOtherData(Mead,filePath + fileName)
fileName = "PrecipEvapMead.csv"
dataExchange.readPrecipEvap(Mead,filePath + fileName)
fileName = "dsMeadTable.csv"
dataExchange.readPearceFerrySignpost(Mead,filePath + fileName)
fileName = "SurplusRelease.csv"
dataExchange.readMeadSurplusRelease(Mead,filePath + fileName)
fileName = "SumCurrentDemandMead.csv"
dataExchange.readCRSSDemandBelowMead(Mead,filePath + fileName)



# read User data
# depletion.csv includes UB, LB depletion (demand) schedules.
fileName = "depletion.csv"
# read data from depletion.csv to User object
dataExchange.readDepletion(UBLB, filePath + fileName)

# set up depletion data, copy depletion data to Lake Powell and Lake Mead
Powell.setupDepletion(UBLB)
Mead.setupDepletion(UBLB)

# read CRSS release information, only used for validation purpose
fileName = "CRSSPowellOutflow.csv"
dataExchange.readCRSSoutflow(Powell, filePath + fileName)
fileName = "CRSSMeadOutflow.csv"
dataExchange.readCRSSoutflow(Mead, filePath + fileName)
fileName = "CRSSPowellInflow.csv"
dataExchange.readCRSSinflow(Powell, filePath + fileName)
fileName = "CRSSMeadInflow.csv"
dataExchange.readCRSSinflow(Mead, filePath + fileName)
fileName = "CRSSPowellElevation.csv"
dataExchange.readCRSSelevation(Powell, filePath + fileName)
fileName = "CRSSMeadElevation.csv"
dataExchange.readCRSSelevation(Mead, filePath + fileName)
fileName = "CRSSMeadInterveInflow.csv"
dataExchange.readCRSSIntereveinflow(Mead, filePath + fileName)
fileName = "ForecastMeadRelease.csv"
dataExchange.readCRSSForecastMeadRelease(Mead, filePath + fileName)
fileName = "ForecastEOWYSMead.csv"
dataExchange.readCRSSForecastEOWYSMead(Mead, filePath + fileName)
fileName = "SNWPDiversionTotalDepletionRequested.csv"
dataExchange.readCRSSSNWPDiversionTotalDepletionRequested(Mead, filePath + fileName)


# fileName = "CRSSUBMonthShort.csv"
# dataExchange.readCRSSubShortage(Powell, filePath + fileName)

### 3.set policies
# policy control(plc),  EQUAL_DCP: equalization rule and drought contingency plan
# ADP: adaptive policy, only consider Pearce Ferry Rapid signpost, will add more.
# FPF: Fill Powell First
# FMF: Fill Mead First (Re-drill Lake Powell)
plc.EQUAL_DCP = False
plc.ADP = False
plc.FPF = False
plc.FMF = False

### 4. run the model
n.simulation()

### 5. export results
filePath = "../results/"

# Powell.xls will store all Lake Powell results.
name = 'Powell.xls'
# exports results to  ExploratoryModel --> results folder.
dataExchange.exportData(Powell, filePath + name)
# Mead.xls will store all Lake Powell results.
name = 'Mead.xls'
# exports results to ExploratoryModel --> results folder.
dataExchange.exportData(Mead, filePath + name)

name = 'PowellReleaseTemp.xls'
dataExchange.exportReleaseTemperature(Powell, filePath + name)



### 6. plot results
date_series = pd.date_range(start= n.begtime, periods=n.periods, freq="M")
# plotsIndex = [0,40,80,100]
plotsIndex = [0, 40, 80]
for j in range(len(plotsIndex)):
    i = plotsIndex[j]
    title = "Lake Powell (Run" + str(i) +")"
    plots.plot_Elevations_Flows_CRSS_Exploratory_Powell(date_series, Powell.crssElevation[i], Powell.crssInflow[i], Powell.crssOutflow[i],
                                                        Powell.elevation[i], Powell.totalinflow[i], Powell.release[i], title)
    title = "Lake Mead (Run" + str(i) +")"
    plots.plot_Elevations_Flows_CRSS_Exploratory_Mead(date_series, Mead.crssElevation[i], Mead.crssInflow[i], Mead.crssOutflow[i],
                                                      Mead.elevation[i], Mead.totalinflow[i], Mead.release[i], title)
    # title = "Equalization (Run" + str(i) +")"
    # plots.Equalization(date_series,Powell.crssStorage[i]/Powell.maxStorage-Mead.crssStorage[i]/Mead.maxStorage,Powell.storage[i]/Powell.maxStorage- Mead.storage[i]/Mead.maxStorage,title)

### 6. run decision scaling
# ds1 = DStools.DStools()
# ds1.setupMead(Mead)
# ds1.simulateCombinations()
# ds1.plot()
# dataExchange.exportDSresults(ds1, filePath + 'MeadDS.xls')
#
#
# ds2 = DStools.DStools()
# ds2.setupPowell(Powell)
# ds2.simulateCombinations()
# # ds2.plot()
# dataExchange.exportDSresults(ds2, filePath + 'PowellDS.xls')
