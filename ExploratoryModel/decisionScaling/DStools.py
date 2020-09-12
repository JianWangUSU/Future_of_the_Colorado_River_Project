from components.Reservoir import Reservoir
import numpy as np
import matplotlib.pyplot as plt
import mayavi.mlab as mlab


# This is decision scaling tools
class DStools():
    reservoir = None

    # 1. three dimensions: demand, inflow and initStorage, see setup function for data
    demandRange = None
    inflowRange = None
    initSorage = None

    xLength = None
    yLength = None
    zLength = None

    xx = None
    yy = None
    zz = None

    # 2. Signposts
    # minimum power pool or Pearce Ferry Rapid
    results = None

    def __init__(self):
        pass

    def setupMead(self, reservoir):
        self.reservoir = reservoir

        # 1. three dimensions: demand, inflow and initStorage
        # LB + Mexico depletion (9, 12)
        self.demandRange = np.arange(9, 12.1, 1)
        self.inflowRange = np.arange(6, 15.1, 1)
        self.initSorage = np.arange(11, 22.1, 1)
        # print(self.demandRange.shape)
        # print(self.inflowRange.shape)
        # print(self.initSorage.shape)

        self.xLength = len(self.demandRange)
        self.yLength = len(self.inflowRange)
        self.zLength = len(self.initSorage)

        a = complex(0,self.xLength)
        b = complex(0,self.yLength)
        c = complex(0,self.zLength)

        self.xx, self.yy, self.zz = np.mgrid[self.demandRange[0]:self.demandRange[self.xLength-1]:a,
                                    self.inflowRange[0]:self.inflowRange[self.yLength-1]:b,
                                    self.initSorage[0]:self.initSorage[self.zLength-1]:c]
        # print(self.xx.shape)
        # print(self.yy.shape)
        # print(self.zz.shape)
        # print(self.demandRange[self.xLength-1])

        self.results = np.zeros([self.xLength, self.yLength, self.zLength])

    def setupPowell(self, reservoir):
        self.reservoir = reservoir

        # 1. three dimensions: demand, inflow and initStorage
        self.demandRange = np.arange(6, 12, 1)
        self.inflowRange = np.arange(6, 14, 1)
        self.initSorage = np.arange(0, 15, 1)
        # print(self.demandRange.shape)
        # print(self.inflowRange.shape)
        # print(self.initSorage.shape)

        self.xLength = len(self.demandRange)
        self.yLength = len(self.inflowRange)
        self.zLength = len(self.initSorage)

        a = complex(0,self.xLength)
        b = complex(0,self.yLength)
        c = complex(0,self.zLength)

        self.xx, self.yy, self.zz = np.mgrid[self.demandRange[0]:self.demandRange[self.xLength-1]:a,
                                    self.inflowRange[0]:self.inflowRange[self.yLength-1]:b,
                                    self.initSorage[0]:self.initSorage[self.zLength-1]:c]
        print(self.xx.shape)
        print(self.yy.shape)
        print(self.zz.shape)
        # print(self.demandRange[self.xLength-1])

        self.results = np.zeros([self.xLength, self.yLength, self.zLength])

    # 3. Simulate every combinations
    def simulateCombinations(self):
        for k in range(0, self.zLength):
            for i in range(0, self.xLength):
                for j in range(0, self.yLength):
                    # simulation for a single period given demand, inflow and initStorage
                    # maf to af
                    unit = 1000000
                    elevation = self.reservoir.DSsimulation(self.demandRange[i]*unit,
                                                            self.inflowRange[j]*unit,
                                                            self.initSorage[k]*unit)
                    self.results[i][j][k] = elevation

    # 4. plot
    def plot(self):
        if self.reservoir.name == "Mead":
            blue = mlab.contour3d(self.xx, self.yy, self.zz, self.results, colormap = 'Blues', contours = [1135], vmax = 1227, vmin = 895)
            # blue = mlab.contour3d(xx,yy,zz,PP, colormap = 'Blues', contours = [10,25,45])
            # lut = blue.module_manager.scalar_lut_manager.lut.table.to_array()
            # lut = [[191,178,255,255], [101,81,204,255], [38,15,153,255]]
            # blue.module_manager.scalar_lut_manager.lut.table = lut
            # mlab.draw()
            # sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal',nb_colors=3)
            # sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal')
            # sb1.scalar_bar.unconstrained_font_size = True
            # sb1.label_text_property.font_size = 24
            # sb1.title_text_property.font_size = 24
            # # sb1.ScalarBarRepresentation.position = [0,0]
            # sb1.scalar_bar.position = (0,0)
            # sb1.scalar_bar.position2 = (0.4,0.2)

        if self.reservoir.name == "Powell":
            red = mlab.contour3d(self.xx, self.yy, self.zz, self.results, colormap = 'Reds', contours = [3510], vmax = 3700, vmin = 3370)
            # blue = mlab.contour3d(xx,yy,zz,PP, colormap = 'Blues', contours = [10,25,45])
            # lut = blue.module_manager.scalar_lut_manager.lut.table.to_array()
            # lut = [[191,178,255,255], [101,81,204,255], [38,15,153,255]]
            # blue.module_manager.scalar_lut_manager.lut.table = lut
            # mlab.draw()
            # sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal',nb_colors=3)
            # sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal')
            # sb1.scalar_bar.unconstrained_font_size = True
            # sb1.label_text_property.font_size = 24
            # sb1.title_text_property.font_size = 24
            # sb1.scalar_bar.position = (0,0)
            # sb1.scalar_bar.position2 = (0.4,0.2)

        ax3D = mlab.axes(xlabel='demand', ylabel='inflow', zlabel='initial storage',
                         ranges=(self.demandRange[0], self.demandRange[self.xLength-1],
                                 self.inflowRange[0], self.inflowRange[self.yLength-1],
                                 self.initSorage[0], self.initSorage[self.zLength-1]))

        ax3D.axes.font_factor = 0.8
        # mlab.orientation_axes()
        mlab.outline()

        mlab.show()



