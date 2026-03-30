"""Symbolic layer for galaga — expression nodes, simplification, and sym().

This module provides:
- Re-exports of all Expr node classes from galaga.expr
- simplify() for algebraic rewriting of expression trees
- sym() for creating named symbolic copies of multivectors
- _is_symbolic() helper for checking lazy state

The drop-in function replacements that were previously here have been removed.
All functions in the main galaga module (gp, grade, reverse, etc.) already
handle lazy Multivectors via @lazy_unary/@lazy_binary decorators.
"""

from __future__ import annotations

import galaga.algebra as _alg

# Re-export all Expr nodes so existing "from galaga.symbolic import Gp" still works
from galaga.expr import (  # noqa: F401
    Add,
    Anticommutator,
    Commutator,
    Complement,
    Conjugate,
    Div,
    Dli,
    Dual,
    Even,
    Exp,
    Expr,
    Gp,
    Grade,
    Hi,
    Inverse,
    Involute,
    JordanProduct,
    Lc,
    LieBracket,
    Log,
    Neg,
    Norm,
    Odd,
    Op,
    Rc,
    Regressive,
    Reverse,
    Scalar,
    ScalarDiv,
    ScalarMul,
    Sp,
    Sqrt,
    Squared,
    Sub,
    Sym,
    Uncomplement,
    Undual,
    Unit,
    _coerce,
    _ensure_expr,
)

# Re-export simplify
from galaga.simplify import _eq, _known_grade, simplify  # noqa: F401


def _is_symbolic(x) -> bool:
    """True if x is a lazy Multivector (has an expression tree)."""
    return isinstance(x, _alg.Multivector) and x._is_lazy


def sym(mv: _alg.Multivector, name: str | None = None, grade: int | None = None) -> _alg.Multivector:
    """Create a named symbolic copy of a multivector.

    Returns a new Multivector that is a copy of mv, with .name(name) applied.
    If no name is given, the copy is made lazy (symbolic but anonymous).
    Non-mutating: the original mv is not modified.
    """
    copy = _alg.Multivector(mv.algebra, mv.data)
    if name is not None:
        copy.name(name)
    else:
        copy.lazy()
    return copy
