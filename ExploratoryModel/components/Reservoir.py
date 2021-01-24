from components.component import Node
import numpy as np
import components.PolicyControl as policyControl
import components.Parameters as Parameters
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
    # upDepletion = None # UB basin depletion
    downRivers = None # rivers below this reservoir, not used in current version
    # downDepletion = None # LB basin depletion

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

    # PearceFerryRapid signpost look up table,
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
    maxRelease = None # in cfs from CRSS
    minRelease = None # in cfs from CRSS

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
    releaseTemperature = None # reservoir release temerpature

    # temperory data, for validation, rename validation.
    crssUBshortage = None # UB basin shortages
    crssOutflow = None
    crssInflow = None
    crssElevation = None
    crssStorage = None
    crssInterveInflow = None
    crssDemandBelowMead = None
    crssMohaveHavasu = None

    InactiveCapacity = None
    LiveCapacity = None

    # UBRuleCurveData.ReservoirData in CRSS
    inactiveCapacityStorage = None
    liveCapacityStorage = None

    Qsum = None
    # Powell upper Equazliation Tier
    upperTier = None

    # Equalization data
    # ForecastEOWYSPowell = None
    # ForecastEOWYSMead = None
    # ForecastPowellRelease = None
    # ForecastMeadRelease = None
    # ForecastPowellInflow = None
    # SNWPDiversionTotalDepletionRequested = None

    relatedUser = None

    # iteration for water budget calculation
    iteration = 20
    # 1 acre-feet, change to 1,000 acre-feet
    maxError = 10000

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
        self.releaseTemperature = np.zeros([self.inflowTraces, self.periods])

    # setup depletion data
    # def setupDepletion(self, user):
    #     self.upDepletion = user.upDepletion
    #     self.downDepletion = user.downDepletion

    # simulate one time period, k: depletionTrace, i: inflowTrace, j: period
    def simulationSinglePeriod(self, k, i, j):
       pass

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
