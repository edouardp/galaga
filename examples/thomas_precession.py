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

    from ga import Algebra, exp, sandwich, unit
    import galaga_marimo as gm
    from ga.notation import NotationRule

    return Algebra, NotationRule, exp, gm, mo, np, plt, sandwich, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Thomas-Wigner Rotation and Thomas Precession

    Two non-collinear boosts do not compose to a pure boost. Their mismatch leaves
    a spatial rotation, the Thomas-Wigner rotation. In spacetime algebra this falls
    straight out of rotor multiplication.

    The first section studies that finite rotation from composing boosts. The later
    section shows how the continuous limit of many tiny boost mismatches becomes
    Thomas precession.
    """)
    return


@app.cell
def _(Algebra, NotationRule):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    sta.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
    return g0, g1, g2


@app.cell
def _(mo):
    phi_x = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.7, label="x-rapidity")
    phi_y = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.9, label="y-rapidity")
    mo.vstack([phi_x, phi_y])
    return phi_x, phi_y


@app.cell(hide_code=True)
def _(exp, g0, g1, g2, gm, phi_x, phi_y):
    Bx = (g0 * g1).name(latex="B_x")
    By = (g0 * g2).name(latex="B_y")
    Rx = exp((phi_x.value / 2) * Bx)
    Ry = exp((phi_y.value / 2) * By)
    Rxy = Ry * Rx
    Ryx = Rx * Ry
    mismatch = Rxy * ~Ryx

    gm.md(t"""
    ## Thomas-Wigner Rotation from Boost Composition

    {Rx} = {Rx.eval()}

    {Ry} = {Ry.eval()}

    {Rxy} = {Rxy.eval()}

    {Ryx} = {Ryx.eval()}

    Mismatch rotor {mismatch} = {mismatch.eval()}

    This residual even multivector is the finite Thomas-Wigner rotation.
    """)
    return (mismatch,)


@app.cell(hide_code=True)
def _(g1, g2, mismatch, plt, sandwich):
    _e1 = sandwich(mismatch, g1).eval()
    _e2 = sandwich(mismatch, g2).eval()
    _v1 = _e1.vector_part[:2]
    _v2 = _e2.vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, 0, 1, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, _v1[0], _v1[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, _v2[0], _v2[1], angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-1.2, 1.2)
    _ax.set_ylim(-1.2, 1.2)
    _ax.set_title("Residual spatial rotation in the x-y plane")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Thomas Precession from Many Tiny Boosts

    The finite mismatch above is the Thomas-Wigner rotation for two non-collinear
    boosts. Thomas precession is the continuous version of the same effect: as a
    particle follows a curved relativistic path, its instantaneous rest frame is
    built from many tiny non-collinear boosts, and those tiny mismatches accumulate
    into a real precession of the spin axis.

    For uniform circular motion, the precession rate magnitude is

    $$
    \Omega_T = (\gamma - 1) \omega
    $$

    opposite the orbital rotation. After one orbit the spin axis lags by

    $$
    \Delta 	heta_T = 2\pi (\gamma - 1).
    $$

    Below, the first cell gives the analytic prediction. The second computes the
    same effect in GA by comparing consecutive pure boosts into the instantaneous
    rest frame and extracting the residual spatial rotor left after the net boost
    is factored out.
    """)
    return


@app.cell
def _(mo):
    beta = mo.ui.slider(start=0.0, stop=0.99, step=0.01, value=0.6, label="orbital speed β = v/c")
    orbit_period = mo.ui.slider(start=0.5, stop=20.0, step=0.1, value=5.0, label="lab-frame orbital period")
    num_orbits = mo.ui.slider(start=1, stop=20, step=1, value=5, label="number of orbits")
    steps_per_orbit = mo.ui.slider(start=12, stop=720, step=12, value=180, label="tiny boosts per orbit")
    mo.vstack([beta, orbit_period, num_orbits, steps_per_orbit])
    return beta, num_orbits, orbit_period, steps_per_orbit


@app.cell(hide_code=True)
def _(beta, gm, np, num_orbits, orbit_period):
    _beta = beta.value
    gamma = 1.0 / np.sqrt(1.0 - _beta**2) if _beta < 1.0 else np.inf
    omega = 2 * np.pi / orbit_period.value
    omega_t = (gamma - 1.0) * omega
    lag_per_orbit = 2 * np.pi * (gamma - 1.0)
    total_lag = num_orbits.value * lag_per_orbit

    gm.md(t"""
    ## Uniform Circular Motion

    For $\\beta = {_beta:.3f}$:

    $$
    \\gamma = {gamma:.6f}
    $$

    Orbital angular frequency:

    $$
    \\omega = {omega:.6f}
    $$

    Thomas precession rate magnitude:

    $$
    \\Omega_T = {omega_t:.6f}
    $$

    Spin-axis lag per orbit:

    $$
    \\Delta \\theta_T = {lag_per_orbit:.6f}\\ \\text{{rad}} = {np.degrees(lag_per_orbit):.3f}^\\circ
    $$

    Over {num_orbits.value} orbits, the accumulated lag is

    $$
    {total_lag:.6f}\\ \\text{{rad}} = {np.degrees(total_lag):.3f}^\\circ.
    $$
    """)
    return gamma, omega, omega_t, total_lag


