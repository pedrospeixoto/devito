# Took from `devito/tests/conftest.py`
from devito.tools import as_tuple
def EVAL(exprs, *args):
    scope = {}
    for i in args:
            scope[i.name] = i
            for j in i.function.indices:
                scope[j.name] = j
    processed = []
    for i in as_tuple(exprs):
        processed.append(eval(i, globals(), scope))
    return processed[0] if isinstance(exprs, str) else processed


##
from devito import Grid
grid = Grid((3,3,3))
x, y, z = grid.dimensions

from devito.types import Array
t0i = Array(name='t0i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
t1i = Array(name='t1i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')



exprs = ['Eq(t0i[x,y,z], t1i[x,y,z])',
         'Eq(t1i[x,y,z], t0i[x,y,z])']

from devito import Eq
eq1, eq2 =  EVAL(exprs, t0i, t1i)

from devito.ir.equations import LoweredEq
expr1 = LoweredEq(eq1)
expr2 = LoweredEq(eq2)

# print(eq1)
# print(expr1)
# print(eq1 == expr1)
