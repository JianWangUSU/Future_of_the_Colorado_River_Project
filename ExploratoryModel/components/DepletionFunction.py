import components.Parameters as para
import components.ICS_DCP_Surplus as OtherData

# May not be used in Exploratory model

# CRSS policy 9, i: inflow trace; t: time period
def ReduceMexicobyComputedBWSCPSavingsandCreateBWSCPSavings (MexicoUser, i, t):
    month = para.determineMonth(t)
    year = para.determineCurrentYear(t)
    if month != para.JAN:
        return

    if MexicoUser.DCPMXBWSCPSavingsVolume[i][year] > 0:
        monthlyReduction = MexicoUser.DCPMXBWSCPSavingsVolume[i][t] / 12.0
        for m in range(12):
            MexicoUser.DepltionRequest[i][t+m] = MexicoUser.DepltionRequest[i][t+m] - monthlyReduction

        MexicoUser.ICMABWSCPActualAnnualPut[i][year] = MexicoUser.DCPMXBWSCPSavingsVolume[i][t]

# look up DCP contributions table based on Mead pool elevation
def DetermineDCPContribution(user, i, t):
    pass

# CRSS policy 159
def SetRequiredDCPandBWSCPContributions(user, i, t):
    if user.name == "MexicoDiversion":
        user.DCPMXBWSCPSavingsVolume[i][t] = DetermineDCPContribution(user, i, t)
    else:
        user.DCPContributionVolume[i][t] = DetermineDCPContribution(user, i, t)

# CRSS policy 56
def Quantified7StatePlanLevel1Surplus(user, i, t):
    month = para.determineMonth(t)
    year = para.determineCurrentYear(t)

    # only triggered on JAN
    if month != para.JAN:
        return

    # This is a important trigger!
    if OtherData.SurplusRelease[year] <= 0:
        return

    deliveryAdjustmentFor323 = GetMonthlyUSReductionForMXIncrease(user, i, t)

    for m in range(12):
        temp = ComputeSurplusDepl7StatePlanLevel1(user, i, t+m) + GetICSDeliveryAdjustment(user, i, t+m) - deliveryAdjustmentFor323
        user.DepletionRequest[i][t] = temp * LBUserToAggRatio(user, i, t+m)

def ComputeSurplusDepl7StatePlanLevel1(user, i, t):
    pass

def GetICSDeliveryAdjustment(user, i, t):
    pass

def LBUserToAggRatio(user, i, t):
    pass

def GetMonthlyUSReductionForMXIncrease(user, i, t):
    pass

def USUsersReducedForMXIncrease():
    return list()

# CRSS policy 58
def IncreaseMXDeliveryfromMinute32x(user, i, t):
    month = para.determineMonth(t)
    year = para.determineCurrentYear(t)
    if month != para.JAN:
        return

    if user.name != "MexicoDiversion":
        return

    if user.AnnualIncreaseVolume[year] <= 0:
        return

    for m in range(12):
        increaseAmount = user.AnnualIncreaseVolume[year] * SurplusMonthlyPercent(user, month)
        user.DepltionRequest[i][t+m] = user.DepltionRequest[i][t+m] + increaseAmount

def SurplusMonthlyPercent(user, i, t):
    # look up $ "Surplus.MonthlyPercents" tables
    pass

# CRSS policy 59
def SetMexicoMinute323AnnualIncreaseduetoHighReservoirConditions():
    # assume Minute 323 not expires until 2060
    # look up $ "MexicoSchedule.HighElevationAnnualIncrease" based on Mead elevation.
    pass

# CRSS policy 33
def Compute70RAssuranceLevelSurplusVolume():
    pass
    # one item about SumPreviousYearICSCredits

def SumPreviousYearICSCredits():
    pass
    # one item about PreviousYearBankBalance()

def ComputeBankBalance():
    # previous left + put - take - DCP removed evaporation assessment
    pass

def ComputeArizonaAvailableICSWater():
    pass