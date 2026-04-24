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

import re as _re
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


# --- Coefficient formatting helpers ---


def fmt_coeff(c: float) -> str:
    """Format a coefficient for default LaTeX display.

    Uses Python's :g (6 significant digits) but forces non-scientific
    notation for numbers with abs >= 1e-6.
    """
    if c == 0:
        return "0"
    s = f"{c:g}"
    if abs(c) >= 1e-6 and ("e" in s or "E" in s):
        s = f"{c:.6f}".rstrip("0").rstrip(".")
    return s


def sci_lnode(s: str, style: str) -> LNode:
    """Convert a formatted number string to an LNode, handling scientific notation.

    Returns Text for plain numbers, or Seq with Sup for scientific notation.
    """
    if style == "raw":
        return Text(s)
    m = _re.match(r"^(-?)(\d+\.?\d*)[eE]([+-]?\d+)$", s)
    if not m:
        return Text(s)
    sign, mantissa, exp = m.groups()
    exp_int = int(exp)
    sep = r" \times " if style == "times" else r" \cdot "
    if mantissa in ("1", "1."):
        return Seq([Text(sign), Sup(Text("10"), Text(str(exp_int)))])
    return Seq([Text(f"{sign}{mantissa}{sep}"), Sup(Text("10"), Text(str(exp_int)))])
