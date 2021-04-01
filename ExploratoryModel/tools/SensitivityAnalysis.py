# Opeartion coded as a function
# POLICY A B C D.
# dropdown list for policy, inflow, which parameters can we change, select ones to test.
# for each parameter to give it a range, select which paramters.
# 4 MAJOR options to users: hydrology, demand, initial storage and Operating policy.
# This tool create loops to all combinations. soft code.
# key outputs, select those. How often/soon/frequently reservoir fills and to dead pool. Shortages to LB/UB users.
# major inputs. Generic inflows, demands, operating policies, evaporation.
# help identify signposts, we need this, this, not that.
# once reservoir hit dead pool, stop and change policy

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import math
from tools import DataExchange
import components.ReleaseFunction as RelFun
from tools import ReleaseTemperature

# resultPathAndName = "../results/LakeMeadDSResults.pdf"
resultPathAndName = "../tools/results/LakeMeadSensitivityAnalysisPlot.pdf"

totalN = 40  # PLANNING HORIZON, 100 years, no need to be 100 years, maybe 40 years.
storageM = np.zeros([totalN*12])  # reservoir storage in MAF
storageM1 = np.zeros([totalN*12])  # reservoir storage in MAF
storageM2 = np.zeros([totalN*12])  # reservoir storage in MAF
CombinedStorage = np.zeros([totalN*12])

storage = np.zeros([totalN])  # reservoir storage in MAF
# storage = np.zeros([totalN])  # reservoir storage in MAF
MAFtoAF = 1000000

# ==== Change parameters here ====
# steps 0.2 is used for two dimensional analysis
# steps = 0.5
# steps = 0.2
steps = 0.1
# steps 1 is used for three dimensional analysis
# steps = 1

# demand for the first reservoir to release
defaultRelease1 = 9
minRelease1 = 3
maxRelease1 = 12
# inflow to the second reservoir
defaultInflow1 = 9
minInflow1 = 3
maxInflow1 = 16

# demand for the second reservoir to release
defaultRelease2 = 9
minRelease2 = 3
maxRelease2 = 12
# inflow to the second reservoir
defaultInflow2 = 9
minInflow2 = 3
maxInflow2 = 14

# initial storage
initStorage = 0
mininitS1 = 6
maxinitS1 = 20
mininitS2 = 6
maxinitS2 = 20
totalMinIntiS = 12
totalMaxIntiS = 30

# policy
deductionPolicy = 0

