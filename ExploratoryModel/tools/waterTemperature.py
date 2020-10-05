import math

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
    if elevation > 3525:
        return getReleaseTemp(month, elevation)
    elif elevation < 3490:
        return getReleaseTemp(month, elevation)
    else:
        # half release from penstock, half from river outlet.
        w1 = 0.5
        w2 = 0.5
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