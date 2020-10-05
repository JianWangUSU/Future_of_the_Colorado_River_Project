from components.Reservoir import Reservoir
import numpy as np
import sys
import math

class LakePowell(Reservoir):
    # Only for Powell, monthly release table
    PowellmonthlyRelease = None
    # column of the monthly release table, current water year
    column = 2
    # column of the monthly release table, next water year
    columnNext = 2
    # used in CRSS, not exactly the same
    targetSpace = 0

    redrillflag = False # only for Lake Powell, true means redrill
    lastPowellStorage = 1.89 # storage between 3370 to bottom of Lake Powell

    # Combined Upper Basin Storage, used by drought response operation
    ubStorage = None
    # Flaming Gorge, Blue Mesa, Morrow Point, Crystal, Navajo
    initUBstorage = 3319784 + 584695 + 112001 + 16969 + 1450225
    minUBstorage = 0
    # Flaming Gorge (6039), Blue Mesa (7519.4), Morrow Point, Crystal, Navajo (6085)
    maxUBstorage = 3710151 + 830704 + 111819 + 16957 + 1701300
    # Flaming Gorge (6027), Blue Mesa (7498), Morrow Point (7153.73), Crystal (6753.04), Navajo (6065)
    targetUBstorage = 3234735 + 644992 + 111819 + 16957 + 1412737
    # UB release
    UBreleaseFlag = False
    # UB release next month
    UBmonthRelease = 0
    # UB refill next month
    UBmonthRefill = 0

    # column for monthly release table
    COL700 = 0
    COL748 = 1
    COL823 = 2
    COL900 = 3
    COL950 = 4
    COL1050 = 5
    COL1100 = 6
    COL1200 = 7
    COL1300 = 8
    COL1400 = 9

    # CRSS UBRuleCurveData, from JAN to DEC
    targetSpace = {0,0,0,0,0,0,500000,1222000,1722000,2022000,2322000,2422000}

    # Equalization data
    EQTrumpUpperLevelBalancingFlag = None
    EqualizationTolerance = 10000

    # Periodic Net Evaporation
    grossEvapCoef = None
    riverEvapCoef = None
    streamsideCoef = None
    terranceCoef = None
    averageAirTemp = None
    averagePrecip = None

    grossEvaporation = None
    riverEvaporation = None
    streamsideEvaporation = None
    terraceEvaporation = None
    remainingEvaporation = None
    salvageEvaporation = None

    # PNE: Periodic Net Evaporation
    PNETableElevation = None
    PNETableRiverArea = None
    PNETableStreamsideArea = None
    PNETableTerranceArea = None

    PowellComputeRunoffSeasonRelease = None
    PowellComputeFallSeasonRelease = None

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)

    def setupPeriodsandTraces(self):
        super().setupPeriodsandTraces()
        self.ubStorage = np.zeros([self.inflowTraces, self.periods])
        self.grossEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.riverEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.streamsideEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.terraceEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.remainingEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.salvageEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.EQTrumpUpperLevelBalancingFlag = np.zeros([self.inflowTraces, self.periods])

    # simulate one time period, k: depletionTrace, i: inflowTrace, t: period
    def simulationSinglePeriod(self, k, i, t):
        ### 1. determine the start of reservoir storage in the current time period.
        startStorage = 0
        if t == 0:
            startStorage = self.initStorage
            self.ubStorage[i][t] = self.initUBstorage
        else:
            startStorage = self.storage[i][t - 1]
            self.ubStorage[i][t] = self.ubStorage[i][t - 1]

        ### 2. determine inflow for the current month, add shortage
        # inflowthismonth = self.inflow[i][j] - (self.upDepletion[k][j] + self.crssUBshortage[i][j])
        inflowthismonth = self.inflow[i][t] - self.upDepletion[k][t]
        if inflowthismonth < 0:
            inflowthismonth = 0
        if self.UBreleaseFlag == True:
            if self.UBmonthRelease <= self.ubStorage[i][t]:
                inflowthismonth = inflowthismonth + self.UBmonthRelease
                self.ubStorage[i][t] = self.ubStorage[i][t] - self.UBmonthRelease
            else:
                inflowthismonth = inflowthismonth + self.ubStorage[i][t]
                self.ubStorage[i][t] = self.ubStorage[i][t] - self.ubStorage[i][t]
        else:
            if self.ubStorage[i][t] < self.targetUBstorage:
                if inflowthismonth < self.UBmonthRefill:
                    inflowthismonth = 0
                    self.ubStorage[i][t] = self.ubStorage[i][t] + inflowthismonth
                    if self.ubStorage[i][t] > self.targetUBstorage:
                        inflowthismonth = inflowthismonth + self.ubStorage[i][t] - self.targetUBstorage
                        self.ubStorage[i][t] = self.targetUBstorage
                else:
                    inflowthismonth = inflowthismonth - self.UBmonthRefill
                    self.ubStorage[i][t] = self.ubStorage[i][t] + self.UBmonthRefill
                    if self.ubStorage[i][t] > self.targetUBstorage:
                        inflowthismonth = inflowthismonth + self.ubStorage[i][t] - self.targetUBstorage
                        self.ubStorage[i][t] = self.targetUBstorage

        # monthly release table
        self.upShortage[i][t] = self.upDepletion[k][t] - (self.inflow[i][t] - inflowthismonth)
        if self.upShortage[i][t] < 0:
            self.upShortage[i][t] = 0

        # validation use, use CRSS INFLOW data
        inflowthismonth = self.crssInflow[i][t]
        self.totalinflow[i][t] = inflowthismonth

        ### 3. determine policy. equalization rule is only triggered in Apr and Aug
        # strategy equalization + DCP
        if self.plc.EQUAL_DCP == True:
            self.equalizationAndDCP(k, i, t)
        # strategy adaptive policy (only consider Pearce Ferry Rapid now)
        if self.plc.ADP == True:
            self.adaptivePolicy(k, i, t)
        # strategy FPF
        if self.plc.FPF == True:
            self.FPF(startStorage)
        # strategy re-drill Lake Powell (FMF)
        if self.plc.FMF == True:
            self.redrillPowell(startStorage)


        # determine which month are we in
        month = self.determineMonth(t)
        # self.release[i][j] = 0
        # monthly release table
        # print(str(i)+" "+str(j) +" "+str(self.column) +" "+str(month))
        # self.release[i][j] = self.PowellmonthlyRelease[self.column][month]

        # If Pearce Ferry Rapid flag is true, decreasing Powell outflow
        # if self.downReservoir.FerryFlag == True:
        #     if self.column >= 2:
        #         self.release[i][j] = self.PowellmonthlyRelease[self.column - 2][month]

        # After re-drilling Lake Powell
        # if self.redrillflag == True:
        #
        #     # There are 1.89 maf between dead pool and bottom pool elevation for Lake Powell
        #     if self.lastPowellStorage > 0:
        #         # outflow = inflow + 1.89/12 maf/mth
        #         self.release[i][j] = self.inflow[i][j] + 1.89 / 12 * 1000000
        #         self.lastPowellStorage = self.lastPowellStorage - 1.89/12
        #     else:
        #         # outflow = inflow
        #         self.release[i][j] = self.totalinflow[i][j]
        #         self.elevation[i][j] = self.minElevation
        #
        #     # calculate UB shortage
        #     self.upShortage[i][j] = self.upDepletion[k][j] - (self.inflow[i][j] - inflowthismonth)
        #     if self.upShortage[i][j] < 0:
        #         self.upShortage[i][j] = 0
        #
        #     return

        # outflow meet boundary conditions
        # self.release[i][j] = max(self.release[i][j], self.MinReleaseFun(j))

        # CRSS policy 28
        self.release[i][t] = self.PowellOperationsRule(i, t)

        # CRSS policy 24
        self.release[i][t] = self.MeetPowellMinObjectiveRelease(i, t)

        # strategy: CRSS release for validation, use CRSS release data
        # self.release[i][j] = self.crssOutflow[i][j]

        # CRSS policy 23
        temp = self.LowerElevationBalancingTier(i,t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        # CRSS policy 22
        temp = self.MidElevationReleaseTier(i,t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        # CRSS policy 21
        if month >= self.APR or month <= self.SEP:
            temp = self.UpperElevationBalancingTierAprilthruSept(i, t)
            if temp != None and temp > 0:
                self.release[i][t] = temp

        # CRSS policy 20
        if month <= self.MAR:
            temp = self.UpperElevationBalancingTierJanthruMarch(i, t)
            if temp != None and temp > 0:
                self.release[i][t] = temp

        # CRSS policy 19
        temp = self.EqualizationTier(i, t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, t)

        ### 7. calculate UB shortage for the current time period
        self.upShortage[i][t] = self.upDepletion[k][t] - (self.inflow[i][t] - inflowthismonth)
        if self.upShortage[i][t] < 0:
            self.upShortage[i][t] = 0

    # solve water balance equation given outflow
    def sovleStorageGivenOutflow(self, startStorage, inflowthismonth, month, i, j):
        ### 5. set initial data for water balance calculation
        # set initial area, evaporation values
        self.area[i][j] = self.volume_to_area(startStorage)
        self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
        self.storage[i][j] = startStorage + inflowthismonth - self.evaporation[i][j] - self.release[i][j]

        ### 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        while index < self.iteration:
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            # self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
            self.evaporation[i][j] = self.calculateEvaporation(self.area[i][j], startStorage, self.storage[i][j],i,j)
            # if storage increases, water flow from reservoir to bank
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.storage[i][j] = startStorage + inflowthismonth - self.changeBankStorage[i][j] - self.evaporation[i][j] - self.release[i][j]
            index = index + 1

        if self.storage[i][j] > self.maxStorage:
            self.spill[i][j] = self.storage[i][j] - self.maxStorage
            self.storage[i][j] = self.maxStorage
        elif self.storage[i][j] < self.minStorage:
            self.storage[i][j] = self.minStorage
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            # self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
            self.evaporation[i][j] = self.calculateEvaporation(self.area[i][j], startStorage, self.storage[i][j],i,j)
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.release[i][j] = startStorage - self.storage[i][j] + inflowthismonth - self.changeBankStorage[i][j] - self.evaporation[i][j]

        self.outflow[i][j] = self.release[i][j] + self.spill[i][j]
        self.elevation[i][j] = self.volume_to_elevation(self.storage[i][j])

    # CRSS policy 19
    def EqualizationTier(self, i, t):
        currentMonth = self.determineMonth(t)
        currentYear = self.getCurrentYear(t)
        # DEC in previous year
        previousDECindex = self.getPreviousDecIndex(t)
        if previousDECindex == self.BEFORE_START_TIME:
            PowellpreviousDECstroage = self.initStorage
        else:
            PowellpreviousDECstroage = self.storage[i][previousDECindex]

        if PowellpreviousDECstroage >= self.upperTier[currentYear] and self.ForecastEOWYSPowell[i][t] > self.downReservoir.ForecastEOWYSMead[i][t]:
            # ComputePowellRelease() in CRSS
            tempRelease = self.ConvertPowellRelease(self.ComputeEqualizationReleaseList(i, t), i, t)

            remainingWYReleaseForecast = self.CheckEqualizationRelease_Mead1105(i, t, tempRelease) + self.ForecastPowellRelease[i][t]

            result = remainingWYReleaseForecast * self.GetPowellMonthlyProportion(i, t, remainingWYReleaseForecast)

            maxTurbineRelease = self.GetMaxReleaseGivenInflow(i, t)
            if result > maxTurbineRelease:
                result = maxTurbineRelease

            return result

    # CRSS rule 20, Upper Elevation Balancing Tier Jan thru March
    def UpperElevationBalancingTierJanthruMarch(self, i, t):
        currentMonth = self.determineMonth(t)
        if currentMonth > self.SEP or currentMonth < self.APR:
            return

        currentYear = self.getCurrentYear(t)
        # DEC in previous year
        previousDECindex = self.getPreviousDecIndex(t)
        if previousDECindex == self.BEFORE_START_TIME:
            PowellpreviousDECstroage = self.initStorage
            MeadpreviousDECstroage = self.downReservoir.initStorage
        else:
            PowellpreviousDECstroage = self.storage[i][previousDECindex]
            MeadpreviousDECstroage = self.downReservoir.storage[i][previousDECindex]

        if PowellpreviousDECstroage < self.upperTier[currentYear] and PowellpreviousDECstroage >= self.elevation_to_volume(self.Hybrid_PowellUpperTierElevation):
            if MeadpreviousDECstroage < self.downReservoir.elevation_to_volume(self.Hybrid_MeadMinBalancingElevation):
                tempRelease = self.ConvertPowellReleaseBalancing(self.ComputeEqualizationReleaseList(i, t), i, t)
                # return 7 maf to 9 maf
                return self.ComputePowellReleaseBalancing(i, t, tempRelease, self.COL700, self.COL900)

    # CRSS rule 21, Upper Elevation Balancing Tier April thru Sept
    def UpperElevationBalancingTierAprilthruSept(self, i, t):
        currentMonth = self.determineMonth(t)
        if currentMonth > self.SEP or currentMonth < self.APR:
            return

        currentYear = self.getCurrentYear(t)
        # DEC in previous year
        previousDECindex = self.getPreviousDecIndex(t)
        if previousDECindex == self.BEFORE_START_TIME:
            PowellpreviousDECstroage = self.initStorage
        else:
            PowellpreviousDECstroage = self.storage[i][previousDECindex]

        # InUpperElevationBalancingTier
        if PowellpreviousDECstroage < self.upperTier[currentYear] and PowellpreviousDECstroage >= self.elevation_to_volume(self.Hybrid_PowellUpperTierElevation):
            if (not self.EqualizationConditionsMet(i, t)) and (self.EQTrumpUpperLevelBalancingFlag[i][t - 1] == 0):
                # previous DEC Mead storage
                if previousDECindex == self.BEFORE_START_TIME:
                    MeadpreviousDECstroage = self.downReservoir.initStorage
                else:
                    MeadpreviousDECstroage = self.downReservoir.storage[i][previousDECindex]

                if self.downReservoir.ForecastEOWYSMead[i][self.getCurrentAprIndex(t)] < self.downReservoir.elevation_to_volume(self.Hybrid_MeadMinBalancingElevation) \
                        and self.ForecastEOWYSPowell[i][self.getCurrentAprIndex(t)] > self.elevation_to_volume(self.Hybrid_PowellUpperTierElevation) \
                        or MeadpreviousDECstroage < self.downReservoir.elevation_to_volume(self.Hybrid_MeadMinBalancingElevation):

                    if MeadpreviousDECstroage < self.downReservoir.elevation_to_volume(self.Hybrid_MeadMinBalancingElevation):
                        tempRelease = self.ConvertPowellReleaseBalancing(self.ComputeEqualizationReleaseList(i, t), i, t)

                        # return 7 maf to 9 maf
                        return self.ComputePowellReleaseBalancing(i, t, tempRelease, self.COL700, self.COL900)
                    else:
                        tempRelease = self.ConvertPowellReleaseBalancing(self.ComputeEqualizationReleaseList(i, t), i, t)

                        self.testSeries2[i][t] = tempRelease

                        # return 8.23 maf to 9 maf
                        result = self.ComputePowellReleaseBalancing(i, t, tempRelease, self.COL823, self.COL900)
                        self.testSeries3[i][t] = result

                        return result
            else:
                # ComputePowellRelease() in CRSS
                tempRelease = self.ConvertPowellRelease(self.ComputeEqualizationReleaseList(i, t), i, t)

                remainingWYReleaseForecast = self.CheckEqualizationRelease_Mead1105(i, t, tempRelease) + self.ForecastPowellRelease[i][t]

                # remainingWYReleaseForecast = self.CheckEqualizationRelease_Mead1105(i, t, self.ComputeEqualizationReleaseList(i, t)) + self.ForecastPowellRelease[i][t]

                result = remainingWYReleaseForecast * self.GetPowellMonthlyProportion(i, t, remainingWYReleaseForecast)

                maxTurbineRelease = self.GetMaxReleaseGivenInflow(i, t)
                if result > maxTurbineRelease:
                    result = maxTurbineRelease

                return result

            # written under InUpperElevationBalancingTier
            if self.EqualizationConditionsMet(i, t) or (not (self.EQTrumpUpperLevelBalancingFlag[i][t - 1] == 0)):
                self.EQTrumpUpperLevelBalancingFlag[i][t] = 1

    def ConvertPowellRelease(self, equalizationRelease, i, t):
        return equalizationRelease - self.ForecastPowellRelease[i][t]

    def ConvertPowellReleaseBalancing(self, equalizationRelease, i, t):
        return (equalizationRelease - self.ForecastPowellRelease[i][t])

    def GetMaxReleaseGivenInflow(self, i, t):
        if t == 0:
            startS = self.initStorage
        else:
            startS = self.storage[i][t-1]

        startElevation  = self.volume_to_elevation(startS)
        twElevation = 3150
        head = startElevation - twElevation
        maxOutFlow = self.MaxTurbineQ_head_to_TurbineCapacity(head)
        # evaporation and bank assumes to 0 for initial values
        evaporation = 0
        changeofBank = 0
        endS = startS + self.inflow[i][t] - maxOutFlow - changeofBank - evaporation

        if endS < self.minStorage:
            endS = self.minStorage
            maxOutFlow = startS + self.inflow[i][t] - changeofBank - evaporation - endS
        if endS > self.maxStorage:
            endS = self.maxStorage

        index = 0
        oldmaxOutFlow = 0
        while abs(maxOutFlow - oldmaxOutFlow) < 100  and index < 20:
            index = index + 1
            oldendS = maxOutFlow

            twElevation = self.TWTable_outflow_to_Elevation(self.convertAFtoCFS(t,maxOutFlow))
            head = (startElevation+self.volume_to_elevation(endS))/2 - twElevation
            maxOutFlow = self.MaxTurbineQ_head_to_TurbineCapacity(head)

            startArea = self.volume_to_area(startS)
            endArea = self.volume_to_area(endS)
            aveArea = (startArea+endArea)/2.0
            evaporation = self.calculateEvaporation(aveArea, startS, endS, i, t)
            changeofBank = self.EstimateBankStoragewithoutEvap(startS, endS)
            endS = startS + self.inflow[i][t] - maxOutFlow - changeofBank - evaporation
            if endS < self.minStorage:
                endS = self.minStorage
                maxOutFlow = startS + self.inflow[i][t] - changeofBank - evaporation - endS
            if endS > self.maxStorage:
                endS = self.maxStorage
                # besides turbine release, there will be spills here, no change for turbine capacity

        return maxOutFlow

    def CheckEqualizationRelease_Mead1105(self, i, t, equalizationRelease):
        currentYear = self.getCurrentYear(t)

        if self.ForecastEOWYSPowell[i][t] - equalizationRelease < self.upperTier[currentYear]:
            if self.downReservoir.ForecastEOWYSMead[i][t] < self.downReservoir.elevation_to_volume(self.MeadProtectionElevation):
                temp = min(self.ForecastEOWYSPowell[i][t] - self.ShiftedEQLine[currentYear]
                           , self.downReservoir.elevation_to_volume(self.MeadProtectionElevation) - self.downReservoir.ForecastEOWYSMead[i][t])
                temp2 = min(temp, equalizationRelease)
                return max(self.ForecastEOWYSPowell[i][t] - self.upperTier[currentYear], temp2, 0)
            else:
                return max(self.ForecastEOWYSPowell[i][t] - self.upperTier[currentYear], 0)
        else:
            # minimum number 0 constraint
            return max(equalizationRelease, 0)

    def GetPowellMonthlyProportion(self, i, t, remainingWYReleaseForecast):
        currentMonth = self.determineMonth(t)
        temp = 0

        CurrentOctIndex = self.getCurrentOctIndex(t)
        PreviousOctIndex = self.getPreviousOctIndex(t)

        if currentMonth >= self.NOV:
            temp = sum(self.outflow[i][CurrentOctIndex: self.getEndIndexforSum(t-1)])
        else:
            if currentMonth == self.OCT:
                temp = 0
            else:
                if PreviousOctIndex == self.BEFORE_START_TIME:
                    temp = 640000 + 640000 + 720000 + sum(self.outflow[i][self.getCurrentJanIndex(t): self.getEndIndexforSum(t-1)])
                else:
                    temp = sum(self.outflow[i][PreviousOctIndex: self.getEndIndexforSum(t-1)])

        WYReleaseForecast = remainingWYReleaseForecast + temp

        columnI = self.GetPowellReleaseColumnIndex(WYReleaseForecast)

        return self.PowellmonthlyRelease[columnI][currentMonth]/self.SumoftheRemainingMonthlyReleases(columnI, t)

    # CRSS problem, Jian: I think ComputeNewPowellRelease should be TotalPowellRelease. Also, equazliation here means Powell storage == Mead storage
    def ComputeEqualizationReleaseList(self, i, t):
        PowellS = self.ForecastEOWYSPowell[i][t]
        MeadS = self.downReservoir.ForecastEOWYSMead[i][t]
        PowellRelease = self.ForecastPowellRelease[i][t]
        index = 0
        # logic here is the same as CRSS, but it's not right.
        while abs(PowellS - MeadS) > self.EqualizationTolerance and index < 30:
            index = index + 1

            tempPowellRelease = PowellRelease
            tempPowellS = PowellS
            tempMeadS = MeadS

            PowellRelease = self.TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS)
            PowellS = self.EOWYStorage(self, i, t, self.ComputeNewPowellRelease(tempPowellRelease, tempPowellS, tempMeadS), self.downReservoir.ForecastMeadRelease[i][t])
            MeadS = self.EOWYStorage(self.downReservoir, i, t, self.TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS), self.downReservoir.ForecastMeadRelease[i][t])

        #     if i == 0 and t == 399:
        #         print("-----------------------")
        #         print(index)
        #         print(PowellRelease)
        #         print(PowellS)
        #         print(MeadS)
        #
        # if i == 0 and t == 399:
        #     print("==============")
        #     print(PowellRelease)
        #     print(PowellS)
        #     print(MeadS)

        # ConvertPowellReleaseBalancing = PowellRelease - self.ForecastPowellRelease[i][t]
        self.testSeries1[i][t] = PowellRelease

        # ConvertPowellReleaseBalancing is not the same
        # return ConvertPowellReleaseBalancing

        return PowellRelease

    def TotalPowellRelease(self, tempPowellRelease, tempPowellS, tempMeadS):
        return tempPowellRelease + (tempPowellS - tempMeadS)/2.0

    def ComputeNewPowellRelease(self, tempPowellRelease, tempPowellS, tempMeadS):
        # ignore CheckEqualizationRelease() because don't use list in here.
        EstimateEqualizationRelease = (tempPowellS - tempMeadS)/2.0
        return self.TotalPowellRelease(tempPowellRelease, tempPowellS, tempMeadS) + self.CheckERMeadExclusiveFCS(tempMeadS, EstimateEqualizationRelease)

    def CheckERMeadExclusiveFCS(self, EOWYSMead, equalizationRelease):
        if EOWYSMead + equalizationRelease > self.downReservoir.maxStorage - self.downReservoir.MinSpace:
            result = self.downReservoir.maxStorage - self.downReservoir.MinSpace - EOWYSMead
            if result < 0:
                return 0
            else:
                return result
        else:
            if equalizationRelease < 0:
                return 0
            else:
                return equalizationRelease


    def ComputePowellReleaseBalancing(self, i, t, equalizationRelease, minCol, maxCol):
        currentMonth = self.determineMonth(t)
        remainingWYReleaseForecast = equalizationRelease + self.ForecastPowellRelease[i][t]
        previousOctIndex = self.getPreviousOctIndex(t)

        # past OCT to current time-1, water year outflow released
        if previousOctIndex == self.BEFORE_START_TIME:
            WYOutflowMade = 640000+640000+720000+sum(self.outflow[i][self.getCurrentJanIndex(t): self.getEndIndexforSum(t-1)])
        else:
            WYOutflowMade = sum(self.outflow[i][previousOctIndex: self.getEndIndexforSum(t-1)])

        totalWYRelease = min(sum(self.PowellmonthlyRelease[maxCol]), max(remainingWYReleaseForecast + WYOutflowMade, sum(self.PowellmonthlyRelease[minCol])))

        # get column given release
        columnI = self.GetPowellReleaseColumnIndex(totalWYRelease)

        result = remainingWYReleaseForecast * self.PowellmonthlyRelease[columnI][currentMonth] / sum(self.PowellmonthlyRelease[columnI][currentMonth:self.getEndIndexforSum(self.SEP)])

        minlimit = self.PowellReducedRelforCurrentMonth(minCol, i, t)
        maxlimit = self.PowellReducedRelforCurrentMonth(maxCol, i, t)

        if result > maxlimit:
            result = maxlimit
        if result < minlimit:
            result = minlimit

        return result

    def PowellReducedRelforCurrentMonth(self, col, i, t):
        currentMonth = self.determineMonth(t)
        PowellReducedRelVolRemaining = sum(self.PowellmonthlyRelease[col]) - self.ReleaseMade(i,t)
        rate = self.PowellmonthlyRelease[col][currentMonth] / self.ComputeReducedReleaseRemaining(col, i, t)
        return PowellReducedRelVolRemaining * rate

    def ComputeReducedReleaseRemaining(self, col, i, t):
        currentMonth = self.determineMonth(t)
        if currentMonth <= self.SEP:
            # from current month to SEP
            return sum(self.PowellmonthlyRelease[col][currentMonth: self.getEndIndexforSum(self.SEP)])
        if currentMonth == self.OCT:
            # sum of 12 months
            return sum(self.PowellmonthlyRelease[col])
        if currentMonth == self.NOV:
            # only except OCT
            return sum(self.PowellmonthlyRelease[col]) - self.PowellmonthlyRelease[col][self.OCT]
        if currentMonth == self.DEC:
            # only except OCT, NOV
            return sum(self.PowellmonthlyRelease[col]) \
                   - self.PowellmonthlyRelease[col][self.OCT] \
                   - self.PowellmonthlyRelease[col][self.NOV]


    def GetPowellReleaseColumnIndex(self, forecastWYRelease):
        if forecastWYRelease < sum(self.PowellmonthlyRelease[self.COL700]):
            return self.COL700
        if forecastWYRelease >= sum(self.PowellmonthlyRelease[self.COL1400]):
            return self.COL1400
        for i in range(self.COL700, self.COL1400):
            if forecastWYRelease >= sum(self.PowellmonthlyRelease[i]) and forecastWYRelease < sum(self.PowellmonthlyRelease[i+1]):
                return i


    def adaptivePolicy(self, demandtrace, inflowtrace, period):
        month = self.determineMonth(period)
        # in these months, nothing happened

        if month == self.JAN or month == self.FEB or month == self.MAR or month == self.MAY or month == self.JUN or \
                month == self.JUL or month == self.SEP or month == self.NOV or month == self.DEC:
            return

        # signpost 1. Pearce Ferry Rapid: 1135 feet

        if period + 12 > self.periods:
            return

        self.downReservoir.FerryFlag = False

        inflow = sum(self.downReservoir.inflow[inflowtrace][period:period+12]) + sum(self.PowellmonthlyRelease[self.column][0:12])
        demand = sum(self.downReservoir.downDepletion[demandtrace][period:period + 12])
        initS = self.downReservoir.storage[inflowtrace][period-1]
        gap = inflow - demand
        lenS = len(self.downReservoir.Mead_Storage)
        for i in range (0, lenS):
            if initS > self.downReservoir.Mead_Storage[i]:
                if gap > self.downReservoir.inflow_demand[i]:
                    self.downReservoir.FerryFlag = True

        # Other signposts
        # if Mead elevation > 1115 feet, 20 feet buffer, then Store water in Lake Powell (FPF).
        # if Mead elevation < 1050 feet, 10 feet buffer, then Store water in Lake Powell (FPF).

        # 1. Glen canyon dam minimum power pool = 3490 feet
        # 1. if Powell elevation is < 3525 feet, then decreasing UB monthly depletion.

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
        elif elevation >= 1025:
            if inflowNextYear > 13000000:
                self.column = self.column + 1
        else:
            if inflowNextYear > 13000000:
                self.column = self.column + 1

        self.column = min(self.column, 9)

    # equalization + DCP, only triggered for Lake Powell
    def equalizationAndDCP(self, demandtrace, inflowtrace, period):
        month = self.determineMonth(period)
        # in these months, nothing happened

        if month == self.JAN or month == self.FEB or month == self.MAR or month == self.MAY or month == self.JUN or \
                month == self.JUL or month == self.SEP or month == self.NOV or month == self.DEC:
            return

        # equalization rule is triggered in AUG, then adjusted in APR
        MeadJan1elevation = self.equalization(demandtrace, inflowtrace, period)
        # if month == self.AUG:
        #     self.downReservoir.MeadMDeductionNext = self.downReservoir.cutbackFromDCP(MeadJan1elevation) / 12
        # elif month == self.OCT:
        #     self.downReservoir.MeadMDeductionCurrent = self.downReservoir.MeadMDeductionNext

    def equalization(self, demandtrace, inflowtrace, period):
        # inflow, release to determine end of year storage
        month = self.determineMonth(period)

        # print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:"+ str(month))

        predictedMeadElevation = 0

        # APR adjustment. Determine SEP 31 elevation, and adjust column
        if month == self.APR:
            predictedMonth = 6  # APR TO SEP
            col = self.column

            # print("-----------------------------------------------------")

            predictedElevations = self.forecastFutureElevations(demandtrace, inflowtrace, period, predictedMonth, col,
                                                                True)
            predictedPowellElevation = predictedElevations[0]
            predictedMeadElevation = predictedElevations[1]

            # print("1 period: " + str(period) + " column:" + str(self.column))
            # print("1 predictedPowellElevation: " + str(predictedPowellElevation) + " predictedMeadElevation:" + str(predictedMeadElevation))
            # SP = self.elevation_to_volume(predictedPowellElevation)
            # SM = self.downReservoir.elevation_to_volume(predictedMeadElevation)
            # RP = SP/self.maxStorage
            # RM = SM/self.downReservoir.maxStorage
            # print("1 powell rate: " + str(RP) + " mead rate:" + str(RM))
            #
            # print("======================================================")

            if predictedPowellElevation > self.determineUpperTier(period):
                # 8.23 to 14 MAF/year
                minCol = 3
                maxCol = 10
                self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol,
                                                             maxCol, True)

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) /predictedMonth

            elif predictedPowellElevation > 3575:
                if predictedMeadElevation >= 1075:
                    self.column = 2  # annual release for Powell 8.23 MAF
                else:
                    # 7.0 and 9.0 maf, which means 4 columns to test
                    minCol = 0
                    maxCol = 4
                    self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                                 minCol, maxCol, True)

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) /predictedMonth

            elif predictedPowellElevation > 3525:
                if predictedMeadElevation >= 1025:
                    self.column = 1  # annual release for Powell 7.48 MAF
                else:
                    self.column = 2  # annual release for Powell 8.23 MAF

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) /predictedMonth

            elif predictedPowellElevation > 3370:
                # 7.0 and 9.5 maf
                minCol = 0
                maxCol = 5
                self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                             minCol, maxCol, True)
                self.UBreleaseFlag = True
                self.UBmonthRelease = (self.elevation_to_volume(3525) - self.elevation_to_volume(predictedPowellElevation))/predictedMonth

            # print("period: " + str(period) +" column:" + str(self.column))

        # AUG, determine annual water year release for the next water year
        # Since it starts from Oct, there are two variables, one for this year to Sep, one for next year From OCT
        if month == self.AUG:
            # AUG TO DEC, number of months
            predictedMonth = 5
            # predict JAN 1 elevation
            col = 2

            # print("-----------------------------------------------------------------------------------")
            # print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:" + str(month))

            predictedElevations = self.forecastFutureElevations(demandtrace, inflowtrace, period, predictedMonth, col,
                                                                True)
            predictedPowellElevation = predictedElevations[0]
            predictedMeadElevation = predictedElevations[1]

            # print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:" + str(month))
            # print(predictedPowellElevation)
            # 14 means AUG this year to SEP next year, when determining equalized release based on EOWY elevation
            predictedMonth = 14

            if predictedPowellElevation > self.determineUpperTier(period):
                # 8.23 to 14 MAF/year
                minCol = 3
                maxCol = 10
                self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                                 minCol, maxCol, True)
                # print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:"+ str(month))
                # print(self.columnNext)

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) /predictedMonth

            elif predictedPowellElevation > 3575:
                if predictedMeadElevation >= 1075:
                    self.columnNext = 2  # annual release for Powell 8.23 MAF
                else:
                    # 7.0, 7.48, 8.23, 9.0 maf, which means 4 columns to test
                    minCol = 0
                    maxCol = 4
                    # print("-----------------------------------------------------")
                    self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol, maxCol, True)
                    # print("1 period: " + str(period) + " columnNext:" + str(self.columnNext))
                    # print("1 predictedPowellElevation: " + str(predictedPowellElevation) + " predictedMeadElevation:" + str(predictedMeadElevation))
                    # SP = self.elevation_to_volume(predictedPowellElevation)
                    # SM = self.downReservoir.elevation_to_volume(predictedMeadElevation)
                    # RP = SP/self.maxStorage
                    # RM = SM/self.downReservoir.maxStorage
                    # print("1 powell rate: " + str(RP) + " mead rate:" + str(RM))
                    # print("=====================================================")

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) / predictedMonth

            elif predictedPowellElevation > 3525:
                if predictedMeadElevation >= 1025:
                    self.columnNext = 1  # annual release for Powell 7.48 MAF
                else:
                    self.columnNext = 2  # annual release for Powell 8.23 MAF

                self.UBreleaseFlag = False
                if self.ubStorage[inflowtrace][period] < self.targetUBstorage:
                    self.UBmonthRefill = (self.targetUBstorage - self.ubStorage[inflowtrace][period]) /predictedMonth

            elif predictedPowellElevation > 3370:
                # 7.0 and 9.5 maf
                minCol = 0
                maxCol = 5
                self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                                 minCol, maxCol, True)

                self.UBreleaseFlag = True
                self.UBmonthRelease = (self.elevation_to_volume(3525) - self.elevation_to_volume(predictedPowellElevation))/predictedMonth
            # print("2 period: " + str(period) +" columnNext:" + str(self.columnNext))

        # OCT, come in the next water year.
        if month == self.OCT:
            if self.columnNext == None:  # for the last year
                self.column = 2
            else:
                self.column = self.columnNext

            return

        # if predictedMeadElevation < self.downReservoir.volume_to_elevation(self.downReservoir.minStorage):
        #     print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:"+ str(month))
        #     print(predictedMeadElevation)
        #     print(self.downReservoir.volume_to_elevation(self.downReservoir.minStorage))

        return predictedMeadElevation

    # determine column of equalization release
    # totalCol max value 10, it means 10 release pattern to use, ranges from 7.0, 7.48, 8.23, ... 14.00 MAF/year
    def determineEqualizedRelease(self,demandtrace, inflowtrace, period, num, minCol, maxCol, twoWaterYears):
        if period+num > self.periods:
            return

        # Powell end of year storage
        # naturalInflow is assumed to be the predicted future inflow
        gap = np.zeros([maxCol])
        for i in range (0,maxCol):
            gap[i] = sys.maxsize

        for col in range(minCol, maxCol):
            # determine Powell inflow from Sep to Dec
            tempElevations = self.forecastFutureElevations(demandtrace, inflowtrace, period, num, col, twoWaterYears)
            # print("Pelevation:"+str(tempElevations[0]) + " Melevation:" + str(tempElevations[1]))

            endStorage1 = self.elevation_to_volume(tempElevations[0])
            endStorage2 = self.downReservoir.elevation_to_volume(tempElevations[1])

            gap[col] = abs(endStorage1/self.maxStorage - endStorage2/self.downReservoir.maxStorage)
            # print("col:" + str(col) + " " + str(gap[col]))
            # if inflowtrace == 40 and period > 366 and period < 386:
            #     print(period)
            #     print(self.determineMonth(period))
            #     print("Pstorage:"+str(endStorage1) + " Mstorage:" + str(endStorage2))
            #     print("PRATE:"+str(endStorage1/self.maxStorage) + " Mrate:" + str(endStorage2/self.downReservoir.maxStorage))

        index = 0
        minVal = sys.maxsize
        # print("min:"+str(minCol)+" max:"+str(maxCol))
        # for i in range (minCol, maxCol):
        #     # print("col:" + str(i) + " " + str(gap[i]))
        #     if gap[i] <= minVal:
        #         index = i
        #         minVal = gap[i]

        b = np.array(range(minCol, maxCol))
        for i in reversed (b):
            # print("col:" + str(i) + " " + str(gap[i]))
            if gap[i] <= minVal:
                index = i
                minVal = gap[i]

        return index

    # Periodic Net Evaporation
    def calculateEvaporation(self, area, startS, endS, i, t):
        month = self.determineMonth(t)
        startEle = self.volume_to_elevation(startS)
        endEle = self.volume_to_elevation(endS)

        self.grossEvaporation[i][t] = area * self.grossEvapCoef[month]

        tempRiverArea = (self.elevation_to_riverArea(startEle)+ self.elevation_to_riverArea(endEle)) / 2.0
        self.riverEvaporation[i][t] = tempRiverArea * self.riverEvapCoef[month]

        tempStreamSideArea = (self.elevation_to_streamsideArea(startEle)+ self.elevation_to_streamsideArea(endEle)) / 2.0
        self.streamsideEvaporation[i][t] = tempStreamSideArea * self.streamsideCoef[month] * self.averageAirTemp[month]

        tempTerranceArea = (self.elevation_to_terranceArea(startEle)+ self.elevation_to_terranceArea(endEle)) / 2.0
        self.terraceEvaporation[i][t] = tempTerranceArea * self.terranceCoef[month] * self.averageAirTemp[month]

        tempRemainArea = area - tempRiverArea - tempStreamSideArea - tempTerranceArea
        self.remainingEvaporation[i][t] = tempRemainArea * self.averagePrecip[month]

        self.salvageEvaporation[i][t] = self.riverEvaporation[i][t] + self.streamsideEvaporation[i][t] \
                                        + self.terraceEvaporation[i][t] + self.remainingEvaporation[i][t]

        return self.grossEvaporation[i][t] - self.salvageEvaporation[i][t]


    def elevation_to_riverArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableRiverArea)

    def elevation_to_streamsideArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableStreamsideArea)

    def elevation_to_terranceArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableTerranceArea)

    # upperTier needs to be volume
    def EqualizationConditionsMet(self, i, t):
        currentYear = self.getCurrentYear(t)
        currentAprindex = self.getCurrentAprIndex(t)
        if self.ForecastEOWYSPowell[i][currentAprindex] >= self.upperTier[currentYear] and self.ForecastEOWYSPowell[i][t] >= self.downReservoir.ForecastEOWYSMead[i][t]:
            return True
        else:
            return False

    # CRSS rule 24
    def MeetPowellMinObjectiveRelease(self, i, t):
        result = self.PowellMinObjRelforCurrentMonth(i, t)
        if self.release[i][t] < result:
            return result
        else:
            return self.release[i][t]

    # CRSS rule 23
    def LowerElevationBalancingTier(self, i, t):
        currentYear = self.getCurrentYear(t)
        # DEC in previous year
        previousDECindex = self.getPreviousDecIndex(t)
        if previousDECindex == self.BEFORE_START_TIME:
            PowellpreviousDECstroage = self.initStorage
        else:
            PowellpreviousDECstroage = self.storage[i][previousDECindex]

        if PowellpreviousDECstroage < self.elevation_to_volume(self.Hybrid_PowellLowerTierElevation):
            tempRelease = self.ConvertPowellReleaseBalancing(self.ComputeEqualizationReleaseList(i, t), i, t)
            # return 7.00 maf to 9.5 maf
            result = self.ComputePowellReleaseBalancing(i, t, tempRelease, self.COL700, self.COL950)

            return result

    # CRSS rule 22
    def MidElevationReleaseTier(self, i, t):
        currentMonth = self.determineMonth(t)

        previousDECindex = self.getPreviousDecIndex(t)
        if previousDECindex == self.BEFORE_START_TIME:
            PowellpreviousDECstroage = self.initStorage
            PowellpreviousDECelevation = self.volume_to_elevation(self.initStorage)
            MeadpreviousDECstroage = self.downReservoir.initStorage
            MeadpreviousDECelevation = self.volume_to_elevation(self.downReservoir.initStorage)
        else:
            PowellpreviousDECstroage = self.storage[i][previousDECindex]
            PowellpreviousDECelevation = self.elevation[i][previousDECindex]
            MeadpreviousDECstroage = self.downReservoir.storage[i][previousDECindex]
            MeadpreviousDECelevation = self.downReservoir.elevation[i][previousDECindex]

        if currentMonth <= self.SEP:
            if PowellpreviousDECstroage < self.elevation_to_volume(self.Hybrid_PowellUpperTierElevation) \
                    and PowellpreviousDECstroage >= self.elevation_to_volume(self.Hybrid_PowellLowerTierElevation) \
                    and MeadpreviousDECstroage >= self.downReservoir.elevation_to_volume(self.downReservoir.Hybrid_Mead823Trigger):
                return self.PowellReducedRelforCurrentMonth(self.COL748, i, t)
        else:
            sepIndex = self.getCurrentSepIndex(t)

            if self.elevation[i][sepIndex] < self.Hybrid_PowellUpperTierElevation \
                    and self.elevation[i][sepIndex] >= self.Hybrid_PowellLowerTierElevation \
                    and self.downReservoir.elevation[i][sepIndex] >= self.downReservoir.Hybrid_Mead823Trigger:

                return self.PowellReducedRelforCurrentMonth(self.COL748, i, t)

    def PowellMinObjRelforCurrentMonth(self, i, t):
        currentMonth = self.determineMonth(t)

        result = self.PowellMinObjRelVolRemaining(i, t) * self.PowellmonthlyRelease[self.COL823][currentMonth] / self.ComputeMinObjReleaseRemaining(t)

        if result < self.MinReleaseFun(t):
            return self.MinReleaseFun(t)
        else:
            return result

    def ComputeMinObjReleaseRemaining(self, t):
        currentMonth = self.determineMonth(t)
        if currentMonth <= self.SEP:
            # from current month to SEP
            return sum(self.PowellmonthlyRelease[self.COL823][currentMonth: self.getEndIndexforSum(self.SEP)])
        if currentMonth == self.OCT:
            # sum of 12 months
            return sum(self.PowellmonthlyRelease[self.COL823][self.JAN: self.getEndIndexforSum(self.DEC)])
        if currentMonth == self.NOV:
            # only except OCT
            return sum(self.PowellmonthlyRelease[self.COL823][self.JAN: self.getEndIndexforSum(self.DEC)])\
                   - self.PowellmonthlyRelease[self.COL823][self.OCT]
        if currentMonth == self.DEC:
            # only except OCT, NOV
            return sum(self.PowellmonthlyRelease[self.COL823][self.JAN: self.getEndIndexforSum(self.DEC)])\
                   - self.PowellmonthlyRelease[self.COL823][self.OCT] \
                   - self.PowellmonthlyRelease[self.COL823][self.NOV]

    # sum of the remaining monthly releases per the release table
    def SumoftheRemainingMonthlyReleases(self, columnI, t):
        currentMonth = self.determineMonth(t)
        if currentMonth <= self.SEP:
            # from current month to SEP
            return sum(self.PowellmonthlyRelease[columnI][currentMonth: self.getEndIndexforSum(self.SEP)])
        if currentMonth == self.OCT:
            # sum of 12 months
            return sum(self.PowellmonthlyRelease[columnI][self.JAN: self.getEndIndexforSum(self.DEC)])
        if currentMonth == self.NOV:
            # only except OCT
            return sum(self.PowellmonthlyRelease[columnI][self.JAN: self.getEndIndexforSum(self.DEC)])\
                   - self.PowellmonthlyRelease[columnI][self.OCT]
        if currentMonth == self.DEC:
            # only except OCT, NOV
            return sum(self.PowellmonthlyRelease[columnI][self.JAN: self.getEndIndexforSum(self.DEC)])\
                   - self.PowellmonthlyRelease[columnI][self.OCT] \
                   - self.PowellmonthlyRelease[columnI][self.NOV]


    # todo, do not caonsider CarryoverEQReleasesMade now.
    def PowellMinObjRelVolRemaining(self,i,j):
        return self.AnnualMinObjectiveRelease() - self.ReleaseMade(i,j)

    def AnnualMinObjectiveRelease(self):
        return 8230000

    def ReleaseMade(self,i,j):
        currentMonth = self.determineMonth(j)
        previoiusIndex = j-1
        if currentMonth == self.JAN:
            return self.PowellFallRelease(i,j)
        else:
            if currentMonth > self.JAN and currentMonth < self.OCT:
                # sum means [min,max)
                return sum(self.outflow[i][self.getCurrentJanIndex(j):self.getEndIndexforSum(previoiusIndex)]) + self.PowellFallRelease(i,j)
            else:
                if currentMonth == self.OCT:
                    return 0
                else:
                    # here is code for NOV and DEC, sum means [min,max)
                    return sum(self.outflow[i][self.getCurrentOctIndex(j):self.getEndIndexforSum(previoiusIndex)])

    def PowellFallRelease(self,i,j):
        previousOCTindex = self.getPreviousOctIndex(j)
        previousDECindex = self.getPreviousDecIndex(j)
        if previousDECindex < previousOCTindex:
            print("error in determing previousOCTindex and previousDECindex!")

        if previousOCTindex == self.BEFORE_START_TIME:
            # before start time, if start time = 2021, then it requires to know 2020 OCT to DEC outflow.
            return 640000 + 640000 + 720000
        else:
            # previousDECindex+1 because sum function add [previousOCTindex, previousDECindex+1) values
            return sum(self.outflow[i][previousOCTindex:self.getEndIndexforSum(previousDECindex)])


    # CRSS rule 28
    def PowellOperationsRule(self, i, t):
        currentMonth = self.determineMonth(t)
        if currentMonth <= self.JUL and currentMonth >= self.JAN:
            return self.PowellComputeRunoffSeasonRelease[i][t]
        else:
            return self.PowellComputeFallSeasonRelease[i][t]

