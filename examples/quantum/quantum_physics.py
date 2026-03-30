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

    from galaga import (
        Algebra, norm, grade, lie_bracket, squared,
        even_grades, exp, log, jordan_product, commutator, anticommutator
    )
    from galaga import symbolic as sym
    Sym = sym.sym
    import galaga_marimo as gm

    return (
        Algebra,
        Sym,
        anticommutator,
        commutator,
        exp,
        gm,
        jordan_product,
        lie_bracket,
        log,
        np,
        plt,
        squared,
        sym,
    )


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""

    In the GA approach to quantum mechanics, **pure spin-½ states can be represented
    as rotors** — normalized even-grade elements of Cl(3,0). This is an alternative to
    the usual column-vector-in-Hilbert-space formalism, valid for single-particle
    pure states (global phase is absorbed into the rotor, so this is really a
    projective correspondence).

    The key insight: every element of SU(2) corresponds to a rotor in Cl(3,0).
    The Pauli matrices correspond to basis vectors, and the Bloch sphere is the space of
    rotations of a reference direction.

    | Conventional QM | Geometric Algebra |
    |---|---|
    | Spin state $\\vert\\psi\\rangle$ | Rotor $\\psi$ (even multivector) |
    | Pauli matrix $\\sigma_k$ | Basis vector $e_k$ |
    | Spin operator $\\hat{{S}}_k = \\frac{{\\hbar}}{{2}}\\sigma_k$ | Bivector $\\frac{{\\hbar}}{{2}}Ie_k$ |
    | Expectation $\\langle\\psi\\vert\\sigma_k\\vert\\psi\\rangle$ | Scalar $(\\psi\\, e_3\\, \\tilde\\psi) \\cdot e_k$ |
    | Time evolution $e^{{-iHt/\\hbar}}$ | Rotor $e^{{-Bt}}$ |

    *Note:* this correspondence is for pure states of a single spin-½ particle.
    Mixed states, entanglement, and many-particle systems require additional structure
    (density operators, tensor products) beyond what rotors alone capture.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md("""
    ## The Algebra of Spin

    We work in Cl(3,0) — three Euclidean basis vectors. The pseudoscalar $I = e_1 e_2 e_3$
    plays the role of the imaginary unit $i$ (it squares to $-1$ and commutes with even elements).

    The three bivectors $e_{12}$, $e_{23}$, $e_{31}$ each square to $-1$ and form a
    Lie algebra under the commutator — isomorphic to $\\mathfrak{{su}}(2)$.
    """)
    return


