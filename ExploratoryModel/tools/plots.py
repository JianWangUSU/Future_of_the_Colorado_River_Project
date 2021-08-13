import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import figaspect
from textwrap import wrap

# result style, scientific notation
def formatnum(x, pos):
    return '$%.0f$x$10^{6}$' % (x/1000000)
formatter = FuncFormatter(formatnum)




def subplotstest():
    x1 = np.linspace(0.0, 5.0)
    x2 = np.linspace(0.0, 2.0)

    y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
    y2 = np.cos(2 * np.pi * x2)

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle('A tale of 2 subplots')

    ax1.plot(x1, y1, 'o-')
    ax1.set_ylabel('Damped oscillation')

    ax2.plot(x2, y2, '.-')
    ax2.set_xlabel('time (s)')
    ax2.set_ylabel('Undamped')

    plt.show()

def plot_Elevations_Flows_CRSS_Exploratory_Powell(x, y1crss, y2crss, y3crss, y4crss, y1, y2, y3, y4, title):
    EleRange = [3370, 3710]
    StrRange = [0, 30000000]

    plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, StrRange)
    # plot_Elevations_CRSS_Exploratory(x, y4crss, y1crss, y4, y1, title, EleRange, StrRange)
    # plot_Elevations_CRSS_Exploratory_Gap(x, y1crss-y1, title)
    # title = "inflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y2crss-y2, title)
    # title = "outflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y3crss-y3, title)

def plot_Elevations_Flows_CRSS_Exploratory_Mead(x, y1crss, y2crss, y3crss, y4crss, y1, y2, y3, y4, title):
    EleRange = [895, 1250]
    StrRange = [0, 30000000]
    plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, StrRange)
    # plot_Elevations_CRSS_Exploratory(x, y4crss, y1crss, y4, y1, title, EleRange, StrRange)
    # plot_Elevations_CRSS_Exploratory_Gap(x, y1crss-y1, title)
    # title = "inflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y2crss-y2, title)
    # title = "outflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y3crss-y3, title)

def plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, EleRange):

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig.suptitle(title)

    ax1.plot(x, y1, color='blue', label='Exploratory')
    ax1.plot(x, y1crss, color='red',label='CRSS',linewidth=1)
    ax1.set_ylabel('Storage (acre-feet)')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.set_ylim(EleRange)

    ax2.plot(x, y2, color='blue',label='Exploratory')
    ax2.plot(x, y2crss, color='red',label='CRSS',linewidth=1)
    ax2.set_ylabel('Inflow (acre-feet)')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.set_ylim([0, 8000000])

    ax3.plot(x, y3, color='blue',label='Exploratory')
    ax3.plot(x, y3crss, color='red',label='CRSS',linewidth=1)
    ax3.set_ylabel('Outflow (acre-feet)')
    ax3.set_ylim([0, 8000000])

    ax3.set_xlabel('time')
    ax3.yaxis.set_major_formatter(formatter)

    plt.legend()
    plt.show()

# ele means elevation, str means storage
def plot_Elevations_CRSS_Exploratory(x, yEleCRSS, yStrCRSS, yEelvationEx, yStrEx, title, EleRange, strRange):

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle(title)

    ax1.plot(x, yEelvationEx, color='blue', label='Exploratory')
    ax1.plot(x, yEleCRSS, color='red',label='CRSS',linewidth=1)
    ax1.set_ylabel('Elevation (feet)')
    ax1.set_ylim(EleRange)
    ax1.set_xlabel('time')

    ax2.plot(x, yStrEx, color='blue',label='Exploratory')
    ax2.plot(x, yStrCRSS, color='red',label='CRSS',linewidth=1)
    ax2.set_ylabel('Storage (acre-feet)')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.set_ylim(strRange)

    plt.legend()
    plt.show()

def plot_Elevations_CRSS_Exploratory_Gap(x, y1, title):

    fig, (ax1) = plt.subplots(1, 1)
    fig.suptitle(title)

    ax1.plot(x, y1, color='blue', label='gap')
    ax1.set_ylabel('Elevation (feet)')
    ax1.set_xlabel('time')

    plt.legend()
    plt.show()

def plot_Flow_CRSS_Exploratory_Gap(x, y1, title):

    fig, (ax1) = plt.subplots(1, 1)
    fig.suptitle(title)

    ax1.plot(x, y1, color='blue', label='gap')
    ax1.set_ylabel('volumen (acre-feet)')
    ax1.set_xlabel('time')

    plt.legend()
    plt.show()

def Equalization(x, y1crss, y1, title):

    fig, (ax1) = plt.subplots(1, 1)
    fig.suptitle(title)

    ax1.plot(x, y1, color='blue', label='Exploratory')
    ax1.plot(x, y1crss, color='red',label='CRSS',linewidth=1)
    ax1.set_ylabel('P_Storage/P_maxStorage - M_Storage/M_maxStorage')
    # ax1.set_ylim([0,1])
    ax1.set_xlabel('time')

    plt.legend()
    plt.show()

def plot_Elevations_Flows_CRSS_Exploratory_backUP(x, y1crss, y2crss, y3crss, title):

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig.suptitle(title)

    ax1.plot(x, y1crss, color='blue')
    ax1.set_ylabel('Elevation (feet)')
    ax1.set_ylim([3490, 3700])

    ax2.plot(x, y2crss, color='green')
    ax2.set_ylabel('Inflow (acre-feet)')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.set_ylim([0, 8000000])

    ax3.plot(x, y3crss, color='red')
    ax3.set_ylabel('Outflow (acre-feet)')
    ax3.set_ylim([0, 8000000])

    ax3.set_xlabel('time')
    ax3.yaxis.set_major_formatter(formatter)

    plt.show()

