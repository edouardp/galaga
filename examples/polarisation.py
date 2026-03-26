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

    from ga import Algebra, gp, scalar, norm, unit, exp
    from ga.symbolic import simplify
    import galaga_marimo as gm

    return Algebra, exp, gm, gp, matplotlib, norm, np, plt, scalar, simplify, unit


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Polarisation Optics with Geometric Algebra

    Light polarisation lives in a 2D transverse plane. A polariser is a
    **projector** — it keeps the component of the electric field along its
    axis and discards the rest. GA expresses this cleanly without matrices.
    """)
    return


# ============================================================
# Setup
# ============================================================


@app.cell
def _(Algebra):
    alg = Algebra((1, 1))
    e1, e2 = alg.basis_vectors(lazy=True)
    return alg, e1, e2


@app.cell(hide_code=True)
def _(e1, e2, gm):
    gm.md(t"""
    ## The Transverse Plane

    Basis: {e1} = horizontal, {e2} = vertical.

    A polarisation state is a unit vector in this plane.
    """)
    return


# ============================================================
# Polariser as projector
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Polariser = Projector

    An ideal linear polariser along unit axis $a$ maps a field $E$ to:

    $$P_a(E) = (E \\cdot a)\\,a$$

    In GA, this is equivalently:

    $$P_a(E) = \\frac{{1}}{{2}}(E + aEa)$$

    because $aEa$ reflects $E$ in the axis $a$, and averaging with the
    original keeps only the parallel component.
    """)
    return


@app.cell
def _(alg, gp, scalar):
    def polarise(E, a):
        """Apply ideal linear polariser along unit axis a to field E."""
        return scalar(gp(E, a)) * a

    def polarise_ga(E, a):
        """GA form: P_a(E) = ½(E + aEa)."""
        return 0.5 * (E + a * E * a)

    return polarise, polarise_ga


# ============================================================
# Classic demo: H blocks V
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## H Blocks V

    Horizontal light through a vertical polariser → nothing.
    """)
    return


@app.cell
def _(e1, e2, gm, norm, polarise):
    _H = e1.eval()
    _V = e2.eval()

    _E0 = _H  # horizontally polarised
    _E1 = polarise(_E0, _V)

    _intensity = norm(_E1) ** 2

    gm.md(t"""
    Start: $E_0 = $ {_H}

    After vertical polariser: $E_1 = P_V(E_0) = $ {_E1}

    Intensity: $|E_1|^2 = $ {_intensity}

    **Completely blocked** — as expected.
    """)
    return


# ============================================================
# Three-polariser trick
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Three-Polariser Trick

    Insert a 45° polariser between H and V — now light gets through!
    """)
    return


@app.cell
def _(e1, e2, gm, norm, np, polarise, unit):
    _H = e1.eval()
    _V = e2.eval()
    _D = unit(e1.eval() + e2.eval())  # 45° diagonal

    _E0 = _H
    _E1 = polarise(_E0, _D)
    _E2 = polarise(_E1, _V)

    _I1 = norm(_E1) ** 2
    _I2 = norm(_E2) ** 2

    gm.md(t"""
    Start: $E_0 = $ {_H}

    After 45° polariser: $E_1 = P_D(E_0) = $ {_E1}
    — intensity: {_I1:.4f}

    After vertical polariser: $E_2 = P_V(E_1) = $ {_E2}
    — intensity: {_I2:.4f}

    **Quarter of the light gets through!** This is Malus' law in action.
    """)
    return


# ============================================================
# Interactive: angle of middle polariser
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Interactive: Vary the Middle Polariser Angle

    Drag the slider to change the angle of the middle polariser and see
    how the transmitted intensity changes.
    """)
    return


@app.cell
def _(mo):
    angle_slider = mo.ui.slider(
        start=0, stop=90, step=1, value=45,
        label="Middle polariser angle (degrees)"
    )
    angle_slider
    return (angle_slider,)


@app.cell
def _(alg, angle_slider, e1, e2, gm, norm, np, polarise, unit):
    _deg = angle_slider.value
    _rad = np.radians(_deg)

    _H = e1.eval()
    _V = e2.eval()
    _mid = unit(np.cos(_rad) * e1.eval() + np.sin(_rad) * e2.eval())

    _E0 = _H
    _E1 = polarise(_E0, _mid)
    _E2 = polarise(_E1, _V)

    _I_out = norm(_E2) ** 2

    gm.md(t"""
    Middle polariser at **{_deg}°**

    - After middle: {_E1}
    - After vertical: {_E2}
    - **Output intensity: {_I_out:.4f}**

    Theory: $I = \\cos^2(\\theta)\\sin^2(\\theta) = \\frac{{1}}{{4}}\\sin^2(2\\theta)$
    = {0.25 * np.sin(2 * _rad)**2:.4f}
    """)
    return


# ============================================================
# Malus' law plot
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Malus' Law — Full Curve

    Transmitted intensity through H → θ → V as a function of the middle
    polariser angle.
    """)
    return


