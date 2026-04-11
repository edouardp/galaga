"""Decorators for making algebra functions symbolic-aware.

The GA library has two modes: numeric (concrete NumPy arrays) and symbolic
(expression trees). Every module-level function (gp, reverse,
dual, etc.) needs to handle both. Without these decorators, each function
would have 4 lines of boilerplate:

    if x._is_symbolic:
        from galaga.expr import NodeClass
        result = func(Multivector(x.algebra, x.data))  # numeric computation
        return x._symbolic_result(result.data, NodeClass(x._to_expr()))

The decorators eliminate this repetition. They:
1. Check if any argument is symbolic
2. If so, compute the numeric result (for .data) using a plain MV copy
3. Build the symbolic Expr node (for display/simplification)
4. Return a symbolic MV carrying both

Why compute numerically even for symbolic?
  Symbolic MVs carry both concrete data AND an expression tree. This means
  .eval() is instant (data already computed), and .data is always valid.
  The tree is only for display and simplification.
"""

from __future__ import annotations

import functools


def _make_numeric(mv):
    """Create a plain numeric MV from a possibly-symbolic one.

    This strips all symbolic metadata (_is_symbolic, _expr, _name) so the
    decorated function's numeric path runs without triggering symbolic logic.
    """
    from galaga.algebra import Multivector

    return Multivector(mv.algebra, mv.data)


def symbolic_unary(sym_node_name: str):
    """Decorator for unary functions: f(x) → SymNode(x) when x is symbolic.

    Args:
        sym_node_name: Name of the Expr subclass in ga.symbolic (e.g. 'Reverse').
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(x):
            if x._is_symbolic:
                import galaga.expr as _expr_mod

                NodeClass = getattr(_expr_mod, sym_node_name)
                result = func(_make_numeric(x))
                return x._symbolic_result(result.data, NodeClass(x._to_expr()))
            return func(x)

        return wrapper

    return decorator


def symbolic_binary(sym_node_name: str):
    """Decorator for binary functions: f(a, b) → SymNode(a, b) when either is symbolic.

    Args:
        sym_node_name: Name of the Expr subclass in ga.symbolic (e.g. 'Gp').
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(a, b):
            if a._is_symbolic or b._is_symbolic:
                import galaga.expr as _expr_mod

                NodeClass = getattr(_expr_mod, sym_node_name)
                result = func(_make_numeric(a), _make_numeric(b))
                return a._symbolic_result(result.data, NodeClass(a._to_expr(), b._to_expr()))
            return func(a, b)

        return wrapper

    return decorator


# Backward-compat aliases
lazy_unary = symbolic_unary
lazy_binary = symbolic_binary
