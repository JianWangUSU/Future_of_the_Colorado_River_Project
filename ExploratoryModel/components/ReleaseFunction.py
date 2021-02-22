import components.Parameters as para
import numpy as np
from dateutil.relativedelta import relativedelta
import calendar
import math

# Release function defined in here. Go to here to add new release function.


# ----------------------------------------- CRSS functions begins-----------------------------------

# reproduce CRSS lake Powell equalization policies
# LakePowell: Lake Powell reservoir itself; i: inflow trace index; t: time period index
def crssPolicy(LakePowell, i, t):
    month = LakePowell.para.determineMonth(t)

    # CRSS policy 28
    LakePowell.release[i][t] = PowellOperationsRule(LakePowell, i, t)

    # CRSS policy 24
    LakePowell.release[i][t] = MeetPowellMinObjectiveRelease(LakePowell, i, t)

    # strategy: CRSS release for validation, use CRSS release data
    # self.release[i][j] = self.crssOutflow[i][j]

    # CRSS policy 23
    temp = LowerElevationBalancingTier(LakePowell, i, t)
    if temp != None and temp > 0:
        LakePowell.release[i][t] = temp

    # CRSS policy 22
    temp = MidElevationReleaseTier(LakePowell, i, t)
    if temp != None and temp > 0:
        LakePowell.release[i][t] = temp

    # CRSS policy 21
    if month >= LakePowell.APR or month <= LakePowell.SEP:
        temp = UpperElevationBalancingTierAprilthruSept(LakePowell, i, t)
        if temp != None and temp > 0:
            LakePowell.release[i][t] = temp

    # CRSS policy 20
    if month <= LakePowell.MAR:
        temp = UpperElevationBalancingTierJanthruMarch(LakePowell, i, t)
        if temp != None and temp > 0:
            LakePowell.release[i][t] = temp

    # CRSS policy 19
    temp = EqualizationTier(LakePowell, i, t)
    if temp != None and temp > 0:
        LakePowell.release[i][t] = temp

    return LakePowell.release[i][t]


# CRSS rule 28
def PowellOperationsRule(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth <= reservoir.para.JUL and currentMonth >= reservoir.para.JAN:
        return reservoir.PowellComputeRunoffSeasonRelease[i][t]
    else:
        return reservoir.PowellComputeFallSeasonRelease[i][t]


# CRSS rule 24
def MeetPowellMinObjectiveRelease(reservoir, i, t):
    result = PowellMinObjRelforCurrentMonth(reservoir, i, t)
    if reservoir.release[i][t] < result:
        return result
    else:
        return reservoir.release[i][t]


# CRSS rule 23
def LowerElevationBalancingTier(reservoir, i, t):
    currentYear = reservoir.para.getCurrentYear(t)
    # DEC in previous year
    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.para.BEFORE_START_TIME:
        PowellpreviousDECstroage = reservoir.initStorage
    else:
        PowellpreviousDECstroage = reservoir.storage[i][previousDECindex]

    if PowellpreviousDECstroage < reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellLowerTierElevation):
        tempRelease = ConvertPowellReleaseBalancing(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)
        # return 7.00 maf to 9.5 maf
        result = ComputePowellReleaseBalancing(reservoir, i, t, tempRelease, reservoir.COL700, reservoir.COL950)

        return result


# CRSS rule 22
def MidElevationReleaseTier(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)

    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.para.BEFORE_START_TIME:
        PowellpreviousDECstroage = reservoir.initStorage
        PowellpreviousDECelevation = reservoir.volume_to_elevation(reservoir.initStorage)
        MeadpreviousDECstroage = reservoir.downReservoir.initStorage
        MeadpreviousDECelevation = reservoir.volume_to_elevation(reservoir.downReservoir.initStorage)
    else:
        PowellpreviousDECstroage = reservoir.storage[i][previousDECindex]
        PowellpreviousDECelevation = reservoir.elevation[i][previousDECindex]
        MeadpreviousDECstroage = reservoir.downReservoir.storage[i][previousDECindex]
        MeadpreviousDECelevation = reservoir.downReservoir.elevation[i][previousDECindex]

    if currentMonth <= reservoir.para.SEP:
        if PowellpreviousDECstroage < reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellUpperTierElevation) \
                and PowellpreviousDECstroage >= reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellLowerTierElevation) \
                and MeadpreviousDECstroage >= reservoir.downReservoir.elevation_to_volume(reservoir.para.Hybrid_Mead823Trigger):
            return PowellReducedRelforCurrentMonth(reservoir, reservoir.COL748, i, t)
    else:
        sepIndex = reservoir.para.getCurrentSepIndex(t)

        if reservoir.elevation[i][sepIndex] < reservoir.para.Hybrid_PowellUpperTierElevation \
                and reservoir.elevation[i][sepIndex] >= reservoir.para.Hybrid_PowellLowerTierElevation \
                and reservoir.downReservoir.elevation[i][sepIndex] >= reservoir.para.Hybrid_Mead823Trigger:

            return PowellReducedRelforCurrentMonth(reservoir, reservoir.COL748, i, t)


