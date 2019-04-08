from devito import Grid
grid = Grid((3,3,3))
x, y, z = grid.dimensions

from devito.types import Array
t0 = Array(name='t0', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
t0i = t0.indexify() #devito/symbolics/manipulation.py

# t0
# t0i
# type(t0i)
# t0.indices
# t0i.indices
# t0i.function
# t0i.function
# t0i.base
# t0.base !
# t0.size
# t0i.size !
# t0i.function.size

