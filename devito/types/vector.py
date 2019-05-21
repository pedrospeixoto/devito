import sympy

from cached_property import cached_property

from devito.finite_differences import Differentiable, generate_fd_shortcuts
from devito.types.basic import Cached, _SymbolCache
from devito.types.dense import Function, TimeFunction

__all__ = ['VectorFunction', 'VectorTimeFunction']

class VectorFunction(sympy.Matrix, Cached):
    """
    Discretized symbol representing an array in symbolic equations.

    A Function carries multi-dimensional data and provides operations to create
    finite-differences approximations.

    A Function encapsulates space-varying data; for data that also varies in time,
    use TimeFunction instead.

    Parameters
    ----------
    name : str
        Name of the symbol.
    grid : Grid, optional
        Carries shape, dimensions, and dtype of the Function. When grid is not
        provided, shape and dimensions must be given. For MPI execution, a
        Grid is compulsory.
    space_order : int or 3-tuple of ints, optional
        Discretisation order for space derivatives. Defaults to 1. ``space_order`` also
        impacts the number of points available around a generic point of interest.  By
        default, ``space_order`` points are available on both sides of a generic point of
        interest, including those nearby the grid boundary. Sometimes, fewer points
        suffice; in other scenarios, more points are necessary. In such cases, instead of
        an integer, one can pass a 3-tuple ``(o, lp, rp)`` indicating the discretization
        order (``o``) as well as the number of points on the left (``lp``) and right
        (``rp``) sides of a generic point of interest.
    shape : tuple of ints, optional
        Shape of the domain region in grid points. Only necessary if ``grid`` isn't given.
    dimensions : tuple of Dimension, optional
        Dimensions associated with the object. Only necessary if ``grid`` isn't given.
    dtype : data-type, optional
        Any object that can be interpreted as a numpy data type. Defaults
        to ``np.float32``.
    staggered : Dimension or tuple of Dimension or Stagger, optional
        Define how the Function is staggered.
    padding : int or tuple of ints, optional
        Allocate extra grid points to maximize data access alignment. When a tuple
        of ints, one int per Dimension should be provided.
    initializer : callable or any object exposing the buffer interface, optional
        Data initializer. If a callable is provided, data is allocated lazily.
    allocator : MemoryAllocator, optional
        Controller for memory allocation. To be used, for example, when one wants
        to take advantage of the memory hierarchy in a NUMA architecture. Refer to
        `default_allocator.__doc__` for more information.

    Examples
    --------
    Creation

    >>> from devito import Grid, Function
    >>> grid = Grid(shape=(4, 4))
    >>> f = Function(name='f', grid=grid)
    >>> f
    f(x, y)
    >>> g = Function(name='g', grid=grid, space_order=2)
    >>> g
    g(x, y)

    First-order derivatives through centered finite-difference approximations

    >>> f.dx
    Derivative(f(x, y), x)
    >>> f.dy
    Derivative(f(x, y), y)
    >>> g.dx
    Derivative(g(x, y), x)
    >>> (f + g).dx
    Derivative(f(x, y) + g(x, y), x)

    First-order derivatives through left/right finite-difference approximations

    >>> f.dxl
    Derivative(f(x, y), x)
    >>> g.dxl
    Derivative(g(x, y), x)
    >>> f.dxr
    Derivative(f(x, y), x)

    Second-order derivative through centered finite-difference approximation

    >>> g.dx2
    Derivative(g(x, y), (x, 2))

    Notes
    -----
    The parameters must always be given as keyword arguments, since SymPy
    uses ``*args`` to (re-)create the dimension arguments of the symbolic object.
    """
    is_TimeFunction = False
    is_SparseTimeFunction = False
    sub_type = Function
    is_MatrixLike = True
    is_Matrix = False

    def __new__(cls, *args, **kwargs):
        options = kwargs.get('options', {})
        if cls in _SymbolCache:
            newobj = sympy.Matrix.__new__(cls, *args, **options)
            newobj._cached_init()
        else:
            options = kwargs.get('options', {})
            name = kwargs.pop('name')
            # Number of dimensions
            grid = kwargs.get('grid')
            comps = kwargs.get("components",
                               [cls.sub_type(name=name+"_%s"%d.name, **kwargs)
                                for d in grid.dimensions])

            # Create the new Function object and invoke __init__
            newobj = sympy.Matrix.__new__(cls, comps)

            # Initialization. The following attributes must be available
            # when executing __init__
            newobj._indices = cls.__indices_setup__(**kwargs)
            # All objects cached on the AbstractFunction /newobj/ keep a reference
            # to /newobj/ through the /function/ field. Thus, all indexified
            # object will point to /newobj/, the "actual Function".
            newobj.function = newobj
            # Store new instance in symbol cache
            newobj._cache_put(newobj)

        return newobj

    def __getattr__(self, name):
        """
        Try calling a dynamically created FD shortcut.

        Notes
        -----
        This method acts as a fallback for __getattribute__
        """
        if name in self[0]._fd:
            return self.xreplace({c: getattr(c, name) for c in self})
        raise AttributeError("%r object has no attribute %r" % (self.__class__, name))

    @classmethod
    def __indices_setup__(cls, **kwargs):
        grid = kwargs.get('grid')
        dimensions = kwargs.get('dimensions')
        if grid is None:
            if dimensions is None:
                raise TypeError("Need either `grid` or `dimensions`")
        elif dimensions is None:
            dimensions = grid.dimensions
        return dimensions

    @property
    def indices(self):
        return self._indices

    @property
    def grid(self):
        return self._grid

    @property
    def ndim(self):
        return self._ndim

    @property
    def name(self):
        return self._name

    @property
    def space_order(self):
        return self._space_order

    @property
    def evaluate(self):
        return self.xreplace({c: c.evaluate for c in self})

    @property
    def div(self):
        return sum(getattr(c, "d%s"%d) for c, d in zip(self, self.indices))

    def __str__(self):
        st = ''.join([' %-2s,' % c for c in self])[1:-1]
        return "Vector(%s)"%st

    __repr__ = __str__

