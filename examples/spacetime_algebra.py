import marimo

app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    if _root not in sys.path:
        sys.path.insert(0, _root)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Spacetime Algebra (STA)

    The Spacetime Algebra is Cl(1,3) — one timelike dimension ($\\gamma_0^2 = +1$)
    and three spacelike ($\\gamma_i^2 = -1$). It encodes special relativity,
    electromagnetism, and the Dirac equation in a single algebraic framework.
    """)
    return


@app.cell
def _():
    import numpy as np
    from ga import Algebra
    from ga.symbolic import (
        sym, gp, op, grade, reverse, involute, conjugate,
        dual, norm, unit, inverse, sandwich, simplify,
        even_grades, odd_grades, left_contraction,
    )
    return (
        Algebra, np,
        sym, gp, op, grade, reverse, involute, conjugate,
        dual, norm, unit, inverse, sandwich, simplify,
        even_grades, odd_grades, left_contraction,
    )


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors()
    return sta, g0, g1, g2, g3


@app.cell
def _(mo):
    mo.md("## Basis Vectors and Signature")
    return


@app.cell
def _(g0, g1, g2, g3, mo, sta):
    mo.vstack([
        mo.md(f"$\\gamma_0^2 = $ `{g0 * g0}` (timelike)"),
        mo.md(f"$\\gamma_1^2 = $ `{g1 * g1}` (spacelike)"),
        mo.md(f"$\\gamma_2^2 = $ `{g2 * g2}` (spacelike)"),
        mo.md(f"$\\gamma_3^2 = $ `{g3 * g3}` (spacelike)"),
        mo.md(f"Pseudoscalar $I = $ `{sta.I}`"),
        mo.md(f"$I^2 = $ `{sta.I * sta.I}`"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Bivectors — Boosts and Rotations

    In STA, bivectors split into two types:
    - **Timelike bivectors** ($\\gamma_0 \\gamma_i$): generate Lorentz boosts
    - **Spacelike bivectors** ($\\gamma_i \\gamma_j$): generate spatial rotations
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo):
    mo.vstack([
        mo.md("**Boost generators** (square to $+1$):"),
        mo.md(f"- $(\\gamma_0 \\gamma_1)^2 = $ `{(g0*g1)*(g0*g1)}`"),
        mo.md(f"- $(\\gamma_0 \\gamma_2)^2 = $ `{(g0*g2)*(g0*g2)}`"),
        mo.md(f"- $(\\gamma_0 \\gamma_3)^2 = $ `{(g0*g3)*(g0*g3)}`"),
        mo.md(""),
        mo.md("**Rotation generators** (square to $-1$):"),
        mo.md(f"- $(\\gamma_1 \\gamma_2)^2 = $ `{(g1*g2)*(g1*g2)}`"),
        mo.md(f"- $(\\gamma_1 \\gamma_3)^2 = $ `{(g1*g3)*(g1*g3)}`"),
        mo.md(f"- $(\\gamma_2 \\gamma_3)^2 = $ `{(g2*g3)*(g2*g3)}`"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Interactive Lorentz Boost

    A boost in the $\\gamma_0 \\gamma_1$ plane with rapidity $\\varphi$:

    $$R = \\cosh(\\varphi/2) + \\sinh(\\varphi/2)\\, \\gamma_0 \\gamma_1$$

    The sandwich product $R \\gamma_0 \\tilde{R}$ boosts the rest-frame
    timelike vector into a moving frame.
    """)
    return


@app.cell
def _(mo):
    rapidity_slider = mo.ui.slider(
        start=-3.0, stop=3.0, step=0.05, value=0.5,
        label="Rapidity φ",
    )
    rapidity_slider
    return (rapidity_slider,)


@app.cell
def _(g0, g1, grade, mo, np, rapidity_slider, sta, sym):
    _phi = rapidity_slider.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)

    _boosted = _R * g0 * ~_R
    _t, _x = _boosted.vector_part[0], _boosted.vector_part[1]

    # Velocity: v/c = tanh(φ)
    _beta = np.tanh(_phi)
    _gamma_factor = np.cosh(_phi)

    # Symbolic display
    _R_s = sym(_R, "R")
    _g0_s = sym(g0, "\\gamma_0")
    _expr = grade(_R_s * _g0_s * ~_R_s, 1)

    mo.vstack([
        mo.md(f"$\\varphi = {_phi:.2f}$"),
        mo.md(f"$\\beta = v/c = \\tanh(\\varphi) = {_beta:.4f}$"),
        mo.md(f"$\\gamma = \\cosh(\\varphi) = {_gamma_factor:.4f}$"),
        mo.md(f"Symbolic: {_expr.latex(wrap='$')}"),
        mo.md(f"Result: `{_boosted}`"),
        mo.md(f"Components: $t' = {_t:.4f}\\gamma_0,\\; x' = {_x:.4f}\\gamma_1$"),
    ])
    return


