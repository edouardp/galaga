"""Context-dependent rewrites on the LaTeX render tree.

Single responsibility: walk an LNode tree and apply structural transforms
that depend on context (ancestor nodes). The tree is rebuilt immutably —
input nodes are not mutated.

Current rewrites:
    1. Frac inside Sup → inline slash (a/b instead of \\frac{a}{b})
    2. Collapse nested Parens: Parens(Parens(x)) → Parens(x)
    3. Hoist negation out of fractions: \\frac{-a}{b} → -\\frac{a}{b}
    4. Simplify trivial denominators: \\frac{a}{1} → a
"""

from __future__ import annotations

from .latex_nodes import Command, Frac, LNode, Parens, Seq, SlashFrac, Sup, Text


def rewrite(node: LNode) -> LNode:
    """Apply all rewrite rules to an LNode tree. Returns a new tree."""
    node = _walk(node, in_sup=False)
    return _wrap_ambiguous_slashes(node)


def _is_neg_seq(node: LNode) -> bool:
    """True if node is Seq([Text("-"), ...]) — a structured negation."""
    return (
        isinstance(node, Seq)
        and len(node.children) >= 2
        and isinstance(node.children[0], Text)
        and node.children[0].text == "-"
        and node.sep == ""
    )


def _walk(node: LNode, *, in_sup: bool) -> LNode:
    """Recursive walk. `in_sup` is True when inside a Sup exponent."""
    t = type(node)

    if t is Text:
        return node

    if t is Seq:
        return Seq([_walk(c, in_sup=in_sup) for c in node.children], sep=node.sep)

    if t is Frac:
        num = _walk(node.num, in_sup=in_sup)
        den = _walk(node.den, in_sup=in_sup)

        # Rewrite 4: frac{x}{1} → x
        if isinstance(den, Text) and den.text == "1":
            return num

        # Rewrite 3: hoist negation — frac{-a}{b} → -frac{a}{b}
        # Only when num is a structured Seq starting with Text("-")
        if _is_neg_seq(num) and not in_sup:
            inner_num = Seq(num.children[1:], sep=num.sep) if len(num.children) > 2 else num.children[1]
            return Seq([Text("-"), Frac(inner_num, den, small=node.small)])

        # Rewrite 1: frac inside superscript → SlashFrac (inline slash)
        if in_sup:
            # Hoist neg before slash too: -a/b not (-a)/b
            if _is_neg_seq(num):
                inner_num = Seq(num.children[1:], sep=num.sep) if len(num.children) > 2 else num.children[1]
                return Seq([Text("-"), SlashFrac(inner_num, den)])
            return SlashFrac(num, den)

        return Frac(num, den, small=node.small)

    if t is Sup:
        return Sup(
            _walk(node.base, in_sup=in_sup),
            _walk(node.exp, in_sup=True),
        )

    # Rewrite 2: collapse nested Parens
    if t is Parens:
        child = _walk(node.child, in_sup=in_sup)
        while isinstance(child, Parens):
            child = child.child
        return Parens(child)

    if t is Command:
        return Command(node.cmd, _walk(node.child, in_sup=in_sup))

    if t is SlashFrac:
        return SlashFrac(
            _walk(node.num, in_sup=in_sup),
            _walk(node.den, in_sup=in_sup),
        )

    raise TypeError(f"Unknown LNode type: {t}")


def _wrap_ambiguous_slashes(node: LNode) -> LNode:
    """Wrap SlashFrac in Parens when it has siblings in a Seq.

    A standalone SlashFrac like e^{a/2} is unambiguous.
    A SlashFrac adjacent to other terms like e^{a/2 b} is ambiguous —
    wrap it: e^{(a/2) b}.
    """
    t = type(node)

    if t is Text:
        return node

    if t is SlashFrac:
        return SlashFrac(
            _wrap_ambiguous_slashes(node.num),
            _wrap_ambiguous_slashes(node.den),
        )

    if t is Seq:
        children = [_wrap_ambiguous_slashes(c) for c in node.children]
        if len(children) > 1:
            # Wrap SlashFrac when it has real siblings (not just a leading minus)
            has_real_siblings = sum(1 for c in children if not (isinstance(c, Text) and c.text == "-")) > 1
            if has_real_siblings:
                children = [Parens(c) if isinstance(c, SlashFrac) else c for c in children]
        return Seq(children, sep=node.sep)

    if t is Frac:
        return Frac(
            _wrap_ambiguous_slashes(node.num),
            _wrap_ambiguous_slashes(node.den),
            small=node.small,
        )

    if t is Sup:
        return Sup(
            _wrap_ambiguous_slashes(node.base),
            _wrap_ambiguous_slashes(node.exp),
        )

    if t is Parens:
        return Parens(_wrap_ambiguous_slashes(node.child))

    if t is Command:
        return Command(node.cmd, _wrap_ambiguous_slashes(node.child))

    return node
