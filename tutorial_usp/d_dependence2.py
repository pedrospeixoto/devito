from devito import Grid
grid = Grid((10))
x = grid.dimensions

from devito.types import Array
a = Array(name='a', shape=(10), dimensions=(x), scope='heap')
b = Array(name='b', shape=(10), dimensions=(x), scope='heap')
c = Array(name='c', shape=(10), dimensions=(x), scope='heap')
d = Array(name='d', shape=(10), dimensions=(x), scope='heap')


from devito import Eq
s1 = Eq(a[x], b[x] + c[x])
s2 = Eq(d[x], a[x])

from devito.ir.equations import LoweredEq
expr1 = LoweredEq(s1)
expr2 = LoweredEq(s2)

from devito.ir.support.basic import Scope
scope1 = Scope([expr1, expr2])
scope1

scope1.d_all

##

e1 = LoweredEq(Eq(a[x], b[x] + c[x]))
e2 = LoweredEq(Eq(d[x], a[x]))

scope2 = Scope([e1, e2])
scope1 == scope2

scope2
