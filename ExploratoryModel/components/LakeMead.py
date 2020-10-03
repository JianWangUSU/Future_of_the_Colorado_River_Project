from components.Reservoir import Reservoir
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np

class LakeMead(Reservoir):

    # PearceFerryRapid signpost look up table
    Mead_Storage = None # storage for Mead
    inflow_demand = None # inflow - demand
    FerryFlag = False # if Pearce Ferry Rapid will be reached

    # Only for Mead, different policies will change this value, monthly deduction
    MeadMDeductionCurrent = 0 # current water year
    MeadMDeductionNext = 0 # next water year

    ### Mead Flood Control, acre-feet
    MinSpace = 1500000

    # UBDristribution from JAN to DEC
    UBDist = {0, 0, 0.01, 0.06, 0.23, 0.3, 0.22, 0.13, 0.04, 0.01, 0, 0}

    Qavg = {332000.000000181, 370999.999999894, 630999.999999606, 1250999.99999842, 3162000.00000384, 4135000.00000081
        ,2162000.00000183, 1061000.00000169, 652000.000000013, 573000.000000219, 452999.999999978, 363000.000000203}

    # in cfs!!! first to sixth level.
    Levels = {0, 19000, 28000, 35000, 40000, 73000.0000001413}

    # space from Jan to Dec, in acre-feet
    Space = {0, 0,0,0,0,0,0,2269999.99999767,3039999.99999638,3810000.0000032,4580000.00000191,5350000.00000062}

    # in acre-feet, Powell, Navajo, BlueMesa, FlamingGorge
    CredSpace = {3850000.00000166, 1035900, 748499.999999741,1507199.99999868}

    UBCreditableStorageReservoirs = {"Powell", "Navajo", "BlueMesa", "FlamingGorge"}

    # UBRuleCurveData
    BaseRuleCurves = {26120000, 26120000, 26120000, 26120000, 26120000, 26120000, 26120000,	26120000
        , 26120000, 26120000, 26120000, 26120000}

    ### Surplus Release
    SurplusRelease = None

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)


    def simulationSinglePeriod(self, k, i, j):
       # 1. determine initial values for reservoir storage
        startStorage = 0
        if j == 0:
            startStorage = self.initStorage
        else:
            startStorage = self.storage[i][j-1]

        # 2. determine inflow for current month
        # inflowthismonth = 0
        # inflowthismonth = self.inflow[i][j] + self.upReservoir.outflow[i][j] + self.upReservoir.spill[i][j]

        inflowthismonth = self.crssInflow[i][j] - self.upReservoir.crssOutflow[i][j] + self.upReservoir.outflow[i][j]
        self.totalinflow[i][j] = inflowthismonth

        # validation use, use CRSS release data
        inflowthismonth = self.crssInflow[i][j]
        self.totalinflow[i][j] = inflowthismonth

        # 4. determine release this month
        # determine which month are we in
        month = self.determineMonth(j)
        self.release[i][j] = 0
        # depletion - cutbacks

        if month == self.JAN:
            self.MeadMDeductionNext = self.cutbackFromDCP(self.volume_to_elevation(startStorage)) / 12

        # self.release[i][j] = self.downDepletion[k][j] - self.MeadMDeductionCurrent
        # Use CRSS demand below Mead
        self.release[i][j] = self.crssDemandBelowMead[i][j] - self.MeadMDeductionCurrent
        # outflow > minimum outflow requirement
        self.release[i][j] = max(self.release[i][j], self.MinReleaseFun(j))

        self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, j)

        # surpluse release, todo
        if self.storage[i][j] >= self.maxStorage:
            # self.release[i][j] = self.downDepletion[k][j] - self.MeadMDeductionCurrent + self.SurplusRelease[j]
            self.release[i][j] = self.crssDemandBelowMead[i][j] - self.MeadMDeductionCurrent + self.SurplusRelease[j]

       # CRSS release for validation, use CRSS release data
        # self.release[i][j] = self.crssOutflow[i][j]

        self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, j)


       # 7. calculate shortage for current period
        # determine cutbacks
        self.downShortage[i][j] = self.downDepletion[k][j] - self.release[i][j]
        if self.downShortage[i][j] < 0:
            self.downShortage[i][j] = 0

    def sovleStorageGivenOutflow(self, startStorage, inflowthismonth, month, i, j):
        # set initial values for area, evaporation and precipitation
        self.spill[i][j] = 0
        self.area[i][j] = self.volume_to_area(startStorage)
        self.evaporation[i][j] = self.area[i][j] * self.evapRates[month] * self.calcualtefractionOfEvaporation(j)
        self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
        self.storage[i][j] = startStorage + inflowthismonth + self.precipitation[i][j] - self.evaporation[i][j] - self.release[i][j]

        # 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        while index < self.iteration:
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            self.evaporation[i][j] = self.area[i][j] * self.evapRates[month] * self.calcualtefractionOfEvaporation(j)
            self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
            # if storage increases, water flow from reservoir to bank
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.storage[i][j] = startStorage + inflowthismonth + self.precipitation[i][j] - self.changeBankStorage[i][j] - self.evaporation[i][j] - self.release[i][j]
            index = index + 1

        if self.storage[i][j] > self.maxStorage:
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.maxStorage)) / 2.0
            self.evaporation[i][j] = self.area[i][j] * self.evapRates[month] * self.calcualtefractionOfEvaporation(j)
            self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
            self.changeBankStorage[i][j] = self.bankRates * (self.maxStorage - startStorage)
            self.storage[i][j] = self.maxStorage
            self.spill[i][j] = -self.storage[i][j] + startStorage + inflowthismonth + self.precipitation[i][j] \
                               - self.changeBankStorage[i][j] - self.evaporation[i][j] - self.release[i][j]
        elif self.storage[i][j] < self.minStorage:
            self.storage[i][j] = self.minStorage
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            self.evaporation[i][j] = self.area[i][j] * self.evapRates[month] * self.calcualtefractionOfEvaporation(j)
            self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.release[i][j] = startStorage - self.storage[i][j] + inflowthismonth + self.precipitation[i][j] - self.changeBankStorage[i][j] - self.evaporation[i][j]

        self.outflow[i][j] = self.release[i][j] + self.spill[i][j]
        self.elevation[i][j] = self.volume_to_elevation(self.storage[i][j])

    # cutback from 2007 Guidelines (combined volume) for Lake Mead, acre-feet
    def cutbackfromGuidelines(self, elevation):
        if elevation > 1075:
            return 0
        elif elevation >= 1050:
            return 333000
        elif elevation >= 1025:
            return 417000
        else:
            return 500000

    # Drought contingency plan (combined volume) for Lake Mead, acre-feet
    def cutbackFromDCP(self, elevation):
        if elevation > 1090:
            return 0
        elif elevation > 1075:
            return 200000+41000
        elif elevation >= 1050:
            return 533000+30000
        elif elevation > 1045:
            return 617000+34000
        elif elevation > 1040:
            return 867000+76000
        elif elevation > 1035:
            return 917000+84000
        elif elevation > 1030:
            return 967000+92000
        elif elevation >= 1025:
            return 1017000+101000
        else:
            return 1100000+150000


    # flood control policy
    def MeadFloodControl(self,i, j):
        month = self.determineMonth(j)
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
        month = self.determineMonth(period)
        if month == self.JUL:
            pass
        else:
            pass
        pass

    def MeadMinReleaseWithoutFloodControl(self, i, j):
        return self.MeadInflowForecast() + self.Qsum[j] - self.AvailableSpace(i, j) - self.upReservoir.AvailableSpace(i, j) \
               + self.MinSpace - self.DeltaBankStorage() - self.FloodControlEvap(i, j) \
               - self.upReservoir.FloodControlEvap(i, j) - self.SouthernNevConsumed()

    def MeadInflowForecast(self):
        pass

    def DeltaBankStorage(self):
        pass

    def FloodControlEvap(self, i, j):
        return self.volume_to_area(self.LiveCapacity - self.AvailableSpace(i,j)/2.0) * self.SumEvapCoeff()

    def SouthernNevConsumed(self):
        pass

    def FloodControlLevelVolume(self):
        pass

    # sum evaporation rates from current month to Jul
    def SumEvapCoeff(self, j):
        month  = self.determineMonth(j)
        sum(self.evapRates[month: self.JUL])


    def DeltaBankStorage(self, i, j):
        return self.bankRates * (self.AvailableSpace(i,j) - self.MinSpace) \
        + self.upReservoir.bankRates * self.upReservoir.AvailableSpace(i,j)