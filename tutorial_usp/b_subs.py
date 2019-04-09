from devito import Grid, TimeFunction, Coefficient
grid = Grid(shape=(4, 4))
u = TimeFunction(name='u', grid=grid, space_order=2, coefficients='symbolic')
x, y = grid.dimensions

import numpy as np
u_x_coeffs = Coefficient(1, u, x, np.array([-0.6, 0.1, 0.6])) # devito/finite_differences/coefficients.py
# u_x_coeffs
# u_x_coeffs.deriv_order
# u_x_coeffs.dimension
# u_x_coeffs.weigths


from devito import Substitutions
subs = Substitutions(u_x_coeffs)
# subs
# subs._rules

from devito import Eq
eq1 = Eq(u.dt+u.dx)
eq2 = Eq(u.dt+u.dx, coefficients=subs)
# eq1
# eq1


##

from devito import Eq, TimeFunction, Operator
u = TimeFunction(name='u', grid=grid)
op = Operator(Eq(u.forward, u + 1))

# u.data
# op.apply() !
# u.data
# op.apply(time_M = 1)
# u.data
# op.apply(time_M = 2)
# u.data
# run1 = op.apply(time_M = 1)
# u.data

# If no key-value parameters are specified, the Operator runs with its
# default arguments, namely ``u=u, x_m=0, x_M=2, y_m=0, y_M=2, time_m=0,
# time_M=1``.

# At this point, the same Operator can be used for a completely different
#run, for example

u2 = TimeFunction(name='u', grid=grid, save=5)
run2 = op.apply(u=u2, x_m=1, y_M=1)

# u2.data