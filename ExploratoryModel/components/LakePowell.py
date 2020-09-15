from components.Reservoir import Reservoir

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

    def __init__(self, name, upR):
        Reservoir.__init__(self, name, upR)

    # simulate one time period, k: depletionTrace, i: inflowTrace, j: period
    def simulationSinglePeriod(self, k, i, j):
        ### 1. determine the start of reservoir storage in the current time period.
        startStorage = 0
        if j == 0:
            startStorage = self.initStorage
        else:
            startStorage = self.storage[i][j-1]

        ### 2. determine inflow for the current month
        inflowthismonth = self.inflow[i][j] - self.upDepletion[k][j]
        if inflowthismonth < 0:
            inflowthismonth = 0
        # validation use, use CRSS release data
        # inflowthismonth = self.inflow[i][j]

        # monthly release table
        self.upShortage[i][j] = self.upDepletion[k][j] - (self.inflow[i][j] - inflowthismonth)
        if self.upShortage[i][j] < 0:
            self.upShortage[i][j] = 0

        self.totalinflow[i][j] = inflowthismonth

        ### 3. determine policy. equalization rule is only triggered in Apr and Aug
        # strategy equalization + DCP
        if self.plc.EQUAL_DCP == True:
            self.equalizationAndDCP(k, i, j)
        # strategy adaptive policy (only consider Pearce Ferry Rapid now)
        if self.plc.ADP == True:
            self.adaptivePolicy(k, i, j)
        # strategy FPF
        if self.plc.FPF == True:
            self.FPF(startStorage)
        # strategy re-drill Lake Powell (FMF)
        if self.plc.FMF == True:
            self.redrillPowell(startStorage)

        # OTHER strategies: equalization + ISG
        # MeadJan1elevation = self.equalizationAndISG(k, i, j)
        # self.MeadmonthlyDeduction = self.downReservoir.cutbackfromGuidelines(MeadJan1elevation) / 12
        # strategy 3: equalization + DCP + ICS
        # MeadJan1elevation = self.equalization(k, i, j)
        # self.downReservoir.MeadMDeductionNext = self.downReservoir.DCPICScutback(MeadJan1elevation, i) / 12
        # strategy 4: Powell Release is fun of (storage, inflow)
        # if Mead storage is less than... and inflow to Powell is less than
        # MeadJan1elevation = self.forecastJanuray1elevation(k, i, j)[1]
        # self.PowellReleaseFun(MeadJan1elevation, i, j)
        # self.downReservoir.MeadmonthlyDeduction = self.downReservoir.cutbackFromDCP(MeadJan1elevation) / 12
        # strategy 5: FMF
        # MeadJan1elevation = self.forecastFutureElevations(k, i, j)[1]
        # self.FMF(MeadJan1elevation)
        # self.downReservoir.MeadmonthlyDeduction = self.downReservoir.cutbackFromDCP(MeadJan1elevation) / 12

        ### 4. determine release in this month
        # determine which month are we in
        month = self.determineMonth(j)
        self.outflow[i][j] = 0
        # monthly release table
        # print(str(i)+" "+str(j) +" "+str(self.column) +" "+str(month))
        self.outflow[i][j] = self.PowellmonthlyRelease[self.column][month]

        # If Pearce Ferry Rapid flag is true, decreasing Powell outflow
        if self.downReservoir.FerryFlag == True:
            if self.column >= 2:
                self.outflow[i][j] = self.PowellmonthlyRelease[self.column-2][month]

        # After re-drilling Lake Powell
        if self.redrillflag == True:

            # There are 1.89 maf between dead pool and bottom pool elevation for Lake Powell
            if self.lastPowellStorage > 0:
                # outflow = inflow + 1.89/12 maf/mth
                self.outflow[i][j] = self.inflow[i][j] + 1.89/12*1000000
                self.lastPowellStorage = self.lastPowellStorage - 1.89/12
            else:
                # outflow = inflow
                self.outflow[i][j] = self.totalinflow[i][j]
                self.elevation[i][j] = self.minElevation

            # calculate UB shortage
            self.upShortage[i][j] = self.upDepletion[k][j] - (self.inflow[i][j] - inflowthismonth)
            if self.upShortage[i][j] < 0:
                self.upShortage[i][j] = 0

            return

        # outflow meet boundary conditions
        self.outflow[i][j] = max(self.outflow[i][j], self.minOutflow)

        # strategy: CRSS release for validation, use CRSS release data
        # self.outflow[i][j] = self.crssRelease[j]

        ### 5. set initial data for water balance calculation
        # set initial area, evaporation and precipitation values
        self.area[i][j] = self.volume_to_area(startStorage)
        self.evaporation[i][j] = self.area[i][j] * self.evapRates[month]
        self.precipitation[i][j] = self.area[i][j] * self.precipRates[month]
        self.storage[i][j] = startStorage + inflowthismonth + self.precipitation[i][j] - self.evaporation[i][j] - self.outflow[i][j]

        ### 6. iteration to make water budget balanced, the deviation is less than 10 to power of the negative 10
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

        ### 7. calculate UB shortage for the current time period
        self.upShortage[i][j] = self.upDepletion[k][j] - (self.inflow[i][j] - inflowthismonth)
        if self.upShortage[i][j] < 0:
            self.upShortage[i][j] = 0

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

    # re-drill Lake Powell
    def redrillPowell(self, storage):
        # 1. empty Lake Powell
        self.column = 9
        # 2. empty storage between 3370 to bottom of the reservoir
        if storage == self.minStorage:
            self.redrillflag = True
        # 3. outflow equals to inflow,

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