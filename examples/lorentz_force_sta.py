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

    from ga import Algebra
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Lorentz Force in STA

        In spacetime algebra the electromagnetic field is one bivector $F$, and the
        Lorentz force law is naturally written in terms of how that bivector acts on
        the particle velocity. This notebook keeps the emphasis on the geometry of the
        resulting motion.
        """
    )
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, g3


@app.cell
def _(mo):
    bx = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=0.0, label="B_x")
    bz = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=1.0, label="B_z")
    speed = mo.ui.slider(start=0.0, stop=0.95, step=0.01, value=0.6, label="initial speed / c")
    mo.vstack([bx, bz, speed])
    return bx, bz, speed


@app.cell(hide_code=True)
def _(bx, bz, g1, g2, g3, gm, speed):
    F = bx.value * (g2 * g3) + bz.value * (g1 * g2)
    v = speed.value * g1
    gm.md(t"""
    ## Field and Initial Velocity

    {F} = {F.eval()}

    {v} = {v.eval()}

    In a purely magnetic field the speed is constant while the spatial velocity
    direction rotates.
    """)
    return


@app.cell
def _(bx, bz, np, plt, speed):
    _w = np.sqrt(bx.value**2 + bz.value**2)
    _t = np.linspace(0, 12, 400)
    if _w < 1e-12:
        _x = speed.value * _t
        _y = np.zeros_like(_t)
    else:
        _x = speed.value * np.sin(_w * _t) / _w
        _y = speed.value * (1 - np.cos(_w * _t)) / _w
    _fig, _ax = plt.subplots(figsize=(7, 5))
    _ax.plot(_x, _y, color="steelblue", linewidth=2.5)
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")
    _ax.set_aspect("equal")
    _ax.set_title("Qualitative magnetic-orbit projection")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
