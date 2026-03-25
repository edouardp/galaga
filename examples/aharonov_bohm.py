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

    return (mo,)


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, scalar, grade, exp, sandwich
    import galaga_marimo as gm

    return Algebra, gm, np, plt, scalar


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # The Aharonov–Bohm Effect in Spacetime Algebra

    The Aharonov–Bohm effect demonstrates that the electromagnetic **potential**
    $A$ has physical consequences even in regions where the field $F = 0$. A charged
    particle acquires a phase shift from the potential alone.

    In the STA formulation, this phase factor is a unit even multivector generated
    by the pseudoscalar $I$. The role of the imaginary unit $i$ in the conventional
    phase $e^{{i\\Delta\\phi}}$ is played by the STA pseudoscalar — no external complex
    scalars are needed.

    $$\\psi \\to \\psi' = e^{{-I\\,\\Delta\\phi/2}} \\, \\psi, \\qquad \\Delta\\phi = \\frac{{q}}{{\\hbar}} \\oint A \\cdot dl = \\frac{{q \\Phi_B}}{{\\hbar}}$$

    where $\\Phi_B$ is the magnetic flux enclosed by the path.

    *This notebook uses natural units ($\\hbar = 1$, $q = 1$) throughout, so
    $\\Delta\\phi = \\Phi_B$ numerically. The slider values are in units of $\\pi$.*
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Algebra

    We work in the Spacetime Algebra Cl(1,3). The pseudoscalar $I = e_0 e_1 e_2 e_3$
    squares to $-1$, just like the imaginary unit $i$ in conventional QM. In 4D STA,
    $I$ commutes with even-grade multivectors and anticommutes with odd-grade ones —
    this is what makes it suitable as a U(1) phase generator for spinors (which are
    even multivectors in STA).
    """)
    return


@app.cell
def _(Algebra, gm, scalar):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors()
    I = sta.I

    gm.md(t"""**Spacetime Algebra** Cl(1,3):
    - {I} $= e_0 e_1 e_2 e_3$ , $\\quad I^2$ = {scalar(I * I):text} (plays the role of $i$ in QM)
    - $I$ commutes with even multivectors, anticommutes with odd
    - $I$ generates internal U(1) phase rotations: $e^{{I\\phi}}$ replaces $e^{{i\\phi}}$""")
    return I, sta


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## U(1) Phase as an Internal Rotation

    In conventional QM, a phase factor is $e^{{i\\phi}}$. In STA, the
    pseudoscalar $I$ replaces $i$, and the phase factor becomes a unit even
    multivector:

    $$R(\\phi) = e^{{-\\phi I/2}} = \\cos(\\phi/2) - \\sin(\\phi/2)\\,I$$

    This is an **internal phase rotation**, not a spacetime rotation of the
    particle trajectory. It leaves the spin vector unchanged but shifts the
    overall phase of the spinor representation.
    """)
    return


