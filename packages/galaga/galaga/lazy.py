"""Decorators for making algebra functions lazy-aware.

The GA library has two modes: eager (concrete NumPy arrays) and lazy
(symbolic expression trees). Every module-level function (gp, reverse,
dual, etc.) needs to handle both. Without these decorators, each function
would have 4 lines of boilerplate:

    if x._is_lazy:
        from galaga.symbolic import NodeClass
        result = func(Multivector(x.algebra, x.data))  # eager computation
        return x._lazy_result(result.data, NodeClass(x._to_expr()))

The decorators eliminate this repetition. They:
1. Check if any argument is lazy
2. If so, compute the eager result (for .data) using a plain MV copy
3. Build the symbolic Expr node (for display/simplification)
4. Return a lazy MV carrying both

Why compute eagerly even for lazy?
  Lazy MVs carry both concrete data AND an expression tree. This means
  .eval() is instant (data already computed), and .data is always valid.
  The tree is only for display and simplification.
"""

from __future__ import annotations

import functools


def _make_eager(mv):
    """Create a plain eager MV from a possibly-lazy one.

    This strips all symbolic metadata (_is_lazy, _expr, _name) so the
    decorated function's eager path runs without triggering lazy logic.
    """
    from galaga.algebra import Multivector
    return Multivector(mv.algebra, mv.data)


def lazy_unary(sym_node_name: str):
    """Decorator for unary functions: f(x) → SymNode(x) when x is lazy.

    Args:
        sym_node_name: Name of the Expr subclass in ga.symbolic (e.g. 'Reverse').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(x):
            if x._is_lazy:
                import galaga.symbolic as sym
                NodeClass = getattr(sym, sym_node_name)
                result = func(_make_eager(x))
                return x._lazy_result(result.data, NodeClass(x._to_expr()))
            return func(x)
        return wrapper
    return decorator


def lazy_binary(sym_node_name: str):
    """Decorator for binary functions: f(a, b) → SymNode(a, b) when either is lazy.

    Args:
        sym_node_name: Name of the Expr subclass in ga.symbolic (e.g. 'Gp').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(a, b):
            if a._is_lazy or b._is_lazy:
                import galaga.symbolic as sym
                NodeClass = getattr(sym, sym_node_name)
                result = func(_make_eager(a), _make_eager(b))
                return a._lazy_result(result.data, NodeClass(a._to_expr(), b._to_expr()))
            return func(a, b)
        return wrapper
    return decorator
