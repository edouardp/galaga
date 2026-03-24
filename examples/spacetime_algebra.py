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
    import numpy as np
    from ga import Algebra
    from ga.symbolic import (
        sym, gp, op, grade, reverse, involute, conjugate,
        dual, norm, unit, inverse, sandwich, simplify,
        even_grades, odd_grades,
    )
    return (
        Algebra, mo, np,
        sym, gp, op, grade, reverse, involute, conjugate,
        dual, norm, unit, inverse, sandwich, simplify,
        even_grades, odd_grades,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Spacetime Algebra (STA)

    The Spacetime Algebra is $\text{Cl}(1,3)$ — one timelike dimension
    ($\gamma_0^2 = +1$) and three spacelike ($\gamma_i^2 = -1$).
    It encodes special relativity, electromagnetism, and the Dirac equation.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors()
    return sta, g0, g1, g2, g3


# ── Basis vectors ──────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md("## Basis Vectors and Signature")
    return


@app.cell
def _(g0, g1, g2, g3, mo, sta):
    mo.vstack([
        mo.hstack([mo.md("Timelike:"), g0 * g0]),
        mo.hstack([mo.md("Spacelike:"), g1 * g1, g2 * g2, g3 * g3]),
        mo.hstack([mo.md("Pseudoscalar:"), sta.I]),
        mo.hstack([mo.md("$I^2 =$"), sta.I * sta.I]),
    ])
    return


# ── Bivectors ──────────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Bivectors — Boosts and Rotations

    - **Timelike bivectors** ($\gamma_0 \gamma_i$): generate Lorentz boosts, square to $+1$
    - **Spacelike bivectors** ($\gamma_i \gamma_j$): generate spatial rotations, square to $-1$
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo):
    mo.vstack([
        mo.md("**Boost generators:**"),
        mo.hstack([g0 * g1, mo.md("squared ="), (g0 * g1) * (g0 * g1)]),
        mo.hstack([g0 * g2, mo.md("squared ="), (g0 * g2) * (g0 * g2)]),
        mo.hstack([g0 * g3, mo.md("squared ="), (g0 * g3) * (g0 * g3)]),
        mo.md("**Rotation generators:**"),
        mo.hstack([g1 * g2, mo.md("squared ="), (g1 * g2) * (g1 * g2)]),
        mo.hstack([g1 * g3, mo.md("squared ="), (g1 * g3) * (g1 * g3)]),
        mo.hstack([g2 * g3, mo.md("squared ="), (g2 * g3) * (g2 * g3)]),
    ])
    return


# ── Interactive Lorentz Boost ──────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Interactive Lorentz Boost

    A boost in the $\gamma_0 \gamma_1$ plane with rapidity $\varphi$:
    $$R = \cosh(\varphi/2) + \sinh(\varphi/2)\, \gamma_0 \gamma_1$$
    """)
    return


@app.cell
def _(mo):
    rapidity = mo.ui.slider(start=-3.0, stop=3.0, step=0.05, value=0.5, label="Rapidity φ")
    rapidity
    return (rapidity,)


@app.cell
def _(g0, g1, grade, mo, np, rapidity, sta, sym):
    _phi = rapidity.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)
    _boosted = _R * g0 * ~_R

    _R_s = sym(_R, "R")
    _g0_s = sym(g0, r"\gamma_0")
    _expr = grade(_R_s * _g0_s * ~_R_s, 1)

    mo.vstack([
        mo.md(f"$\\varphi = {_phi:.2f}, \\quad \\beta = {np.tanh(_phi):.4f}, \\quad \\gamma = {np.cosh(_phi):.4f}$"),
        mo.md(f"Symbolic: {_expr.latex(wrap='$')}"),
        mo.hstack([mo.md("Result:"), _boosted]),
    ])
    return


@app.cell
def _(mo):
    mo.md("### Minkowski Diagram")
    return


@app.cell
def _(g0, g1, np, rapidity, sta):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    _phi = rapidity.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)

    _tp = (_R * g0 * ~_R).vector_part[:2]
    _xp = (_R * g1 * ~_R).vector_part[:2]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

    # Light cone
    _s = np.linspace(-3, 3, 100)
    ax.plot(_s, _s, "y-", alpha=0.4, lw=2, label="light cone")
    ax.plot(_s, -_s, "y-", alpha=0.4, lw=2)

    # Rest frame
    ax.quiver(0, 0, 0, 2, angles="xy", scale_units="xy", scale=1,
              color="steelblue", width=0.015, alpha=0.4, label=r"$\gamma_0$ (rest)")
    ax.quiver(0, 0, 2, 0, angles="xy", scale_units="xy", scale=1,
              color="coral", width=0.015, alpha=0.4, label=r"$\gamma_1$ (rest)")

    # Boosted frame
    ax.quiver(0, 0, 2 * _tp[1], 2 * _tp[0], angles="xy", scale_units="xy", scale=1,
              color="steelblue", width=0.02, label=r"$\gamma_0'$ (boosted)")
    ax.quiver(0, 0, 2 * _xp[1], 2 * _xp[0], angles="xy", scale_units="xy", scale=1,
              color="crimson", width=0.02, label=r"$\gamma_1'$ (boosted)")

    ax.set_xlabel("x")
    ax.set_ylabel("t")
    ax.set_title(f"φ = {_phi:.2f}")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    fig
    return


# ── Interactive Spatial Rotation ───────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Spatial Rotation

    Rotations use spacelike bivectors: $R = \cos(\theta/2) - \sin(\theta/2)\, \gamma_1 \gamma_2$
    """)
    return


