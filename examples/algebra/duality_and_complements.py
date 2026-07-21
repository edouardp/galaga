import marimo

__generated_with = "0.23.11"
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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga import Algebra, DisplayPolicy, complement, dual, undual, uncomplement, left_complement, left_hodge_dual, left_contraction, left_interior_product, left_weight_dual
    import galaga_marimo as gm

    return (
        Algebra,
        DisplayPolicy,
        complement,
        dual,
        gm,
        left_complement,
        left_contraction,
        left_hodge_dual,
        left_interior_product,
        left_weight_dual,
        mo,
        np,
        plt,
        uncomplement,
        undual,
    )


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
def _(Algebra, DisplayPolicy):
    cl3 = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
    pga = Algebra((1, 1, 1, 0), display=DisplayPolicy(content="full"))
    e1, e2, e3 = cl3.basis_vectors(expr=True)
    p1, p2, p3, p0 = pga.basis_vectors(expr=True)
    return e1, e2, e3, p0, p1, p2


@app.cell
def _(complement, dual, e1, e2, e3, gm, uncomplement, undual):
    bivector = (e1 ^ e2).named("B_1")
    bivector2 = (e2 ^ e3).named("B_2")
    dual_b = dual(bivector)
    comp_b = complement(bivector)
    undual_b = undual(dual_b)
    uncomp_b = uncomplement(comp_b)

    gm.md(rt"""
    {bivector}

    {dual(bivector)}

    {complement(bivector)}

    {undual(dual_b)}

    {uncomplement(comp_b)}
    """)
    return bivector, bivector2


@app.cell
def _(
    bivector,
    bivector2,
    gm,
    left_complement,
    left_contraction,
    left_hodge_dual,
    left_interior_product,
    left_weight_dual,
):
    gm.md(rt"""
    {bivector}

    {left_complement(bivector)}

    {left_hodge_dual(bivector)}

    {left_contraction(bivector, bivector2)}

    {left_interior_product(bivector, bivector2)}

    {left_weight_dual(bivector)}
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
    plane = (p1 + 0.7 * p2 - 1.2 * p0).named(r"\pi", latex=r"\pi")
    ideal_line = complement(plane)

    gm.md(rt"""
    {plane}

    {ideal_line}

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
    a = e1.named("a")
    b = (np.cos(_theta) * e1 + np.sin(_theta) * e2).named("b")
    area = (a ^ b)
    dual_area = dual(area)
    comp_area = complement(area)

    gm.md(rt"""
    {area}

    {dual_area}

    {comp_area}
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
