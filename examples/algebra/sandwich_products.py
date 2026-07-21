import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga import Algebra, exp, inverse, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, inverse, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Sandwich Products

        The sandwich `R x R̃` is the common pattern behind rotations, boosts, and many
        observable updates. This notebook compares a reflection and a rotor sandwich.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), )
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2, e3


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=40, label="rotation angle")
    angle
    return (angle,)


@app.cell
def _(angle, e1, e2, exp, gm, inverse, np, sandwich):
    _theta = np.radians(angle.value)
    v = e1 + 0.5 * e2
    R = exp((-_theta / 2) * (e1 * e2))
    reflected = -e1 * v * inverse(e1)
    gm.md(rt"""
    {v} = {v:value}

    {-e1 * v * inverse(e1)} = {reflected:value}

    {sandwich(R, v)} = {sandwich(R, v):value}
    """)
    return R, v


@app.cell
def _(R, np, plt, v):
    _v = v.vector_part[:2]
    _r = (R * v * ~R).vector_part[:2]
    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, _v[0], _v[1], angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, _r[0], _r[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-2, 2)
    _ax.set_ylim(-2, 2)
    _ax.grid(True, alpha=0.2)
    _ax.set_title("Sandwich update in the plane")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