@app.cell
def _(mo):
    rot_angle = mo.ui.slider(start=0, stop=360, step=1, value=45, label="θ (degrees)")
    rot_angle
    return (rot_angle,)


@app.cell
def _(g1, g2, grade, mo, np, rot_angle, sta, sym):
    _theta = np.radians(rot_angle.value)
    _R = sta.rotor_from_plane_angle(g1 ^ g2, _theta)
    _rotated = _R * g1 * ~_R

    _expr = grade(sym(_R, "R") * sym(g1, r"\gamma_1") * ~sym(_R, "R"), 1)

    mo.vstack([
        mo.md(f"$\\theta = {rot_angle.value}°$"),
        mo.md(f"Symbolic: {_expr.latex(wrap='$')}"),
        mo.hstack([mo.md("Result:"), _rotated]),
    ])
    return


# ── Electromagnetic Field ──────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Electromagnetic Field Bivector

    In STA, the EM field is a single bivector $F = \mathbf{E} + I\mathbf{B}$.
    The Lorentz invariants are encoded in $F^2$: scalar part = $E^2 - B^2$,
    pseudoscalar part = $2\mathbf{E} \cdot \mathbf{B}$.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo):
    _E = 2 * g1 * g0
    _B = 3 * g2 * g3
    _F = _E + _B
    _F2 = _F * _F

    mo.vstack([
        mo.hstack([mo.md("$E =$"), _E]),
        mo.hstack([mo.md("$IB =$"), _B]),
        mo.hstack([mo.md("$F =$"), _F]),
        mo.hstack([mo.md("$F^2 =$"), _F2]),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Boosting the EM Field

    Under a Lorentz boost, $F \to R F \tilde{R}$. The invariant $F^2$ should not change.
    """)
    return


@app.cell
def _(mo):
    em_boost = mo.ui.slider(start=-2.0, stop=2.0, step=0.05, value=0.0, label="Boost rapidity φ")
    em_boost
    return (em_boost,)


@app.cell
def _(em_boost, g0, g1, g2, g3, mo, np, sta):
    _phi = em_boost.value
    _R = sta.scalar(np.cosh(_phi / 2)) + np.sinh(_phi / 2) * (g0 * g1)
    _F = 2 * g1 * g0 + 3 * g2 * g3
    _Fp = _R * _F * ~_R
    _Fp2 = _Fp * _Fp

    mo.vstack([
        mo.md(f"$\\varphi = {_phi:.2f}$"),
        mo.hstack([mo.md("$F =$"), _F]),
        mo.hstack([mo.md("$F' = R F \\tilde{{R}} =$"), _Fp]),
        mo.hstack([mo.md("$F'^2 =$"), _Fp2, mo.md("(Lorentz invariant)")]),
    ])
    return


# ── Pauli Algebra ──────────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Relative Vectors (Pauli Algebra)

    The relative vectors $\sigma_i = \gamma_i \gamma_0$ are bivectors in STA
    but behave like the Pauli matrices: $\sigma_i^2 = 1$, anticommuting.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, mo):
    _s1, _s2, _s3 = g1 * g0, g2 * g0, g3 * g0

    mo.vstack([
        mo.hstack([mo.md("$\\sigma_1 =$"), _s1]),
        mo.hstack([mo.md("$\\sigma_2 =$"), _s2]),
        mo.hstack([mo.md("$\\sigma_3 =$"), _s3]),
        mo.md(""),
        mo.hstack([mo.md("$\\sigma_1^2 =$"), _s1 * _s1]),
        mo.hstack([mo.md("$\\sigma_1 \\sigma_2 =$"), _s1 * _s2]),
        mo.hstack([mo.md("$\\sigma_1 \\sigma_2 \\sigma_3 =$"), _s1 * _s2 * _s3, mo.md("(= pseudoscalar)")]),
    ])
    return


# ── Thomas-Wigner Rotation ────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Thomas-Wigner Rotation

    Two boosts along different axes don't commute — their composition
    includes a spatial rotation.
    """)
    return


@app.cell
def _(g0, g1, g2, mo, np, sta):
    _R1 = sta.scalar(np.cosh(0.4)) + np.sinh(0.4) * (g0 * g1)
    _R2 = sta.scalar(np.cosh(0.3)) + np.sinh(0.3) * (g0 * g2)

    _R12 = _R1 * _R2
    _R21 = _R2 * _R1
    _diff = _R12 * ~_R21

    mo.vstack([
        mo.hstack([mo.md("$R_1 R_2 =$"), _R12]),
        mo.hstack([mo.md("$R_2 R_1 =$"), _R21]),
        mo.hstack([mo.md("$(R_1 R_2)(R_2 R_1)^{\\sim} =$"), _diff]),
        mo.md(r"The residual rotor has a $\gamma_1 \gamma_2$ component — a **Thomas-Wigner rotation**."),
    ])
    return


# ── Velocity Addition ──────────────────────────────────────────


@app.cell
def _(mo):
    mo.md(r"""
    ## Relativistic Velocity Addition

    Collinear boosts compose by adding rapidities: $\varphi_\text{total} = \varphi_1 + \varphi_2$.
    Velocities add via Einstein's formula: $v = (v_1 + v_2)/(1 + v_1 v_2)$.
    """)
    return


@app.cell
def _(mo):
    phi1 = mo.ui.slider(start=-2, stop=2, step=0.05, value=0.5, label="φ₁")
    phi2 = mo.ui.slider(start=-2, stop=2, step=0.05, value=0.3, label="φ₂")
    mo.hstack([phi1, phi2])
    return (phi1, phi2)


@app.cell
def _(g0, g1, mo, np, phi1, phi2, sta):
    _p1, _p2 = phi1.value, phi2.value
    _v1, _v2 = np.tanh(_p1), np.tanh(_p2)
    _v_einstein = (_v1 + _v2) / (1 + _v1 * _v2)

    _R1 = sta.scalar(np.cosh(_p1 / 2)) + np.sinh(_p1 / 2) * (g0 * g1)
    _R2 = sta.scalar(np.cosh(_p2 / 2)) + np.sinh(_p2 / 2) * (g0 * g1)
    _boosted = _R1 * _R2 * g0 * ~_R2 * ~_R1

    mo.vstack([
        mo.md(f"$v_1/c = \\tanh({_p1:.2f}) = {_v1:.4f}$"),
        mo.md(f"$v_2/c = \\tanh({_p2:.2f}) = {_v2:.4f}$"),
        mo.md(f"$v_{{\\text{{total}}}}/c = {_v_einstein:.4f}$"),
        mo.hstack([mo.md("Composed boost on $\\gamma_0$:"), _boosted]),
    ])
    return


@app.cell
def _(mo):
    mo.md("### Velocity Addition Plot")
    return


@app.cell
def _(np, phi1, phi2):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    _v1, _v2 = np.tanh(phi1.value), np.tanh(phi2.value)
    _v_rel = (_v1 + _v2) / (1 + _v1 * _v2)

    _vr = np.linspace(-0.99, 0.99, 200)
    _v_ein = (_v1 + _vr) / (1 + _v1 * _vr)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(_vr, _v_ein, "b-", lw=2, label=f"Einstein ($v_1 = {_v1:.2f}$)")
    ax.plot(_vr, _v1 + _vr, "r--", lw=1.5, alpha=0.5, label="Classical")
    ax.axhline(1, color="gold", lw=2, alpha=0.5, label="$c$")
    ax.axhline(-1, color="gold", lw=2, alpha=0.5)
    ax.plot(_v2, _v_rel, "ko", ms=8, zorder=5)
    ax.annotate(f"  ({_v2:.2f}, {_v_rel:.2f})", (_v2, _v_rel), fontsize=10)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("$v_2 / c$")
    ax.set_ylabel("$v_{total} / c$")
    ax.set_title("Relativistic Velocity Addition")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig
    return


# ── Symbolic Identities ───────────────────────────────────────


@app.cell
def _(mo):
    mo.md("## Symbolic Identities")
    return


@app.cell
def _(g0, g1, g2, g3, mo, np, simplify, sta, sym):
    _R = sym(sta.rotor_from_plane_angle(g1 ^ g2, np.pi / 3), "R")
    _v = sym(g0, "p")
    _F = sym(2 * g1 * g0 + 3 * g2 * g3, "F")

    _rules = [
        ("Double reverse: ~~R", simplify(~~_R)),
        ("Rotor normalization: R~R", simplify(_R * ~_R)),
        ("Collection: F + F", simplify(_F + _F)),
    ]
    mo.vstack([
        mo.md(f"- {name} → {result.latex(wrap='$')}")
        for name, result in _rules
    ])
    return


if __name__ == "__main__":
    app.run()
