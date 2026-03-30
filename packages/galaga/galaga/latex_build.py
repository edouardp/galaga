"""Build a LaTeX render tree (LNode) from a symbolic Expr tree.

Single responsibility: map each Expr node type to the corresponding
LNode structure, handling precedence-based parenthesization. No knowledge
of context-dependent rewrites (that's latex_rewrite) or serialization
(that's latex_emit).

The builder uses the same Notation and OpInfo registry as the unicode
renderer in render.py, ensuring consistent precedence decisions.
"""

from __future__ import annotations

from galaga.expr import (
    Add,
    Conjugate,
    Div,
    Exp,
    Expr,
    Gp,
    Grade,
    Log,
    Neg,
    Norm,
    Reverse,
    Scalar,
    ScalarDiv,
    ScalarMul,
    Sqrt,
    Sub,
    Sym,
    Unit,
)
from galaga.latex_nodes import Command, Frac, LNode, Parens, Seq, Sup, Text
from galaga.notation import Notation
from galaga.render import _CHILD_MIN, _COMMA_BINARY, _NAME, _needs_wrap

_DEFAULT = Notation()


def _is_single_latex_glyph(s: str) -> bool:
    """True if s renders as a single glyph in LaTeX (e.g. 'R', '\\theta', '\\mathbf{F}')."""
    if len(s) <= 1:
        return True
    # LaTeX commands render as single glyphs: \theta, \alpha, \mathbf{X}, etc.
    return s.startswith("\\")


def build(node: Expr, notation: Notation | None = None) -> LNode:
    """Build an LNode tree from an Expr tree."""
    n = notation or _DEFAULT
    return _build(node, n)


def _wp(child_lnode: LNode, child_expr: Expr, min_prec: int, parent_type=None) -> LNode:
    """Wrap child in Parens if its precedence is too low."""
    if _needs_wrap(child_expr, min_prec, parent_type):
        return Parens(child_lnode)
    return child_lnode


