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
    mo.md(
        """
        # Exponentials, Logarithms, and Rotors

        A bivector exponential produces a rotor. The logarithm recovers the bivector
        generator when the rotor lies on the supported branch.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=55, label="rotation angle")
    angle
    return (angle,)


@app.cell
def _(angle, e1, e2, exp, gm, log, np):
    _theta = np.radians(angle.value)
    B = e1 * e2
    R = exp((-_theta / 2) * B)
    gm.md(t"""
    {B} = {B.eval()}

    {R} = {R.eval()}

    {log(R)} = {log(R).eval()}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
