How to write your own release policy?

Step 1:
In ../components/policyControl.py, define policy name

Step 2:
In ../components/ReleaseFunction.py, define policy details. "def FPF(reservoir, EYstorage, t):" function is an example of Fill Powell First 

Step 3:
In ../components/LakePowell.py or ../components/LakeMead.py , under "def releasePolicy(self, startStorage, k, i, t):" function, add your policy judgement and return the policy you defined in step 2. Note you need to return reservoir release 

Step 4: 
In  ../simulation/start.py, in section "### 3.set policies", add your policy and make it active by setting "True" to it, at the same time set other polilcies by "False"
