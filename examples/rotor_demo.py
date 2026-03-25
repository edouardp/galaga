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

    from ga import (
        Algebra, grade, reverse, sandwich, scalar, norm, unit,
        gp, op, exp, log, norm2,
    )
    from ga.symbolic import (
        sym, gp as sgp, grade as sgrade, reverse as srev,
        simplify, norm as snorm, unit as sunit, inverse as sinverse,
    )
    import galaga_marimo as gm

    return (
        Algebra,
        exp,
        gm,
        log,
        np,
        plt,
        sandwich,
        scalar,
        simplify,
        sinverse,
        snorm,
        sunit,
        sym,
        unit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rotors in Geometric Algebra

    A **rotor** is an even-graded multivector that encodes rotations via the sandwich product:
    $$v' = R\,v\,\tilde{R}$$

    Rotors compose by multiplication, invert by reversion, and generalize seamlessly
    from 2D through spacetime. This notebook explores rotors across several algebras,
    including composing rotors, rotating rotors themselves, and rotating the bivector
    generators that produce rotors.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2D Rotors — $\mathrm{Cl}(2,0)$

    In 2D there is exactly one bivector plane $e_1 e_2$, so every rotor is
    $R = \cos(\theta/2) - \sin(\theta/2)\,e_{12}$.
    """)
    return


@app.cell
def _(Algebra):
    cl2 = Algebra((1, 1))
    f1, f2 = cl2.basis_vectors()
    return cl2, f1, f2


@app.cell(hide_code=True)
def _(mo):
    angle_2d = mo.ui.slider(start=0, stop=360, step=1, value=45, label="θ (degrees)")
    angle_2d
    return (angle_2d,)


@app.cell
def _(angle_2d, cl2, f1, f2, gm, mo, np, sandwich):
    _theta = np.radians(angle_2d.value)
    _R = cl2.rotor(f1 ^ f2, radians=_theta)
    _v = f1
    _result = sandwich(_R, _v)

    mo.vstack([
        gm.md(t"$\\theta = {angle_2d.value}°$"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$R\\,e_1\\,\\tilde{{R}} =$ {_result}"),
    ])
    return


@app.cell(hide_code=True)
def _(angle_2d, cl2, f1, f2, np, plt, sandwich):
    _theta = np.radians(angle_2d.value)
    _R = cl2.rotor(f1 ^ f2, radians=_theta)
    _v_rot = sandwich(_R, f1)
    _vx, _vy = _v_rot.vector_part

    _fig, _ax = plt.subplots(figsize=(5, 5))
    _ax.set_xlim(-1.4, 1.4)
    _ax.set_ylim(-1.4, 1.4)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.3)
    _ax.axhline(0, color="k", lw=0.5)
    _ax.axvline(0, color="k", lw=0.5)

    _t = np.linspace(0, 2 * np.pi, 100)
    _ax.plot(np.cos(_t), np.sin(_t), "k-", alpha=0.1)

    _ax.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1,
               color="steelblue", width=0.02, label="$e_1$")
    _ax.quiver(0, 0, _vx, _vy, angles="xy", scale_units="xy", scale=1,
               color="crimson", width=0.02, label="$Re_1\\tilde{R}$")

    _arc = np.linspace(0, _theta, 50)
    _ax.plot(0.3 * np.cos(_arc), 0.3 * np.sin(_arc), "k-", alpha=0.4)

    _ax.legend(loc="upper left", fontsize=11)
    _ax.set_title(f"2D Rotation — θ = {angle_2d.value}°", fontsize=13)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3D Rotors — $\mathrm{Cl}(3,0)$

    In 3D there are three bivector planes. Any rotation axis corresponds to a
    bivector (its dual). The rotor formula is the same:
    $R = \cos(\theta/2) - \sin(\theta/2)\,\hat{B}$.
    """)
    return


@app.cell
def _(Algebra):
    cl3 = Algebra((1, 1, 1))
    e1, e2, e3 = cl3.basis_vectors()
    return cl3, e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    plane_3d = mo.ui.dropdown(
        options={"e₁e₂ (rotation about e₃)": "12", "e₂e₃ (rotation about e₁)": "23", "e₁e₃ (rotation about e₂)": "13"},
        value="e₁e₂ (rotation about e₃)", label="Plane"
    )
    angle_3d = mo.ui.slider(start=0, stop=360, step=1, value=90, label="θ (degrees)")
    mo.vstack([plane_3d, angle_3d])
    return angle_3d, plane_3d


