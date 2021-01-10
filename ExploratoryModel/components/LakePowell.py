from components.Reservoir import Reservoir
import numpy as np
import components.ReleaseFunction as RelFun


class LakePowell(Reservoir):

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

    # Only for Powell, monthly release table
    PowellmonthlyRelease = None
    # column of the monthly release table, current water year
    column = 2

    # used in CRSS, not exactly the same
    targetSpace = 0

    lastPowellStorage = None

    # Combined Upper Basin Storage, used by drought response operation
    ubStorage = None
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

    # READ FROM CRSS
    ShiftedEQLine = None

    # USED by CRSS policy
    ForecastEOWYSPowell = None
    ForecastPowellRelease = None
    ForecastPowellInflow = None

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)
        self.lastPowellStorage = self.para.lastPowellStorage
        self.initUBstorage = self.para.initUBstorage
        self.maxUBstorage = self.para.maxUBstorage
        self.targetUBstorage = self.para.targetUBstorage

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
        # inflowthismonth = self.inflow[i][j] - (self.relatedUser.Depletion[k][j] + self.crssUBshortage[i][j])
        inflowthismonth = self.inflow[i][t] - self.relatedUser.Depletion[k][t]
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

        # self.upShortage[i][t] = self.relatedUser.Depletion[k][t] - (self.inflow[i][t] - inflowthismonth)
        # if self.upShortage[i][t] < 0:
        #     self.upShortage[i][t] = 0

        # validation use, use CRSS INFLOW data
        inflowthismonth = self.crssInflow[i][t]
        self.totalinflow[i][t] = inflowthismonth

        ### 3. determine policy. equalization rule is only triggered in Apr and Aug
        self.release[i][t] = self.releasePolicy(startStorage, k, i, t)

        # outflow meet boundary conditions
        # self.release[i][j] = max(self.release[i][j], self.MinReleaseFun(j))

        month = self.para.determineMonth(t)
        self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, t)

        ### calculate UB shortage for the current time period
        self.upShortage[i][t] = self.relatedUser.Depletion[k][t] - (self.inflow[i][t] - inflowthismonth)
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

    def simulationSinglePeriodGeneral(self, startStorage, inflowthismonth, release, t):
        month = self.para.determineMonth(t)
        return self.sovleStorageGivenOutflowGeneral(startStorage, inflowthismonth, release, month, t)

    # solve water balance equation given outflow
    def sovleStorageGivenOutflowGeneral(self, startStorage, inflowthismonth, release, month, t):
        ### 5. set initial data for water balance calculation
        # set initial area, evaporation values
        area = self.volume_to_area(startStorage)
        evaporation = area * self.evapRates[month]
        storage = startStorage + inflowthismonth - evaporation - release

        ### 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        error = 100
        while index < self.iteration and error > self.maxError:
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

        return storage, outflow

    # release policy, self: Lake Powell itself, startStorage: begining storage, k: depletionTrace, i: inflowTrace, t: period
    def releasePolicy(self, startStorage, k, i, t):
         # strategy FPF
        if self.plc.FPF == True:
            return RelFun.FPF(self, startStorage, t)
        # strategy re-drill Lake Powell (FMF)
        if self.plc.FMF == True:
            return RelFun.redrillPowell(startStorage)
        # Major CRSS Lake Powell policies
        if self.plc.CRSS_Powell == True:
            return self.crssPolicy(i,t)

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

    # Periodic Net Evaporation
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

    def elevation_to_riverArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableRiverArea)

    def elevation_to_streamsideArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableStreamsideArea)

    def elevation_to_terranceArea(self,ele):
        #INPUT acre-feet, RETURN feet
        return np.interp(ele, self.PNETableElevation, self.PNETableTerranceArea)


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
            self.upShortage[i][t] = self.relatedUser.Depletion[k][t] - (self.inflow[i][t] - inflowthismonth)
            if self.upShortage[i][t] < 0:
                self.upShortage[i][t] = 0

            return