@app.cell
def _(e1, e2, norm, np, plt, polarise, unit):
    _angles = np.linspace(0, 90, 200)
    _intensities = []

    _H = e1.eval()
    _V = e2.eval()

    for _deg in _angles:
        _rad = np.radians(_deg)
        _mid = unit(np.cos(_rad) * e1.eval() + np.sin(_rad) * e2.eval())
        _E1 = polarise(_H, _mid)
        _E2 = polarise(_E1, _V)
        _intensities.append(norm(_E2) ** 2)

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_angles, _intensities, 'b-', linewidth=2, label='GA computation')
    _ax.plot(_angles, 0.25 * np.sin(2 * np.radians(_angles))**2,
             'r--', linewidth=1.5, label=r'$\frac{1}{4}\sin^2(2\theta)$')
    _ax.set_xlabel('Middle polariser angle (degrees)')
    _ax.set_ylabel('Transmitted intensity')
    _ax.set_title('Three-Polariser Transmission (Malus\' Law)')
    _ax.legend()
    _ax.set_xlim(0, 90)
    _ax.set_ylim(-0.01, 0.3)
    _ax.grid(True, alpha=0.3)
    _fig
    return


# ============================================================
# Symbolic chain
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Symbolic Polariser Chain

    Using named vectors, we can see the algebra symbolically.
    """)
    return


@app.cell
def _(e1, e2, gm, gp, norm, np, scalar, unit):
    _H = e1.name("H")
    _V = e2.name("V")
    _D = unit(e1.eval() + e2.eval()).name("D")

    _E0 = _H.eval()

    # Symbolic projection: (E · a) a
    _dot1 = scalar(gp(_E0, _D.eval()))
    _E1 = _dot1 * _D.eval()

    _dot2 = scalar(gp(_E1, _V.eval()))
    _E2 = _dot2 * _V.eval()

    gm.md(t"""
    Polariser axes: {_H}, {_V}, {_D}

    $E_0 = $ {_H} (horizontal)

    $E_1 = (E_0 \\cdot D)\\,D = $ {_E1}

    $E_2 = (E_1 \\cdot V)\\,V = $ {_E2}

    $|E_2|^2 = $ {norm(_E2)**2:.4f}
    """)
    return


# ============================================================
# GA form: P(E) = ½(E + aEa)
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## GA Reflection Form

    The projector $P_a(E) = \\frac{{1}}{{2}}(E + aEa)$ uses the sandwich
    product $aEa$ which reflects $E$ in the axis $a$.
    """)
    return


@app.cell
def _(e1, e2, gm, norm, np, polarise_ga, unit):
    _H = e1.eval()
    _V = e2.eval()
    _D = unit(e1.eval() + e2.eval())

    _E0 = _H
    _E1 = polarise_ga(_E0, _D)
    _E2 = polarise_ga(_E1, _V)

    gm.md(t"""
    Using $P_a(E) = \\frac{{1}}{{2}}(E + aEa)$:

    $E_1 = $ {_E1}

    $E_2 = $ {_E2}

    $|E_2|^2 = $ {norm(_E2)**2:.4f}

    Same result — the two forms are equivalent.
    """)
    return


# ============================================================
# Waveplate as rotor
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Waveplates as Rotors

    A half-wave plate rotates the polarisation by $2\\theta$ where $\\theta$
    is the angle of the fast axis. In GA, this is a rotor:

    $$R = e^{{-B\\theta}}$$

    where $B = e_1 \\wedge e_2$ is the bivector of the transverse plane.
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, norm, np):
    _B = (e1.eval() ^ e2.eval())
    _theta = np.pi / 4  # 45° fast axis → 90° rotation

    _R = exp(-_B * _theta)

    _E0 = e1.eval()  # horizontal
    _E_rotated = _R * _E0 * ~_R

    gm.md(t"""
    Half-wave plate with fast axis at 45°:

    Rotor: $R = $ {_R}

    Input: {e1} (horizontal)

    Output: $R E_0 \\tilde{{R}} = $ {_E_rotated}

    The horizontal polarisation has been rotated to vertical!
    Intensity preserved: $|E|^2 = $ {norm(_E_rotated)**2:.4f}
    """)
    return


