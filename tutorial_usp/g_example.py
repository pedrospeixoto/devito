# Run with:
# DEVITO_BACKEND='ops' python g_example.py

# from sympy import solve
# from devito import Grid, TimeFunction, Operator
# from devito.equation import Eq

# grid = Grid(shape=(3, 3))

# u = TimeFunction(name='u', grid=grid)
# eq = Eq(u.forward, u+1)
# op = Operator(eq)

##

import numpy as np

from examples.seismic import Model, plot_velocity, TimeAxis, RickerSource
from devito import TimeFunction, Eq, solve, Operator

grid_points = 10
# Define a physical size
shape = (grid_points, grid_points, grid_points)  # Number of grid point (nx, nz)
spacing = (1., 1., 1.)  # Grid spacing in m. The domain size is now 1km by 1km
# What is the location of the top left corner. This is necessary to define
origin = (0., 0., 0.)

# single layer velocity model in km/s
v = np.empty(shape, dtype=np.float32)
v[:, :, :] = 2
# v[:, :int(grid_points/2), :] = 1.5
# v[:, int(grid_points/2):, :] = 2.5


# With the velocity and model size defined, we can create the seismic model that
# encapsulates this properties. We also define the size of the absorbing layer as 10 grid points
model = Model(vp=v, origin=origin, shape=shape, spacing=spacing,
              space_order=2, nbpml=10)


dt = 0.001  # Time step from model grid spacing
t0 = 0.  # Simulation starts a t=0
tn = 30.  # Simulation last 1 second (1000 ms)

time_range = TimeAxis(start=t0, stop=tn, step=dt)

# Define the wavefield with the size of the model and the time dimension
u = TimeFunction(name="u", grid=model.grid, time_order=2, space_order=2)

# Write PDE.
pde = model.m * u.dt2 - u.laplace + model.damp * u.dt

# Solve equation for u[t1]
stencil = Eq(u.forward, solve(pde, u.forward))
print(stencil)

op = Operator([stencil], subs=model.spacing_map)

# print(op)