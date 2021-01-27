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
       # 1. get initial values for reservoir storage
        startStorage = self.getinitStorageForEachPeriod(i,t)

        # 2. determine inflow for current month
        inflowthismonth = self.interveningInflow(k, i, t) + self.upReservoir.outflow[i][t]
        self.totalinflow[i][t] = inflowthismonth

        # 2. validate Mead only, use CRSS inflow to Lake Mead, will be delete after validation
        # inflowthismonth = self.crssInflow[i][t]
        # self.totalinflow[i][t] = inflowthismonth

        # 3. determine release this month
        month = self.para.determineMonth(t)
        self.release[i][t] = self.releasePolicy(startStorage, k, i, t)

        # self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, t)

        self.storage[i][t], self.outflow[i][t], self.area[i][t], self.evaporation[i][t] \
            , self.changeBankStorage[i][t], self.elevation[i][t], self.release[i][t], self.spill[i][t] \
            = self.sovleStorageGivenOutflowGeneral(startStorage, inflowthismonth, self.release[i][t], month, t)

        # surpluse release
        # if self.storage[i][j] >= self.maxStorage:
            # self.release[i][j] = self.relatedUser.Depletion[k][j] - self.MeadDeduction + self.SurplusRelease[j]
            # self.release[i][j] = self.crssDemandBelowMead[i][j] - self.MeadDeduction + self.SurplusRelease[j]
            # self.release[i][j] = self.crssDemandBelowMead[i][j] + self.SurplusRelease[j]

       # CRSS release for validation, use CRSS release data, will be delete after validation
        # self.release[i][j] = self.crssOutflow[i][j]
        # self.sovleStorageGivenOutflow(startStorage, inflowthismonth, month, i, j)

       # 4. calculate shortage for current period
        self.LBMShortage[i][t] = self.relatedUser.DepletionNormal[k][t] \
                                 - self.outflow[i][t] - self.relatedUser.GainLoss/12
        if self.LBMShortage[i][t] < 0:
            self.LBMShortage[i][t] = 0

    def getinitStorageForEachPeriod(self, i, t):
        if t == 0:
            return self.initStorage
        else:
            return self.storage[i][t - 1]

    def interveningInflow(self, k, i, t):
        # In validation, intervening inflow to Mead are equal to MEAD inflow (CRSS results) - Powell outflow (CRSS results).
        if self.plc.CRSS_Mead == True:
            return self.crssInflow[i][t] - self.upReservoir.crssOutflow[i][t]
        elif self.plc.ADP_DemandtoInflow == True:
            return self.crssInflow[i][t] - self.upReservoir.crssOutflow[i][t]
        else:
            # todo, use CRSS results for the time being
            return self.crssInflow[i][t] - self.upReservoir.crssOutflow[i][t]

    def getOneYearInterveningInflow(self, k, i, t):
        # In validation, intervening inflow to Mead are equal to MEAD inflow (CRSS results) - Powell outflow (CRSS results).
        if self.plc.CRSS_Mead == True:
            return sum(self.crssInflow[i][t:t+12]) \
                   - sum(self.upReservoir.crssOutflow[i][t:t+12])
        elif self.plc.ADP_DemandtoInflow == True:
            return sum(self.crssInflow[i][t:t+12]) \
                   - sum(self.upReservoir.crssOutflow[i][t:t+12])
        else:
            # todo, use CRSS results for the time being
            return sum(self.crssInflow[i][t:t+12]) \
                   - sum(self.upReservoir.crssOutflow[i][t:t+12])

    def getOneYearRlease(self, k, i, t):
        if self.plc.ADP_DemandtoInflow == True:
            startStorage = self.getinitStorageForEachPeriod(i,t)
            results = 0
            for tt in range(12):
                results = results + self.releasePolicy(startStorage, k, i, t)

            return results

    # Lake Mead release policy,
    #   self: Lake Mead itself,
    #   startStorage: start of month storage,
    #   k: depletionTrace,
    #   i: inflowTrace,
    #   t: period
    def releasePolicy(self, startStorage, k, i, t):
        if self.plc.LB_demand == True:
            return self.relatedUser.DepletionNormal[k][t]

        if self.plc.DCP == True:
            month = self.para.determineMonth(t)
            # determine cutbacks for drought conditions
            if month == self.JAN:
                self.MeadDeduction = RelFun.cutbackFromDCP(self.volume_to_elevation(startStorage)) / 12

            return self.relatedUser.DepletionNormal[k][t] - self.MeadDeduction
            # self.release[i][t] = self.relatedUser.DepletionNormal[k][t] - self.MeadDeduction - self.relatedUser.CRSSbankPutTake[i][t]

        if self.plc.CRSS_Mead == True:
            # Use CRSS demand below Mead
            self.release[i][t] = self.crssDemandBelowMead[i][t]
            # outflow > minimum outflow requirement
            self.release[i][t] = max(self.release[i][t], RelFun.MinReleaseFun(self, t))

            return self.release[i][t]

        # adapt release to inflow
        if self.plc.ADP_DemandtoInflow == True:
            if startStorage < self.plc.ADP_triggerS:
                # release = normal demand - gains (inflow below - Mohave and Havasu loss) - LB AND MEXICO contribution
                return self.relatedUser.DepletionNormal[k][t] - self.relatedUser.GainLoss/12 - self.relatedUser.Contribution/12
            else:
                return self.relatedUser.DepletionNormal[k][t] - self.relatedUser.GainLoss / 12

    def simulationSinglePeriodGeneral(self, startStorage, inflowthismonth, release, t):
        # determine which month are we in
        month = self.para.determineMonth(t)

        # outflow > minimum outflow requirement
        release = max(release, RelFun.MinReleaseFun(self, t))

        return self.sovleStorageGivenOutflowGeneral(startStorage, inflowthismonth, release, month, t)

    def sovleStorageGivenOutflowGeneral(self, startStorage, inflowthismonth, release, month, t):
        # set initial values for area, evaporation and precipitation
        spill = 0
        area = self.volume_to_area(startStorage)
        evaporation = area * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
        precipitation = area * self.precipRates[month]
        storage = startStorage + inflowthismonth + precipitation - evaporation - release
        changeBankStorage = 0

        # iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        # plot iteration vs storage. 1/5/10,000 acre-feet. Add an error to stop iteration. (decrease computational time)
        error = self.maxError + 1
        while index < self.iteration and error > self.maxError:
            # if t == 0 or t == 100:
            #     print(str(index) + " " + str(storage))
            preStorage = storage
            area = (self.volume_to_area(startStorage) + self.volume_to_area(storage)) / 2.0
            evaporation = area * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            precipitation = area * self.precipRates[month]
            # if storage increases, water flow from reservoir to bank
            changeBankStorage = self.bankRates * (storage - startStorage)
            storage = startStorage + inflowthismonth + precipitation - changeBankStorage - evaporation - release
            index = index + 1
            error = abs(preStorage - storage)

        if storage > self.maxStorage:
            area = (self.volume_to_area(startStorage) + self.volume_to_area(self.maxStorage)) / 2.0
            evaporation = area * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            precipitation = area * self.precipRates[month]
            changeBankStorage = self.bankRates * (self.maxStorage - startStorage)
            storage = self.maxStorage
            spill = -storage + startStorage + inflowthismonth + precipitation \
                               - changeBankStorage - evaporation - release
        elif storage < self.minStorage:
            storage = self.minStorage
            area = (self.volume_to_area(startStorage) + self.volume_to_area(storage)) / 2.0
            evaporation = area * self.evapRates[month] * RelFun.calcualtefractionOfEvaporation(t)
            precipitation = area * self.precipRates[month]
            changeBankStorage = self.bankRates * (self.minStorage - startStorage)
            release = startStorage - storage + inflowthismonth + precipitation - changeBankStorage - evaporation

        outflow = release + spill
        elevation = self.volume_to_elevation(storage)

        # return storage
        return storage, outflow, area, evaporation, changeBankStorage, elevation, release, spill

    # abandoned
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
