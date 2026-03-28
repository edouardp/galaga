"""Serialize a LaTeX render tree to a string.

Single responsibility: walk an LNode tree and produce the final LaTeX
string. No knowledge of Expr trees, notation, or precedence — just
straightforward serialization of the intermediate representation.
"""

from __future__ import annotations

from galaga.latex_nodes import LNode, Text, Seq, Frac, Sup, Parens, Command


def emit(node: LNode) -> str:
    """Convert an LNode tree to a LaTeX string."""
    t = type(node)

    if t is Text:
        return node.text

    if t is Seq:
        return node.sep.join(emit(c) for c in node.children)

    if t is Frac:
        cmd = r"\tfrac" if node.small else r"\frac"
        return f"{cmd}{{{emit(node.num)}}}{{{emit(node.den)}}}"

    if t is Sup:
        base = emit(node.base)
        # Brace-wrap if base is also a Sup to avoid double-superscript
        if isinstance(node.base, Sup):
            base = "{" + base + "}"
        return f"{base}^{{{emit(node.exp)}}}"

    if t is Parens:
        return rf"\left({emit(node.child)}\right)"

    if t is Command:
        return f"{node.cmd}{{{emit(node.child)}}}"

    raise TypeError(f"Unknown LNode type: {t}")
