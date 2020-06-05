from matplotlib import pyplot as plt
import pandas as pd

df = pd.read_csv('https://raw.github.com/pandas-dev/pandas/master'
                    '/pandas/tests/data/iris.csv')
pd.plotting.parallel_coordinates(
        df, 'Name',
        color=('#556270', '#4ECDC4', '#C7F464'))
plt.show()

print(df)

# xx1 = np.zeros(xLength*yLength)
# yy1 = np.zeros(xLength*yLength)
# zz1 = np.zeros(xLength*yLength)
# Name1 = np.zeros(xLength*yLength)
#
# for i in range(0, xLength):
#     for j in range(0, yLength):
#         xx1[i*yLength+j] = x[i]
#         yy1[i*yLength+j] = y[j]
#         zz1[i*yLength+j] = z1[i][j]
#         Name1[i*yLength+j] = 1
#
# xx2 = np.zeros(xLength*yLength)
# yy2 = np.zeros(xLength*yLength)
# zz2 = np.zeros(xLength*yLength)
# Name2 = np.zeros(xLength*yLength)
#
# for i in range(0, xLength):
#     for j in range(0, yLength):
#         xx2[i*yLength+j] = x[i]
#         yy2[i*yLength+j] = y[j]
#         zz2[i*yLength+j] = z2[i][j]
#         Name2[i*yLength+j] = 2
#
# xx3 = np.zeros(xLength*yLength)
# yy3 = np.zeros(xLength*yLength)
# zz3 = np.zeros(xLength*yLength)
# Name3 = np.zeros(xLength*yLength)
#
# for i in range(0, xLength):
#     for j in range(0, yLength):
#         xx3[i*yLength+j] = x[i]
#         yy3[i*yLength+j] = y[j]
#         zz3[i*yLength+j] = z3[i][j]
#         Name3[i*yLength+j] = 3
#
# xx = np.hstack((xx1,xx2,xx3))
# yy = np.hstack((yy1,yy2,yy3))
# zz = np.hstack((zz1,zz2,zz3))
# Name = np.hstack((Name1,Name2,Name3))
#
# data = {'demand':xx,'inflow':yy,'year':zz, 'Name':Name}
# df = pd.DataFrame(data)
#
# fig = go.Figure(data=
#     go.Parcoords(
#         line = dict(color = df['Name'], colorscale = [[0,'purple'],[0.5,'lightseagreen'],[1,'gold']]),
#         dimensions = list([
#             dict(range = [6,12],
#                 label = 'demand', values = df['demand']),
#             dict(range = [6,16],
#                 label = 'inflow', values = df['inflow']),
#             dict(range = [0,60],
#                 label = 'years', values = df['year']),
#         ])
#     )
# )
#
# fig.update_layout(
#     plot_bgcolor = 'white',
#     paper_bgcolor = 'white'
# )
#
# fig.show()