# ============================================================
# Polarisation state visualisation
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Polarisation State Diagram

    Visualising the electric field vector at each stage of the
    three-polariser chain.
    """)
    return


@app.cell
def _(e1, e2, norm, np, plt, polarise, unit):
    _H = e1.eval()
    _V = e2.eval()
    _D = unit(e1.eval() + e2.eval())

    _E0 = _H
    _E1 = polarise(_E0, _D)
    _E2 = polarise(_E1, _V)

    _fig, _ax = plt.subplots(figsize=(6, 6))

    _states = [
        (_E0, "E₀ (after H)", "blue"),
        (_E1, "E₁ (after 45°)", "green"),
        (_E2, "E₂ (after V)", "red"),
    ]

    for _E, _label, _color in _states:
        _x, _y = _E.data[1], _E.data[2]
        _ax.annotate("", xy=(_x, _y), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=_color, lw=2.5))
        _ax.annotate(_label, xy=(_x, _y), fontsize=10, color=_color,
                     xytext=(5, 5), textcoords="offset points")

    # Draw polariser axes
    for _a, _name, _ls in [(_H, "H axis", "--"), (_D, "D axis", ":"), (_V, "V axis", "-.")]:
        _ax.plot([-_a.data[1]*1.2, _a.data[1]*1.2],
                 [-_a.data[2]*1.2, _a.data[2]*1.2],
                 color="gray", linestyle=_ls, alpha=0.5, label=_name)

    _ax.set_xlim(-1.3, 1.3)
    _ax.set_ylim(-1.3, 1.3)
    _ax.set_aspect("equal")
    _ax.set_xlabel("Horizontal (e₁)")
    _ax.set_ylabel("Vertical (e₂)")
    _ax.set_title("Polarisation States Through Three Polarisers")
    _ax.legend(loc="lower right", fontsize=9)
    _ax.grid(True, alpha=0.3)

    # Unit circle
    _t = np.linspace(0, 2 * np.pi, 100)
    _ax.plot(np.cos(_t), np.sin(_t), "k-", alpha=0.1)

    _fig
    return


# ============================================================
# N polarisers
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## N Equally-Spaced Polarisers

    What happens if we insert $N$ polarisers equally spaced between H and V?
    As $N \\to \\infty$, the transmission approaches 100% — this is related
    to the quantum Zeno effect.
    """)
    return


@app.cell
def _(mo):
    n_slider = mo.ui.slider(
        start=1, stop=50, step=1, value=5,
        label="Number of intermediate polarisers"
    )
    n_slider
    return (n_slider,)


@app.cell
def _(e1, e2, gm, n_slider, norm, np, polarise, unit):
    _N = n_slider.value
    _E = e1.eval()  # start horizontal

    for _i in range(1, _N + 2):  # N intermediate + final V
        _angle = np.radians(90 * _i / (_N + 1))
        _axis = unit(np.cos(_angle) * e1.eval() + np.sin(_angle) * e2.eval())
        _E = polarise(_E, _axis)

    _I_out = norm(_E) ** 2
    _theory = np.cos(np.pi / (2 * (_N + 1))) ** (2 * (_N + 1))

    gm.md(t"""
    **{_N} intermediate polarisers** (plus H and V):

    Output intensity: **{_I_out:.6f}**

    Theory: $\\cos^{{2(N+1)}}(\\pi / 2(N+1))$ = {_theory:.6f}

    As N → ∞, intensity → 1 (quantum Zeno effect analogue).
    """)
    return


@app.cell
def _(e1, e2, norm, np, plt, polarise, unit):
    _Ns = range(1, 51)
    _intensities = []

    for _N in _Ns:
        _E = e1.eval()
        for _i in range(1, _N + 2):
            _angle = np.radians(90 * _i / (_N + 1))
            _axis = unit(np.cos(_angle) * e1.eval() + np.sin(_angle) * e2.eval())
            _E = polarise(_E, _axis)
        _intensities.append(norm(_E) ** 2)

    _theory = [np.cos(np.pi / (2 * (N + 1))) ** (2 * (N + 1)) for N in _Ns]

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(list(_Ns), _intensities, 'bo-', markersize=3, label='GA computation')
    _ax.plot(list(_Ns), _theory, 'r--', linewidth=1.5,
             label=r'$\cos^{2(N+1)}(\pi/2(N+1))$')
    _ax.set_xlabel('Number of intermediate polarisers')
    _ax.set_ylabel('Transmitted intensity')
    _ax.set_title('N Polarisers Between H and V (Quantum Zeno Analogue)')
    _ax.legend()
    _ax.set_xlim(1, 50)
    _ax.set_ylim(0, 1.05)
    _ax.grid(True, alpha=0.3)
    _fig
    return


if __name__ == "__main__":
    app.run()
