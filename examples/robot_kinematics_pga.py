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

    from galaga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Robot Kinematics in PGA

    PGA packages rotations and translations into motors, which makes planar robot
    kinematics a natural teaching example. This notebook uses a simple two-link arm.
    """)
    return


@app.cell
def _(Algebra):
    pga = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3, e0 = pga.basis_vectors(lazy=True)
    return e0, e1, e2, e3


@app.cell
def _(mo):
    theta1 = mo.ui.slider(start=-180, stop=180, step=1, value=30, label="joint 1 angle")
    theta2 = mo.ui.slider(start=-180, stop=180, step=1, value=45, label="joint 2 angle")
    l1 = mo.ui.slider(start=0.5, stop=3.0, step=0.1, value=1.8, label="link 1 length")
    l2 = mo.ui.slider(start=0.5, stop=3.0, step=0.1, value=1.2, label="link 2 length")
    mo.vstack([theta1, theta2, l1, l2])
    return l1, l2, theta1, theta2


@app.cell(hide_code=True)
def _(e0, e1, e2, exp, gm, l1, l2, np, theta1, theta2):
    _t1 = np.radians(theta1.value)
    _t2 = np.radians(theta2.value)
    _R1 = exp((-_t1 / 2) * (e1 * e2))
    _R2 = exp((-( _t1 + _t2) / 2) * (e1 * e2))
    _T1 = 1 + 0.5 * l1.value * e0 * (_R1 * e1 * ~_R1).eval()
    _T2 = 1 + 0.5 * l2.value * e0 * (_R2 * e1 * ~_R2).eval()
    _M = _T2 * _T1

    gm.md(t"""
    ## Motors and Links

    {_R1} = {_R1.eval()}

    {_R2} = {_R2.eval()}

    {_T1} = {_T1.eval()}

    {_T2} = {_T2.eval()}

    Composite motor {_M} = {_M.eval()}
    """)
    return


@app.cell
def _(l1, l2, np, plt, theta1, theta2):
    _t1 = np.radians(theta1.value)
    _t2 = np.radians(theta2.value)
    _joint = np.array([l1.value * np.cos(_t1), l1.value * np.sin(_t1)])
    _end = _joint + np.array([l2.value * np.cos(_t1 + _t2), l2.value * np.sin(_t1 + _t2)])

    _fig, _ax = plt.subplots(figsize=(6.5, 6.5))
    _ax.plot([0, _joint[0]], [0, _joint[1]], color="steelblue", linewidth=3)
    _ax.plot([_joint[0], _end[0]], [_joint[1], _end[1]], color="crimson", linewidth=3)
    _ax.plot([0, _joint[0], _end[0]], [0, _joint[1], _end[1]], "ko", ms=6)
    _r = l1.value + l2.value + 0.5
    _ax.set_xlim(-_r, _r)
    _ax.set_ylim(-_r, _r)
    _ax.set_aspect("equal")
    _ax.set_title("Planar 2-link arm")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