# The following function is used to do Multi-dimensional sensitivity analysis for Lake Mead.
def SA_EmptyAndFull(reservoir, filePath):
    print("Multi-dimensional sensitivity analysis start!")

    # set up data
    releaseRange = np.arange(minRelease2, maxRelease2, steps)
    inflowRange = np.arange(minInflow2, maxInflow2, steps)

    # have to do this, otherwise, number will be something like 3.00000000000001
    releaseRange = np.round(releaseRange, 1)
    inflowRange = np.round(inflowRange, 1)

    # If ToEmpty is true:
    ### Mead storage start at 6 maf, end at 0;
    # else:
    ### Mead storage start at 10 maf, end at storage(1025 ft)
    ToEmpty = True
    if ToEmpty:
        # https://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html
        # Lake Mead End of Month elevation DEC 2020 is 1083.72 feet, which equals to 10321613 acre-feet
        # initStorage = 10.32 * MAFtoAF
        # initStorage = 8 * MAFtoAF
        # initStorage = 6 * MAFtoAF
        initStorage = 4 * MAFtoAF
    else:
        # Lake Mead January 1, 2021 elevation (1083.72 feet), the corresponding storage is 10.32 maf.
        initStorage = 10.32 * MAFtoAF
        # initStorage = 13 * MAFtoAF
        # initStorage = 16 * MAFtoAF
        # initStorage = 8 * MAFtoAF

    releaseLength = len(releaseRange)
    inflowLength = len(inflowRange)

    x = np.asarray(releaseRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([releaseLength, inflowLength])
    z2 = np.zeros([releaseLength, inflowLength])
    z3 = np.zeros([releaseLength, inflowLength])

    deduction = 0
    for i in range(0, releaseLength):
        print(str(format(i / releaseLength * 100, '.0f')) + '%' + " finish!")
        for j in range(0, inflowLength):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorage
                else:
                    startStorage = storageM[t-1]

                inflow = inflowRange[j]/12*MAFtoAF
                release = releaseRange[i]/12*MAFtoAF

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                # if inflowRange[j] == 3.3 and releaseRange[i] == 3:
                #     print(storageM[t])

            if ToEmpty:
                z1[i][j] = findYearsToEmpty(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetweenEmptyandFull(reservoir, storageM)
            else:
                z1[i][j] = findYearsTo1025ft(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetween1025ftandFull(reservoir, storageM)

    X, Y = np.meshgrid(x, y)
    Z1 = np.transpose(z1)
    Z2 = np.transpose(z2)
    Z3 = np.transpose(z3)

    fig, ax = plt.subplots()

    # upper lines
    CS = ax.contour(X, Y, Z2, levels=[5, 10, 20, 25, 30], colors="#024979")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to full pool (Unit: years)")

    # middle lines
    if ToEmpty:
        CS = ax.contour(X, Y, Z3, levels=[4, 8, 12, 16, 20, 24], colors='#44A5C2')
        # ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=2)
        CS.collections[0].set_label("Mead EOPH elevation between full pool and dead pool")
    else:
        CS = ax.contour(X, Y, Z3, levels=[8, 12, 16, 20, 24], colors='#44A5C2')
        # ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=2)
        CS.collections[0].set_label("Mead EOPH elevation between full pool and 1025 ft")

    # bottom lines
    if ToEmpty:
        CS = ax.contour(X, Y, Z1, levels=[1, 2, 3, 4, 5, 10, 20, 30, 34], colors="#FFAE49")
        ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
        CS.collections[0].set_label("Years to empty (Unit: years)")
    else:
        CS = ax.contour(X, Y, Z1, levels=[1, 2, 3, 4, 5, 10, 20, 35, 40], colors="#FFAE49")
        ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
        CS.collections[0].set_label("Years to 1025 ft (Unit: years)")

    if ToEmpty:
        # 1.375 LB and Mexico cutback value
        ax.hlines(y=7 + 1, xmin=3, xmax=9.6, linewidth=1, color='grey', linestyles='dashed')
        ax.vlines(x=9.6 - 1.375, ymin=3, ymax=7 + 1, linewidth=1, color='grey', linestyles='dashed')
        ax.vlines(x=9.6, ymin=3, ymax=7 + 1, linewidth=1, color='grey', linestyles='dashed')

        ax.hlines(y=7, xmin=3, xmax=9.6 - 1.375, linewidth=1, color='r', linestyles='dotted')
        ax.vlines(x=9.6 - 1.375*2, ymin=3, ymax=7, linewidth=1, color='r', linestyles='dotted')

        # ax.hlines(y=5.7 + 1, xmin=3, xmax=7.5, linewidth=1, color='r', linestyles='dotted')
        # ax.vlines(x=7.5, ymin=3, ymax=5.7 + 1, linewidth=1, color='r', linestyles='dotted')
        # ax.vlines(x=6.4, ymin=3, ymax=5.7 + 1, linewidth=1, color='r', linestyles='dotted')
    else:
        ax.hlines(y=8.23+1, xmin=3, xmax=9.6, linewidth=1, color='grey', linestyles='dashed')
        ax.hlines(y=7+1, xmin=3, xmax=9.6, linewidth=1, color='grey', linestyles='dashed')
        # ax.vlines(x=9.6 - 0.66, ymin=3, ymax=8.23+1, linewidth=1, color='grey', linestyles='dashed')
        ax.vlines(x=9.6 - 1.375, ymin=3, ymax=8.23+1, linewidth=1, color='grey', linestyles='dashed')
        ax.vlines(x=9.6, ymin=3, ymax=8.23+1, linewidth=1, color='grey', linestyles='dashed')

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead Release(MAF/year)')
    plt.ylabel('Lake Mead Inflow (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

    print("Multi-dimensional sensitivity analysis finished!")

    x = np.round(x, 1)
    y = np.round(y, 1)
    z1 = np.round(z1, 1)
    z2 = np.round(z2, 1)
    z3 = np.round(z3, 1)

    if ToEmpty:
        tabName = 'YearsToDeadPool'
    else:
        tabName = 'YearsTo1025ft'
    DataExchange.exportMSAresults(filePath, y, x, z1, z2, z3, tabName)

# This function can only be used by Lake Mead
def SA_YearsTo1025_DCP(reservoir, filePath):
    print("Multi-dimensional sensitivity analysis start!")

    # set up data
    releaseRange = [9.6]
    # releaseRange = np.arange(minRelease2, maxRelease2, steps)
    inflowRange = np.arange(minInflow2, maxInflow2, steps)

    # have to do this, otherwise, number will be something like 3.00000000000001
    releaseRange = np.round(releaseRange, 1)
    inflowRange = np.round(inflowRange, 1)

    ToEmpty = False
    if ToEmpty:
        # https://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html
        # Lake Mead End of Month elevation DEC 2020 is 1083.72 feet, which equals to 10321613 acre-feet
        # initStorage = 10.32 * MAFtoAF
        # initStorage = 8 * MAFtoAF
        # initStorage = 6 * MAFtoAF
        initStorage = 4 * MAFtoAF
    else:
        # Lake Mead January 1, 2021 elevation (1083.72 feet), the corresponding storage is 10.32 maf.
        initStorage = 10.32 * MAFtoAF
        # initStorage = 13 * MAFtoAF
        # initStorage = 16 * MAFtoAF
        # initStorage = 8 * MAFtoAF

    releaseLength = len(releaseRange)
    inflowLength = len(inflowRange)

    x = np.asarray(releaseRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([releaseLength, inflowLength])
    z2 = np.zeros([releaseLength, inflowLength])
    z3 = np.zeros([releaseLength, inflowLength])

    for i in range(0, releaseLength):
        print(str(format(i / releaseLength * 100, '.0f')) + '%' + " finish!")
        for j in range(0, inflowLength):
            deduction = 0
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorage
                else:
                    startStorage = storageM[t-1]

                if t%12 == 0:
                    startElevation = reservoir.volume_to_elevation(startStorage)
                    deduction = RelFun.cutbackFromDCP(startElevation)
                    # print(startStorage)
                    # print(startElevation)
                    # print(deduction)
                    # print("===================")

                inflow = inflowRange[j]/12*MAFtoAF
                release = releaseRange[i]/12*MAFtoAF - deduction/12

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                if inflowRange[j] == 9.2:
                    print(storageM[t])

            if ToEmpty:
                z1[i][j] = findYearsToEmpty(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetweenEmptyandFull(reservoir, storageM)
            else:
                z1[i][j] = findYearsTo1025ft(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetween1025ftandFull(reservoir, storageM)


    print("Multi-dimensional sensitivity analysis finished!")

    x = np.round(x, 1)
    y = np.round(y, 1)
    z1 = np.round(z1, 1)
    z2 = np.round(z2, 1)
    z3 = np.round(z3, 1)

    if ToEmpty:
        tabName = 'YearsToDeadPool'
    else:
        tabName = 'YearsTo1025ft'
    DataExchange.exportMSAresults(filePath, y, x, z1, z2, z3, tabName)

# This function can only be used by Lake Powell
def SA_YearsTo3525(reservoir, filePath):
    print("Multi-dimensional sensitivity analysis start!")

    # set up data
    releaseRange = [8.23]
    # releaseRange = np.arange(minRelease2, maxRelease2, steps)
    inflowRange = np.arange(minInflow2, maxInflow2, steps)

    # have to do this, otherwise, number will be something like 3.00000000000001
    releaseRange = np.round(releaseRange, 1)
    inflowRange = np.round(inflowRange, 1)

    ToEmpty = False
    if ToEmpty:
        # https://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html
        # Lake Mead End of Month elevation DEC 2020 is 1083.72 feet, which equals to 10321613 acre-feet
        # initStorage = 10.32 * MAFtoAF
        # initStorage = 8 * MAFtoAF
        # initStorage = 6 * MAFtoAF
        initStorage = 4 * MAFtoAF
    else:
        # Lake Mead January 1, 2021 elevation (1083.72 feet), the corresponding storage is 10.32 maf.
        initStorage = 10.13 * MAFtoAF
        # initStorage = 13 * MAFtoAF
        # initStorage = 16 * MAFtoAF
        # initStorage = 8 * MAFtoAF

    releaseLength = len(releaseRange)
    inflowLength = len(inflowRange)

    x = np.asarray(releaseRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([releaseLength, inflowLength])
    z2 = np.zeros([releaseLength, inflowLength])
    z3 = np.zeros([releaseLength, inflowLength])

    for i in range(0, releaseLength):
        print(str(format(i / releaseLength * 100, '.0f')) + '%' + " finish!")
        for j in range(0, inflowLength):
            deduction = 0
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorage
                else:
                    startStorage = storageM[t-1]

                inflow = inflowRange[j]/12*MAFtoAF
                release = releaseRange[i]/12*MAFtoAF

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                if inflowRange[j] == 8.5:
                    print(storageM[t])

            if ToEmpty:
                z1[i][j] = findYearsToEmpty(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetweenEmptyandFull(reservoir, storageM)
            else:
                z1[i][j] = findYearsTo1025ft(reservoir, storageM)
                z2[i][j] = findYearsToFull(reservoir, storageM)
                z3[i][j] = findEndStorageBetween1025ftandFull(reservoir, storageM)


    print("Multi-dimensional sensitivity analysis finished!")

    x = np.round(x, 1)
    y = np.round(y, 1)
    z1 = np.round(z1, 1)
    z2 = np.round(z2, 1)
    z3 = np.round(z3, 1)

    if ToEmpty:
        tabName = 'YearsToDeadPool'
    else:
        tabName = 'YearsTo3525ft'
    DataExchange.exportMSAresults(filePath, y, x, z1, z2, z3, tabName)

# calculate reservoir storage based on different inflows and release policies
# x: Natural inflow Y: years to 12 maf; X: time, Y: Delivery
def SensitivityAnalysisPowellMead_12MAF_Delivery(reservoir1, reservoir2, filePath):
    print("Multi-dimensional sensitivity for Lake Powell and Lake Mead analysis start!")

    # policy index, 0-DCP, 1-Other cutbacks, 2-ADP
    policyIndex = 2
    # additional cut value for DCP+
    additionalCut = 0.4

    # set up data
    minLeesFerryNatural = 5
    maxLeesFerryNatural = 14
    steps = 0.2
    inflowRange1 = np.arange(minLeesFerryNatural, maxLeesFerryNatural, steps)
    i1_length = len(inflowRange1)

    YearsTo12maf = np.zeros([i1_length])
    TotalDelivery = np.zeros([i1_length, totalN * 12])
    PowellReleaseTempMAX = np.zeros([i1_length, totalN * 12])
    PowellReleaseTempMIN = np.zeros([i1_length, totalN * 12])

    # Lake Powell JAN 1, 2021 elevation: 3582.2 feet, 10.1 maf:
    # Lake Mead JAN 1, 2021 elevation: 1083.72 feet, 10.3 maf
    PowellInitS = 10.1 * MAFtoAF
    MeadInitS = 10.3 * MAFtoAF
    totalInitS = PowellInitS + MeadInitS

    # first year evaporation, 2020
    PowellInitE = 0.36 * MAFtoAF
    MeadInitE = 0.55 * MAFtoAF

    # intervening inflow (intervening inflow + Virgin river) in maf/yr
    # Wang and Schmidt. (2020) Stream flow and Losses of the Colorado River in the Southern Colorado Plateau
    # 2007-2018 average is 0.927 amf (including Virgin river, excluding seepage from Lake Powell);
    interveningInflow = 0.9 * MAFtoAF

    # UCRC 2007 schedule B. http://www.ucrcommission.com/RepDoc/DepSchedules/Dep_Schedules_2007.pdf
    # UBdemand = 5.35 * MAFtoAF
    # UBdemand = 5 * MAFtoAF
    UBdemand = 4.5 * MAFtoAF
    # UBdemand = 4 * MAFtoAF
    # UBdemand = 3.5 * MAFtoAF
    # UBdemand = 3 * MAFtoAF

    # Lower Basin and Mexico demand. In my understanding, it also includes inflows below Lake Mead
    # http://www.inkstain.net/fleck/2020/01/how-big-was-lake-meads-structural-deficit-in-2019/
    LBMdemand = 9.6 * MAFtoAF

    # look 10 years backward
    pastYears = 10

    evaprationPowell = np.zeros([totalN * 12])  # evaporation for reservoir 1, Lake Powell, monthly results
    evaprationMead = np.zeros([totalN * 12])  # evaporation for reservoir 2, Lake Mead, monthly results
    CombinedStoragePM = np.zeros([i1_length ,totalN * 12])

    # for different natural inflow at Lees Ferry
    for i1 in range(0, i1_length):
        print(str(format(i1 / i1_length * 100, '.0f')) + '%' + " finish!")
        # reset these values when inflow changes
        UBshortage = 0
        LBshortage = 0
        annualLBMshort = 0
        annualMeadRelease = 0

        # for different time series
        for t in range(0, totalN*12):
            # get initial monthly storage
            if t == 0:
                startStorage1 = PowellInitS
                startStorage2 = MeadInitS
            else:
                # storageM means monthly storage
                startStorage1 = storageM1[t - 1]
                startStorage2 = storageM2[t - 1]

            # calculate inflow to Lake Powell
            if policyIndex == 2:
                # January and smaller than trigger
                if t%12 == 0 and startStorage2 < reservoir2.plc.ADP_triggerS_LOW:

                    if t == 0:
                        totalEvap = PowellInitE + MeadInitE
                    else:
                        if t/12 >=pastYears:
                            totalEvap = sum(evaprationPowell[t - pastYears * 12:t])/pastYears \
                                        + sum(evaprationMead[t - pastYears * 12:t])/pastYears
                        else:
                            totalEvap = sum(evaprationPowell[0:t])/int(t/12) \
                                        + sum(evaprationMead[0:t])/int(t/12)

                    # in acre-feet
                    totalInflow = inflowRange1[i1] * MAFtoAF + interveningInflow - totalEvap
                    totalDemand = UBdemand + LBMdemand
                    totalShortage = max(totalDemand - totalInflow, 0)

                    UBshortage = totalShortage * UBdemand/totalDemand
                    LBshortage = totalShortage * LBMdemand/totalDemand
            else:
                UBshortage = 0

            inflow1 = max((inflowRange1[i1] * MAFtoAF - UBdemand + UBshortage)/12, 0)

            # determined by policies
            # (1) equalization + DCP
            # (2) equalization + other DCPs
            # (3) equalization + ADP

            # release2 = Lake Mead release, determined by different policies
            if t % 12 == 0:
                # annual cutbacks are calculated in January
                if policyIndex == 0:
                    # DCP
                    annualLBMshort = RelFun.cutbackFromDCP_storage(reservoir2, startStorage2)
                elif policyIndex == 1:
                    # DCP2
                    annualLBMshort = RelFun.cutbackFromDCPplus_storage(reservoir2, startStorage2, additionalCut)
                elif policyIndex == 2:
                    # ADP
                    if startStorage2 < reservoir2.plc.ADP_triggerS_LOW:
                        annualLBMshort = LBshortage
                    else:
                        annualLBMshort = 0

                annualMeadRelease = LBMdemand - annualLBMshort

            release2 = annualMeadRelease/12

            # endStorage1 = startStorage1 + inflow1 - release1
            # inflow2 = release1 + interveningInflow / 12
            # endStorage2 = startStorage2 + inflow2 - release2
            # release1 = Lake Powell release, determined by equalization policy (simple version here, no evap and bank change)
            # use previous equations can solve Lake Powell release
            release1 = (startStorage1 + inflow1 - startStorage2 + release2 - interveningInflow / 12) / 2.0

            results = reservoir1.simulationSinglePeriodGeneral(startStorage1, inflow1, release1, t)
            storageM1[t] = results[0]
            outflow1 = results[1]
            evaprationPowell[t] = results[3]

            inflow2 = outflow1 + interveningInflow / 12
            results = reservoir2.simulationSinglePeriodGeneral(startStorage2, inflow2, release2, t)
            storageM2[t] = results[0]
            outflow2 = results[1]
            evaprationMead[t] = results[3]

            CombinedStoragePM[i1][t] = storageM1[t] + storageM2[t]

            # totaldelivery equals to UB + LBM
            TotalDelivery[i1][t] = UBdemand/12 - UBshortage/12 + outflow2

            # calcualte release temprature
            month = reservoir1.para.determineMonth(t)
            ave_elevation = \
                (reservoir1.volume_to_elevation(storageM1[t]) + reservoir1.volume_to_elevation(startStorage1)) / 2
            PowellReleaseTempMAX[i1][t] = \
                ReleaseTemperature.getReleaseTempDeltaD(month, ave_elevation)
            PowellReleaseTempMIN[i1][t] = \
                ReleaseTemperature.getMinReleaseTempDeltaD(month, ave_elevation)

            # if round(inflowRange1[i1],1) == 12:
                # print(str(t)+" "+str(storageM1[t])+" "+str(storageM2[t]))
                # print(CombinedStorage[t])

        YearsTo12maf[i1] = findYearsTo12maf(CombinedStoragePM[i1])

    print("Multi-dimensional sensitivity analysis for Lake Powell and Lake Mead finished!")

    DataExchange.exportMSAresults2(filePath, inflowRange1, YearsTo12maf, TotalDelivery,
                                   CombinedStoragePM, PowellReleaseTempMAX, PowellReleaseTempMIN)

def SA_EmptyAndFullPowellMead(reservoir1, reservoir2, filePath):
    print("Multi-dimensional sensitivity for Lake Powell and Lake Mead analysis start!")

    # set up data
    releaseRange2 = np.arange(minRelease2, maxRelease2, steps)
    inflowRange1 = np.arange(minInflow1, maxInflow1, steps)

    r2_length = len(releaseRange2)
    i1_length = len(inflowRange1)

    x = np.asarray(releaseRange2)
    y = np.asarray(inflowRange1)
    z1 = np.zeros([r2_length, i1_length])
    z2 = np.zeros([r2_length, i1_length])
    z3 = np.zeros([r2_length, i1_length])

    ToEmpty = False
    if ToEmpty:
        # totalInitS = 20 * MAFtoAF
        # totalInitS = 12 * MAFtoAF
        totalInitS = 6 * MAFtoAF
    else:
        # totalInitS = 20 * MAFtoAF
        # totalInitS = 30 * MAFtoAF
        totalInitS = 40 * MAFtoAF

    # intervening inflow (intervening inflow + Virgin river) in maf/yr
    # Wang and Schmidt. (2020) Stream flow and Losses of the Colorado River in the Southern Colorado Plateau
    # 2007-2018 average is 1.064 amf (including Virgin river); 1990-2018 average is 1.03 maf (including Virgin river)
    interveningInflow = 1 * MAFtoAF

    for r2 in range(0, r2_length):
        print(str(format(r2 / r2_length * 100, '.0f')) + '%' + " finish!")

        for i1 in range(0, i1_length):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage1 = totalInitS / 2
                else:
                    # storageM means monthly storage
                    startStorage1 = storageM1[t - 1]

                # these two are determined once i1 and r2 are determined
                inflow1 = inflowRange1[i1] / 12 * MAFtoAF
                release2 = releaseRange2[r2] / 12 * MAFtoAF

                # Equalization, not perfect because evaporation will not be the same for the same reservoir storage
                # Experiment 1: if inflow to Powell is 10 maf, release from Mead is 6 maf, interveningInflow = 1 maf
                # The combined storage will increase 5, 2.5 by each. Release from Powell should be (10+6-1)/2
                # Experiment 2: if inflow to Powell is 10 maf, release from Mead is 10 maf, interveningInflow = 1 maf
                # The combined storage will increase 1, 0.5 by each. Release from Powell should be (10+10-1)/2
                # Experiment 3: if inflow to Powell is 4, release from Mead is 12, interveningInflow = 1 maf
                # The combined storage will decrease by 7, 3.5 by each. Release from Powell should be (4+12-1)/2
                release1 = (inflow1 + release2 - interveningInflow / 12 ) / 2
                results = reservoir1.simulationSinglePeriodGeneral(startStorage1, inflow1, release1, t)
                storageM1[t] = results[0]
                inflow2 = results[1]

                if t == 0:
                    startStorage2 = totalInitS / 2
                else:
                    startStorage2 = storageM2[t - 1]
                inflow2 = inflow2 + interveningInflow / 12
                results = reservoir2.simulationSinglePeriodGeneral(startStorage2, inflow2, release2, t)
                storageM2[t] = results[0]
                # print(str(t)+" "+str(storageM1[t])+" "+str(storageM2[t]))

                CombinedStorage[t] = storageM1[t] + storageM2[t]

                # if round(inflowRange1[i1],1) == 3 and round(releaseRange2[r2], 1) == 11.9:
                #     print(CombinedStorage[t])

            if ToEmpty:
                z1[r2][i1] = findYearsToEmpty2(reservoir1, reservoir2, CombinedStorage)
                z2[r2][i1] = findYearsToFull2(reservoir1, reservoir2, CombinedStorage)
                z3[r2][i1] = findEndStorageBetweenEmptyandFull2(reservoir1, reservoir2, CombinedStorage)
            else:
                z1[r2][i1] = findYearsTo12maf(CombinedStorage)
                z2[r2][i1] = findYearsToFull2(reservoir1, reservoir2, CombinedStorage)
                z3[r2][i1] = findEndStorageBetween12MafandFull(reservoir1, reservoir2, CombinedStorage)

    X, Y = np.meshgrid(x, y)
    Z1 = np.transpose(z1)
    Z2 = np.transpose(z2)
    Z3 = np.transpose(z3)

    fig, ax = plt.subplots()

    CS = ax.contour(X, Y, Z2, levels=[5, 10, 15, 30], colors="#024979")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to full pool (Unit: years)")

    if ToEmpty:
        CS = ax.contour(X, Y, Z3, levels=[4, 12, 20, 28, 36, 42, 50], colors='#44A5C2')
        # ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
        CS.collections[0].set_label("Final combined storage between dead pool and full pool")
    else:
        CS = ax.contour(X, Y, Z3, levels=[4, 12, 20, 28, 36, 42, 50], colors='#44A5C2')
        # ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
        CS.collections[0].set_label("Final combined storage between 12 maf and full pool")

    CS = ax.contour(X, Y, Z1, levels=[5, 10, 20, 35], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    if ToEmpty:
        CS.collections[0].set_label("Years to dead pool (Unit: years)")
    else:
        CS.collections[0].set_label("Years to 12 maf (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead Release (MAF/year)')
    plt.ylabel('Lake Powell Inflow (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

    print("Multi-dimensional sensitivity analysis for Lake Powell and Lake Mead finished!")

    x = np.round(x, 1)
    y = np.round(y, 1)
    z1 = np.round(z1, 1)
    z2 = np.round(z2, 1)
    z3 = np.round(z3, 1)

    if ToEmpty:
        tabName = 'YearsToDeadPool'
    else:
        tabName = 'YearsTo12MAF'
    DataExchange.exportMSAresults(filePath, y, x, z1, z2, z3, tabName)

def findYearsToEmpty(reservoir, s):
    for i in range(0, totalN*12):
      if s[i] <= reservoir.minStorage: # how many years to dry
          # return math.floor(i / 12)
          return i / 12

# for two reservoirs
def findYearsToEmpty2(reservoir1, reservoir2, s):
    for i in range(0, totalN*12):
      if s[i] <= reservoir1.minStorage + reservoir2.minStorage: # how many years to dry
          return i / 12

def findYearsTo1025ft(reservoir, s):
    for i in range(0, totalN*12):
      if s[i] <= reservoir.elevation_to_volume(1025): # how many years to 1025 feet
          return i / 12

def findYearsTo12maf(s):
    for i in range(0, totalN*12):
      if s[i] <= 12 * MAFtoAF: # how many years to 12 maf
          return i/12 # months divided by 12

# s: storage array
def findYearsToFull(reservoir, s):
    for i in range(0, totalN*12):
      if s[i] >= reservoir.maxStorage: # how many years to fill
          return i / 12

# for two reservoirs
def findYearsToFull2(reservoir1, reservoir2, s):
    for i in range(0, totalN*12):
      if s[i] >= reservoir1.maxStorage + reservoir2.maxStorage: # how many years to fill
          return i / 12

# return unit: MAF
def findEndStorageBetween1025ftandFull(reservoir, s):
    index = len(s)
    if s[index-1] < reservoir.maxStorage and s[index-1] > reservoir.elevation_to_volume(1025):
        return s[index-1]/MAFtoAF

# return unit: MAF
def findEndStorageBetween12MafandFull(reservoir1, reservoir2, s):
    index = len(s)
    if s[index-1] < reservoir1.maxStorage + reservoir2.maxStorage\
            and s[index-1] > 12 * MAFtoAF:
        return s[index-1]/MAFtoAF

# return unit: MAF
def findEndStorageBetweenEmptyandFull(reservoir, s):
    index = len(storageM)
    if s[index - 1] < reservoir.maxStorage and s[index - 1] > reservoir.minStorage:
        return s[index - 1] / MAFtoAF

# for two reservoirs
def findEndStorageBetweenEmptyandFull2(reservoir1, reservoir2, s):
    index = len(storageM)
    if s[index - 1] < reservoir1.maxStorage + reservoir2.maxStorage\
            and s[index - 1] > reservoir1.minStorage + reservoir2.minStorage:
        return s[index - 1] / MAFtoAF

# ===================================================abandon========================================================
def setParameters(minDemand,maxDemand,minInflow,maxInflow,reservoir):

    # 1. set yearly data, disaggregate into monthly data
    # 2. do simulation
    demandRange = np.arange(minDemand, maxDemand, 1)
    inflowRange = np.arange(minInflow, maxInflow, 1)

    reservoir.simulationSinglePeriod()

    return

# Yearly simulation
def simulation(t, reservoir, demand, inflow):
    annualevapRate = 6  # feet

    if t == 0:
        # release = demand - cutbackFromDCP3(reservoir, reservoir.initStorage)
        # release = demand - cutbackFromDCPgivenStorageAndInflow(reservoir, reservoir.initStorage, inflow)
        release = demand - cutbackFromDCPgivenStorageInflowDemand(reservoir, reservoir.initStorage, inflow, demand)

        evaporation = annualevapRate * reservoir.volume_to_area(reservoir.initStorage) / MAFtoAF
        storage[t] = reservoir.initStorage/MAFtoAF + inflow - release - evaporation
    else:
        # release = demand - cutbackFromDCP3(reservoir, storage[t - 1] * MAFtoAF)
        # release = demand - cutbackFromDCPgivenStorageAndInflow(reservoir, storage[t - 1] * MAFtoAF, inflow)
        release = demand - cutbackFromDCPgivenStorageInflowDemand(reservoir, storage[t - 1] * MAFtoAF, inflow, demand)

        evaporation = annualevapRate * reservoir.volume_to_area(storage[t - 1] * MAFtoAF) / MAFtoAF
        storage[t] = storage[t - 1] + inflow - release - evaporation

    storage[t] = min(reservoir.maxStorage/MAFtoAF, storage[t])
    storage[t] = max(reservoir.minStorage/MAFtoAF, storage[t])

def cutbackFromDCPgivenStorageInflowDemand(reservoir, storage, inflow, demand):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        if inflow < 9 and demand > 9:
            return 0.2 * 3
        else:
            return 0.2
    elif elevation >= 1050:
        if inflow < 9 and demand > 9:
            return 0.533 * 3
        else:
            return 0.533
    elif elevation > 1045:
        if inflow < 9 and demand > 9:
            return 0.617 * 3
        else:
            return 0.617
    elif elevation > 1040:
        if inflow < 9 and demand > 9:
            return 0.867 * 3
        else:
            return 0.867
    elif elevation > 1035:
        if inflow < 9 and demand > 9:
            return 0.917 * 3
        else:
            return 0.917
    elif elevation > 1030:
        if inflow < 9 and demand > 9:
            return 0.967 * 3
        else:
            return 0.967
    elif elevation >= 1025:
        if inflow < 9 and demand > 9:
            return 1.017 * 3
        else:
            return 1.017
    else:
        if inflow < 9 and demand > 9:
            return 1.1 * 3
        else:
            return 1.1


# policy: cutback from Drought contingency plan for Lake Mead for decision scaling
def cutbackFromDCPgivenStorageAndInflow(reservoir, storage, inflow):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        if inflow < 9:
            return 0.2 * 3
        else:
            return 0.2
    elif elevation >= 1050:
        if inflow < 9:
            return 0.533 * 3
        else:
            return 0.533
    elif elevation > 1045:
        if inflow < 9:
            return 0.617 * 3
        else:
            return 0.617
    elif elevation > 1040:
        if inflow < 9:
            return 0.867 * 3
        else:
            return 0.867
    elif elevation > 1035:
        if inflow < 9:
            return 0.917 * 3
        else:
            return 0.917
    elif elevation > 1030:
        if inflow < 9:
            return 0.967 * 3
        else:
            return 0.967
    elif elevation >= 1025:
        if inflow < 9:
            return 1.017 * 3
        else:
            return 1.017
    else:
        if inflow < 9:
            return 1.1 * 3
        else:
            return 1.1



# double cutbacks
def cutbackFromDCP2(reservoir, storage):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        return 0.2*2
    elif elevation >= 1050:
        return 0.533*2
    elif elevation > 1045:
        return 0.617*2
    elif elevation > 1040:
        return 0.867*2
    elif elevation > 1035:
        return 0.917*2
    elif elevation > 1030:
        return 0.967*2
    elif elevation >= 1025:
        return 1.017*2
    else:
        return 1.1*2

# triple cutbacks
def cutbackFromDCP3(reservoir, storage):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        return 0.2*3
    elif elevation >= 1050:
        return 0.533*3
    elif elevation > 1045:
        return 0.617*3
    elif elevation > 1040:
        return 0.867*3
    elif elevation > 1035:
        return 0.917*3
    elif elevation > 1030:
        return 0.967*3
    elif elevation >= 1025:
        return 1.017*3
    else:
        return 1.1*3

def cutbackFromDCP4(reservoir, storage):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        return 0.2*4
    elif elevation >= 1050:
        return 0.533*4
    elif elevation > 1045:
        return 0.617*4
    elif elevation > 1040:
        return 0.867*4
    elif elevation > 1035:
        return 0.917*4
    elif elevation > 1030:
        return 0.967*4
    elif elevation >= 1025:
        return 1.017*4
    else:
        return 1.1*4


# The following function is used to do decision scaling for Lake Powell and Lake Mead in 6 dimensions
def MultiUncertaintiesAnalysis(reservoir1, reservoir2):
    print("Decision scaling start!")
    # set up uncertain factor range
    initSrange1 = np.arange(mininitS1, maxinitS1, steps)
    initSrange2 = np.arange(mininitS2, maxinitS2, steps)
    releaseRange1 = np.arange(minRelease1, maxRelease1, steps)
    releaseRange2 = np.arange(minRelease2, maxRelease2, steps)
    inflowRange1 = np.arange(minInflow1, maxInflow1, steps)
    inflowRange2 = np.arange(minInflow2, maxInflow2, steps)

    s1_length = len(initSrange1)
    s2_length = len(initSrange2)
    r1_length = len(releaseRange1)
    r2_length = len(releaseRange2)
    i1_length = len(inflowRange1)
    i2_length = len(inflowRange2)

    df = pd.DataFrame(columns=('InitStorage_Powell', 'Inflow_Powell', 'Release_Powell', 'InitStorage_Mead', 'Release_Mead', 'YearsToEmpty'))
    to_append = []

    # first coarse resolution, then finer resolution
    for s1 in range(0, s1_length):
        print(str(format(s1/s1_length*100, '.0f'))+'%'+" finish!")
        for s2 in  range(0, s2_length):
            for r1 in range(0, r1_length):
                for r2 in range(0, r2_length):
                    for i1 in range(0, i1_length):
                        # for i2 in range(0, i2_length):
                            for t in range(0, totalN * 12):
                                if t == 0:
                                    startStorage1 = initSrange1[s1] * MAFtoAF
                                else:
                                    startStorage1 = storageM1[t - 1]
                                inflow1 = inflowRange1[i1]/12 * MAFtoAF
                                release1 = releaseRange1[r1]/12 * MAFtoAF
                                results = reservoir1.simulationSinglePeriodGeneral(startStorage1, inflow1, release1, t)
                                storageM1[t] = results[0]
                                inflow2 = results[1]

                                if t == 0:
                                    startStorage2 = initSrange2[s2] * MAFtoAF
                                else:
                                    startStorage2 = storageM2[t - 1]
                                inflow2 = inflow2 + 0.6 / 12 * MAFtoAF
                                release2 = releaseRange2[r2] / 12 * MAFtoAF
                                resutls = reservoir2.simulationSinglePeriodGeneral(startStorage2, inflow2, release2, t)
                                storageM2[t] = results[0]

                            for t in range(0,totalN):
                                storage[t] = storageM2[t*12+11]/MAFtoAF

                            years = findYearsToEmpty(reservoir2, storageM2)

                            to_append.clear()
                            to_append.append(initSrange1[s1])
                            to_append.append(inflowRange1[i1])
                            to_append.append(releaseRange1[r1])
                            to_append.append(initSrange2[s2])
                            to_append.append(releaseRange2[r2])
                            to_append.append(years)

                            df_length = len(df)
                            df.loc[df_length] = to_append

    # pd.plotting.parallel_coordinates(df,'Name')
    # plt.show()
    print(df)
    df.to_csv('../tools/parallel.csv')
    df = pd.read_csv('../tools/parallel.csv')
    df2 = df.sort_values(by=['YearsToEmpty'], ascending=True)
    print(df2)

    fig = px.parallel_coordinates(df2, color="YearsToEmpty",
                                  dimensions=['InitStorage_Powell','Inflow_Powell','Release_Powell','InitStorage_Mead','Release_Mead','YearsToEmpty'],
                                  color_continuous_scale=px.colors.diverging.Tealrose, color_continuous_midpoint=20)
    fig.show()

    # compression_opts = dict(method='zip', archive_name='out1.csv')
    # df.to_csv('out1.zip', index=False, compression=compression_opts)

    print("Decision scaling finished!")


# The following function is used to do decision scaling for Lake Mead.
def DS_EmptyAndFull2(reservoir):
    print("Decision scaling start!")

    # set up data
    inflowRange = np.arange(minInflow2, maxInflow2, steps)
    mininitS2 = 2
    initStorageRange = np.arange(mininitS2, maxinitS2, steps)
    # demandRange = np.arange(6, 12.1, 0.1)
    # inflowRange = np.arange(6, 14.1, 0.1)

    xLength = len(initStorageRange)
    yLength = len(inflowRange)

    x = np.asarray(initStorageRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([xLength, yLength])
    z2 = np.zeros([xLength, yLength])
    z3 = np.zeros([xLength, yLength])

    deduction = 0
    for i in range(0, xLength):
        for j in range(0, yLength):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorageRange[i]*MAFtoAF
                else:
                    startStorage = storageM[t-1]

                inflow = inflowRange[j]/12*MAFtoAF
                defaultRelease2 = 6.6
                release = defaultRelease2 / 12 * MAFtoAF

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                # simulation(t, reservoir, demandRange[i], inflowRange[j])
            for t in range(0,totalN):
                storage[t] = storageM[t*12+11]/MAFtoAF

            z1[i][j] = findYearsToEmpty(reservoir)
            z2[i][j] = findYearsToFull(reservoir)
            z3[i][j] = findEndStorageBetween1025ftandFull(reservoir)

    np.round(x, 1)
    np.round(y, 1)
    np.round(z1, 0)
    np.round(z2, 0)
    np.round(z3, 0)

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

    CS = ax.contour(X, Y, Z1, levels=[1, 2, 3, 5, 10, 20, 35], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead initial Storage (MAF)')
    plt.ylabel('Lake Mead Inflow (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

    print("Decision scaling finished!")


# The following function is used to do decision scaling for Lake Mead.
def DS_EmptyAndFull3(reservoir):
    print("Decision scaling start!")

    # set up data
    releaseRange = np.arange(minRelease2, maxRelease2, steps)
    initStorageRange = np.arange(mininitS2, maxinitS2, steps)

    xLength = len(initStorageRange)
    yLength = len(releaseRange)

    x = np.asarray(initStorageRange)
    y = np.asarray(releaseRange)
    z1 = np.zeros([xLength, yLength])
    z2 = np.zeros([xLength, yLength])
    z3 = np.zeros([xLength, yLength])

    for i in range(0, xLength):
        for j in range(0, yLength):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorageRange[i]*MAFtoAF
                else:
                    startStorage = storageM[t-1]

                release = releaseRange[j]/12*MAFtoAF
                inflow = defaultInflow2 / 12 * MAFtoAF

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                # simulation(t, reservoir, demandRange[i], inflowRange[j])
            for t in range(0,totalN):
                storage[t] = storageM[t*12+11]/MAFtoAF

            z1[i][j] = findYearsToEmpty(reservoir)
            z2[i][j] = findYearsToFull(reservoir)
            z3[i][j] = findEndStorageBetween1025ftandFull(reservoir)

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

    CS = ax.contour(X, Y, Z1, levels=[5, 10, 20, 35], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead initial Storage (MAF)')
    plt.ylabel('Lake Mead Release (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

    print("Decision scaling finished!")


# The following function is used to do decision scaling for Lake Mead.
def DS_EmptyAndFullPowellMead2(reservoir1, reservoir2):
    print("Decision scaling start!")

    # set up data
    releaseRange2 = np.arange(minRelease2, maxRelease2, steps)
    releaseRange1 = np.arange(minRelease1, maxRelease1, steps)

    xLength = len(releaseRange2)
    yLength = len(releaseRange1)

    x = np.asarray(releaseRange2)
    y = np.asarray(releaseRange1)
    z1 = np.zeros([xLength, yLength])
    z2 = np.zeros([xLength, yLength])
    z3 = np.zeros([xLength, yLength])

    for i in range(0, xLength):
        for j in range(0, yLength):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = reservoir1.initStorage
                else:
                    startStorage = storageM1[t-1]

                inflow1 = defaultInflow1/12*MAFtoAF
                release1 = releaseRange1[j]/12*MAFtoAF
                inflow2 = reservoir1.simulationSinglePeriodGeneral(startStorage, inflow1, release1, t)[1]

                if t == 0:
                    startStorage = reservoir2.initStorage
                else:
                    startStorage = storageM2[t-1]
                inflow2 = inflow2 + 0.2/12*MAFtoAF
                release2 = releaseRange2[i]/12*MAFtoAF
                storageM2[t] = reservoir2.simulationSinglePeriodGeneral(startStorage, inflow2, release2, t)[0]

                # simulation(t, reservoir, demandRange[i], inflowRange[j])
            for t in range(0,totalN):
                storage[t] = storageM2[t*12+11]/MAFtoAF

            z1[i][j] = findYearsToEmpty(reservoir2)
            z2[i][j] = findYearsToFull(reservoir2)
            z3[i][j] = findEndStorageBetween1025ftandFull(reservoir2)

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

    CS = ax.contour(X, Y, Z1, levels=[5, 10, 20, 35], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead Release (MAF/year)')
    plt.ylabel('Lake Powell Release (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

    print("Decision scaling finished!")


# The following function is used to do decision scaling for Lake Powell and Lake Mead in 3 dimensions
def MultiUncertaintiesAnalysis_3d(reservoir1, reservoir2):
    print("Decision scaling start!")
    # set up uncertain factor range
    # combined Powell and Mead storage
    initSrange = np.arange(totalMinIntiS, totalMaxIntiS, steps)
    # Release from Mead
    releaseRange2 = np.arange(minRelease2, maxRelease2, steps/2)
    # inflow to Powell
    inflowRange1 = np.arange(minInflow1, maxInflow1, steps/2)

    s_length = len(initSrange)
    # 2 means downstream reservoir (Lake Mead)
    r2_length = len(releaseRange2)
    # 1 means upstream reservoir (Lake Powell)
    i1_length = len(inflowRange1)
    # intervening inflow (intervening inflow + Virgin river) in maf/yr
    # Wang and Schmidt. (2020) Stream flow and Losses of the Colorado River in the Southern Colorado Plateau
    interveningInflow = 0.9

    df = pd.DataFrame(columns=('InitStorage(Powell&Mead)', 'Inflow_Powell', 'Release_Mead', 'YearsTo12MAF'))
    to_append = []

    # first coarse resolution, then finer resolution
    for s in range(0, s_length):
        print(str(format(s / s_length * 100, '.0f')) + '%' + " finish!")
        for i1 in range(0, i1_length):
            for r2 in range(0, r2_length):
                # for i2 in range(0, i2_length):
                for t in range(0, totalN * 12):
                    if t == 0:
                        startStorage1 = initSrange[s]/2 * MAFtoAF
                    else:
                        # storageM means monthly storage
                        startStorage1 = storageM1[t - 1]

                    # these two are determined once i1 and r2 are determined
                    inflow1 = inflowRange1[i1] / 12 * MAFtoAF
                    release2 = releaseRange2[r2] / 12 * MAFtoAF

                    # Equalization, not perfect because evaporation will not be the same for the same reservoir storage
                    # Experiment 1: if inflow to Powell is 10 maf, release from Mead is 6 maf, interveningInflow = 1 maf
                    # The combined storage will increase 5, 2.5 by each. Release from Powell should be (10+6-1)/2
                    # Experiment 2: if inflow to Powell is 10 maf, release from Mead is 10 maf, interveningInflow = 1 maf
                    # The combined storage will increase 1, 0.5 by each. Release from Powell should be (10+10-1)/2
                    # Experiment 3: if inflow to Powell is 4, release from Mead is 12, interveningInflow = 1 maf
                    # The combined storage will decrease by 7, 3.5 by each. Release from Powell should be (4+12-1)/2
                    release1 = (inflow1 + release2 - interveningInflow) / 2 / 12 * MAFtoAF
                    results = reservoir1.simulationSinglePeriodGeneral(startStorage1, inflow1, release1, t)
                    storageM1[t] = results[0]
                    inflow2 = results[1]

                    if t == 0:
                        startStorage2 = initSrange[s]/2 * MAFtoAF
                    else:
                        startStorage2 = storageM2[t - 1]
                    inflow2 = inflow2 + interveningInflow / 12 * MAFtoAF
                    results = reservoir2.simulationSinglePeriodGeneral(startStorage2, inflow2, release2, t)
                    storageM2[t] = results[0]

                    # print(str(t)+" "+str(storageM1[t])+" "+str(storageM2[t]))

                CombinedStorage[t] = storageM1[t] + storageM2[t]

                years = findYearsTo12maf(CombinedStorage)
                # years = findYearsToEmpty()

                to_append.clear()
                to_append.append(initSrange[s])
                to_append.append(inflowRange1[i1])
                to_append.append(releaseRange2[r2])
                to_append.append(years)

                df_length = len(df)
                df.loc[df_length] = to_append

    # pd.plotting.parallel_coordinates(df,'Name')
    # plt.show()
    print(df)
    df.to_csv('../tools/parallel.csv')
    df = pd.read_csv('../tools/parallel.csv')
    df2 = df.sort_values(by=['YearsTo12MAF'], ascending=False)
    print(df2)

    fig = px.parallel_coordinates(df2, color="YearsTo12MAF",
                                  dimensions=['InitStorage(Powell&Mead)','Inflow_Powell','Release_Mead','YearsTo12MAF'],
                                  color_continuous_scale='reds_r', color_continuous_midpoint=20)

    # px.colors.diverging.Tealrose
    fig.show()

    # compression_opts = dict(method='zip', archive_name='out1.csv')
    # df.to_csv('out1.zip', index=False, compression=compression_opts)

    print("Decision scaling finished!")