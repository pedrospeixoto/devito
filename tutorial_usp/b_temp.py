# Took from `devito/tests/conftest.py`
from devito.tools import as_tuple
def EVAL(exprs, *args):
    scope = {}
    for i in args:
        try:
            scope[i.name] = i
            for j in i.base.function.indices:
                scope[j.name] = j
        except AttributeError:
            scope[i.label.name] = i
            for j in i.function.indices:
                scope[j.name] = j
    processed = []
    for i in as_tuple(exprs):
        processed.append(eval(i, globals(), scope))
    return processed[0] if isinstance(exprs, str) else processed

#

from devito import Grid
grid = Grid((3,3,3))
x, y, z = grid.dimensions

from devito import TimeFunction

tu = TimeFunction(name='tu', grid=grid, space_order=4).indexify()
tv = TimeFunction(name='tv', grid=grid, space_order=4).indexify()

from devito import Eq

# eq1 = Eq(tu[t,x,y,z], tu[t,x,y,z] + tv[t,x,y,z])


expr1 = ('Eq(tu[t,x,y,z], tu[t,x,y,z] + tv[t,x,y,z])')
eq1 = EVAL(expr1, tu.base, tv.base)

