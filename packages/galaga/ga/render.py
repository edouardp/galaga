"""Precedence-aware tree-walking renderer for symbolic expressions.

A standalone visitor that walks an Expr tree and produces correctly
parenthesized unicode or LaTeX output. Each node type has a precedence
level; a child is wrapped in parens when its precedence is lower than
the parent's context requires.

Precedence levels (higher = binds tighter):
    100  Atoms: Sym, Scalar
     95  Postfix unary: Reverse, Involute, Conjugate, Dual, Undual,
         Inverse, Squared (these decorate a single operand)
     90  Prefix unary: Neg, ScalarMul, ScalarDiv
     80  Geometric product (juxtaposition)
     70  Wedge, contractions, inner products, Div
     60  Add, Sub

Bracket-style ops (Grade, Norm, Unit, Exp, Commutator family) have
explicit delimiters so they never need precedence-based parens.
"""

from __future__ import annotations

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

# --- Precedence table ---

_PREC = {
    Sym: 100, Scalar: 100,
    Reverse: 95, Involute: 95, Conjugate: 95,
    Dual: 95, Undual: 95, Inverse: 95, Squared: 95,
    Neg: 90, ScalarMul: 80, ScalarDiv: 80,
    Gp: 80,
    Op: 70, Lc: 70, Rc: 70, Hi: 70, Dli: 70, Sp: 70, Div: 70,
    Add: 60, Sub: 60,
    # Bracket-style — never need outer parens
    Grade: 100, Norm: 100, Unit: 100, Exp: 100, Even: 100, Odd: 100,
    Commutator: 100, Anticommutator: 100,
    LieBracket: 100, JordanProduct: 100,
}


def _prec(node: Expr) -> int:
    return _PREC.get(type(node), 0)


def _wrap(s: str, child: Expr, min_prec: int) -> str:
    """Wrap s in parens if child's precedence is below min_prec."""
    if _prec(child) < min_prec:
        return f"({s})"
    return s


def _wrap_latex(s: str, child: Expr, min_prec: int) -> str:
    if _prec(child) < min_prec:
        return rf"\left({s}\right)"
    return s


# --- Unicode renderer ---

def render(node: Expr) -> str:
    """Render an Expr tree as a unicode string with correct parenthesization."""
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
            inner = render(node.x)
            return f"-{_wrap(inner, node.x, 61)}"
        inner = render(node.x)
        return f"{node.k:g}{_wrap(inner, node.x, 61)}"
    if t is ScalarDiv:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 70)}/{node.k:g}"

    # Geometric product (juxtaposition)
    if t is Gp:
        left = _wrap(render(node.a), node.a, 80)
        right = _wrap(render(node.b), node.b, 80)
        return f"{left}{right}"

    # Wedge and other multiplicative binary ops
    if t is Op:
        left = render(node.a)
        if not isinstance(node.a, Op):
            left = _wrap(left, node.a, 81)
        right = render(node.b)
        if not isinstance(node.b, Op):
            right = _wrap(right, node.b, 81)
        return f"{left}∧{right}"
    if t is Lc:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 71)
        return f"{left}⌋{right}"
    if t is Rc:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 71)
        return f"{left}⌊{right}"
    if t is Hi:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 71)
        return f"{left}·{right}"
    if t is Dli:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 71)
        return f"{left}·{right}"
    if t is Sp:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 71)
        return f"{left}∗{right}"
    if t is Div:
        left = _wrap(render(node.a), node.a, 71)
        right = _wrap(render(node.b), node.b, 95)
        return f"{left}/{right}"

    # Addition / subtraction
    if t is Add:
        left = render(node.a)
        right = render(node.b)
        return f"{left} + {right}"
    if t is Sub:
        left = render(node.a)
        right = _wrap(render(node.b), node.b, 61)
        return f"{left} - {right}"

    # Postfix unary — need parens on anything non-atomic
    if t is Reverse:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}{_REVERSE}"
    if t is Involute:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}{_INVOLUTE}"
    if t is Conjugate:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}{_CONJUGATE}"
    if t is Dual:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}⋆"
    if t is Undual:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}⋆⁻¹"
    if t is Inverse:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}⁻¹"
    if t is Squared:
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 95)}²"

    # Bracket-style (explicit delimiters — no precedence issue)
    if t is Grade:
        sub = str(node.k).translate(_SUBSCRIPTS)
        return f"⟨{render(node.x)}⟩{sub}"
    if t is Norm:
        return f"‖{render(node.x)}‖"
    if t is Unit:
        if isinstance(node.x, (Sym, Scalar)):
            return f"{render(node.x)}{_HAT}"
        inner = render(node.x)
        return f"{_wrap(inner, node.x, 70)}/‖{render(node.x)}‖"
    if t is Exp:
        return f"exp({render(node.x)})"
    if t is Even:
        return f"⟨{render(node.x)}⟩₊"
    if t is Odd:
        return f"⟨{render(node.x)}⟩₋"

    # Commutator family (bracket-delimited)
    if t is Commutator:
        return f"[{render(node.a)}, {render(node.b)}]"
    if t is Anticommutator:
        return f"{{{render(node.a)}, {render(node.b)}}}"
    if t is LieBracket:
        return f"½[{render(node.a)}, {render(node.b)}]"
    if t is JordanProduct:
        return f"½{{{render(node.a)}, {render(node.b)}}}"

    return str(node)