@app.cell
def _(I, gm, np, scalar, sta):
    _phases = [0, np.pi / 4, np.pi / 2, np.pi, 2 * np.pi]
    _rows = []
    for phi in _phases:
        R = sta.rotor(I, radians=phi)
        RR = scalar(R * ~R)
        _rows.append(f"| ${phi / np.pi:.2f}\\pi$ | {R.latex(wrap='$')} | ${RR:.4f}$ |")

    gm.md(t"""| Phase $\\phi$ | $R(\\phi) = e^{{-\\phi I/2}}$ | $R\\tilde{{R}}$ |
    |---|---|---|
    {"\n".join(_rows):text}

    Note: at $\\phi = 2\\pi$ the factor is $-1$ (the spinor sign flip familiar from
    the SU(2) double cover). The **observable** interference depends on the
    *relative* phase between paths, not the global sign.""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Aharonov–Bohm Setup

    In the idealized AB geometry, an infinitely long solenoid confines all
    magnetic flux $\\Phi_B$ to its interior. Two electron paths pass on opposite
    sides and recombine at a detector. The electron travels only through regions
    where $F = 0$, but the potential $A$ is nonzero.

    Each path accumulates a phase from the line integral of $A$:
    - Path 1 (above): $\\phi_1 = \\frac{{q}}{{\\hbar}} \\int_1 A \\cdot dl$
    - Path 2 (below): $\\phi_2 = \\frac{{q}}{{\\hbar}} \\int_2 A \\cdot dl$

    The phase difference is (by Stokes' theorem):
    $$\\Delta\\phi = \\frac{{q}}{{\\hbar}} \\oint A \\cdot dl = \\frac{{q \\Phi_B}}{{\\hbar}}$$

    In GA, each path produces a U(1) phase factor, and the interference depends
    on the relative factor $R_1 \\tilde{{R}}_2$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    flux_slider = mo.ui.slider(
        start=0.0, stop=4.0, step=0.01, value=1.0,
        label="Δφ = qΦ_B/ℏ (units of π)"
    )
    flux_slider
    return (flux_slider,)


@app.cell
def _(I, flux_slider, gm, mo, np, sta):
    _delta_phi = flux_slider.value * np.pi  # total phase difference

    # Phase accumulated by each path (symmetric split)
    _phi1 = _delta_phi / 2    # path above
    _phi2 = -_delta_phi / 2   # path below

    _R1 = sta.rotor(I, radians=_phi1)
    _R2 = sta.rotor(I, radians=_phi2)

    # Relative phase factor
    _R_rel = _R1 * ~_R2

    # Interference: P = (1 + cos(Δφ)) / 2
    _prob = (1 + np.cos(_delta_phi)) / 2

    mo.vstack([
        gm.md(t"$\\Delta\\phi = {flux_slider.value:.2f}\\pi$"),
        gm.md(t"Path 1 phase factor: {_R1}"),
        gm.md(t"Path 2 phase factor: {_R2}"),
        gm.md(t"Relative factor $R_1 \\tilde{{R}}_2$: {_R_rel}"),
        gm.md(t"**Interference: $P = \\frac{{1 + \\cos(\\Delta\\phi)}}{{2}} = {_prob:.4f}$**"),
    ])
    return


@app.cell(hide_code=True)
def _(flux_slider, np, plt):
    _dphi_range = np.linspace(0, 4 * np.pi, 500)
    _prob_curve = (1 + np.cos(_dphi_range)) / 2
    _current_dphi = flux_slider.value * np.pi
    _current_prob = (1 + np.cos(_current_dphi)) / 2

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_dphi_range / np.pi, _prob_curve, "crimson", lw=2.5)
    _ax.plot(_current_dphi / np.pi, _current_prob, "ko", ms=10, zorder=5)
    _ax.axhline(0.5, color="gray", ls=":", alpha=0.3)
    _ax.set_xlabel("$\\Delta\\phi = q\\Phi_B/\\hbar$ (units of $\\pi$)", fontsize=12)
    _ax.set_ylabel("Detection probability $P$", fontsize=12)
    _ax.set_title("Aharonov\\u2013Bohm Interference Pattern", fontsize=13)
    _ax.set_xlim(0, 4)
    _ax.set_ylim(-0.05, 1.05)
    _ax.grid(True, alpha=0.2)

    # Mark key points
    for n, label in [(0, "constructive"), (1, "destructive"), (2, "constructive")]:
        _ax.annotate(label, xy=(n, (1 + np.cos(n * np.pi)) / 2),
                     xytext=(n + 0.15, 0.85 if n % 2 == 0 else 0.15),
                     fontsize=9, alpha=0.6,
                     arrowprops=dict(arrowstyle="->", alpha=0.4))

    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Geometric Picture

    The diagram below shows the two paths around the solenoid. Each path
    accumulates an internal U(1) phase factor generated by $I$.
    """)
    return


