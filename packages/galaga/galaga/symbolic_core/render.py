"""Small precedence-aware renderer for non-GA symbolic domains."""

from __future__ import annotations

from .expr import Add, Div, Expr, Neg, Scalar, ScalarDiv, ScalarMul, Sub, Sym

_PREC = {
    Sym: 100,
    Scalar: 100,
    Neg: 90,
    ScalarMul: 80,
    ScalarDiv: 80,
    Div: 70,
    Add: 60,
    Sub: 60,
}


def _node_prec(node: Expr) -> int:
    if hasattr(node, "_render_prec"):
        return node._render_prec
    return _PREC.get(type(node), 50)


def _wrap(rendered: str, child: Expr, min_prec: int) -> str:
    return f"({rendered})" if _node_prec(child) < min_prec else rendered


def _fmt_scalar(value) -> str:
    try:
        return f"{value:g}"
    except (TypeError, ValueError):
        return str(value)


def render(node: Expr) -> str:
    return _render(node, "unicode")


def render_latex(node: Expr) -> str:
    return _render(node, "latex")


def _render(node: Expr, fmt: str) -> str:
    if hasattr(node, "_render"):
        return node._render(lambda child: _render(child, fmt), fmt)

    t = type(node)
    if t is Sym:
        return node._name_latex if fmt == "latex" else node._name
    if t is Scalar:
        return _fmt_scalar(node._value)
    if t is Neg:
        return f"-{_wrap(_render(node.x, fmt), node.x, 61)}"
    if t is ScalarMul:
        inner = _wrap(_render(node.x, fmt), node.x, 61)
        if node.k == 1:
            return inner
        if node.k == -1:
            return f"-{inner}"
        return f"{_fmt_scalar(node.k)}{inner}"
    if t is ScalarDiv:
        inner = _wrap(_render(node.x, fmt), node.x, 70)
        if fmt == "latex":
            return rf"\frac{{{inner}}}{{{_fmt_scalar(node.k)}}}"
        return f"{inner}/{_fmt_scalar(node.k)}"
    if t is Add:
        lhs = _wrap(_render(node.a, fmt), node.a, 60)
        rhs = _render(node.b, fmt)
        if rhs.startswith("-"):
            return f"{lhs} - {rhs[1:]}"
        return f"{lhs} + {rhs}"
    if t is Sub:
        return f"{_render(node.a, fmt)} - {_wrap(_render(node.b, fmt), node.b, 61)}"
    if t is Div:
        lhs = _wrap(_render(node.a, fmt), node.a, 71)
        rhs = _wrap(_render(node.b, fmt), node.b, 95)
        if fmt == "latex":
            return rf"\frac{{{lhs}}}{{{rhs}}}"
        return f"{lhs}/{rhs}"

    return repr(node)
