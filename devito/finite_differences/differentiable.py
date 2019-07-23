from collections import ChainMap

import sympy
from sympy import S

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
    def dimensions(self):
        return tuple(filter_ordered(flatten(getattr(i, 'dimensions', ())
                                            for i in self._args_diff)))

    @cached_property
    def staggered(self):
        return tuple(filter_ordered(flatten(getattr(i, 'staggered', ())
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

    def eval_at(self, var):
        if not var.is_Staggered:
            return self
        # print([(a, type(a), getattr(a, 'eval_at', lambda x: a)(var)) for a in self.args])
        return self.func(*[getattr(a, 'eval_at', lambda x: a)(var) for a in self.args])

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

    def __mul__(self, other):
        return Mul(self, other)

    def __imul__(self, other):
        return Mul(self, other)

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

    def index(self, dim):
        inds = [self.dimensions[i] for i, d in enumerate(self.dimensions) if d == dim]
        return inds[0]

    @property
    def name(self):
        return "".join(f.name for f in self._functions)

    @property
    def laplace(self):
        """
        Generates a symbolic expression for the Laplacian, the second
        derivative w.r.t all spatial Dimensions.
        """
        space_dims = [d for d in self.dimensions if d.is_Space]
        derivs = tuple('d%s2' % d.name for d in space_dims)
        return Add(*[getattr(self, d) for d in derivs])

    @property
    def div(self):
        space_dims = [d for d in self.indices if d.is_Space]
        derivs = tuple('d%s' % d.name for d in space_dims)
        return Add(*[getattr(self, d) for d in derivs])

    @property
    def grad(self):
        from devito.types.tensor import VectorFunction, VectorTimeFunction
        comps = [getattr(self, 'd%s' % d.name) for d in self.dimensions if d.is_Space]
        vec_func = VectorTimeFunction if self.is_TimeDependent else VectorFunction
        return vec_func(name='grad_%s' % self.name, time_order=self.time_order,
                        space_order=self.space_order, components=comps, grid=self.grid)

    def laplace2(self, weight=1):
        """
        Generates a symbolic expression for the double Laplacian w.r.t.
        all spatial Dimensions.
        """
        space_dims = [d for d in self.dimensions if d.is_Space]
        derivs = tuple('d%s2' % d.name for d in space_dims)
        return Add(*[getattr(self.laplace * weight, d) for d in derivs])

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

    @classmethod
    def flatten(cls, seq):
        """
        Takes the sequence "seq" of nested Adds and returns a flatten list.
        Returns: (commutative_part, noncommutative_part, order_symbols)
        Applies associativity, all terms are commutable with respect to
        addition.
        NB: the removal of 0 is already handled by AssocOp.__new__
        See also
        ========
        sympy.core.mul.Mul.flatten
        """
        from sympy.calculus.util import AccumBounds
        from sympy.matrices.expressions import MatrixExpr
        from sympy.tensor.tensor import TensExpr
        rv = None
        if len(seq) == 2:
            a, b = seq
            if b.is_Rational:
                a, b = b, a
            if a.is_Rational:
                if b.is_Mul:
                    rv = [a, b], [], None
            if rv:
                if all(s.is_commutative for s in rv[0]):
                    return rv
                return [], rv[0], None

        terms = {}      # term -> coeff
                        # e.g. x**2 -> 5   for ... + 5*x**2 + ...

        coeff = S.Zero  # coefficient (Number or zoo) to always be in slot 0
                        # e.g. 3 + ...
        order_factors = []

        extra = []

        for o in seq:

            # O(x)
            if o.is_Order:
                for o1 in order_factors:
                    if o1.contains(o):
                        o = None
                        break
                if o is None:
                    continue
                order_factors = [o] + [
                    o1 for o1 in order_factors if not o.contains(o1)]
                continue

            # 3 or NaN
            elif o.is_Number:
                if (o is S.NaN or coeff is S.ComplexInfinity and
                        o.is_finite is False) and not extra:
                    # we know for sure the result will be nan
                    return [S.NaN], [], None
                if coeff.is_Number:
                    coeff += o
                    if coeff is S.NaN and not extra:
                        # we know for sure the result will be nan
                        return [S.NaN], [], None
                continue

            elif isinstance(o, AccumBounds):
                coeff = o.__add__(coeff)
                continue

            elif isinstance(o, MatrixExpr):
                # can't add 0 to Matrix so make sure coeff is not 0
                extra.append(o)
                continue

            elif isinstance(o, TensExpr):
                coeff = o.__add__(coeff) if coeff else o
                continue

            elif o is S.ComplexInfinity:
                if coeff.is_finite is False and not extra:
                    # we know for sure the result will be nan
                    return [S.NaN], [], None
                coeff = S.ComplexInfinity
                continue

            # Add([...])
            elif o.is_Add:
                # NB: here we assume Add is always commutative
                seq.extend(o.args)  # TODO zerocopy?
                continue

            # Mul([...])
            elif o.is_Mul:
                c, s = o.as_coeff_Mul()

            # check for unevaluated Pow, e.g. 2**3 or 2**(-1/2)
            elif o.is_Pow:
                b, e = o.as_base_exp()
                if b.is_Number and (e.is_Integer or
                                   (e.is_Rational and e.is_negative)):
                    seq.append(b**e)
                    continue
                c, s = S.One, o

            else:
                # everything else
                c = S.One
                s = o

            # now we have:
            # o = c*s, where
            #
            # c is a Number
            # s is an expression with number factor extracted
            # let's collect terms with the same s, so e.g.
            # 2*x**2 + 3*x**2  ->  5*x**2
            if s in terms:
                terms[s] += c
                if terms[s] is S.NaN and not extra:
                    # we know for sure the result will be nan
                    return [S.NaN], [], None
            else:
                terms[s] = c

        # now let's construct new args:
        # [2*x**2, x**3, 7*x**4, pi, ...]
        newseq = []
        noncommutative = False
        for s, c in terms.items():
            # 0*s
            if c is S.Zero:
                continue
            # 1*s
            elif c is S.One:
                newseq.append(s)
            # c*s
            else:
                if s.is_Mul:
                    # Mul, already keeps its arguments in perfect order.
                    # so we can simply put c in slot0 and go the fast way.
                    cs = s._new_rawargs(*((c,) + s.args))
                    newseq.append(cs)
                elif s.is_Add:
                    # we just re-create the unevaluated Mul
                    newseq.append(Mul(c, s, evaluate=False))
                else:
                    # alternatively we have to call all Mul's machinery (slow)
                    newseq.append(Mul(c, s))

            noncommutative = noncommutative or not s.is_commutative

        # oo, -oo
        if coeff is S.Infinity:
            newseq = [f for f in newseq if not (f.is_extended_nonnegative or f.is_real)]

        elif coeff is S.NegativeInfinity:
            newseq = [f for f in newseq if not (f.is_extended_nonpositive or f.is_real)]

        if coeff is S.ComplexInfinity:
            # zoo might be
            #   infinite_real + finite_im
            #   finite_real + infinite_im
            #   infinite_real + infinite_im
            # addition of a finite real or imaginary number won't be able to
            # change the zoo nature; adding an infinite qualtity would result
            # in a NaN condition if it had sign opposite of the infinite
            # portion of zoo, e.g., infinite_real - infinite_real.
            newseq = [c for c in newseq if not (c.is_finite and
                                                c.is_extended_real is not None)]

        # process O(x)
        if order_factors:
            newseq2 = []
            for t in newseq:
                for o in order_factors:
                    # x + O(x) -> O(x)
                    if o.contains(t):
                        t = None
                        break
                # x + O(x**2) -> x + O(x**2)
                if t is not None:
                    newseq2.append(t)
            newseq = newseq2 + order_factors
            # 1 + O(1) -> O(1)
            for o in order_factors:
                if o.contains(coeff):
                    coeff = S.Zero
                    break

        # order args canonically
        _addsort(newseq)

        # current code expects coeff to be first
        if coeff is not S.Zero:
            newseq.insert(0, coeff)

        if extra:
            newseq += extra
            noncommutative = True

        # we are done
        if noncommutative:
            return [], newseq, None
        else:
            return newseq, [], None


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


from functools import cmp_to_key


_args_sortkey = cmp_to_key(sympy.Basic.compare)


def _addsort(args):
    # in-place sorting of args
    args.sort(key=_args_sortkey)