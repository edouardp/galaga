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

    from galaga import Algebra, exp, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Relativistic Rocket Equation

    In rapidity language the rocket equation becomes simple:

    $$
    \\Delta \\varphi = u \\ln \\frac{m_0}{m_f}
    $$

    where `u` is the exhaust speed in units of `c`. This notebook uses that form
    to compute reachable speeds and distances for a burn-coast-burn profile.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1


@app.cell
def _(g0, g1, gm):
    gm.md(t"""
    Boost plane: {g0 * g1} = {(g0 * g1).eval()}

    The burn changes rapidity; the coast holds rapidity fixed.
    """)
    return


@app.cell
def _(mo):
    exhaust = mo.ui.slider(start=0.05, stop=0.99, step=0.01, value=0.5, label="exhaust speed u/c")
    mass_ratio = mo.ui.slider(start=1.1, stop=50.0, step=0.1, value=4.0, label="single-burn mass ratio m₀/m_f")
    coast_years = mo.ui.slider(start=0.0, stop=20.0, step=0.1, value=2.0, label="coast time on ship (years)")
    mo.vstack([exhaust, mass_ratio, coast_years])
    return coast_years, exhaust, mass_ratio


@app.cell(hide_code=True)
def _(coast_years, exhaust, exp, g0, g1, gm, mass_ratio, np, sandwich):
    c = 299_792_458.0
    year_s = 365.25 * 24 * 60 * 60
    light_year_m = c * year_s

    u = exhaust.value
    r = mass_ratio.value
    phi = u * np.log(r)
    beta = np.tanh(phi)
    gamma = np.cosh(phi)

    coast_ship = coast_years.value * year_s
    coast_earth = gamma * coast_ship
    coast_distance = beta * c * coast_earth

    gm.md(t"""
    ## Burn Result

    $\\Delta\\varphi = {phi:.5f}$

    {exp((phi / 2) * (g0 * g1))} = {exp((phi / 2) * (g0 * g1)).eval()}

    {sandwich(exp((phi / 2) * (g0 * g1)), g0)} = {sandwich(exp((phi / 2) * (g0 * g1)), g0).eval()}

    Peak speed after one burn: $\\beta = {beta:.6f}$, $\\gamma = {gamma:.6f}$

    Coast phase:
    - ship time: {coast_years.value:.3f} years
    - Earth time: {coast_earth / year_s:.3f} years
    - distance: {coast_distance / light_year_m:.3f} light-years
    """)
    return beta, coast_distance, coast_earth, gamma, light_year_m, year_s


@app.cell
def _(beta, coast_distance, coast_earth, gamma, light_year_m, np, plt, year_s):
    _ratios = np.linspace(1.0, 50.0, 300)
    _exhausts = [0.1, 0.3, 0.5, 0.8]
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    for _u in _exhausts:
        _beta_curve = np.tanh(_u * np.log(_ratios))
        _ax1.plot(_ratios, _beta_curve, linewidth=2, label=fr"$u/c = {_u:.1f}$")
    _ax1.axhline(beta, color="black", alpha=0.2)
    _ax1.set_xlabel(r"mass ratio $m_0 / m_f$")
    _ax1.set_ylabel(r"terminal $\beta$")
    _ax1.set_title("Rocket equation in rapidity form")
    _ax1.grid(True, alpha=0.2)
    _ax1.legend()

    _times = np.linspace(0, coast_earth / year_s if coast_earth > 0 else 1, 200)
    _ax2.plot(_times, beta * _times, color="steelblue", linewidth=2.5)
    _ax2.plot([coast_earth / year_s], [coast_distance / light_year_m], "ko", ms=7)
    _ax2.set_xlabel("Earth coast time (years)")
    _ax2.set_ylabel("distance during coast (light-years)")
    _ax2.set_title(f"Coast at γ = {gamma:.3f}")
    _ax2.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
