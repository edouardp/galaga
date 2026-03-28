import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
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

    from galaga import Algebra
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Camera Geometry in PGA

        This notebook keeps the geometry intentionally simple: a pinhole camera in 2D,
        an image plane, and a point in the world. The projective lesson is that image
        formation is about intersections of rays with a plane.
        """
    )
    return


@app.cell
def _(Algebra):
    pga = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3, e0 = pga.basis_vectors(lazy=True)
    return e0, e1, e2, e3


@app.cell
def _(e0, e1, e2, e3, gm):
    gm.md(t"""
    PGA basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}

    {e0} = {e0.eval()}

    The degenerate direction {e0} = {e0.eval()} is what lets projective geometry
    distinguish location from pure direction.
    """)
    return


@app.cell
def _(mo):
    x = mo.ui.slider(start=1.0, stop=10.0, step=0.1, value=6.0, label="object depth")
    y = mo.ui.slider(start=-4.0, stop=4.0, step=0.1, value=1.5, label="object height")
    focal = mo.ui.slider(start=0.5, stop=3.0, step=0.1, value=1.0, label="focal length")
    mo.vstack([x, y, focal])
    return focal, x, y


@app.cell(hide_code=True)
def _(focal, gm, x, y):
    ix = -focal.value
    iy = -focal.value * y.value / x.value
    gm.md(t"""
    ## Perspective Projection

    World point:
    $({x.value:.3f}, {y.value:.3f})$

    Pinhole at the origin, image plane at $x = -f$ with $f = {focal.value:.3f}$.

    Projected image point:
    $({ix:.3f}, {iy:.3f})$

    This is the projective statement that the camera ray through the world point
    intersects the image plane at a scaled copy of the direction.
    """)
    return ix, iy


@app.cell
def _(focal, ix, iy, np, plt, x, y):
    _fig, _ax = plt.subplots(figsize=(8, 5))
    _ax.axvline(0, color="black", linewidth=1.5, alpha=0.5)
    _ax.axvline(-focal.value, color="crimson", linewidth=2, alpha=0.5)
    _ax.plot([0, x.value], [0, y.value], color="steelblue", linewidth=2.5)
    _ax.plot([0, ix], [0, iy], color="darkorange", linewidth=2.5)
    _ax.plot([x.value], [y.value], "ko", ms=7)
    _ax.plot([ix], [iy], "ko", ms=7)
    _ax.text(x.value + 0.1, y.value, "world point")
    _ax.text(ix - 0.7, iy, "image point")
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")
    _ax.set_title("Pinhole camera geometry")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
