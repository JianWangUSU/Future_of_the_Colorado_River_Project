from components.Reservoir import Reservoir

class LakeMead(Reservoir):

    # PearceFerryRapid signpost look up table
    Mead_Storage = None # storage for Mead
    inflow_demand = None # inflow - demand
    FerryFlag = False # if Pearce Ferry Rapid will be reached

    # Only for Mead, different policies will change this value, monthly deduction
    MeadMDeductionCurrent = 0 # current water year
    MeadMDeductionNext = 0 # next water year

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
        inflowthismonth = 0
        inflowthismonth = self.inflow[i][j] + self.upReservoir.outflow[i][j] + self.upReservoir.spill[i][j]
            # validation use, use CRSS release data
            # inflowthismonth = self.inflow[i][j]
        self.totalinflow[i][j] = inflowthismonth

        # 3. determine release pattern, triggered in Apr and Aug


        # 4. determine release this month
        # determine which month are we in
        month = self.determineMonth(j)
        self.outflow[i][j] = 0
        # depletion - cutbacks
        self.outflow[i][j] = self.downDepletion[k][j] - self.MeadMDeductionCurrent
        # outflow > minimum outflow requirement
        self.outflow[i][j] = max(self.outflow[i][j], self.minOutflow)

        # strategy: CRSS release for validation, use CRSS release data
        # self.outflow[i][j] = self.crssRelease[j]

        # 5. set initial data
        # set initial values for area, evaporation and precipitation
        self.area[i][j] = self.volume_to_area(startStorage)
        self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
        self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
        self.storage[i][j] = startStorage + inflowthismonth + self.precipitation[i][j] - self.evaporation[i][j] - self.outflow[i][j]

        # 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
        index = 0
        while index < self.iteration:
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
            self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
            # if storage increases, water flow from reservoir to bank
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.storage[i][j] = startStorage + inflowthismonth + self.precipitation[i][j] - self.changeBankStorage[i][j] - self.evaporation[i][j] - self.outflow[i][j]
            index = index + 1

        if self.storage[i][j] > self.maxStorage:
            self.spill[i][j] = self.storage[i][j] - self.maxStorage
            self.storage[i][j] = self.maxStorage
        elif self.storage[i][j] < self.minStorage:
            self.storage[i][j] = self.minStorage
            self.area[i][j] = (self.volume_to_area(startStorage) + self.volume_to_area(self.storage[i][j])) / 2.0
            self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
            self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
            self.changeBankStorage[i][j] = self.bankRates * (self.storage[i][j] - startStorage)
            self.outflow[i][j] = startStorage - self.storage[i][j] + inflowthismonth + self.precipitation[i][j] - self.changeBankStorage[i][j] - self.evaporation[i][j]

        self.elevation[i][j] = self.volume_to_elevation(self.storage[i][j])

        # 7. calculate shortage for current period
        # determine cutbacks
        self.downShortage[i][j] = self.downDepletion[k][j] - self.outflow[i][j]
        if self.downShortage[i][j] < 0:
            self.downShortage[i][j] = 0

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