@app.cell
def _(mo):
    mo.md("### Boost — Minkowski Diagram")
    return


@app.cell
def _(g0, g1, mo, np, rapidity_slider, sta):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    _phi = rapidity_slider.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)

    # Boost the basis vectors
    _t_prime = _R * g0 * ~_R
    _x_prime = _R * g1 * ~_R

    _tp = _t_prime.vector_part[:2]  # (t, x) components
    _xp = _x_prime.vector_part[:2]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)

    # Light cone
    _s = np.linspace(-3, 3, 100)
    ax.plot(_s, _s, "y-", alpha=0.4, lw=2, label="light cone")
    ax.plot(_s, -_s, "y-", alpha=0.4, lw=2)

    # Rest frame axes
    ax.quiver(0, 0, 0, 2, angles="xy", scale_units="xy", scale=1,
              color="steelblue", width=0.015, alpha=0.4, label="$\\gamma_0$ (rest)")
    ax.quiver(0, 0, 2, 0, angles="xy", scale_units="xy", scale=1,
              color="coral", width=0.015, alpha=0.4, label="$\\gamma_1$ (rest)")

    # Boosted axes
    _scale = 2.0
    ax.quiver(0, 0, _scale * _tp[1], _scale * _tp[0], angles="xy", scale_units="xy", scale=1,
              color="steelblue", width=0.02, label="$\\gamma_0'$ (boosted)")
    ax.quiver(0, 0, _scale * _xp[1], _scale * _xp[0], angles="xy", scale_units="xy", scale=1,
              color="crimson", width=0.02, label="$\\gamma_1'$ (boosted)")

    ax.set_xlabel("x", fontsize=12)
    ax.set_ylabel("t", fontsize=12)
    ax.set_title(f"Minkowski Diagram — φ = {_phi:.2f}", fontsize=14)
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    fig
    return


@app.cell
def _(mo):
    mo.md("""
    ## Interactive Spatial Rotation

    Rotations in STA use spacelike bivectors ($\\gamma_i \\gamma_j$).
    The rotor is $R = \\cos(\\theta/2) - \\sin(\\theta/2)\\, \\gamma_1 \\gamma_2$.
    """)
    return


@app.cell
def _(mo):
    rot_slider = mo.ui.slider(
        start=0, stop=360, step=1, value=45,
        label="θ (degrees)",
    )
    rot_slider
    return (rot_slider,)


