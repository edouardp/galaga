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

    from ga import Algebra, exp, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # The Twin Paradox

    One twin stays on Earth. The other travels away, turns around, and returns.
    The key geometric fact is simple: different worldlines between the same two
    reunion events can accumulate different proper times.

    This notebook uses spacetime algebra to connect the kinematics to the usual
    story:

    - rapidity labels the boost state
    - the stay-at-home twin follows a straight timelike worldline
    - the traveler follows a broken worldline with an outbound and inbound leg
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1


@app.cell
def _(g0, g1, gm):
    boost_plane = (g0 * g1).name("B", latex=r"\gamma_0 \gamma_1")
    gm.md(t"""
    ## STA Setup

    Outbound and inbound inertial legs are related to Earth by boost rotors in the
    plane {boost_plane} = {boost_plane.eval()}.

    Proper time is the Minkowski length of a timelike worldline segment, so the
    twin paradox is really a spacetime-geometry statement rather than a paradox.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Controls

    The traveler is modeled as:

    1. an outbound inertial leg at speed `v`
    2. an instantaneous turnaround
    3. an inbound inertial leg at the same speed

    The slider `T_half` is the Earth-frame time for one leg.
    """)
    return


@app.cell
def _(mo):
    beta = mo.ui.slider(start=0.0, stop=0.995, step=0.005, value=0.8, label="traveler speed v/c")
    earth_half = mo.ui.slider(start=0.5, stop=30.0, step=0.5, value=5.0, label="Earth time per leg (years)")
    mo.vstack([beta, earth_half])
    return beta, earth_half


@app.cell(hide_code=True)
def _(beta, earth_half, exp, g0, g1, gm, np, sandwich):
    c = 299_792_458.0
    year_s = 365.25 * 24 * 60 * 60
    light_year_m = c * year_s

    _beta = beta.value
    T_half = earth_half.value
    gamma = 1.0 / np.sqrt(1.0 - _beta**2) if _beta < 1.0 else np.inf
    phi = np.arctanh(_beta) if _beta < 1.0 else np.inf
    traveler_half = T_half / gamma if gamma != np.inf else 0.0

    reunion_earth = 2.0 * T_half
    reunion_ship = 2.0 * traveler_half
    turnaround_distance = _beta * T_half

    outbound_rotor = exp((phi / 2) * (g0 * g1)).name(latex=r"\Lambda_{\mathrm{out}}")
    inbound_rotor = exp((-phi / 2) * (g0 * g1)).name(latex=r"\Lambda_{\mathrm{in}}")
    outbound_axis = sandwich(outbound_rotor, g0).name(latex=r"u_{\mathrm{out}}")
    inbound_axis = sandwich(inbound_rotor, g0).name(latex=r"u_{\mathrm{in}}")

    gm.md(t"""
    ## Proper-Time Comparison

    {outbound_rotor} = {outbound_rotor.eval()}

    {inbound_rotor} = {inbound_rotor.eval()}

    {outbound_axis} = {outbound_axis.eval()}

    {inbound_axis} = {inbound_axis.eval()}

    Rapidity: $\\varphi = {phi:.5f}$

    Earth-frame reunion time: {reunion_earth:.3f} years

    Traveler proper time: {reunion_ship:.3f} years

    Age gap at reunion: {reunion_earth - reunion_ship:.3f} years

    Turnaround distance: {turnaround_distance:.3f} light-years

    Each traveler leg lasts {traveler_half:.3f} years of ship time
    """)
    return T_half, gamma, reunion_earth, reunion_ship, turnaround_distance


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Why the Traveler Ages Less

    In Euclidean geometry the straight line is shortest. In Minkowski geometry,
    for timelike paths, the inertial straight worldline is longest in proper
    time. The Earth twin stays inertial the whole trip; the traveler does not.
    """)
    return


@app.cell
def _(T_half, beta, gamma, gm, reunion_earth, reunion_ship):
    gm.md(t"""
    With $\\beta = {beta.value:.3f}$ and one Earth-frame leg lasting {T_half:.2f} years:

    - Earth twin proper time = {reunion_earth:.3f} years
    - Traveling twin proper time = {reunion_ship:.3f} years
    - Time dilation per inertial leg is set by $\\gamma = {gamma:.5f}$

    The turnaround matters because it changes which inertial frame the traveler uses
    to compare distant clocks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Spacetime Diagram

    The Earth twin stays on the vertical worldline `x = 0`. The traveler traces
    an outward and return leg that meet again at the reunion event.
    """)
    return


@app.cell
def _(T_half, beta, np, plt, reunion_earth, turnaround_distance):
    _t1 = np.linspace(0.0, T_half, 100)
    _x1 = beta.value * _t1
    _t2 = np.linspace(T_half, reunion_earth, 100)
    _x2 = turnaround_distance - beta.value * (_t2 - T_half)

    _fig, _ax = plt.subplots(figsize=(6.5, 6.5))
    _cone = np.linspace(0, reunion_earth, 200)
    _ax.plot(_cone, _cone, "k--", alpha=0.25)
    _ax.plot(-_cone, _cone, "k--", alpha=0.25)

    _ax.plot(np.zeros_like(_cone), _cone, color="steelblue", linewidth=2.5, label="Earth twin")
    _ax.plot(_x1, _t1, color="crimson", linewidth=2.5, label="traveler outbound")
    _ax.plot(_x2, _t2, color="darkorange", linewidth=2.5, label="traveler inbound")
    _ax.plot([0], [0], "ko", ms=6)
    _ax.plot([turnaround_distance], [T_half], "ko", ms=6)
    _ax.plot([0], [reunion_earth], "ko", ms=6)

    _ax.text(0.08, 0.25, "departure")
    _ax.text(turnaround_distance + 0.08, T_half, "turnaround")
    _ax.text(0.08, reunion_earth, "reunion")

    _ax.set_xlabel("distance from Earth (light-years)")
    _ax.set_ylabel("Earth time (years)")
    _ax.set_title("Twin paradox worldlines")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _ax.set_xlim(-reunion_earth * 0.15, max(1.5, turnaround_distance * 1.25))
    _ax.set_ylim(0, reunion_earth * 1.05)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Limiting Cases

    - at `v = 0`, both twins follow the same worldline and age equally
    - as `v` approaches `c`, the traveler's proper time shrinks relative to Earth
    - longer outbound and inbound legs increase both the reunion distance and the age gap
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
