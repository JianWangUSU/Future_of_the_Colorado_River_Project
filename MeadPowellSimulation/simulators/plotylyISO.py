import plotly.graph_objects as go
import numpy as np

X, Y, Z = np.mgrid[-5:5:40j, -5:5:40j, -5:5:40j]

# ellipsoid
values = X * X * 0.5 + Y * Y + Z * Z * 2

values2 = X  + Y  + Z 


fig = go.Figure(
    data=go.Isosurface(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    value=values.flatten(),
    isomin=10,
    isomax=40,
    caps=dict(x_show=False, y_show=False)
    ),
)

fig = go.Figure(data=go.Isosurface(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    value=values2.flatten(),
    isomin=10,
    isomax=40,
    caps=dict(x_show=False, y_show=False)
    ))

print(X.shape)
print(X.flatten().shape)
print(Y.flatten().shape)
print(Z.flatten().shape)
print(values.flatten().shape)

fig.show()