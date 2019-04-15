from devito import Grid, TimeFunction
grid = Grid((3,3,3))
tu = TimeFunction(name='tu', grid=grid)
tui = tu.indexify() #devito/symbolics/manipulation.py

# tu
# tui
# type(tui)
# tu.indices
# tui.indices
# tui.function
# tu.function
# tui.base
# tu.base !
# tu.size
# tu.data
# tui.size !
# tui.function.size

# tu.dx
# tu.forward
# tui.forward !
# tui2 = tu.forward.indexify()
# tui == tui2 (False)
# tui2.function == tui.functon (True)

x, y, z = grid.dimensions
from devito.types import Array
t0 = Array(name='t0', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
t0i = t0.indexify() 

# t0.data ! ?