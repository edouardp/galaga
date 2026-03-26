"""Precedence-aware tree-walking renderer for symbolic expressions.

A standalone visitor that walks an Expr tree and produces correctly
parenthesized unicode or LaTeX output. Operation metadata (precedence,
associativity, flattenability) is stored in a registry, not hardcoded
per-node.

Precedence levels (higher = binds tighter):
    100  Atoms: Sym, Scalar
     95  Postfix unary: Reverse, Involute, Conjugate, Dual, Undual,
         Inverse, Squared
     90  Prefix unary: Neg
     80  Geometric product, ScalarMul, ScalarDiv
     70  Wedge, contractions, inner products, Div
     60  Add, Sub

Bracket-style ops (Grade, Norm, Unit, Exp, Commutator family) have
explicit delimiters so they never need precedence-based parens.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from ga.symbolic import (
    Expr, Sym, Scalar,
    Gp, Op, Add, Sub, Neg, ScalarMul, ScalarDiv, Div,
    Reverse, Involute, Conjugate, Dual, Undual,
    Inverse, Squared, Exp,
    Grade, Norm, Unit, Even, Odd,
    Lc, Rc, Hi, Dli, Sp,
    Commutator, Anticommutator, LieBracket, JordanProduct,
)

_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_REVERSE = "\u0303"
_INVOLUTE = "\u0302"
_CONJUGATE = "\u0304"
_HAT = "\u0302"

# Subscript/superscript codepoint ranges
_SUB_SUPER = set("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₔₕₖₗₘₙₚₛₜ"
                 "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")


def _base_len(s: str) -> int:
    """Count 'base' characters, ignoring combining marks and sub/superscripts."""
    import unicodedata
    n = 0
    for c in s:
        cat = unicodedata.category(c)
        if cat.startswith("M"):  # combining marks (Mn, Mc, Me)
            continue
        if c in _SUB_SUPER:
            continue
        n += 1
    return n


def _is_single_char_name(s: str) -> bool:
    """True if s is visually a single character (ignoring diacriticals/subscripts)."""
    return _base_len(s) == 1


# ============================================================
# Operation metadata
# ============================================================

class Assoc(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class OpInfo:
    """Metadata for an expression node type."""
    prec: int
    assoc: Assoc = Assoc.NONE
    flat: bool = False  # True if associative and can be flattened (a∧b∧c)


# Registry: node type → metadata
INFO: dict[type, OpInfo] = {
    # Atoms
    Sym:     OpInfo(100),
    Scalar:  OpInfo(100),

    # Postfix unary
    Reverse:   OpInfo(95),
    Involute:  OpInfo(95),
    Conjugate: OpInfo(95),
    Dual:      OpInfo(95),
    Undual:    OpInfo(95),
    Inverse:   OpInfo(95),
    Squared:   OpInfo(95),

    # Prefix unary
    Neg:       OpInfo(90),
    ScalarMul: OpInfo(80),
    ScalarDiv: OpInfo(80),

    # Binary multiplicative
    Gp:  OpInfo(80, Assoc.LEFT, flat=True),
    Op:  OpInfo(70, Assoc.LEFT, flat=True),
    Lc:  OpInfo(70, Assoc.LEFT),
    Rc:  OpInfo(70, Assoc.LEFT),
    Hi:  OpInfo(70, Assoc.LEFT),
    Dli: OpInfo(70, Assoc.LEFT),
    Sp:  OpInfo(70, Assoc.LEFT),
    Div: OpInfo(70, Assoc.LEFT),

    # Additive
    Add: OpInfo(60, Assoc.LEFT, flat=True),
    Sub: OpInfo(60, Assoc.LEFT),

    # Bracket-style (explicit delimiters — never need outer parens)
    Grade:           OpInfo(100),
    Norm:            OpInfo(100),
    Unit:            OpInfo(100),
    Exp:             OpInfo(100),
    Even:            OpInfo(100),
    Odd:             OpInfo(100),
    Commutator:      OpInfo(100),
    Anticommutator:  OpInfo(100),
    LieBracket:      OpInfo(100),
    JordanProduct:   OpInfo(100),
}


def _info(node: Expr) -> OpInfo:
    return INFO.get(type(node), OpInfo(0))


# ============================================================
# Wrapping logic
# ============================================================

def _needs_wrap(child: Expr, min_prec: int, parent_type: type = None) -> bool:
    """Does child need parens in a context requiring min_prec?

    If parent is flattenable and child is the same type, no wrap needed.
    """
    ci = _info(child)
    if parent_type is not None:
        pi = INFO.get(parent_type)
        if pi and pi.flat and type(child) is parent_type:
            return False
    return ci.prec < min_prec


def _wrap(s: str, child: Expr, min_prec: int, parent_type: type = None) -> str:
    if _needs_wrap(child, min_prec, parent_type):
        return f"({s})"
    return s


def _wrap_latex(s: str, child: Expr, min_prec: int, parent_type: type = None) -> str:
    if _needs_wrap(child, min_prec, parent_type):
        return rf"\left({s}\right)"
    return s


# ============================================================
# Binary op symbols
# ============================================================

_BINARY_UNICODE = {
    Op: "∧", Lc: "⌋", Rc: "⌊", Hi: "·", Dli: "·", Sp: "∗",
}

_BINARY_LATEX = {
    Op: r" \wedge ", Lc: r" \;\lrcorner\; ", Rc: r" \;\llcorner\; ",
    Hi: r" \cdot ", Dli: r" \cdot ", Sp: r" * ",
}

# Threshold for wrapping children of binary ops.
# Children must have prec >= this to avoid wrapping.
# For Gp (prec 80): children at 80+ are fine (Gp, ScalarMul).
# For Op (prec 70): children must be > 80 to avoid ambiguity with ScalarMul.
_BINARY_CHILD_MIN = {
    Gp: 80,
    Op: 81,  # ScalarMul (80) inside Op needs wrapping
    Lc: 71, Rc: 71, Hi: 71, Dli: 71, Sp: 71,
}


# ============================================================
# Postfix unary decorations
# ============================================================

_POSTFIX_UNICODE = {
    Reverse: _REVERSE, Involute: _INVOLUTE, Conjugate: _CONJUGATE,
    Dual: "⋆", Undual: "⋆⁻¹", Inverse: "⁻¹", Squared: "²",
}

# Combining diacriticals only work on single letters.
# For compound expressions, use these prefix/wrap fallbacks instead.
_COMPOUND_FALLBACK = {
    Reverse:   ("~", None),      # ~(expr)
    Involute:  ("inv(", ")"),     # inv(expr)
    Conjugate: ("conj(", ")"),    # conj(expr)
}

_POSTFIX_LATEX_FMT = {
    Involute:  r"{inner}^\dagger",
    Dual:      r"{inner}^*",
    Undual:    r"{inner}^{{*^{{-1}}}}",
    Inverse:   r"{inner}^{{-1}}",
    Squared:   r"{inner}^2",
}


def _latex_postfix(t: type, inner: str, node: Expr) -> str:
    """Render postfix unary in LaTeX, using wide accents for compound expressions."""
    is_atom = isinstance(node.x, (Sym, Scalar))
    if t is Reverse:
        return rf"\widetilde{{{inner}}}" if not is_atom else rf"\tilde{{{inner}}}"
    if t is Conjugate:
        return rf"\overline{{{inner}}}" if not is_atom else rf"\bar{{{inner}}}"
    fmt = _POSTFIX_LATEX_FMT[t]
    return fmt.format(inner=inner)


def _has_multichar_name(node: Expr) -> bool:
    """True if node is (or contains at the edge) a multi-char Sym name."""
    if isinstance(node, Sym):
        return not _is_single_char_name(node._name)
    if isinstance(node, ScalarMul):
        return _has_multichar_name(node.x)
    if isinstance(node, Neg):
        return _has_multichar_name(node.x)
    # Postfix unary — the decorated name might be multi-char visually
    if isinstance(node, (Reverse, Involute, Conjugate, Dual, Undual, Inverse, Squared)):
        return _has_multichar_name(node.x)
    return False


# ============================================================
# Unicode renderer
# ============================================================

def render(node: Expr) -> str:
    t = type(node)

    # Atoms
    if t is Sym:
        return node._name
    if t is Scalar:
        return f"{node._value:g}"

    # Prefix unary
    if t is Neg:
        inner = render(node.x)
        return f"-{_wrap(inner, node.x, 61)}"
    if t is ScalarMul:
        if node.k == -1:
            return f"-{_wrap(render(node.x), node.x, 61)}"
        return f"{node.k:g}{_wrap(render(node.x), node.x, 61)}"
    if t is ScalarDiv:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 70)}/{node.k:g}"

    # Binary with infix symbol (wedge, contractions, inner products)
    if t in _BINARY_UNICODE:
        sym = _BINARY_UNICODE[t]
        min_p = _BINARY_CHILD_MIN.get(t, 71)
        left = _wrap(render(node.a), node.a, min_p, parent_type=t)
        right = _wrap(render(node.b), node.b, min_p, parent_type=t)
        return f"{left}{sym}{right}"

    # Geometric product (juxtaposition — no symbol)
    if t is Gp:
        left = _wrap(render(node.a), node.a, 80, parent_type=Gp)
        right = _wrap(render(node.b), node.b, 80, parent_type=Gp)
        # Space if either immediate child has a multi-char name
        if _has_multichar_name(node.a) or _has_multichar_name(node.b):
            return f"{left} {right}"
        return f"{left}{right}"

    # Div (unicode uses /)
    if t is Div:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 95)  # denom needs tight wrapping
        return f"{left}/{right}"

    # Addition / subtraction
    if t is Add:
        left = _wrap(render(node.a), node.a, 60, parent_type=Add)
        right = render(node.b)
        return f"{left} + {right}"
    if t is Sub:
        left = render(node.a)
        right = _wrap(render(node.b), node.b, 61)
        return f"{left} - {right}"

    # Postfix unary
    if t in _POSTFIX_UNICODE:
        suffix = _POSTFIX_UNICODE[t]
        inner = render(node.x)
        is_atom = isinstance(node.x, (Sym, Scalar))
        if is_atom:
            # Combining diacritical on single letter
            return f"{inner}{suffix}"
        elif t in _COMPOUND_FALLBACK:
            # Combining chars don't work on compound expressions
            prefix, close = _COMPOUND_FALLBACK[t]
            wrapped = _wrap(inner, node.x, 95)
            if close is not None:
                return f"{prefix}{inner}{close}"
            else:
                return f"{prefix}{wrapped}"
        else:
            # Suffix chars (⋆, ⁻¹, ²) work fine on parens
            return f"{_wrap(inner, node.x, 95)}{suffix}"

    # Bracket-style (explicit delimiters)
    if t is Grade:
        sub = str(node.k).translate(_SUBSCRIPTS)
        return f"⟨{render(node.x)}⟩{sub}"
    if t is Norm:
        return f"‖{render(node.x)}‖"
    if t is Unit:
        if isinstance(node.x, Sym) and len(str(node.x)) == 1:
            return f"{render(node.x)}{_HAT}"
        return f"{_wrap(render(node.x), node.x, 70)}/‖{render(node.x)}‖"
    if t is Exp:
        return f"exp({render(node.x)})"
    if t is Even:
        return f"⟨{render(node.x)}⟩₊"
    if t is Odd:
        return f"⟨{render(node.x)}⟩₋"

    # Commutator family
    if t is Commutator:
        return f"[{render(node.a)}, {render(node.b)}]"
    if t is Anticommutator:
        return f"{{{render(node.a)}, {render(node.b)}}}"
    if t is LieBracket:
        return f"½[{render(node.a)}, {render(node.b)}]"
    if t is JordanProduct:
        return f"½{{{render(node.a)}, {render(node.b)}}}"

    return str(node)


# ============================================================
# LaTeX renderer
# ============================================================

def render_latex(node: Expr) -> str:
    t = type(node)

    if t is Sym:
        return node._name_latex
    if t is Scalar:
        return f"{node._value:g}"

    if t is Neg:
        inner = render_latex(node.x)
        return f"-{_wrap_latex(inner, node.x, 61)}"
    if t is ScalarMul:
        if node.k == -1:
            return f"-{_wrap_latex(render_latex(node.x), node.x, 61)}"
        return f"{node.k:g} {_wrap_latex(render_latex(node.x), node.x, 61)}"
    if t is ScalarDiv:
        return rf"\frac{{{render_latex(node.x)}}}{{{node.k:g}}}"

    if t in _BINARY_LATEX:
        sep = _BINARY_LATEX[t]
        min_p = _BINARY_CHILD_MIN.get(t, 71)
        left = _wrap_latex(render_latex(node.a), node.a, min_p, parent_type=t)
        right = _wrap_latex(render_latex(node.b), node.b, min_p, parent_type=t)
        return f"{left}{sep}{right}"

    if t is Gp:
        left = _wrap_latex(render_latex(node.a), node.a, 80, parent_type=Gp)
        right = _wrap_latex(render_latex(node.b), node.b, 80, parent_type=Gp)
        return f"{left} {right}"

    if t is Div:
        return rf"\frac{{{render_latex(node.a)}}}{{{render_latex(node.b)}}}"

    if t is Add:
        left = _wrap_latex(render_latex(node.a), node.a, 60, parent_type=Add)
        return f"{left} + {render_latex(node.b)}"
    if t is Sub:
        left = render_latex(node.a)
        right = _wrap_latex(render_latex(node.b), node.b, 61)
        return f"{left} - {right}"

    if t is Reverse or t is Conjugate:
        # Wide accents act as visual grouping — no parens needed
        raw = render_latex(node.x)
        return _latex_postfix(t, raw, node)
    if t in _POSTFIX_LATEX_FMT:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return _latex_postfix(t, inner, node)

    if t is Grade:
        return rf"\langle {render_latex(node.x)} \rangle_{{{node.k}}}"
    if t is Norm:
        return rf"\lVert {render_latex(node.x)} \rVert"
    if t is Unit:
        if isinstance(node.x, (Sym, Scalar)):
            return rf"\hat{{{render_latex(node.x)}}}"
        num = _wrap_latex(render_latex(node.x), node.x, 70)
        return rf"\frac{{{num}}}{{{render_latex(Norm(node.x))}}}"
    if t is Exp:
        return rf"e^{{{render_latex(node.x)}}}"
    if t is Even:
        return rf"\langle {render_latex(node.x)} \rangle_{{\text{{even}}}}"
    if t is Odd:
        return rf"\langle {render_latex(node.x)} \rangle_{{\text{{odd}}}}"

    if t is Commutator:
        return rf"[{render_latex(node.a)},\, {render_latex(node.b)}]"
    if t is Anticommutator:
        return rf"\{{{render_latex(node.a)},\, {render_latex(node.b)}\}}"
    if t is LieBracket:
        return rf"\tfrac{{1}}{{2}}[{render_latex(node.a)},\, {render_latex(node.b)}]"
    if t is JordanProduct:
        return rf"\tfrac{{1}}{{2}}\{{{render_latex(node.a)},\, {render_latex(node.b)}\}}"

    return str(node)