@app.cell
def _(angle_3d, cl3, e1, e2, e3, gm, mo, np, plane_3d, sandwich):
    _planes = {"12": e1 ^ e2, "23": e2 ^ e3, "13": e1 ^ e3}
    _B = _planes[plane_3d.value]
    _theta = np.radians(angle_3d.value)
    _R = cl3.rotor(_B, radians=_theta)
    _v = e1 + e2 + e3

    _result = sandwich(_R, _v)
    _RR = _R * ~_R

    mo.vstack([
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$v = e_1 + e_2 + e_3$"),
        gm.md(t"$R\\,v\\,\\tilde{{R}} =$ {_result}"),
        gm.md(t"$R\\tilde{{R}} =$ {_RR}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Composing Rotors

    Two successive rotations $R_1$ then $R_2$ compose as $R = R_2 R_1$.
    This is just multiplication — no matrix products, no quaternion rules.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    comp_a1 = mo.ui.slider(start=0, stop=360, step=1, value=45, label="θ₁ in e₁e₂ (degrees)")
    comp_a2 = mo.ui.slider(start=0, stop=360, step=1, value=30, label="θ₂ in e₂e₃ (degrees)")
    mo.vstack([comp_a1, comp_a2])
    return comp_a1, comp_a2


@app.cell
def _(cl3, comp_a1, comp_a2, e1, e2, e3, gm, mo, np, sandwich):
    _R1 = cl3.rotor(e1 ^ e2, degrees=comp_a1.value)
    _R2 = cl3.rotor(e2 ^ e3, degrees=comp_a2.value)
    _R_composed = _R2 * _R1

    _v = e1
    _step1 = sandwich(_R1, _v)
    _step2 = sandwich(_R2, _step1)
    _direct = sandwich(_R_composed, _v)

    _match = np.allclose(_step2.data, _direct.data)
    mo.vstack([
        gm.md(t"$R_1$ ({comp_a1.value}° in $e_1 e_2$): {_R1}"),
        gm.md(t"$R_2$ ({comp_a2.value}° in $e_2 e_3$): {_R2}"),
        gm.md(t"$R_2 R_1 =$ {_R_composed}"),
        gm.md(t"Step-by-step: $R_2(R_1 e_1 \\tilde{{R_1}})\\tilde{{R_2}} =$ {_step2}"),
        gm.md(t"Direct: $(R_2 R_1) e_1 (\\widetilde{{R_2 R_1}})^ =$ {_direct}"),
        gm.md(t"Match? **{_match!s}**"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rotors from `exp` and `log`

    A rotor can be built from a bivector via the exponential map:
    $R = e^{-\theta/2\,\hat{B}} = \cos(\theta/2) - \sin(\theta/2)\,\hat{B}$.

    The logarithm extracts the bivector generator back: $\log R = -\frac{\theta}{2}\hat{B}$.
    """)
    return


@app.cell
def _(cl3, e1, e2, exp, gm, log, mo, np, unit):
    _B = e1 ^ e2
    _theta = np.pi / 3
    _R_rotor = cl3.rotor(_B, radians=_theta)
    _R_exp = exp(-_theta / 2 * unit(_B))

    _match = np.allclose(_R_rotor.data, _R_exp.data)

    _B_recovered = log(_R_rotor)

    mo.vstack([
        gm.md(t"$\\theta = 60°$, plane $= e_1 e_2$"),
        gm.md(t"`alg.rotor(B, θ)`: {_R_rotor}"),
        gm.md(t"`exp(-θ/2 B̂)`: {_R_exp}"),
        gm.md(t"Match? **{_match!s}**"),
        gm.md(t"`log(R)` = {_B_recovered}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Composed Rotation — 3D Visualization

    Same idea as above, but with an interactive 3D plot. Drag the sliders to see
    how composing rotations in different planes produces a single combined rotation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    rr_alpha = mo.ui.slider(start=0, stop=360, step=1, value=0, label="α — second rotation (degrees)")
    rr_theta = mo.ui.slider(start=0, stop=360, step=1, value=90, label="θ — first rotation (degrees)")
    mo.vstack([rr_theta, rr_alpha])
    return rr_alpha, rr_theta


@app.cell(hide_code=True)
def _(cl3, e1, e2, e3, gm, mo, rr_alpha, rr_theta, sandwich, scalar):
    _R = cl3.rotor(e1 ^ e2, degrees=rr_theta.value)
    _S = cl3.rotor(e1 ^ e3, degrees=rr_alpha.value)
    _R_composed = _S * _R

    _v = e1
    _orig = sandwich(_R, _v)
    _new = sandwich(_R_composed, _v)
    _RR = scalar(_R_composed * ~_R_composed)

    mo.vstack([
        gm.md(t"$R$ ({rr_theta.value}° in $e_1 e_2$): {_R}"),
        gm.md(t"$S$ ({rr_alpha.value}° in $e_1 e_3$): {_S}"),
        gm.md(t"$SR =$ {_R_composed}"),
        gm.md(t"$R\\,e_1\\,\\tilde{{R}} =$ {_orig}"),
        gm.md(t"$(SR)\\,e_1\\,(SR)^\\sim =$ {_new}"),
        gm.md(t"$(SR)(SR)^\\sim = {_RR:.4f}$"),
    ])
    return


@app.cell(hide_code=True)
def _(cl3, e1, e2, e3, plt, rr_alpha, rr_theta, sandwich):
    _R = cl3.rotor(e1 ^ e2, degrees=rr_theta.value)
    _S = cl3.rotor(e1 ^ e3, degrees=rr_alpha.value)
    _R_composed = _S * _R

    _v = e1
    _orig = sandwich(_R, _v)
    _new = sandwich(_R_composed, _v)

    _fig = plt.figure(figsize=(7, 7))
    _ax = _fig.add_subplot(111, projection="3d")

    def _arrow(ax, vec, color, label):
        x, y, z = vec.vector_part
        ax.quiver(0, 0, 0, x, y, z, color=color, arrow_length_ratio=0.1, linewidth=2, label=label)

    _arrow(_ax, _v, "gray", "$e_1$")
    _arrow(_ax, _orig, "steelblue", "$Re_1\\tilde{R}$")
    _arrow(_ax, _new, "crimson", "$(SR)e_1(SR)^\\sim$")

    _ax.set_xlim([-1.2, 1.2])
    _ax.set_ylim([-1.2, 1.2])
    _ax.set_zlim([-1.2, 1.2])
    _ax.set_xlabel("$e_1$")
    _ax.set_ylabel("$e_2$")
    _ax.set_zlabel("$e_3$")
    _ax.legend(fontsize=10)
    _ax.set_title(f"Composed rotation: θ={rr_theta.value}°, α={rr_alpha.value}°", fontsize=12)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rotating a Rotor Generator (Bivector)

    Instead of rotating the rotor, we can rotate its **generator** — the bivector $B$
    that defines the rotation plane. If $B' = S\,B\,\tilde{S}$, then
    $\exp(-\theta/2\,\hat{B'})$ rotates by the same angle $\theta$ but in the new plane.

    This is how you re-orient a rotation axis in 3D: rotate the bivector, then
    exponentiate.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    gen_alpha = mo.ui.slider(start=0, stop=360, step=1, value=0, label="α — rotate the generator (degrees)")
    gen_theta = mo.ui.slider(start=0, stop=180, step=1, value=90, label="θ — rotation angle (degrees)")
    mo.vstack([gen_theta, gen_alpha])
    return gen_alpha, gen_theta


@app.cell(hide_code=True)
def _(cl3, e1, e2, e3, exp, gen_alpha, gen_theta, gm, mo, np, sandwich, unit):
    _B = e1 ^ e2
    _S = cl3.rotor(e2 ^ e3, degrees=gen_alpha.value)
    _B_rotated = sandwich(_S, _B)

    _theta = np.radians(gen_theta.value)
    _R_orig = exp(-_theta / 2 * unit(_B))
    _R_new = exp(-_theta / 2 * unit(_B_rotated))

    _v = e1
    _result_orig = sandwich(_R_orig, _v)
    _result_new = sandwich(_R_new, _v)

    mo.vstack([
        gm.md(t"Generator $B = e_1 e_2$: {_B}"),
        gm.md(t"Rotated generator $B' = S B \\tilde{{S}}$: {_B_rotated}"),
        gm.md(t"$R = \\exp(-\\theta/2\\,\\hat{{B}})$: {_R_orig}"),
        gm.md(t"$R' = \\exp(-\\theta/2\\,\\hat{{B'}})$: {_R_new}"),
        gm.md(t"$R\\,e_1\\,\\tilde{{R}} =$ {_result_orig}"),
        gm.md(t"$R'\\,e_1\\,\\tilde{{R'}} =$ {_result_new}"),
    ])
    return


@app.cell(hide_code=True)
def _(cl3, e1, e2, e3, exp, gen_alpha, gen_theta, np, plt, sandwich, unit):
    _B = e1 ^ e2
    _S = cl3.rotor(e2 ^ e3, degrees=gen_alpha.value)
    _B_rot = sandwich(_S, _B)

    _theta = np.radians(gen_theta.value)
    _R_orig = exp(-_theta / 2 * unit(_B))
    _R_new = exp(-_theta / 2 * unit(_B_rot))

    _v = e1
    _r_orig = sandwich(_R_orig, _v)
    _r_new = sandwich(_R_new, _v)

    _fig = plt.figure(figsize=(7, 7))
    _ax = _fig.add_subplot(111, projection="3d")

    def _arrow(ax, vec, color, label):
        x, y, z = vec.vector_part
        ax.quiver(0, 0, 0, x, y, z, color=color, arrow_length_ratio=0.1, linewidth=2, label=label)

    _arrow(_ax, _v, "gray", "$e_1$")
    _arrow(_ax, _r_orig, "steelblue", "Original plane")
    _arrow(_ax, _r_new, "crimson", "Rotated generator")

    _ax.set_xlim([-1.2, 1.2])
    _ax.set_ylim([-1.2, 1.2])
    _ax.set_zlim([-1.2, 1.2])
    _ax.set_xlabel("$e_1$")
    _ax.set_ylabel("$e_2$")
    _ax.set_zlabel("$e_3$")
    _ax.legend(fontsize=10)
    _ax.set_title(f"Rotating the generator: θ={gen_theta.value}°, α={gen_alpha.value}°", fontsize=12)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Spacetime Algebra — $\mathrm{Cl}(1,3)$

    In STA, bivectors split into two families:
    - **Spacelike** ($\gamma_i\gamma_j$, square $= -1$): generate spatial rotations (circular)
    - **Timelike** ($\gamma_0\gamma_i$, square $= +1$): generate Lorentz boosts (hyperbolic)

    The rotor formula adapts automatically:
    - Spacelike: $R = \cos(\varphi/2) - \sin(\varphi/2)\,\hat{B}$
    - Timelike: $R = \cosh(\varphi/2) + \sinh(\varphi/2)\,\hat{B}$

    Both are just `exp(B)` — the algebra handles the sign.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors()
    return g0, g1, g2, g3, sta


@app.cell
def _(g0, g1, g2, g3, gm, scalar):
    _bivectors = [
        ("γ₁γ₂ (spacelike)", g1 * g2),
        ("γ₁γ₃ (spacelike)", g1 * g3),
        ("γ₂γ₃ (spacelike)", g2 * g3),
        ("γ₀γ₁ (timelike)", g0 * g1),
        ("γ₀γ₂ (timelike)", g0 * g2),
        ("γ₀γ₃ (timelike)", g0 * g3),
    ]
    _lines = "\n".join(f"- {name}: $B^2 = {scalar(b * b):+.0f}$" for name, b in _bivectors)
    gm.md(t"{_lines:text}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Spatial Rotation in STA

    Rotating $\gamma_1$ in the $\gamma_1\gamma_2$ plane — same circular rotor as Euclidean 3D.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    sta_rot = mo.ui.slider(start=0, stop=360, step=1, value=90, label="θ (degrees)")
    sta_rot
    return (sta_rot,)


@app.cell
def _(g1, g2, gm, mo, np, sandwich, scalar, sta, sta_rot):
    _theta = np.radians(sta_rot.value)
    _R = sta.rotor(g1 ^ g2, radians=_theta)
    _result = sandwich(_R, g1)
    _RR = scalar(_R * ~_R)

    mo.vstack([
        gm.md(t"$\\theta = {sta_rot.value}°$"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$R\\,\\gamma_1\\,\\tilde{{R}} =$ {_result}"),
        gm.md(t"$R\\tilde{{R}} = {_RR:.4f}$"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Lorentz Boost

    Boosting $\gamma_0$ along $\gamma_1$ with a timelike bivector $\gamma_0\gamma_1$.
    The rotor uses hyperbolic functions because $(\gamma_0\gamma_1)^2 = +1$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    boost_phi = mo.ui.slider(start=0.0, stop=3.0, step=0.05, value=0.5, label="Rapidity φ")
    boost_phi
    return (boost_phi,)


@app.cell
def _(boost_phi, exp, g0, g1, gm, mo, np, sandwich, scalar):
    _phi = boost_phi.value
    _B = g0 * g1
    _R = exp(_phi / 2 * _B)

    _g0_boosted = sandwich(_R, g0)
    _g1_boosted = sandwich(_R, g1)

    _beta = np.tanh(_phi)
    _gamma = np.cosh(_phi)
    _RR = scalar(_R * ~_R)

    mo.vstack([
        gm.md(t"$\\varphi = {_phi:.2f}$"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$\\gamma_0' =$ {_g0_boosted}"),
        gm.md(t"$\\gamma_1' =$ {_g1_boosted}"),
        gm.md(t"$\\beta = v/c = {_beta:.4f}$, $\\gamma = {_gamma:.4f}$"),
        gm.md(t"$R\\tilde{{R}} = {_RR:.4f}$"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Rotating a Boost

    To re-orient a boost, compose it with a spatial rotation: $R' = SR$.

    Start with a boost along $\gamma_1$, then compose with a rotation by $\alpha$ in the
    $\gamma_1\gamma_2$ plane to boost in a new spatial direction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    rb_phi = mo.ui.slider(start=0.0, stop=2.0, step=0.05, value=0.8, label="Rapidity φ")
    rb_alpha = mo.ui.slider(start=0, stop=360, step=1, value=0, label="α — rotate boost direction (degrees)")
    mo.vstack([rb_phi, rb_alpha])
    return rb_alpha, rb_phi


@app.cell
def _(exp, g0, g1, g2, gm, mo, rb_alpha, rb_phi, sandwich, sta):
    _B_boost = g0 * g1
    _R_boost = exp(rb_phi.value / 2 * _B_boost)

    _S = sta.rotor(g1 ^ g2, degrees=rb_alpha.value)
    _R_rotated = _S * _R_boost

    _g0_orig = sandwich(_R_boost, g0)
    _g0_new = sandwich(_R_rotated, g0)

    mo.vstack([
        gm.md(t"Boost rotor (along $\\gamma_1$): {_R_boost}"),
        gm.md(t"Spatial rotation $S$ ({rb_alpha.value}° in $\\gamma_1\\gamma_2$): {_S}"),
        gm.md(t"Composed $SR$: {_R_rotated}"),
        gm.md(t"$\\gamma_0'$ (original boost): {_g0_orig}"),
        gm.md(t"$\\gamma_0'$ (rotated boost): {_g0_new}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Rotating a Boost Generator

    Alternatively, rotate the timelike bivector $\gamma_0\gamma_1$ itself, then
    exponentiate. The rotated bivector $B' = S\,(\gamma_0\gamma_1)\,\tilde{S}$
    is still timelike ($B'^2 = +1$), so it still generates a boost — just in a
    different direction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    bg_alpha = mo.ui.slider(start=0, stop=360, step=1, value=0, label="α — rotate generator (degrees)")
    bg_phi = mo.ui.slider(start=0.0, stop=2.0, step=0.05, value=0.8, label="Rapidity φ")
    mo.vstack([bg_phi, bg_alpha])
    return bg_alpha, bg_phi


@app.cell
def _(bg_alpha, bg_phi, exp, g0, g1, g2, gm, mo, sandwich, scalar, sta, unit):
    _B = g0 * g1
    _S = sta.rotor(g1 ^ g2, degrees=bg_alpha.value)
    _B_rot = sandwich(_S, _B)

    _R = exp(bg_phi.value / 2 * unit(_B_rot))

    _g0_boosted = sandwich(_R, g0)

    _B_rot_sq = scalar(_B_rot * _B_rot)
    mo.vstack([
        gm.md(t"Original generator: {_B}"),
        gm.md(t"Rotated generator $B'$: {_B_rot}"),
        gm.md(t"$B'^2 = {_B_rot_sq:+.4f}$ (still timelike)"),
        gm.md(t"Boost rotor $\\exp(\\varphi/2\\,\\hat{{B'}})$: {_R}"),
        gm.md(t"$\\gamma_0'$: {_g0_boosted}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Minkowski Diagram — Boost Direction

    Visualizing how rotating the boost generator changes the direction of the
    boosted timelike vector in the $\gamma_1$-$\gamma_2$ spatial plane.
    """)
    return


@app.cell(hide_code=True)
def _(bg_alpha, bg_phi, exp, g0, g1, g2, np, plt, sandwich, sta, unit):
    _B = g0 * g1
    _S = sta.rotor(g1 ^ g2, degrees=bg_alpha.value)
    _B_rot = sandwich(_S, _B)
    _R = exp(bg_phi.value / 2 * unit(_B_rot))

    _g0b = sandwich(_R, g0)
    # Extract time (g0=index 1), space-x (g1=index 2), space-y (g2=index 4)
    _t = _g0b.data[1]
    _x = _g0b.data[2]
    _y = _g0b.data[4]

    _fig, _axes = plt.subplots(1, 2, figsize=(11, 5))

    # Left: t-x Minkowski diagram
    _ax = _axes[0]
    _lc = np.linspace(-2.5, 2.5, 100)
    _ax.plot(_lc, _lc, "k--", alpha=0.3)
    _ax.plot(_lc, -_lc, "k--", alpha=0.3)
    _ax.quiver(0, 0, 0, 2, angles="xy", scale_units="xy", scale=1,
               color="steelblue", width=0.015, label="$\\gamma_0$")
    _ax.quiver(0, 0, _x * 2, _t * 2, angles="xy", scale_units="xy", scale=1,
               color="crimson", width=0.015, label="$\\gamma_0'$")
    _ax.set_xlim(-2.5, 2.5)
    _ax.set_ylim(-0.5, 3)
    _ax.set_aspect("equal")
    _ax.set_xlabel("space")
    _ax.set_ylabel("time")
    _ax.legend(fontsize=10)
    _ax.set_title("Minkowski (t-x)")
    _ax.grid(True, alpha=0.2)

    # Right: spatial projection (x-y)
    _ax2 = _axes[1]
    _ax2.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1,
                color="steelblue", width=0.02, label="$\\gamma_1$")
    _ax2.quiver(0, 0, 0, 1, angles="xy", scale_units="xy", scale=1,
                color="steelblue", width=0.02, alpha=0.5, label="$\\gamma_2$")
    if abs(_x) + abs(_y) > 1e-6:
        _norm = np.sqrt(_x**2 + _y**2)
        _ax2.quiver(0, 0, _x / _norm, _y / _norm, angles="xy", scale_units="xy", scale=1,
                    color="crimson", width=0.02, label="boost direction")
    _circ = np.linspace(0, 2 * np.pi, 100)
    _ax2.plot(np.cos(_circ), np.sin(_circ), "k-", alpha=0.1)
    _ax2.set_xlim(-1.4, 1.4)
    _ax2.set_ylim(-1.4, 1.4)
    _ax2.set_aspect("equal")
    _ax2.set_xlabel("$\\gamma_1$")
    _ax2.set_ylabel("$\\gamma_2$")
    _ax2.legend(fontsize=10)
    _ax2.set_title("Spatial boost direction")
    _ax2.grid(True, alpha=0.2)

    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Symbolic Rotor Identities

    The symbolic layer verifies key rotor identities as expression trees.
    """)
    return


@app.cell
def _(cl3, e1, e2, gm, simplify, sinverse, snorm, sunit, sym):
    _R = sym(cl3.rotor(e1 ^ e2, radians=0.7), "R")
    _v = sym(e1, "v")

    _rules = [
        ("R̃̃ = R (double reverse)", simplify(~~_R)),
        ("RR̃ = 1 (normalization)", simplify(_R * ~_R)),
        ("inv(inv(v)) = v", simplify(sinverse(sinverse(_v)))),
        ("‖unit(v)‖ = 1", simplify(snorm(sunit(_v)))),
    ]

    _lines = "\n".join(f"- {name}: ${result.latex()}$" for name, result in _rules)
    gm.md(t"{_lines:text}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
