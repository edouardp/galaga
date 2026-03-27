"""Context-dependent rewrites on the LaTeX render tree.

Single responsibility: walk an LNode tree and apply structural transforms
that depend on context (ancestor nodes). The tree is rebuilt immutably —
input nodes are not mutated.

Current rewrites:
    - Frac inside Sup → Frac(small=True)
      \\frac in a superscript is too tall; \\tfrac renders inline-sized.

Future rewrites could include:
    - Collapsing redundant \\left(\\right) nesting
    - Auto-sizing delimiters based on content depth
    - Simplifying \\operatorname for known functions
"""

from __future__ import annotations

from ga.latex_nodes import LNode, Text, Seq, Frac, Sup, Parens, Command


def rewrite(node: LNode) -> LNode:
    """Apply all rewrite rules to an LNode tree. Returns a new tree."""
    return _walk(node, in_sup=False)


def _walk(node: LNode, *, in_sup: bool) -> LNode:
    """Recursive walk. `in_sup` is True when inside a Sup exponent."""
    t = type(node)

    if t is Text:
        return node

    if t is Seq:
        return Seq([_walk(c, in_sup=in_sup) for c in node.children], sep=node.sep)

    if t is Frac:
        # Core rewrite: frac inside superscript → inline slash (a/b)
        # \frac in a superscript renders too tall; inline slash is compact.
        if in_sup:
            return Seq([
                _walk(node.num, in_sup=True),
                Text("/"),
                _walk(node.den, in_sup=True),
            ])
        return Frac(
            _walk(node.num, in_sup=in_sup),
            _walk(node.den, in_sup=in_sup),
            small=node.small,
        )

    if t is Sup:
        # Base is NOT inside a superscript; exponent IS.
        return Sup(
            _walk(node.base, in_sup=in_sup),
            _walk(node.exp, in_sup=True),
        )

    if t is Parens:
        return Parens(_walk(node.child, in_sup=in_sup))

    if t is Command:
        return Command(node.cmd, _walk(node.child, in_sup=in_sup))

    raise TypeError(f"Unknown LNode type: {t}")