def dottyPlotforAveReleaseTempforEachInflow(data1, data2, data3, labels, title, plot, showYtitle):
    [lenYear,numPoints] = data1.shape

    totalEmpty = sum(range(0, numPoints))

    x1 = np.zeros([lenYear*numPoints-totalEmpty])
    y1 = np.zeros([lenYear*numPoints-totalEmpty])
    x2 = np.zeros([lenYear*numPoints-totalEmpty])
    y2 = np.zeros([lenYear*numPoints-totalEmpty])
    x3 = np.zeros([lenYear*numPoints-totalEmpty])
    y3 = np.zeros([lenYear*numPoints-totalEmpty])
    x17 = np.zeros([lenYear])
    y17 = np.zeros([lenYear])
    x20 = np.zeros([lenYear])
    y20 = np.zeros([lenYear])
    index = 0
    for i in range(lenYear):
        for j in range(numPoints-i):
            x1[index] = i+1
            y1[index] = data1[i][j]
            x2[index] = i+1
            y2[index] = data2[i][j]
            x3[index] = i+1
            y3[index] = data3[i][j]
            index = index + 1

        x17[i] = i+1
        y17[i] = 17
        x20[i] = i+1
        y20[i] = 20

    colors1 = '#628FB6'
    colors2 = "red"
    colors3 = '#E7BA41'

    plot.scatter(x1, y1, s = 8, alpha=1, c=colors1, label = labels[0])
    plot.scatter(x2, y2, s = 8, alpha=1, c=colors2, label = labels[1])
    plot.scatter(x3, y3, s = 8, alpha=1, c=colors3, label = labels[2])
    plot.plot(x17,y17,c="black")
    plot.plot(x20,y20,c="black")

    plot.title(title, size = 18)
    plot.tick_params(axis='both', which='major', labelsize=14)
    plot.xlabel("Duration of Years", size = 14)
    if showYtitle:
        plot.ylabel("Average Summer Temperature\n across all inflow traces (°C)", size = 14)
        plot.legend(prop={'size': 14})
    plot.ylim(5, 35)

    # plt.show()

def dottyPlotforAveReleaseTemp(data1, title, plot, color):
    [lenYear,numPoints] = data1.shape

    totalEmpty = sum(range(0, numPoints))

    x1 = np.zeros([lenYear*numPoints-totalEmpty])
    y1 = np.zeros([lenYear*numPoints-totalEmpty])

    x17 = np.zeros([lenYear])
    y17 = np.zeros([lenYear])
    x20 = np.zeros([lenYear])
    y20 = np.zeros([lenYear])
    index = 0
    for i in range(lenYear):
        for j in range(numPoints-i):
            x1[index] = i+1
            y1[index] = data1[i][j]
            index = index + 1

        x17[i] = i+1
        y17[i] = 17
        x20[i] = i+1
        y20[i] = 20

    plot.scatter(x1, y1, s = 2, alpha=1, c=color)

    plt.plot(x17,y17,c="black")
    plt.plot(x20,y20,c="black")

    plot.xlabel("Years",size = 7)
    plot.ylabel("Temperature (°C)", size = 7)
    plot.ylim(5,35)
    plot.title(title, size = 10)
    plot.tick_params(axis='both', which='major', labelsize=7)


def dottyPlotforAveReleaseTemp31(data1, data2, data3, data4, data5, data6, data7, data8, data9, lables, titleForEachInflow):
    plot = plt
    plot.rcParams['figure.dpi'] = 600
    w, h = figaspect(1 / 3)
    plot.figure(figsize=(w, h))

    plot.subplot(1, 3, 1)
    dottyPlotforAveReleaseTempforEachInflow(data1, data2, data3, lables, titleForEachInflow[0], plot, True)
    plot.subplot(1, 3, 2)
    dottyPlotforAveReleaseTempforEachInflow(data4, data5, data6, lables, titleForEachInflow[1], plot, False)
    plot.subplot(1, 3, 3)
    dottyPlotforAveReleaseTempforEachInflow(data7, data8, data9, lables, titleForEachInflow[2], plot, False)

    plot.show()

def dottyPlotforAveReleaseTempRange31(data1, data2, data3, lables, titleForEachInflow):
    plot = plt
    plot.rcParams['figure.dpi'] = 600
    w, h = figaspect(1 / 3)
    plot.figure(figsize=(w, h))

    plot.subplot(1, 3, 1)
    dottyPlotforReleaseTempRangeForEachInflow(data1[0], data1[1], data1[2], lables, titleForEachInflow[0], plot, True)
    plot.subplot(1, 3, 2)
    dottyPlotforReleaseTempRangeForEachInflow(data2[0], data2[1], data2[2], lables, titleForEachInflow[1], plot, False)
    plot.subplot(1, 3, 3)
    dottyPlotforReleaseTempRangeForEachInflow(data3[0], data3[1], data3[2], lables, titleForEachInflow[2], plot, False)

    plot.show()

def dottyPlotforAveReleaseTemp33(data1, data2, data3, data4, data5, data6, data7, data8, data9, titles):
    plot = plt
    plt.rcParams['figure.dpi'] = 600

    colors1 = '#628FB6'
    colors2 = "red"
    colors3 = '#E7BA41'

    plot.subplot(3, 3, 1)
    dottyPlotforAveReleaseTemp(data1, titles[0], plot, colors1)
    plot.subplot(3, 3, 2)
    dottyPlotforAveReleaseTemp(data2, titles[1], plot, colors2)
    plot.subplot(3, 3, 3)
    dottyPlotforAveReleaseTemp(data3, titles[2], plot, colors3)
    plot.subplot(3, 3, 4)
    dottyPlotforAveReleaseTemp(data4, titles[3], plot, colors1)
    plot.subplot(3, 3, 5)
    dottyPlotforAveReleaseTemp(data5, titles[4], plot, colors2)
    plot.subplot(3, 3, 6)
    dottyPlotforAveReleaseTemp(data6, titles[5], plot, colors3)
    plot.subplot(3, 3, 7)
    dottyPlotforAveReleaseTemp(data7, titles[6], plot, colors1)
    plot.subplot(3, 3, 8)
    dottyPlotforAveReleaseTemp(data8, titles[7], plot, colors2)
    plot.subplot(3, 3, 9)
    dottyPlotforAveReleaseTemp(data9, titles[8], plot, colors3)

    plot.show()


