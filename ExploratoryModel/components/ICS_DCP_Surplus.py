
# Surplus release.
SurplusRelease = None

# AZ
ArizonaBankInitialBalance = 520460.7 # in acre-feet
ArizonaBank = None
# annual data
ArizonaPutSchedule = None
ArizonaTakeSchedule = None

# monthly data
ArizonaICSTotalActualMonthlyPut = None
# sum of following series, put schedule is determined. only put in 2021.
# $ "Arizona ICS.ActualMonthlyPut", run 0 determine by policy 39
# $ "Arizona ICS.CRITActualMonthlyPut", run 0 determine by policy 39
# $ "Arizona ICS.GRICActualMonthlyPut" , run 0 determine by policy 39
#      --> Arizona ICS.AnnualRequestedPut, Arizona ICS.CRITAnnualRequestedPut, Arizona ICS.GRICAnnualRequestedPut, direct inputs
# $ "Arizona ICS.MVIDDActualMonthlyPut"
#      --> from Arizona ICS.MVIDDAnnualRequestedPut, direct input
# $ "Arizona ICS.DCPActualMonthlyPut", run 0 determine by policy 39
#      --> Arizona ICS.ConvertECToDCP, determine by CRSS policy 51

ArizonaICSTotalActualMonthlyTake = None
#      --> the following takes are determined by policy 39, varied in different hydrology
# $ "Arizona ICS.ActualMonthlyTake", policy 39, RUN 0, VALUE 0
# $ "Arizona ICS.GRICFedActualMonthlyTake", policy 39, RUN 0, VALUE 0
# $ "Arizona ICS.GRICAZActualMonthlyTake", policy 39, RUN 0, VALUE 0
# $ "Arizona ICS.GRICActualMonthlyTake"
# $ "Arizona ICS.CRITActualMonthlyTake"
# $ "Arizona ICS.BICSActualMonthlyTake", calculated monthly
#      --> policy 39, DetermineArizonaAnnualTake(), MANY PARAMETERS THERE, related to CAP end time (2025), Mead elevation, shortage tier
#      --> DetermineArizonaECICSUnmetDemand, DetermineArizonaAnnualTake
#       DrainCAWCDICS(), $ "Arizona ICS.GRICAnnualRequestedTake", $ "Arizona ICS.CRITAnnualRequestedTake", $ "Arizona ICS.InputBICSAnnualTake", ActualAZTribalFirmingTake, DetermineAZDCPTake

# $ "Arizona ICS.BrockActualMonthlyTake"
# $ "Arizona ICS.YDPActualMonthlyTake"
# $ "Arizona ICS.DCPActualMonthlyTake", policy 39, RUN 0, VALUE 0

# CA
CaliforniaBankInitialBalance = 1168799
CaliforniaBank = None
# MWD + IID

IIDBank = None
# existing + PUT - TAKE - EVAP
# IID TAKE = 0, but IID BANK decrease
# IID ICS.ECActualAnnualPut, Attempts to keep IID's bank full.

MWDBank = None
# $ "MWD ICS.ECBalance", $ "MWD ICS.TotalDCPBalance", $ "MWD ICS.BICSAvailableBalance"

# $ "MWD ICS.ECBalance" related to the following three parameters
MWDICSECActualAnnualPut = None
MWDICSECActualAnnualTake = None
MWDICSConvertECToDCP = None
# determined by policy 43
# MWDICSECActualAnnualPut --> DetermineMWDDesiredPut --> $ "MWD ICS.AnnualRequestedPutTake", look up a table triggered by different condition
# MWDICSECActualAnnualTake --> DetermineMWDDesiredTake --> $ "MWD ICS.AnnualRequestedPutTake", look up a table triggered by different condition
# Remember MWD ICS.AnnualRequestedPutTake means all take for MWD, only MWDICSECActualAnnualTake works one MWDBank.

MWDICSTotalDCPBalance = None
# "ConvertECToDCP"
# "DCPActualAnnualPut"
# "DCPActualAnnualTake"
# They are 0, determined by some policies

MWDICSBICSAvailableBalance = None
# $ "MWD ICS.BICSAvailableBalance", value doesn't change with different hydrology

# NV
NevadaBank = None
# $ "Nevada ICS.ECBalance" $ "Nevada ICS.DCPBalance" $ "Nevada ICS.BICSAvailableBalance" (static value),

# Nevada ICS.DCPBalance, not quite understand why DCP was considered
NVDCPBalance = None
# Computes Nevada's DCP-ICS take based on their demand above 300 kaf, the available DCP-ICS balance, and the ability to recover DCP-ICS.
NevadaICSDCPActualAnnualTake = None
# Computes Nevada's annual DCP-ICS creation. Will only be non-zero if Nevada does not have enough EC credits to convert to DCP ICS.
NevadaICSDCPActualAnnualPut = None
NevadaICSDCPAdditionalAnnualContribution = None
# determine by policy 51
# Computes Nevada's DCP-ICS take based on their demand above 300 kaf, the available DCP-ICS balance, and the ability to recover DCP-ICS.

# Mexico
# Intentionally Created Mexican Allocation (ICMA)
ICMABank = None # include $ "ICMA.Balance" and $ "ICMA.BWSCPBalance"
ICMAInitialBalance = 191362

# "ICMA.Balance"
ICMAConvertMWRToBWSCP = None, # set to 0 by input data
ICMAActualAnnualPut = None # set to 0 by CRSS policy 52
ICMAActualAnnualTake = None # set to 0 by CRSS policy 52

# "ICMA.BWSCPBalance"
BWSCPBalance = None # set to 0
ICMABWSCPActualAnnualTake = None # # set to 0 by CRSS policy 52
ICMABWSCPActualAnnualPut = None  # determined by DCP contribution, not very clear.

# 2020 10 14
# What do we do when reservoir drop below, DCP is one form of cutback rule. ICS gives user flexiblity to store water, allocate Surplus water,
# a lot of assumptions.
# reduce ICS program, talk LB ICS as a total!!! interact with reservoir level. What is a good put/take strategy.
# ICS combined with Pearce Ferry Rapid. linkage between water supply and environemntal impact. ICS
# ICS general form give user flexiblity to store and release later. Another name, flex accounts, may yield a good environemntal AMP
# pools for tribal
# Ecosystem gets a flex account.
# keep in mind reproduce the rules, not use them much. Reproducing as much as possible, what they really doing, re-create behaviours of those rules.
#

