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

    from ga import Algebra, grade, scalar, sandwich, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, grade, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Electromagnetism as One Bivector

    In spacetime algebra the electric and magnetic fields are not separate
    objects. They are the timelike and spacelike parts of a single bivector
    field `F`.

    This notebook uses lazy basis blades so the reader can see the field
    assembled symbolically before evaluating it.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    I = sta.I.name("I")
    return g0, g1, g2


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Build the Faraday Bivector

    For an observer with timelike basis vector `γ₀`:

    - electric pieces live in the planes `γᵢγ₀`
    - magnetic pieces live in the spatial bivectors `γⱼγₖ`

    The combined field is

    $$
    F = E_x \gamma_1\gamma_0 + E_y \gamma_2\gamma_0 + E_z \gamma_3\gamma_0 + B_x \gamma_2\gamma_3 + B_y \gamma_3\gamma_1 + B_z \gamma_1\gamma_2.
    $$
    """)
    return


@app.cell
def _(mo):
    ex = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=1.2, label="Eₓ")
    ey = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=0.0, label="E_y")
    bz = mo.ui.slider(start=-2.0, stop=2.0, step=0.1, value=0.8, label="B_z")
    mo.vstack([ex, ey, bz])
    return bz, ex, ey


@app.cell
def _(bz, ex, ey, g0, g1, g2, gm):
    Ex = ex.value
    Ey = ey.value
    Bz = bz.value
    E_field = (Ex * (g1 * g0) + Ey * (g2 * g0)).name("E", latex=r"E")
    B_field = (Bz * (g1 * g2)).name("B", latex=r"B")
    F = (E_field + B_field).name("F", latex=r"F")

    gm.md(t"""
    {E_field} = {E_field.eval()}

    {B_field} = {B_field.eval()}

    {F} = {F.eval()}
    """)
    return (F,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Lorentz Invariants

    The square of the field bivector contains the standard invariant content.
    The scalar part distinguishes electric-dominated from magnetic-dominated
    configurations, while the pseudoscalar part measures the `E·B` coupling.
    """)
    return


@app.cell
def _(F, gm, grade):
    F2 = F**2
    scalar_part = grade(F2, 0)
    pseudoscalar_part = grade(F2, 4)

    gm.md(t"""
    {F2} = {F2.eval()}

    {scalar_part} = {scalar_part.eval()}

    {pseudoscalar_part} = {pseudoscalar_part.eval()}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Boost the Field

    A boost mixes electric and magnetic parts automatically because `F` is one
    bivector. This is the cleanest pedagogical payoff of the STA formulation.
    """)
    return


@app.cell
def _(mo):
    boost = mo.ui.slider(start=-2.0, stop=2.0, step=0.05, value=0.6, label="boost rapidity along x")
    boost
    return (boost,)


@app.cell
def _(F, boost, exp, g0, g1, gm, grade, sandwich):
    phi = boost.value
    Lambda = exp((phi / 2) * (g0 * g1)).name("Λ", latex=r"\Lambda")
    F_prime = sandwich(Lambda, F).name(latex=r"F'")
    electric_prime = grade(F_prime, 2)
    invariant_prime = grade(F_prime**2, 0)

    gm.md(t"""
    {Lambda} = {Lambda.eval()}

    {F_prime} = {F_prime.eval()}

    {electric_prime} = {electric_prime.eval()}

    {invariant_prime} = {invariant_prime.eval()}
    """)
    return (F_prime,)


@app.cell
def _(F, F_prime, np, plt):
    _source = F.eval()
    _boosted = F_prime.eval()
    _labels = [r"$\gamma_1\gamma_0$", r"$\gamma_2\gamma_0$", r"$\gamma_3\gamma_0$", r"$\gamma_2\gamma_3$", r"$\gamma_3\gamma_1$", r"$\gamma_1\gamma_2$"]
    _indices = [3, 5, 9, 12, 10, 6]
    _before = np.array([_source.data[i] for i in _indices])
    _after = np.array([_boosted.data[i] for i in _indices])
    _x = np.arange(len(_labels))

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.bar(_x - 0.18, _before, width=0.36, label="original", color="steelblue")
    _ax.bar(_x + 0.18, _after, width=0.36, label="boosted", color="crimson")
    _ax.axhline(0, color="black", linewidth=0.8)
    _ax.set_xticks(_x)
    _ax.set_xticklabels(_labels)
    _ax.set_ylabel("coefficient")
    _ax.set_title("How a boost redistributes field bivector components")
    _ax.legend()
    _ax.grid(True, axis="y", alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
