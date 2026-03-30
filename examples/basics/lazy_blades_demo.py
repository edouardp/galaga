import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
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
    from galaga import (
        Algebra, gp, op, grade, reverse, dual, norm, unit,
        inverse, exp, log, sandwich, squared,
    )
    from galaga.symbolic import simplify
    import galaga_marimo as gm

    return (
        Algebra,
        dual,
        exp,
        gm,
        grade,
        inverse,
        norm,
        np,
        op,
        reverse,
        simplify,
        squared,
        unit,
    )


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Lazy Basis Blades

    `basis_vectors(lazy=True)` returns blades that are **named + lazy** —
    every operation automatically builds a symbolic expression tree.
    No `sym()` wrapping needed.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Setup
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return alg, e1, e2, e3


@app.cell(hide_code=True)
def _(e1, e2, e3, gm):
    gm.md(t"""
    Blades are named and lazy:

    - {e1} — `_is_lazy = {e1._is_lazy}`
    - {e2} — `_is_lazy = {e2._is_lazy}`
    - {e3} — `_is_lazy = {e3._is_lazy}`
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Products — Everything Stays Symbolic
    """)
    return


@app.cell
def _(e1, e2, e3, gm, op):
    with gm.doc() as _d:
        _d.text("| Expression | Symbolic | Concrete |")
        _d.line("|---|---|---|")
        _exprs = [
            ("e₁e₂", e1 * e2),
            ("e₁∧e₂", e1 ^ e2),
            ("e₁·e₁", e1 | e1),
            ("e₁∧e₂∧e₃", op(op(e1, e2), e3)),
        ]
        for _label, _expr in _exprs:
            _d.line(f"| {_label} | ${_expr.latex()}$ | ${_expr.eval().latex()}$ |")

    _d.render()
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Rotation — Symbolic All the Way

    With lazy blades, the rotor and sandwich product are fully symbolic:
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, np, reverse):
    theta = alg.scalar(np.pi / 4).name("θ", latex=r"\theta")
    B = (e1 ^ e2).name("B")
    R = exp(-B * theta / 2).name("R")

    _v = e1
    _v_rot = R * _v * ~R

    gm.md(t"""
    Rotation plane: {B} = {B.eval()}

    Rotor: {R} = exp(-{B}{theta}/2) = {R.eval()}

    Rotated vector: {_v_rot} = {_v_rot.eval()}

    Reverse: {reverse(R)} = {reverse(R).eval()}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Grade Projection
    """)
    return


@app.cell
def _(e1, e2, e3, gm, grade):
    mv = 3 + 2 * e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)

    gm.md(t"""
    Mixed multivector: {mv}

    - Grade 0: {grade(mv, 0)} = {grade(mv, 0).eval()}
    - Grade 1: {grade(mv, 1)} = {grade(mv, 1).eval()}
    - Grade 2: {grade(mv, 2)} = {grade(mv, 2).eval()}
    - Grade 3: {grade(mv, 3)} = {grade(mv, 3).eval()}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Unary Operations — All Symbolic
    """)
    return


@app.cell
def _(dual, e1, e2, gm, inverse, norm, reverse, squared, unit):
    v = (e1 + e2).name("v")

    with gm.doc() as d:
        d.text("| Operation | Symbolic | Concrete |")
        d.line("|---|---|---|")
        ops = [
            ("reverse", reverse(v)),
            ("unit", unit(v)),
            ("inverse", inverse(v)),
            ("norm", norm(v)),
            ("dual", dual(v)),
            ("squared", squared(v)),
        ]
        for label, result in ops:
            if isinstance(result, float):
                d.line(f"| {label}(v) | — | {result} |")
            else:
                d.line(f"| {label}(v) | ${result.latex()}$ | ${result.eval().latex()}$ |")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Simplification
    """)
    return


@app.cell
def _(e1, e2, gm, simplify):
    a = e1
    b = e2

    with gm.doc() as _d:
        _d.text("| Expression | Simplified |")
        _d.line("|---|---|")
        _cases = [
            ("~~a", ~~a),
            ("a - a", a - a),
            ("a + a", a + a),
            ("a ∧ a", a ^ a),
        ]
        for _label, _expr in _cases:
            _d.line(f"| {_label} | ${simplify(_expr).latex()}$ |")

    _d.render()
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Eager vs Lazy — Side by Side
    """)
    return


@app.cell
def _(Algebra, gm):
    alg2 = Algebra((1, 1, 1))
    ee1, ee2, _ = alg2.basis_vectors()            # eager
    le1, le2, _ = alg2.basis_vectors(lazy=True)    # lazy

    gm.md(t"""
    | Operation | Eager | Lazy |
    |---|---|---|
    | `e1 ^ e2` | {ee1 ^ ee2} | {le1 ^ le2} |
    | `e1 * e2` | {ee1 * ee2} | {le1 * le2} |
    | `3 * e1 + e2` | {3 * ee1 + ee2} | {3 * le1 + le2} |
    | `e1 / 2` | {ee1 / 2} | {le1 / 2} |

    Eager shows concrete results. Lazy shows the expression structure.
    Both have the same `.eval()` values.
    """)
    return


@app.cell
def _(e1, e2):
    e1^e2
    return


@app.cell
def _(e1, e2):
    Bi = (e1^e2).name('Bi')
    return (Bi,)


@app.cell
def _(Bi):
    Bi
    return


@app.cell
def _(Bi):
    Bi.anon()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
