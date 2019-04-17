from devito.types import Scalar, Constant

A = Scalar(name='A')
B = Scalar(name='C')
C = Scalar(name='C')
D = Scalar(name='D')

from devito import Eq

eqs = [Eq(A,1),
       Eq(B,A+2),
       Eq(A,C-D),
       Eq(A,B/C)]

from devito.ir.equations import LoweredEq
exprs = [LoweredEq(i) for i in eqs]

from devito.ir.support.basic import Scope
scope = Scope(exprs)
print(scope)

deps = scope.d_flow
print(deps)



# for i in exprs:
#     print(i.ispace._directions)

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

# # print(eqs[0].ispace) !

# from devito.ir.equations import LoweredEq
# exprs = [LoweredEq(i) for i in eqs]

# for i in exprs:
#     print(i.ispace)