@app.cell(hide_code=True)
def _(beta, exp, g0, g1, g2, gamma, gm, np, num_orbits, steps_per_orbit, unit):
    _beta = beta.value
    _g0 = g0.eval()
    _g1 = g1.eval()
    _g2 = g2.eval()
    rapidity = np.arctanh(_beta) if _beta < 1.0 else np.inf

    def orbital_frame_rotor(phase_angle):
        return exp(-(phase_angle / 2) * (_g1 * _g2))

    def tangent_direction(phase_angle):
        C = orbital_frame_rotor(phase_angle)
        return C * _g2 * ~C

    def boost_to_rest_frame(phase_angle):
        return exp((rapidity / 2) * (_g0 * tangent_direction(phase_angle)))

    num_steps = num_orbits.value * steps_per_orbit.value
    phase_samples = np.linspace(0.0, 2 * np.pi * num_orbits.value, num_steps + 1)
    ga_lag_samples = [0.0]

    for k in range(num_steps):
        L0 = boost_to_rest_frame(phase_samples[k])
        L1 = boost_to_rest_frame(phase_samples[k + 1])
        u0 = L0 * _g0 * ~L0
        u1 = L1 * _g0 * ~L1
        step_boost = unit(1 + u1 * u0)
        wigner_step = (~(step_boost * L0) * L1).eval()
        delta_theta = -2 * np.arctan2(wigner_step.data[6], wigner_step.scalar_part)
        ga_lag_samples.append(ga_lag_samples[-1] + delta_theta)

    ga_lag_samples = np.array(ga_lag_samples)
    analytic_lag_samples = (gamma - 1.0) * phase_samples
    numeric_lag_one_orbit = ga_lag_samples[steps_per_orbit.value]
    analytic_lag_one_orbit = 2 * np.pi * (gamma - 1.0)

    gm.md(t"""
    ## Tiny-Boost Comparison

    Steps per orbit: {steps_per_orbit.value}

    At each step we build the pure boost {step_boost} that carries the previous
    four-velocity into the next one, compare it with the next pure lab-to-comoving
    boost {L1}, and keep only the residual spatial rotor

    $$
    W_k = (B_k L_k)^\\dagger L_{{k+1}}.
    $$

    Each $W_k$ is a tiny spatial rotation in the $\\gamma_1 \\gamma_2$ plane, so
    we extract its signed angle from the scalar and $\\gamma_1 \\gamma_2$
    coefficient and sum those increments directly. That avoids the branch-cut
    ambiguity you get if you try to read the total lag from the angle of a rotated
    spatial axis after many full turns.

    Numeric GA lag after one orbit:

    $$
    {numeric_lag_one_orbit:.6f}\\ \\text{{rad}} = {np.degrees(numeric_lag_one_orbit):.3f}^\\circ
    $$

    Analytic lag after one orbit:

    $$
    {analytic_lag_one_orbit:.6f}\\ \\text{{rad}} = {np.degrees(analytic_lag_one_orbit):.3f}^\\circ
    $$

    Absolute difference:

    $$
    {abs(numeric_lag_one_orbit - analytic_lag_one_orbit):.6e}
    $$
    """)
    return analytic_lag_samples, ga_lag_samples, phase_samples


@app.cell
def _(
    analytic_lag_samples,
    ga_lag_samples,
    np,
    omega,
    omega_t,
    orbit_period,
    phase_samples,
    plt,
    total_lag,
):
    _t = np.linspace(0, phase_samples[-1] / omega * orbit_period.value / orbit_period.value, 600)
    _orbital_angle = omega * _t
    _spin_angle = (omega - omega_t) * _t

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    _ax1.plot(_t, _orbital_angle, color="steelblue", linewidth=2.5, label="orbital angle")
    _ax1.plot(_t, _spin_angle, color="crimson", linewidth=2.5, label="spin axis angle")
    _ax1.set_xlabel("lab time")
    _ax1.set_ylabel("angle (rad)")
    _ax1.set_title("Orbital rotation vs spin orientation")
    _ax1.grid(True, alpha=0.2)
    _ax1.legend()

    _orbits = phase_samples / (2 * np.pi)
    _ax2.plot(_orbits, np.degrees(ga_lag_samples), color="darkorange", linewidth=2.5, label="GA tiny-boost accumulation")
    _ax2.plot(_orbits, np.degrees(analytic_lag_samples), color="black", alpha=0.5, linestyle="--", label="analytic $(\\gamma-1)\\phi$")
    _ax2.axhline(np.degrees(total_lag), color="black", alpha=0.2, linestyle=":")
    _ax2.set_xlabel("completed orbits")
    _ax2.set_ylabel("spin lag (degrees)")
    _ax2.set_title("Accumulated Thomas precession")
    _ax2.grid(True, alpha=0.2)
    _ax2.legend()
    _fig.tight_layout()
    _fig
    return


if __name__ == "__main__":
    app.run()
