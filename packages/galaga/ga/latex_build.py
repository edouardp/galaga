"""Build a LaTeX render tree (LNode) from a symbolic Expr tree.

Single responsibility: map each Expr node type to the corresponding
LNode structure, handling precedence-based parenthesization. No knowledge
of context-dependent rewrites (that's latex_rewrite) or serialization
(that's latex_emit).

The builder uses the same Notation and OpInfo registry as the unicode
renderer in render.py, ensuring consistent precedence decisions.
"""

from __future__ import annotations

from ga.latex_nodes import LNode, Text, Seq, Frac, Sup, Parens, Command
from ga.notation import Notation
from ga.symbolic import (
    Expr, Sym, Scalar,
    Gp, Op, Add, Sub, Neg, ScalarMul, ScalarDiv, Div,
    Reverse, Involute, Conjugate, Dual, Undual, Complement, Uncomplement,
    Inverse, Squared, Exp, Log,
    Grade, Norm, Unit, Even, Odd,
    Lc, Rc, Hi, Dli, Sp, Regressive,
    Commutator, Anticommutator, LieBracket, JordanProduct,
)
from ga.render import INFO, _NAME, _CHILD_MIN, _COMMA_BINARY, _needs_wrap, Notation as _Notation


_DEFAULT = Notation()


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

    # Gp: juxtaposition with space
    if t is Gp:
        la = _wp(_build(node.a, n), node.a, 80, Gp)
        lb = _wp(_build(node.b, n), node.b, 80, Gp)
        return Seq([la, lb], sep=" ")

    # Add: a + b
    if t is Add:
        la = _wp(_build(node.a, n), node.a, 60, Add)
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
    if rule.kind == "infix" and hasattr(node, 'a'):
        mp = _CHILD_MIN.get(t, 71)
        la = _wp(_build(node.a, n), node.a, mp, t)
        lb = _wp(_build(node.b, n), node.b, mp, t)
        return Seq([la, Text(rule.separator), lb])

    # Function call
    if rule.kind == "function":
        if hasattr(node, 'a'):
            return Seq([
                Text(rf"\operatorname{{{rule.symbol}}}("),
                _build(node.a, n), Text(r",\, "), _build(node.b, n),
                Text(")"),
            ])
        return Seq([
            Text(rf"\operatorname{{{rule.symbol}}}("),
            _build(node.x, n),
            Text(")"),
        ])

    # Prefix unary
    if rule.kind == "prefix" and hasattr(node, 'x'):
        inner = _wp(_build(node.x, n), node.x, 95)
        return Seq([Text(rule.symbol), inner])

    # Accent (combining diacritical or wide accent)
    if rule.kind == "accent" and hasattr(node, 'x'):
        is_atom = isinstance(node.x, (Sym, Scalar))
        if t in (Reverse, Conjugate):
            inner = _build(node.x, n)
        else:
            inner = _wp(_build(node.x, n), node.x, 95)
        cmd = rule.latex_cmd if is_atom else rule.latex_wide_cmd
        return Command(cmd, inner)

    # Postfix
    if rule.kind == "postfix" and hasattr(node, 'x'):
        inner = _wp(_build(node.x, n), node.x, 96)
        # If the postfix symbol starts with ^ (superscript) and the child
        # already rendered as a Sup, wrap in braces to avoid double-superscript:
        # {e^{x}}^{\dagger} not e^{x}^{\dagger}
        if rule.symbol.startswith("^") and isinstance(inner, Sup):
            inner = Seq([Text("{"), inner, Text("}")])
        return Seq([inner, Text(rule.symbol)])

    # Superscript: symbol goes in ^{...}, auto-braced. The user writes
    # just the symbol (e.g. r"\dagger"), not the ^{} wrapper.
    if rule.kind == "superscript" and hasattr(node, 'x'):
        inner = _wp(_build(node.x, n), node.x, 96)
        return Sup(inner, Text(rule.symbol))

    # Wrap (delimiters around content)
    if rule.kind == "wrap":
        if t in _COMMA_BINARY:
            return Seq([
                Text(rule.open), _build(node.a, n),
                Text(r",\, "), _build(node.b, n),
                Text(rule.close),
            ])
        if t is Grade:
            return Seq([
                Text(rule.open), _build(node.x, n),
                Text(f"{rule.close}_{{{node.k}}}"),
            ])
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
        # Generic wrap
        return Seq([Text(rule.open), _build(node.x, n), Text(rule.close)])

    return Text(str(node))
