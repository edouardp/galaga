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

    return (mo,)


@app.cell
def _():
    import numpy as np
    import galaga_marimo as gm
    from ga import (
        Algebra, exp, log, dual, undual, inverse, reverse,
        complement, uncomplement,
    )
    from ga.notation import Notation, NotationRule

    return (
        Algebra,
        NotationRule,
        complement,
        dual,
        exp,
        gm,
        inverse,
        log,
        np,
        reverse,
        undual,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # LaTeX Render Tree Rewrites
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(Algebra, NotationRule):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)

    # Set the reverse rendering to use postfix dagger
    alg.notation.set("Reverse", "latex", NotationRule(kind="postfix", symbol=r"\dagger"))
    return alg, e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rewrite 1: Fractions become inline slash in superscripts

    `\frac` inside a superscript is too tall. The render tree detects
    `Frac` nodes inside `Sup` nodes and rewrites them as inline `/`.
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, np):
    _theta = alg.scalar(np.radians(45)).name(latex=r"\theta")
    _B = (e1 * e2).name("B")
    _R = exp((-_theta / 2) * _B)

    with gm.doc() as _d:
        _d.md(t"""
        A rotor with a fractional angle in the exponent:

        {_R} = {_R.eval()}

        The exponent renders as a compact inline slash, not a tall fraction.
        """)
    _d.render()
    return


@app.cell
def _(alg, e1, exp, gm, np):
    _phi = alg.scalar(np.pi / 6).name(latex=r"\phi")
    _n = e1.name(latex=r"\hat{n}")
    _R2 = exp((-_phi / 4) * _n)

    with gm.doc() as _d:
        _d.md(t"""
        Another example -- quarter-angle rotor:

        {_R2} = {_R2.eval()}
        """)
    _d.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Meanwhile, fractions **outside** superscripts still render as proper
    `\frac` for readability.
    """)
    return


@app.cell
def _(e1, gm):
    _v = e1.name("v")
    _half_v = _v / 2

    with gm.doc() as _d:
        _d.md(t"""
        {_half_v} = {_half_v.eval()}
        """)
    _d.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rewrite 2: Collapse nested parentheses

    Postfix-on-postfix operations (e.g. taking the inverse of a dual)
    produce nested `\left(\left(\ldots\right)\right)`. The rewrite
    collapses these to a single pair.
    """)
    return


@app.cell
def _(complement, dual, e1, gm, inverse, undual):
    _v = e1.name("v")

    with gm.doc() as _d:
        _d.text("| Expression | LaTeX |")
        _d.line("|---|---|")
        _exprs = [
            ("undual(dual(v))", undual(dual(_v))),
            ("inverse(dual(v))", inverse(dual(_v))),
            ("dual(inverse(v))", dual(inverse(_v))),
            ("complement(dual(v))", complement(dual(_v))),
            ("inverse(complement(v))", inverse(complement(_v))),
        ]
        for _label, _expr in _exprs:
            _d.line(f"| `{_label}` | ${_expr.latex()}$ |")
    _d.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rewrite 3: Hoist negation out of fractions

    `\frac{-a}{b}` is rewritten to `-\frac{a}{b}`, which is the
    conventional mathematical style. Inside superscripts, the negation
    hoists before the slash: `-a/b` not `(-a)/b`.
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, np):
    _alpha = alg.scalar(np.radians(30)).name(latex=r"\alpha")
    _B = (e1 * e2).name("B")

    with gm.doc() as _d:
        _d.md(t"""
        Negative angle in exponent:

        {exp((-_alpha / 2) * _B)} = {exp((-_alpha / 2) * _B).eval()}

        The sign hoists cleanly before the slash.
        """)
    _d.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rewrite 4: Simplify trivial denominators

    `\frac{a}{1}` simplifies to just `a`. This can arise from
    algebraic simplification producing a ScalarDiv with divisor 1.
    """)
    return


@app.cell
def _(e1, gm):
    _v = e1.name("v")
    _trivial = _v / 1

    with gm.doc() as _d:
        _d.md(t"""
        Division by 1:

        {_trivial} = {_trivial.eval()}

        Renders as just v, not a fraction with denominator 1.
        """)
    _d.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Combined: all rewrites in a physics expression

    A rotation in 3D Euclidean space, showing all rewrites working together.
    """)
    return


@app.cell
def _(alg, e1, e2, e3, exp, gm, log, np):
    _theta = alg.scalar(np.radians(60)).name(latex=r"\theta")

    _B = (e1 * e2).name("B")
    _v = (3 * e1 + 4 * e2 + e3).name("v")
    _R = exp((-_theta / 2) * _B)

    _rotated = _R * _v * ~_R

    with gm.doc() as _d:
        _d.md(t"""
        Rotor: {_R} = {_R.eval()}

        Vector: {_v} = {_v.eval()}

        Rotation: {_rotated}

        Result: {_rotated.eval()}

        Log of rotor: {log(_R)} = {log(_R).eval()}
        """)
    _d.render()
    return


@app.cell
def _(alg, e1, e2, e3, exp, np, reverse):
    _theta = alg.scalar(np.radians(60)).name(latex=r"\theta")

    _B = (e1 * e2).name("B")
    _v = (3 * e1 + 4 * e2 + e3).name("v")
    _R = exp((-_theta / 2) * _B)

    _rotated = _R * _v * reverse(_R)

    _rotated.latex()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