def dottyPlotforReleaseTempRangeForEachInflow(data1,data2,data3,labels,title,plot,showYtitle):
    [inflowTrace, lenYear, numPoints] = data1.shape

    totalEmpty = sum(range(0, numPoints))

    x1 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    y1 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    x2 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    y2 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    x3 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    y3 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    x17 = np.zeros([lenYear])
    y17 = np.zeros([lenYear])
    x20 = np.zeros([lenYear])
    y20 = np.zeros([lenYear])

    for i in range(inflowTrace):
        index = 0
        for y in range(lenYear):
            for j in range(numPoints-y):
                x1[i][index] = y+1
                y1[i][index] = data1[i][y][j]
                x2[i][index] = y+1
                y2[i][index] = data2[i][y][j]
                x3[i][index] = y+1
                y3[i][index] = data3[i][y][j]
                index = index + 1

            if i == 0:
                x17[y] = y+1
                y17[y] = 17
                x20[y] = y+1
                y20[y] = 20

    colors1 = '#628FB6'
    colors2 = "red"
    colors3 = '#E7BA41'

    for i in range(inflowTrace):
        if i == 0:
            plt.scatter(x1[i], y1[i], s = 8, alpha=1, c=colors1, label = labels[0])
            plt.scatter(x2[i], y2[i], s = 8, alpha=1, c=colors2, label = labels[1])
            plt.scatter(x3[i], y3[i], s = 8, alpha=1, c=colors3, label = labels[2])
        else:
            plt.scatter(x1[i], y1[i], s=8, alpha=1, c=colors1)
            plt.scatter(x2[i], y2[i], s=8, alpha=1, c=colors2)
            plt.scatter(x3[i], y3[i], s=8, alpha=1, c=colors3)

    plot.plot(x17,y17,c="black")
    plot.plot(x20,y20,c="black")

    plot.title(title, size=18)
    plot.tick_params(axis='both', which='major', labelsize=14)
    plot.xlabel("Years", size=14)
    if showYtitle:
        plot.ylabel("Average Summer Temperature\n across all inflow traces (°C)", size=14)
        plot.legend(prop={'size': 14})
    plot.ylim(5, 35)

    # plt.show()

def dottyPlotforReleaseTempRange(data1,title,plot,color):
    [inflowTrace, lenYear, numPoints] = data1.shape

    totalEmpty = sum(range(0, numPoints))

    x1 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])
    y1 = np.zeros([inflowTrace, lenYear*numPoints-totalEmpty])

    x17 = np.zeros([lenYear])
    y17 = np.zeros([lenYear])
    x20 = np.zeros([lenYear])
    y20 = np.zeros([lenYear])

    for i in range(inflowTrace):
        index = 0
        for y in range(lenYear):
            for j in range(numPoints-y):
                x1[i][index] = y+1
                y1[i][index] = data1[i][y][j]
                index = index + 1

            if i == 0:
                x17[y] = y+1
                y17[y] = 17
                x20[y] = y+1
                y20[y] = 20

    for i in range(inflowTrace):
        plot.scatter(x1[i], y1[i], s=2, alpha=1, c=color)

    # plot.plot(x17,y17,c="black")
    # plot.plot(x20,y20,c="black")

    plot.xlabel("Years",size = 7)
    plot.ylabel("Temperature (°C)", size = 7)
    plot.ylim(5,35)
    plot.title(title, size = 10)
    plot.tick_params(axis='both', which='major', labelsize=7)


# dotty plots
def dottyPlotforReleaseTempRange33(results1, results2, results3, titles):
    data1 = results1[0]
    data2 = results1[1]
    data3 = results1[2]
    data4 = results2[0]
    data5 = results2[1]
    data6 = results2[2]
    data7 = results3[0]
    data8 = results3[1]
    data9 = results3[2]

    plot = plt
    plt.rcParams['figure.dpi'] = 600  # 分辨率

    colors1 = '#628FB6'
    colors2 = "red"
    colors3 = '#E7BA41'

    plot.subplot(3, 3, 1)
    dottyPlotforReleaseTempRange(data1, titles[0], plot, colors1)
    plot.subplot(3, 3, 2)
    dottyPlotforReleaseTempRange(data2, titles[1], plot, colors2)
    plot.subplot(3, 3, 3)
    dottyPlotforReleaseTempRange(data3, titles[2], plot, colors3)
    plot.subplot(3, 3, 4)
    dottyPlotforReleaseTempRange(data4, titles[3], plot, colors1)
    plot.subplot(3, 3, 5)
    dottyPlotforReleaseTempRange(data5, titles[4], plot, colors2)
    plot.subplot(3, 3, 6)
    dottyPlotforReleaseTempRange(data6, titles[5], plot, colors3)
    plot.subplot(3, 3, 7)
    dottyPlotforReleaseTempRange(data7, titles[6], plot, colors1)
    plot.subplot(3, 3, 8)
    dottyPlotforReleaseTempRange(data8, titles[7], plot, colors2)
    plot.subplot(3, 3, 9)
    dottyPlotforReleaseTempRange(data9, titles[8], plot, colors3)

    plot.show()