@app.cell
def _(
    Algebra,
    Sym,
    anticommutator,
    commutator,
    gm,
    jordan_product,
    lie_bracket,
    squared,
    sym,
):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors()
    I = alg.I

    # Bivector basis for the spin algebra
    B12 = e1 ^ e2
    B23 = e2 ^ e3
    B31 = e3 ^ e1

    B12_s = Sym(B12, "e_{12}")
    B23_s = Sym(B23, "e_{23}")
    B31_s = Sym(B31, "e_{31}")

    I_s = Sym(I, "I")

    gm.md(t"""**Bivector basis** (each squares to $-1$, like $i$):
    - {sym.squared(B12_s)} = {squared(B12)}
    - {sym.squared(B23_s)} = {squared(B23)}
    - {sym.squared(B31_s)} = {squared(B31)}

    **Commutator**:
    - {sym.commutator(B12_s, B23_s)} = {commutator(B12, B23)}

    **Anti-commutator**:
    - {sym.anticommutator(B12_s, B23_s)} = {anticommutator(B12, B23)}

    **Lie bracket** $[A, B] = \\frac{{1}}{{2}}(AB - BA)$ — bivectors form $\\mathfrak{{su}}(2)$:
    - {sym.lie_bracket(B12_s, B23_s)} = {lie_bracket(B12, B23)}
    - {sym.lie_bracket(B23_s, B31_s)} = {lie_bracket(B23, B31)}
    - {sym.lie_bracket(B31_s, B12_s)} = {lie_bracket(B31, B12)}

    **Jordan product** $A \\circ B = \\frac{{1}}{{2}}\\{{A,B\\}} = \\frac{{1}}{{2}}(AB + BA)$ — the symmetric part:
    - {sym.jordan_product(B12_s, B23_s)} = {jordan_product(B12, B23)}
    - {sym.jordan_product(B12_s, B12_s)} = {jordan_product(B12, B12)}

    **Pseudoscalar** {I_s}, $\\quad$ {sym.squared(I_s)} = {squared(I)}

    $I$ commutes with all even elements and plays the role of $i$ in the Pauli algebra.""")
    return alg, e1, e2, e3


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Spin States as Rotors

    A pure spin state is represented by a rotor $\\psi$ — a normalized even-grade
    element with $\\psi\\tilde\\psi = 1$.

    The **spin vector** (Bloch vector) is $\\mathbf{{s}} = \\psi\\, e_3\\, \\tilde\\psi$: the image
    of the reference direction $e_3$ under the rotation $\\psi$. This is the direction the
    spin "points".

    | State | Rotor $\\psi$ | Spin vector $\\mathbf{{s}}$ |
    |---|---|---|
    | Spin-up ($+z$) | $1$ | $e_3$ |
    | Spin-down ($-z$) | $e_1 e_3$ | $-e_3$ |
    | Spin $+x$ | $\\cos 45° + \\sin 45°\\, e_3 e_1$ | $e_1$ |
    | Spin $+y$ | $\\cos 45° + \\sin 45°\\, e_3 e_2$ | $e_2$ |
    """)
    return


@app.cell
def _(alg, e1, e2, e3, gm, np):
    _states = [
        ("Spin ↑z", alg.identity),
        ("Spin ↓z", alg.rotor(e3 ^ e1, radians=np.pi)),
        ("Spin +x", alg.rotor(e3 ^ e1, radians=np.pi / 2)),
        ("Spin +y", alg.rotor(e3 ^ e2, radians=np.pi / 2)),
        ("Spin −x", alg.rotor(e3 ^ e1, radians=-np.pi / 2)),
    ]

    _rows = []
    for name, psi in _states:
        s = psi * e3 * ~psi
        sx, sy, sz = s.vector_part
        _rows.append(
            f"| {name} | {psi.latex(wrap='$')} | ({sx:+.0f}, {sy:+.0f}, {sz:+.0f}) |"
        )

    gm.md(t"""| State | Rotor $\\psi$ | Spin vector $(s_x, s_y, s_z)$ |
    |---|---|---|
    {"\n".join(_rows):text}""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## The Bloch Sphere

    Every pure spin state maps to a point on the unit sphere via its spin vector.
    The rotor $\\psi(\\theta, \\varphi) = R_\\varphi\\, R_\\theta$ tilts $e_3$ to the direction
    $(\\sin\\theta\\cos\\varphi,\\; \\sin\\theta\\sin\\varphi,\\; \\cos\\theta)$.

    Drag the sliders to move the spin state on the Bloch sphere.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    theta_slider = mo.ui.slider(
        start=0, stop=180, step=1, value=60, label="θ (degrees)"
    )
    phi_slider = mo.ui.slider(
        start=0, stop=360, step=1, value=45, label="φ (degrees)"
    )
    mo.vstack([theta_slider, phi_slider])
    return phi_slider, theta_slider