# CRSS rule 21, Upper Elevation Balancing Tier April thru Sept
def UpperElevationBalancingTierAprilthruSept(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth > reservoir.para.SEP or currentMonth < reservoir.para.APR:
        return

    currentYear = reservoir.para.getCurrentYear(t)
    # DEC in previous year
    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.para.BEFORE_START_TIME:
        PowellpreviousDECstroage = reservoir.initStorage
    else:
        PowellpreviousDECstroage = reservoir.storage[i][previousDECindex]

    # InUpperElevationBalancingTier
    if PowellpreviousDECstroage < reservoir.upperTier[currentYear] and PowellpreviousDECstroage >= reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellUpperTierElevation):
        if (not EqualizationConditionsMet(reservoir, i, t)) and (reservoir.EQTrumpUpperLevelBalancingFlag[i][t - 1] == 0):
            # previous DEC Mead storage
            if previousDECindex == reservoir.para.BEFORE_START_TIME:
                MeadpreviousDECstroage = reservoir.downReservoir.initStorage
            else:
                MeadpreviousDECstroage = reservoir.downReservoir.storage[i][previousDECindex]

            if reservoir.downReservoir.ForecastEOWYSMead[i][reservoir.para.getCurrentAprIndex(t)] < reservoir.downReservoir.elevation_to_volume(reservoir.para.Hybrid_MeadMinBalancingElevation) \
                    and reservoir.ForecastEOWYSPowell[i][reservoir.para.getCurrentAprIndex(t)] > reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellUpperTierElevation) \
                    or MeadpreviousDECstroage < reservoir.downReservoir.elevation_to_volume(reservoir.para.Hybrid_MeadMinBalancingElevation):

                if MeadpreviousDECstroage < reservoir.downReservoir.elevation_to_volume(reservoir.para.Hybrid_MeadMinBalancingElevation):
                    tempRelease = ConvertPowellReleaseBalancing(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)

                    # return 7 maf to 9 maf
                    return ComputePowellReleaseBalancing(reservoir, i, t, tempRelease, reservoir.COL700, reservoir.COL900)
                else:
                    tempRelease = ConvertPowellReleaseBalancing(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)

                    reservoir.testSeries2[i][t] = tempRelease

                    # return 8.23 maf to 9 maf
                    result = ComputePowellReleaseBalancing(reservoir, i, t, tempRelease, reservoir.COL823, reservoir.COL900)
                    reservoir.testSeries3[i][t] = result

                    return result
        else:
            # ComputePowellRelease() in CRSS
            tempRelease = ConvertPowellRelease(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)

            remainingWYReleaseForecast = CheckEqualizationRelease_Mead1105(reservoir, i, t, tempRelease) + reservoir.ForecastPowellRelease[i][t]

            # remainingWYReleaseForecast = self.CheckEqualizationRelease_Mead1105(i, t, self.ComputeEqualizationReleaseList(i, t)) + self.ForecastPowellRelease[i][t]

            result = remainingWYReleaseForecast * GetPowellMonthlyProportion(reservoir, i, t, remainingWYReleaseForecast)

            maxTurbineRelease = GetMaxReleaseGivenInflow(reservoir, i, t)
            if result > maxTurbineRelease:
                result = maxTurbineRelease

            return result

        # written under InUpperElevationBalancingTier
        if EqualizationConditionsMet(reservoir, i, t) or (not (reservoir.EQTrumpUpperLevelBalancingFlag[i][t - 1] == 0)):
            reservoir.EQTrumpUpperLevelBalancingFlag[i][t] = 1


# CRSS rule 20, Upper Elevation Balancing Tier Jan thru March
def UpperElevationBalancingTierJanthruMarch(reservoir, i, t):
    currentYear = reservoir.para.getCurrentYear(t)
    # DEC in previous year
    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.para.BEFORE_START_TIME:
        PowellpreviousDECstroage = reservoir.initStorage
        MeadpreviousDECstroage = reservoir.downReservoir.initStorage
    else:
        PowellpreviousDECstroage = reservoir.storage[i][previousDECindex]
        MeadpreviousDECstroage = reservoir.downReservoir.storage[i][previousDECindex]

    if PowellpreviousDECstroage < reservoir.upperTier[currentYear] and PowellpreviousDECstroage >= reservoir.elevation_to_volume(reservoir.para.Hybrid_PowellUpperTierElevation):
        if MeadpreviousDECstroage < reservoir.downReservoir.elevation_to_volume(reservoir.para.Hybrid_MeadMinBalancingElevation):
            tempRelease = ConvertPowellReleaseBalancing(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)
            # return 7 maf to 9 maf
            return ComputePowellReleaseBalancing(reservoir, i, t, tempRelease, reservoir.COL700, reservoir.COL900)


# CRSS policy 19
def EqualizationTier(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    currentYear = reservoir.para.getCurrentYear(t)
    # DEC in previous year
    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.BEFORE_START_TIME:
        PowellpreviousDECstroage = reservoir.initStorage
    else:
        PowellpreviousDECstroage = reservoir.storage[i][previousDECindex]

    if PowellpreviousDECstroage >= reservoir.upperTier[currentYear] and reservoir.ForecastEOWYSPowell[i][t] > reservoir.downReservoir.ForecastEOWYSMead[i][t]:
        # ComputePowellRelease() in CRSS
        tempRelease = ConvertPowellRelease(reservoir, ComputeEqualizationReleaseList(reservoir, i, t), i, t)

        remainingWYReleaseForecast = CheckEqualizationRelease_Mead1105(reservoir, i, t, tempRelease) + reservoir.ForecastPowellRelease[i][t]

        result = remainingWYReleaseForecast * GetPowellMonthlyProportion(reservoir, i, t, remainingWYReleaseForecast)

        maxTurbineRelease = GetMaxReleaseGivenInflow(reservoir, i, t)
        if result > maxTurbineRelease:
            result = maxTurbineRelease

        return result


def PowellMinObjRelforCurrentMonth(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)

    result = PowellMinObjRelVolRemaining(reservoir, i, t) * reservoir.PowellmonthlyRelease[reservoir.COL823][currentMonth] / ComputeMinObjReleaseRemaining(reservoir, t)

    if result < MinReleaseFun(reservoir, t):
        return MinReleaseFun(reservoir, t)
    else:
        return result


# todo, do not caonsider CarryoverEQReleasesMade now.
def PowellMinObjRelVolRemaining(reservoir, i, t):
    return AnnualMinObjectiveRelease() - ReleaseMade(reservoir, i, t)


def AnnualMinObjectiveRelease():
    return 8230000


def ReleaseMade(reservoir, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    previoiusIndex = t - 1
    if currentMonth == reservoir.para.JAN:
        return PowellFallRelease(reservoir, i, t)
    else:
        if currentMonth > reservoir.para.JAN and currentMonth < reservoir.para.OCT:
            # sum means [min,max)
            return sum(reservoir.outflow[i][reservoir.para.getCurrentJanIndex(t):reservoir.para.getEndIndexforSum(previoiusIndex)]) + PowellFallRelease(reservoir, i, t)
        else:
            if currentMonth == reservoir.para.OCT:
                return 0
            else:
                # here is code for NOV and DEC, sum means [min,max)
                return sum(reservoir.outflow[i][reservoir.para.getCurrentOctIndex(t):reservoir.para.getEndIndexforSum(previoiusIndex)])


def ComputeMinObjReleaseRemaining(reservoir, t):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth <= reservoir.para.SEP:
        # from current month to SEP
        return sum(reservoir.PowellmonthlyRelease[reservoir.COL823][currentMonth: reservoir.para.getEndIndexforSum(reservoir.para.SEP)])
    if currentMonth == reservoir.para.OCT:
        # sum of 12 months
        return sum(reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)])
    if currentMonth == reservoir.para.NOV:
        # only except OCT
        return sum(reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)]) \
               - reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.OCT]
    if currentMonth == reservoir.para.DEC:
        # only except OCT, NOV
        return sum(reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)]) \
               - reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.OCT] \
               - reservoir.PowellmonthlyRelease[reservoir.COL823][reservoir.para.NOV]


