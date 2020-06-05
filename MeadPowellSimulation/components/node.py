from pynsim import Node
import numpy as np
import pandas as pd
import os

class SurfaceReservoir(Node):
    """
    A general surface reservoir node
    """
    type = 'surface reservoir'

    totalN = 100 # PLANNING HORIZON

    storage = np.zeros([totalN])  # reservoir storage in MAF

    _properties = {'inflow': None,
                   'demand': None,
                   'release': None,
                   'evapRate': None,
                   'evaporation': None,
                   'initStorage': None,
                   'maxStorage': None,
                   'minStorage': None}

    def setData(self, demand, inflow):
        self.demand = demand
        self.inflow = inflow

    def setup(self, timestamp):
        # print(timestamp)
        self.evapRate = 6 #feet
        self.initStorage = 10.9 #MAF
        self.maxStorage = 26 #MAF
        self.minStorage = 0 #MAF
        # self.evaporation is in MAF

        if timestamp == 0:
            self.release = self.demand - self.cutbackFromDCP(self.initStorage*1000)
            self.evaporation = self.evapRate * self.volume_to_area(self.initStorage*1000)/1000000
            self.storage[timestamp] = self.initStorage + self.inflow - self.release - self.evaporation
        else:
            self.release = self.demand - self.cutbackFromDCP(self.storage[timestamp-1]*1000)
            self.evaporation = self.evapRate * self.volume_to_area(self.storage[timestamp-1]*1000)/1000000
            self.storage[timestamp] = self.storage[timestamp-1] + self.inflow - self.release - self.evaporation

        self.storage[timestamp] = min(self.maxStorage, self.storage[timestamp])
        self.storage[timestamp] = max(self.minStorage, self.storage[timestamp])

    # policy: cutback from Drought contingency plan for Lake Mead in MAF
    def cutbackFromDCP(self, s):
        h = self.volume_to_height(s)

        if h > 1090:
            return 0
        elif h > 1075:
            return 0.2
        elif h >= 1050:
            return 0.533
        elif h > 1045:
            return 0.617
        elif h > 1040:
            return 0.867
        elif h > 1035:
            return 0.917
        elif h > 1030:
            return 0.967
        elif h >= 1025:
            return 1.017
        else:
            return 1.1

    def readData(self, filePath):
        self.zvFile = filePath
        pwd = os.getcwd()
        os.chdir(os.path.dirname(self.zvFile))
        self.zv = pd.read_csv(os.path.basename(self.zvFile))
        os.chdir(pwd)
        self.z = self.zv.elevation.values #in feet
        self.v = self.zv.storage.values #in KAF
        self.a = self.zv.area.values #in acre

    def volume_to_height(self,v):
        #INPUT KAF, RETURN feet
        return np.interp(v, self.v, self.z)

    def volume_to_area(self,v):
        # input KAF, return acre
        return np.interp(v, self.v, self.a)

    def height_to_volume(self,z):
        # input feet, return KAF
        return np.interp(z, self.z, self.v)

    def height_to_area(self,z):
        # input feet, return acre
        return np.interp(z, self.z, self.a)

    def findYearsToDry(self):
        for i in range(0, self.totalN):
          if self.storage[i] <= self.minStorage: # how many years to dry
              return i + 1

    def findYearsToFill(self):
        for i in range(0, self.totalN):
          if self.storage[i] >= self.maxStorage: # how many years to fill
              return i + 1

    def findStaticStorage(self):
        sum = 0
        for i in range(self.totalN - 10, self.totalN):
            sum = sum + self.storage[i]
        ave = sum / 10

        return round(ave)

