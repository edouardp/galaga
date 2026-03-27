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

    from ga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Screw Motion in PGA

        A screw motion combines rotation and translation along the rotation axis.
        In full 3D PGA this is the native rigid-motion language. This notebook gives
        a planar-style teaching approximation: rotation plus drift, shown as one
        composite motion and discussed in motor terms.
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
    PGA basis for rigid motions:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}

    {e0} = {e0.eval()}
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=360, step=1, value=120, label="rotation angle")
    pitch = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=1.0, label="translation along axis")
    radius = mo.ui.slider(start=0.5, stop=3.0, step=0.1, value=1.5, label="radius")
    mo.vstack([angle, pitch, radius])
    return angle, pitch, radius


@app.cell(hide_code=True)
def _(angle, e0, e1, e2, exp, gm, np, pitch):
    _theta = np.radians(angle.value)
    _R = exp((-_theta / 2) * (e1 * e2))
    _T = 1 + 0.5 * pitch.value * e0 * e3
    _M = _T * _R

    gm.md(t"""
    ## Composite Motion

    Rotation part:
    {_R} = {_R.eval()}

    Translation part:
    {_T} = {_T.eval()}

    Composite motor-like element:
    {_M} = {_M.eval()}
    """)
    return


@app.cell
def _(angle, np, pitch, plt, radius):
    _t = np.linspace(0, np.radians(angle.value), 300)
    _x = radius.value * np.cos(_t)
    _y = radius.value * np.sin(_t)
    _z = pitch.value * (_t / max(_t[-1], 1e-9))

    _fig = plt.figure(figsize=(7, 5))
    _ax = _fig.add_subplot(111, projection="3d")
    _ax.plot(_x, _y, _z, color="steelblue", linewidth=2.5)
    _ax.scatter([_x[-1]], [_y[-1]], [_z[-1]], color="crimson", s=50)
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")
    _ax.set_zlabel("axis drift")
    _ax.set_title("Screw-like trajectory")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