@app.cell(hide_code=True)
def _(alg, e1, e2, e3, gm, mo, np, phi_slider, plt, theta_slider):
    _theta = np.radians(theta_slider.value)
    _phi = np.radians(phi_slider.value)

    _R_tilt = alg.rotor(e3 ^ e1, radians=_theta)
    _R_azimuth = alg.rotor(e1 ^ e2, radians=_phi)
    _psi = _R_azimuth * _R_tilt

    _s = _psi * e3 * ~_psi
    _sx, _sy, _sz = _s.vector_part

    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")

    # Sphere wireframe
    _u = np.linspace(0, 2 * np.pi, 40)
    _v = np.linspace(0, np.pi, 20)
    _xs = np.outer(np.cos(_u), np.sin(_v))
    _ys = np.outer(np.sin(_u), np.sin(_v))
    _zs = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_xs, _ys, _zs, alpha=0.08, color="gray")

    # Axes
    for vec, label in [([1, 0, 0], "$x$"), ([0, 1, 0], "$y$"), ([0, 0, 1], "$z$")]:
        _ax.quiver(0, 0, 0, *[1.3 * v for v in vec], color="gray", alpha=0.4, arrow_length_ratio=0.08)
        _ax.text(*(1.45 * np.array(vec)), label, fontsize=11, alpha=0.5)

    # Spin vector
    _ax.quiver(0, 0, 0, _sx, _sy, _sz, color="crimson", arrow_length_ratio=0.1, linewidth=2.5)
    _ax.scatter([_sx], [_sy], [_sz], color="crimson", s=60, zorder=5)

    # Shadow projections on the walls
    _lim = 1.3
    _ax.plot([_sx, _sx], [_sy, _sy], [-_lim, _sz], color="crimson", alpha=0.15, lw=1.5)  # drop to floor
    _ax.scatter([_sx], [_sy], [-_lim], color="crimson", alpha=0.2, s=30)                  # floor dot
    _ax.plot([_sx, _sx], [_lim, _sy], [_sz, _sz], color="crimson", alpha=0.15, lw=1.5)    # drop to back wall (yz)
    _ax.scatter([_sx], [_lim], [_sz], color="crimson", alpha=0.2, s=30)                    # back wall dot
    _ax.plot([-_lim, _sx], [_sy, _sy], [_sz, _sz], color="crimson", alpha=0.15, lw=1.5)   # drop to side wall (xz)
    _ax.scatter([-_lim], [_sy], [_sz], color="crimson", alpha=0.2, s=30)                   # side wall dot

    # Reference poles
    _ax.scatter([0], [0], [1], color="steelblue", s=40, marker="^", label="$|{\\uparrow}\\rangle$")
    _ax.scatter([0], [0], [-1], color="steelblue", s=40, marker="v", label="$|{\\downarrow}\\rangle$")

    _ax.set_xlim(-1.3, 1.3)
    _ax.set_ylim(-1.3, 1.3)
    _ax.set_zlim(-1.3, 1.3)
    _ax.set_box_aspect([1, 1, 1])
    _ax.set_title(f"Bloch Sphere — θ={theta_slider.value}°, φ={phi_slider.value}°", fontsize=13)
    _ax.legend(loc="upper left", fontsize=10)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"Rotor: $\\psi$ = {_psi}"),
        gm.md(t"Spin vector: $\\mathbf{{s}} = ({_sx:+.4f},\\; {_sy:+.4f},\\; {_sz:+.4f})$"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Measurement Probabilities

    For a spin state with spin vector $\\mathbf{{s}}$, the probability of measuring
    spin-up along direction $\\hat{{n}}$ is:

    $$P(+\\hat{{n}}) = \\frac{{1 + \\hat{{n}} \\cdot \\mathbf{{s}}}}{{2}} = \\cos^2\\!\\frac{{\\alpha}}{{2}}$$

    where $\\alpha$ is the angle between $\\mathbf{{s}}$ and $\\hat{{n}}$. This is the
    **Malus's law** of quantum spin — identical to the classical law for polarized light.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    meas_theta = mo.ui.slider(
        start=0, stop=180, step=1, value=60,
        label="State θ (tilt from z)"
    )
    meas_theta
    return (meas_theta,)


