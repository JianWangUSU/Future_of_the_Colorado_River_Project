import math
import numpy as np

JAN = 0
FEB = 1
MAR = 2
APR = 3
MAY = 4
JUN = 5
JUL = 6
AUG = 7
SEP = 8
OCT = 9
NOV = 10
DEC = 11

# historical records. WY
HisRecord_2005 = [3570.5, 3567.28, 3564.42, 3562.07, 3559.23, 3555.9, 3562.81, 3586.53, 3606.28, 3606.87, 3602.83, 3601.97]
WYindex = [OCT, NOV, DEC, JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP]

# Millennium_drought scenario (2000 to 2018)

# mid-20th century drought (1953 to 1977)

deltaT = [0.4, 0.3, 0.4, 0.4, 0.6, 0.8, 1.1, 1.2, 1.8, 1.7, 2.5, 0.5]
# deltaD = [0, 0, 0, -23, -20, -18, -19, -14, -17, -15, -30, -14]
deltaD = -15

# depth, profile table, D: depth; P_JAN: profile in Jan
D = None
# profile
P_JAN = None
P_FEB = None
P_MAR = None
P_APR = None
P_MAY = None
P_JUN = None
P_JUL = None
P_AUG = None
P_SEP = None
P_OCT = None
P_NOV = None
P_DEC = None

def getJanReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_JAN) + deltaT[JAN]

def getFebReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_FEB) + deltaT[FEB]

def getMarReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_MAR) + deltaT[MAR]

def getAprReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_APR) + deltaT[APR]

def getMayReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_MAY) + deltaT[MAY]

def getJunReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_JUN) + deltaT[JUN]

def getJulReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_JUL) + deltaT[JUL]

def getAugReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_AUG) + deltaT[AUG]

def getSepReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_SEP) + deltaT[SEP]

def getOctReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_OCT) + deltaT[OCT]

def getNovReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_NOV) + deltaT[NOV]

def getDecReleaseTempNEW(elevation):
    if elevation > 3490:
        depth = elevation - 3470
    else:
        depth = elevation - 3370

    return np.interp(depth, D, P_DEC) + deltaT[DEC]

def getReleaseTempGivenElevationRangeNEW(month, elevation):
    # return getReleaseTempNEW(month, elevation)
    return getReleaseTempDeltaD(month, elevation)

# reservoir release temperature simulation model, current model is only for Lake Powell
def simulateResTemp(reservoir):
    for i in range(0, reservoir.inflowTraces):
        for t in range(0, reservoir.periods):
            month = reservoir.para.determineMonth(t)
            if t == 0:
                Ave_Elevation = (reservoir.elevation[i][t] + reservoir.volume_to_elevation(reservoir.initStorage))/2.0
                reservoir.releaseTemperature[i][t] = getReleaseTempDeltaD(month, Ave_Elevation)
            else:
                Ave_Elevation = (reservoir.elevation[i][t] + reservoir.elevation[i][t-1])/2.0
                reservoir.releaseTemperature[i][t] = getReleaseTempDeltaD(month, Ave_Elevation)

    for i in range(reservoir.inflowTraces):
        for t in range(reservoir.years):
            # Jun Jul Aug Sep
            reservoir.summerReleaseTemperature[i][t] \
                = sum(reservoir.releaseTemperature[i][t * 12 + 5:t * 12 + 9]) \
                  / len(reservoir.releaseTemperature[i][t * 12 + 5:t * 12 + 9])

def getReleaseTempNEW(month, elevation):
    if month == JAN:
        return getJanReleaseTempNEW(elevation)
    if month == FEB:
        return getFebReleaseTempNEW(elevation)
    if month == MAR:
        return getMarReleaseTempNEW(elevation)
    if month == APR:
        return getAprReleaseTempNEW(elevation)
    if month == MAY:
        return getMayReleaseTempNEW(elevation)
    if month == JUN:
        return getJunReleaseTempNEW(elevation)
    if month == JUL:
        return getJulReleaseTempNEW(elevation)
    if month == AUG:
        return getAugReleaseTempNEW(elevation)
    if month == SEP:
        return getSepReleaseTempNEW(elevation)
    if month == OCT:
        return getOctReleaseTempNEW(elevation)
    if month == NOV:
        return getNovReleaseTempNEW(elevation)
    if month == DEC:
        return getDecReleaseTempNEW(elevation)

def getJanReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_JAN)

def getFebReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_FEB)

def getMarReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_MAR)

def getAprReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_APR)

def getMayReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_MAY)

def getJunReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_JUN)

def getJulReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_JUL)

def getAugReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_AUG)

def getSepReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_SEP)

def getOctReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_OCT)

def getNovReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_NOV)

