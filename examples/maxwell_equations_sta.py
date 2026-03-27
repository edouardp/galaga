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

    from ga import Algebra, grade
    import galaga_marimo as gm

    return Algebra, gm, grade, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Maxwell Equations in STA

        In spacetime algebra the four Maxwell equations collapse to one equation:

        $$
        \nabla F = J.
        $$

        Here `F` is the electromagnetic field bivector, `J` is the spacetime current,
        and the geometric product automatically contains both divergence and curl parts.
        """
    )
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, g3


@app.cell
def _(g0, g1, g2, g3, gm):
    nabla = g0 + g1 + g2 + g3
    electric_piece = g1 * g0 + g2 * g0 + g3 * g0
    magnetic_piece = g2 * g3 + g3 * g1 + g1 * g2
    gm.md(t"""
    ## Field Structure

    Spacetime vector derivative:

    {nabla} = {nabla.eval()}

    Electric bivector slots:

    {electric_piece} = {electric_piece.eval()}

    Magnetic bivector slots:

    {magnetic_piece} = {magnetic_piece.eval()}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Split Relative to an Observer

        Relative to $\gamma_0$, write

        $$
        F = E_x \gamma_1 \gamma_0 + E_y \gamma_2 \gamma_0 + E_z \gamma_3 \gamma_0
        + B_x \gamma_2 \gamma_3 + B_y \gamma_3 \gamma_1 + B_z \gamma_1 \gamma_2.
        $$

        The grade-1 and grade-3 parts of $\nabla F$ correspond to the inhomogeneous
        and homogeneous Maxwell equations.
        """
    )
    return


@app.cell
def _(mo):
    ex = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=1.0, label="E_x")
    ey = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=0.4, label="E_y")
    bz = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=1.0, label="B_z")
    mo.vstack([ex, ey, bz])
    return bz, ex, ey


@app.cell(hide_code=True)
def _(bz, ex, ey, g0, g1, g2, grade, gm):
    F = ex.value * (g1 * g0) + ey.value * (g2 * g0) + bz.value * (g1 * g2)
    F2 = F * F
    gm.md(t"""
    ## A Concrete Field

    {F} = {F.eval()}

    {F2} = {F2.eval()}

    Scalar invariant:

    {grade(F2, 0)} = {grade(F2, 0).eval()}

    Pseudoscalar invariant:

    {grade(F2, 4)} = {grade(F2, 4).eval()}
    """)
    return F


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Plane Wave Example

        For a vacuum plane wave with $E \perp B$ and $|E| = |B|$, the invariant square
        vanishes:

        $$
        F^2 = 0.
        $$
        """
    )
    return


@app.cell
def _(mo):
    amplitude = mo.ui.slider(start=0.1, stop=2.0, step=0.05, value=1.0, label="wave amplitude")
    phase = mo.ui.slider(start=0.0, stop=6.28, step=0.05, value=0.0, label="phase")
    mo.vstack([amplitude, phase])
    return amplitude, phase


@app.cell(hide_code=True)
def _(amplitude, g0, g1, g2, g3, gm, grade, np, phase):
    _a = amplitude.value * np.cos(phase.value)
    wave = _a * (g1 * g0) + _a * (g2 * g3)
    wave2 = wave * wave
    gm.md(t"""
    {wave} = {wave.eval()}

    {wave2} = {wave2.eval()}

    {grade(wave2, 0)} = {grade(wave2, 0).eval()}

    {grade(wave2, 4)} = {grade(wave2, 4).eval()}
    """)
    return _a


@app.cell
def _(_a, np, phase, plt):
    _x = np.linspace(0, 2 * np.pi, 300)
    _y = _a * np.cos(_x - phase.value)
    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_x, _y, color="crimson", linewidth=2.5, label="E")
    _ax.plot(_x, _y, color="steelblue", linestyle="--", linewidth=2.0, label="B")
    _ax.set_xlabel("phase coordinate")
    _ax.set_ylabel("field amplitude")
    _ax.set_title("Vacuum plane wave in STA")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