@app.cell(hide_code=True)
def _(alg, e1, e3, meas_theta, np, plt):
    _theta = np.radians(meas_theta.value)
    _psi = alg.rotor(e3 ^ e1, radians=_theta)
    _s = _psi * e3 * ~_psi

    # Measure along directions from 0° to 180° (in xz plane)
    _angles = np.linspace(0, np.pi, 200)
    _probs = []
    for a in _angles:
        _R_n = alg.rotor(e3 ^ e1, radians=a)
        _n = _R_n * e3 * ~_R_n
        _probs.append((1 + (_n | _s).scalar_part) / 2)

    # Theoretical curve
    _theory = np.cos((_angles - _theta) / 2) ** 2

    _fig, _ax = plt.subplots(figsize=(7, 4))
    _ax.plot(np.degrees(_angles), _probs, "crimson", lw=2.5, label="GA computation")
    _ax.plot(np.degrees(_angles), _theory, "k--", lw=1, alpha=0.5, label=r"$\cos^2(\alpha/2)$")
    _ax.axvline(np.degrees(_theta), color="steelblue", ls=":", alpha=0.6, label=f"state θ={meas_theta.value}°")
    _ax.set_xlabel("Measurement angle (degrees)", fontsize=12)
    _ax.set_ylabel("$P(+\\hat{n})$", fontsize=12)
    _ax.set_title("Measurement Probability vs. Detector Angle", fontsize=13)
    _ax.legend(fontsize=10)
    _ax.grid(True, alpha=0.2)
    _ax.set_xlim(0, 180)
    _ax.set_ylim(-0.05, 1.05)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Sequential Stern–Gerlach

    A classic thought experiment: pass a beam through three Stern–Gerlach devices.

    1. **First device** (along $z$): select spin-up → state $|\\!\\uparrow_z\\rangle$
    2. **Second device** (at angle $\\alpha$): select spin-up → state $|\\!\\uparrow_\\alpha\\rangle$
    3. **Third device** (along $z$): measure spin-up

    The total transmission probability is $\\cos^2(\\alpha/2) \\times \\cos^2(\\alpha/2) = \\cos^4(\\alpha/2)$.

    At $\\alpha = 90°$ this is $1/4$ — the intermediate measurement "restores" some
    spin-up that the first device would have blocked completely.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    sg_slider = mo.ui.slider(
        start=0, stop=180, step=1, value=60,
        label="Middle device angle α (degrees)"
    )
    sg_slider
    return (sg_slider,)


@app.cell(hide_code=True)
def _(alg, e1, e3, gm, mo, np, plt, sg_slider):
    _alpha = np.radians(sg_slider.value)

    # After first device: spin-up along z
    _psi_1 = alg.identity
    _s_1 = _psi_1 * e3 * ~_psi_1

    # Measurement direction for second device
    _R_alpha = alg.rotor(e3 ^ e1, radians=_alpha)
    _n_alpha = _R_alpha * e3 * ~_R_alpha

    # P(pass second device)
    _P_2 = (1 + (_n_alpha | _s_1).scalar_part) / 2

    # After second device: spin aligned with n_alpha
    _psi_2 = alg.rotor(e3 ^ e1, radians=_alpha)
    _s_2 = _psi_2 * e3 * ~_psi_2

    # P(pass third device | passed second)
    _P_3 = (1 + (e3 | _s_2).scalar_part) / 2

    _P_total = _P_2 * _P_3

    # Plot: total probability vs alpha
    _alphas = np.linspace(0, np.pi, 200)
    _P_curve = np.cos(_alphas / 2) ** 4

    _fig, _ax = plt.subplots(figsize=(7, 4))
    _ax.plot(np.degrees(_alphas), _P_curve, "crimson", lw=2.5)
    _ax.plot(sg_slider.value, _P_total, "ko", ms=10, zorder=5)
    _ax.axhline(0.25, color="gray", ls=":", alpha=0.4)
    _ax.text(92, 0.27, "$1/4$ at 90°", fontsize=10, alpha=0.6)
    _ax.set_xlabel("Middle device angle α (degrees)", fontsize=12)
    _ax.set_ylabel("Total transmission $P$", fontsize=12)
    _ax.set_title("Sequential Stern–Gerlach: $P = \\cos^4(\\alpha/2)$", fontsize=13)
    _ax.grid(True, alpha=0.2)
    _ax.set_xlim(0, 180)
    _ax.set_ylim(-0.05, 1.05)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"""- $\\alpha = {sg_slider.value:.0f}°$
    - $P$(pass 2nd) $= \\cos^2(\\alpha/2) = {_P_2:.4f}$
    - $P$(pass 3rd | passed 2nd) $= \\cos^2(\\alpha/2) = {_P_3:.4f}$
    - **Total: $P = {_P_total:.4f}$**"""),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Larmor Precession

    A spin in a magnetic field $\\mathbf{{B}} = B\\,e_3$ precesses about the field axis.

    The Hamiltonian bivector is $\\Omega = -\\frac{{\\omega}}{{2}}\\,e_1 e_2$ (where $\\omega = \\gamma B$
    is the Larmor frequency). Time evolution is a rotor:

    $$U(t) = e^{{-\\Omega t}} = e^{{\\omega t/2\\; e_1 e_2}}$$

    This is just a rotation about $e_3$ — the spin vector traces a cone, with $s_z$ constant.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    precess_theta = mo.ui.slider(
        start=1, stop=90, step=1, value=60,
        label="Initial tilt θ (degrees)"
    )
    precess_theta
    return (precess_theta,)


