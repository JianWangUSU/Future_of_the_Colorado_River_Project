
# This file is designed to change policy on/off status


# ================================Policy for Lake Powell==================================

### Replicated CRSS (AUG 2020 VERSION) lake Powell policy:
# including PowellOperationsRule (POLICY 28), MeetPowellMinObjectiveRelease (POLICY 24)
# , LowerElevationBalancingTier (POLICY 23), MidElevationReleaseTier (POLICY 22)
# , UpperElevationBalancingTierAprilthruSept (POLICY 21), UpperElevationBalancingTierJanthruMarch (POLICY 20)
# , EqualizationTier (POLICY 19)
#########
# NOTE: in these policies there are a lot of parameters are copied directly from CRSS simulation results
# because the Exploratory model don't have a way to calculate them.
# This policy can ONLY be used for validation!!!
#########
CRSS_Powell = False

# Equalization rule, it is a simple policy developed by JIAN, not policy used in CRSS
EQUAL = False

# ADP: adaptive policy, only consider Pearce Ferry Rapid signpost, will add more.
ADP = False

# Fill Mead First
FMF = False

# Fill Powell First
FPF = False

LakePowellPolicyList = [CRSS_Powell, EQUAL, ADP, FMF, FPF]
LakePowellPolicyListNames = ['CRSS_Powell', 'Equalization', 'ADP', 'FMF', 'FPF']

# This function is not well written
def setPowellPolicy(name):
    global CRSS_Powell
    global EQUAL

    if name == 'CRSS_Powell':
        CRSS_Powell = True
        EQUAL = False
    elif name == 'Equalization':
        CRSS_Powell = False
        EQUAL = True
    else:
        CRSS_Powell = True
        EQUAL = False

# ================================Policy for Lake Mead===================================

#########
# NOTE: We assume Lake Mead outflow = demands below Lake Mead (including Lake Mohave, Lake Hasvasu evaporation).
# Since the Exploratory model don't have a way to calculate, these parameters, we use CRSS simulation results directly.
# In Set Mead Outflow For Demands(CRSS policy 7), we export CurrentDemandBelowMead()
# as well as Mead.Diversion and Mead.Return Flow
# Demand in the Exploratory model = CurrentDemandBelowMead() + Mead.Diversion - Mead.Return Flow
# This policy can ONLY be used for validation!!!
#########
CRSS_Mead = False

# Adapt demand to inflow policy (it will change Lake Powell inflow and Lake Mead release)
ADP_DemandtoInflow = False
# trigger ADP policy only when reservoir storage is < self.plc.ADP_triggerS, 10857008 af respond to 1090 feet
# ADP_triggerS_LOW = 10857008
# 1025 feet, 5981122 acre-feet;
# 1050 feet, 7682878 acre-feet;
# 1060 feet, 8423088 acre-feet
# ADP_triggerS_LOW = 7682878
ADP_triggerS_LOW = 8423088


# Protect Pearce Ferry Rapid
PFR = False

# Meet Lower basin demand
LB_demand = False

# Drought contingency plan, todo
DCP = False

# Intentional creat surplus, todo
ICS = False
# Release policy for each reservoir, which inflow scenario to use, which demand scenario to use, which signpost?

LakeMeadPolicyList = [CRSS_Mead, ADP_DemandtoInflow, PFR, LB_demand, DCP, ICS]
LakeMeadPolicyListNames = ['CRSS_Mead', 'ADP_DemandtoInflow', 'PFR', 'LB_demand', 'DCP', 'ICS']

def setMeadPolicy(name):
    global CRSS_Mead
    global ADP_DemandtoInflow
    global DCP

    if name == 'CRSS_Mead':
        CRSS_Mead = True
        ADP_DemandtoInflow = False
        DCP = False
    elif name == 'ADP_DemandtoInflow':
        CRSS_Mead = False
        ADP_DemandtoInflow = True
        DCP = False
    elif name == 'DCP':
        CRSS_Mead = False
        ADP_DemandtoInflow = False
        DCP = True
    else:
        CRSS_Mead = True
        ADP_DemandtoInflow = False
        DCP = False