def ConvertPowellReleaseBalancing(reservoir, equalizationRelease, i, t):
    return (equalizationRelease - reservoir.ForecastPowellRelease[i][t])


# one potential CRSS problem
# Jian: I think ComputeNewPowellRelease should be TotalPowellRelease.
# Note: Equazliation here means Powell storage == Mead storage
def ComputeEqualizationReleaseList(reservoir, i, t):
    PowellS = reservoir.ForecastEOWYSPowell[i][t]
    MeadS = reservoir.downReservoir.ForecastEOWYSMead[i][t]
    PowellRelease = reservoir.ForecastPowellRelease[i][t]
    index = 0
    # logic here is the same as CRSS, but I think it's not quite right.
    while abs(PowellS - MeadS) > reservoir.EqualizationTolerance and index < 30:
        index = index + 1

        tempPowellRelease = PowellRelease
        tempPowellS = PowellS
        tempMeadS = MeadS

        PowellRelease = TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS)
        PowellS = EOWYStorage(reservoir, i, t, ComputeNewPowellRelease(reservoir, tempPowellRelease, tempPowellS, tempMeadS), reservoir.downReservoir.ForecastMeadRelease[i][t])
        MeadS = EOWYStorage(reservoir.downReservoir, i, t, TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS), reservoir.downReservoir.ForecastMeadRelease[i][t])

    # ConvertPowellReleaseBalancing = PowellRelease - self.ForecastPowellRelease[i][t]
    reservoir.testSeries1[i][t] = PowellRelease

    # ConvertPowellReleaseBalancing is not the same
    # return ConvertPowellReleaseBalancing

    return PowellRelease


def ComputePowellReleaseBalancing(reservoir, i, t, equalizationRelease, minCol, maxCol):
    currentMonth = reservoir.para.determineMonth(t)
    remainingWYReleaseForecast = equalizationRelease + reservoir.ForecastPowellRelease[i][t]
    previousOctIndex = reservoir.para.getPreviousOctIndex(t)

    # past OCT to current time-1, water year outflow released
    if previousOctIndex == reservoir.BEFORE_START_TIME:
        WYOutflowMade = 640000+640000+720000+sum(reservoir.outflow[i][reservoir.para.getCurrentJanIndex(t): reservoir.para.getEndIndexforSum(t - 1)])
    else:
        WYOutflowMade = sum(reservoir.outflow[i][previousOctIndex: reservoir.para.getEndIndexforSum(t - 1)])

    totalWYRelease = min(sum(reservoir.PowellmonthlyRelease[maxCol]), max(remainingWYReleaseForecast + WYOutflowMade, sum(reservoir.PowellmonthlyRelease[minCol])))

    # get column given release
    columnI = GetPowellReleaseColumnIndex(reservoir, totalWYRelease)

    result = remainingWYReleaseForecast * reservoir.PowellmonthlyRelease[columnI][currentMonth] / sum(reservoir.PowellmonthlyRelease[columnI][currentMonth:reservoir.para.getEndIndexforSum(reservoir.para.SEP)])

    minlimit = PowellReducedRelforCurrentMonth(reservoir, minCol, i, t)
    maxlimit = PowellReducedRelforCurrentMonth(reservoir, maxCol, i, t)

    if result > maxlimit:
        result = maxlimit
    if result < minlimit:
        result = minlimit

    return result


