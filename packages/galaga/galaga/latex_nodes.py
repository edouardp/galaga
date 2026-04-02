"""Intermediate render tree for LaTeX output.

This module defines a small tree of typed nodes that sits between the
symbolic Expr tree and the final LaTeX string. The pipeline is:

    Expr  →  latex_build()  →  LatexNode tree
          →  latex_rewrite() →  LatexNode tree (transformed)
          →  latex_emit()   →  str

Why an intermediate tree?
    The Expr tree describes mathematical structure (Add, Gp, Reverse, etc.).
    The LaTeX string describes typesetting. Some typesetting decisions depend
    on context that isn't available during a single recursive walk — e.g.
    \\frac should become \\tfrac when it appears inside a superscript.
    The intermediate tree makes context available for a rewrite pass.

Node types:
    Text     — literal LaTeX string (leaf)
    Seq      — concatenation of children
    Frac     — \\frac{num}{den} or \\tfrac{num}{den}
    Sup      — base^{exponent}  (superscript)
    Parens   — \\left( child \\right)
    Command  — \\cmd{child}  (e.g. \\tilde, \\widetilde, \\hat)
"""

from __future__ import annotations

from dataclasses import dataclass


class LNode:
    """Base class for all LaTeX render tree nodes."""

    pass


@dataclass
class Text(LNode):
    """Literal LaTeX text. Leaf node."""

    text: str


@dataclass
class Seq(LNode):
    """Concatenation of child nodes, joined by a separator string."""

    children: list[LNode]
    sep: str = ""


@dataclass
class Frac(LNode):
    """Fraction: \\frac{num}{den}. The `small` flag selects \\tfrac."""

    num: LNode
    den: LNode
    small: bool = False


@dataclass
class Sup(LNode):
    """Superscript: base^{exponent}."""

    base: LNode
    exp: LNode


@dataclass
class Parens(LNode):
    """Parenthesized group: \\left( child \\right)."""

    child: LNode


@dataclass
class Command(LNode):
    """LaTeX command wrapping a child: \\cmd{child}."""

    cmd: str
    child: LNode


@dataclass
class SlashFrac(LNode):
    """Inline fraction: num/den. Created by rewrite when Frac is in a superscript.

    Separate node type so the rewrite pass can detect it in a Seq and wrap
    it in Parens when adjacent to other terms (avoiding ambiguity).
    """

    num: LNode
    den: LNode
