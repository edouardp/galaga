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

    from ga import Algebra
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Rotors from Reflections

    A Euclidean rotation can be built as two reflections. In geometric algebra this
    is not a trick or a special case: it is the basic construction behind rotors.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), repr_unicode=True)
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(mo):
    alpha = mo.ui.slider(start=0, stop=180, step=1, value=20, label="first mirror angle")
    beta = mo.ui.slider(start=0, stop=180, step=1, value=65, label="second mirror angle")
    vector_angle = mo.ui.slider(start=0, stop=180, step=1, value=15, label="input vector angle")
    mo.vstack([alpha, beta, vector_angle])
    return alpha, beta, vector_angle


@app.cell(hide_code=True)
def _(alpha, beta, e1, e2, gm, np, vector_angle):
    _a = np.radians(alpha.value)
    _b = np.radians(beta.value)
    _v = np.radians(vector_angle.value)
    _n1 = (np.cos(_a) * e1 + np.sin(_a) * e2)
    _n2 = (np.cos(_b) * e1 + np.sin(_b) * e2)
    _x = np.cos(_v) * e1 + np.sin(_v) * e2
    _x1 = -_n1 * _x * _n1
    _x2 = -_n2 * _x1 * _n2
    _R = _n2 * _n1

    gm.md(t"""
    ## Reflection Composition

    {_n1} = {_n1.eval()}

    {_n2} = {_n2.eval()}

    After first reflection: {_x1} = {_x1.eval()}

    After second reflection: {_x2} = {_x2.eval()}

    Rotor from the mirror pair: {_R} = {_R.eval()}
    """)
    return


@app.cell
def _(alpha, beta, np, plt, vector_angle):
    _a = np.radians(alpha.value)
    _b = np.radians(beta.value)
    _v = np.radians(vector_angle.value)
    _x = np.array([np.cos(_v), np.sin(_v)])
    _rot = 2 * (beta.value - alpha.value)
    _y = np.array([np.cos(np.radians(vector_angle.value + _rot)), np.sin(np.radians(vector_angle.value + _rot))])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _m1 = np.array([np.cos(_a), np.sin(_a)])
    _m2 = np.array([np.cos(_b), np.sin(_b)])
    _ax.plot([-2 * _m1[0], 2 * _m1[0]], [-2 * _m1[1], 2 * _m1[1]], color="steelblue", alpha=0.5)
    _ax.plot([-2 * _m2[0], 2 * _m2[0]], [-2 * _m2[1], 2 * _m2[1]], color="darkorange", alpha=0.5)
    _ax.quiver(0, 0, _x[0], _x[1], angles="xy", scale_units="xy", scale=1, color="black", width=0.012)
    _ax.quiver(0, 0, _y[0], _y[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-2, 2)
    _ax.set_ylim(-2, 2)
    _ax.set_title("Two reflections compose to a rotation")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
