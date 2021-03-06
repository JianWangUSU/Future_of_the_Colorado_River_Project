from components.component import Node
import numpy as np
import pandas as pd
import os

# todo
class User(Node):
    # normal depletion, not change with inflow scenario. 2 dimension: depletion scenario and time period.
    DepletionNormal = None
    # actual depletion,
    DepletionActual = None

    DepletionRequest = None
    DepletionSchedule = None

    # yearly contribution, change with time
    Contribution = 0

    base_type = 'user'

    def __init__(self, name):
        self.name = name

    # def setupPeriodsandTraces(self, periods, tracesInflow, tracesDepletion):
    #     self.upDepletion = np.zeros([tracesDepletion][periods])
    #     self.downDepletion = np.zeros([tracesDepletion][periods])

    def setupPeriodsandTraces(self):
        self.inflowTraces = self.network.inflowTraces
        self.depletionTraces = self.network.depletionTraces
        self.periods = self.network.periods

# Lower Basin and Mexico
class LBMexico(User):
    # AZ:520460.7 NV:462154 CA:1168799 MX:191362
    initialBlance = 2342775.7
    bankBalance = None
    CRSSbankBalance = None
    CRSSbankPutTake = None

    annualPut = None
    annualTake = None
    monthPut = None
    monthTake = None
    MeadBank = None
    MeadBankInitialBalance = 0

    MAXBankCapacity = None
    MAXPUT = None
    MAXTAKE = None

    reservoir = None

    # The following parameter is calculated with CRSS simulation results.
    # Inflow below Mead = 455,652 af/year;
    InflowBelowMead = 455652
    # Mohave/Havasu change of storage and evaporation loss 330,422 af/year
    MohaveHavasu = 330422
    GainLoss = InflowBelowMead - MohaveHavasu

    def __init__(self, name, relatedReservoir):
        self.name = name
        if relatedReservoir!= None:
            self.reservoir = relatedReservoir
            self.reservoir.relatedUser = self

            self.MeadBankInitialBalance = self.reservoir.para.MeadBankInitialBalance
            self.MAXBankCapacity = self.reservoir.para.MAXBankCapacity

    # setup total periods and create related variables
    def setupPeriodsandTraces(self):
        self.inflowTraces = self.network.inflowTraces
        self.depletionTraces = self.network.depletionTraces
        self.periods = self.network.periods

        self.bankBalance = np.zeros([self.inflowTraces, self.periods])
        self.CRSSbankBalance = np.zeros([self.inflowTraces, self.periods])
        self.CRSSbankPutTake = np.zeros([self.inflowTraces, self.periods])
        self.monthPut = np.zeros([self.inflowTraces, self.periods])
        self.monthTake = np.zeros([self.inflowTraces, self.periods])
        self.annualPut = np.zeros([self.inflowTraces, int(self.periods/12)])
        self.annualTake = np.zeros([self.inflowTraces, int(self.periods/12)])

# Upper Basin
class UB(User):

    def __init__(self, name, relatedReservoir):
        self.name = name
        if relatedReservoir != None:
            self.reservoir = relatedReservoir
            self.reservoir.relatedUser = self

    # setup total periods and create related variables
    def setupPeriodsandTraces(self):
        self.inflowTraces = self.network.inflowTraces
        self.depletionTraces = self.network.depletionTraces
        self.periods = self.network.periods

        self.bankBalance = np.zeros([self.inflowTraces, self.periods])
        self.CRSSbankBalance = np.zeros([self.inflowTraces, self.periods])
        self.CRSSbankPutTake = np.zeros([self.inflowTraces, self.periods])