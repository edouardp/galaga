import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    import numpy as np
    import galaga_marimo as gm
    from ga import (
        Algebra, exp, log, dual, undual, inverse, reverse,
        complement, uncomplement,
    )
    return


@app.cell
def _(Algebra, np, gm):
    mo.md("""# LaTeX Render Tree Rewrites""")
    return


@app.cell
def _(Algebra, np, gm):
    _alg = Algebra((1, 1, 1))
    e1, e2, e3 = _alg.basis_vectors(lazy=True)
    return e1, e2, e3, _alg


@app.cell
def _(e1, e2, _alg, np, gm, exp):
    mo.md("""
    ## Rewrite 1: Fractions become inline slash in superscripts

    `\\frac` inside a superscript is too tall. The render tree detects
    `Frac` nodes inside `Sup` nodes and rewrites them as inline `/`.
    """)
    return


@app.cell
def _(e1, e2, _alg, np, gm, exp):
    _theta = _alg.scalar(np.radians(45)).name(latex=r"\theta")
    _B = (e1 * e2).name("B")
    _R = exp((-_theta / 2) * _B)

    with gm.doc() as d:
        d.md(t"""
        A rotor with a fractional angle in the exponent:

        {_R} = {_R.eval()}

        The exponent renders as a compact inline slash, not a tall fraction.
        """)
    d.render()
    return


@app.cell
def _(e1, e2, _alg, np, gm, exp):
    _phi = _alg.scalar(np.pi / 6).name(latex=r"\phi")
    _n = e1.name(latex=r"\hat{n}")
    _R2 = exp((-_phi / 4) * _n)

    with gm.doc() as d:
        d.md(t"""
        Another example — quarter-angle rotor:

        {_R2} = {_R2.eval()}
        """)
    d.render()
    return


@app.cell
def _(gm):
    mo.md("""
    Meanwhile, fractions **outside** superscripts still render as proper
    `\\frac` for readability.
    """)
    return


@app.cell
def _(e1, gm):
    _v = e1.name("v")
    _half_v = _v / 2

    with gm.doc() as d:
        d.md(t"""
        {_half_v} = {_half_v.eval()}
        """)
    d.render()
    return


@app.cell
def _(gm):
    mo.md("""
    ## Rewrite 2: Collapse nested parentheses

    Postfix-on-postfix operations (e.g. taking the inverse of a dual)
    produce nested `\\left(\\left(…\\right)\\right)`. The rewrite
    collapses these to a single pair.
    """)
    return


@app.cell
def _(e1, gm, dual, undual, inverse, complement):
    _v = e1.name("v")

    with gm.doc() as d:
        d.text("| Expression | LaTeX |")
        d.line("|---|---|")
        _exprs = [
            ("undual(dual(v))", undual(dual(_v))),
            ("inverse(dual(v))", inverse(dual(_v))),
            ("dual(inverse(v))", dual(inverse(_v))),
            ("complement(dual(v))", complement(dual(_v))),
            ("inverse(complement(v))", inverse(complement(_v))),
        ]
        for _label, _expr in _exprs:
            d.line(f"| `{_label}` | ${_expr.latex()}$ |")
    d.render()
    return


@app.cell
def _(gm):
    mo.md("""
    ## Rewrite 3: Hoist negation out of fractions

    `\\frac{-a}{b}` is rewritten to `-\\frac{a}{b}`, which is the
    conventional mathematical style. Inside superscripts, the negation
    hoists before the slash: `-a/b` not `(-a)/b`.
    """)
    return


@app.cell
def _(e1, e2, _alg, np, gm, exp):
    _theta = _alg.scalar(np.radians(30)).name(latex=r"\alpha")
    _B = (e1 * e2).name("B")

    with gm.doc() as d:
        d.md(t"""
        Negative angle in exponent:

        {exp((-_theta / 2) * _B)} = {exp((-_theta / 2) * _B).eval()}

        The sign hoists cleanly before the slash.
        """)
    d.render()
    return


@app.cell
def _(gm):
    mo.md("""
    ## Rewrite 4: Simplify trivial denominators

    `\\frac{a}{1}` simplifies to just `a`. This can arise from
    algebraic simplification producing a ScalarDiv with divisor 1.
    """)
    return


@app.cell
def _(e1, gm):
    _v = e1.name("v")
    _trivial = _v / 1

    with gm.doc() as d:
        d.md(t"""
        Division by 1:

        {_trivial} = {_trivial.eval()}

        Renders as just $v$, not $\\frac{{v}}{{1}}$.
        """)
    d.render()
    return


@app.cell
def _(gm):
    mo.md("""
    ## Combined: all rewrites in a physics expression

    A rotation in 3D Euclidean space, showing all rewrites working together.
    """)
    return


@app.cell
def _(e1, e2, e3, _alg, np, gm, exp, log, reverse):
    _theta = _alg.scalar(np.radians(60)).name(latex=r"\theta")
    _B = (e1 * e2).name("B")
    _v = (3 * e1 + 4 * e2 + e3).name("v")
    _R = exp((-_theta / 2) * _B)

    _rotated = _R * _v * reverse(_R)

    with gm.doc() as d:
        d.md(t"""
        Rotor: {_R} = {_R.eval()}

        Vector: {_v} = {_v.eval()}

        Rotation: {_rotated}

        Result: {_rotated.eval()}

        Log of rotor: {log(_R)} = {log(_R).eval()}
        """)
    d.render()
    return


if __name__ == "__main__":
    app.run()