@app.cell(hide_code=True)
def _(alg, e1, e2, e3, gm, mo, np, plt, precess_theta):
    _theta = np.radians(precess_theta.value)
    _psi_0 = alg.rotor(e3 ^ e1, radians=_theta)

    _omega = 1.0
    _times = np.linspace(0, 4 * np.pi, 300)
    _sx, _sy, _sz = [], [], []

    for t in _times:
        _U = alg.rotor(e1 ^ e2, radians=_omega * t)
        _psi_t = _U * _psi_0
        _s = _psi_t * e3 * ~_psi_t
        _vx, _vy, _vz = _s.vector_part
        _sx.append(_vx)
        _sy.append(_vy)
        _sz.append(_vz)

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Time traces
    _ax1.plot(_times, _sx, label="$s_x$", color="crimson")
    _ax1.plot(_times, _sy, label="$s_y$", color="steelblue")
    _ax1.plot(_times, _sz, label="$s_z$", color="seagreen", ls="--")
    _ax1.set_xlabel("$\\omega t$", fontsize=12)
    _ax1.set_ylabel("Spin component", fontsize=12)
    _ax1.set_title("Larmor Precession", fontsize=13)
    _ax1.legend(fontsize=10)
    _ax1.grid(True, alpha=0.2)

    # Trajectory on Bloch sphere (top view)
    _ax2.plot(_sx, _sy, "crimson", lw=1.5, alpha=0.7)
    _ax2.plot(_sx[0], _sy[0], "ko", ms=8, label="$t=0$")
    _t = np.linspace(0, 2 * np.pi, 100)
    _r = np.sin(_theta)
    _ax2.plot(_r * np.cos(_t), _r * np.sin(_t), "k:", alpha=0.3)
    _ax2.set_xlim(-1.2, 1.2)
    _ax2.set_ylim(-1.2, 1.2)
    _ax2.set_aspect("equal")
    _ax2.set_xlabel("$s_x$", fontsize=12)
    _ax2.set_ylabel("$s_y$", fontsize=12)
    _ax2.set_title("Top View (looking down $z$)", fontsize=13)
    _ax2.legend(fontsize=10)
    _ax2.grid(True, alpha=0.2)

    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"$s_z = \\cos\\theta = {np.cos(_theta):.4f}$ (constant — precession preserves $z$-component)"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Spin Rotations and SU(2) Double Cover

    A $360°$ rotation returns a vector to itself, but the **rotor** picks up a sign:
    $\\psi \\to -\\psi$. You need $720°$ to get back to $+\\psi$.

    This is the famous **spinor sign flip** — a manifestation of the SU(2) double cover of SO(3).
    """)
    return


@app.cell
def _(alg, e1, e2, e3, gm, np):
    _B = e1 ^ e2
    _angles = [0, 90, 180, 270, 360, 450, 540, 630, 720]

    _rows = []
    for deg in _angles:
        _R = alg.rotor(_B, radians=np.radians(deg))
        _s = _R * e3 * ~_R
        _sz = _s.vector_part[2]
        _sc = (_R).scalar_part
        _rows.append(
            f"| {deg:3d}° | {_sc:+.4f} | {_R.latex(wrap='$')} | {_sz:+.4f} |"
        )

    gm.md(t"""| Angle | Scalar part | Rotor $\\psi$ | $s_z$ |
    |---|---|---|---|
    {"\n".join(_rows):text}

    At 360°: the rotor is $-1$ (not $+1$!). The spin vector returns to $e_3$,
    but the rotor has flipped sign. Only at 720° does $\\psi$ return to $+1$.""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Rotor Interpolation (SLERP)

    Because spin states are rotors, interpolation is natural. The relative rotor
    $\\Delta = \\psi_1 \\tilde\\psi_0$ connects two states, and scaling its logarithm
    gives the geodesic:

    $$\\psi(t) = \\exp\\!\\big(t \\cdot \\log(\\psi_1 \\tilde\\psi_0)\\big)\\,\\psi_0, \\qquad t \\in [0, 1]$$

    This traces the shortest path between two spin states on the Bloch sphere.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    slerp_slider = mo.ui.slider(
        start=0.0, stop=1.0, step=0.01, value=0.5, label="t (interpolation)"
    )
    slerp_slider
    return (slerp_slider,)


