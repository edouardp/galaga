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

    from galaga import Algebra, unit
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Fresnel Polarisation in GA

        At an interface, the parallel and perpendicular polarisation components do not
        generally reflect with the same amplitude. In a 2D GA teaching model, this is
        a natural projector/decomposition example.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), repr_unicode=True)
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(e1, e2, gm):
    gm.md(t"""
    Polarisation basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}
    """)
    return


@app.cell
def _(mo):
    incidence = mo.ui.slider(start=0, stop=89, step=1, value=45, label="incidence angle")
    n1 = mo.ui.slider(start=1.0, stop=2.0, step=0.01, value=1.0, label="n₁")
    n2 = mo.ui.slider(start=1.0, stop=2.5, step=0.01, value=1.5, label="n₂")
    pol = mo.ui.slider(start=0, stop=90, step=1, value=30, label="input polarisation angle")
    mo.vstack([incidence, n1, n2, pol])
    return incidence, n1, n2, pol


@app.cell(hide_code=True)
def _(e1, e2, gm, incidence, n1, n2, np, pol, unit):
    _theta_i = np.radians(incidence.value)
    _sin_t = np.clip(n1.value * np.sin(_theta_i) / n2.value, -1.0, 1.0)
    _theta_t = np.arcsin(_sin_t)

    rs = (n1.value * np.cos(_theta_i) - n2.value * np.cos(_theta_t)) / (n1.value * np.cos(_theta_i) + n2.value * np.cos(_theta_t))
    rp = (n2.value * np.cos(_theta_i) - n1.value * np.cos(_theta_t)) / (n2.value * np.cos(_theta_i) + n1.value * np.cos(_theta_t))

    _alpha = np.radians(pol.value)
    _E = unit(np.cos(_alpha) * e1 + np.sin(_alpha) * e2)
    _Er = rs * (_E.eval().vector_part[1] * e2.eval()) + rp * (_E.eval().vector_part[0] * e1.eval())

    gm.md(t"""
    ## Fresnel Coefficients

    Input polarisation:
    {_E} = {_E.eval()}

    $r_s = {rs:.6f}$ and $r_p = {rp:.6f}$

    Reflected field:
    {_Er} = {_Er.eval()}
    """)
    return rp, rs


@app.cell
def _(incidence, np, plt, rp, rs):
    _angles = np.radians(np.linspace(0, 89, 300))
    _n1 = 1.0
    _n2 = 1.5
    _theta_t = np.arcsin(np.clip(_n1 * np.sin(_angles) / _n2, -1.0, 1.0))
    _rs = (_n1 * np.cos(_angles) - _n2 * np.cos(_theta_t)) / (_n1 * np.cos(_angles) + _n2 * np.cos(_theta_t))
    _rp = (_n2 * np.cos(_angles) - _n1 * np.cos(_theta_t)) / (_n2 * np.cos(_angles) + _n1 * np.cos(_theta_t))

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(np.degrees(_angles), _rs, color="steelblue", linewidth=2.5, label=r"$r_s$")
    _ax.plot(np.degrees(_angles), _rp, color="crimson", linewidth=2.5, label=r"$r_p$")
    _ax.plot([incidence.value], [rs], "o", color="steelblue")
    _ax.plot([incidence.value], [rp], "o", color="crimson")
    _ax.set_xlabel("incidence angle (degrees)")
    _ax.set_ylabel("reflection coefficient")
    _ax.set_title("Fresnel reflection coefficients")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
