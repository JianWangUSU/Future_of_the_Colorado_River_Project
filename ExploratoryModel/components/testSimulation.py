import datetime
import components.policyControl as policy
from dateutil.relativedelta import relativedelta
import calendar
import sys
import numpy as np

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



import matplotlib.pyplot as plt
import numpy as np

#plot 1:
x = np.array([0, 1, 2, 3])
y = np.array([3, 8, 1, 10])

plt.subplot(1, 2, 1)
plt.plot(x,y)

#plot 2:
x = np.array([0, 1, 2, 3])
y = np.array([10, 20, 30, 40])

plt.subplot(1, 2, 2)
plt.plot(x,y)

plt.show()

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