def PowellReducedRelforCurrentMonth(reservoir, col, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    PowellReducedRelVolRemaining = sum(reservoir.PowellmonthlyRelease[col]) - ReleaseMade(reservoir, i, t)
    rate = reservoir.PowellmonthlyRelease[col][currentMonth] / ComputeReducedReleaseRemaining(reservoir, col, i, t)
    return PowellReducedRelVolRemaining * rate


def ComputeReducedReleaseRemaining(reservoir, col, i, t):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth <= reservoir.para.SEP:
        # from current month to SEP
        return sum(reservoir.PowellmonthlyRelease[col][currentMonth: reservoir.para.getEndIndexforSum(reservoir.para.SEP)])
    if currentMonth == reservoir.para.OCT:
        # sum of 12 months
        return sum(reservoir.PowellmonthlyRelease[col])
    if currentMonth == reservoir.para.NOV:
        # only except OCT
        return sum(reservoir.PowellmonthlyRelease[col]) - reservoir.PowellmonthlyRelease[col][reservoir.para.OCT]
    if currentMonth == reservoir.para.DEC:
        # only except OCT, NOV
        return sum(reservoir.PowellmonthlyRelease[col]) \
               - reservoir.PowellmonthlyRelease[col][reservoir.para.OCT] \
               - reservoir.PowellmonthlyRelease[col][reservoir.para.NOV]


def ConvertPowellRelease(reservoir, equalizationRelease, i, t):
    return equalizationRelease - reservoir.ForecastPowellRelease[i][t]


def CheckEqualizationRelease_Mead1105(reservoir, i, t, equalizationRelease):
    currentYear = reservoir.para.getCurrentYear(t)

    if reservoir.ForecastEOWYSPowell[i][t] - equalizationRelease < reservoir.upperTier[currentYear]:
        if reservoir.downReservoir.ForecastEOWYSMead[i][t] < reservoir.downReservoir.elevation_to_volume(reservoir.para.MeadProtectionElevation):
            temp = min(reservoir.ForecastEOWYSPowell[i][t] - reservoir.ShiftedEQLine[currentYear]
                       , reservoir.downReservoir.elevation_to_volume(reservoir.para.MeadProtectionElevation) - reservoir.downReservoir.ForecastEOWYSMead[i][t])
            temp2 = min(temp, equalizationRelease)
            return max(reservoir.ForecastEOWYSPowell[i][t] - reservoir.upperTier[currentYear], temp2, 0)
        else:
            return max(reservoir.ForecastEOWYSPowell[i][t] - reservoir.upperTier[currentYear], 0)
    else:
        # minimum number 0 constraint
        return max(equalizationRelease, 0)


def GetPowellMonthlyProportion(reservoir, i, t, remainingWYReleaseForecast):
    currentMonth = reservoir.para.determineMonth(t)
    temp = 0

    CurrentOctIndex = reservoir.para.getCurrentOctIndex(t)
    PreviousOctIndex = reservoir.para.getPreviousOctIndex(t)

    if currentMonth >= reservoir.para.NOV:
        temp = sum(reservoir.outflow[i][CurrentOctIndex: reservoir.para.getEndIndexforSum(t - 1)])
    else:
        if currentMonth == reservoir.para.OCT:
            temp = 0
        else:
            if PreviousOctIndex == reservoir.para.BEFORE_START_TIME:
                temp = 640000 + 640000 + 720000 + sum(reservoir.outflow[i][reservoir.para.getCurrentJanIndex(t): reservoir.para.getEndIndexforSum(t - 1)])
            else:
                temp = sum(reservoir.outflow[i][PreviousOctIndex: reservoir.para.getEndIndexforSum(t - 1)])

    WYReleaseForecast = remainingWYReleaseForecast + temp

    columnI = GetPowellReleaseColumnIndex(reservoir, WYReleaseForecast)

    return reservoir.PowellmonthlyRelease[columnI][currentMonth] / SumoftheRemainingMonthlyReleases(reservoir, columnI, t)


def GetMaxReleaseGivenInflow(reservoir, i, t):
    if t == 0:
        startS = reservoir.initStorage
    else:
        startS = reservoir.storage[i][t - 1]

    startElevation  = reservoir.volume_to_elevation(startS)
    twElevation = 3150
    head = startElevation - twElevation
    maxOutFlow = reservoir.MaxTurbineQ_head_to_TurbineCapacity(head)
    # evaporation and bank assumes to 0 for initial values
    evaporation = 0
    changeofBank = 0
    endS = startS + reservoir.inflow[i][t] - maxOutFlow - changeofBank - evaporation

    if endS < reservoir.minStorage:
        endS = reservoir.minStorage
        maxOutFlow = startS + reservoir.inflow[i][t] - changeofBank - evaporation - endS
    if endS > reservoir.maxStorage:
        endS = reservoir.maxStorage

    index = 0
    oldmaxOutFlow = 0
    while abs(maxOutFlow - oldmaxOutFlow) < 100  and index < 20:
        index = index + 1
        oldendS = maxOutFlow

        twElevation = reservoir.TWTable_outflow_to_Elevation(convertAFtoCFS(reservoir, t, maxOutFlow))
        head = (startElevation + reservoir.volume_to_elevation(endS)) / 2 - twElevation
        maxOutFlow = reservoir.MaxTurbineQ_head_to_TurbineCapacity(head)

        startArea = reservoir.volume_to_area(startS)
        endArea = reservoir.volume_to_area(endS)
        aveArea = (startArea+endArea)/2.0
        evaporation = reservoir.calculateEvaporation(aveArea, startS, endS, i, t)
        changeofBank = EstimateBankStoragewithoutEvap(reservoir, startS, endS)
        endS = startS + reservoir.inflow[i][t] - maxOutFlow - changeofBank - evaporation
        if endS < reservoir.minStorage:
            endS = reservoir.minStorage
            maxOutFlow = startS + reservoir.inflow[i][t] - changeofBank - evaporation - endS
        if endS > reservoir.maxStorage:
            endS = reservoir.maxStorage
            # besides turbine release, there will be spills here, no change for turbine capacity

    return maxOutFlow


# upperTier needs to be volume
def EqualizationConditionsMet(reservoir, i, t):
    currentYear = reservoir.para.getCurrentYear(t)
    currentAprindex = reservoir.para.getCurrentAprIndex(t)
    if reservoir.ForecastEOWYSPowell[i][currentAprindex] >= reservoir.upperTier[currentYear] and reservoir.ForecastEOWYSPowell[i][t] >= reservoir.downReservoir.ForecastEOWYSMead[i][t]:
        return True
    else:
        return False


def PowellFallRelease(reservoir, i, t):
    previousOCTindex = reservoir.para.getPreviousOctIndex(t)
    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex < previousOCTindex:
        print("error in determing previousOCTindex and previousDECindex!")

    if previousOCTindex == reservoir.BEFORE_START_TIME:
        # before start time, if start time = 2021, then it requires to know 2020 OCT to DEC outflow.
        return 640000 + 640000 + 720000
    else:
        # previousDECindex+1 because sum function add [previousOCTindex, previousDECindex+1) values
        return sum(reservoir.outflow[i][previousOCTindex:reservoir.para.getEndIndexforSum(previousDECindex)])


# sum of the remaining monthly releases per the release table
def SumoftheRemainingMonthlyReleases(reservoir, columnI, t):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth <= reservoir.para.SEP:
        # from current month to SEP
        return sum(reservoir.PowellmonthlyRelease[columnI][currentMonth: reservoir.para.getEndIndexforSum(reservoir.para.SEP)])
    if currentMonth == reservoir.para.OCT:
        # sum of 12 months
        return sum(reservoir.PowellmonthlyRelease[columnI][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)])
    if currentMonth == reservoir.para.NOV:
        # only except OCT
        return sum(reservoir.PowellmonthlyRelease[columnI][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)]) \
               - reservoir.PowellmonthlyRelease[columnI][reservoir.para.OCT]
    if currentMonth == reservoir.para.DEC:
        # only except OCT, NOV
        return sum(reservoir.PowellmonthlyRelease[columnI][reservoir.para.JAN: reservoir.para.getEndIndexforSum(reservoir.para.DEC)]) \
               - reservoir.PowellmonthlyRelease[columnI][reservoir.para.OCT] \
               - reservoir.PowellmonthlyRelease[columnI][reservoir.para.NOV]

def GetPowellReleaseColumnIndex(reservoir, forecastWYRelease):
    if forecastWYRelease < sum(reservoir.PowellmonthlyRelease[reservoir.COL700]):
        return reservoir.COL700
    if forecastWYRelease >= sum(reservoir.PowellmonthlyRelease[reservoir.COL1400]):
        return reservoir.COL1400
    for i in range(reservoir.COL700, reservoir.COL1400):
        if forecastWYRelease >= sum(reservoir.PowellmonthlyRelease[i]) and forecastWYRelease < sum(reservoir.PowellmonthlyRelease[i + 1]):
            return i


def ComputeNewPowellRelease(reservoir, tempPowellRelease, tempPowellS, tempMeadS):
    # ignore CheckEqualizationRelease() because don't use list in here.
    EstimateEqualizationRelease = (tempPowellS - tempMeadS)/2.0
    return TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS) + CheckERMeadExclusiveFCS(reservoir, tempMeadS, EstimateEqualizationRelease)


def CheckERMeadExclusiveFCS(reservoir, EOWYSMead, equalizationRelease):
    if EOWYSMead + equalizationRelease > reservoir.downReservoir.maxStorage - reservoir.downReservoir.MinSpace:
        result = reservoir.downReservoir.maxStorage - reservoir.downReservoir.MinSpace - EOWYSMead
        if result < 0:
            return 0
        else:
            return result
    else:
        if equalizationRelease < 0:
            return 0
        else:
            return equalizationRelease


def TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS):
    return tempPowellRelease + (tempPowellS - tempMeadS)/2.0


def EOWYStorage(reservoir, i, t, powellRelease, meadRelease):
    if reservoir.name == "Powell":
        startS = PreviousStorage(reservoir, i, t)
        endS = min(InitialEOWYStoragePowell(reservoir, i, t, powellRelease), reservoir.liveCapacityStorage)
        startPeriod = t
        endPeriod = reservoir.para.getCurrentSepIndex(t)
        result = InitialEOWYStoragePowell(reservoir, i, t, powellRelease) \
                 - EstimateEvaporation(reservoir, startS, endS, startPeriod, endPeriod) \
                 - EstimateBankStoragewithoutEvap(reservoir, startS, endS)
        if result < reservoir.PowellMinimumContent:
            return reservoir.PowellMinimumContent
        if result > reservoir.liveCapacityStorage:
            return reservoir.liveCapacityStorage
        else:
            return result
        # return reservoir.InitialEOWYStoragePowell(i, t, powellRelease) - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
        #        - reservoir.EstimateBankStoragewithoutEvap(startS, endS)
    if reservoir.name == "Mead":
        startS = PreviousStorage(reservoir, i, t)
        endS = min(InitialEOWYStorageMead(reservoir, i, t, powellRelease, meadRelease), reservoir.liveCapacityStorage)
        startPeriod = t
        endPeriod = reservoir.para.getCurrentSepIndex(t)
        result = InitialEOWYStorageMead(reservoir, i, t, powellRelease, meadRelease) \
                 - EstimateEvaporation(reservoir, startS, endS, startPeriod, endPeriod) \
                 - EstimateBankStoragewithoutEvap(reservoir, startS, endS)
        if result < reservoir.inactiveCapacityStorage:
            return reservoir.inactiveCapacityStorage
        if result > reservoir.liveCapacityStorage:
            return reservoir.liveCapacityStorage
        else:
            return result

        # return reservoir.InitialEOWYStorageMead(i, t, powellRelease, meadRelease) - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
        #        - reservoir.EstimateBankStoragewithoutEvap(startS, endS)


def InitialEOWYStoragePowell(reservoir, i, t, powellRelease):
    result = PreviousStorage(reservoir, i, t) + reservoir.ForecastPowellInflow[i][t] - powellRelease

    if result < 0:
        return 0
    else:
        return result
    # return self.PreviousStorage(i, t) + self.ForecastPowellInflow[i][t] - powellRelease


def InitialEOWYStorageMead(reservoir, i, t, powellRelease, meadRelease):
    currentMonth = reservoir.para.determineMonth(t)
    if currentMonth == reservoir.SEP:
        startPeriod = t
        endPeriod = reservoir.para.getCurrentSepIndex(t)

        result = PreviousStorage(reservoir, i, t) + powellRelease - meadRelease \
                 - sum(reservoir.SNWPDiversionTotalDepletionRequested[i][startPeriod: reservoir.para.getEndIndexforSum(endPeriod)]) \
                 + para.GlenToHoover[currentMonth]

        if result < 0:
            return 0
        else:
            return result
    else:
        startPeriod = t
        endPeriod = reservoir.para.getCurrentSepIndex(t)

        # it doesn't make sense to me, but that's how CRSS treats here.
        result = PreviousStorage(reservoir, i, t) + powellRelease - meadRelease \
                 - sum(reservoir.SNWPDiversionTotalDepletionRequested[i][startPeriod: reservoir.para.getEndIndexforSum(endPeriod)]) \
                 + para.GlenToHoover[currentMonth] + sum(para.GlenToHoover[max(currentMonth + 1, reservoir.AUG): reservoir.para.getEndIndexforSum(reservoir.SEP)])

        if result < 0:
            return 0
        else:
            return result


# startDate, endDate: period index
def EstimateEvaporation(reservoir, startStorage, endStorage, startPeriod, endPeriod):
    startArea = reservoir.volume_to_area(startStorage)
    endArea = reservoir.volume_to_area(endStorage)
    eporateRate = 0
    for t in range(startPeriod, endPeriod):
        month = reservoir.para.determineMonth(t)
        eporateRate = eporateRate + reservoir.evapRates[month] * calcualtefractionOfEvaporation(t)

    Evap = (startArea+endArea)/2.0*eporateRate

    return Evap


def EstimateBankStoragewithoutEvap(reservoir, startStorage, endStorage):
    return (endStorage - startStorage) * reservoir.bankRates


# CRSS use this way to change its evapration rates, for Lake Mead
def calcualtefractionOfEvaporation(period):
    currentTime = para.begtime + relativedelta(months=+period)
    rate = calendar.monthrange(currentTime.year, currentTime.month)[1]/31.0

    return rate


def PreviousStorage(reservoir, i, t):
    if t == 0:
        return reservoir.initStorage
    else:
        return reservoir.storage[i][t - 1]


# retrun acre-feet
def MinReleaseFun(reservoir, period):
    currentTime = reservoir.begtime + relativedelta(months=+period)
    days = calendar.monthrange(currentTime.year, currentTime.month)[1]
    return reservoir.para.secondsInaDay * days * reservoir.minRelease * reservoir.para.CFtoAcreFeet


# retrun acre-feet
def MaxReleaseFun(reservoir, period):
    currentTime = reservoir.begtime + relativedelta(months=+period)
    days = calendar.monthrange(currentTime.year, currentTime.month)[1]
    return reservoir.para.secondsInaDay * days * reservoir.maxRelease * reservoir.para.CFtoAcreFeet


# convert acre-feet to cfs
def convertAFtoCFS(reservoir, period, value):
    currentTime = reservoir.begtime + relativedelta(months=+period)
    days = calendar.monthrange(currentTime.year, currentTime.month)[1]
    return value / reservoir.para.CFtoAcreFeet / reservoir.para.secondsInaDay * days


# flood control policy
def MeadFloodControl(self,i, j):
    month = self.para.determineMonth(j)
    if month <= self.JUL and self.outflow[i][j] < self.RunoffSeasonRelease():
        self.outflow[i][j] = self.ComputeMeadSpringReleaseConstrained()
    else:
        if month > self.JUL and self.outflow[i][j] < self.ComputeOutflowAtGivenStorage():
            self.outflow[i][j] = self.ComputeMeadFallReleaseConstrained()

