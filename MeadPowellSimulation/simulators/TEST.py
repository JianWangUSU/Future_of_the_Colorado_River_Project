# This code reads a results of WQ samplings from a lake at various time and locations by
# several researchers
# The code does the following steps#
# 1) reads the .csv files
# 2) calculates the mean and standard deviations of samples at taken a particular date (by all researcher)
# 3) fills the gap between dates to have a consistent data set from the beginning to the end of all samplings
# 4) plots a time series of the variables versus water level

# This code has been written by Somayeh Sima in 6/1/2019
#----------------------------------------------------
# Import the Pandas and Matplotlib and other packages
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sci
import numpy as np
from numpy import *
from scipy.stats import *
import seaborn as sns

# Determine the temporal range of your data
beginDate = '06-01-1977'
endDate = '25-08-2017'
idx = pd.date_range(beginDate, endDate)


# Define the name of authors who you are using their data as a unique list
r=['Kelts and Shahrabi,1986', 'Daneshvar& Ashasi,1995',  'Alipur,2006',
    'Hafezieh, 2016','Asem et al.,2007','Karbasi et al.,2010', 'sima & Tajrishy, 2015', 'EAWB']

# Define the name of water quality parameters (header line of the .csv files)
Parameters_list=['water_level','TDS','Na','Mg','SO4','Cl','HCO3','K','Ca']

#read and merge dataframes of ionic composition and TDs
dicMean={}
dicStd={}
df={}

#create a blank dictionary for each parameter
for n, p in enumerate(Parameters_list):
    globals()['Mean_%s'%p]={}
    globals()['Std_%s'%p]={}

# Notice that the name of csv files is the first 6 letters of the reference (authors)
for i , dr in enumerate(r):
        dfname=(dr[0:6])
        # set the path of your .csv files
        csv_FilesPath = r'C:\Users\somay\PycharmProjects\PyCodes\ULplots_PNAS\TDS_Ions_Timeseries\WQCSV_InputFiles\\'
        name = dfname.strip() + '.csv'
        df = pd.read_csv(csv_FilesPath + name, header=0, sep=',',
                         index_col=0, parse_dates=True,
                         infer_datetime_format=True, low_memory=False)