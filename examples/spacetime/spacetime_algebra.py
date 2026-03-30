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

    return (mo,)


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga import Algebra, grade, reverse, dual, sandwich, norm2
    from galaga.symbolic import sym, grade as sym_grade, simplify, norm, unit, inverse
    import galaga_marimo as gm

    return (
        Algebra,
        gm,
        grade,
        inverse,
        norm,
        np,
        plt,
        sandwich,
        simplify,
        sym,
        sym_grade,
        unit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Spacetime Algebra (STA)

    The **Spacetime Algebra** is the Clifford algebra $\mathrm{{Cl}}(1,3)$: one timelike basis vector ($\gamma_0^2 = +1$) and three spacelike ($\gamma_i^2 = -1$).

    STA unifies rotations, Lorentz boosts, and electromagnetism in a single algebraic framework — no matrices, no index gymnastics.
    """)
    return


@app.cell
def _(Algebra, gm):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors()
    I = sta.I

    _g0sq = g0 * g0
    _g1sq = g1 * g1
    _g2sq = g2 * g2
    _g3sq = g3 * g3

    gm.md(t"""**Basis vectors and their squares:**
    - $\\gamma_0^2$ = {_g0sq}
    - $\\gamma_1^2$ = {_g1sq}
    - $\\gamma_2^2$ = {_g2sq}
    - $\\gamma_3^2$ = {_g3sq}
    - Pseudoscalar $I$ = {I}, $\\quad I^2$ = {I*I}""")
    return I, g0, g1, g2, g3, sta


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Bivector Zoo

    STA has **six** bivectors, split into two families. The sign of the square tells you
    whether a bivector generates a **hyperbolic** (boost) or **circular** (rotation) transformation.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, gm):
    _bivectors = [
        ("γ₀γ₁ (timelike)", g0 * g1),
        ("γ₀γ₂ (timelike)", g0 * g2),
        ("γ₀γ₃ (timelike)", g0 * g3),
        ("γ₁γ₂ (spacelike)", g1 * g2),
        ("γ₁γ₃ (spacelike)", g1 * g3),
        ("γ₂γ₃ (spacelike)", g2 * g3),
    ]
    _lines = "\n".join(f"- {name}: square = **{(b * b).scalar_part:+.0f}**" for name, b in _bivectors)
    gm.md(t"{_lines:text}")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Spatial Rotations

    Spacelike bivectors ($\\gamma_i\\gamma_j$, square $= -1$) generate spatial rotations.
    The rotor is $R = \\cos(\\theta/2) - \\sin(\\theta/2)\\,\\gamma_1\\gamma_2$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    rotation_slider = mo.ui.slider(
        start=0, stop=360, step=1, value=90, label="θ (degrees)"
    )
    rotation_slider
    return (rotation_slider,)


@app.cell
def _(g1, g2, gm, mo, np, rotation_slider, sandwich, sta, sym, sym_grade):
    _theta = np.radians(rotation_slider.value)
    _R = sta.rotor_from_plane_angle(g1 ^ g2, radians=_theta)
    _result = sandwich(_R, g1)

    _R_s = sym(_R, "R")
    _v_s = sym(g1, "γ₁")
    _expr = sym_grade(_R_s * _v_s * ~_R_s, 1)

    _RR = _R * ~_R
    mo.vstack([
        gm.md(t"$\\theta = {rotation_slider.value}°$"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"Symbolic: {_expr}"),
        gm.md(t"Result: {_result}"),
        gm.md(t"$R\\tilde{{R}} =$ {_RR}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Lorentz Boosts

    Timelike bivectors ($\\gamma_0\\gamma_i$, square $= +1$) generate Lorentz boosts.
    The rotor is $R = \\cosh(\\varphi/2) + \\sinh(\\varphi/2)\\,\\gamma_0\\gamma_1$.

    Key relations: $\\beta = v/c = \\tanh\\varphi$, $\\gamma = \\cosh\\varphi$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    boost_slider = mo.ui.slider(
        start=0.0, stop=3.0, step=0.05, value=0.5, label="Rapidity φ"
    )
    boost_slider
    return (boost_slider,)


@app.cell
def _(boost_slider, g0, g1, gm, mo, np, sandwich, sta):
    _phi = boost_slider.value
    _B = g0 * g1
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * _B

    _g0_boosted = sandwich(_R, g0)
    _g1_boosted = sandwich(_R, g1)

    _beta = np.tanh(_phi)
    _gamma = np.cosh(_phi)

    _RR = (_R * ~_R).scalar_part
    mo.vstack([
        gm.md(t"$\\varphi = {_phi:.2f}$"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$\\gamma_0' =$ {_g0_boosted}"),
        gm.md(t"$\\gamma_1' =$ {_g1_boosted}"),
        gm.md(t"- $\\beta = v/c = \\tanh\\varphi = {_beta:.4f}$"),
        gm.md(t"- $\\gamma = \\cosh\\varphi = {_gamma:.4f}$"),
        gm.md(t"$R\\tilde{{R}} =$ {_RR:.4f}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Minkowski Diagram

    The rest-frame axes ($\\gamma_0$, $\\gamma_1$) are orthogonal. Under a boost, the
    boosted axes tilt toward the light cone but never reach it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mink_slider = mo.ui.slider(
        start=0.0, stop=3.0, step=0.05, value=0.8, label="Rapidity φ"
    )
    mink_slider
    return (mink_slider,)


@app.cell(hide_code=True)
def _(g0, g1, mink_slider, np, plt, sandwich, sta):
    _phi = mink_slider.value
    _B = g0 * g1
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * _B

    _g0b = sandwich(_R, g0)
    _g1b = sandwich(_R, g1)

    # Extract components: g0 coefficient is "time", g1 coefficient is "space"
    # In our basis ordering, g0 is index 1, g1 is index 2
    _g0b_t, _g0b_x = _g0b.data[1], _g0b.data[2]  # boosted γ₀
    _g1b_t, _g1b_x = _g1b.data[1], _g1b.data[2]  # boosted γ₁

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.set_xlim(-2.5, 2.5)
    _ax.set_ylim(-2.5, 2.5)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.set_xlabel("$x$ (space)", fontsize=12)
    _ax.set_ylabel("$t$ (time)", fontsize=12)

    # Light cone
    _lc = np.linspace(-2.5, 2.5, 100)
    _ax.plot(_lc, _lc, "k--", alpha=0.3, label="light cone")
    _ax.plot(_lc, -_lc, "k--", alpha=0.3)

    # Rest frame axes
    _ax.quiver(0, 0, 0, 2, angles="xy", scale_units="xy", scale=1,
               color="steelblue", width=0.015, label="$\\gamma_0$ (rest)")
    _ax.quiver(0, 0, 2, 0, angles="xy", scale_units="xy", scale=1,
               color="steelblue", width=0.015, label="$\\gamma_1$ (rest)")

    # Boosted axes (scale to length 2 for visibility)
    _ax.quiver(0, 0, 2 * _g0b_x, 2 * _g0b_t, angles="xy", scale_units="xy", scale=1,
               color="crimson", width=0.015, label="$\\gamma_0'$ (boosted)")
    _ax.quiver(0, 0, 2 * _g1b_x, 2 * _g1b_t, angles="xy", scale_units="xy", scale=1,
               color="crimson", width=0.008, label="$\\gamma_1'$ (boosted)")

    _ax.legend(loc="upper left", fontsize=10)
    _ax.set_title(f"Minkowski Diagram — φ = {_phi:.2f}", fontsize=13)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Velocity Addition

    Rapidities add linearly: $\\varphi = \\varphi_1 + \\varphi_2$.
    Velocities compose via Einstein's formula: $v = \\frac{{v_1 + v_2}}{{1 + v_1 v_2/c^2}}$.
    The speed of light is never exceeded.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    phi1_slider = mo.ui.slider(start=0.0, stop=2.0, step=0.05, value=0.6, label="φ₁")
    phi2_slider = mo.ui.slider(start=0.0, stop=2.0, step=0.05, value=0.8, label="φ₂")
    mo.vstack([phi1_slider, phi2_slider])
    return phi1_slider, phi2_slider


@app.cell(hide_code=True)
def _(gm, np, phi1_slider, phi2_slider):
    _phi1 = phi1_slider.value
    _phi2 = phi2_slider.value
    _phi_total = _phi1 + _phi2

    _v1 = np.tanh(_phi1)
    _v2 = np.tanh(_phi2)
    _v_einstein = (_v1 + _v2) / (1 + _v1 * _v2)
    _v_classical = _v1 + _v2
    _v_rapidity = np.tanh(_phi_total)

    _warn = "⚠️ exceeds c!" if _v_classical > 1 else ""
    gm.md(t"""- $\\varphi_1 = {_phi1:.2f}$, $v_1/c = \\tanh\\varphi_1 = {_v1:.4f}$
    - $\\varphi_2 = {_phi2:.2f}$, $v_2/c = \\tanh\\varphi_2 = {_v2:.4f}$
    - $\\varphi_{{\\text{{total}}}} = {_phi_total:.2f}$, $\\tanh\\varphi_{{\\text{{total}}}} = {_v_rapidity:.4f}$
    - Einstein addition: $v/c = {_v_einstein:.4f}$
    - Classical addition: $v_1 + v_2 = {_v_classical:.4f}$ {_warn:text}""")
    return


@app.cell(hide_code=True)
def _(np, phi1_slider, phi2_slider, plt):
    _v1 = np.tanh(phi1_slider.value)
    _v2_range = np.linspace(0, 0.99, 200)

    _einstein = (_v1 + _v2_range) / (1 + _v1 * _v2_range)
    _classical = _v1 + _v2_range
    _v2_current = np.tanh(phi2_slider.value)
    _v_current = (_v1 + _v2_current) / (1 + _v1 * _v2_current)

    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    _ax.plot(_v2_range, _einstein, "crimson", lw=2, label="Einstein addition")
    _ax.plot(_v2_range, _classical, "steelblue", lw=2, ls="--", label="Classical addition")
    _ax.axhline(1.0, color="k", ls=":", alpha=0.5, label="$c$ (speed of light)")
    _ax.plot(_v2_current, _v_current, "ko", ms=8, zorder=5)

    _ax.set_xlabel("$v_2 / c$", fontsize=12)
    _ax.set_ylabel("$v_{\\mathrm{total}} / c$", fontsize=12)
    _ax.set_title(f"Velocity Addition ($v_1/c = {_v1:.2f}$)", fontsize=13)
    _ax.set_xlim(0, 1)
    _ax.set_ylim(0, 2.0)
    _ax.legend(fontsize=10)
    _ax.grid(True, alpha=0.2)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Thomas–Wigner Rotation

    Composing two boosts along **different** axes yields a boost *plus* a spatial rotation.
    This is the Thomas–Wigner rotation — painful with matrices, but it falls out naturally
    from the algebra: the spatial bivector component of $R_1 R_2 (R_2 R_1)^{-1}$.
    """)
    return