def RunoffSeasonRelease(self):
    pass

def ComputeMeadSpringReleaseConstrained(self):

    pass

def ComputeMeadSpringFCRelease(self):
    pass

def ComputeOutflowAtGivenStorage(self):
    pass

def ComputeMeadFallReleaseConstrained(self):
    pass

def ComputeTargetStorage(self):
    pass

def ComputeStorageAtGivenOutflow(self):
    pass

def SpaceBuilding(self):
    pass

# it is not right, but don't have data for Flaming Gorge.
def UBCreditableSpace(self):
    return sum(self.CredSpace)

def PowellRunoffForecast(self):
    pass

def ComputeMinMeadFloodRelease(self, period):
    month = self.para.determineMonth(period)
    if month == self.JUL:
        pass
    else:
        pass
    pass

def MeadMinReleaseWithoutFloodControl(self, i, t):
    return self.MeadInflowForecast() + self.Qsum[t] - self.AvailableSpace(i, t) - self.upReservoir.AvailableSpace(i, t) \
           + self.MinSpace - self.DeltaBankStorage(i, t) - self.FloodControlEvap(i, t) \
           - self.upReservoir.FloodControlEvap(i, t) - self.SouthernNevConsumed()

def MeadInflowForecast(self):
    pass

def FloodControlEvap(self, i, t):
    return self.volume_to_area(self.LiveCapacity - self.AvailableSpace(i, t) / 2.0) * self.SumEvapCoeff()

def SouthernNevConsumed(self):
    pass

def FloodControlLevelVolume(self):
    pass

# sum evaporation rates from current month to Jul
def SumEvapCoeff(self, t):
    month  = self.para.determineMonth(t)
    sum(self.evapRates[month: self.JUL])

def DeltaBankStorage(self, i, t):
    return self.bankRates * (self.AvailableSpace(i, t) - self.MinSpace) \
    + self.upReservoir.bankRates * self.upReservoir.AvailableSpace(i, t)

# i: inflow trace; j: period
def AvailableSpace(self, i, t):
    if t == 0:
        return self.LiveCapacity - self.initStorage
    else:
        return self.LiveCapacity - self.storage[i][t - 1]

def CurrentAvailableSpace(self, i, j):
    return self.LiveCapacity - self.storage[i][j]


def lastfun():
    pass
# ----------------------------------------- CRSS functions ends-----------------------------------

def ICS(reservoir, i, t):
    user = reservoir.relatedUser

    previousDECindex = reservoir.para.getPreviousDecIndex(t)
    if previousDECindex == reservoir.para.BEFORE_START_TIME:
        MeadpreviousDECstroage = reservoir.initStorage
    else:
        MeadpreviousDECstroage = reservoir.storage[i][previousDECindex]

    if MeadpreviousDECstroage > reservoir.elevation_to_volume(reservoir.para.MeadStartDCPElevation):
        reservoir.relatedUser.annualTake = min(600000, user.MeadBank[i][t])
    elif MeadpreviousDECstroage > reservoir.elevation_to_volume(reservoir.para.MeadMIDDCPElevation):
        reservoir.relatedUser.annualTake = min(400000, user.MeadBank[i][t])
    elif MeadpreviousDECstroage > reservoir.elevation_to_volume(reservoir.para.Hybrid_Mead823Trigger):
        reservoir.relatedUser.annualTake = min(200000, user.MeadBank[i][t])

def FPF(self, storage):
    if storage < self.maxStorage:
        self.column = 1
    else:
        self.column = 2

# re-drill Lake Powell
def redrillPowell(self, storage):
    # 1. empty Lake Powell
    self.column = 8
    # 2. empty storage between 3370 to bottom of the reservoir
    if storage == self.minStorage:
        self.redrillflag = True
    # 3. outflow equals to inflow

# Powell release is a fun of Powell inflow and Mead elevation
def PowellReleaseFun(self, elevation, i, j):
    inflowNextYear = sum(self.inflow[i][j:j+12])
    if elevation > 1090:
        return
    elif elevation > 1075:
        return
    elif elevation >= 1050:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    elif elevation > 1045:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    elif elevation > 1040:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    elif elevation > 1035:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    elif elevation > 1030:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    elif elevation >= para.MeadDCPElevation1:
        if inflowNextYear > 13000000:
            self.column = self.column + 1
    else:
        if inflowNextYear > 13000000:
            self.column = self.column + 1

    self.column = min(self.column, 9)

# fill Mead first
def FMF(reservoir, meadS):
    # Powell to 3370 feet, if Mead reaches to full pool, Powell store water
    if reservoir.name == "Powell":
        if meadS < reservoir.downReservoir.maxStorage:
            reservoir.column = 9
        else:
            reservoir.column = 3

# fill Powell first
# parameter, column for Powell monthly release table
PowellReleasTableCol = 2
def FPF(reservoir, EYstorage, t):
    global PowellReleasTableCol

    month = reservoir.para.determineMonth(t)

    # initialize data before running
    if t == 0:
        PowellReleasTableCol = 2

    # if Lake Powell is full pool, Mead start to store water
    if reservoir.name == "Powell":
        if month == reservoir.para.JAN:
            if EYstorage < reservoir.maxStorage:
                PowellReleasTableCol = 1
            else:
                PowellReleasTableCol = 2

        return reservoir.PowellmonthlyRelease[PowellReleasTableCol][month]

# IntentionallyCreatedSurplus, ICS strategy
# i: inflowtrace
def DCPICScutback(self, elevation, i):
    # max deposit each year: 625,000 acre-feet; max total deposit: 2,100,000 acre-feet; max withdraw each year: 1,000,000
    # when and how much to deposit, when and how much to withdraw
    # deposit 200,000 acre-feet when Mead elevation is higher than 1090 feet; withdraw 0.1 maf DCP cutbacks if we have
    maxtotalICS = 2100000
    maxyearlyICS = 625000
    maxwithdraw = 1000000
    depositThisYear = 200000
    withdrawThisyear = 100000

    if elevation > 1090:
        if self.icsAccount[i] < maxtotalICS - depositThisYear:
            self.icsAccount[i] = self.icsAccount[i] + depositThisYear
            return depositThisYear
        return 0
    elif elevation > 1075:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 200000 - withdrawThisyear
        return 200000
    elif elevation >= 1050:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 533000 - withdrawThisyear
        return 533000
    elif elevation > 1045:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 617000 - withdrawThisyear
        return 617000
    elif elevation > 1040:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 867000 - withdrawThisyear
        return 867000
    elif elevation > 1035:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 917000 - withdrawThisyear
        return 917000
    elif elevation > 1030:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 967000 - withdrawThisyear
        return 967000
    elif elevation >= 1025:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 1017000 - withdrawThisyear
        return 1017000
    else:
        if self.icsAccount[i] > withdrawThisyear:
            self.icsAccount[i] = self.icsAccount[i] - withdrawThisyear
            return 1100000 - withdrawThisyear
        return 1100000