def dottyPlotforReleaseTempRangePercentage(data1,title,plot,showLegend):
    [inflowTrace, lenYear, numPoints] = data1.shape

    x17 = np.zeros([lenYear])
    y17 = np.zeros([lenYear])
    x20 = np.zeros([lenYear])
    y20 = np.zeros([lenYear])

    labels = ["100th Pctile","75th Pctile","50th Pctile","25th Pctile","0th Pctile"]
    colors = ["#f48c06","#e85d04","#d00000","#9d0208","#6a040f"]
    percent = [0,25,50,75,100]

    # labels = ["100th Pctile","90th Pctile","80th Pctile","70th Pctile","60th Pctile","50th Pctile","40th Pctile"
    #     ,"30th Pctile","20th Pctile","10th Pctile","0th Pctile"]
    # colors = ["#03071e","#370617","#6a040f","#9d0208","#d00000","#dc2f02","#e85d04","#f48c06","#faa307","#ffba08","#ffea00"]
    # percent = [0,10,20,30,40,50,60,70,80,90,100]

    xp = np.zeros([len(labels),lenYear])
    yp = np.zeros([len(labels),lenYear])

    for y in range(lenYear):
        templist = []
        for i in range(inflowTrace):
            for j in range(numPoints - y):
                templist.append(data1[i][y][j])

        for p in range(len(labels)):
            xp[p][y] = y + 1
            yp[p][y] = np.percentile(np.array(templist), percent[p])

            if y == 0 and percent[p] == 100:
                print(yp[p][y])

        x17[y] = y + 1
        y17[y] = 17
        x20[y] = y + 1
        y20[y] = 20

    for p in range(len(labels)):
        if p == 2:
            plt.plot(xp[p], yp[p], label=labels[p], c=colors[p], linewidth=2)
        else:
            plt.plot(xp[p], yp[p], label=labels[p], c=colors[p], linewidth=0.5)

    # plt.plot(x17, y17, c="black")
    # plt.plot(x20, y20, c="black")

    plot.xlabel("Duration of Years",size = 7)
    plot.ylabel("Summer Release \nTemperature (°C)", size = 7)
    plot.ylim(5,35)
    plot.title(title, size = 7)
    if showLegend:
        plot.legend(prop={'size': 4})
    plot.tick_params(axis='both', which='major', labelsize=7)


# 3*3 plot
def ReleaseTempRangePercentage33(results1, results2, results3, titles):
    data1 = results1[0]
    data2 = results1[1]
    data3 = results1[2]
    data4 = results2[0]
    data5 = results2[1]
    data6 = results2[2]
    data7 = results3[0]
    data8 = results3[1]
    data9 = results3[2]

    plot = plt
    plt.rcParams['figure.dpi'] = 600  # 分辨率

    plot.subplot(3, 3, 1)
    dottyPlotforReleaseTempRangePercentage(data1,titles[0],plot,True)
    plot.subplot(3, 3, 2)
    dottyPlotforReleaseTempRangePercentage(data4,titles[3],plot,False)
    plot.subplot(3, 3, 3)
    dottyPlotforReleaseTempRangePercentage(data7,titles[6],plot,False)
    plot.subplot(3, 3, 4)
    dottyPlotforReleaseTempRangePercentage(data2,titles[1],plot,False)
    plot.subplot(3, 3, 5)
    dottyPlotforReleaseTempRangePercentage(data5,titles[4],plot,False)
    plot.subplot(3, 3, 6)
    dottyPlotforReleaseTempRangePercentage(data8,titles[7],plot,False)
    plot.subplot(3, 3, 7)
    dottyPlotforReleaseTempRangePercentage(data3,titles[2],plot,False)
    plot.subplot(3, 3, 8)
    dottyPlotforReleaseTempRangePercentage(data6,titles[5],plot,False)
    plot.subplot(3, 3, 9)
    dottyPlotforReleaseTempRangePercentage(data9,titles[8],plot,False)

    # plot.subplot(3, 3, 1)
    # dottyPlotforReleaseTempRangePercentage(data1,titles[0],plot,True)
    # plot.subplot(3, 3, 2)
    # dottyPlotforReleaseTempRangePercentage(data2,titles[1],plot,False)
    # plot.subplot(3, 3, 3)
    # dottyPlotforReleaseTempRangePercentage(data3,titles[2],plot,False)
    # plot.subplot(3, 3, 4)
    # dottyPlotforReleaseTempRangePercentage(data4,titles[3],plot,False)
    # plot.subplot(3, 3, 5)
    # dottyPlotforReleaseTempRangePercentage(data5,titles[4],plot,False)
    # plot.subplot(3, 3, 6)
    # dottyPlotforReleaseTempRangePercentage(data6,titles[5],plot,False)
    # plot.subplot(3, 3, 7)
    # dottyPlotforReleaseTempRangePercentage(data7,titles[6],plot,False)
    # plot.subplot(3, 3, 8)
    # dottyPlotforReleaseTempRangePercentage(data8,titles[7],plot,False)
    # plot.subplot(3, 3, 9)
    # dottyPlotforReleaseTempRangePercentage(data9,titles[8],plot,False)

    plot.show()

