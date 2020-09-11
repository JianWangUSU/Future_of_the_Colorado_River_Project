from components import AggregateReservoir
from engines import AnEngine
from pynsim import Simulator, Network
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt2
import mayavi.mlab as mlab

# vtk should be 8.1.2, not 9.0

filePath1 = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/data/zvPowell.csv"
filePath2 = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/data/zv.csv"
resultPathAndName = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/results/MeadPowellEcoResults.pdf"

#Create a simulator object which will be run.
s = Simulator()

#Set the timesteps of the simulator.
# s.set_timesteps(None, start_time='2020-01-01', frequency='y', periods=40)
t = range(0, 100)  # months
s.set_timesteps(t)

#Create the network with initial data
n = Network(name="Major Colorado River Network")

#All nodes have an x, y and name.
sr1 = AggregateReservoir(x=1,  y=1, name="Lake Powell and Lake Mead")
sr1.readData1(filePath1)
sr1.readData2(filePath2)

# print(sr1.z)

n.add_nodes(sr1)

#Set the simulator's network to this network.
s.network = n

#Create an instance of the deficit allocation engine.
anEngine = AnEngine(n)

#add the engine to the simulator
s.add_engine(anEngine)

# n.nodes[0].setData(6.5, 6)
# s.start()
# print(n.nodes[0].storage)

demandRange = np.arange(6, 12.1, 0.5)
inflowRange = np.arange(6, 16.1, 0.5)
# demandRange = np.arange(6, 12.1, 0.2)
# inflowRange = np.arange(6, 16.1, 0.2)

xLength = len(demandRange)
yLength = len(inflowRange)

x = np.asarray(demandRange)
y = np.asarray(inflowRange)
z1 = np.zeros([xLength, yLength])
z2 = np.zeros([xLength, yLength])
z3 = np.zeros([xLength, yLength])

for i in range(0, xLength):
    for j in range(0, yLength):
        n.nodes[0].setData(demandRange[i], inflowRange[j], 30)
        # n.nodes[0].setData(demandRange[i], inflowRange[j], 12.6 + 10.9)

        # self.initStorage = 12.6 + 10.9 #MAF, Powell + Mead 2020 Jan storage
        # print(demandRange[i])
        # print(inflowRange[j])
        # print(" ")
        s.start()
        z1[i][j] = n.nodes[0].findYearsToMinPowerPool()
        z2[i][j] = n.nodes[0].findYearsToPearceFerry()
        z3[i][j] = n.nodes[0].findStaticStorage()

X, Y = np.meshgrid(x, y)
Z1 = np.transpose(z1)
Z2 = np.transpose(z2)
Z3 = np.transpose(z3)

fig, ax = plt.subplots()

CS = ax.contour(X, Y, Z2, levels = [5,10,20,30] , colors = "green")
# CS = ax.contour(X, Y, Z2, levels = 5 , colors = "green")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=6)
CS.collections[0].set_label("Years to Pearce Ferry Rapid (Unit: years)")

CS = ax.contour(X, Y, Z3, levels = [9,15,20,25,29] , colors = "red")#8.27, 29.22
# CS = ax.contour(X, Y, Z3, levels = 5 , colors = "red")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=6)
CS.collections[0].set_label("Static reservoir storage (Unit: MAF)")

CS = ax.contour(X, Y, Z1, levels = [10,25,45], colors = "blue")
# CS = ax.contour(X, Y, Z1, levels = 5, colors = "blue")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=6)
CS.collections[0].set_label("Years to Powell minimum power pool (Unit: years)")

font = {'size': 8}
plt.legend(loc='upper left', prop=font)
plt.ylim((6, 14))

plt.xlabel('Lower Basin (including delivery to Mexico) Depletion schedule (MAF/year)', fontsize=8)
plt.ylabel('Inflow to the aggregate Powell and Mead reservoir (MAF/year)', fontsize=8)
plt.title('How long will the aggregate Powell and Mead reservoir go minmum power pool or above Pearce Ferry Rapid?', fontsize=8)

plt.savefig(resultPathAndName,dpi=600,format='pdf')

plt2.clf()

# three dimensional plot
# for i in range(0, xLength):
#     for j in range(0, yLength):
#         n.nodes[0].setData(demandRange[i], inflowRange[j], 12.6 + 10.9)
#         s.start()
#         z1[i][j] = n.nodes[0].findYearsToMinPowerPool()
#         z2[i][j] = n.nodes[0].findYearsToPearceFerry()
#         z3[i][j] = n.nodes[0].findStaticStorage()
#
# X, Y = np.meshgrid(x, y)
# Z1 = np.transpose(z1)
# Z2 = np.transpose(z2)
# Z3 = np.transpose(z3)

# initSorage = np.arange(10, 30.1, 4)
initSorage = np.arange(10, 30.1, 2)
# initSorage = np.arange(10, 30.1, 1)


zLength = len(initSorage)
z = np.asarray(initSorage) # storage dimension

XX = np.zeros([xLength*yLength*zLength])
YY = np.zeros([xLength*yLength*zLength])
ZZ = np.zeros([xLength*yLength*zLength])
CC = np.zeros([xLength*yLength*zLength])
PP = np.zeros([xLength,yLength,zLength]) # minimum power pool
PF = np.zeros([xLength,yLength,zLength]) # pearceferry
SS = np.zeros([xLength,yLength,zLength]) # static storage

