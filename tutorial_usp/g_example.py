# Run with:
# DEVITO_BACKEND='ops' python g_example.py

from sympy import solve
from devito import Grid, TimeFunction, Operator
from devito.equation import Eq

grid = Grid(shape=(3, 3))
u = TimeFunction(name='u', grid=grid)
eq = Eq(u.forward, u+1)
op = Operator(eq)

##

u = TimeFunction(name='u', grid=grid, space_order=2, time_order=2)
m = TimeFunction(name='m', grid=grid)

eq = Eq(m * u.dt2 - u.laplace)
# print(type(eq))


stencil = solve(eq, u.forward)[0]
print(stencil)
op = Operator(stencil)
