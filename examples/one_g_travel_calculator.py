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

    from ga import Algebra, exp, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 1g Relativistic Travel Calculator

    This notebook models a one-way trip with three phases:

    1. accelerate at constant proper acceleration `1g`
    2. coast at constant velocity
    3. decelerate at `1g` to arrive at rest

    It reports the elapsed time on the ship, the elapsed time for an observer
    back on Earth, and the Earth-frame distance covered. The acceleration model
    is fully relativistic, so rapidity and hyperbolic functions appear naturally.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1


@app.cell
def _(g0, g1, gm):
    _boost_plane = (g0 * g1).name("B", latex=r"\gamma_0 \gamma_1")
    gm.md(t"""
    ## STA Setup

    Boost generator {_boost_plane} = {_boost_plane.eval()}

    Constant proper acceleration builds rapidity linearly:

    $$
    \\varphi = \\frac{{a \\tau}}{{c}}.
    $$

    The corresponding boost rotor is $\\Lambda = e^{{(\\varphi/2)B}}$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Controls

    The sliders are measured in the traveler's proper time.

    - `τ_acc`: ship-time spent accelerating
    - `τ_coast`: ship-time spent coasting between the acceleration legs
    """)
    return


@app.cell
def _(mo):
    tau_acc_years = mo.ui.slider(start=0.0, stop=30.0, step=0.1, value=1.0, label="ship acceleration time τ_acc (years)")
    tau_coast_years = mo.ui.slider(start=0.0, stop=40.0, step=0.1, value=0.0, label="ship coasting time τ_coast (years)")
    mo.vstack([tau_acc_years, tau_coast_years])
    return tau_acc_years, tau_coast_years


@app.cell(hide_code=True)
def _(exp, g0, g1, gm, np, sandwich, tau_acc_years, tau_coast_years):
    c = 299_792_458.0
    g = 9.80665
    year_s = 365.25 * 24 * 60 * 60
    light_year_m = c * year_s

    tau_acc = tau_acc_years.value * year_s
    tau_coast = tau_coast_years.value * year_s

    phi = g * tau_acc / c
    beta = np.tanh(phi)
    gamma = np.cosh(phi)

    t_acc = (c / g) * np.sinh(phi)
    x_acc = (c**2 / g) * (np.cosh(phi) - 1.0)

    t_coast = gamma * tau_coast
    x_coast = beta * c * t_coast

    total_ship_time = 2.0 * tau_acc + tau_coast
    total_earth_time = 2.0 * t_acc + t_coast
    total_distance = 2.0 * x_acc + x_coast

    boost_plane = (g0 * g1).name("B", latex=r"\gamma_0 \gamma_1")
    rapidity = (phi + 0 * g0).name("φ", latex=r"\varphi")
    Lambda = exp((phi / 2) * boost_plane).name("Λ", latex=r"\Lambda")
    ship_time_axis = sandwich(Lambda, g0).name(latex=r"\gamma_0'")

    gm.md(t"""
    ## Journey Summary

    {rapidity} = {phi:.5f}

    {Lambda} = {Lambda.eval()}

    Boosted ship time axis {ship_time_axis} = {ship_time_axis.eval()}

    Peak speed: $\\beta = v/c = {beta:.6f}$ and $\\gamma = {gamma:.6f}$

    Ship time: {total_ship_time / year_s:.3f} years

    Earth time: {total_earth_time / year_s:,.3f} years

    Earth-frame distance: {total_distance / light_year_m:,.3f} light-years

    Acceleration-only distance each leg: {x_acc / light_year_m:,.3f} light-years

    Coast distance: {x_coast / light_year_m:,.3f} light-years
    """)
    return (
        beta,
        c,
        g,
        gamma,
        light_year_m,
        t_acc,
        t_coast,
        total_distance,
        total_earth_time,
        x_acc,
        year_s,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Traveler vs Earth

    The traveler's acceleration is constant in their own instantaneous rest frame.
    That makes rapidity the clean variable:

    - ship acceleration time adds linearly to rapidity
    - Earth-frame velocity stays below `c`
    - Earth-frame time and distance grow hyperbolically
    """)
    return


@app.cell
def _(beta, gamma, gm, tau_acc_years, tau_coast_years):
    _ship_acc = tau_acc_years.value
    _ship_coast = tau_coast_years.value
    _earth_coast = gamma * _ship_coast
    gm.md(t"""
    With $\\tau_{{acc}} = {_ship_acc:.2f}$ years and $\\tau_{{coast}} = {_ship_coast:.2f}$ years:

    - Earth sees the coast phase last {_earth_coast:,.3f} years
    - The ship reaches {beta:.4%} of light speed before deceleration
    - If coasting is zero, this becomes the classic accelerate-half / decelerate-half brachistochrone profile
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Earth-Frame Worldline

    The plot below shows the outbound worldline in Earth coordinates. The
    acceleration and deceleration legs are hyperbolic; the coast phase is linear.
    """)
    return


@app.cell
def _(
    beta,
    c,
    g,
    light_year_m,
    np,
    plt,
    t_acc,
    t_coast,
    total_distance,
    total_earth_time,
    x_acc,
    year_s,
):
    _n = 240

    _t1 = np.linspace(0.0, t_acc, _n)
    _x1 = np.sqrt((c**2 / g) ** 2 + (c * _t1) ** 2) - (c**2 / g)

    _t2 = np.linspace(t_acc, t_acc + t_coast, max(2, _n // 2))
    _x2 = x_acc + beta * c * (_t2 - t_acc)

    _t3_local = np.linspace(0.0, t_acc, _n)
    _x3 = total_distance - (np.sqrt((c**2 / g) ** 2 + (c * _t3_local) ** 2) - (c**2 / g))
    _t3 = total_earth_time - _t3_local

    _fig, _ax = plt.subplots(figsize=(8, 5))
    _ax.plot(_t1 / year_s, _x1 / light_year_m, color="crimson", linewidth=2.5, label="accelerate")
    if t_coast > 0:
        _ax.plot(_t2 / year_s, _x2 / light_year_m, color="steelblue", linewidth=2.5, label="coast")
    _ax.plot(_t3 / year_s, _x3 / light_year_m, color="darkorange", linewidth=2.5, label="decelerate")
    _ax.plot([0, total_earth_time / year_s], [0, total_distance / light_year_m], "k:", alpha=0.15)
    _ax.set_xlabel("Earth time (years)")
    _ax.set_ylabel("Distance from Earth (light-years)")
    _ax.set_title("One-way 1g relativistic journey")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Rules of Thumb

    A few consequences of the relativistic formulas:

    - one year of 1g acceleration already gets you to a large fraction of `c`
    - once `γ` becomes large, ship coasting time corresponds to much longer Earth time
    - destination distance scales much faster than the ship's own elapsed time
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