def getDecReleaseTempDeltaD(elevation):
    if elevation > 3490:
        depth = elevation - 3470 + deltaD
    else:
        depth = elevation - 3370 + deltaD

    if depth < 0:
        depth = 0

    return np.interp(depth, D, P_DEC)


def getReleaseTempDeltaD(month, elevation):
    if month == JAN:
        return getJanReleaseTempDeltaD(elevation)
    if month == FEB:
        return getFebReleaseTempDeltaD(elevation)
    if month == MAR:
        return getMarReleaseTempDeltaD(elevation)
    if month == APR:
        return getAprReleaseTempDeltaD(elevation)
    if month == MAY:
        return getMayReleaseTempDeltaD(elevation)
    if month == JUN:
        return getJunReleaseTempDeltaD(elevation)
    if month == JUL:
        return getJulReleaseTempDeltaD(elevation)
    if month == AUG:
        return getAugReleaseTempDeltaD(elevation)
    if month == SEP:
        return getSepReleaseTempDeltaD(elevation)
    if month == OCT:
        return getOctReleaseTempDeltaD(elevation)
    if month == NOV:
        return getNovReleaseTempDeltaD(elevation)
    if month == DEC:
        return getDecReleaseTempDeltaD(elevation)

def getMinReleaseTempDeltaD(month, elevation):

    depth = elevation - 3370 + deltaD

    if month == JAN:
        return np.interp(depth, D, P_JAN)
    if month == FEB:
        return np.interp(depth, D, P_FEB)
    if month == MAR:
        return np.interp(depth, D, P_MAR)
    if month == APR:
        return np.interp(depth, D, P_APR)
    if month == MAY:
        return np.interp(depth, D, P_MAY)
    if month == JUN:
        return np.interp(depth, D, P_JUN)
    if month == JUL:
        return np.interp(depth, D, P_JUL)
    if month == AUG:
        return np.interp(depth, D, P_AUG)
    if month == SEP:
        return np.interp(depth, D, P_SEP)
    if month == OCT:
        return np.interp(depth, D, P_OCT)
    if month == NOV:
        return np.interp(depth, D, P_NOV)
    if month == DEC:
        return np.interp(depth, D, P_DEC)

def getJanReleaseTemp(elevation):
    if elevation > 3490:
        return 5.36+(3.815525648*math.exp(-(-0.004664035)*((elevation/3.28084)-1127.76)))
    else:
        return 5.36 + (3.815525648 * math.exp(-(-0.004664035) * (((elevation+96)/ 3.28084) - 1127.76)))