@app.cell
def _(g1, g2, grade, mo, np, rot_slider, sta, sym):
    _theta = np.radians(rot_slider.value)
    _R = sta.rotor_from_plane_angle(g1 ^ g2, _theta)
    _rotated = _R * g1 * ~_R

    _R_s = sym(_R, "R")
    _v_s = sym(g1, "\\gamma_1")
    _expr = grade(_R_s * _v_s * ~_R_s, 1)

    _vy, _vz = _rotated.vector_part[1], _rotated.vector_part[2]

    mo.vstack([
        mo.md(f"$\\theta = {rot_slider.value}°$"),
        mo.md(f"Symbolic: {_expr.latex(wrap='$')}"),
        mo.md(f"Result: `{_rotated}`"),
        mo.md(f"$\\gamma_1' = {_vy:.4f}\\gamma_1 + {_vz:.4f}\\gamma_2$"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Electromagnetic Field Bivector

    In STA, the electromagnetic field is a single bivector $F$:

    $$F = \\mathbf{E} + I\\mathbf{B}$$

    where $\\mathbf{E} = E^i \\gamma_i \\gamma_0$ (electric) and
    $I\\mathbf{B}$ encodes the magnetic field via the pseudoscalar.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo, sta):
    # Electric field in x-direction, magnetic field in z-direction
    _E = 2 * g1 * g0
    _B_mag = 3 * g2 * g3  # This is I * (B in z-direction)
    _F = _E + _B_mag

    # F² = E² - B² + 2EBI (Lorentz invariants)
    _F2 = _F * _F

    mo.vstack([
        mo.md(f"Electric field: $E = 2\\gamma_1\\gamma_0$ → `{_E}`"),
        mo.md(f"Magnetic field: $IB = 3\\gamma_2\\gamma_3$ → `{_B_mag}`"),
        mo.md(f"EM bivector: $F = E + IB$ → `{_F}`"),
        mo.md(f"$F^2 = $ `{_F2}`"),
        mo.md(f"Scalar part ($E^2 - B^2$): `{_F2.scalar_part}`"),
        mo.md(f"Pseudoscalar part ($2\\mathbf{{E}} \\cdot \\mathbf{{B}}$): grade-4 of $F^2$"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ### Boosting the EM Field

    Under a Lorentz boost, $F \\to R F \\tilde{R}$. Drag the rapidity
    to see how the electric and magnetic fields mix.
    """)
    return


@app.cell
def _(mo):
    em_rapidity = mo.ui.slider(
        start=-2.0, stop=2.0, step=0.05, value=0.0,
        label="Boost rapidity φ",
    )
    em_rapidity
    return (em_rapidity,)


@app.cell
def _(em_rapidity, g0, g1, g2, g3, mo, np, sta):
    _phi = em_rapidity.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)

    # Original field: E in x, B in z
    _F = 2 * g1 * g0 + 3 * g2 * g3

    # Boost the field
    _F_prime = _R * _F * ~_R

    # Extract components: E' and B' parts
    # Electric: γ_i γ_0 components, Magnetic: γ_i γ_j (i,j spatial) components
    _F2 = _F_prime * _F_prime

    mo.vstack([
        mo.md(f"$\\varphi = {_phi:.2f}$"),
        mo.md(f"Original: $F = $ `{_F}`"),
        mo.md(f"Boosted: $F' = RFR̃ = $ `{_F_prime}`"),
        mo.md(f"$F'^2 = $ `{_F2}` (Lorentz invariant — should not change!)"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Relative Vectors (Pauli Algebra)

    The relative (spatial) vectors are $\\sigma_i = \\gamma_i \\gamma_0$.
    These are bivectors in STA but behave like the Pauli matrices:
    $\\sigma_i^2 = 1$, $\\sigma_i \\sigma_j = -\\sigma_j \\sigma_i$ for $i \\neq j$.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo):
    _s1 = g1 * g0
    _s2 = g2 * g0
    _s3 = g3 * g0

    mo.vstack([
        mo.md(f"$\\sigma_1 = \\gamma_1\\gamma_0 = $ `{_s1}`"),
        mo.md(f"$\\sigma_2 = \\gamma_2\\gamma_0 = $ `{_s2}`"),
        mo.md(f"$\\sigma_3 = \\gamma_3\\gamma_0 = $ `{_s3}`"),
        mo.md(""),
        mo.md(f"$\\sigma_1^2 = $ `{_s1 * _s1}`"),
        mo.md(f"$\\sigma_1 \\sigma_2 = $ `{_s1 * _s2}` (bivector in spatial plane)"),
        mo.md(f"$\\sigma_1 \\sigma_2 \\sigma_3 = $ `{_s1 * _s2 * _s3}` (= $I$, the pseudoscalar)"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Symbolic Identities

    Verify key STA identities using the symbolic layer.
    """)
    return


@app.cell
def _(g0, g1, g2, mo, np, simplify, sta, sym):
    _R = sym(sta.rotor_from_plane_angle(g1 ^ g2, np.pi / 3), "R")
    _v = sym(g0, "p")
    _F = sym(2 * g1 * g0 + 3 * g2 * g3, "F")

    _identities = [
        ("R̃R̃ = R", simplify(~~_R)),
        ("RR̃ = 1", simplify(_R * ~_R)),
        ("F + F = 2F", simplify(_F + _F)),
    ]
    mo.vstack([
        mo.md(f"- `{name}` → {result.latex(wrap='$')}")
        for name, result in _identities
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Composition of Boosts

    Two successive boosts along different axes don't commute —
    their composition includes a spatial rotation (Thomas-Wigner rotation).
    """)
    return


@app.cell
def _(g0, g1, g2, mo, np, sta):
    _phi1, _phi2 = 0.8, 0.6

    _R1 = sta.scalar(np.cosh(_phi1 / 2)) + np.sinh(_phi1 / 2) * (g0 * g1)
    _R2 = sta.scalar(np.cosh(_phi2 / 2)) + np.sinh(_phi2 / 2) * (g0 * g2)

    _R12 = _R1 * _R2  # boost x then boost y
    _R21 = _R2 * _R1  # boost y then boost x

    # The difference is a spatial rotation
    _diff = _R12 * ~_R21

    mo.vstack([
        mo.md(f"Boost x (φ={_phi1}), then boost y (φ={_phi2}):"),
        mo.md(f"$R_1 R_2 = $ `{_R12}`"),
        mo.md(f"$R_2 R_1 = $ `{_R21}`"),
        mo.md(f"$(R_1 R_2)(R_2 R_1)^{{\\sim}} = $ `{_diff}`"),
        mo.md("This residual rotor is the **Thomas-Wigner rotation**."),
        mo.md(f"It has a spatial bivector component ($\\gamma_1\\gamma_2$), confirming it's a pure rotation."),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Velocity Addition

    Drag two rapidity sliders to compose boosts along the x-axis.
    Rapidities add: $\\varphi_{\\text{total}} = \\varphi_1 + \\varphi_2$.
    """)
    return


@app.cell
def _(mo):
    phi1_slider = mo.ui.slider(start=-2, stop=2, step=0.05, value=0.5, label="φ₁")
    phi2_slider = mo.ui.slider(start=-2, stop=2, step=0.05, value=0.3, label="φ₂")
    mo.hstack([phi1_slider, phi2_slider])
    return (phi1_slider, phi2_slider)


@app.cell
def _(g0, g1, mo, np, phi1_slider, phi2_slider, sta):
    _p1, _p2 = phi1_slider.value, phi2_slider.value

    _R1 = sta.scalar(np.cosh(_p1 / 2)) + np.sinh(_p1 / 2) * (g0 * g1)
    _R2 = sta.scalar(np.cosh(_p2 / 2)) + np.sinh(_p2 / 2) * (g0 * g1)
    _R_total = _R1 * _R2

    _v1 = np.tanh(_p1)
    _v2 = np.tanh(_p2)
    _v_einstein = (_v1 + _v2) / (1 + _v1 * _v2)
    _v_total = np.tanh(_p1 + _p2)

    _boosted = _R_total * g0 * ~_R_total

    mo.vstack([
        mo.md(f"$\\varphi_1 = {_p1:.2f}$ → $v_1/c = {_v1:.4f}$"),
        mo.md(f"$\\varphi_2 = {_p2:.2f}$ → $v_2/c = {_v2:.4f}$"),
        mo.md(f"Einstein addition: $(v_1 + v_2)/(1 + v_1 v_2) = {_v_einstein:.4f}$"),
        mo.md(f"Rapidity addition: $\\tanh(\\varphi_1 + \\varphi_2) = {_v_total:.4f}$"),
        mo.md(f"Composed rotor applied to $\\gamma_0$: `{_boosted}`"),
    ])
    return


@app.cell
def _(mo):
    mo.md("### Velocity Addition Plot")
    return


@app.cell
def _(mo, np, phi1_slider, phi2_slider):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    _p1, _p2 = phi1_slider.value, phi2_slider.value
    _v1, _v2 = np.tanh(_p1), np.tanh(_p2)
    _v_rel = (_v1 + _v2) / (1 + _v1 * _v2)
    _v_classical = _v1 + _v2

    # Plot velocity addition curves
    _v_range = np.linspace(-0.99, 0.99, 200)

    fig, ax = plt.subplots(figsize=(6, 4))

    # For fixed v1, plot v_total vs v2
    _v_einstein = (_v1 + _v_range) / (1 + _v1 * _v_range)
    _v_class = _v1 + _v_range

    ax.plot(_v_range, _v_einstein, "b-", lw=2, label=f"Einstein (v₁={_v1:.2f})")
    ax.plot(_v_range, _v_class, "r--", lw=1.5, alpha=0.5, label="Classical (v₁+v₂)")
    ax.axhline(1, color="gold", lw=2, alpha=0.5, label="c (speed limit)")
    ax.axhline(-1, color="gold", lw=2, alpha=0.5)

    # Mark current point
    ax.plot(_v2, _v_rel, "ko", ms=8, zorder=5)
    ax.annotate(f"  ({_v2:.2f}, {_v_rel:.2f})", (_v2, _v_rel), fontsize=10)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("v₂ / c", fontsize=12)
    ax.set_ylabel("v_total / c", fontsize=12)
    ax.set_title("Relativistic Velocity Addition", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig
    return


if __name__ == "__main__":
    app.run()