@app.cell(hide_code=True)
def _(alg, e1, e3, exp, gm, log, mo, np, plt, slerp_slider):
    # Interpolate from spin +z (tilted 30°) to spin +x
    _psi_0 = alg.rotor(e3 ^ e1, radians=np.pi / 6)
    _psi_1 = alg.rotor(e3 ^ e1, radians=np.pi / 2)

    _Delta = _psi_1 * ~_psi_0
    _B = log(_Delta)
    _t = slerp_slider.value
    _psi_t = exp(_t * _B) * _psi_0

    _s_t = _psi_t * e3 * ~_psi_t
    _sx_t, _sy_t, _sz_t = _s_t.vector_part

    # Trace the full path
    _ts = np.linspace(0, 1, 100)
    _path_x, _path_z = [], []
    for ti in _ts:
        _Ri = exp(ti * _B) * _psi_0
        _si = _Ri * e3 * ~_Ri
        _vp = _si.vector_part
        _path_x.append(_vp[0])
        _path_z.append(_vp[2])

    # Start and end spin vectors
    _s0 = _psi_0 * e3 * ~_psi_0
    _s1 = _psi_1 * e3 * ~_psi_1

    _fig, _ax = plt.subplots(figsize=(5, 5))
    _t_circle = np.linspace(0, 2 * np.pi, 100)
    _ax.plot(np.sin(_t_circle), np.cos(_t_circle), "k-", alpha=0.1)
    _ax.plot(_path_x, _path_z, "crimson", lw=2, alpha=0.5, label="geodesic")
    _ax.plot(_sx_t, _sz_t, "ko", ms=10, zorder=5, label=f"$t = {_t:.2f}$")
    _ax.plot(_s0.vector_part[0], _s0.vector_part[2], "s", color="steelblue", ms=10, label="$\\psi_0$")
    _ax.plot(_s1.vector_part[0], _s1.vector_part[2], "s", color="seagreen", ms=10, label="$\\psi_1$")
    _ax.set_xlim(-1.3, 1.3)
    _ax.set_ylim(-1.3, 1.3)
    _ax.set_aspect("equal")
    _ax.set_xlabel("$s_x$", fontsize=12)
    _ax.set_ylabel("$s_z$", fontsize=12)
    _ax.set_title("SLERP on the Bloch Sphere ($xz$ plane)", fontsize=13)
    _ax.legend(fontsize=10, loc="lower left")
    _ax.grid(True, alpha=0.2)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"$\\psi(t)$ = {_psi_t}"),
        gm.md(t"Spin vector: $\\mathbf{{s}} = ({_sx_t:+.4f},\\; 0,\\; {_sz_t:+.4f})$"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Symbolic Identities

    The symbolic layer verifies algebraic identities as expression trees.
    """)
    return


@app.cell
def _(Sym, alg, e1, e2, e3, gm, sym):
    _R = Sym(alg.rotor(e1 ^ e2, radians=0.5), "ψ")
    _v = Sym(e3, "e₃")

    _rules = [
        ("Double reverse: ~~ψ", sym.simplify(~~_R)),
        ("Rotor normalization: ψ~ψ", sym.simplify(_R * ~_R)),
        ("Sandwich grade: ⟨ψ e₃ ~ψ⟩₁", sym.simplify(sym.grade(_R * _v * ~_R, 1))),
        ("Norm of unit: ‖unit(e₃)‖", sym.simplify(sym.norm(Sym(e3 / 1.0, "n̂")))),
    ]

    _lines = "\n".join(f"- {name} $\\;\\to\\;$ ${result.latex()}$" for name, result in _rules)
    gm.md(t"{_lines:text}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
