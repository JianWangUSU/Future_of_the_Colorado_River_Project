from components.component import Node
import numpy as np
import sys
import components.policyControl as policyControl
import components.Parameters as Parameters
import math

from dateutil.relativedelta import relativedelta
import calendar

# class reservoir, there should be a Powell class and a Mead class, in specific reservoir class, unique virables will be defined.
class Reservoir(Node):
    name = None
    # parameters
    para = Parameters
    # policy control
    plc = policyControl

    # reservoir type
    base_type = 'reservoir'

    upRivers = None # rivers flow into this reservoir, not used in current version
    upDepletion = None # UB basin depletion
    downRivers = None # rivers below this reservoir, not used in current version
    downDepletion = None # LB basin depletion

    upReservoir = None # up stream reservoir, if this reservoir is Mead, then its upReservoir is Powell
    downReservoir = None # down stream reservoir, if this reservoir is Powell, then its downReservoir is Mead

    # elevation volume/ elevation area table
    z = None # elevation (feet)
    v = None # volume (acre-feet)
    a = None # area (acre)

    # MaxTurbineQ table
    MaxTurbineQ_Head = None # in feet
    MaxTurbineQ_TurbineCapacity = None # in acre-feet/month

    # Tailwater Table
    Tailwater_Outflow = None # in cfs, needs to convert acre-feet/month before use
    Tailwater_Elevation = None # in feet

    # PearceFerryRapid signpost look up table
    Mead_Storage = None # storage for Mead
    inflow_demand = None # inflow - demand
    FerryFlag = False # if Pearce Ferry Rapid will be reached

    # rates
    evapRates = None # gross evaporation rate
    precipRates = None # precipitation rate
    bankRates = None # change in bank storage rate

    # initial conditions (storage and reservoir elevation)
    initStorage = None
    initElevation = None

    # boundary conditions (storage, elevation and outflow)
    maxStorage = None
    minStorage = None
    maxElevation = None
    minElevation = None
    maxRelease = None # in cfs in CRSS
    minRelease = None # in cfs in CRSS

    # variables
    inflow = None # inflow storage in KAF, for Powell: total natural inflow; for Mead: intervening inflow
    outflow = None # outflow = release + spill
    release = None # release in KAF
    spill = None # spill in KAF
    evaporation = None # evaporation in KAF
    precipitation = None # precipitation in KAF
    changeBankStorage = None # change in bankStorage in KAF
    elevation = None # elevation in KAF
    storage = None # end of month storage in KAF
    area = None # area in acre
    convergence = None

    # temperory data, for validation
    crssUBshortage = None # UB basin shortages
    crssOutflow = None
    crssInflow = None
    crssElevation = None
    crssStorage = None
    crssInterveInflow = None
    crssDemandBelowMead = None

    InactiveCapacity = None
    LiveCapacity = None

    # UBRuleCurveData.ReservoirData in CRSS
    inactiveCapacityStorage = None
    liveCapacityStorage = None

    Qsum = None
    # Powell upper Equazliation Tier
    upperTier = None

    # Equalization data
    ForecastEOWYSPowell = None
    ForecastEOWYSMead = None

    ForecastPowellRelease = None
    ForecastMeadRelease = None
    ForecastPowellInflow = None

    SNWPDiversionTotalDepletionRequested = None

    # Coordinated Operation in CRSS
    Hybrid_MeadMinBalancingElevation = 1075
    Hybrid_PowellUpperTierElevation = 3575
    Hybrid_PowellLowerTierElevation = 3525
    MeadProtectionElevation = 1105
    Hybrid_Mead823Trigger = 1025

    # todo
    ShiftedEQLine = None

    ### EqualizationData
    # GlenToHoover from Jan to Dec
    GlenToHoover = [685799.999999927, 608999.999999643, 527400.000000355, 441499.999999813, 370899.999999696
        ,336400.000000011,264599.99999994,160000.000000322,73400.0000000097,0,0,0]

    # iteration for water budget calculation
    iteration = 20

    # Only for Powell, monthly release table
    PowellmonthlyRelease = None
    # column of the monthly release table, current water year
    column = 2
    # column of the monthly release table, next water year
    columnNext = 2
    # used in CRSS, not exactly the same
    targetSpace = 0

    # Only for Mead, different policies will change this value, monthly deduction
    MeadMDeductionCurrent = 0 # current water year
    MeadMDeductionNext = 0 # next water year

    redrillflag = False # only for Lake Powell, true means redrill
    lastPowellStorage = 1.89 # storage between 3370 to bottom of Lake Powell

    # PowellMinObjRelData
    PowellMinimumContent = 0

    def __init__(self, name, upR):
        self.name = name
        if upR!= None:
            self.upReservoir = upR # UP reservoir
            upR.downReservoir = self

    # setup total periods and create related variables
    def setupPeriodsandTraces(self):
        self.inflowTraces = self.network.inflowTraces
        self.depletionTraces = self.network.depletionTraces
        self.periods = self.network.periods

        self.inflow = np.zeros([self.inflowTraces, self.periods])
        self.totalinflow = np.zeros([self.inflowTraces, self.periods])
        self.outflow = np.zeros([self.inflowTraces, self.periods])
        self.release = np.zeros([self.inflowTraces, self.periods])
        self.spill = np.zeros([self.inflowTraces, self.periods])
        self.evaporation = np.zeros([self.inflowTraces, self.periods])
        self.precipitation = np.zeros([self.inflowTraces, self.periods])
        self.changeBankStorage = np.zeros([self.inflowTraces, self.periods])
        self.elevation = np.zeros([self.inflowTraces, self.periods])
        self.storage = np.zeros([self.inflowTraces, self.periods])
        self.area = np.zeros([self.inflowTraces, self.periods])
        self.balance = np.zeros([self.inflowTraces, self.periods])
        self.icsAccount = np.zeros([self.inflowTraces])
        self.upShortage = np.zeros([self.inflowTraces, self.periods])
        self.downShortage = np.zeros([self.inflowTraces, self.periods])
        self.crssStorage = np.zeros([self.inflowTraces, self.periods])
        self.testSeries1 = np.zeros([self.inflowTraces, self.periods])
        self.testSeries2 = np.zeros([self.inflowTraces, self.periods])
        self.testSeries3 = np.zeros([self.inflowTraces, self.periods])

    # setup depletion data
    def setupDepletion(self, user):
        self.upDepletion = user.upDepletion
        self.downDepletion = user.downDepletion

    # simulate one time period, k: depletionTrace, i: inflowTrace, j: period
    def simulationSinglePeriod(self, k, i, j):
       pass

    # 2007 interim Guideline, equalization + ISG
    def equalizationAndISG(self, demandtrace, inflowtrace, period):
        month = self.determineMonth(period)
        if month == self.JAN or self.FEB or self.MAR or self.MAY or self.JUN or self.JUL or self.SEP or self.NOV or self.DEC:
            return

        MeadJan1elevation = self.equalization(demandtrace, inflowtrace, period)
        if month == self.AUG:
            self.downReservoir.MeadMDeductionNext = self.downReservoir.cutbackfromGuidelines(MeadJan1elevation) / 12
        elif month == self.OCT:
            self.downReservoir.MeadMDeductionCurrent = self.downReservoir.MeadMDeductionNext

    # equalization + DCP, only triggered for Lake Powell
    def equalizationAndDCP(self, demandtrace, inflowtrace, period):
        month = self.determineMonth(period)
        # in these months, nothing happened

        if month == self.JAN or month == self.FEB or month == self.MAR or month == self.MAY or month == self.JUN or \
                month == self.JUL or month == self.SEP or month == self.NOV or month == self.DEC:
            return

        # equalization rule is triggered in AUG, then adjusted in APR
        MeadJan1elevation = self.equalization(demandtrace, inflowtrace, period)
        if month == self.AUG:
            self.downReservoir.MeadMDeductionNext = self.downReservoir.cutbackFromDCP(MeadJan1elevation) / 12
        elif month == self.OCT:
            self.downReservoir.MeadMDeductionCurrent = self.downReservoir.MeadMDeductionNext

    # Powell release under equalization rule, Mead release is determined by demand.
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

            predictedElevations = self.forecastFutureElevations(demandtrace, inflowtrace, period, predictedMonth, col, True)
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
                self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol, maxCol, True)
                self.UBreleaseFlag = False
            elif predictedPowellElevation > 3575:
                if predictedMeadElevation >= 1075:
                    self.column = 2 # annual release for Powell 8.23 MAF
                else:
                    # 7.0 and 9.0 maf, which means 4 columns to test
                    minCol = 0
                    maxCol = 4
                    self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol, maxCol, True)
                self.UBreleaseFlag = False
            elif predictedPowellElevation > 3525:
                if predictedMeadElevation >= 1025:
                    self.column = 1 # annual release for Powell 7.48 MAF
                else:
                    self.column = 2 # annual release for Powell 8.23 MAF
                self.UBreleaseFlag = False
            elif predictedPowellElevation > 3370:
                # 7.0 and 9.5 maf
                minCol = 0
                maxCol = 5
                self.column = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                                 minCol, maxCol, True)
                self.UBreleaseFlag = True

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

            predictedElevations = self.forecastFutureElevations(demandtrace, inflowtrace, period, predictedMonth, col, True)
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
                self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol, maxCol, True)
                # print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:"+ str(month))
                # print(self.columnNext)
                self.UBreleaseFlag = False

            elif predictedPowellElevation > 3575:
                if predictedMeadElevation >= 1075:
                    self.columnNext = 2 # annual release for Powell 8.23 MAF
                else:
                    # 7.0, 7.48, 8.23, 9.0 maf, which means 4 columns to test
                    minCol = 0
                    maxCol = 4
                    # print("-----------------------------------------------------")
                    # self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth, minCol, maxCol, True)
                    # print("1 period: " + str(period) + " columnNext:" + str(self.columnNext))
                    # print("1 predictedPowellElevation: " + str(predictedPowellElevation) + " predictedMeadElevation:" + str(predictedMeadElevation))
                    # SP = self.elevation_to_volume(predictedPowellElevation)
                    # SM = self.downReservoir.elevation_to_volume(predictedMeadElevation)
                    # RP = SP/self.maxStorage
                    # RM = SM/self.downReservoir.maxStorage
                    # print("1 powell rate: " + str(RP) + " mead rate:" + str(RM))
                    # print("=====================================================")
                    self.UBreleaseFlag = False
            elif predictedPowellElevation > 3525:
                if predictedMeadElevation >= 1025:
                    self.columnNext = 1 # annual release for Powell 7.48 MAF
                else:
                    self.columnNext = 2 # annual release for Powell 8.23 MAF
                self.UBreleaseFlag = False
            elif predictedPowellElevation > 3370:
                # 7.0 and 9.5 maf
                minCol = 0
                maxCol = 5
                self.columnNext = self.determineEqualizedRelease(demandtrace, inflowtrace, period, predictedMonth,
                                                                 minCol, maxCol, True)
                self.UBreleaseFlag = True

            # print("2 period: " + str(period) +" columnNext:" + str(self.columnNext))

        # OCT, come in the next water year.
        if month == self.OCT:
            if self.columnNext == None: # for the last year
                self.column = 3
            else:
                self.column = self.columnNext

            return

        # if predictedMeadElevation < self.downReservoir.volume_to_elevation(self.downReservoir.minStorage):
        #     print("inflowtrace:" + str(inflowtrace) + " period:" + str(period) + " month:"+ str(month))
        #     print(predictedMeadElevation)
        #     print(self.downReservoir.volume_to_elevation(self.downReservoir.minStorage))

        return predictedMeadElevation

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

    # Drought contingency plan (combined volume) for Lake Mead, acre-feet,
    # This is based on previous Mead elevatin, not for the predicted elevation.
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

            gap[col] = abs(endStorage1/self.maxStorage-endStorage2/self.downReservoir.maxStorage)
            # print("col:" + str(col) + " " + str(gap[col]))
            # print("Pstorage:"+str(endStorage1) + " Mstorage:" + str(endStorage2))
            # print("PRATE:"+str(endStorage1/self.maxStorage) + " Mrate:" + str(endStorage2/self.downReservoir.maxStorage))

        index = 0
        minVal = sys.maxsize
        # print("min:"+str(minCol)+" max:"+str(maxCol))
        for i in range (minCol, maxCol):
            # print("col:" + str(i) + " " + str(gap[i]))
            if gap[i] <= minVal:
                index = i
                minVal = gap[i]

        return index

    # fill Mead first
    def FMF(self, meadS):
        # Powell to 3370 feet, if Mead reaches to full pool, Powell store water
        if self.name == "Powell":
            if meadS < self.downReservoir.maxStorage:
                self.column = 9
            else:
                self.column = 3

    # fill Powell first
    def FPF(self, powerS):
        # Mead to 895 feet, if Powell reasches to full pool, Mead store water
        if self.name == "Powell":
            if powerS < self.maxStorage:
                self.column = 1
            else:
                self.column = 2

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
                self.icsAccount[i]= self.icsAccount[i] + depositThisYear
                return depositThisYear
            return 0
        elif elevation > 1075:
            if self.icsAccount[i]> withdrawThisyear:
                self.icsAccount[i]= self.icsAccount[i] - withdrawThisyear
                return 200000 - withdrawThisyear
            return 200000
        elif elevation >= 1050:
            if self.icsAccount[i] > withdrawThisyear:
                self.icsAccount[i] = self.icsAccount[i]- withdrawThisyear
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

        pass

    # to do, store water in Lake Powell
    def ICSPowell(self, elevation, i):
        # 1. store water in Lake Powell

        # 2. when in shortage, ask Lake Powell for more water
        pass

    # Lake Powell equalization elevation table
    def determineUpperTier(self, period):
        # upperTier = [3659, 3660, 3662, 3663, 3664, 3666]
        temp = period / 12.0
        index = math.floor(temp)
        return self.volume_to_elevation(self.upperTier[index])

    # determine month based on period
    def determineMonth(self, period):
        if period%12 == 0:
            return 0         #January
        if period%12 == 1:
            return 1         #Feb
        if period%12 == 2:
            return 2         #Mar
        if period%12 == 3:
            return 3         #Apr
        if period%12 == 4:
            return 4         #May
        if period%12 == 5:
            return 5         #Jun
        if period%12 == 6:
            return 6         #JUl
        if period%12 == 7:
            return 7         #Aug
        if period%12 == 8:
            return 8         #Sep
        if period%12 == 9:
            return 9         #Oct
        if period%12 == 10:
            return 10         #Nov
        if period%12 == 11:
            return 11         #Dec

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

    # re-drill Lake Powell
    def redrillPowell(self, storage):
        # 1. empty Lake Powell to dead pool
        self.column = 9
        # 2. empty storage between 3370 to bottom of the reservoir
        if storage == self.minStorage:
            self.redrillflag = True
        # 3. outflow equals to inflow

    # return Powell monthly release
    def releasePowellfun(self, month):
        return self.PowellmonthlyRelease[self.column][month]

    def volume_to_elevation(self,v):
        #INPUT acre-feet, RETURN feet
        return np.interp(v, self.v, self.z)

    def volume_to_area(self,v):
        # input acre-feet, return acre
        return np.interp(v, self.v, self.a)

    def elevation_to_volume(self,z):
        # input feet, return acre-feet
        return np.interp(z, self.z, self.v)

    def elevation_to_area(self,z):
        # input feet, return acre
        return np.interp(z, self.z, self.a)

    def MaxTurbineQ_head_to_TurbineCapacity(self, head):
        return np.interp(head, self.MaxTurbineQ_Head, self.MaxTurbineQ_TurbineCapacity)

    def TWTable_outflow_to_Elevation(self, outflow):



        return np.interp(outflow, self.Tailwater_Outflow, self.Tailwater_Elevation)

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

    # retrun acre-feet
    def MinReleaseFun(self, period):
        currentTime = self.begtime + relativedelta(months=+period)
        days = calendar.monthrange(currentTime.year, currentTime.month)[1]
        return self.para.secondsInaDay * days * self.minRelease * self.para.CFtoAcreFeet

    # retrun acre-feet
    def MaxReleaseFun(self, period):
        currentTime = self.begtime + relativedelta(months=+period)
        days = calendar.monthrange(currentTime.year, currentTime.month)[1]
        return self.para.secondsInaDay * days * self.maxRelease * self.para.CFtoAcreFeet

    # convert acre-feet to cfs
    def convertAFtoCFS(self, period, value):
        currentTime = self.begtime + relativedelta(months=+period)
        days = calendar.monthrange(currentTime.year, currentTime.month)[1]
        return value / self.para.CFtoAcreFeet / self.para.secondsInaDay * days

    # i: inflow trace; j: period
    def AvailableSpace(self, i, j):
        if j == 0:
            return self.LiveCapacity - self.initStorage
        else:
            return self.LiveCapacity - self.storage[i][j - 1]

    def CurrentAvailableSpace(self, i, j):
        return self.LiveCapacity - self.storage[i][j]

    # startDate, endDate: period index
    def EstimateEvaporation(self, startStorage, endStorage, startPeriod, endPeriod):
        startArea = self.volume_to_area(startStorage)
        endArea = self.volume_to_area(endStorage)
        eporateRate = 0
        for t in range(startPeriod, endPeriod):
            month = self.determineMonth(t)
            eporateRate = eporateRate + self.evapRates[month] * self.calcualtefractionOfEvaporation(t)

        Evap = (startArea+endArea)/2.0*eporateRate

        return Evap

    def EstimateBankStoragewithoutEvap(self, startStorage, endStorage):
        return (endStorage - startStorage) * self.bankRates

    # CRSS use this way to change its evapration rates, for Lake Mead
    def calcualtefractionOfEvaporation(self, period):
        currentTime = self.begtime + relativedelta(months=+period)
        rate = calendar.monthrange(currentTime.year, currentTime.month)[1]/31.0

        return rate

    def EOWYStorage(self, reservoir, i, t, powellRelease, meadRelease):
        if reservoir.name == "Powell":
            startS = reservoir.PreviousStorage(i, t)
            endS = min(reservoir.InitialEOWYStoragePowell(i, t, powellRelease), reservoir.liveCapacityStorage)
            startPeriod = t
            endPeriod = self.getCurrentSepIndex(t)
            result = reservoir.InitialEOWYStoragePowell(i, t, powellRelease) \
                     - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
                     - reservoir.EstimateBankStoragewithoutEvap(startS, endS)
            if result < self.PowellMinimumContent:
                return self.PowellMinimumContent
            if result > self.liveCapacityStorage:
                return self.liveCapacityStorage
            else:
                return result
            # return reservoir.InitialEOWYStoragePowell(i, t, powellRelease) - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
            #        - reservoir.EstimateBankStoragewithoutEvap(startS, endS)
        if reservoir.name == "Mead":
            startS = reservoir.PreviousStorage(i, t)
            endS = min(reservoir.InitialEOWYStorageMead(i, t, powellRelease, meadRelease), reservoir.liveCapacityStorage)
            startPeriod = t
            endPeriod = self.getCurrentSepIndex(t)
            result = reservoir.InitialEOWYStorageMead(i, t, powellRelease, meadRelease) \
                     - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
                     - reservoir.EstimateBankStoragewithoutEvap(startS, endS)
            if result < self.inactiveCapacityStorage:
                return self.inactiveCapacityStorage
            if result > self.liveCapacityStorage:
                return self.liveCapacityStorage
            else:
                return result

            # return reservoir.InitialEOWYStorageMead(i, t, powellRelease, meadRelease) - reservoir.EstimateEvaporation(startS, endS, startPeriod, endPeriod) \
            #        - reservoir.EstimateBankStoragewithoutEvap(startS, endS)

    def InitialEOWYStoragePowell(self, i, t, powellRelease):
        result = self.PreviousStorage(i, t) + self.ForecastPowellInflow[i][t] - powellRelease

        # if i == 0 and t == 399:
        #     print("-----------------------")
        #     print(self.getDate(t))
        #     print(self.PreviousStorage(i, t))
        #     print(self.ForecastPowellInflow[i][t])
        #     print(powellRelease)


        if result < 0:
            return 0
        else:
            return result
        # return self.PreviousStorage(i, t) + self.ForecastPowellInflow[i][t] - powellRelease

    def InitialEOWYStorageMead(self, i, t, powellRelease, meadRelease):
        currentMonth = self.determineMonth(t)
        if currentMonth == self.SEP:
            startPeriod = t
            endPeriod = self.getCurrentSepIndex(t)

            result = self.PreviousStorage(i, t) + powellRelease - meadRelease \
                     - sum(self.SNWPDiversionTotalDepletionRequested[i][startPeriod: self.getEndIndexforSum(endPeriod)]) \
                     + self.GlenToHoover[currentMonth]

            if result < 0:
                return 0
            else:
                return result
        else:
            startPeriod = t
            endPeriod = self.getCurrentSepIndex(t)

            # it doesn't make sense to me, but that's how CRSS treats here.
            result = self.PreviousStorage(i, t) + powellRelease - meadRelease\
                     - sum(self.SNWPDiversionTotalDepletionRequested[i][startPeriod: self.getEndIndexforSum(endPeriod)]) \
                     + self.GlenToHoover[currentMonth] + sum(self.GlenToHoover[max(currentMonth+1,self.AUG): self.getEndIndexforSum(self.SEP)])

            # if i == 0 and t == 399:
            #     print("-----------------------")
            #     print(self.getDate(t))
            #     print(self.PreviousStorage(i, t))
            #     print(meadRelease)
            #     print(sum(self.SNWPDiversionTotalDepletionRequested[i][startPeriod: self.getEndIndexforSum(endPeriod)]))
            #     print(self.GlenToHoover[currentMonth])
            #     print(sum(self.GlenToHoover[max(currentMonth+1,self.AUG): self.getEndIndexforSum(self.SEP)]))

            if result < 0:
                return 0
            else:
                return result

    def PreviousStorage(self, i, t):
        if t == 0:
            return self.initStorage
        else:
            return self.storage[i][t - 1]

    def getCurrentYear(self, t):
        index = t / 12.0
        currentYear = math.floor(index)
        return currentYear

        # determine current Jan index

    def getCurrentJanIndex(self, t):
        currentYear = self.getCurrentYear(t)
        return currentYear * 12 + self.JAN

        # determine current APR index

    def getCurrentAprIndex(self, t):
        currentYear = self.getCurrentYear(t)
        return currentYear * 12 + self.APR

    # determine current SEP index
    def getCurrentSepIndex(self, t):
        currentYear = self.getCurrentYear(t)
        return currentYear * 12 + self.SEP

    # determine current OCT index
    def getCurrentOctIndex(self, t):
        currentYear = self.getCurrentYear(t)
        return currentYear * 12 + self.OCT

    def getPreviousOctIndex(self, t):
        currentYear = self.getCurrentYear(t)
        previousYear = currentYear - 1
        if previousYear < 0:
            return self.BEFORE_START_TIME
        else:
            return previousYear * 12 + self.OCT

    def getPreviousDecIndex(self, t):
        currentYear = self.getCurrentYear(t)
        previousYear = currentYear - 1
        if previousYear < 0:
            return self.BEFORE_START_TIME
        else:
            return previousYear * 12 + self.DEC

    def getEndIndexforSum(self, index):
        return index + 1

    # return new time given period t.
    def getDate(self, t):
        newTime = self.begtime + relativedelta(months=+t)
        return newTime