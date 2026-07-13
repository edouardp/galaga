"""Operation registry for geometric algebra.

Every GA operation is registered here with algebraic metadata.
The symbolic layer (expr.py) is a consumer — it registers handlers
against operation names defined here. This breaks the circular
dependency between algebra.py and expr.py.

Dependency rule: this module never imports expr.py or render.py.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class OpInfo:
    """Metadata for a registered GA operation."""

    name: str
    func: Callable  # the raw numeric implementation
    arity: int  # Number of positional arguments, including scalar parameters
    grade_rule: Callable | None = None


# ── Registries ──

GA_OPS: dict[str, OpInfo] = {}
_SYMBOLIC_HANDLERS: dict[str, Any] = {}  # populated by expr.py at import time
_SYM_FACTORY: Callable | None = None  # builds Sym nodes; set by expr.py
_SYM_CLASS: type | None = None  # the Sym class itself; set by expr.py


def register_symbolic_handler(op_name: str, handler: Any) -> None:
    """Register a symbolic handler for a named operation.

    Called by the symbolic layer (expr.py) at import time.
    The handler is a callable or node class that builds an expression tree node.
    """
    _SYMBOLIC_HANDLERS[op_name] = handler


def register_sym_factory(factory: Callable, sym_class: type) -> None:
    """Register the Sym node factory and class.

    Called by expr.py at import time so that algebra.py can build Sym nodes
    without importing expr.py.
    """
    global _SYM_FACTORY, _SYM_CLASS
    _SYM_FACTORY = factory
    _SYM_CLASS = sym_class


def build_expr(name: str, *args):
    """Build an expression node by name via the registered handler."""
    handler = _SYMBOLIC_HANDLERS[name]
    return handler(*args)


def make_sym(*args, **kwargs):
    """Build a Sym node via the registered factory."""
    return _SYM_FACTORY(*args, **kwargs)


def is_sym(obj) -> bool:
    """Check if obj is a Sym node without importing expr.py."""
    return _SYM_CLASS is not None and isinstance(obj, _SYM_CLASS)


# ── Decorator ──


def ga_op(name: str, arity: int, grade: Callable | None = None):
    """Register a GA operation with algebraic metadata.

    The decorated function must be a pure numeric implementation —
    no symbolic awareness. The wrapper handles:
    1. Symbolic dispatch (if a handler is registered by expr.py)
    2. Grade tracking (if a grade rule is provided)

    Args:
        name: Registry key (should match the function name).
        arity: Number of positional arguments. Most operations are unary or
               binary; parameterized products such as ``transwedge(a, b, k)``
               have arity 3.
        grade: Grade propagation rule (optional). The wrapper passes the known
               grades of all multivector arguments, followed by any non-MV
               parameters, followed by the algebra dimension ``n``.
    """

    def decorator(func):
        # Register
        GA_OPS[name] = OpInfo(name=name, func=func, arity=arity, grade_rule=grade)

        @functools.wraps(func)
        def wrapper(*args):
            from .algebra import Multivector

            # Check if any arg is symbolic
            is_sym = any(isinstance(a, Multivector) and a._is_symbolic for a in args)

            if is_sym:
                # Compute numeric result from stripped copies
                numeric_args = []
                for a in args:
                    if isinstance(a, Multivector):
                        numeric_args.append(Multivector(a.algebra, a.data))
                    else:
                        numeric_args.append(a)
                result = func(*numeric_args)

                # Build symbolic tree if handler registered
                handler = _SYMBOLIC_HANDLERS.get(name)
                if handler:
                    first_mv = next(a for a in args if isinstance(a, Multivector))
                    expr_args = [a._to_expr() if isinstance(a, Multivector) else a for a in args]
                    result = first_mv._symbolic_result(result.data, handler(*expr_args))
            else:
                result = func(*args)

            # Apply grade propagation
            if grade and isinstance(result, Multivector) and result._grade is None:
                mv_args = [a for a in args if isinstance(a, Multivector)]
                grades = [a._grade for a in mv_args]
                if all(g is not None for g in grades):
                    n = mv_args[0].algebra.n
                    params = [a for a in args if not isinstance(a, Multivector)]
                    result._grade = grade(*grades, *params, n)

            return result

        return wrapper

    return decorator