def _build(node: Expr, n: Notation) -> LNode:
    t = type(node)
    name = _NAME.get(t, "")

    # Atoms
    if t is Sym:
        return Text(node._name_latex)
    if t is Scalar:
        return Text(f"{node._value:g}")

    # Neg: -child
    if t is Neg:
        inner = _build(node.x, n)
        return Seq([Text("-"), _wp(inner, node.x, 61)])

    # ScalarMul: k * child or -child
    if t is ScalarMul:
        inner = _build(node.x, n)
        if node.k == -1:
            return Seq([Text("-"), _wp(inner, node.x, 61)])
        return Seq([Text(f"{node.k:g} "), _wp(inner, node.x, 61)])

    # ScalarDiv: frac{child}{k}
    if t is ScalarDiv:
        return Frac(_build(node.x, n), Text(f"{node.k:g}"))

    # Gp: juxtaposition with space (unless overridden to function style)
    if t is Gp:
        gp_rule = n.get("Gp", "latex")
        if gp_rule and gp_rule.kind == "function":
            la = _build(node.a, n)
            lb = _build(node.b, n)
            return Seq([Text(rf"\operatorname{{{gp_rule.symbol}}}("), la, Text(r",\, "), lb, Text(")")])
        la = _wp(_build(node.a, n), node.a, 80, Gp)
        lb = _wp(_build(node.b, n), node.b, 80, Gp)
        return Seq([la, lb], sep=" ")

    # Add: a + b (renders as a - b when b is negative)
    if t is Add:
        la = _wp(_build(node.a, n), node.a, 60, Add)
        if isinstance(node.b, ScalarMul) and node.b.k < 0:
            pos = ScalarMul(-node.b.k, node.b.x)
            lb = _build(pos, n) if pos.k != 1 else _build(pos.x, n)
            return Seq([la, Text(" - "), lb])
        if isinstance(node.b, Neg):
            lb = _wp(_build(node.b.x, n), node.b.x, 61)
            return Seq([la, Text(" - "), lb])
        lb = _build(node.b, n)
        return Seq([la, Text(" + "), lb])

    # Sub: a - b
    if t is Sub:
        la = _build(node.a, n)
        lb = _wp(_build(node.b, n), node.b, 61)
        return Seq([la, Text(" - "), lb])

    # Div: frac{a}{b}
    if t is Div:
        return Frac(_build(node.a, n), _build(node.b, n))

    # Notation-driven rendering
    rule = n.get(name, "latex")
    if not rule:
        return Text(str(node))

    # Infix binary
    if rule.kind == "infix" and hasattr(node, "a"):
        mp = _CHILD_MIN.get(t, 71)
        la = _wp(_build(node.a, n), node.a, mp, t)
        lb = _wp(_build(node.b, n), node.b, mp, t)
        return Seq([la, Text(rule.separator), lb])

    # Function call
    if rule.kind == "function":
        if hasattr(node, "a"):
            return Seq(
                [
                    Text(rf"\operatorname{{{rule.symbol}}}("),
                    _build(node.a, n),
                    Text(r",\, "),
                    _build(node.b, n),
                    Text(")"),
                ]
            )
        if t is Grade:
            return Seq(
                [
                    Text(rf"\operatorname{{{rule.symbol}}}("),
                    _build(node.x, n),
                    Text(f",\\, {node.k})"),
                ]
            )
        return Seq(
            [
                Text(rf"\operatorname{{{rule.symbol}}}("),
                _build(node.x, n),
                Text(")"),
            ]
        )

    # Prefix unary
    if rule.kind == "prefix" and hasattr(node, "x"):
        inner = _wp(_build(node.x, n), node.x, 95)
        # LaTeX commands (e.g. \tilde) need a space before the operand
        # to avoid running together: \tilde v not \tildev
        sep = " " if rule.symbol.startswith("\\") and rule.symbol[-1:].isalpha() else ""
        return Seq([Text(rule.symbol), inner], sep=sep)

    # Accent (combining diacritical or wide accent)
    if rule.kind == "accent" and hasattr(node, "x"):
        # Use narrow accent (\tilde) for single-glyph names, wide (\widetilde) otherwise.
        # LaTeX commands like \theta, \mathbf{F} render as single glyphs.
        is_single_glyph = isinstance(node.x, Sym) and _is_single_latex_glyph(node.x._name_latex or node.x._name)
        if t in (Reverse, Conjugate):
            inner = _build(node.x, n)
        else:
            inner = _wp(_build(node.x, n), node.x, 95)
        cmd = rule.latex_cmd if is_single_glyph else rule.latex_wide_cmd
        return Command(cmd, inner)

    # Postfix
    if rule.kind == "postfix" and hasattr(node, "x"):
        inner = _wp(_build(node.x, n), node.x, 96)
        # If the postfix symbol starts with ^ (superscript) and the child
        # already rendered as a Sup, wrap in braces to avoid double-superscript:
        # {e^{x}}^{\dagger} not e^{x}^{\dagger}
        if rule.symbol.startswith("^") and isinstance(inner, Sup):
            inner = Seq([Text("{"), inner, Text("}")])
        return Seq([inner, Text(rule.symbol)])

    # Superscript: symbol goes in ^{...}, auto-braced. The user writes
    # just the symbol (e.g. r"\dagger"), not the ^{} wrapper.
    if rule.kind == "superscript" and hasattr(node, "x"):
        inner = _wp(_build(node.x, n), node.x, 96)
        return Sup(inner, Text(rule.symbol))

    # Wrap (delimiters around content)
    if rule.kind == "wrap":
        if t in _COMMA_BINARY:
            return Seq(
                [
                    Text(rule.open),
                    _build(node.a, n),
                    Text(r",\, "),
                    _build(node.b, n),
                    Text(rule.close),
                ]
            )
        if t is Grade:
            return Seq(
                [
                    Text(rule.open),
                    _build(node.x, n),
                    Text(f"{rule.close}_{{{node.k}}}"),
                ]
            )
        if t is Unit:
            if isinstance(node.x, (Sym, Scalar)):
                cmd = rule.latex_cmd or r"\hat"
                return Command(cmd, _build(node.x, n))
            num = _wp(_build(node.x, n), node.x, 70)
            den = _build(Norm(node.x), n)
            return Frac(num, den)
        if t is Exp:
            return Sup(Text("e"), _build(node.x, n))
        if t is Log:
            return Seq([Text(r"\log\left("), _build(node.x, n), Text(r"\right)")])
        if t is Sqrt:
            return Command(r"\sqrt", _build(node.x, n))
        # Generic wrap
        return Seq([Text(rule.open), _build(node.x, n), Text(rule.close)])

    return Text(str(node))
