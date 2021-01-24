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

resultPathAndName = "../results/LakeMeadDSResults.pdf"

totalN = 40  # PLANNING HORIZON, 100 years, no need to be 100 years, maybe 40 years.
storageM = np.zeros([totalN*12])  # reservoir storage in MAF
storageM1 = np.zeros([totalN*12])  # reservoir storage in MAF
storageM2 = np.zeros([totalN*12])  # reservoir storage in MAF

storage = np.zeros([totalN])  # reservoir storage in MAF
# storage = np.zeros([totalN])  # reservoir storage in MAF
MAFtoAF = 1000000

# ==== Change parameters here ====
# steps 0.2 is used for two dimensional analysis
# steps = 0.2
# steps 1 is used for three dimensional analysis
steps = 1

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
totalMaxIntiS = 40

# policy
deductionPolicy = 0

# The following function is used to do decision scaling for Lake Mead.
def DS_EmptyAndFull(reservoir):
    print("Decision scaling start!")

    # set up data
    releaseRange = np.arange(minRelease2, maxRelease2, steps)
    inflowRange = np.arange(minInflow2, maxInflow2, steps)
    # initStorage = reservoir.initStorage
    initStorage = 6 * MAFtoAF

    xLength = len(releaseRange)
    yLength = len(inflowRange)

    x = np.asarray(releaseRange)
    y = np.asarray(inflowRange)
    z1 = np.zeros([xLength, yLength])
    z2 = np.zeros([xLength, yLength])
    z3 = np.zeros([xLength, yLength])

    deduction = 0
    for i in range(0, xLength):
        print(str(format(i / xLength * 100, '.0f')) + '%' + " finish!")

        for j in range(0, yLength):
            for t in range(0,totalN*12):
                if t == 0:
                    startStorage = initStorage
                else:
                    startStorage = storageM[t-1]

                month = reservoir.para.determineMonth(t)
                # if month == reservoir.JAN:
                #     if deductionPolicy == 0:
                #         deduction = cutbackFromDCP(reservoir, startStorage)/12.0*MAFtoAF
                #     if deductionPolicy == 1:
                #         deduction = cutbackFromDCP2(reservoir, startStorage)/12.0*MAFtoAF
                #     if deductionPolicy == 2:
                #         deduction = cutbackFromDCP3(reservoir, startStorage)/12.0*MAFtoAF

                inflow = inflowRange[j]/12*MAFtoAF
                release = releaseRange[i]/12*MAFtoAF

                storageM[t] = reservoir.simulationSinglePeriodGeneral(startStorage, inflow, release, t)[0]

                # simulation(t, reservoir, demandRange[i], inflowRange[j])
            for t in range(0,totalN):
                storage[t] = storageM[t*12+11]/MAFtoAF

            z1[i][j] = findYearsToDry(reservoir)
            # z1[i][j] = findYearsTo1025(reservoir)
            z2[i][j] = findYearsToFill(reservoir)
            z3[i][j] = findStaticStorage()

    X, Y = np.meshgrid(x, y)
    Z1 = np.transpose(z1)
    Z2 = np.transpose(z2)
    Z3 = np.transpose(z3)

    fig, ax = plt.subplots()

    CS = ax.contour(X, Y, Z2, levels=[5, 10, 20, 30], colors="#024979")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to full pool (Unit: years)")

    CS = ax.contour(X, Y, Z3, levels=[4, 8, 12, 16, 20, 24], colors='#44A5C2')
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Static reservoir storage (Unit: MAF)")

    CS = ax.contour(X, Y, Z1, levels=[1, 2, 3, 4, 5, 10, 20, 35, 40], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    # CS.collections[0].set_label("Years to 1025 ft (Unit: years)")
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    ax.hlines(y=9.3, xmin=3, xmax=9.6, linewidth=1, color='r', linestyles = 'dashed')
    ax.hlines(y=7+1, xmin=3, xmax=9.6, linewidth=1, color='r', linestyles = 'dashed')
    ax.hlines(y=5.7+1, xmin=3, xmax=9.6, linewidth=1, color='r', linestyles = 'dashed')
    ax.vlines(x=9.6-1.4, ymin=3, ymax=9.3, linewidth=1, color='r', linestyles = 'dashed')
    ax.vlines(x=9.6, ymin=3, ymax=9.3, linewidth=1, color='r', linestyles = 'dashed')

    ax.vlines(x=7.5, ymin=3, ymax=5.7+1, linewidth=1, color='r', linestyles = 'dotted')
    ax.vlines(x=6.4, ymin=3, ymax=5.7+1, linewidth=1, color='r', linestyles = 'dotted')


    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead Release(MAF/year)')
    plt.ylabel('Lake Mead Inflow (MAF/year)')
    # plt.title('How long will Lake Mead go dry or get full?')

    plt.savefig(resultPathAndName, dpi=600, format='pdf')
    plt.show()

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

                            years = findYearsToDry(reservoir2)

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
    r2_length = len(releaseRange2)
    i1_length = len(inflowRange1)
    interveningInflow = 0.6

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
                        release1 = releaseRange2[r2] / 12 * MAFtoAF
                    else:
                        startStorage1 = storageM1[t - 1]
                        if storageM1[t - 1] > storageM2[t - 1]:
                            release1 = releaseRange2[r2] / 12 * MAFtoAF
                        else:
                            release1 = releaseRange2[r2]/ 2 / 12 * MAFtoAF

                    inflow1 = inflowRange1[i1] / 12 * MAFtoAF
                    # release1 = (releaseRange2[r2]/2+1) / 12 * MAFtoAF
                    results = reservoir1.simulationSinglePeriodGeneral(startStorage1, inflow1, release1, t)
                    storageM1[t] = results[0]
                    inflow2 = results[1]

                    if t == 0:
                        startStorage2 = initSrange[s]/2 * MAFtoAF
                    else:
                        startStorage2 = storageM2[t - 1]
                    inflow2 = inflow2 + interveningInflow / 12 * MAFtoAF
                    release2 = releaseRange2[r2] / 12 * MAFtoAF
                    results = reservoir2.simulationSinglePeriodGeneral(startStorage2, inflow2, release2, t)
                    storageM2[t] = results[0]

                    # print(str(t)+" "+str(storageM1[t])+" "+str(storageM2[t]))

                for t in range(0, totalN):
                    storage[t] = (storageM1[t * 12 + 11] + storageM2[t * 12 + 11]) / MAFtoAF

                # years = findYearsTo12MAF()
                years = findYearsToEmpty()

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

def DS_EmptyAndFullPowellMead(reservoir1, reservoir2):
    print("Decision scaling start!")

    # set up data
    releaseRange2 = np.arange(minRelease2, maxRelease2, steps)
    inflowRange1 = np.arange(minInflow1, maxInflow1, steps)

    xLength = len(releaseRange2)
    yLength = len(inflowRange1)

    x = np.asarray(releaseRange2)
    y = np.asarray(inflowRange1)
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

                inflow1 = inflowRange1[j]/12*MAFtoAF
                release1 = defaultRelease1/12*MAFtoAF
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

            z1[i][j] = findYearsToDry(reservoir2)
            z2[i][j] = findYearsToFill(reservoir2)
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

    CS = ax.contour(X, Y, Z1, levels=[5, 10, 20, 35], colors="#FFAE49")
    ax.clabel(CS, inline=1, fmt='%1.0f', fontsize=8)
    CS.collections[0].set_label("Years to dead pool (Unit: years)")

    plt.legend(loc='upper left')

    plt.xlabel('Lake Mead Release (MAF/year)')
    plt.ylabel('Lake Powell Inflow (MAF/year)')
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

            z1[i][j] = findYearsToDry(reservoir2)
            z2[i][j] = findYearsToFill(reservoir2)
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

# how to do combined simulation.

# policy: cutback from Drought contingency plan for Lake Mead for decision scaling
def cutbackFromDCP(reservoir, storage):
    elevation = reservoir.volume_to_elevation(storage)

    if elevation > 1090:
        return 0
    elif elevation > 1075:
        return 0.2
    elif elevation >= 1050:
        return 0.533
    elif elevation > 1045:
        return 0.617
    elif elevation > 1040:
        return 0.867
    elif elevation > 1035:
        return 0.917
    elif elevation > 1030:
        return 0.967
    elif elevation >= 1025:
        return 1.017
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

def findYearsTo12MAF():
    for i in range(0, totalN):
      if storage[i] <= 12: # how many years to dry
          return i + 1

    return totalN

def findYearsToEmpty():
    for i in range(0, totalN):
      if storage[i] <= 0: # how many years to dry
          return i + 1

    return totalN

def findYearsToDry(reservoir):
    for i in range(0, totalN):
      if storage[i] <= reservoir.minStorage/MAFtoAF: # how many years to dry
          return i + 1

    return totalN


def findYearsTo1025(reservoir):
    for i in range(0, totalN):
      if storage[i] <= reservoir.elevation_to_volume(1025)/MAFtoAF: # how many years to 1025 feet
          return i + 1

    return totalN

def findYearsToFill(reservoir):
    for i in range(0, totalN):
      if storage[i] >= reservoir.maxStorage/MAFtoAF: # how many years to fill
          return i + 1

def findStaticStorage():
    sum = 0
    for i in range(totalN - 5, totalN):
        if storage[i] <= 0:
            return 0
        sum = sum + storage[i]
    ave = sum / 5

    return round(ave)

# not use
def setParameters(minDemand,maxDemand,minInflow,maxInflow,reservoir):

    # 1. set yearly data, disaggregate into monthly data
    # 2. do simulation
    demandRange = np.arange(minDemand, maxDemand, 1)
    inflowRange = np.arange(minInflow, maxInflow, 1)

    reservoir.simulationSinglePeriod()

    return