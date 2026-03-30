import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
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
    mo.md(r"""
    # Bell States and Correlations

    Full multipartite geometric algebra needs extra structure beyond the single-
    particle rotor story, so this notebook treats Bell states pedagogically through
    their correlation functions and compares that with the singlet geometry.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm):
    gm.md(t"""
    Measurement-axis basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}

    In the singlet, the correlation depends only on the geometric relationship
    between the two measurement axes.
    """)
    return


@app.cell
def _(mo):
    delta = mo.ui.slider(start=0, stop=180, step=1, value=45, label="angle between measurement axes")
    delta
    return (delta,)


@app.cell(hide_code=True)
def _(delta, e1, e2, exp, gm, np):
    _d = np.radians(delta.value)
    a = e1
    R = exp((-_d / 2) * (e1 * e2)).name(latex=f"\\R_{{{delta.value}°}}")
    b = R * e1 * ~R
    singlet_corr = -((a * b).eval()).scalar_part
    same_prob = 0.5 * (1 - singlet_corr)
    diff_prob = 0.5 * (1 + singlet_corr)

    gm.md(t"""
    ## Singlet Correlation

    For the Bell singlet state

    $$
    |\\Psi^-\\rangle =
    \\frac{{1}}{{\\sqrt{{2}}}} (|01\\rangle - |10\\rangle),
    $$

    the two-spin correlation is

    $$
    E(a,b) = - a \\cdot b.
    $$

    Choose

    {a} = {a.eval()}

    and rotate it in the $e_1 e_2$ plane to get

    {b} = {b.eval()}

    Then the GA scalar product gives

    $$
    -\\langle ab \\rangle_0 = {singlet_corr:.6f}.
    $$

    Same-result probability: {same_prob:.6f}

    Opposite-result probability: {diff_prob:.6f}
    """)
    return b, singlet_corr


@app.cell
def _(b, delta, np, plt, singlet_corr):
    _ds = np.linspace(0, np.pi, 300)
    _curve = -np.cos(_ds)
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4))
    _ax1.plot(np.degrees(_ds), _curve, color="steelblue", linewidth=2.5)
    _ax1.plot([delta.value], [singlet_corr], "ko", ms=7)
    _ax1.set_xlabel("axis angle difference (degrees)")
    _ax1.set_ylabel("E(a,b)")
    _ax1.set_title("Bell singlet correlation")
    _ax1.grid(True, alpha=0.2)

    _ax2.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.015)
    _bv = b.eval().vector_part[:2]
    _ax2.quiver(0, 0, _bv[0], _bv[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.015)
    _ax2.set_aspect("equal")
    _ax2.set_xlim(-1.2, 1.2)
    _ax2.set_ylim(-1.2, 1.2)
    _ax2.set_title("Measurement-axis geometry")
    _ax2.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
