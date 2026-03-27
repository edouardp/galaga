"""Decorator for making algebra functions lazy-aware.

When a decorated function receives a lazy Multivector, it:
1. Computes the concrete result using the eager path
2. Wraps it in a lazy MV with the corresponding symbolic Expr node
"""

from __future__ import annotations

import functools


def _make_eager(mv):
    """Create a plain eager MV from a possibly-lazy one."""
    from ga.algebra import Multivector
    return Multivector(mv.algebra, mv.data)


def lazy_unary(sym_node_name: str):
    """Decorator for unary functions: f(x) → SymNode(x) when x is lazy."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(x):
            if x._is_lazy:
                import ga.symbolic as sym
                NodeClass = getattr(sym, sym_node_name)
                result = func(_make_eager(x))
                return x._lazy_result(result.data, NodeClass(x._to_expr()))
            return func(x)
        return wrapper
    return decorator


def lazy_binary(sym_node_name: str):
    """Decorator for binary functions: f(a, b) → SymNode(a, b) when either is lazy."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(a, b):
            if a._is_lazy or b._is_lazy:
                import ga.symbolic as sym
                NodeClass = getattr(sym, sym_node_name)
                result = func(_make_eager(a), _make_eager(b))
                return a._lazy_result(result.data, NodeClass(a._to_expr(), b._to_expr()))
            return func(a, b)
        return wrapper
    return decorator
