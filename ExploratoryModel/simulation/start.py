from components import Network, Reservoir, User, River, LakePowell, LakeMead
from tools import dataExchange
from decisionScaling import DStools
import components.policyControl as plc

### 1. create a network
n = Network(name="Exploratory Colorado River Network")
# setup planning horizon, inflow traces and demand traces
n.setupPeriods(41*12, 112, 6)

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

# read User data
# depletion.csv includes UB, LB depletion (demand) schedules.
fileName = "depletion.csv"
# read data from depletion.csv to User object
dataExchange.readDepletion(UBLB, filePath + fileName)

# set up depletion data, copy depletion data to Lake Powell and Lake Mead
Powell.setupDepletion(UBLB)
Mead.setupDepletion(UBLB)

# read CRSS release information, only used for validation purpose
# fileName = "Powellrelease.csv"
# dataExchange.readCRSSrelease(Powell, filePath + fileName)
# fileName = "Meadrelease.csv"
# dataExchange.readCRSSrelease(Mead, filePath + fileName)

### 3.set policies
# policy control(plc),  EQUAL_DCP: equalization rule and drought contingency plan
# ADP: adaptive policy, only consider Pearce Ferry Rapid signpost, will add more.
# FPF: Fill Powell First
# FMF: Fill Mead First (Re-drill Lake Powell)
plc.EQUAL_DCP = False
plc.ADP = False
plc.FPF = False
plc.FMF = True

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
