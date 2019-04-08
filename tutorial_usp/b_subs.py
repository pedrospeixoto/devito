from devito import Grid, TimeFunction, Coefficient
grid = Grid(shape=(4, 4))

u = TimeFunction(name='u', grid=grid, space_order=2, coefficients='symbolic')
x, y = grid.dimensions

u_x_coeffs = Coefficient(1, u, x, np.array([-0.6, 0.1, 0.6]))

from devito import Substitutions

subs = Substitutions(u_x_coeffs)

from devito import Eq
Eq(u.dt+u.dx, coefficients=subs)