def getFebReleaseTemp(elevation):
    if elevation > 3490:
        return 5.667857143+(2.64291514*math.exp(-(-0.002277994)*((elevation/3.28084)-1127.76)))
    else:
        return 5.667857143+(2.64291514*math.exp(-(-0.002277994)*(((elevation+96)//3.28084)-1127.76)))

def getMarReleaseTemp(elevation):
    if elevation > 3490:
        return 7.343478261+(0.866777569*math.exp(-(0.009667425)*((elevation/3.28084)-1127.76)))
    else:
        return 7.343478261+(0.866777569*math.exp(-(0.009667425)*(((elevation+96)/3.28084)-1127.76)))

def getAprReleaseTemp(elevation):
    if elevation > 3490:
        return 6.759259259+(1.734071491*math.exp(-(0.007769259)*((elevation/3.28084)-1127.76)))
    else:
        return 6.759259259+(1.734071491*math.exp(-(0.007769259)*(((elevation+96)/3.28084)-1127.76)))

def getMayReleaseTemp(elevation):
    if elevation > 3490:
        return 7.112903226+(1.473399599*math.exp(-(0.018251341)*((elevation/3.28084)-1127.76)))
    else:
        return 7.112903226+(1.473399599*math.exp(-(0.018251341)*(((elevation+96)/3.28084)-1127.76)))

def getJunReleaseTemp(elevation):
    if elevation > 3490:
        return 8.095238095+(1.097430498*math.exp(-(0.031219207)*((elevation/3.28084)-1127.76)))
    else:
        return 8.095238095+(1.097430498*math.exp(-(0.031219207)*(((elevation+96)/3.28084)-1127.76)))

def getJulReleaseTemp(elevation):
    if elevation > 3490:
        return 8.115384615+(1.106900875*math.exp(-(0.044112483)*((elevation/3.28084)-1127.76)))
    else:
        return 8.115384615+(1.106900875*math.exp(-(0.044112483)*(((elevation+96)/3.28084)-1127.76)))

def getAugReleaseTemp(elevation):
    if elevation > 3490:
        return 7.910714286+(1.252536876*math.exp(-(0.044297389)*((elevation/3.28084)-1127.76)))
    else:
        return 7.910714286+(1.252536876*math.exp(-(0.044297389)*(((elevation+96)/3.28084)-1127.76)))

def getSepReleaseTemp(elevation):
    if elevation > 3490:
        return 7.788461538+(1.509123384*math.exp(-(0.040706994)*((elevation/3.28084)-1127.76)))
    else:
        return 7.788461538+(1.509123384*math.exp(-(0.040706994)*(((elevation+96)/3.28084)-1127.76)))

def getOctReleaseTemp(elevation):
    if elevation > 3490:
        return 7.876923077+(1.5738892*math.exp(-(0.035494644)*((elevation/3.28084)-1127.76)))
    else:
        return 7.876923077+(1.5738892*math.exp(-(0.035494644)*(((elevation+96)/3.28084)-1127.76)))

def getNovReleaseTemp(elevation):
    if elevation > 3490:
        return 7.594444444+(1.880906664*math.exp(-(0.025102979)*((elevation/3.28084)-1127.76)))
    else:
        return 7.594444444+(1.880906664*math.exp(-(0.025102979)*(((elevation+96)/3.28084)-1127.76)))

def getDecReleaseTemp(elevation):
    if elevation > 3490:
        return 7.587096774+(1.978022304*math.exp(-(0.011288015)*((elevation/3.28084)-1127.76)))
    else:
        return 7.587096774+(1.978022304*math.exp(-(0.011288015)*(((elevation+96)/3.28084)-1127.76)))

def getReleaseTempGivenElevationRange(month, elevation):
    if elevation > 3555:
        return getReleaseTemp(month, elevation)
    elif elevation < 3490:
        return getReleaseTemp(month, elevation)
    else:
        # half release from penstock, half from river outlet.
        w1 = 1
        w2 = 0
        return w1* getReleaseTemp(month, elevation) + w2 * getReleaseTemp(month, elevation+96)

def getReleaseTempWhenReleaesfromOutlet(month, elevation):
    w1 = 0
    w2 = 1
    return w1* getReleaseTemp(month, elevation) + w2 * getReleaseTemp(month, elevation+96)

def getReleaseTemp(month, elevation):
    if month == JAN:
        return getJanReleaseTemp(elevation)
    if month == FEB:
        return getFebReleaseTemp(elevation)
    if month == MAR:
        return getMarReleaseTemp(elevation)
    if month == APR:
        return getAprReleaseTemp(elevation)
    if month == MAY:
        return getMayReleaseTemp(elevation)
    if month == JUN:
        return getJunReleaseTemp(elevation)
    if month == JUL:
        return getJulReleaseTemp(elevation)
    if month == AUG:
        return getAugReleaseTemp(elevation)
    if month == SEP:
        return getSepReleaseTemp(elevation)
    if month == OCT:
        return getOctReleaseTemp(elevation)
    if month == NOV:
        return getNovReleaseTemp(elevation)
    if month == DEC:
        return getDecReleaseTemp(elevation)

def CalculateTempForEachInflowTrace(reservoir, elevations):

    [inflowTraces, periods] = elevations.shape
    # print(elevations.shape)
    # average month elevation
    aveElevations = np.zeros([inflowTraces, periods])

    # calculate average elevation for each month
    for i in range(inflowTraces):
        for t in range(periods):
            if t == 0:
                aveElevations[i][t] = elevations[i][t]
            else:
                aveElevations[i][t] = (elevations[i][t]+elevations[i][t-1])/2.0

    # release through penstock when elevation > 3490
    releaseTemp = np.zeros([inflowTraces, periods])
    # release through river outlet when release temperature > 20
    releaseTemp2 = np.zeros([inflowTraces, periods])
    for i in range(inflowTraces):
        for t in range(periods):
            month = reservoir.para.determineMonth(t)
            releaseTemp[i][t] = getReleaseTempGivenElevationRangeNEW(month, aveElevations[i][t])
            # releaseTemp[i][t] = getReleaseTempGivenElevationRange(month, aveElevations[i][t])

    # dotty plot
    # calculate summer temperature for each year (JUL, AUG. SEP)
    years = int(periods / 12)
    summerTemp = np.zeros([inflowTraces, years])
    for i in range(inflowTraces):
        for t in range(years):
            # Jun Jul Aug Sep
            summerTemp[i][t] = sum(releaseTemp[i][t * 12 + 5:t * 12 + 9]) / len(releaseTemp[i][t * 12 + 5:t * 12 + 9])

    AveTempForPeriod = np.zeros([inflowTraces, years, years])
    # length of years (x axis)

    for i in range(inflowTraces):
        for y in range(years):
            # years (y axis)
            for t in range(years):
                if y == 0:
                    # year 1 has 40 points, Run 25 has the lowest reservoir elevation
                    AveTempForPeriod[i][y][t] = summerTemp[i][t]
                else:
                    # year 2 has 39 points, year 3 has 38 points....
                    if t + y >= years:
                        break

                    AveTempForPeriod[i][y][t] = sum(summerTemp[i][t:t + y + 1]) / len(summerTemp[i][t:t + y + 1])

    return AveTempForPeriod