class VectorTimeFunction(VectorFunction):
    """
    Discretized symbol representing an array in symbolic equations.

    A Function carries multi-dimensional data and provides operations to create
    finite-differences approximations.

    A Function encapsulates space-varying data; for data that also varies in time,
    use TimeFunction instead.

    Parameters
    ----------
    name : str
        Name of the symbol.
    grid : Grid, optional
        Carries shape, dimensions, and dtype of the Function. When grid is not
        provided, shape and dimensions must be given. For MPI execution, a
        Grid is compulsory.
    space_order : int or 3-tuple of ints, optional
        Discretisation order for space derivatives. Defaults to 1. ``space_order`` also
        impacts the number of points available around a generic point of interest.  By
        default, ``space_order`` points are available on both sides of a generic point of
        interest, including those nearby the grid boundary. Sometimes, fewer points
        suffice; in other scenarios, more points are necessary. In such cases, instead of
        an integer, one can pass a 3-tuple ``(o, lp, rp)`` indicating the discretization
        order (``o``) as well as the number of points on the left (``lp``) and right
        (``rp``) sides of a generic point of interest.
    shape : tuple of ints, optional
        Shape of the domain region in grid points. Only necessary if ``grid`` isn't given.
    dimensions : tuple of Dimension, optional
        Dimensions associated with the object. Only necessary if ``grid`` isn't given.
    dtype : data-type, optional
        Any object that can be interpreted as a numpy data type. Defaults
        to ``np.float32``.
    staggered : Dimension or tuple of Dimension or Stagger, optional
        Define how the Function is staggered.
    padding : int or tuple of ints, optional
        Allocate extra grid points to maximize data access alignment. When a tuple
        of ints, one int per Dimension should be provided.
    initializer : callable or any object exposing the buffer interface, optional
        Data initializer. If a callable is provided, data is allocated lazily.
    allocator : MemoryAllocator, optional
        Controller for memory allocation. To be used, for example, when one wants
        to take advantage of the memory hierarchy in a NUMA architecture. Refer to
        `default_allocator.__doc__` for more information.

    Examples
    --------
    Creation

    >>> from devito import Grid, Function
    >>> grid = Grid(shape=(4, 4))
    >>> f = Function(name='f', grid=grid)
    >>> f
    f(x, y)
    >>> g = Function(name='g', grid=grid, space_order=2)
    >>> g
    g(x, y)

    First-order derivatives through centered finite-difference approximations

    >>> f.dx
    Derivative(f(x, y), x)
    >>> f.dy
    Derivative(f(x, y), y)
    >>> g.dx
    Derivative(g(x, y), x)
    >>> (f + g).dx
    Derivative(f(x, y) + g(x, y), x)

    First-order derivatives through left/right finite-difference approximations

    >>> f.dxl
    Derivative(f(x, y), x)
    >>> g.dxl
    Derivative(g(x, y), x)
    >>> f.dxr
    Derivative(f(x, y), x)

    Second-order derivative through centered finite-difference approximation

    >>> g.dx2
    Derivative(g(x, y), (x, 2))

    Notes
    -----
    The parameters must always be given as keyword arguments, since SymPy
    uses ``*args`` to (re-)create the dimension arguments of the symbolic object.
    """
    is_TimeFunction = True
    is_SparseTimeFunction = True
    sub_type = TimeFunction
