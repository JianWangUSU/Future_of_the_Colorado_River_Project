from components import Network, Reservoir, User, River, LakePowell, LakeMead
from tools import dataExchange
from decisionScaling import DStools
import components.policyControl as plc

### 1. create a network
n = Network(name="Exploratory Colorado River Network")
# setup planning horizon, inflow traces and demand traces
n.setupPeriods(41*12, 112, 6)

# create Lake Powell Object
# Powell = Reservoir.Reservoir("Powell", None)
Powell = LakePowell.LakePowell("Powell", None)
# add Powell to network
n.add_node(Powell)
# initialize Powell variables
Powell.setupPeriodsandTraces()

Mead = LakeMead.LakeMead("Mead", Powell)
n.add_node(Mead)
Mead.setupPeriodsandTraces()

UBLB = User.User("UBLB")
n.add_node(UBLB)
UBLB.setupPeriodsandTraces()

### 2. load data
# filePath = "E:/Future_of_the_Colorado_River_Project/ExploratoryModel/data/"
filePath = "../data/"

# read Lake Powell data
fileName = "zvPowell.csv"
dataExchange.readEleStoArea(Powell,filePath + fileName)
fileName = "inflowPowell.csv"
dataExchange.readInflow(Powell,filePath + fileName)
fileName = "PowellReleaseTable.csv"
dataExchange.readPowellReleaseTable(Powell,filePath + fileName)
fileName = "otherdataPowell.csv"
dataExchange.readOtherData(Powell,filePath + fileName)
fileName = "PrecipEvapPowell.csv"
dataExchange.readPrecipEvap(Powell,filePath + fileName)

# read Lake Mead data
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
fileName = "depletion.csv"
dataExchange.readDepletion(UBLB, filePath + fileName)

# set up depletion data
Powell.setupDepletion(UBLB)
Mead.setupDepletion(UBLB)

# read CRSS release information, for validation purpose
fileName = "Powellrelease.csv"
dataExchange.readCRSSrelease(Powell, filePath + fileName)
fileName = "Meadrelease.csv"
dataExchange.readCRSSrelease(Mead, filePath + fileName)

### 3.set policies
plc.EQUAL_DCP = True
plc.ADP = True
plc.FPF = False
plc.FMF = False

### 4. run the model
n.simulation()

### 5. export results
# filePath = "E:/Future_of_the_Colorado_River_Project/ExploratoryModel/results/"
filePath = "../results/"

name = 'Powell.xls'
dataExchange.exportData(Powell, filePath + name)
name = 'Mead.xls'
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
