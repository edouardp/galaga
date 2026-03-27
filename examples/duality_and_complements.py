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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, complement, dual, undual, uncomplement
    import galaga_marimo as gm

    return Algebra, complement, dual, gm, mo, np, plt, uncomplement, undual


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Duality and Complements

    `dual(...)` and `complement(...)` look similar in Euclidean examples, but they
    answer different questions.

    - `dual` uses the metric and the pseudoscalar inverse
    - `complement` is combinatorial and still works cleanly in degenerate algebras

    This notebook compares them side by side in `Cl(3,0)` and in PGA.
    """)
    return


@app.cell
def _(Algebra):
    cl3 = Algebra((1, 1, 1), repr_unicode=True)
    pga = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3 = cl3.basis_vectors(lazy=True)
    p1, p2, p3, p0 = pga.basis_vectors(lazy=True)
    return e1, e2, p0, p1, p2


@app.cell
def _(complement, dual, e1, e2, gm, uncomplement, undual):
    bivector = (e1 ^ e2).name("B")
    dual_b = dual(bivector).name(latex=r"B^\star")
    comp_b = complement(bivector).name(latex=r"B^\complement")
    undual_b = undual(dual_b).name(latex=r"(B^\star)^{\star^{-1}}")
    uncomp_b = uncomplement(comp_b).name(latex=r"(B^\complement)^{\complement^{-1}}")

    gm.md(t"""
    ## Euclidean 3D

    {bivector} = {bivector.eval()}

    {dual_b} = {dual_b.eval()}

    {comp_b} = {comp_b.eval()}

    {undual_b} = {undual_b.eval()}

    {uncomp_b} = {uncomp_b.eval()}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Degenerate Metric: PGA

    In PGA the pseudoscalar is not invertible, so `dual(...)` is not the right
    tool. `complement(...)` remains available because it is metric-independent.
    """)
    return


@app.cell
def _(complement, gm, p0, p1, p2):
    plane = (p1 + 0.7 * p2 - 1.2 * p0).name(latex=r"\pi")
    ideal_line = complement(plane).name(latex=r"\pi^\complement")

    gm.md(t"""
    {plane} = {plane.eval()}

    {ideal_line} = {ideal_line.eval()}

    In this degenerate algebra the complement still converts between primal and
    complementary basis structure without needing a pseudoscalar inverse.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Visual Comparison

    In Euclidean 3D the dual of an oriented area element is an axial vector.
    In PGA, complements let us move between incidence representations even when
    metric duality becomes singular.
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=35, label="plane angle")
    angle
    return (angle,)


@app.cell
def _(angle, complement, dual, e1, e2, gm, np):
    _theta = np.radians(angle.value)
    a = e1.name("a")
    b = (np.cos(_theta) * e1 + np.sin(_theta) * e2).name("b")
    area = (a ^ b).name(latex=r"a \wedge b")
    dual_area = dual(area).name(latex=r"(a \wedge b)^\star")
    comp_area = complement(area).name(latex=r"(a \wedge b)^\complement")

    gm.md(t"""
    {area} = {area.eval()}

    {dual_area} = {dual_area.eval()}

    {comp_area} = {comp_area.eval()}
    """)
    return


@app.cell
def _(angle, np, plt):
    _theta = np.radians(angle.value)
    _a = np.array([1.0, 0.0])
    _b = np.array([np.cos(_theta), np.sin(_theta)])
    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, _a[0], _a[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, _b[0], _b[1], angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.fill([0, _a[0], _a[0] + _b[0], _b[0]], [0, _a[1], _a[1] + _b[1], _b[1]], color="goldenrod", alpha=0.25)
    _ax.set_aspect("equal")
    _ax.set_xlim(-1.5, 2.0)
    _ax.set_ylim(-1.2, 2.0)
    _ax.set_title("A bivector and its Euclidean dual/complement")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
