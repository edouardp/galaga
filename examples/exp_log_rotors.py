import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from ga import Algebra, exp, log
    import galaga_marimo as gm

    return Algebra, exp, gm, log, mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Exponentials, Logarithms, and Rotors

    A bivector exponential produces a rotor. The logarithm recovers the bivector
    generator when the rotor lies on the supported branch.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return alg, e1, e2


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=55, label="rotation angle")
    angle
    return (angle,)


@app.cell
def _(alg, angle, e1, e2, exp, gm, log, np):
    _theta = alg.scalar(np.radians(angle.value)).name(latex=r"\theta")
    B = (e1 * e2).name("B")
    half_angle = (-_theta * B) / 2
    R = exp(half_angle)
    gm.md(t"""
    {B} = {B.eval()}

    {R} = {R.eval()}

    {log(R)} = {log(R).eval()}

    {half_angle} = {half_angle.eval()}
    """)
    return (R,)


@app.cell
def _(R):
    R.latex()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