# not used
def box_whisker(reservoir, crssElevation, adpElevation):
    data_ADP = np.zeros([20, 113])
    data_CRSS = np.zeros([20, 113])

    for i in range(reservoir.inflowTraces):
        for t in range(20):
            data_CRSS[t][i] = crssElevation[i][2*t*12 + 11]
            data_ADP[t][i] = adpElevation[i][2*t*12 + 11]

    # ticks = [' ',' ',' ',' ','2025',
    #          ' ',' ',' ',' ','2030',
    #          ' ',' ',' ',' ','2035',
    #          ' ',' ',' ',' ','2040',
    #          ' ',' ',' ',' ','2045',
    #          ' ',' ',' ',' ','2050',
    #          ' ',' ',' ',' ','2055',
    #          ' ',' ',' ',' ','2060']

    ticks = [' ','2024',
             ' ','2028',
             ' ','2032',
             ' ','2036',
             ' ','2040',
             ' ','2044',
             ' ','2048',
             ' ','2052',
             ' ','2056',
             ' ','2060']

    def set_box_color(bp, color):
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        plt.setp(bp['medians'], color=color)

    plt.figure()

    bpl = plt.boxplot(data_ADP.tolist(), positions=np.array(range(len(data_ADP.tolist()))) * 2.0 - 0.4, sym='', widths=0.6)
    bpr = plt.boxplot(data_CRSS.tolist(), positions=np.array(range(len(data_CRSS.tolist()))) * 2.0 + 0.4, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C')  # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    # draw temporary red and blue lines and use them to create a legend
    plt.plot([], c='#D7191C', label='ADP')
    plt.plot([], c='#2C7BB6', label='CRSS')
    plt.legend()

    plt.xticks(range(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks) * 2)
    if reservoir.name == "Powell":
        plt.ylim(3350, 3750)
        plt.title("Lake Powell elevation across different hydrological traces")
    elif reservoir.name == "Mead":
        plt.ylim(895, 1250)
        plt.title("Lake Mead elevation across different hydrological traces")

    plt.tight_layout()
    plt.show()
    # plt.savefig('boxcompare.png')

def ElvationComparison(PowellElevations47, MeadElevations47, TotalShortages47, DepletionTradeOff47,
                       PowellElevations94, MeadElevations94, TotalShortages94, DepletionTradeOff94):
    # print(PowellElevations47.iloc[:,0])

    # ====================RUN47, 25 years of drought========================
    # Lake Powell
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(a) Lake Powell Elevation")

    ax2 = ax1.twinx()
    ax1.plot(PowellElevations47.iloc[:,2], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.plot(PowellElevations47.iloc[:,1], linestyle='dashed', color = 'black', linewidth=1.5, label= 'DCP')
    ax1.axhline(3490, color='grey',  linestyle='dashed', linewidth=0.8, label= '3490 feet')
    ax2.plot(PowellElevations47.iloc[:,2], color = '#ed7d31')

    ax1.set_ylim([3370,3650])
    ax2.set_ylim([3370,3650])

    y = [3400, 3450, 3500, 3550, 3600, 3650]
    ylabels = ['0', '0.7', '2.3', '4.5', '7.6', '11.8', '17.2']
    ax2.set_yticklabels(ylabels)

    x = [0, 60, 120, 180, 240, 300]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040', '2045']
    ax1.set_xticklabels(xlabels)
    ax1.set_ylabel('Elevation (feet)')
    ax2.set_ylabel('Storage (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Lake Mead
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(b) Lake Mead Elevation")

    ax2 = ax1.twinx()
    ax1.plot(MeadElevations47.iloc[:,2], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.plot(MeadElevations47.iloc[:,1], linestyle='dashed', color = 'black', linewidth=1.5, label= 'DCP')
    ax1.axhline(1025, color='grey',  linestyle='dashed', linewidth=0.8, label= '1025 feet')
    ax2.plot(MeadElevations47.iloc[:,2], color = '#ed7d31')

    ax1.set_ylim([895,1145])
    ax2.set_ylim([895,1145])

    y = [895, 945, 995, 1045, 1095, 1145]
    ax1.set_yticks(y)
    ax2.set_yticks(y)
    ylabels = ['0', '1.8', '4.2', '7.3', '11.3', '16.2']
    ax2.set_yticklabels(ylabels)

    x = [0, 60, 120, 180, 240, 300]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040', '2045']
    ax1.set_xticklabels(xlabels)

    ax1.set_ylabel('Elevation (feet)')
    ax2.set_ylabel('Storage (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Total shortages
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(c) Total Annual Shortages")

    ax1.plot(TotalShortages47.iloc[:,2], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.plot(TotalShortages47.iloc[:,1], linestyle='dashed', color = 'black', linewidth=1.5, label= 'DCP')

    ax1.set_ylim([0,3])

    x = [0, 5, 10, 15, 20, 25]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040', '2045']
    ax1.set_xticklabels(xlabels)

    ax1.set_ylabel('Shortages (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Bar graph
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(d) Additional Cutback by ADP")
    labels = np.arange(2020, 2046)
    ax1.bar(labels, TotalShortages47.iloc[:,2] - TotalShortages47.iloc[:,1], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.axhline(0, color='grey', linewidth=0.8)
    ax1.set_ylim([-1.5, 1.5])
    ax1.set_ylabel('Additional Cutback (maf)')

    plt.show()

    # Depletion trade-off
    fig, ax1 = plt.subplots()

    size1 = 80
    size2 = 90
    size3 = 90

    ax1.scatter(DepletionTradeOff47.iat[7, 0], DepletionTradeOff47.iat[7, 1], size3, color='gold', alpha=1,
                marker = "o", label='Ideal point')
    ax1.scatter(DepletionTradeOff47.iat[6, 0], DepletionTradeOff47.iat[6, 1], size1, color='black', alpha=1,
                marker = "s", label='DCP')
    ax1.scatter(DepletionTradeOff47.iloc[0:6, 0], DepletionTradeOff47.iloc[0:6, 1], size2, color='#ed7d31', alpha=1,
                marker = "^", label='ADP')

    x0 = 100
    y0 = 185
    ax1.hlines(DepletionTradeOff47.iat[7, 1], x0, DepletionTradeOff47.iat[7, 0], color='grey', linestyle='dashed', alpha=0.5)
    ax1.vlines(DepletionTradeOff47.iat[7, 0], y0, DepletionTradeOff47.iat[7, 1], color='grey', linestyle='dashed', alpha=0.5)

    ADPlabel = [' UB, LB&M propotionally','  All by UB','  All by LB&M','  50% by UB ','  75% by UB','  75% by LB&M']
    for i in range(len(ADPlabel)):
        if i == 0:
            ax1.text(DepletionTradeOff47.iat[i, 0]-11, DepletionTradeOff47.iat[i, 1]-2, ADPlabel[i])
        else:
            ax1.text(DepletionTradeOff47.iat[i, 0], DepletionTradeOff47.iat[i, 1], ADPlabel[i])

    ax1.set_ylim(y0, 230)
    ax1.set_xlim(x0, 135)

    ax1.set_xlabel('UB water depletions for the next 25 years (maf)')
    ax1.set_ylabel('LB and Mexico water depletions for the next 25 years (maf)')

    ax1.legend()
    plt.show()

    # ==============RUN94, 19 years of drought==================
    # Lake Powell
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(a) Lake Powell Elevation")

    ax2 = ax1.twinx()
    ax1.plot(PowellElevations94.iloc[:, 2], color='#ed7d31', label='ADP', linewidth=2.0)
    ax1.plot(PowellElevations94.iloc[:, 1], linestyle='dashed', color='black', linewidth=1.5, label='DCP')
    ax1.axhline(3490, color='grey',  linestyle='dashed', linewidth=0.8, label= '3490 feet')
    ax2.plot(PowellElevations94.iloc[:, 2], color='#ed7d31')

    ax1.set_ylim([3370, 3650])
    ax2.set_ylim([3370, 3650])

    y = [3400, 3450, 3500, 3550, 3600, 3650]
    ylabels = ['0', '0.7', '2.3', '4.5', '7.6', '11.8', '17.2']
    ax2.set_yticklabels(ylabels)

    x = [0, 60, 120, 180, 240]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040']
    ax1.set_xticklabels(xlabels)
    ax1.set_ylabel('Elevation (feet)')
    ax2.set_ylabel('Storage (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Lake Mead
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(b) Lake Mead Elevation")

    ax2 = ax1.twinx()
    ax1.plot(MeadElevations94.iloc[:,2], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.plot(MeadElevations94.iloc[:,1], linestyle='dashed', color = 'black', linewidth=1.5, label= 'DCP')
    ax1.axhline(1025, color='grey',  linestyle='dashed', linewidth=0.8, label= '1025 feet')
    # ax1.plot(MeadElevations94.iloc[:,3], linestyle='dashed', color = 'grey', linewidth=1.0, label= '1025 feet')
    ax2.plot(MeadElevations94.iloc[:,2], color = '#ed7d31')

    ax1.set_ylim([895,1145])
    ax2.set_ylim([895,1145])

    y = [895, 945, 995, 1045, 1095, 1145]
    ax1.set_yticks(y)
    ax2.set_yticks(y)
    ylabels = ['0', '1.8', '4.2', '7.3', '11.3', '16.2']
    ax2.set_yticklabels(ylabels)

    x = [0, 60, 120, 180, 240]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040']
    ax1.set_xticklabels(xlabels)

    ax1.set_ylabel('Elevation (feet)')
    ax2.set_ylabel('Storage (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Total shortages
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(c) Total Annual Shortages")

    ax1.plot(TotalShortages94.iloc[:,2], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.plot(TotalShortages94.iloc[:,1], linestyle='dashed', color = 'black', linewidth=1.5, label= 'DCP')

    ax1.set_ylim([0,3.5])

    x = [0, 5, 10, 15, 20]
    ax1.set_xticks(x)
    xlabels = ['2020', '2025', '2030', '2035', '2040']
    ax1.set_xticklabels(xlabels)

    ax1.set_ylabel('Shortages (maf)')

    ax1.legend(loc='lower right', prop={'size': 8})
    plt.show()

    # Bar graph
    fig, ax1 = plt.subplots(figsize=(8, 4.8))

    ax1.set_title("(d) Additional Cutback by ADP")
    labels = np.arange(2020, 2040)
    ax1.bar(labels, TotalShortages94.iloc[:,2] - TotalShortages94.iloc[:,1], color = '#ed7d31', label= 'ADP', linewidth=2.0)
    ax1.axhline(0, color='grey', linewidth=0.8)
    ax1.set_ylim([-1.5, 1.5])
    ax1.set_ylabel('Additional Cutback (maf)')

    x = [2020, 2025, 2030, 2035, 2040]
    ax1.set_xticks(x)
    # xlabels = ['2020', '2025', '2030', '2035', '2040']
    # ax1.set_xticklabels(xlabels)

    plt.show()

    # Depletion trade-off
    fig, ax1 = plt.subplots()

    size1 = 80
    size2 = 90
    size3 = 90

    ax1.scatter(DepletionTradeOff94.iat[7, 0], DepletionTradeOff94.iat[7, 1], size3, color='gold', alpha=1,
                marker = "o", label='Ideal point')
    ax1.scatter(DepletionTradeOff94.iat[6, 0], DepletionTradeOff94.iat[6, 1], size1, color='black', alpha=1,
                marker = "s", label='DCP')
    ax1.scatter(DepletionTradeOff94.iloc[0:6, 0], DepletionTradeOff94.iloc[0:6, 1], size2, color='#ed7d31', alpha=1,
                marker = "^", label='ADP')

    x0 = 65
    y0 = 140
    ax1.hlines(DepletionTradeOff94.iat[7, 1], x0, DepletionTradeOff94.iat[7, 0], color='grey', linestyle='dashed', alpha=0.5)
    ax1.vlines(DepletionTradeOff94.iat[7, 0], y0, DepletionTradeOff94.iat[7, 1], color='grey', linestyle='dashed', alpha=0.5)

    ADPlabel = [' UB, LB&M propotionally','  All by UB','  All by LB&M','  50% by UB ','  75% by UB','  75% by LB&M']

    for i in range(len(ADPlabel)):
        if i == 0:
            ax1.text(DepletionTradeOff94.iat[i, 0]-11, DepletionTradeOff94.iat[i, 1]-2, ADPlabel[i])
        elif i == 5:
            ax1.text(DepletionTradeOff94.iat[i, 0] , DepletionTradeOff94.iat[i, 1]-2, ADPlabel[i])
        else:
            ax1.text(DepletionTradeOff94.iat[i, 0], DepletionTradeOff94.iat[i, 1], ADPlabel[i])

    ax1.set_ylim(y0, 175)
    ax1.set_xlim(x0, 105)

    ax1.set_xlabel('UB water depletions for the next 19 years (maf)')
    ax1.set_ylabel('LB and Mexico water depletions for the next 19 years (maf)')

    ax1.legend()
    plt.show()

# plot results for sensitivity analysis
def plotYearsto12maf(DCP, DCPplus12, DCPplus8, DCPplus4, ADP, Paleo,
                     Depletion, TemperatureMIN, TemperatureMAX, DepletionStorage):

    # first plot
    # scatter points
    plt.plot(ADP[0], ADP[1], 'o', color = '#ffa505', label= 'ADP')

    # line, BLUE: 015C92, 6fa4d4, 88CDF6; RED: a70000, ff0000, ff7b7b; Yellow: ffa505, ffc905, ffe505
    plt.plot(DCPplus12[0], DCPplus12[1], '#015C92', label='DCP+(1.2 maf additional cut)')
    plt.plot(DCPplus8[0], DCPplus8[1], '#6fa4d4', label='DCP+(0.8 maf additional cut)')
    plt.plot(DCPplus4[0], DCPplus4[1], '#88CDF6', label='DCP+(0.4 maf additional cut)')
    plt.plot(DCP[0], DCP[1], '#ff0000', label='DCP')

    plt.fill_between(Paleo[0], Paleo[1], color="grey", alpha=0.2, label='Paleo + observed drought events')

    # plt.title('')
    plt.xlabel('Natural Inflow at Lees Ferry (maf/yr)')
    plt.ylabel('Years to for combined Powell and Mead storage to 12 maf')

    y = [0, 5, 10, 15, 20, 25, 30]
    labels = ['0', '5', '10', '15', '20', '25', '>40']
    plt.yticks(y, labels)

    plt.legend()
    plt.show()

    # second plot
    # plt.cla()
    # 6.4 4.8 by default
    plt.figure(figsize=(10, 4.8))

    # print(TurningPointYear[3])
    # print(np.where(Depletion[0] == TurningPointYear[3], True, False))

    labels = ['placeholder',
              '6 maf/yr natural flow at Lees Ferry --- DCP',
              '9 maf/yr natural flow at Lees Ferry --- DCP',
              '12 maf/yr natural flow at Lees Ferry --- DCP',
              '6 maf/yr natural flow at Lees Ferry --- ADP',
              '9 maf/yr natural flow at Lees Ferry --- ADP',
              '12 maf/yr natural flow at Lees Ferry --- ADP',
              '6 maf/yr natural flow at Lees Ferry --- DCP+ 1.2 maf more contribution',
              '9 maf/yr natural flow at Lees Ferry --- DCP+ 1.2 maf more contribution',
              '12 maf/yr natural flow at Lees Ferry --- DCP+ 1.2 maf more contribution']
    newlabels = ['\n'.join(wrap(l, 28)) for l in labels]

    # plt.plot(Depletion[0], Depletion[3], '#ffa505', label=newlabels[3],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][3], True, False), marker = 'o')
    # plt.plot(Depletion[0], Depletion[9], '#ffe505', label=newlabels[9],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][9], True, False), marker = 'o')
    # plt.plot(Depletion[0], Depletion[6], '#ffc905', label=newlabels[6],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][6], True, False), marker = 'o')
    #
    # plt.plot(Depletion[0], Depletion[8], '#88CDF6', label=newlabels[8],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][8], True, False), marker = 'o')
    # plt.plot(Depletion[0], Depletion[2], '#015C92', label=newlabels[2],
    #          markevery=np.where(Depletion[0] == TurningPointYear[0][2], True, False), marker='o')
    # plt.plot(Depletion[0], Depletion[5], '#6fa4d4', label=newlabels[5],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][5], True, False), marker = 'o')
    #
    # plt.plot(Depletion[0], Depletion[7], '#ff7b7b', label=newlabels[7],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][7], True, False), marker = 'o')
    # plt.plot(Depletion[0], Depletion[1], '#a70000', label=newlabels[1],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][1], True, False), marker = 'o')
    # plt.plot(Depletion[0], Depletion[4], '#ff0000', label=newlabels[4],
    #          markevery = np.where(Depletion[0] == TurningPointYear[0][4], True, False), marker = 'o')
    #
    # plt.ylabel('The entire basin depletion (maf)')
    # plt.ylim([5,16])
    # # plt.legend()
    # plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", labelspacing=0.6)
    #
    # plt.show()

    # third figure
    # plt.figure(figsize=(6.4, 7.2))
    # fig, axs = plt.subplots(3, figsize=(6.4, 7.2))
    fig, axs = plt.subplots(2, figsize=(6.4, 4.8))

    fig.suptitle('')
    axs[0].fill_between(TemperatureMIN[0], TemperatureMIN[1], TemperatureMAX[1], color="#ff0000",
                        alpha=0.4, label='DCP (6 maf/yr natural flow at Lees Ferry)')
    axs[0].fill_between(TemperatureMIN[0], TemperatureMIN[2], TemperatureMAX[2], color="#6fa4d4",
                        alpha=0.4, label='DCP (9 maf/yr natural flow at Lees Ferry)')
    axs[0].fill_between(TemperatureMIN[0], TemperatureMIN[3], TemperatureMAX[3], color="#ffc905",
                        alpha=0.4, label='DCP (12 maf/yr natural flow at Lees Ferry)')

    axs[1].fill_between(TemperatureMIN[0], TemperatureMIN[4], TemperatureMAX[4], color="#ff0000",
                        alpha=0.4, label='ADP (6 maf/yr natural flow at Lees Ferry)')
    axs[1].fill_between(TemperatureMIN[0], TemperatureMIN[5], TemperatureMAX[5], color="#6fa4d4",
                        alpha=0.4, label='ADP (9 maf/yr natural flow at Lees Ferry)')
    axs[1].fill_between(TemperatureMIN[0], TemperatureMIN[6], TemperatureMAX[6], color="#ffc905",
                        alpha=0.4, label='ADP (12 maf/yr natural flow at Lees Ferry)')

    # axs[2].fill_between(TemperatureMIN[0], TemperatureMIN[7], TemperatureMAX[7], color="#ff0000",
    #                     alpha=0.4, label='DCP+ 1.2 maf more contribution (6 maf/yr natural flow at Lees Ferry)')
    # axs[2].fill_between(TemperatureMIN[0], TemperatureMIN[8], TemperatureMAX[8], color="#6fa4d4",
    #                     alpha=0.4, label='DCP+ 1.2 maf more contribution (9 maf/yr natural flow at Lees Ferry)')
    # axs[2].fill_between(TemperatureMIN[0], TemperatureMIN[9], TemperatureMAX[9], color="#ffc905",
    #                     alpha=0.4, label='DCP+ 1.2 maf more contribution (12 maf/yr natural flow at Lees Ferry)')

    axs[0].set_ylim([0, 30])
    axs[0].set_ylabel('Temperature(°C)')
    axs[1].set_ylim([0, 30])
    axs[1].set_ylabel('Temperature(°C)')
    # axs[2].set_ylim([0, 30])
    # axs[2].set_ylabel('Temperature(°C)')

    # axs[0].legend(loc='center right', prop={'size': 8})
    axs[0].legend(loc='lower right', prop={'size': 8})
    axs[1].legend(loc='upper right', prop={'size': 8})
    # axs[2].legend(loc='lower right', prop={'size': 8})

    plt.show()

    # inflow = 6 maf/yr
    # BLUE: #005073, #107dac, #189ad3, #1ebbd7, #71c7ec
    # RED: #a70000, #ff0000, #ff5252, #ff7b7b, #ffbaba
    # Yellow: #ffa505, #ffb805, #ffc905, #ffe505, #fffb05

    # 3 colors, BLUE: 015C92, 6fa4d4, 88CDF6; RED: a70000, ff0000, ff7b7b; Yellow: ffa505, ffc905, ffe505

    plt.figure(figsize=(8, 4.8))

    size1 = 90
    size2 = 120
    size3 = 150

    plt.scatter(DepletionStorage[5][0], DepletionStorage[6][0], size1, color='#ffa505', alpha=1,
                marker = "x", label=newlabels[3])
    plt.scatter(DepletionStorage[5][2], DepletionStorage[6][2], size2, color='#ffc905', alpha=1,
                marker = "+", label=newlabels[9])
    plt.scatter(DepletionStorage[5][1], DepletionStorage[6][1], size3, color='#ffe505', alpha=1,
                marker = "1", label=newlabels[6])

    # overlapping problem
    # plt.scatter(DepletionStorage[5][3], DepletionStorage[6][3], color='#ffe505', alpha=1, marker = "H")
    # plt.scatter(DepletionStorage[5][4], DepletionStorage[6][4], color='#fffb05', alpha=1, marker = "D")

    plt.scatter(DepletionStorage[3][0], DepletionStorage[4][0], size1, color='#015C92', alpha=1,
                marker = "x", label=newlabels[2])
    plt.scatter(DepletionStorage[3][2], DepletionStorage[4][2], size2, color='#6fa4d4', alpha=1,
                marker="+", label=newlabels[8])
    plt.scatter(DepletionStorage[3][1], DepletionStorage[4][1], size3, color='#88CDF6', alpha=1,
                marker = "1", label=newlabels[5])

    # plt.scatter(DepletionStorage[3][3], DepletionStorage[4][3], color='#1ebbd7', alpha=1, marker = "H")
    # plt.scatter(DepletionStorage[3][4], DepletionStorage[4][4], color='#71c7ec', alpha=1, marker = "D")

    plt.scatter(DepletionStorage[1][0], DepletionStorage[2][0], size1, color='#a70000', alpha=1,
                marker = "x", label=newlabels[1])
    plt.scatter(DepletionStorage[1][2], DepletionStorage[2][2], size2, color='#ff0000', alpha=1,
                marker="+", label=newlabels[7])
    plt.scatter(DepletionStorage[1][1], DepletionStorage[2][1], size3, color='#ff7b7b', alpha=1,
                marker = "1", label=newlabels[4])

    plt.xlabel('End of planning horizon combined Lake Powell and Lake Mead storage (maf)')
    plt.ylabel('Steady ending state UB, LB and Mexico depletion (maf)')
    # plt.xlim([-2, 18])
    plt.ylim([0,16])

    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", labelspacing=0.6)

    plt.show()



