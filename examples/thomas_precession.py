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

    from ga import Algebra, exp, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Thomas Precession

    Two non-collinear boosts do not compose to a pure boost. Their mismatch leaves
    a spatial rotation, the Thomas-Wigner rotation. In spacetime algebra this falls
    straight out of rotor multiplication.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2


@app.cell
def _(mo):
    phi_x = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.7, label="x-rapidity")
    phi_y = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.9, label="y-rapidity")
    mo.vstack([phi_x, phi_y])
    return phi_x, phi_y


@app.cell(hide_code=True)
def _(exp, g0, g1, g2, gm, phi_x, phi_y, sandwich):
    Bx = g0 * g1
    By = g0 * g2
    Rx = exp((phi_x.value / 2) * Bx)
    Ry = exp((phi_y.value / 2) * By)
    Rxy = Ry * Rx
    Ryx = Rx * Ry
    mismatch = Rxy * ~Ryx

    gm.md(t"""
    ## Boost Composition

    {Rx} = {Rx.eval()}

    {Ry} = {Ry.eval()}

    {Rxy} = {Rxy.eval()}

    {Ryx} = {Ryx.eval()}

    Mismatch rotor {mismatch} = {mismatch.eval()}

    This residual even multivector is the Thomas-Wigner rotation.
    """)
    return mismatch


@app.cell
def _(g1, g2, mismatch, np, plt, sandwich):
    _e1 = sandwich(mismatch, g1).eval()
    _e2 = sandwich(mismatch, g2).eval()
    _v1 = _e1.vector_part[:2]
    _v2 = _e2.vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, 0, 1, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, _v1[0], _v1[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, _v2[0], _v2[1], angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-1.2, 1.2)
    _ax.set_ylim(-1.2, 1.2)
    _ax.set_title("Residual spatial rotation in the x-y plane")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
