"""galaga_marimo — Marimo notebook helpers for geometric algebra.

Provides t-string powered markdown rendering that automatically
converts GA objects to LaTeX in marimo notebooks.

Requires Python 3.14+ for t-string support.

Usage::

    import galaga_marimo as gm

    gm.md(t"Rotor: {R}")
    gm.md(t"Result: {expr:block}")

    # For loops and programmatic content:
    with gm.doc() as d:
        d.md(t"# Results")
        for name, e in exprs:
            d.md(t"**{name}:** {e} = {e.eval()}")
"""

from galaga_marimo.api import md, inline, block, latex, block_latex, text, doc, Doc
from galaga_marimo.renderer import render_template

__all__ = [
    "md", "inline", "block", "latex", "block_latex", "text",
    "doc", "Doc", "render_template",
]