# to do, store water in Lake Powell
def ICSPowell(self, elevation, i):
    # 1. store water in Lake Powell

    # 2. when in shortage, ask Lake Powell for more water
    pass

    # simulation for decision scaling
    def DSsimulation(self, DSdemand, DSinflow, DSinitStorage):
        # simulate one year
        years = 1

        # set initial data
        # set initial values for area, evaporation and precipitation
        area = self.volume_to_area(DSinitStorage)
        evaporation = area * sum(self.evapRates) * years
        precipitation = area * sum(self.precipRates) * years
        endstorage = DSinitStorage + DSinflow + precipitation - evaporation - DSdemand

        # 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        while index < self.iteration:
            area = (self.volume_to_area(DSinitStorage) + self.volume_to_area(endstorage)) / 2.0
            evaporation = area * sum(self.evapRates) * years
            precipitation = area * sum(self.precipRates) * years
            # if storage increases, water flow from reservoir to bank
            changeBankStorage = self.bankRates * (endstorage - DSinitStorage)
            endstorage = DSinitStorage + DSinflow + precipitation - changeBankStorage - evaporation - DSdemand
            index = index + 1

        if endstorage > self.maxStorage:
            endstorage = self.maxStorage
        elif endstorage < self.minStorage:
            endstorage = self.minStorage

        return self.volume_to_elevation(endstorage)

def adaptivePolicy(self, demandtrace, inflowtrace, period):
    month = self.determineMonth(period)
    # in these months, nothing happened

    if month == self.JAN or month == self.FEB or month == self.MAR or month == self.MAY or month == self.JUN or \
            month == self.JUL or month == self.SEP or month == self.NOV or month == self.DEC:
        return

    # signpost 1. Pearce Ferry Rapid: 1135 feet

    if self.name == "Powell":
        if period + 12 > self.periods:
            return

        self.FerryFlag = False

        inflow = sum(self.downReservoir.inflow[inflowtrace][period:period+12]) + sum(self.PowellmonthlyRelease[self.column][0:12])
        demand = sum(self.downReservoir.downDepletion[demandtrace][period:period + 12])
        initS = self.downReservoir.storage[inflowtrace][period-1]
        gap = inflow - demand
        lenS = len(self.downReservoir.Mead_Storage)
        for i in range (0, lenS):
            if initS > self.downReservoir.Mead_Storage[i]:
                if gap > self.downReservoir.inflow_demand[i]:
                    self.FerryFlag = True

        # pass
    # if Mead elevation > 1115 feet, 20 feet buffer, then Store water in Lake Powell (FPF).
    # if Mead elevation < 1050 feet, 10 feet buffer, then Store water in Lake Powell (FPF).

    # 1. Glen canyon dam minimum power pool = 3490 feet
    # 1. if Powell elevation is < 3525 feet, then decreasing UB monthly depletion.
    # if self.name == "Powell":
    #     pass

    pass

