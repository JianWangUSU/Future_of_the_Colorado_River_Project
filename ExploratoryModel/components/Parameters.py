import math
from dateutil.relativedelta import relativedelta
import datetime


# This file defines some basic parameters and functions

# cubic feet to acre feet
CFtoAcreFeet = 0.000022956840904921

secondsInaDay = 24*60*60

# Coordinated Operation in CRSS
Hybrid_MeadMinBalancingElevation = 1075
Hybrid_PowellUpperTierElevation = 3575
Hybrid_PowellLowerTierElevation = 3525
MeadProtectionElevation = 1105
Hybrid_Mead823Trigger = 1025


# ICS, surplus policy
MAXBankCapacity = 2700000 # acre-feet
MeadStartDCPElevation = 1090
MeadMIDDCPElevation = 1045
maxTakeEachYear = 500000
maxPutEachYear = 500000

# DCP elevations and contributions
MeadDCPElevations = [1090, 1075, 1050, 1045, 1040, 1035, 1030, 1025]
MeadDCPcutbacks = [0, 200000+41000, 533000+80000, 617000+104000, 867000+146000,
                   917000+154000, 967000+162000, 1017000+171000, 1100000+275000]

# Interim guidelines elevations and contributions
MeadIGSElevations = [1075, 1050, 1025]
MeadIGScutbacks = [0, 333000, 417000, 500000]

MAFTOAF = 1000000

# Past system inflow (in maf) based on regulated inflow to Powell, side inflow to Lake Mead from 24 month study
# and UB consumptive uses and losses. Since UB CU&L only has data to 2018, we assume 2019, 2020 CU&L is the same as 2018 data
PastInflow = [21.2363, 10.6611, 10.6665, 14.1998, 13.871, 14.7438, 17.2176, 10.6932, 18.0022, 11.4772]
PastEvapration = [1.081, 1.069, 0.948, 0.914, 0.906, 0.913, 0.964, 0.902, 0.915, 0.916]

# Define months
JAN = 0
FEB = 1
MAR = 2
APR = 3
MAY = 4
JUN = 5
JUL = 6
AUG = 7
SEP = 8
OCT = 9
NOV = 10
DEC = 11

BEFORE_START_TIME = -100

# determine month based on period
def determineMonth(period):
    if period %12 == 0:
        return 0  # January
    if period %12 == 1:
        return 1  # Feb
    if period %12 == 2:
        return 2  # Mar
    if period %12 == 3:
        return 3  # Apr
    if period %12 == 4:
        return 4  # May
    if period %12 == 5:
        return 5  # Jun
    if period %12 == 6:
        return 6  # JUl
    if period %12 == 7:
        return 7  # Aug
    if period %12 == 8:
        return 8  # Sep
    if period %12 == 9:
        return 9  # Oct
    if period %12 == 10:
        return 10  # Nov
    if period %12 == 11:
        return 11  # Dec

# --------------------- Powell para ----------------------

# Flaming Gorge, Blue Mesa, Morrow Point, Crystal, Navajo
initUBstorage = 3319784 + 584695 + 112001 + 16969 + 1450225
# Flaming Gorge (6039), Blue Mesa (7519.4), Morrow Point, Crystal, Navajo (6085)
maxUBstorage = 3710151 + 830704 + 111819 + 16957 + 1701300
# Flaming Gorge (6027), Blue Mesa (7498), Morrow Point (7153.73), Crystal (6753.04), Navajo (6065)
targetUBstorage = 3234735 + 644992 + 111819 + 16957 + 1412737
# storage between 3370 to bottom of Lake Powell
lastPowellStorage = 1.89

# CRSS POWELL UBRuleCurveData, from JAN to DEC
# targetSpace = {0,0,0,0,0,0,500000,1222000,1722000,2022000,2322000,2422000}
# --------------------- Powell para end ----------------------


# --------------------- Mead para ----------------------
### Mead Flood Control, acre-feet
MinSpace = 1500000

# UBDristribution from JAN to DEC
UBDist = {0, 0, 0.01, 0.06, 0.23, 0.3, 0.22, 0.13, 0.04, 0.01, 0, 0}

Qavg = {332000.000000181, 370999.999999894, 630999.999999606, 1250999.99999842, 3162000.00000384, 4135000.00000081
    , 2162000.00000183, 1061000.00000169, 652000.000000013, 573000.000000219, 452999.999999978, 363000.000000203}

# in cfs!!! first to sixth level.
Levels = {0, 19000, 28000, 35000, 40000, 73000.0000001413}

# space from Jan to Dec, in acre-feet
Space = {0, 0, 0, 0, 0, 0, 0, 2269999.99999767, 3039999.99999638, 3810000.0000032, 4580000.00000191, 5350000.00000062}

# in acre-feet, Powell, Navajo, BlueMesa, FlamingGorge
CredSpace = {3850000.00000166, 1035900, 748499.999999741, 1507199.99999868}

UBCreditableStorageReservoirs = {"Powell", "Navajo", "BlueMesa", "FlamingGorge"}

# UBRuleCurveData
BaseRuleCurves = {26120000, 26120000, 26120000, 26120000, 26120000, 26120000, 26120000, 26120000
    , 26120000, 26120000, 26120000, 26120000}

MeadBankInitialBalance = 520460.7 + 462154 + 1168799 + 232362

### EqualizationData
# GlenToHoover from Jan to Dec
GlenToHoover = [685799.999999927, 608999.999999643, 527400.000000355, 441499.999999813, 370899.999999696
    , 336400.000000011, 264599.99999994, 160000.000000322, 73400.0000000097, 0, 0, 0]

# --------------------- Mead para end ----------------------

# policies trigger year
defaultTriggerYear = 2021
# defaultTriggerYear = 2026



# determine month based on period
def determineCurrentYear(period):
    pass

def getCurrentYear(t):
    index = t / 12.0
    currentYear = math.floor(index)
    return currentYear

# determine current Jan index
def getCurrentJanIndex(t):
    currentYear = getCurrentYear(t)
    return currentYear * 12 + JAN

# determine current APR index
def getCurrentAprIndex(t):
    currentYear = getCurrentYear(t)
    return currentYear * 12 + APR

# determine current SEP index
def getCurrentSepIndex(t):
    currentYear = getCurrentYear(t)
    return currentYear * 12 + SEP

# determine current OCT index
def getCurrentOctIndex(t):
    currentYear = getCurrentYear(t)
    return currentYear * 12 + OCT

def getPreviousOctIndex(t):
    currentYear = getCurrentYear(t)
    previousYear = currentYear - 1
    if previousYear < 0:
        return BEFORE_START_TIME
    else:
        return previousYear * 12 + OCT

def getPreviousDecIndex(t):
    currentYear = getCurrentYear(t)
    previousYear = currentYear - 1
    if previousYear < 0:
        return BEFORE_START_TIME
    else:
        return previousYear * 12 + DEC

def getEndIndexforSum(index):
    return index + 1

begtime = datetime.datetime(2021, 1, 31)


# return new time given period t.
def getDate(t):
    newTime = begtime + relativedelta(months=+t)
    return newTime