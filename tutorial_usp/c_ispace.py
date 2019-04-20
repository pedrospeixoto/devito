from devito import Grid, Eq
from devito.types import Array
from devito.ir.equations import LoweredEq
from devito.ir.support.basic import Scope, IterationInstance

grid = Grid((10))
x, = grid.dimensions

a = Array(name='a', shape=grid.shape, dimensions=grid.dimensions, scope='heap')
b = Array(name='b', shape=grid.shape, dimensions=grid.dimensions, scope='heap')
c = Array(name='c', shape=grid.shape, dimensions=grid.dimensions, scope='heap')
d = Array(name='d', shape=grid.shape, dimensions=grid.dimensions, scope='heap')


exprs1 = [LoweredEq(Eq(a[x], b[x] + c[x])),
        LoweredEq(Eq(d[x], a[x]))]

scope1 = Scope(exprs1)
scope1

dep1 = scope1.d_all[0]
dep1.is_flow
dep1.is_carried
dep1.cause

##

exprs2 = [LoweredEq(Eq(a[x], b[x] + c[x])),
        LoweredEq(Eq(d[x], a[x-1]))]

scope2 = Scope(exprs2)
scope2

dep2 = scope2.d_all[0]
dep2.is_flow
getattr(dep2, 'is_carried')()
dep2.cause

exprs3 = [LoweredEq(Eq(a[x], b[x] + c[x])),
          LoweredEq(Eq(d[x], a[x+10]))]

scope3 = Scope(exprs3)

len(getattr(scope1, 'd_flow'))
len(getattr(scope1, 'd_anti'))
len(getattr(scope2, 'd_flow'))
len(getattr(scope2, 'd_anti'))
len(getattr(scope3, 'd_flow'))
len(getattr(scope3, 'd_anti'))

##


IterationInstance


# scope1

# exprs3 = [LoweredEq(Eq(a[x], b[x] + c[x])),
#           LoweredEq(Eq(d[x], a[x-1]))]

# ### 


# from devito import Grid
# grid = Grid((3,3,3))
# x, y, z = grid.dimensions

# from devito.types import Array
# t0i = Array(name='t0i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')
# t1i = Array(name='t1i', shape=(3,5,7), dimensions=(x, y, z), scope='heap')

# from devito import Eq
# eqs = [Eq(t0i[x,y,z], t1i[x,y,z]),        # flow
#        Eq(t0i[x,y,z], t0i[x,y,z]),        # flow
#        Eq(t0i[x,y,z], t0i[x,y,z]),        # flow
#        Eq(t0i[x,y,z], t0i[x,y,z-1]),      # flow
#        Eq(t0i[x,y,z], t0i[x-1,y,z-1]),    # flow
#        Eq(t0i[x,y,z], t0i[x-1,y,z+1]),
#        Eq(t0i[x,y,z], t0i[x+1,y+2,z]),
#        Eq(t0i[x,y,z], t0i[x,y+2,z-3])]

# # # print(eqs[0].ispace) !

# # from devito.ir.equations import LoweredEq
# # exprs = [LoweredEq(i) for i in eqs]

# # for i in exprs:
# #     print(i.ispace)