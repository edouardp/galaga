"""Precedence-aware tree-walking renderer for symbolic expressions.

This is the single source of truth for how Expr trees become strings.
Both Multivector.__str__() and .latex() delegate here for lazy MVs.

Architecture:
  - OpInfo registry: each Expr node type has a precedence level, associativity,
    and flattenability flag. This drives parenthesization decisions.
  - Notation object: holds rendering rules (symbol, kind) for each node type
    in each format (ascii/unicode/latex). Configurable per-algebra.
  - render() / render_latex(): recursive visitors that walk the tree,
    look up rules from Notation, and wrap children in parens based on OpInfo.

Why a standalone module?
  The original design had each Expr node implement its own __str__() and
  _latex__(). This led to 16 parenthesization bugs because each node
  independently decided whether children needed wrapping. Centralizing
  the logic here with a precedence table fixed all of them.

Why not just use precedence numbers?
  Some operations need special handling beyond simple precedence:
  - Gp (geometric product): juxtaposition with smart spacing for multi-char names
  - Div: unicode uses / with tight denom wrapping, LaTeX uses \\frac{}{}
  - Unit: hat accent for single-char atoms, fraction for compounds
  - Grade: subscript suffix after closing delimiter
  These are handled as explicit cases before the generic rule dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from galaga.expr import (
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
)
from galaga.notation import Notation

_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
# Characters that don't count toward "visual width" — used to decide
# whether a rendered name is single-char (for Gp spacing and accent decisions).
# Subscripts, superscripts, and combining marks are ignored.

_SUB_SUPER = set("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₔₕₖₗₘₙₚₛₜ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")

# --- Precedence ---


class Assoc(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class OpInfo:
    prec: int
    assoc: Assoc = Assoc.NONE
    flat: bool = False


# --- Precedence registry ---
# Higher prec = binds tighter. A child is wrapped if its prec < parent's threshold.
# flat=True means the op is associative: same-type children skip wrapping
# (e.g. Gp(Gp(a,b),c) → "abc", Op(Op(a,b),c) → "a∧b∧c")

INFO: dict[type, OpInfo] = {
    Sym: OpInfo(100),
    Scalar: OpInfo(100),
    Reverse: OpInfo(95),
    Involute: OpInfo(95),
    Conjugate: OpInfo(95),
    Dual: OpInfo(95),
    Undual: OpInfo(95),
    Complement: OpInfo(95),
    Uncomplement: OpInfo(95),
    Inverse: OpInfo(95),
    Squared: OpInfo(95),
    Neg: OpInfo(90),
    ScalarMul: OpInfo(80),
    ScalarDiv: OpInfo(80),
    Gp: OpInfo(80, Assoc.LEFT, flat=True),
    Op: OpInfo(70, Assoc.LEFT, flat=True),
    Lc: OpInfo(70, Assoc.LEFT),
    Rc: OpInfo(70, Assoc.LEFT),
    Hi: OpInfo(70, Assoc.LEFT),
    Dli: OpInfo(70, Assoc.LEFT),
    Sp: OpInfo(70, Assoc.LEFT),
    Div: OpInfo(70, Assoc.LEFT),
    Regressive: OpInfo(70, Assoc.LEFT, flat=True),
    Add: OpInfo(60, Assoc.LEFT, flat=True),
    Sub: OpInfo(60, Assoc.LEFT),
    Grade: OpInfo(100),
    Norm: OpInfo(100),
    Unit: OpInfo(100),
    Exp: OpInfo(100),
    Log: OpInfo(100),
    Even: OpInfo(100),
    Odd: OpInfo(100),
    Commutator: OpInfo(100),
    Anticommutator: OpInfo(100),
    LieBracket: OpInfo(100),
    JordanProduct: OpInfo(100),
}

# Child wrapping thresholds for binary ops
_CHILD_MIN = {Gp: 80, Op: 81, Lc: 71, Rc: 71, Hi: 71, Dli: 71, Sp: 71}

# Map node type to its string name for notation lookup
_NAME = {cls: cls.__name__ for cls in INFO}

# Binary ops with comma-separated children in wrap notation
_COMMA_BINARY = {Commutator, Anticommutator, LieBracket, JordanProduct}

# Default notation singleton
_DEFAULT = Notation()


# --- Helpers ---


def _base_len(s: str) -> int:
    import unicodedata

    return sum(1 for c in s if not unicodedata.category(c).startswith("M") and c not in _SUB_SUPER)


def _is_single(s: str) -> bool:
    return _base_len(s) == 1


def _needs_wrap(child: Expr, min_prec: int, parent_type: type = None) -> bool:
    pi = INFO.get(parent_type)
    if pi and pi.flat and type(child) is parent_type:
        return False
    return INFO.get(type(child), OpInfo(0)).prec < min_prec


def _w(s, child, min_prec, pt=None):
    return f"({s})" if _needs_wrap(child, min_prec, pt) else s


def _multichar(node):
    if isinstance(node, Sym):
        return not _is_single(node._name)
    if isinstance(node, (ScalarMul, Neg)):
        return _multichar(node.x)
    if isinstance(node, (Reverse, Involute, Conjugate, Dual, Undual, Inverse, Squared)):
        return _multichar(node.x)
    return False


# --- Unicode ---


def render(node: Expr, notation: Notation | None = None) -> str:
    n = notation or _DEFAULT
    t = type(node)
    name = _NAME.get(t, "")

    # Atoms
    if t is Sym:
        return node._name
    if t is Scalar:
        return f"{node._value:g}"

    # Prefix with coefficient
    if t is Neg:
        return f"-{_w(render(node.x, n), node.x, 61)}"
    if t is ScalarMul:
        i = render(node.x, n)
        return f"-{_w(i, node.x, 61)}" if node.k == -1 else f"{node.k:g}{_w(i, node.x, 61)}"
    if t is ScalarDiv:
        return f"{_w(render(node.x, n), node.x, 70)}/{node.k:g}"

    # Geometric product — juxtaposition with smart spacing
    if t is Gp:
        l = _w(render(node.a, n), node.a, 80, Gp)
        r = _w(render(node.b, n), node.b, 80, Gp)
        return f"{l} {r}" if _multichar(node.a) or _multichar(node.b) else f"{l}{r}"

    # Add/Sub — asymmetric wrapping
    if t is Add:
        rhs = render(node.b, n)
        if rhs.startswith("-"):
            return f"{_w(render(node.a, n), node.a, 60, Add)} - {rhs[1:]}"
        return f"{_w(render(node.a, n), node.a, 60, Add)} + {rhs}"
    if t is Sub:
        return f"{render(node.a, n)} - {_w(render(node.b, n), node.b, 61)}"

    # Div — tight denom wrapping in unicode
    if t is Div:
        return f"{_w(render(node.a, n), node.a, 71)}/{_w(render(node.b, n), node.b, 95)}"

    # Unit — hat for single-char atoms, fraction for compounds
    if t is Unit:
        if isinstance(node.x, Sym) and _is_single(str(node.x)):
            ur = n.get("Unit", "unicode")
            if ur and ur.combining:
                return f"{render(node.x, n)}{ur.combining}"
        return f"{_w(render(node.x, n), node.x, 70)}/‖{render(node.x, n)}‖"

    # Look up notation rule
    rule = n.get(name, "unicode")
    if not rule:
        return str(node)

    # Infix binary
    if rule.kind == "infix" and hasattr(node, "a"):
        mp = _CHILD_MIN.get(t, 71)
        return f"{_w(render(node.a, n), node.a, mp, t)}{rule.separator}{_w(render(node.b, n), node.b, mp, t)}"

    # Function-style
    if rule.kind == "function":
        if hasattr(node, "a"):
            return f"{rule.symbol}({render(node.a, n)}, {render(node.b, n)})"
        return f"{rule.symbol}({render(node.x, n)})"

    # Prefix unary (e.g. *v for dual)
    if rule.kind == "prefix" and hasattr(node, "x"):
        return f"{rule.symbol}{_w(render(node.x, n), node.x, 95)}"

    # Accent (combining char for atoms, prefix fallback for compounds)
    if rule.kind == "accent" and hasattr(node, "x"):
        inner = render(node.x, n)
        if isinstance(node.x, (Sym, Scalar)) and rule.combining:
            return f"{inner}{rule.combining}"
        if rule.fallback_prefix:
            return f"{rule.fallback_prefix}({inner})"
        return f"{inner}{rule.combining}"

    # Postfix
    if rule.kind == "postfix" and hasattr(node, "x"):
        # Use 96 (not 95) so postfix-on-postfix gets parens: (B⋆)⋆⁻¹
        return f"{_w(render(node.x, n), node.x, 96)}{rule.symbol}"

    # Wrap
    if rule.kind == "wrap":
        # Binary with comma (commutator family)
        if t in _COMMA_BINARY:
            return f"{rule.open}{render(node.a, n)}, {render(node.b, n)}{rule.close}"
        # Grade — append subscript
        if t is Grade:
            return f"{rule.open}{render(node.x, n)}{rule.close}{str(node.k).translate(_SUBSCRIPTS)}"
        # Unit — hat for single-char atoms, fraction for compounds
        if t is Unit:
            if isinstance(node.x, Sym) and _is_single(str(node.x)) and rule.combining:
                return f"{render(node.x, n)}{rule.combining}"
            return f"{_w(render(node.x, n), node.x, 70)}/‖{render(node.x, n)}‖"
        # Generic unary wrap
        return f"{rule.open}{render(node.x, n)}{rule.close}"

    return str(node)


# --- LaTeX ---
#
# LaTeX rendering uses a three-phase pipeline:
#   1. latex_build: Expr → LNode tree (structural mapping)
#   2. latex_rewrite: LNode → LNode (context-dependent transforms, e.g. frac→tfrac in superscripts)
#   3. latex_emit: LNode → str (serialization)
# See latex_nodes.py module docstring for the full rationale.


def render_latex(node: Expr, notation: Notation | None = None) -> str:
    from galaga.latex_build import build
    from galaga.latex_emit import emit
    from galaga.latex_rewrite import rewrite

    return emit(rewrite(build(node, notation)))