class AggregateReservoir(Node):
    """
    A general surface reservoir node
    """
    type = 'aggregate reservoir'

    totalN = 100 # PLANNING HORIZON

    storage = np.zeros([totalN])  # reservoir storage in MAF

    _properties = {'inflow': None,
                   'demand': None,
                   'release': None,
                   'evapRate1': None,
                   'evapRate2': None,
                   'evaporation': None,
                   'initStorage': None,
                   'maxStorage': None,
                   'minStorage': None}

    def setData(self, demand, inflow, initStorage):
        self.demand = demand
        self.inflow = inflow
        self.initStorage = initStorage

    def setup(self, timestamp):
        # print(timestamp)
        self.evapRate1 = 5.7 #feet/year, Powell
        self.evapRate2 = 6 #feet/year, Mead
        self.maxPowellStorage = 24.3 #MAF
        self.maxMeadStorage = 26 #MAF
        self.maxStorage = self.maxMeadStorage + self.maxPowellStorage #MAF
        self.minStorage = 0 #MAF
        self.min_PowellPowerPoolStorage = 3.997 #MAF
        self.max_MeadPearceFerryStorage = 15.107 #MAF
        # spliting total storage to powell and mead
        self.weightPowell = self.maxPowellStorage/ self.maxStorage
        self.weightMead = self.maxMeadStorage/ self.maxStorage

        if timestamp == 0:
            self.release = self.demand - self.cutbackFromDCP(self.initStorage*1000)
            self.evaporation1 = self.evapRate1 * self.volume_to_area1(self.weightPowell*self.initStorage*1000)/1000000
            self.evaporation2 = self.evapRate2 * self.volume_to_area2(self.weightMead*self.initStorage*1000)/1000000
            self.evaporation = self.evaporation1 + self.evaporation2
            self.storage[timestamp] = self.initStorage + self.inflow - self.release - self.evaporation
        else:
            self.release = self.demand - self.cutbackFromDCP(self.storage[timestamp-1]*1000)
            self.evaporation1 = self.evapRate1 * self.volume_to_area1(self.weightPowell*self.storage[timestamp-1]*1000)/1000000
            self.evaporation2 = self.evapRate2 * self.volume_to_area2(self.weightMead*self.storage[timestamp-1]*1000)/1000000
            self.evaporation = self.evaporation1 + self.evaporation2
            self.storage[timestamp] = self.storage[timestamp-1] + self.inflow - self.release - self.evaporation

        self.storage[timestamp] = min(self.maxStorage, self.storage[timestamp])
        self.storage[timestamp] = max(self.minStorage, self.storage[timestamp])

    # policy: cutback from Drought contingency plan for Lake Mead in MAF
    def cutbackFromDCP(self, s):
        h = self.volume_to_height2(self.weightMead*s)

        if h > 1090:
            return 0
        elif h > 1075:
            return 0.2
        elif h >= 1050:
            return 0.533
        elif h > 1045:
            return 0.617
        elif h > 1040:
            return 0.867
        elif h > 1035:
            return 0.917
        elif h > 1030:
            return 0.967
        elif h >= 1025:
            return 1.017
        else:
            return 1.1

    def readData1(self, filePath):
        self.zvFile = filePath
        pwd = os.getcwd()
        os.chdir(os.path.dirname(self.zvFile))
        self.zv1 = pd.read_csv(os.path.basename(self.zvFile))
        os.chdir(pwd)
        self.z1 = self.zv1.elevation.values #in feet
        self.v1 = self.zv1.storage.values #in KAF
        self.a1 = self.zv1.area.values #in acre

    def readData2(self, filePath):
        self.zvFile = filePath
        pwd = os.getcwd()
        os.chdir(os.path.dirname(self.zvFile))
        self.zv2 = pd.read_csv(os.path.basename(self.zvFile))
        os.chdir(pwd)
        self.z2 = self.zv2.elevation.values #in feet
        self.v2 = self.zv2.storage.values #in KAF
        self.a2 = self.zv2.area.values #in acre

    def volume_to_height2(self,v):
        #INPUT KAF, RETURN feet
        return np.interp(v, self.v2, self.z2)

    def volume_to_area1(self,v):
        # input KAF, return acre
        return np.interp(v, self.v1, self.a1)

    def volume_to_area2(self,v):
        # input KAF, return acre
        return np.interp(v, self.v2, self.a2)

    def findYearsToDry(self):
        for i in range(0, self.totalN):
          if self.storage[i] <= self.minStorage: # how many years to dry
              return i + 1

    def findYearsToFill(self):
        for i in range(0, self.totalN):
          if self.storage[i] >= self.maxStorage: # how many years to fill
              return i + 1

    def findStaticStorage(self):
        sum = 0
        for i in range(self.totalN - 10, self.totalN):
            sum = sum + self.storage[i]
        ave = sum / 10

        return round(ave)

    # for ecosystem
    def findYearsToMinPowerPool(self):
        self.totalPowerStorage = self.min_PowellPowerPoolStorage/self.weightPowell

        for i in range(0, self.totalN):
          if self.storage[i] <= self.totalPowerStorage: # how many years to dry
              return i + 1

    def findYearsToPearceFerry(self):
        self.totalPearceStorage = self.max_MeadPearceFerryStorage/self.weightMead

        for i in range(0, self.totalN):
          if self.storage[i] >= self.totalPearceStorage: # how many years to fill
              return i + 1