@app.cell(hide_code=True)
def _(flux_slider, np, plt):
    _fig, _ax = plt.subplots(figsize=(6, 6))

    # Solenoid (center)
    _theta = np.linspace(0, 2 * np.pi, 100)
    _ax.fill(0.3 * np.cos(_theta), 0.3 * np.sin(_theta), color="steelblue", alpha=0.3)
    _ax.text(0, 0, "$\\Phi_B$", ha="center", va="center", fontsize=14, color="steelblue")

    # Path 1 (above)
    _t1 = np.linspace(0, np.pi, 100)
    _ax.plot(1.5 * np.cos(_t1), 1.5 * np.sin(_t1), "crimson", lw=2.5, label="Path 1")
    _ax.annotate("", xy=(-0.1, 1.5), xytext=(0.1, 1.5),
                 arrowprops=dict(arrowstyle="->", color="crimson", lw=2))

    # Path 2 (below)
    _t2 = np.linspace(np.pi, 2 * np.pi, 100)
    _ax.plot(1.5 * np.cos(_t2), 1.5 * np.sin(_t2), "seagreen", lw=2.5, label="Path 2")
    _ax.annotate("", xy=(0.1, -1.5), xytext=(-0.1, -1.5),
                 arrowprops=dict(arrowstyle="->", color="seagreen", lw=2))

    # Source and detector
    _ax.plot(-1.5, 0, "ks", ms=12)
    _ax.text(-1.5, -0.3, "source", ha="center", fontsize=10)
    _ax.plot(1.5, 0, "k^", ms=12)
    _ax.text(1.5, -0.3, "detector", ha="center", fontsize=10)

    # Phase labels
    _phi_val = flux_slider.value * np.pi / 2
    _ax.text(0, 1.8, f"$\\phi_1 = +{_phi_val / np.pi:.2f}\\pi$",
             ha="center", fontsize=11, color="crimson")
    _ax.text(0, -1.8, f"$\\phi_2 = -{_phi_val / np.pi:.2f}\\pi$",
             ha="center", fontsize=11, color="seagreen")

    _ax.set_xlim(-2.5, 2.5)
    _ax.set_ylim(-2.5, 2.5)
    _ax.set_aspect("equal")
    _ax.legend(loc="upper right", fontsize=10)
    _ax.set_title("Aharonov\\u2013Bohm: Two Paths Around a Solenoid", fontsize=13)
    _ax.grid(True, alpha=0.1)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## QM ↔ STA Rosetta Stone

    | Conventional QM | STA equivalent |
    |---|---|
    | Imaginary unit $i$ | Pseudoscalar $I = e_0 e_1 e_2 e_3$ |
    | Phase factor $e^{{i\\Delta\\phi/2}}$ | Even multivector $e^{{I\\Delta\\phi/2}}$ |
    | Normalisation $\\langle\\psi\\|\\psi\\rangle = 1$ | $\\psi\\tilde\\psi = 1$ |
    | Relative phase $\\psi_2 = e^{{i\\Delta\\phi}}\\psi_1$ | $\\psi_2 = e^{{I\\Delta\\phi}}\\psi_1$ |
    | Probability $\\|\\psi_1 + \\psi_2\\|^2$ | $\\langle (\\psi_1 + \\psi_2)(\\widetilde{{\\psi_1 + \\psi_2}}) \\rangle_0$ |

    For the even-multivector spinor used here, the reverse $\\tilde\\psi$ plays the
    role analogous to complex conjugation / Hermitian adjoint in ordinary QM,
    so normalisation is written as $\\psi\\tilde\\psi = 1$.

    Note: the AB phase is an **internal phase rotation** generated by $I$, not a
    spacetime rotation of the trajectory. A GA reader seeing $e^{{I\\phi}}$ should
    think "U(1) phase", not "sandwich product on vectors".
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Interference from the Geometric Product

    The interference formula isn't imported from QM — it emerges directly from
    the algebra. If the two paths produce phase factors $\\psi_1$ and $\\psi_2$,
    the combined amplitude is $\\Psi = \\psi_1 + \\psi_2$, and the detection
    probability is the scalar part of $\\Psi\\tilde\\Psi$:

    $$P = \\langle \\Psi\\tilde\\Psi \\rangle_0 = \\langle (\\psi_1 + \\psi_2)(\\tilde\\psi_1 + \\tilde\\psi_2) \\rangle_0$$
    """)
    return


@app.cell
def _(I, flux_slider, gm, np, scalar, sta):
    _delta_phi = flux_slider.value * np.pi

    _psi1 = sta.rotor(I, radians=_delta_phi / 2)
    _psi2 = sta.rotor(I, radians=-_delta_phi / 2)

    _Psi = _psi1 + _psi2
    _P_ga = scalar(_Psi * ~_Psi) / 2  # normalised (each path has unit amplitude)
    _P_formula = (1 + np.cos(_delta_phi)) / 2

    gm.md(t"""$\\psi_1 = {_psi1}, \\quad \\psi_2 = {_psi2}$

    $\\Psi = \\psi_1 + \\psi_2 = {_Psi}$

    $\\langle \\Psi\\tilde\\Psi \\rangle_0 / 2 = {_P_ga:.6f}$

    $\\frac{{1 + \\cos(\\Delta\\phi)}}{{2}} = {_P_formula:.6f}$ ✓

    The cosine comes from the geometric product — the cross terms
    $\\langle \\psi_1 \\tilde\\psi_2 + \\psi_2 \\tilde\\psi_1 \\rangle_0$
    give $2\\cos(\\Delta\\phi)$.""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Key Insight

    In the idealized setup, the electromagnetic field $F = 0$ everywhere outside
    the solenoid. Yet the potential $A$ is nonzero, and the phase difference
    $\\Delta\\phi = q\\Phi_B/\\hbar$ produces observable interference.

    In the STA formulation:
    - The phase factor is a unit even multivector $e^{{-I\\,\\Delta\\phi/2}}$, represented
      without introducing an external complex scalar — the role of $i$ is played
      by the STA pseudoscalar $I$
    - The generator $I$ produces an **internal phase rotation**, not a spacetime
      rotation of the particle trajectory
    - The interference pattern is $P = \\frac{{1 + \\cos(\\Delta\\phi)}}{{2}}$
    - The spinor sign flip at $\\Delta\\phi = 2\\pi$ is the SU(2) double cover;
      the **observable** is the relative phase between paths
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