index = 0
for k in range(0, zLength):
    for i in range(0, xLength):
        for j in range(0, yLength):
            n.nodes[0].setData(demandRange[i], inflowRange[j], initSorage[k])
            s.start()

            XX[index] = x[i]
            YY[index] = y[j]
            ZZ[index] = z[k]

            c1 = n.nodes[0].findYearsToMinPowerPool()
            c2 = n.nodes[0].findYearsToPearceFerry()
            c3 = n.nodes[0].findStaticStorage()

            PP[i][j][k] = c1
            PF[i][j][k] = c2
            SS[i][j][k] = c3

            # if c1 is not None:
            #     if c1 > 0:
            #         CC[index] = c1
            #         SS[i][j][k] = c1
            #         index = index + 1
            #         continue
            # if c2 is not None:
            #     if c2 > 0:
            #         CC[index] = c2
            #         SS[i][j][k] = c2
            #         index = index + 1
            #         continue
            # else:
            #     CC[index] = c3
            #     SS[i][j][k] = c3
            #
            # index = index +1

# point view
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
#
# img = ax.scatter(XX, YY, ZZ, c=CC, cmap=plt.hot())
# fig.colorbar(img)
# plt.show()
#
# # isosurface from import plotly.graph_objects as go
# fig= go.Figure(data=go.Isosurface(
#     x = XX,
#     y = YY,
#     z = ZZ,
#     value = CC,
#     isomin=10,
#     isomax=60,
# ))
#
# fig.show()

# xx, yy, zz = np.mgrid[6:12:31j, 6:16:51j, 10:30:11j]
# colZ = zLength
# xx, yy, zz = np.mgrid[6:12:13j, 6:16:21j, 10:30:6j]
xx, yy, zz = np.mgrid[6:12:13j, 6:16:21j, 10:30:11j]
# xx, yy, zz = np.mgrid[6:12:13j, 6:16:21j, 10:30:21j]

# print(xx.shape)
# print(yy.shape)
# print(zz.shape)
# print(SS.shape)

# cus = [[247,251,255,255], [245,250,254,255], [103,0,13,255]]

blue = mlab.contour3d(xx,yy,zz,PP, colormap = 'Blues', contours = [15,30,45], vmax = 45, vmin=0)
# blue = mlab.contour3d(xx,yy,zz,PP, colormap = 'Blues', contours = [10,25,45])
# lut = blue.module_manager.scalar_lut_manager.lut.table.to_array()
# lut = [[191,178,255,255], [101,81,204,255], [38,15,153,255]]
# blue.module_manager.scalar_lut_manager.lut.table = lut
# mlab.draw()
# sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal',nb_colors=3)
sb1 = mlab.scalarbar(object = blue, title='Years to Powell minimum power pool (years)',nb_labels=4,orientation='horizontal')
sb1.scalar_bar.unconstrained_font_size = True
sb1.label_text_property.font_size = 24
sb1.title_text_property.font_size = 24
# sb1.ScalarBarRepresentation.position = [0,0]
sb1.scalar_bar.position = (0,0)
sb1.scalar_bar.position2 = (0.4,0.2)


green = mlab.contour3d(xx,yy,zz,PF, colormap = 'Greens', contours = [10,20,30], vmax = 30, vmin=0)
# green = mlab.contour3d(xx,yy,zz,PF, colormap = 'Greens', contours = [10,20,29])
# lut = green.module_manager.scalar_lut_manager.lut.table.to_array()
# lut = [[229,255,178,255], [163,204,81,255], [107,153,15,255]]
# green.module_manager.scalar_lut_manager.lut.table = lut
# mlab.draw()
# sb2 = mlab.scalarbar(object = green, title='Years to Pearce Ferry Rapid (years)',nb_labels=4,orientation='horizontal',nb_colors=3)
sb2 = mlab.scalarbar(object = green, title='Years to Pearce Ferry Rapid (years)',nb_labels=4,orientation='horizontal')
sb2.scalar_bar.unconstrained_font_size = True
sb2.label_text_property.font_size = 24
sb2.title_text_property.font_size = 24

red = mlab.contour3d(xx,yy,zz,SS, colormap = 'Reds', contours = [10,20,30], vmax = 30, vmin=0)
# red = mlab.contour3d(xx,yy,zz,SS, colormap = 'Reds', contours = [10,20,30])
# lut = red.module_manager.scalar_lut_manager.lut.table.to_array()
# lut = [[255,178,178,255], [204,81,81,255], [153,15,15,255]]
# red.module_manager.scalar_lut_manager.lut.table = lut
# mlab.draw()
# sb3 = mlab.scalarbar(object = red, title='Static reservoir storage (MAF)',nb_labels=4,orientation='horizontal',nb_colors=3)
# print(lut)
sb3 = mlab.scalarbar(object = red, title='Static reservoir storage (MAF)',nb_labels=4,orientation='horizontal')
sb3.scalar_bar.unconstrained_font_size = True
sb3.label_text_property.font_size = 24
sb3.title_text_property.font_size = 24

ax3D = mlab.axes(xlabel='demand', ylabel='inflow', zlabel='initial storage', ranges=(6, 12, 6, 16, 30, 10))
ax3D.axes.font_factor = 0.8
# mlab.orientation_axes()
mlab.outline()



mlab.show()

# cubic, scala range to show

