import datetime
import components.PolicyControl as policy
from dateutil.relativedelta import relativedelta
import calendar
import sys
import numpy as np


def test():
    return 1,2,3

x = test()
a = x[0]
b = x[1]
print(a)
print(b)


# For developers, test purpose

from dateutil.relativedelta import relativedelta

# print(datetime.date.today())
# print(datetime.date.today() - relativedelta(months=+1))
#
# x = datetime.datetime(2020, 1, 1)
# y = x + relativedelta(months=+0)
#
#

# releaseTemp = [[5,1],[2,3]]
# print(releaseTemp[0][0])
# print(releaseTemp[0][1])
# print(releaseTemp[1][0])
# print(releaseTemp[1][1])

# print(sum(releaseTemp[0:2][0]))
# print(len(releaseTemp[0:3]))
# print(sum(releaseTemp[0:4]))

# print(sum(range(0,4)))



# import matplotlib.pyplot as plt
# import numpy as np
#
# #plot 1:
# x = np.array([0, 1, 2, 3])
# y = np.array([3, 8, 1, 10])
#
# plt.subplot(1, 2, 1)
# plt.plot(x,y)
#
# #plot 2:
# x = np.array([0, 1, 2, 3])
# y = np.array([10, 20, 30, 40])
#
# plt.subplot(1, 2, 2)
# plt.plot(x,y)
#
# plt.show()

# arr = [20, 2, 5, 7, 34]
# print("arr : ", arr)
# print("50th percentile of arr : ",
#        np.percentile(arr, 50))
# print("25th percentile of arr : ",
#        np.percentile(arr, 25))
# print("75th percentile of arr : ",
#        np.percentile(arr, 75))

# for m in range(12):
#     print(m)
# print(sys.maxsize)
# print(calendar.monthrange(2020, 2)[1])
# begtime = datetime.datetime(2021, 1, 31)
# currentTime = begtime + relativedelta(months=+0)# x = [1,5,3]
# days = calendar.monthrange(currentTime.year, currentTime.month)[1]
#
# print(currentTime)
# print(days)
# print(sum(x))

# for i in range(0, 9):
#     print(i)
# print(calendar.isleap(x.year))
#
# print(c.monthrange(x.year, x.month))

# print(x.strftime("%b %Y"))
# x= x + relativedelta(months=+1)
# print(x.strftime("%b %Y"))

# print(policy.EQUAL)

# for col in range(0, 4):
#     print(col)

# test = [5,1,2,3]
#
# print(sum(test[1:4]))
# print(test[0:4])
#
# print(datetime.datetime(2008,11,1))
#
# x = datetime.datetime(2018, 9, 15)
#
#
# print(x.strftime("%b %Y"))

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# df = px.data.iris()
# print(df)

# df = pd.read_csv('../tools/parallel.csv')
# df = pd.read_csv('../tools/parallel1.csv')
# df = pd.read_csv('../tools/parallel2.csv')
# df = pd.read_csv('../tools/parallel3.csv')

# df = pd.read_csv('../tools/parallel_empty.csv')
df = pd.read_csv('../tools/parallel_empty8.csv')

# df2 = df.sort_values(by=["sepal_length"], ascending=True)
# df.to_csv('../tools/parallel2.csv')
# df.to_csv('../tools/parallel.csv')
# print(df2)

# fig = px.parallel_coordinates(df2, color="species_id", labels={"species_id": "Species",
#                 "sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
#                 "petal_width": "Petal Width", "petal_length": "Petal Length", },
#                              color_continuous_scale=px.colors.diverging.Tealrose,
#                              color_continuous_midpoint=2)
# fig = px.parallel_coordinates(df, color="Release_Mead",
#                                   dimensions=['InitStorage_Powell','Inflow_Powell','Release_Powell','InitStorage_Mead','Release_Mead','YearsToEmpty'],
#                                   color_continuous_scale=px.colors.diverging.Tealrose, color_continuous_midpoint=20)

# fig = go.Figure(data=
#     go.Parcoords(
#         line = dict(color = df['YearsTo12MAF'],
#                    colorscale = 'reds_r',
#                    showscale = True),
#         dimensions = list([
#             dict(range = [12,40],
#                 label = 'InitStorage(Powell&Mead)', values = df['InitStorage(Powell&Mead)']),
#             dict(range = [3,11.5],
#                 label = 'Inflow_Powell', values = df['Inflow_Powell']),
#             dict(range = [3,11.5],
#                 label = 'Release_Mead', values = df['Release_Mead']),
#             dict(range = [0,40],
#                 label = 'YearsTo12MAF', values = df['YearsTo12MAF']),
#         ])
#     )
# )

# fig = px.parallel_coordinates(df, color="YearsTo12MAF",
#                               dimensions= list([dict(range = [12,40], label = 'InitStorage(Powell&Mead)', values = df['InitStorage(Powell&Mead)']),
#                                                 dict(range = [3,15.5], label = 'Inflow_Powell', values = df['Inflow_Powell']),
#                                                 dict(range = [3,11.5], label = 'Release_Mead', values = df['Release_Mead']),
#                                                 dict(range = [0,40], label = 'YearsTo12MAF', values = df['YearsTo12MAF']),]),
#                               color_continuous_scale='reds_r', color_continuous_midpoint=20)

fig = px.parallel_coordinates(df, color="YearsTo12MAF",
                              dimensions=['InitStorage(Powell&Mead)', 'Inflow_Powell', 'Release_Mead', 'YearsTo12MAF'],
                              color_continuous_scale='reds_r', color_continuous_midpoint=20)

# fig = px.parallel_coordinates(df, color="YearsToEmpty",
#                               dimensions=['InitStorage(Powell&Mead)', 'Inflow_Powell', 'Release_Mead', 'YearsToEmpty'],
#                               color_continuous_scale='reds_r', color_continuous_midpoint=20)

fig.show()

# compression_opts = dict(method='zip',archive_name='out.csv')
# df.to_csv('out.zip', index=False,compression=compression_opts)

# import pandas as pd
# import matplotlib.pyplot as plt
#
# df = pd.read_csv(
#     'https://raw.github.com/pandas-dev/'
#     'pandas/master/pandas/tests/io/data/csv/iris.csv')
#
# pd.plotting.parallel_coordinates(
#     df, 'Name', color=('#556270', '#4ECDC4', '#C7F464')
# )
#
# plt.show()
