from components import AggregateReservoir
from engines import AnEngine
from pynsim import Simulator, Network
import numpy as np
import matplotlib.pyplot as plt

filePath1 = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/data/zvPowell.csv"
filePath2 = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/data/zv.csv"
resultPathAndName = "E:/Future_of_the_Colorado_River_Project/MeadPowellSimulation/results/LakeMeadAndPowellResults.pdf"

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

demandRange = np.arange(6, 12.1, 0.1)
inflowRange = np.arange(6, 16.1, 0.1)

xLength = len(demandRange)
yLength = len(inflowRange)

x = np.asarray(demandRange)
y = np.asarray(inflowRange)
z1 = np.zeros([xLength, yLength])
z2 = np.zeros([xLength, yLength])
z3 = np.zeros([xLength, yLength])

for i in range(0, xLength):
    for j in range(0, yLength):
        n.nodes[0].setData(demandRange[i], inflowRange[j])
        s.start()
        z1[i][j] = n.nodes[0].findYearsToDry()
        z2[i][j] = n.nodes[0].findYearsToFill()
        z3[i][j] = n.nodes[0].findStaticStorage()

X, Y = np.meshgrid(x, y)
Z1 = np.transpose(z1)
Z2 = np.transpose(z2)
Z3 = np.transpose(z3)

fig, ax = plt.subplots()

CS = ax.contour(X, Y, Z2, levels = [15,30,45,65] , colors = "green")
# CS = ax.contour(X, Y, Z2, levels = 5 , colors = "green")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
CS.collections[0].set_label("Years to fill (Unit: years)")

CS = ax.contour(X, Y, Z3, levels = [10,20,30,40] , colors = "red")
# CS = ax.contour(X, Y, Z3, levels = 5 , colors = "red")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
CS.collections[0].set_label("Static reservoir storage (Unit: MAF)")

CS = ax.contour(X, Y, Z1, levels = [10,25,45], colors = "blue")
# CS = ax.contour(X, Y, Z1, levels = 5, colors = "blue")
ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
CS.collections[0].set_label("Years to dead pool (Unit: years)")

plt.legend(loc='upper left')

plt.xlabel('Lower Basin (including delivery to Mexico) Depletion schedule (MAF/year)', fontsize=8)
plt.ylabel('Inflow to the aggregate Powell and Mead reservoir (MAF/year)', fontsize=8)
plt.title('How long will the aggregate Powell and Mead reservoir go dry or get full?', fontsize=10)

plt.savefig(resultPathAndName,dpi=600,format='pdf')
