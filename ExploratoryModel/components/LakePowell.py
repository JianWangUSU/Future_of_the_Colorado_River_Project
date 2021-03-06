from components.Reservoir import Reservoir
import numpy as np
import components.ReleaseFunction as RelFun


class LakePowell(Reservoir):
    # Only for Powell, monthly release table
    PowellmonthlyRelease = None

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

    # all columes
    allColumns = [COL700, COL748, COL823, COL900, COL950, COL1050, COL1100, COL1200, COL1300, COL1400]

    # column of the monthly release table, current water year
    column = 2

    # Combined Upper Basin Storage, used by drought response operation
    UBStorage = None
    initUBstorage = None
    maxUBstorage = None
    targetUBstorage = None

    # UB release next month
    UBmonthRelease = 0
    # UB refill next month
    UBmonthRefill = 0
    minUBstorage = 0

    # only for Lake Powell, true means redrill
    redrillflag = False
    # UB release
    UBreleaseFlag = False

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

    # Equalization data used in CRSS policies
    EQTrumpUpperLevelBalancingFlag = None
    EqualizationTolerance = 10000

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)
        self.lastPowellStorage = self.para.lastPowellStorage
        self.initUBstorage = self.para.initUBstorage
        self.maxUBstorage = self.para.maxUBstorage
        self.targetUBstorage = self.para.targetUBstorage

    # create array variables
    def setupPeriodsandTraces(self):
        super().setupPeriodsandTraces()
        self.UBStorage = np.zeros([self.inflowTraces, self.periods])
        self.grossEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.riverEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.streamsideEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.terraceEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.remainingEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.salvageEvaporation = np.zeros([self.inflowTraces, self.periods])
        self.EQTrumpUpperLevelBalancingFlag = np.zeros([self.inflowTraces, self.periods])

    # calculate inflow to Lake Powell, this value changed based on UB contribution
    def inflowToPowell(self, k, i, t):

        # if choosing CRSS policy, then use CRSS inflow to Lake Powell
        if self.plc.CRSS_Powell == True:
            self.UBShortage[i][t] = -self.crssUBshortage[i][t]
            # CRSS INFLOW data for validation purpose
            return self.crssInflow[i][t]

        elif self.plc.ADP_DemandtoInflow == True:
            # Step 1: know the inflow to the system
            #        total inflow = inflow to Powell and intervening inflow to Mead
            #        total demand = UB + LB (including Mohave/Havasu and inflow below Mead) + Mexico normal demand
            # Step 2: adapt depletion to inflow: change inflow to Powell and change release from Mead !
            #        total depletion = average total inflow for the past 5 or ? years
            #        calculate gap (demand - depletion) and divide it for UB and LB.
            #        calculate inflow to Powell and calculate release from Mead
            # Step 3: calculate shortages based on the change of inflow and release
            #        LB+MEXICO: demand - outflow from Mead
            #        UB: incremental of inflow + base shortages from CRSS

            month = self.para.determineMonth(t)
            year = self.para.getCurrentYear(t)
            # start adapt demand to inflow since JAN, 2026, triggered once a year
            # 2021 - 0, 2022 - 1, 2023 - 2, 2024 - 3, 2025 - 4, 2026 - 5
            pastYears = 5
            if month == self.para.JAN and year >= pastYears:
                # reset UB LB MEXICO contributions
                self.relatedUser.Contribution = 0
                self.downReservoir.relatedUser.Contribution = 0

                # Step 1:
                # Calculate 5 past year total inflow to the system: inflow to Powell + intervening inflow to Mead
                # sum works in this way [ , ) instead of [ , ]
                totalInflow5Y = sum(self.crssInflow[i][t-pastYears*12:t]) \
                                      + sum(self.downReservoir.crssInflow[i][t-pastYears*12:t])\
                                      - sum(self.crssOutflow[i][t-pastYears*12:t])
                # totalDemand5Y = sum(self.relatedUser.DepletionNormal[k][t-5*12:t]) \
                #                       + sum(self.downReservoir.relatedUser.DepletionNormal[k][t-5*12:t]) \
                #                       - self.downReservoir.relatedUser.GainLoss * 5
                # Step 2:
                # adapt total release this year to total inflow in the past 5 years
                totalReleaseThisYear = totalInflow5Y/pastYears

                # calculate total demand this year
                UBdemandThisYear = sum(self.relatedUser.DepletionNormal[k][t:t + 12])
                # LBM needs to consider Mohave, Havasu and inflow below
                LBMdemandThisYear = sum(self.downReservoir.relatedUser.DepletionNormal[k][t:t + 12]) \
                                    - self.downReservoir.relatedUser.GainLoss
                totalDemandThisYear = UBdemandThisYear + LBMdemandThisYear

                if totalReleaseThisYear >= totalDemandThisYear:
                    # PowellInflow = self.crssInflow[i][t]
                    # MeadRelease = LBMdemandThisYear

                    # next year contribution = 0
                    self.relatedUser.Contribution = 0
                    self.downReservoir.relatedUser.Contribution = 0

                    # change from negtive to positive
                    self.UBShortage[i][t] = -self.crssUBshortage[i][t]
                    return self.crssInflow[i][t]
                else:
                    # release = totalReleaseThisYear
                    gap = totalDemandThisYear - totalReleaseThisYear
                    # UB contribution
                    self.relatedUser.Contribution = UBdemandThisYear/ totalDemandThisYear * gap
                    # LB and Mexico contribution
                    self.downReservoir.relatedUser.Contribution = LBMdemandThisYear/ totalDemandThisYear * gap

                    if self.getinitStorageForEachPeriod(i,t) < self.plc.ADP_triggerS:
                        self.UBShortage[i][t] = self.relatedUser.Contribution / 12 - self.crssUBshortage[i][t]
                        return self.crssInflow[i][t] + self.relatedUser.Contribution / 12
                    else:
                        self.UBShortage[i][t] = - self.crssUBshortage[i][t]
                        return self.crssInflow[i][t]
            else:
                # self.UBShortage[i][t] = self.relatedUser.Contribution/12 - self.crssUBshortage[i][t]
                # return self.crssInflow[i][t] + self.relatedUser.Contribution/12

                if self.getinitStorageForEachPeriod(i, t) < self.plc.ADP_triggerS:
                    self.UBShortage[i][t] = self.relatedUser.Contribution / 12 - self.crssUBshortage[i][t]
                    return self.crssInflow[i][t] + self.relatedUser.Contribution / 12
                else:
                    self.UBShortage[i][t] = - self.crssUBshortage[i][t]
                    return self.crssInflow[i][t]

        else:
            # todo
            # ubStorage is the aggregated storage above Lake Powell
            # inflowthismonth = self.inflow[i][j] - (self.relatedUser.DepletionNormal[k][j] + self.crssUBshortage[i][j])

            inflowthismonth = self.inflow[i][t] - self.relatedUser.DepletionNormal[k][t]
            if inflowthismonth < 0:
                inflowthismonth = 0
            if self.UBreleaseFlag == True:
                if self.UBmonthRelease <= self.UBStorage[i][t]:
                    inflowthismonth = inflowthismonth + self.UBmonthRelease
                    self.UBStorage[i][t] = self.UBStorage[i][t] - self.UBmonthRelease
                else:
                    inflowthismonth = inflowthismonth + self.UBStorage[i][t]
                    self.UBStorage[i][t] = self.UBStorage[i][t] - self.UBStorage[i][t]
            else:
                if self.UBStorage[i][t] < self.targetUBstorage:
                    if inflowthismonth < self.UBmonthRefill:
                        inflowthismonth = 0
                        self.UBStorage[i][t] = self.UBStorage[i][t] + inflowthismonth
                        if self.UBStorage[i][t] > self.targetUBstorage:
                            inflowthismonth = inflowthismonth + self.UBStorage[i][t] - self.targetUBstorage
                            self.UBStorage[i][t] = self.targetUBstorage
                    else:
                        inflowthismonth = inflowthismonth - self.UBmonthRefill
                        self.UBStorage[i][t] = self.UBStorage[i][t] + self.UBmonthRefill
                        if self.UBStorage[i][t] > self.targetUBstorage:
                            inflowthismonth = inflowthismonth + self.UBStorage[i][t] - self.targetUBstorage
                            self.UBStorage[i][t] = self.targetUBstorage

            ### calculate UB shortage for the current time period
            self.UBShortage[i][t] = self.relatedUser.DepletionNormal[k][t] - (self.inflow[i][t] - inflowthismonth)
            if self.UBShortage[i][t] < 0:
                self.UBShortage[i][t] = 0

            return inflowthismonth

    def getOneYearInflow(self, k, i, t):
        if self.plc.ADP_DemandtoInflow == True:
            return sum(self.crssInflow[i][t:t+12]) + self.relatedUser.Contribution

    # simulate a single time period
    #   self: Lake Powell itself,
    #   k: depletionTrace,
    #   i: inflowTrace,
    #   t: period
    def simulationSinglePeriod(self, k, i, t):
        ### 1. get the start of reservoir storage in the current time period.
        startStorage = self.getinitStorageForEachPeriod(i,t)
        self.UBStorage[i][t] = self.getinitUBStorageForEachPeriod(i,t)

        ### 2. determine inflow for the current month, add shortage
        # inflowthismonth = self.crssInflow[i][t]
        inflowthismonth = self.inflowToPowell(k,i,t)
        self.totalinflow[i][t] = inflowthismonth

        ### 3. determine policy
        self.release[i][t] = self.releasePolicy(startStorage, k, i, t)

        # outflow meet boundary conditions
        # self.release[i][j] = max(self.release[i][j], self.MinReleaseFun(j))

        month = self.para.determineMonth(t)
        # self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, t)
        self.storage[i][t], self.outflow[i][t], self.area[i][t], self.evaporation[i][t]\
            , self.changeBankStorage[i][t], self.elevation[i][t], self.release[i][t], self.spill[i][t] \
            = self.sovleStorageGivenOutflowGeneral(startStorage, inflowthismonth, self.release[i][t], month, t)

    def getinitStorageForEachPeriod(self, i, t):
        if t == 0:
            return self.initStorage
        else:
            return self.storage[i][t - 1]

    def getinitUBStorageForEachPeriod(self, i, t):
        if t == 0:
            return self.initUBstorage
        else:
            return self.UBStorage[i][t - 1]

    # calcualte water balance for each period, used in decision scaling tool
    #   self: Lake Powell itself,
    #   startStorage: start month storage,
    #   inflowthismonth: inflow to Powell in the current month,
    #   release: outflow from Powell
    #   t: period
    def simulationSinglePeriodGeneral(self, startStorage, inflowthismonth, release, t):
        month = self.para.determineMonth(t)
        return self.sovleStorageGivenOutflowGeneral(startStorage, inflowthismonth, release, month, t)

    # solve water balance equation given outflow
    #   self: Lake Powell itself,
    #   startStorage: start month storage,
    #   inflowthismonth: inflow to Powell in the current month,
    #   release: outflow from Powell
    #   month: month in a year
    #   t: period
    def sovleStorageGivenOutflowGeneral(self, startStorage, inflowthismonth, release, month, t):
        ### set initial data for water balance calculation
        # set initial area, evaporation values
        area = self.volume_to_area(startStorage)
        evaporation = area * self.evapRates[month]
        storage = startStorage + inflowthismonth - evaporation - release
        changeBankStorage = 0

        ### iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        # needs to be greater than maxError in the very begining.
        error = self.maxError + 1
        while index < self.iteration and error > self.maxError:
        # while index < self.iteration:
            preStorage = storage
            area = (self.volume_to_area(startStorage) + self.volume_to_area(storage)) / 2.0
            evaporation = self.calculateEvaporationGeneral(area, startStorage, storage, t)
            # if storage increases, water flow from reservoir to bank
            changeBankStorage = self.bankRates * (storage - startStorage)
            storage = startStorage + inflowthismonth - changeBankStorage - evaporation - release
            index = index + 1
            error = abs(preStorage - storage)

        spill = 0
        if storage > self.maxStorage:
            spill = storage - self.maxStorage
            storage = self.maxStorage
        elif storage < self.minStorage:
            storage = self.minStorage
            area = (self.volume_to_area(startStorage) + self.volume_to_area(storage)) / 2.0
            # self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
            evaporation = self.calculateEvaporationGeneral(area, startStorage, storage, t)
            changeBankStorage = self.bankRates * (storage - startStorage)
            release = startStorage - storage + inflowthismonth - changeBankStorage - evaporation

        outflow = release + spill
        elevation = self.volume_to_elevation(storage)

        return storage, outflow, area, evaporation, changeBankStorage, elevation, release, spill

    # release policy for Powell
    #   self: Lake Powell itself,
    #   startStorage: start month storage,
    #   k: depletionTrace,
    #   i: inflowTrace,
    #   t: period
    def releasePolicy(self, startStorage, k, i, t):
        # Major CRSS Lake Powell policies
        if self.plc.CRSS_Powell == True:
            return self.crssPolicy(i, t)
         # strategy FPF
        if self.plc.FPF == True:
            return RelFun.FPF(self, startStorage, t)
        # strategy re-drill Lake Powell (FMF)
        if self.plc.FMF == True:
            return RelFun.FMF(self, startStorage)
        # Equalization deloped by JIAN, not policies in CRSS
        if self.plc.EQUAL == True:
            month = self.para.determineMonth(t)
            if month == self.para.JAN:
                # start of month storages
                startStorage1 = startStorage
                startStorage2 = self.downReservoir.getinitStorageForEachPeriod(i,t)

                # Lake Powell inflow
                inflow1 = self.getOneYearInflow(k, i, t)

                # Lake Mead release
                release2 = self.downReservoir.getOneYearRlease(k, i, t)

                # Lake Mead intervening inflow
                intervenningInflow2 = self.downReservoir.getOneYearInterveningInflow(k,i,t)

                # equalization, calculate Lake Powell release
                self.column = RelFun.Equalization(self, self.downReservoir,
                                           startStorage1, startStorage2, inflow1, release2, intervenningInflow2, t)

            return self.PowellmonthlyRelease[self.column][month]

        # strategy equalization + DCP
        # if self.plc.EQUAL_DCP == True:
        #     RelFun.equalizationAndDCP(k, i, t)
        # strategy adaptive policy (only consider Pearce Ferry Rapid now)
        # if self.plc.ADP == True:
        #     return RelFun.adaptivePolicy(k, i, t)

    def crssPolicy(self, i, t):
        month = self.para.determineMonth(t)

        # CRSS policy 28
        self.release[i][t] = RelFun.PowellOperationsRule(self, i, t)

        # CRSS policy 24
        self.release[i][t] = RelFun.MeetPowellMinObjectiveRelease(self, i, t)

        # strategy: CRSS release for validation, use CRSS release data
        # self.release[i][j] = self.crssOutflow[i][j]

        # CRSS policy 23
        temp = RelFun.LowerElevationBalancingTier(self, i, t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        # CRSS policy 22
        temp = RelFun.MidElevationReleaseTier(self, i, t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        # CRSS policy 21
        if month >= self.APR or month <= self.SEP:
            temp = RelFun.UpperElevationBalancingTierAprilthruSept(self, i, t)
            if temp != None and temp > 0:
                self.release[i][t] = temp

        # CRSS policy 20
        if month <= self.MAR:
            temp = RelFun.UpperElevationBalancingTierJanthruMarch(self, i, t)
            if temp != None and temp > 0:
                self.release[i][t] = temp

        # CRSS policy 19
        temp = RelFun.EqualizationTier(self, i, t)
        if temp != None and temp > 0:
            self.release[i][t] = temp

        return self.release[i][t]

    # Periodic Net Evaporation, set middle values in this functions
    def calculateEvaporation(self, area, startS, endS, i, t):
        month = self.para.determineMonth(t)
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

    # Periodic Net Evaporation, return evaporation results
    def calculateEvaporationGeneral(self, area, startS, endS, t):
        month = self.para.determineMonth(t)
        startEle = self.volume_to_elevation(startS)
        endEle = self.volume_to_elevation(endS)

        grossEvaporation = area * self.grossEvapCoef[month]

        tempRiverArea = (self.elevation_to_riverArea(startEle)+ self.elevation_to_riverArea(endEle)) / 2.0
        riverEvaporation = tempRiverArea * self.riverEvapCoef[month]

        tempStreamSideArea = (self.elevation_to_streamsideArea(startEle)+ self.elevation_to_streamsideArea(endEle)) / 2.0
        streamsideEvaporation = tempStreamSideArea * self.streamsideCoef[month] * self.averageAirTemp[month]

        tempTerranceArea = (self.elevation_to_terranceArea(startEle)+ self.elevation_to_terranceArea(endEle)) / 2.0
        terraceEvaporation = tempTerranceArea * self.terranceCoef[month] * self.averageAirTemp[month]

        tempRemainArea = area - tempRiverArea - tempStreamSideArea - tempTerranceArea
        remainingEvaporation = tempRemainArea * self.averagePrecip[month]

        salvageEvaporation = riverEvaporation + streamsideEvaporation \
                                        + terraceEvaporation + remainingEvaporation

        return grossEvaporation - salvageEvaporation

    # the following three functions are required to calculate Lake Powell evaporation
    def elevation_to_riverArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableRiverArea)

    def elevation_to_streamsideArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableStreamsideArea)

    def elevation_to_terranceArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableTerranceArea)


    # =================================================NOT USED=========================================================
    # # used in CRSS, not exactly the same
    # targetSpace = 0
    # lastPowellStorage = None
    #

    #
    # # READ FROM CRSS
    # ShiftedEQLine = None
    #
    # # USED by CRSS policy
    # ForecastEOWYSPowell = None
    # ForecastPowellRelease = None
    # ForecastPowellInflow = None

    # related to redrilling Powell, not used now. 01/25/2021
    def test(self, k, i, t, month, inflowthismonth):
        # determine which month are we in
        self.release[i][t] = 0
        # monthly release table
        print(str(i) +" " + str(t) + " " + str(self.column) + " " + str(month))
        self.release[i][t] = self.PowellmonthlyRelease[self.column][month]

        # If Pearce Ferry Rapid flag is true, decreasing Powell outflow
        if self.downReservoir.FerryFlag == True:
            if self.column >= 2:
                self.release[i][t] = self.PowellmonthlyRelease[self.column - 2][month]

        # After re-drilling Lake Powell
        if self.redrillflag == True:

            # There are 1.89 maf between dead pool and bottom pool elevation for Lake Powell
            if self.lastPowellStorage > 0:
                # outflow = inflow + 1.89/12 maf/mth
                self.release[i][t] = self.inflow[i][t] + 1.89 / 12 * 1000000
                # problem here
                self.lastPowellStorage = self.lastPowellStorage - 1.89/12
            else:
                # outflow = inflow
                self.release[i][t] = self.totalinflow[i][t]
                self.elevation[i][t] = self.minElevation

            # calculate UB shortage
            self.UBShortage[i][t] = self.relatedUser.DepletionNormal[k][t] - (self.inflow[i][t] - inflowthismonth)
            if self.UBShortage[i][t] < 0:
                self.UBShortage[i][t] = 0

            return

    # solve water balance equation given outflow, abandoned. 01/25/2021
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