# --- LaTeX renderer ---

def render_latex(node: Expr) -> str:
    """Render an Expr tree as LaTeX with correct parenthesization."""
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
            inner = render_latex(node.x)
            return f"-{_wrap_latex(inner, node.x, 61)}"
        inner = render_latex(node.x)
        return f"{node.k:g} {_wrap_latex(inner, node.x, 61)}"
    if t is ScalarDiv:
        return rf"\frac{{{render_latex(node.x)}}}{{{node.k:g}}}"

    if t is Gp:
        left = _wrap_latex(render_latex(node.a), node.a, 80)
        right = _wrap_latex(render_latex(node.b), node.b, 80)
        return f"{left} {right}"

    if t is Op:
        left = render_latex(node.a)
        if not isinstance(node.a, Op):
            left = _wrap_latex(left, node.a, 81)
        right = render_latex(node.b)
        if not isinstance(node.b, Op):
            right = _wrap_latex(right, node.b, 81)
        return rf"{left} \wedge {right}"
    if t is Lc:
        left = _wrap_latex(render_latex(node.a), node.a, 71)
        right = _wrap_latex(render_latex(node.b), node.b, 71)
        return rf"{left} \;\lrcorner\; {right}"
    if t is Rc:
        left = _wrap_latex(render_latex(node.a), node.a, 71)
        right = _wrap_latex(render_latex(node.b), node.b, 71)
        return rf"{left} \;\llcorner\; {right}"
    if t is Hi:
        left = _wrap_latex(render_latex(node.a), node.a, 71)
        right = _wrap_latex(render_latex(node.b), node.b, 71)
        return rf"{left} \cdot {right}"
    if t is Dli:
        left = _wrap_latex(render_latex(node.a), node.a, 71)
        right = _wrap_latex(render_latex(node.b), node.b, 71)
        return rf"{left} \cdot {right}"
    if t is Sp:
        left = _wrap_latex(render_latex(node.a), node.a, 71)
        right = _wrap_latex(render_latex(node.b), node.b, 71)
        return rf"{left} * {right}"
    if t is Div:
        return rf"\frac{{{render_latex(node.a)}}}{{{render_latex(node.b)}}}"

    if t is Add:
        return f"{render_latex(node.a)} + {render_latex(node.b)}"
    if t is Sub:
        right = render_latex(node.b)
        right = _wrap_latex(right, node.b, 61)
        return f"{render_latex(node.a)} - {right}"

    if t is Reverse:
        inner = render_latex(node.x)
        return rf"\tilde{{{_wrap_latex(inner, node.x, 95)}}}"
    if t is Involute:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return rf"{inner}^\dagger"
    if t is Conjugate:
        inner = render_latex(node.x)
        return rf"\bar{{{_wrap_latex(inner, node.x, 95)}}}"
    if t is Dual:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return rf"{inner}^*"
    if t is Undual:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return rf"{inner}^{{*^{{-1}}}}"
    if t is Inverse:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return rf"{inner}^{{-1}}"
    if t is Squared:
        inner = _wrap_latex(render_latex(node.x), node.x, 95)
        return f"{inner}^2"

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
