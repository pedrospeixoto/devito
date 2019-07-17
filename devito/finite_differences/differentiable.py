from collections import ChainMap

import sympy
from sympy.functions.elementary.integers import floor
from sympy.core.evalf import evalf_table
from sympy.core.decorators import call_highest_priority

from cached_property import cached_property

from devito.tools import Evaluable, filter_ordered, flatten
from devito.logger import warning

__all__ = ['Differentiable']


class Differentiable(sympy.Expr, Evaluable):

    """
    A Differentiable is an algebric expression involving Functions, which can
    be derived w.r.t. one or more Dimensions.
    """

    # Set the operator priority higher than SymPy (10.0) to force the overridden
    # operators to be used
    _op_priority = sympy.Expr._op_priority + 1.

    _state = ('space_order', 'time_order', 'indices')

    @cached_property
    def _functions(self):
        return frozenset().union(*[i._functions for i in self._args_diff])

    @cached_property
    def _args_diff(self):
        ret = [i for i in self.args if isinstance(i, Differentiable)]
        ret.extend([i.function for i in self.args if i.is_Indexed])
        return tuple(ret)

    @cached_property
    def space_order(self):
        # Default 100 is for "infinitely" differentiable
        return min([getattr(i, 'space_order', 100) or 100 for i in self._args_diff],
                   default=100)

    @cached_property
    def time_order(self):
        # Default 100 is for "infinitely" differentiable
        return min([getattr(i, 'time_order', 100) or 100 for i in self._args_diff],
                   default=100)

    @cached_property
    def is_TimeDependent(self):
        # Default False, True if anything is time dependant in the expression
        return any(getattr(i, 'is_TimeDependent', False) for i in self._args_diff)

    @cached_property
    def is_VectorValued(self):
        # Default False, True if anything is time dependant in the expression
        return any(getattr(i, 'is_VectorValued', False) for i in self._args_diff)

    @cached_property
    def is_TensorValued(self):
        # Default False, True if anything is time dependant in the expression
        return any(getattr(i, 'is_TensorValued', False) for i in self._args_diff)

    @cached_property
    def is_Function(self):
        # Default False, True if anything is time dependant in the expression
        return any(getattr(i, 'is_Function', False) for i in self._args_diff)

    @cached_property
    def grid(self):
        # Default False, True if anything is time dependant in the expression
        grids = [getattr(i, 'grid', None) for i in self._args_diff]
        grid = set(grids)
        grid.discard(None)
        if len(grid) > 1:
            warning("Expression contains multiple grids, returning first found")
        return list(grid)[0]

    @cached_property
    def indices(self):
        return tuple(filter_ordered(flatten(getattr(i, 'indices', ())
                                            for i in self._args_diff)))

    @cached_property
    def is_Staggered(self):
        return any([getattr(i, 'is_Staggered', False) for i in self._args_diff])

    @cached_property
    def _fd(self):
        return dict(ChainMap(*[getattr(i, '_fd', {}) for i in self._args_diff]))

    @cached_property
    def _symbolic_functions(self):
        return frozenset([i for i in self._functions if i.coefficients == 'symbolic'])

    @cached_property
    def _uses_symbolic_coefficients(self):
        return bool(self._symbolic_functions)

    def __hash__(self):
        return super(Differentiable, self).__hash__()

    def __getattr__(self, name):
        """
        Try calling a dynamically created FD shortcut.

        Notes
        -----
        This method acts as a fallback for __getattribute__
        """
        if name in self._fd:
            return self._fd[name][0](self)
        raise AttributeError("%r object has no attribute %r" % (self.__class__, name))

    # Override SymPy arithmetic operators
    def __add__(self, other):
        return Add(self, other)

    def __iadd__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __isub__(self, other):
        return Add(self, -other)

    def __rsub__(self, other):
        return Add(other, -self)

    @call_highest_priority('__rmul__')
    def __mul__(self, other):
        return Mul(self, other)

    def __imul__(self, other):
        return Mul(self, other)

    @call_highest_priority('__mul__')
    def __rmul__(self, other):
        return Mul(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def __div__(self, other):
        return Mul(self, Pow(other, sympy.S.NegativeOne))

    def __rdiv__(self, other):
        return Mul(other, Pow(self, sympy.S.NegativeOne))

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def __floordiv__(self, other):
        return floor(self / other)

    def __rfloordiv__(self, other):
        return floor(other / self)

    def __mod__(self, other):
        return Mod(self, other)

    def __rmod__(self, other):
        return Mod(other, self)

    def __neg__(self):
        return Mul(sympy.S.NegativeOne, self)

    def __eq__(self, other):
        return super(Differentiable, self).__eq__(other) and\
            all(getattr(self, i, None) == getattr(other, i, None) for i in self._state)

    @property
    def name(self):
        return "".join(f.name for f in self._functions)

    @property
    def laplace(self):
        """
        Generates a symbolic expression for the Laplacian, the second
        derivative w.r.t all spatial Dimensions.
        """
        space_dims = [d for d in self.indices if d.is_Space]
        derivs = tuple('d%s2' % d.name for d in space_dims)
        return Add(*[getattr(self, d) for d in derivs])

    def laplace2(self, weight=1):
        """
        Generates a symbolic expression for the double Laplacian w.r.t.
        all spatial Dimensions.
        """
        space_dims = [d for d in self.indices if d.is_Space]
        derivs = tuple('d%s2' % d.name for d in space_dims)
        return sum([getattr(self.laplace * weight, d) for d in derivs])

    def diff(self, *symbols, **assumptions):
        """
        Like ``sympy.diff``, but return a ``devito.Derivative`` instead of a
        ``sympy.Derivative``.
        """
        from devito.finite_differences.derivative import Derivative
        return Derivative(self, *symbols, **assumptions)


class Add(sympy.Add, Differentiable):

    def __new__(cls, *args, **kwargs):
        obj = sympy.Add.__new__(cls, *args, **kwargs)

        # `(f + f)` is evaluated as `2*f`, with `*` being a sympy.Mul.
        # Here we make sure to return our own Mul.
        if obj.is_Mul:
            obj = Mul(*obj.args)

        return obj


class Mul(sympy.Mul, Differentiable):

    def __new__(cls, *args, **kwargs):
        obj = sympy.Mul.__new__(cls, *args, **kwargs)

        # `(f + g)*2` is evaluated as `2*f + 2*g`, with `+` being a sympy.Add.
        # Here we make sure to return our own Add.
        if obj.is_Add:
            obj = Add(*obj.args)

        # `(f * f)` is evaluated as `f**2`, with `**` being a sympy.Pow.
        # Here we make sure to return our own Pow.
        if obj.is_Pow:
            obj = Pow(*obj.args)

        return obj


class Pow(sympy.Pow, Differentiable):
    def __new__(cls, *args, **kwargs):
        obj = sympy.Pow.__new__(cls, *args, **kwargs)
        return obj


class Mod(sympy.Mod, Differentiable):
    def __new__(cls, *args, **kwargs):
        obj = sympy.Mod.__new__(cls, *args, **kwargs)
        return obj



# Make sure `sympy.evalf` knows how to evaluate the inherited classes
# Without these, `evalf` would rely on a much slower, much more generic, and
# thus much more time-inefficient fallback routine. This would hit us
# pretty badly when taking derivatives (see `finite_difference.py`), where
# `evalf` is used systematically
evalf_table[Add] = evalf_table[sympy.Add]
evalf_table[Mul] = evalf_table[sympy.Mul]
evalf_table[Pow] = evalf_table[sympy.Pow]
