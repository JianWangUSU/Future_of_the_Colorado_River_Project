
# https://stackoverflow.com/questions/29846087/microsoft-visual-c-14-0-is-required-unable-to-find-vcvarsall-bat
# http://docs.enthought.com/mayavi/mayavi/installation.html#installing-with-pip

import numpy as np
import mayavi.mlab as mlab

print(type(6j))

# a=64
# f=str(a)+"j"
# print(f)
# print(type(f))
#
# mm = complex(0,f)
# print(mm)
# print(type(mm))

mlab.clf()

x, y, z = np.mgrid[-5:5:64j, -5:10:20j, -5:5:64j]

values = x*x*0.5 + y*y + z*z*2.0
print(x.shape)
print(y.shape)
print(z.shape)
print(values.shape)
mlab.contour3d(x,y,z,values)
# pl = mlab.surf(x, y, z, warp_scale="auto")
mlab.axes(xlabel='x', ylabel='y', zlabel='z')

mlab.outline()

mlab.show()

