Colorado River Futures - Code Projects
An exploratory model for reservoir simualtion

Author: Jian Wang, Utah State University, jian.wang@usu.edu

Description
An open-source exploratory model is developed to assist in Colorado River long term planning and management. The exploratory model complements existing simulation models by offering greater flexibility and speed to set up scenarios for uncertain future conditions and generate adaptive policies. The current version of this model includes two largest reservoirs in the Colorado River Basin, besides reservoir simulation model, it also connects with a reservoir release temperature model, which will help evaluate water supply decisions on reservoir release temperature response. This model is validated against the Colorado River Simulation System (CRSS), an official model currently used for the Colorado River basin. With the exploratory model, we develop and test an adaptive depletion to inflow policy, which is different from existing operating policies in the Colorado River. The adaptive policy takes advantage of the latest inflow information every year and provides a more sustainable way to operate the Colorado River system. This strategy offers a new way to manage the Colorado River system. 


Run Code


How to write your own release policy?

Step 1:
In ../components/policyControl.py, define policy name

Step 2:
In ../components/ReleaseFunction.py, define policy details. "def FPF(reservoir, EYstorage, t):" function is an example of Fill Powell First 

Step 3:
In ../components/LakePowell.py or ../components/LakeMead.py , under "def releasePolicy(self, startStorage, k, i, t):" function, add your policy judgement and return the policy you defined in step 2. Note you need to return reservoir release 

Step 4: 
In  ../components/PolicyControl.py, add your policy and make it active by setting "True" to it, at the same time set other polilcies by "False"