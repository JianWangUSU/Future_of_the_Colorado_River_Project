
# This file is designed to change policy on/off status


# ==============Policy for Lake Powell=================

# Equalization rule, it is a simple policy developed by JIAN, not policy used in CRSS
EQUAL = False

# Adaptive policy, todo
ADP = False

# Fill Mead First
FMF = False

# Fill Powell First
FPF = False

### Replicated CRSS (AUG 2020 VERSION) lake Powell policy:
# including PowellOperationsRule (POLICY 28), MeetPowellMinObjectiveRelease (POLICY 24)
# , LowerElevationBalancingTier (POLICY 23), MidElevationReleaseTier (POLICY 22)
# , UpperElevationBalancingTierAprilthruSept (POLICY 21), UpperElevationBalancingTierJanthruMarch (POLICY 20)
# , EqualizationTier (POLICY 19)
####################################################################################
# NOTE: in these policies there are a lot of parameters are copied directly from CRSS simulation results
# because the Exploratory model don't have a way to calculate them.
# This policy can ONLY be used for validation!!!
####################################################################################
CRSS_Powell = True

# ==============Policy for Lake Mead=================
# Meet Lower basin demand
LB_demand = False

####################################################################################
# NOTE: We assume Lake Mead outflow = demands below Lake Mead (including Lake Mohave, Lake Hasvasu evaporation).
# Since the Exploratory model don't have a way to calculate, these parameters, we use CRSS simulation results directly.
# In Set Mead Outflow For Demands(CRSS policy 7), we export CurrentDemandBelowMead()
# as well as Mead.Diversion and Mead.Return Flow
# Demand in the Exploratory model = CurrentDemandBelowMead() + Mead.Diversion - Mead.Return Flow
# This policy can ONLY be used for validation!!!
####################################################################################
CRSS_Mead = True

# Protect Pearce Ferry Rapid
PFR = False

# Drought contingency plan, todo
DCP = False

# Intentional creat surplus, todo
ICS = False
# Release policy for each reservoir, which inflow scenario to use, which demand scenario to use, which signpost?
