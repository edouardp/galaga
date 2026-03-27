"""Precedence-aware tree-walking renderer for symbolic expressions.

A standalone visitor that walks an Expr tree and produces correctly
parenthesized unicode or LaTeX output. Operation metadata (precedence,
associativity, flattenability) is stored in a registry. Rendering
rules come from a Notation object (configurable per-algebra).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ga.notation import Notation, NotationRule
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

# Subscript/superscript codepoint ranges
_SUB_SUPER = set("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₔₕₖₗₘₙₚₛₜ"
                 "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")


def _base_len(s: str) -> int:
    import unicodedata
    n = 0
    for c in s:
        cat = unicodedata.category(c)
        if cat.startswith("M"):
            continue
        if c in _SUB_SUPER:
            continue
        n += 1
    return n


def _is_single_char_name(s: str) -> bool:
    return _base_len(s) == 1


# ============================================================
# Precedence
# ============================================================

class Assoc(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class OpInfo:
    prec: int
    assoc: Assoc = Assoc.NONE
    flat: bool = False


INFO: dict[type, OpInfo] = {
    Sym: OpInfo(100), Scalar: OpInfo(100),
    Reverse: OpInfo(95), Involute: OpInfo(95), Conjugate: OpInfo(95),
    Dual: OpInfo(95), Undual: OpInfo(95), Inverse: OpInfo(95), Squared: OpInfo(95),
    Neg: OpInfo(90), ScalarMul: OpInfo(80), ScalarDiv: OpInfo(80),
    Gp: OpInfo(80, Assoc.LEFT, flat=True),
    Op: OpInfo(70, Assoc.LEFT, flat=True),
    Lc: OpInfo(70, Assoc.LEFT), Rc: OpInfo(70, Assoc.LEFT),
    Hi: OpInfo(70, Assoc.LEFT), Dli: OpInfo(70, Assoc.LEFT),
    Sp: OpInfo(70, Assoc.LEFT), Div: OpInfo(70, Assoc.LEFT),
    Add: OpInfo(60, Assoc.LEFT, flat=True),
    Sub: OpInfo(60, Assoc.LEFT),
    Grade: OpInfo(100), Norm: OpInfo(100), Unit: OpInfo(100),
    Exp: OpInfo(100), Even: OpInfo(100), Odd: OpInfo(100),
    Commutator: OpInfo(100), Anticommutator: OpInfo(100),
    LieBracket: OpInfo(100), JordanProduct: OpInfo(100),
}

_BINARY_CHILD_MIN = {
    Gp: 80, Op: 81,
    Lc: 71, Rc: 71, Hi: 71, Dli: 71, Sp: 71,
}

_NODE_NAME = {cls: cls.__name__ for cls in INFO}


def _prec(node: Expr) -> int:
    return INFO.get(type(node), OpInfo(0)).prec


def _needs_wrap(child: Expr, min_prec: int, parent_type: type = None) -> bool:
    ci = INFO.get(type(child), OpInfo(0))
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


def _has_multichar_name(node: Expr) -> bool:
    if isinstance(node, Sym):
        return not _is_single_char_name(node._name)
    if isinstance(node, (ScalarMul, Neg)):
        return _has_multichar_name(node.x)
    if isinstance(node, (Reverse, Involute, Conjugate, Dual, Undual, Inverse, Squared)):
        return _has_multichar_name(node.x)
    return False


# Default notation singleton
_DEFAULT_NOTATION = Notation()


# ============================================================
# Rendering helpers
# ============================================================

def _render_accent_unicode(rule: NotationRule, inner: str, is_atom: bool) -> str:
    if is_atom and rule.combining:
        return f"{inner}{rule.combining}"
    if rule.fallback_prefix:
        return f"{rule.fallback_prefix}({inner})"
    return f"{inner}{rule.combining}"


def _render_accent_latex(rule: NotationRule, inner: str, is_atom: bool) -> str:
    if is_atom:
        return f"{rule.latex_cmd}{{{inner}}}"
    return f"{rule.latex_wide_cmd}{{{inner}}}"


# ============================================================
# Unicode renderer
# ============================================================

def render(node: Expr, notation: Notation | None = None) -> str:
    n = notation or _DEFAULT_NOTATION
    t = type(node)
    name = _NODE_NAME.get(t, "")

    # Atoms
    if t is Sym:
        return node._name
    if t is Scalar:
        return f"{node._value:g}"

    # ScalarMul / ScalarDiv — special handling
    if t is ScalarMul:
        inner = render(node.x, n)
        if node.k == -1:
            return f"-{_wrap(inner, node.x, 61)}"
        return f"{node.k:g}{_wrap(inner, node.x, 61)}"
    if t is ScalarDiv:
        inner = render(node.x, n)
        return f"{_wrap(inner, node.x, 70)}/{node.k:g}"

    # Neg
    if t is Neg:
        inner = render(node.x, n)
        return f"-{_wrap(inner, node.x, 61)}"

    # Geometric product (juxtaposition with smart spacing)
    if t is Gp:
        left = _wrap(render(node.a, n), node.a, 80, parent_type=Gp)
        right = _wrap(render(node.b, n), node.b, 80, parent_type=Gp)
        if _has_multichar_name(node.a) or _has_multichar_name(node.b):
            return f"{left} {right}"
        return f"{left}{right}"

    # Div (unicode uses / with tight denom wrapping)
    if t is Div:
        left = _wrap(render(node.a, n), node.a, 71)
        right = _wrap(render(node.b, n), node.b, 95)
        return f"{left}/{right}"

    # Add/Sub
    if t is Add:
        left = _wrap(render(node.a, n), node.a, 60, parent_type=Add)
        return f"{left} + {render(node.b, n)}"
    if t is Sub:
        left = render(node.a, n)
        right = _wrap(render(node.b, n), node.b, 61)
        return f"{left} - {right}"

    # Infix binary ops (Op, Lc, Rc, Hi, Dli, Sp)
    rule = n.get(name, "unicode")
    if rule and rule.kind == "infix":
        min_p = _BINARY_CHILD_MIN.get(t, 71)
        left = _wrap(render(node.a, n), node.a, min_p, parent_type=t)
        right = _wrap(render(node.b, n), node.b, min_p, parent_type=t)
        return f"{left}{rule.separator}{right}"

    # Function-style binary: "wedge(a, b)"
    if rule and rule.kind == "function" and hasattr(node, 'a'):
        return f"{rule.symbol}({render(node.a, n)}, {render(node.b, n)})"

    # Unit — special: hat for single-char atoms, fraction for compounds
    if t is Unit:
        if isinstance(node.x, Sym) and _is_single_char_name(str(node.x)):
            ur = n.get("Unit", "unicode")
            if ur and ur.combining:
                return f"{render(node.x, n)}{ur.combining}"
        inner = render(node.x, n)
        return f"{_wrap(inner, node.x, 70)}/‖{render(node.x, n)}‖"

    # Accent unary (reverse, involute, conjugate)
    if rule and rule.kind == "accent":
        inner = render(node.x, n)
        is_atom = isinstance(node.x, (Sym, Scalar))
        return _render_accent_unicode(rule, inner, is_atom)

    # Function-style unary: "rev(x)"
    if rule and rule.kind == "function":
        return f"{rule.symbol}({render(node.x, n)})"

    # Postfix unary (dual, inverse, squared, undual)
    if rule and rule.kind == "postfix":
        inner = render(node.x, n)
        return f"{_wrap(inner, node.x, 95)}{rule.symbol}"

    # Wrap (grade, norm, exp, commutators, etc.)
    if rule and rule.kind == "wrap":
        if t is Grade:
            sub = str(node.k).translate(_SUBSCRIPTS)
            return f"{rule.open}{render(node.x, n)}{rule.close}{sub}"
        if t in (Commutator, Anticommutator, LieBracket, JordanProduct):
            return f"{rule.open}{render(node.a, n)}, {render(node.b, n)}{rule.close}"
        return f"{rule.open}{render(node.x, n)}{rule.close}"

    return str(node)


# ============================================================
# LaTeX renderer
# ============================================================

def render_latex(node: Expr, notation: Notation | None = None) -> str:
    n = notation or _DEFAULT_NOTATION
    t = type(node)
    name = _NODE_NAME.get(t, "")

    if t is Sym:
        return node._name_latex
    if t is Scalar:
        return f"{node._value:g}"

    if t is ScalarMul:
        inner = render_latex(node.x, n)
        if node.k == -1:
            return f"-{_wrap_latex(inner, node.x, 61)}"
        return f"{node.k:g} {_wrap_latex(inner, node.x, 61)}"
    if t is ScalarDiv:
        return rf"\frac{{{render_latex(node.x, n)}}}{{{node.k:g}}}"

    if t is Neg:
        inner = render_latex(node.x, n)
        return f"-{_wrap_latex(inner, node.x, 61)}"

    if t is Gp:
        left = _wrap_latex(render_latex(node.a, n), node.a, 80, parent_type=Gp)
        right = _wrap_latex(render_latex(node.b, n), node.b, 80, parent_type=Gp)
        return f"{left} {right}"

    if t is Div:
        return rf"\frac{{{render_latex(node.a, n)}}}{{{render_latex(node.b, n)}}}"

    if t is Add:
        left = _wrap_latex(render_latex(node.a, n), node.a, 60, parent_type=Add)
        return f"{left} + {render_latex(node.b, n)}"
    if t is Sub:
        left = render_latex(node.a, n)
        right = _wrap_latex(render_latex(node.b, n), node.b, 61)
        return f"{left} - {right}"

    # Infix binary
    rule = n.get(name, "latex")
    if rule and rule.kind == "infix":
        min_p = _BINARY_CHILD_MIN.get(t, 71)
        left = _wrap_latex(render_latex(node.a, n), node.a, min_p, parent_type=t)
        right = _wrap_latex(render_latex(node.b, n), node.b, min_p, parent_type=t)
        return f"{left}{rule.separator}{right}"

    # Function-style binary: "\operatorname{wedge}(a, b)"
    if rule and rule.kind == "function" and hasattr(node, 'a'):
        return rf"\operatorname{{{rule.symbol}}}({render_latex(node.a, n)}, {render_latex(node.b, n)})"


    # Accent (reverse, involute, conjugate)
    if rule and rule.kind == "accent":
        is_atom = isinstance(node.x, (Sym, Scalar))
        if t in (Reverse, Conjugate):
            # Wide accents don't need parens
            inner = render_latex(node.x, n)
        else:
            inner = _wrap_latex(render_latex(node.x, n), node.x, 95)
        return _render_accent_latex(rule, inner, is_atom)

    # Function-style unary: "\operatorname{rev}(x)"
    if rule and rule.kind == "function":
        return rf"\operatorname{{{rule.symbol}}}({render_latex(node.x, n)})"

    # Postfix
    if rule and rule.kind == "postfix":
        inner = _wrap_latex(render_latex(node.x, n), node.x, 95)
        return f"{inner}{rule.symbol}"

    # Wrap
    if rule and rule.kind == "wrap":
        if t is Grade:
            return rf"{rule.open}{render_latex(node.x, n)}{rule.close}_{{{node.k}}}"
        if t in (Commutator, Anticommutator, LieBracket, JordanProduct):
            return rf"{rule.open}{render_latex(node.a, n)},\, {render_latex(node.b, n)}{rule.close}"
        if t is Unit:
            if isinstance(node.x, (Sym, Scalar)):
                lr = n.get("Unit", "latex")
                return rf"{lr.latex_cmd}{{{render_latex(node.x, n)}}}"
            num = _wrap_latex(render_latex(node.x, n), node.x, 70)
            return rf"\frac{{{num}}}{{{render_latex(Norm(node.x), n)}}}"
        if t is Exp:
            return rf"e^{{{render_latex(node.x, n)}}}"
        return f"{rule.open}{render_latex(node.x, n)}{rule.close}"

    return str(node)
