"""Symbolic drop-in replacements for ga.algebra functions.

This module re-exports every function from galaga.algebra as a wrapper that
detects lazy Multivector arguments and builds Expr tree nodes. With plain
eager Multivectors, it delegates directly to ga.algebra with zero overhead.

Usage:
    from galaga.symbolic import gp, grade, reverse, sym, simplify

All Expr node classes are re-exported from galaga.expr for backward compatibility.
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

# ── Helpers ──


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


# ── Drop-in function factories ──
#
# Each drop-in checks if any argument is a lazy MV (via _is_symbolic).
# If so, it builds the corresponding Expr tree node.
# If not, it delegates directly to ga.algebra with zero overhead.
#
# The factories take a string name and resolve the function from _alg at
# call time, avoiding circular import issues.


def _make_binary_dropin(node_cls, func_name):
    def dropin(a, b):
        if _is_symbolic(a) or _is_symbolic(b) or isinstance(a, Expr) or isinstance(b, Expr):
            return node_cls(_ensure_expr(a), _ensure_expr(b))
        return getattr(_alg, func_name)(a, b)

    dropin.__name__ = func_name
    return dropin


def _make_unary_dropin(node_cls, func_name):
    def dropin(x):
        if _is_symbolic(x) or isinstance(x, Expr):
            return node_cls(_ensure_expr(x))
        return getattr(_alg, func_name)(x)

    dropin.__name__ = func_name
    return dropin


# Binary drop-ins
gp = _make_binary_dropin(Gp, "gp")
op = _make_binary_dropin(Op, "op")
left_contraction = _make_binary_dropin(Lc, "left_contraction")
right_contraction = _make_binary_dropin(Rc, "right_contraction")
hestenes_inner = _make_binary_dropin(Hi, "hestenes_inner")
doran_lasenby_inner = _make_binary_dropin(Dli, "doran_lasenby_inner")
dorst_inner = doran_lasenby_inner
scalar_product = _make_binary_dropin(Sp, "scalar_product")
commutator = _make_binary_dropin(Commutator, "commutator")
anticommutator = _make_binary_dropin(Anticommutator, "anticommutator")
lie_bracket = _make_binary_dropin(LieBracket, "lie_bracket")
jordan_product = _make_binary_dropin(JordanProduct, "jordan_product")
regressive_product = _make_binary_dropin(Regressive, "regressive_product")
meet = regressive_product

# Unary drop-ins
reverse = _make_unary_dropin(Reverse, "reverse")
involute = _make_unary_dropin(Involute, "involute")
conjugate = _make_unary_dropin(Conjugate, "conjugate")
dual = _make_unary_dropin(Dual, "dual")
undual = _make_unary_dropin(Undual, "undual")
complement = _make_unary_dropin(Complement, "complement")
uncomplement = _make_unary_dropin(Uncomplement, "uncomplement")
norm = _make_unary_dropin(Norm, "norm")
unit = _make_unary_dropin(Unit, "unit")
inverse = _make_unary_dropin(Inverse, "inverse")
squared = _make_unary_dropin(Squared, "squared")
even_grades = _make_unary_dropin(Even, "even_grades")
odd_grades = _make_unary_dropin(Odd, "odd_grades")

normalize = unit
normalise = unit


def grade(x, k):
    if _is_symbolic(x) or isinstance(x, Expr):
        e = _ensure_expr(x)
        if k == "even":
            return Even(e)
        if k == "odd":
            return Odd(e)
        return Grade(e, k)
    return _alg.grade(x, k)


def ip(a, b, mode: str = "doran_lasenby"):
    if _is_symbolic(a) or _is_symbolic(b) or isinstance(a, Expr) or isinstance(b, Expr):
        ea, eb = _ensure_expr(a), _ensure_expr(b)
        if mode == "left":
            return Lc(ea, eb)
        if mode == "right":
            return Rc(ea, eb)
        if mode == "hestenes":
            return Hi(ea, eb)
        if mode == "doran_lasenby":
            return Dli(ea, eb)
        if mode == "scalar":
            return Sp(ea, eb)
        raise ValueError(f"Unknown inner product mode: {mode!r}")
    return _alg.ip(a, b, mode)


def sandwich(r, x):
    if _is_symbolic(r) or _is_symbolic(x) or isinstance(r, Expr) or isinstance(x, Expr):
        er, ex = _ensure_expr(r), _ensure_expr(x)
        return Gp(Gp(er, ex), Reverse(er))
    return _alg.sandwich(r, x)


sw = sandwich
