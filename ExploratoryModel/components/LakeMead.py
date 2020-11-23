from components.Reservoir import Reservoir
import components.ReleaseFunction as RelFun

class LakeMead(Reservoir):

    # PearceFerryRapid signpost look up table
    Mead_Storage = None # storage for Mead
    inflow_demand = None # inflow - demand
    FerryFlag = False # if Pearce Ferry Rapid will be reached

    MeadDeduction = 0 # Mead monthly cutback

    ### Mead Flood Control, acre-feet
    MinSpace = 0

    # UBDristribution from JAN to DEC
    UBDist = None

    Qavg = None

    # in cfs!!! first to sixth level.
    Levels = None

    # space from Jan to Dec, in acre-feet
    Space = None

    # in acre-feet, Powell, Navajo, BlueMesa, FlamingGorge
    CredSpace = None

    UBCreditableStorageReservoirs = None

    # UBRuleCurveData
    BaseRuleCurves = None

    # MeadBank = None
    # MeadBankInitialBalance = 0

    ### Surplus Release
    SurplusRelease = None

    # USED by CRSS policy
    SNWPDiversionTotalDepletionRequested = None
    ForecastEOWYSMead = None
    ForecastMeadRelease = None

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)
        self.MinSpace = self.para.MinSpace
        self.UBDist = self.para.UBDist
        self.Qavg = self.para.Qavg
        self.Levels = self.para.Levels
        self.Space = self.para.Space
        self.CredSpace = self.para.CredSpace
        self.UBCreditableStorageReservoirs = self.para.UBCreditableStorageReservoirs
        self.BaseRuleCurves = self.para.BaseRuleCurves
        # self.MeadBankInitialBalance = self.para.MeadBankInitialBalance

    def simulationSinglePeriod(self, k, i, t):
       # 1. determine initial values for reservoir storage
        startStorage = 0
        if t == 0:
            startStorage = self.initStorage
        else:
            startStorage = self.storage[i][t - 1]

        # 2. determine inflow for current month
        inflowthismonth = 0
        inflowthismonth = self.crssInflow[i][t] - self.upReservoir.crssOutflow[i][t] + self.upReservoir.outflow[i][t]
        self.totalinflow[i][t] = inflowthismonth

        # 2. validation use, use CRSS inflow to Lake Mead, will be delete after validation
        inflowthismonth = self.crssInflow[i][t]
        self.totalinflow[i][t] = inflowthismonth

        # 3. determine release this month
        # determine which month are we in
        month = self.para.determineMonth(t)
        self.release[i][t] = 0

        # determine cutbacks for drought conditions
        if month == self.JAN:
            self.MeadDeduction = RelFun.cutbackFromDCP(self.volume_to_elevation(startStorage)) / 12

        # depletion - cutbacks
        # self.release[i][t] = self.Depletion[k][t]
        # self.release[i][t] = self.Depletion[k][t] - self.MeadDeduction
        self.release[i][t] = self.relatedUser.Depletion[k][t] - self.MeadDeduction - self.relatedUser.CRSSbankPutTake[i][t]

        # Use CRSS demand below Mead
        self.release[i][t] = self.crssDemandBelowMead[i][t]
        # self.release[i][j] = self.crssDemandBelowMead[i][j] - self.MeadDeduction
        # self.release[i][j] = self.relatedUser.Depletion[k][j] - self.MeadDeduction + self.crssMohaveHavasu[i][j]

        # outflow > minimum outflow requirement
        self.release[i][t] = max(self.release[i][t], RelFun.MinReleaseFun(self, t))

        self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, t)

        # surpluse release, todo
        # if self.storage[i][j] >= self.maxStorage:
            # self.release[i][j] = self.relatedUser.Depletion[k][j] - self.MeadDeduction + self.SurplusRelease[j]
            # self.release[i][j] = self.crssDemandBelowMead[i][j] - self.MeadDeduction + self.SurplusRelease[j]
            # self.release[i][j] = self.crssDemandBelowMead[i][j] + self.SurplusRelease[j]

       # CRSS release for validation, use CRSS release data, will be delete after validation
        # self.release[i][j] = self.crssOutflow[i][j]

        # self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, j)

       # 4. calculate shortage for current period
        # determine cutbacks
        self.downShortage[i][t] = self.relatedUser.Depletion[k][t] - self.release[i][t]
        if self.downShortage[i][t] < 0:
            self.downShortage[i][t] = 0

    def sovleStorageGivenOutflow(self, startStorage, inflowthismonth, month, i, t):
        # set initial values for area, evaporation and precipitation
        self.spill[i][t] = 0
        self.area[i][t] = self.volume_to_area(startStorage)
        self.evaporation[i][t] = self.area[i][t] * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
        self.precipitation[i][t] = self.area[i][t] * self.precipRates[month]
        self.storage[i][t] = startStorage + inflowthismonth + self.precipitation[i][t] - self.evaporation[i][t] - self.release[i][t]

        # iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        while index < self.iteration:
            self.area[i][t] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][t])) / 2.0
            self.evaporation[i][t] = self.area[i][t] * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            self.precipitation[i][t] = self.area[i][t] * self.precipRates[month]
            # if storage increases, water flow from reservoir to bank
            self.changeBankStorage[i][t] = self.bankRates * (self.storage[i][t] - startStorage)
            self.storage[i][t] = startStorage + inflowthismonth + self.precipitation[i][t] - self.changeBankStorage[i][t] - self.evaporation[i][t] - self.release[i][t]
            index = index + 1

        if self.storage[i][t] > self.maxStorage:
            self.area[i][t] = (self.volume_to_area(startStorage) + self.volume_to_area(self.maxStorage)) / 2.0
            self.evaporation[i][t] = self.area[i][t] * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            self.precipitation[i][t] = self.area[i][t] * self.precipRates[month]
            self.changeBankStorage[i][t] = self.bankRates * (self.maxStorage - startStorage)
            self.storage[i][t] = self.maxStorage
            self.spill[i][t] = -self.storage[i][t] + startStorage + inflowthismonth + self.precipitation[i][t] \
                               - self.changeBankStorage[i][t] - self.evaporation[i][t] - self.release[i][t]
        elif self.storage[i][t] < self.minStorage:
            self.storage[i][t] = self.minStorage
            self.area[i][t] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][t])) / 2.0
            self.evaporation[i][t] = self.area[i][t] * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            self.precipitation[i][t] = self.area[i][t] * self.precipRates[month]
            self.changeBankStorage[i][t] = self.bankRates * (self.storage[i][t] - startStorage)
            self.release[i][t] = startStorage - self.storage[i][t] + inflowthismonth + self.precipitation[i][t] - self.changeBankStorage[i][t] - self.evaporation[i][t]

        self.outflow[i][t] = self.release[i][t] + self.spill[i][t]
        self.elevation[i][t] = self.volume_to_elevation(self.storage[i][t])

    def releasePolicy(self, startStorage, k, i, t):
        month = self.para.determineMonth(t)
        self.release[i][t] = 0

        # determine cutbacks for drought conditions
        if month == self.JAN:
            self.MeadDeduction = RelFun.cutbackFromDCP(self.volume_to_elevation(startStorage)) / 12

        self.release[i][t] = self.relatedUser.Depletion[k][t] - self.MeadDeduction - self.relatedUser.CRSSbankPutTake[i][t]

