from devito import Eq, Grid, TimeFunction, Operator

grid = Grid((3,3))
u = TimeFunction(name='u', grid=grid)
eq = Eq(u.forward, u+1)
op = Operator(eq)

print(op)