# forecast future elevations, this function only triggerd in AUG, APR
# demandtrace: trace number for demand
# inflowtrace: trace number for inflow
# period: current period
# num: month numbers between current period and predicted month, i.e, Aug to DEC, num = 5
# col: which monthly release pattern to use, comes from CRSS Powell monthly release table
# twoWaterYears: When predicting DEC 31 ELEVATION from AUG, this value is true
def forecastFutureElevations(self, demandtrace, inflowtrace, period, num, col, twoWaterYears):
    # if one looks from AUG, 2060 to SEP, 2061, then return and keep current release column
    if period+num > self.periods:
        return

    # naturalInflow assumed to be the predicted future inflow
    # determine Powell inflow
    # totalInflow1 = sum(self.inflow[inflowtrace][period:period+num]) \
    #                - sum(self.upDepletion[demandtrace][period:period+num]) - sum(self.crssUBshortage[inflowtrace][period:period+num])
    totalInflow1 = sum(self.inflow[inflowtrace][period:period+num]) - sum(self.upDepletion[demandtrace][period:period+num])
    # print("num:"+str(num) + " period:" + str(period) + " inflow: " + str(self.inflow[inflowtrace][period:period+num]))

    # inflow should be positive value
    if totalInflow1 < 0:
        totalInflow1 = 0

    # start storage for the current month
    if period == 0:
        startStorage1 = self.initStorage
    else:
        startStorage1 = self.storage[inflowtrace][period-1]
        # print("storage: "+str(self.storage[inflowtrace][period-1]))

    startArea1 = self.volume_to_area(startStorage1)

    # print("startStorage1: "+str(startStorage1))

    # learn from CRSS, an assumed targetSpace
    endStorage1 = self.maxStorage - self.targetSpace
    endArea1 = self.volume_to_area(endStorage1)

    month = self.determineMonth(period)
    # predicted evaporation and change of bank storage
    if num > 12: # AUG, current year to SEP, next year
        # one year predicted evap
        tempEvap12 = sum(self.evapRates[0: 12])*(startArea1+endArea1)/2.0
        # other months predicted evap
        tempEvapOthers = sum(self.evapRates[month: month+num-12])*(startArea1+endArea1)/2.0
        evaporation1 = tempEvap12 + tempEvapOthers
    else: # AUG TO DEC, OR APR TO SEP
        evaporation1 = sum(self.evapRates[month: month+num])*(startArea1+endArea1)/2.0
    bankStorage1 = (endStorage1-startStorage1)*self.bankRates

    #
    if twoWaterYears: # AUG, current year to SEP, next year, span two water years
        # AUG + SEP
        releaseAugSep = sum(self.PowellmonthlyRelease[col][month: month+2])
        tempcolumn = 2 # assume release is 8.23 MAF/year, which is column 3 of monthly release table
        # the following months
        if month + num > 12:
            releaseNextWY = sum(self.PowellmonthlyRelease[tempcolumn][0: 12])
        else:
            releaseNextWY = sum(self.PowellmonthlyRelease[tempcolumn][month+2: month+num])
        release1 = releaseAugSep + releaseNextWY
    else: # looking into future from APR
        release1 = sum(self.PowellmonthlyRelease[col][month: month+num])

    endStorage1 = startStorage1 + totalInflow1 - evaporation1 - bankStorage1 - release1

    # month = self.determineMonth(period)
    # if month == self.AUG:
    #     print(self.volume_to_elevation(endStorage1))
    #     print(endStorage1)
    #     print(startStorage1)
    #     print(totalInflow1)
    #     print(evaporation1)
    #     print(bankStorage1)
    #     print(release1)
    # if inflowtrace == 40 and period > 366 and period < 386:
    #     print("endS:"+str(endStorage1))
    #     print("startS:"+str(startStorage1))
    #     print("INFLOW:"+str(totalInflow1))
    #     print("evap:"+str(evaporation1))
    #     print("bank:"+str(bankStorage1))
    #     print("releaseAUG:"+str(releaseAugSep))
    #     print("releaseNext:"+str(releaseNextWY))
    #     print("release:"+str(release1))

    if endStorage1 > self.maxStorage:
        endStorage1 = self.maxStorage
        release1 = startStorage1 + totalInflow1 - evaporation1 - bankStorage1 - endStorage1
    elif endStorage1 < self.minStorage:
        endStorage1 = self.minStorage
        release1 = startStorage1 + totalInflow1 - evaporation1 - bankStorage1 - endStorage1
        if release1 < 0:
            release1 = 0

    # if inflowtrace == 40 and period > 366 and period < 386:
    #     print("----------------")
    #     print(col)
    #     print(totalInflow1)
    #     print(release1)
    #     print("================")

    # Mead total inflow
    totalInflow2 = sum(self.downReservoir.inflow[inflowtrace][period:period+num]) + release1

    # start and storage/area
    if period == 0:
        startStorage2 = self.downReservoir.initStorage
    else:
        startStorage2 = self.downReservoir.storage[inflowtrace][period-1]
    startArea2 = self.downReservoir.volume_to_area(startStorage2)
    endStorage2 = self.downReservoir.maxStorage - self.downReservoir.targetSpace
    endArea2 = self.downReservoir.volume_to_area(endStorage2)

    month = self.determineMonth(period)
    if num > 12: # AUG, current year to SEP, next year
        tempEvap12 = sum(self.downReservoir.evapRates[0: 12])*(startArea2+endArea2)/2.0
        tempEvapOthers = sum(self.downReservoir.evapRates[month: month+num-12])*(startArea2+endArea2)/2.0
        evaporation2 = tempEvap12 + tempEvapOthers
    else:
        evaporation2 = sum(self.downReservoir.evapRates[month: month+num])*(startArea2+endArea2)/2.0
    bankStorage2 = (endStorage2-startStorage2)*self.downReservoir.bankRates

    # downstream requirements
    # release2 = sum(self.downReservoir.downDepletion[demandtrace][period:period+num])
    release2 = sum(self.downReservoir.downDepletion[demandtrace][period:period+num]) - self.downReservoir.MeadMDeductionCurrent*num
    endStorage2 = startStorage2 + totalInflow2 - evaporation2 - bankStorage2 - release2

    if endStorage2 > self.downReservoir.maxStorage:
        endStorage2 = self.downReservoir.maxStorage
    elif endStorage2 < self.downReservoir.minStorage:
        endStorage2 = self.downReservoir.minStorage

    result = np.zeros([2])
    result[0] = self.volume_to_elevation(endStorage1)
    result[1] = self.downReservoir.volume_to_elevation(endStorage2)

    return result

# Equalization policy for Lake Powell and Lake Mead
def Equalization(reservoir1, reservoir2, startStorage1, startStorage2, inflow1, release2, intervenningInflow2, t):
    # Step 1: Get current Powell and Mead storage
    # Step 2: Calculate End of year storage
    # Step 3: change Lake Powell release and find the release balance two reservoirs
    JAN = reservoir1.para.JAN
    DEC = reservoir1.para.DEC

    # gap = Powell storage - Mead storage
    allCol = reservoir1.allColumns
    gap = np.zeros([len(allCol)])

    for col in allCol:
        release1 = sum(reservoir1.PowellmonthlyRelease[col][JAN:DEC+1])
        endStorage1 = startStorage1 + inflow1 - release1
        inflow2 = release1 + intervenningInflow2
        endStorage2 = startStorage2 + inflow2 - release2
        startPeriod = t
        endPeriod = t + 12

        index = 0
        tempEndStorage1 = 0
        tempEndStorage2 = 0
        while (abs(endStorage1 - tempEndStorage1) > reservoir1.EqualizationTolerance
                or abs(endStorage2 - tempEndStorage2) > reservoir1.EqualizationTolerance) \
                and index < 30:
            index = index + 1
            tempEndStorage1 = endStorage1
            tempEndStorage2 = endStorage2

            endStorage1 = startStorage1 + inflow1 - release1 \
                          - EstimateEvaporation(reservoir1, startStorage1, endStorage1, startPeriod, endPeriod) \
                          - EstimateBankStoragewithoutEvap(reservoir1, startStorage1, endStorage1)

            endStorage2 = startStorage2 + inflow2 - release2\
                          - EstimateEvaporation(reservoir2, startStorage2, endStorage2, startPeriod, endPeriod) \
                          - EstimateBankStoragewithoutEvap(reservoir2, startStorage2, endStorage2)

        # print(inflow2, release2)
        # if t == 0:
        #     print(col, endStorage2, endStorage1)

        gap[col] = abs(endStorage2 - endStorage1)

    # print("====================================")

    minGAP = min(gap)

    for col in allCol:
        if gap[col] == minGAP:
            return col

# re-drill Lake Powell
def redrillPowell(self, storage):
    # 1. empty Lake Powell to dead pool
    self.column = 9
    # 2. empty storage between 3370 to bottom of the reservoir
    if storage == self.minStorage:
        self.redrillflag = True
    # 3. outflow equals to inflow


# cutback from 2007 Guidelines (combined volume) for Lake Mead, acre-feet
def cutbackfromGuidelines(elevation):
    length = len(para.MeadIGSElevations)

    for i in range(length):
        if elevation > para.MeadIGSElevations[i]:
            return para.MeadIGScutbacks[i]

        if i == length - 1:
            return para.MeadIGScutbacks[length]


# Drought contingency plan (combined volume) for Lake Mead, acre-feet
# Coding in a general way, USE table, seperate code from data, properties and methods.
def cutbackFromDCP(elevation):
    length = len(para.MeadDCPElevations)

    for i in range(length):
        if elevation > para.MeadDCPElevations[i]:
            return para.MeadDCPcutbacks[i]

        if i == length - 1:
            return para.MeadDCPcutbacks[length]
