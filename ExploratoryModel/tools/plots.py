import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import figaspect

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
    plot_Elevations_CRSS_Exploratory(x, y4crss, y1crss, y4, y1, title, EleRange, StrRange)
    # plot_Elevations_CRSS_Exploratory_Gap(x, y1crss-y1, title)
    # title = "inflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y2crss-y2, title)
    # title = "outflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y3crss-y3, title)

def plot_Elevations_Flows_CRSS_Exploratory_Mead(x, y1crss, y2crss, y3crss, y4crss, y1, y2, y3, y4, title):
    EleRange = [895, 1250]
    StrRange = [0, 30000000]
    plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, StrRange)
    plot_Elevations_CRSS_Exploratory(x, y4crss, y1crss, y4, y1, title, EleRange, StrRange)
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

