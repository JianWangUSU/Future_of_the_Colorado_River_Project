import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

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

def plot_Elevations_Flows_CRSS_Exploratory_Powell(x, y1crss, y2crss, y3crss, y1, y2, y3, title):
    EleRange = [3370, 3710]
    plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, EleRange)
    plot_Elevations_CRSS_Exploratory(x, y1crss, y1, title, EleRange)
    # plot_Elevations_CRSS_Exploratory_Gap(x, y1crss-y1, title)
    # title = "inflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y2crss-y2, title)
    # title = "outflow"
    # plot_Flow_CRSS_Exploratory_Gap(x, y3crss-y3, title)

def plot_Elevations_Flows_CRSS_Exploratory_Mead(x, y1crss, y2crss, y3crss, y1, y2, y3, title):
    EleRange = [950, 1250]
    plot_Elevations_Flows_CRSS_Exploratory(x, y1crss, y2crss, y3crss, y1, y2, y3, title, EleRange)
    plot_Elevations_CRSS_Exploratory(x, y1crss, y1, title, EleRange)
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
    ax1.set_ylabel('Elevation (feet)')
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

def plot_Elevations_CRSS_Exploratory(x, y1crss, y1, title, EleRange):

    fig, (ax1) = plt.subplots(1, 1)
    fig.suptitle(title)

    ax1.plot(x, y1, color='blue', label='Exploratory')
    ax1.plot(x, y1crss, color='red',label='CRSS',linewidth=1)
    ax1.set_ylabel('Elevation (feet)')
    ax1.set_ylim(EleRange)
    ax1.set_xlabel('time')

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