@app.cell
def _(g0, g1, g2, gm, grade, mo, np, sta):
    _phi_x = 0.6
    _phi_y = 0.8

    _Rx = sta.scalar(np.cosh(_phi_x / 2)) + np.sinh(_phi_x / 2) * (g0 * g1)
    _Ry = sta.scalar(np.cosh(_phi_y / 2)) + np.sinh(_phi_y / 2) * (g0 * g2)

    _R12 = _Rx * _Ry
    _R21 = _Ry * _Rx

    _diff = _R12 * ~_R21

    # The grade-2 part of the difference reveals the Thomas–Wigner rotation
    _spatial = grade(_diff, 2)

    _commute = np.allclose(_R12.data, _R21.data)
    mo.vstack([
        gm.md(t"Boost x: $\\varphi_x = {_phi_x}$, Boost y: $\\varphi_y = {_phi_y}$"),
        mo.hstack([mo.md("$R_x R_y =$"), _R12], justify="start"),
        mo.hstack([mo.md("$R_y R_x =$"), _R21], justify="start"),
        gm.md(t"$R_x R_y = R_y R_x$? **{_commute!s}** — boosts don't commute!"),
        mo.hstack([mo.md("$(R_x R_y)(R_y R_x)^{{-1}} =$"), _diff], justify="start"),
        mo.hstack([mo.md("Bivector part (Thomas–Wigner rotation):"), _spatial], justify="start"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md("""
    ## The Electromagnetic Field

    In STA, the EM field is a single bivector $F = \\mathbf{E} + I\\mathbf{B}$ where:
    - $\\mathbf{E} = E^i \\gamma_i\\gamma_0$ (electric part — timelike bivectors)
    - $I\\mathbf{B}$ (magnetic part — spacelike bivectors)

    The two Lorentz invariants live in $F^2$:
    - Scalar part: $E^2 - B^2$
    - Pseudoscalar part: $2\\,\\mathbf{E}\\cdot\\mathbf{B}$
    """)
    return


@app.cell
def _(I, g0, g1, g3, gm, grade, mo):
    # E in x-direction, B in z-direction
    # Relative vectors: σᵢ = γᵢγ₀
    _Ex = 2.0
    _Bz = 1.0

    _E = _Ex * (g1 * g0)           # timelike bivector
    _B = _Bz * (g3 * g0)           # relative B vector (σ₃)
    _F = _E + I * _B               # IB gives spacelike bivector

    _F2 = _F * _F
    _scalar_inv = (_F2).scalar_part
    _pseudo_inv = (grade(_F2, 4) * ~I).scalar_part  # pseudoscalar coefficient

    _IB = I * _B
    mo.vstack([
        gm.md(t"$E_x = {_Ex}, \\qquad B_z = {_Bz}$"),
        gm.md(t"$\\mathbf{{E}} =$ {_E}"),
        gm.md(t"$I\\mathbf{{B}} =$ {_IB}"),
        gm.md(t"$F = \\mathbf{{E}} + I\\mathbf{{B}} =$ {_F}"),
        gm.md(t"$F^2 =$ {_F2}"),
        gm.md(t"- Scalar invariant ($E^2 - B^2$): **{_scalar_inv:.1f}**"),
        gm.md(t"- Pseudoscalar invariant ($2\\mathbf{{E}}\\cdot\\mathbf{{B}}$): **{_pseudo_inv:.1f}**"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md("""
    ## Boosting the EM Field

    Under a Lorentz boost, $F \\to R F \\tilde{R}$. The electric and magnetic components
    mix, but $F^2$ is invariant.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    em_boost_slider = mo.ui.slider(
        start=0.0, stop=2.0, step=0.05, value=0.5, label="Rapidity φ"
    )
    em_boost_slider
    return (em_boost_slider,)


@app.cell
def _(I, em_boost_slider, g0, g1, g3, gm, mo, np, sandwich, sta):
    _phi = em_boost_slider.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)

    # Original field: E in x, B in z
    _E = 2.0 * (g1 * g0)
    _F = _E + I * 1.0 * (g3 * g0)

    # Boost
    _F_boosted = sandwich(_R, _F)

    _F2_orig = (_F * _F).scalar_part
    _F2_boosted = (_F_boosted * _F_boosted).scalar_part

    _inv = np.allclose(_F2_orig, _F2_boosted)
    mo.vstack([
        gm.md(t"$\\varphi = {_phi:.2f}$"),
        gm.md(t"$F =$ {_F}"),
        gm.md(t"$F' = R F \\tilde{{R}} =$ {_F_boosted}"),
        gm.md(t"- $F^2$ (original): **{_F2_orig:.4f}**"),
        gm.md(t"- $F'^2$ (boosted): **{_F2_boosted:.4f}**"),
        gm.md(t"- Invariant? **{_inv!s}**"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md("""
    ## Relative Vectors — The Pauli Algebra

    The relative vectors $\\sigma_i = \\gamma_i \\gamma_0$ are bivectors in STA but form a
    subalgebra isomorphic to the Pauli algebra: $\\sigma_i^2 = 1$, $\\sigma_i\\sigma_j = -\\sigma_j\\sigma_i$.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, gm):
    _s1 = g1 * g0
    _s2 = g2 * g0
    _s3 = g3 * g0

    _sigmas = [("σ₁", _s1), ("σ₂", _s2), ("σ₃", _s3)]

    # Squares
    _squares = "\n".join(f"- ${n}^2 = $ {(s * s).scalar_part:+.0f}" for n, s in _sigmas)

    # Anticommutation
    _anticomm = "\n".join([
        f"- σ₁σ₂ + σ₂σ₁ = {(_s1 * _s2 + _s2 * _s1).scalar_part:.0f}",
        f"- σ₁σ₃ + σ₃σ₁ = {(_s1 * _s3 + _s3 * _s1).scalar_part:.0f}",
        f"- σ₂σ₃ + σ₃σ₂ = {(_s2 * _s3 + _s3 * _s2).scalar_part:.0f}",
    ])

    # σ₁σ₂σ₃ = I
    _product = _s1 * _s2 * _s3

    gm.md(t"""**Squares** (all $+1$):
    {_squares:text}

    **Anticommutation** (all $0$):
    {_anticomm:text}

    **σ₁σ₂σ₃ = {_product}** (the pseudoscalar $I$)""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Symbolic Identities

    The symbolic layer lets us verify algebraic identities as expression trees,
    then evaluate them to confirm numerically.
    """)
    return


@app.cell
def _(g0, g1, g2, gm, inverse, norm, simplify, sta, sym, unit):
    _R = sym(sta.rotor_from_plane_angle(g1 ^ g2, radians=0.5), "R")
    _v = sym(g1, "v")
    _F = sym(2.0 * (g1 * g0), "F")

    _rules = [
        ("Double reverse: ~~R", simplify(~~_R)),
        ("Rotor normalization: R~R", simplify(_R * ~_R)),
        ("Double inverse: inv(inv(v))", simplify(inverse(inverse(_v)))),
        ("Norm of unit: ‖unit(v)‖", simplify(norm(unit(_v)))),
        ("Linearity: F + F", simplify(_F + _F)),
    ]

    _lines = "\n".join(f"- {name} → ${result.latex()}$" for name, result in _rules)
    gm.md(t"{_lines:text}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
