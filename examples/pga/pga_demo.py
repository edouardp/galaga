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

    from galaga import Algebra, grade, exp, log, reverse, norm
    import galaga_marimo as gm

    return Algebra, exp, gm, grade, log, norm, np, plt, reverse


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Projective Geometric Algebra (PGA)

    **PGA** is Cl(3,0,1) — three Euclidean basis vectors plus one **degenerate** vector
    ($e_0^2 = 0$). This single extra dimension unifies rotations, translations, and
    reflections into a single algebraic framework: every rigid motion is a sandwich product.

    | Euclidean GA | PGA |
    |---|---|
    | Rotations only | Rotations + translations + screws |
    | Vectors are directions | Points, lines, and planes are all elements |
    | No translation rotors | $T = 1 + \\frac{{d}}{{2}}\\,e_0\\,\\hat{{n}}$ translates by $d$ |
    | Compose rotations | Compose any rigid motions |
    """)
    return


@app.cell
def _(Algebra, gm):
    alg = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3, e0 = alg.basis_vectors()

    gm.md(t"""**Basis vectors:**
- $e_1^2 = {(e1*e1).scalar_part:text}$, $e_2^2 = {(e2*e2).scalar_part:text}$, $e_3^2 = {(e3*e3).scalar_part:text}$ (Euclidean)
- $e_0^2 = {(e0*e0).scalar_part:text}$ (degenerate — this is what makes PGA projective)""")
    return alg, e0, e1, e2, e3


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Points, Planes, and the Degenerate Dimension

    In PGA, geometric objects are multivector elements:

    - **Planes** are 1-vectors: $p = ae_1 + be_2 + ce_3 + de_0$ represents $ax + by + cz + d = 0$
      (with the convention that $d$ has opposite sign)
    - **Points** are trivectors: $P = e_{{123}} + x\\,E_1 + y\\,E_2 + z\\,E_3$
      where $E_i$ are the "dual basis" trivectors

    The degenerate dimension $e_0$ encodes position — it's what lets PGA distinguish
    "where" from "which direction".
    """)
    return


@app.cell
def _(alg, e0, e1, e2, e3, gm, np):
    e123 = e1 ^ e2 ^ e3

    # Dual basis trivectors (encode position components)
    E1 = e2 ^ e3 ^ e0
    E2 = -(e1 ^ e3 ^ e0)
    E3 = e1 ^ e2 ^ e0

    def point(x, y, z):
        """Normalized point at (x, y, z)."""
        return e123 + x * E1 + y * E2 + z * E3

    def coords(P):
        """Extract (x, y, z) from a point trivector."""
        w = P.data[7]  # e123 coefficient
        return np.array([P.data[14] / w, -P.data[13] / w, P.data[11] / w])

    _P = point(3, 4, 5)
    _c = coords(_P)

    gm.md(t"""Point at $(3, 4, 5)$: {_P}

Extracted coordinates: $({_c[0]:.0f},\\; {_c[1]:.0f},\\; {_c[2]:.0f})$ ✓""")
    return E1, E2, E3, coords, e123, point


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Translations

    A translation by distance $d$ along direction $\\hat{{n}}$ is the rotor:

    $$T = 1 + \\frac{{d}}{{2}}\\,e_0\\,\\hat{{n}}$$

    This is a **null rotor** — $e_0^2 = 0$ means $T\\tilde{{T}} = 1$ automatically.
    No trigonometry, no exponentials. Translation is the simplest operation in PGA.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    tx_slider = mo.ui.slider(start=-5, stop=5, step=0.1, value=3, label="Δx")
    ty_slider = mo.ui.slider(start=-5, stop=5, step=0.1, value=0, label="Δy")
    mo.vstack([tx_slider, ty_slider])
    return tx_slider, ty_slider


