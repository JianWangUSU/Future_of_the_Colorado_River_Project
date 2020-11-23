# Opeartion coded as a function
# POLICY A B C D.
# dropdown list for policy, inflow,
import numpy as np
import matplotlib.pyplot as plt

resultPathAndName = "../results/LakeMeadDSResults.pdf"

totalN = 100  # PLANNING HORIZON, 100 years
storage = np.zeros([totalN])  # reservoir storage in MAF
MAFtoAF = 1000000

# The following function is used to do decision scaling for Lake Mead.
def DS_EmptyAndFull(reservoir):
    print("Decision scaling start!")

    demandRange = np.arange(6, 12.1, 0.1)
    inflowRange = np.arange(6, 14.1, 0.1)

    xLength = len(demandRange)
    yLength = len(inflowRange)

    x = np.asarray(demandRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([xLength, yLength])
    z2 = np.zeros([xLength, yLength])
    z3 = np.zeros([xLength, yLength])

    for i in range(0, xLength):
        for j in range(0, yLength):
            for t in range(0,totalN):
                simulation(t, reservoir, demandRange[i], inflowRange[j])
            z1[i][j] = findYearsToDry(reservoir)
            z2[i][j] = findYearsToFill(reservoir)
            z3[i][j] = findStaticStorage()

    X, Y = np.meshgrid(x, y)
    Z1 = np.transpose(z1)
    Z2 = np.transpose(z2)
    Z3 = np.transpose(z3)

    fig, ax = plt.subplots()

    CS = ax.contour(X, Y, Z2, levels=[5, 15, 30, 45], colors="#024979")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to full pool (Unit: years)")

    CS = ax.contour(X, Y, Z3, levels=[4, 8, 12, 16, 20], colors='#44A5C2')
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Static reservoir storage (Unit: MAF)")

    CS = ax.contour(X, Y, Z1, levels=[5, 10, 20, 40], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Demand below Lake Mead (MAF/year)')
    plt.ylabel('Lake Mead Inflow (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')

    print("Decision scaling finished!")

# Yearly simulation
def simulation(t, reservoir, demand, inflow):
    annualevapRate = 6  # feet

    if t == 0:
        release = demand - cutbackFromDCP(reservoir, reservoir.initStorage)
        evaporation = annualevapRate * reservoir.volume_to_area(reservoir.initStorage) / MAFtoAF
        storage[t] = reservoir.initStorage/MAFtoAF + inflow - release - evaporation
    else:
        release = demand - cutbackFromDCP(reservoir, storage[t - 1] * MAFtoAF)
        evaporation = annualevapRate * reservoir.volume_to_area(storage[t - 1] * MAFtoAF) / MAFtoAF
        storage[t] = storage[t - 1] + inflow - release - evaporation

    storage[t] = min(reservoir.maxStorage/MAFtoAF, storage[t])
    storage[t] = max(reservoir.minStorage/MAFtoAF, storage[t])

# policy: cutback from Drought contingency plan for Lake Mead for decision scaling
def cutbackFromDCP(reservoir, s):
    h = reservoir.volume_to_elevation(s)

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

def findYearsToDry(reservoir):
    for i in range(0, totalN):
      if storage[i] <= reservoir.minStorage/MAFtoAF: # how many years to dry
          return i + 1

def findYearsToFill(reservoir):
    for i in range(0, totalN):
      if storage[i] >= reservoir.maxStorage/MAFtoAF: # how many years to fill
          return i + 1

def findStaticStorage():
    sum = 0
    for i in range(totalN - 10, totalN):
        sum = sum + storage[i]
    ave = sum / 10

    return round(ave)