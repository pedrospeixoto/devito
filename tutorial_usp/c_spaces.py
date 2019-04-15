# extracted from `IntervalGroup.generate`, in `devito/ir/support/space.py`

from devito import dimensions
from devito.ir.support import IntervalGroup, Interval

x, y, z = dimensions('x y z')
ig0 = IntervalGroup([Interval(x, 1, -1)])
ig1 = IntervalGroup([Interval(x, 2, -2), Interval(y, 3, -3)])
ig2 = IntervalGroup([Interval(y, 2, -2), Interval(z, 1, -1)])

igg = IntervalGroup.generate('intersection', ig0, ig1, ig2)



# Took from `devito/tests/conftest.py`
# from devito.tools import as_tuple
# def EVAL(exprs, *args):
#     scope = {}
#     for i in args:
#         scope[i.name] = i
#         for j in i.function.indices:
#             scope[j.name] = j
#     processed = []
#     for i in as_tuple(exprs):
#         print(i)
#         print(scope)
#         processed.append(eval(i, globals(), scope))
#     return processed[0] if isinstance(exprs, str) else processed


##
from devito import Grid
grid = Grid((3,3,3))
x, y, z = grid.dimensions

from devito.types import Array
t0i = Array(name='t0i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
t1i = Array(name='t1i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')

from devito import Eq
eq1 = Eq(t0i[x,y,z], t1i[x,y,z])
eq2 = Eq(t1i[x,y,z], t0i[x,y,z])



eqs = [Eq(t0i[x,y,z], t1i[x,y,z]),
       Eq(t0i[x,y,z], t0i[x,y,z]),
       Eq(t0i[x,y,z], t0i[x,y,z]),
       Eq(t0i[x,y,z], t0i[x,y,z-1]),
       Eq(t0i[x,y,z], t0i[x-1,y,z-1]),
       Eq(t0i[x,y,z], t0i[x-1,y,z+1]),
       Eq(t0i[x,y,z], t0i[x+1,y+2,z]),
       Eq(t0i[x,y,z], t0i[x,y+2,z-3])]

from devito.ir.equations import LoweredEq
exprs = [LoweredEq(i) for i in eqs]

for i in exprs:
    print(i.ispace)

# print(eq1)
# print(expr1)
# eq1 == expr1
# eq1.dspace !
# expr1.dspace
# expr1.ispace
# expr1.ispace.directions