@app.cell(hide_code=True)
def _(alg, coords, e0, e1, e2, gm, mo, np, plt, point, tx_slider, ty_slider):
    _dx = tx_slider.value
    _dy = ty_slider.value
    _T = alg.identity + (_dx / 2) * e0 * e1 + (_dy / 2) * e0 * e2

    # Translate a triangle
    _tri = [point(0, 0, 0), point(1, 0, 0), point(0.5, 0.8, 0)]
    _tri_t = [_T * P * ~_T for P in _tri]

    _orig = np.array([coords(P) for P in _tri])
    _trans = np.array([coords(P) for P in _tri_t])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.fill(_orig[:, 0], _orig[:, 1], alpha=0.3, color="steelblue", label="original")
    _ax.fill(_trans[:, 0], _trans[:, 1], alpha=0.3, color="crimson", label="translated")
    for i in range(3):
        _ax.annotate("", xy=_trans[i, :2], xytext=_orig[i, :2],
                     arrowprops=dict(arrowstyle="->", color="gray", alpha=0.5))
    _ax.set_xlim(-6, 6)
    _ax.set_ylim(-4, 4)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.legend(fontsize=10)
    _ax.set_title(f"Translation: Δx={_dx:.1f}, Δy={_dy:.1f}", fontsize=13)
    plt.tight_layout()

    _TT = _T * ~_T
    mo.vstack([
        _fig,
        gm.md(t"Translator: {_T}"),
        gm.md(t"$T\\tilde{{T}}$ = {_TT} (always 1 — null rotor)"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Rotations

    Rotations work exactly as in Euclidean GA — the rotor lives in the $e_1 e_2 e_3$
    subspace. The degenerate dimension $e_0$ comes along for the ride.

    $$R = \\cos\\frac{{\\theta}}{{2}} - \\sin\\frac{{\\theta}}{{2}}\\,(e_1 \\wedge e_2)$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    rot_slider = mo.ui.slider(start=0, stop=360, step=1, value=90, label="θ (degrees)")
    rot_slider
    return (rot_slider,)


@app.cell(hide_code=True)
def _(alg, coords, e1, e2, gm, mo, np, plt, point, rot_slider):
    _theta = np.radians(rot_slider.value)
    _R = alg.rotor(e1 ^ e2, radians=_theta)

    _tri = [point(1, 0, 0), point(2, 0, 0), point(1.5, 0.8, 0)]
    _tri_r = [_R * P * ~_R for P in _tri]

    _orig = np.array([coords(P) for P in _tri])
    _rot = np.array([coords(P) for P in _tri_r])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _t = np.linspace(0, 2 * np.pi, 100)
    _ax.plot(np.cos(_t), np.sin(_t), "k:", alpha=0.1)
    _ax.plot(2 * np.cos(_t), 2 * np.sin(_t), "k:", alpha=0.1)
    _ax.fill(_orig[:, 0], _orig[:, 1], alpha=0.3, color="steelblue", label="original")
    _ax.fill(_rot[:, 0], _rot[:, 1], alpha=0.3, color="crimson", label="rotated")
    _ax.plot(0, 0, "k+", ms=10)
    _ax.set_xlim(-3, 3)
    _ax.set_ylim(-3, 3)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.legend(fontsize=10)
    _ax.set_title(f"Rotation: θ={rot_slider.value}° about origin", fontsize=13)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"Rotor: {_R}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Reflections in Planes

    A plane $p = ae_1 + be_2 + ce_3 + de_0$ reflects points via the sandwich $P' = pPp$.

    The Euclidean part $(a, b, c)$ is the normal; $d$ controls the offset.
    To build an offset plane, translate the origin plane: $p' = T\\,p\\,\\tilde{{T}}$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    ref_d = mo.ui.slider(start=-3, stop=3, step=0.1, value=1.5, label="Plane offset d")
    ref_d
    return (ref_d,)


@app.cell(hide_code=True)
def _(alg, coords, e0, e1, gm, mo, np, plt, point, ref_d):
    _d = ref_d.value
    # Plane x = d: translate e1 by d along x
    _T = alg.identity + (_d / 2) * e0 * e1
    _p = _T * e1 * ~_T

    _tri = [point(2.5, -0.5, 0), point(3.5, -0.5, 0), point(3, 0.5, 0)]
    _tri_ref = [_p * P * _p for P in _tri]

    _orig = np.array([coords(P) for P in _tri])
    _refl = np.array([coords(P) for P in _tri_ref])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.axvline(_d, color="seagreen", lw=2, ls="--", alpha=0.7, label=f"plane $x={_d:.1f}$")
    _ax.fill(_orig[:, 0], _orig[:, 1], alpha=0.3, color="steelblue", label="original")
    _ax.fill(_refl[:, 0], _refl[:, 1], alpha=0.3, color="crimson", label="reflected")
    _ax.set_xlim(-4, 6)
    _ax.set_ylim(-3, 3)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.legend(fontsize=10)
    _ax.set_title("Reflection in a Plane", fontsize=13)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"Plane: {_p}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Motors: Unified Rigid Motions

    The real power of PGA: **any rigid motion** (rotation, translation, or both) is a
    single even-grade element called a **motor**:

    $$M = T \\cdot R$$

    Apply it the same way as always: $P' = M\\,P\\,\\tilde{{M}}$.

    Motors compose by geometric product — just like rotors. The entire group of
    rigid motions (SE(3)) is captured by the even subalgebra of Cl(3,0,1).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    motor_angle = mo.ui.slider(start=0, stop=360, step=1, value=45, label="Rotation θ°")
    motor_tx = mo.ui.slider(start=-3, stop=3, step=0.1, value=2, label="Translation Δx")
    motor_ty = mo.ui.slider(start=-3, stop=3, step=0.1, value=1, label="Translation Δy")
    mo.vstack([motor_angle, motor_tx, motor_ty])
    return motor_angle, motor_tx, motor_ty


@app.cell(hide_code=True)
def _(alg, coords, e0, e1, e2, gm, mo, motor_angle, motor_tx, motor_ty, np, plt, point):
    _theta = np.radians(motor_angle.value)
    _R = alg.rotor(e1 ^ e2, radians=_theta)
    _T = alg.identity + (motor_tx.value / 2) * e0 * e1 + (motor_ty.value / 2) * e0 * e2
    _M = _T * _R  # rotate first, then translate

    _tri = [point(0.5, -0.3, 0), point(1.5, -0.3, 0), point(1, 0.5, 0)]
    _tri_m = [_M * P * ~_M for P in _tri]

    _orig = np.array([coords(P) for P in _tri])
    _moved = np.array([coords(P) for P in _tri_m])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.fill(_orig[:, 0], _orig[:, 1], alpha=0.3, color="steelblue", label="original")
    _ax.fill(_moved[:, 0], _moved[:, 1], alpha=0.3, color="crimson", label="motor applied")
    _ax.plot(0, 0, "k+", ms=10)
    _ax.set_xlim(-5, 5)
    _ax.set_ylim(-5, 5)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.legend(fontsize=10)
    _ax.set_title(f"Motor: rotate {motor_angle.value}° then translate ({motor_tx.value:.1f}, {motor_ty.value:.1f})", fontsize=13)
    plt.tight_layout()

    _MM = _M * ~_M
    mo.vstack([
        _fig,
        gm.md(t"Motor: {_M}"),
        gm.md(t"$M\\tilde{{M}}$ = {_MM}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Motor Interpolation

    Just like rotor SLERP, motor interpolation uses $\\exp$ and $\\log$:

    $$M(t) = \\exp\\!\\big(t \\cdot \\log M\\big), \\qquad t \\in [0, 1]$$

    This traces the **screw motion** — the unique helical path connecting the start
    and end poses. Every rigid motion in 3D is a screw (Chasles' theorem).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    interp_slider = mo.ui.slider(start=0.0, stop=1.0, step=0.01, value=0.5, label="t")
    interp_slider
    return (interp_slider,)


@app.cell(hide_code=True)
def _(alg, coords, e0, e1, e2, exp, gm, interp_slider, log, mo, np, plt, point):
    # Motor: 90° rotation + translation
    _R = alg.rotor(e1 ^ e2, radians=np.pi / 2)
    _T = alg.identity + (3 / 2) * e0 * e1 + (2 / 2) * e0 * e2
    _M = _T * _R

    _B = log(_M)
    _t = interp_slider.value
    _M_t = exp(_t * _B)

    _tri = [point(0.5, -0.3, 0), point(1.5, -0.3, 0), point(1, 0.5, 0)]
    _tri_start = np.array([coords(P) for P in _tri])
    _tri_end = np.array([coords(_M * P * ~_M) for P in _tri])
    _tri_t = np.array([coords(_M_t * P * ~_M_t) for P in _tri])

    # Trace path of centroid
    _cx, _cy = [], []
    _centroid = point(2 / 3, 0, 0)  # approximate centroid
    for ti in np.linspace(0, 1, 80):
        _Mi = exp(ti * _B)
        _c = coords(_Mi * _centroid * ~_Mi)
        _cx.append(_c[0])
        _cy.append(_c[1])

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.plot(_cx, _cy, "gray", lw=1.5, alpha=0.4, label="screw path")
    _ax.fill(_tri_start[:, 0], _tri_start[:, 1], alpha=0.15, color="steelblue")
    _ax.fill(_tri_end[:, 0], _tri_end[:, 1], alpha=0.15, color="seagreen")
    _ax.fill(_tri_t[:, 0], _tri_t[:, 1], alpha=0.4, color="crimson", label=f"$t = {_t:.2f}$")
    _ax.plot(0, 0, "k+", ms=10)
    _ax.set_xlim(-3, 6)
    _ax.set_ylim(-3, 5)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.legend(fontsize=10)
    _ax.set_title("Motor Interpolation (Screw Motion)", fontsize=13)
    plt.tight_layout()

    mo.vstack([
        _fig,
        gm.md(t"$M(t)$ = {_M_t}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Ideal Points (Points at Infinity)

    An **ideal point** is a trivector with no $e_{{123}}$ component — it represents a
    direction, not a position. Translations leave ideal points unchanged (directions
    don't move), but rotations rotate them.

    This is the projective geometry at work: the "point at infinity" along $\\hat{{x}}$
    is where all lines parallel to $\\hat{{x}}$ meet.
    """)
    return


@app.cell
def _(E1, alg, e0, e1, e2, gm, np):
    _d = E1  # ideal point along x

    # Translation does nothing
    _T = alg.identity + (100 / 2) * e0 * e1
    _d_trans = _T * _d * ~_T

    # Rotation rotates the direction
    _R = alg.rotor(e1 ^ e2, radians=np.pi / 2)
    _d_rot = _R * _d * ~_R

    gm.md(t"""Ideal point (direction $+x$): {_d}

After translating by 100 along $x$: {_d_trans} (unchanged ✓)

After rotating 90° in $xy$: {_d_rot} (now points along $+y$ ✓)

Translation-invariance is automatic — $e_0^2 = 0$ kills the translation terms.""")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Why PGA?

    The key insight: **every rigid motion is a sandwich product**. No special cases,
    no separate translation matrices, no homogeneous coordinates bolted on after the fact.

    | Operation | PGA element | Formula |
    |---|---|---|
    | Translation | $T = 1 + \\frac{{d}}{{2}}\\,e_0\\hat{{n}}$ | $P' = TP\\tilde{{T}}$ |
    | Rotation (origin) | $R = \\cos\\frac{{\\theta}}{{2}} - \\sin\\frac{{\\theta}}{{2}}\\,B$ | $P' = RP\\tilde{{R}}$ |
    | Rotation (offset) | $M = T_{{\\text{{back}}}}\\,R\\,T_{{\\text{{to}}}}$ | $P' = MP\\tilde{{M}}$ |
    | Reflection | plane $p$ | $P' = pPp$ |
    | Screw motion | $M = \\exp(-\\frac{{\\theta}}{{2}}\\,L)$ | $P' = MP\\tilde{{M}}$ |
    | Any rigid motion | motor $M$ (even grade) | $P' = MP\\tilde{{M}}$ |
    | Interpolation | $M(t) = \\exp(t\\,\\log M)$ | smooth screw path |

    Motors compose by geometric product: $M_{{\\text{{total}}}} = M_2 M_1$ (right-to-left,
    like rotors). The entire Euclidean group SE(3) lives in the even subalgebra.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
