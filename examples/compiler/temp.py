from devito import Grid
grid = Grid((3,3,3))
x, y, z = grid.dimensions

from devito.types import Array
t0 = Array(name='t0', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
t0i = t0.indexify()




###

from devito.tools import as_tuple

# Took from `devito/tests/conftest.py`
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



from devito import Grid

grid = Grid((3,3,3))
t = grid.time_dim
x, y, z = grid.dimensions


from devito.types import Array

t0 = Array(name='ti0', shape=(3,5,7), dimensions=(x, y, z), scope='heap')


ti1 = Array(name='ti1', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
ti3 = Array(name='ti0', shape=(3,5), dimensions=(x, y), scope='heap')


from devito import TimeFunction

tu = TimeFunction(name='tu', grid=grid, space_order=4).indexify()
tv = TimeFunction(name='tv', grid=grid, space_order=4).indexify()
tw = TimeFunction(name='tw', grid=grid, space_order=4)


from devito import Eq

expr1 = ('Eq(tu[t,x,y,z], tu[t,x,y,z] + tv[t,x,y,z])',
         'Eq(tv[t,x,y,z], tu[t,x,y,z+2])',
         'Eq(tu[t,x,y,0], tu[t,x,y,0] + 1.)')

eq1 = EVAL(expr1, tu.base, tv.base)


from devito import Operator

op = Operator(eq1, dse='noop', dle='noop')


from devito.tools import pprint

pprint(op)  