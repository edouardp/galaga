import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_mermaid import mv_to_mermaid

    import galaga_marimo as gm
    from galaga import Algebra, exp, gp, op, sandwich, spacetime_blade_convention, unit

    return Algebra, exp, gm, gp, mo, mv_to_mermaid, np, op, sandwich, spacetime_blade_convention, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Mermaid Expression Tree Demo

    Build a rotor from two vectors, apply it via sandwich product,
    then visualise its immutable provenance as a Mermaid diagram.

    We normalise the rotation plane before exponentiating: otherwise its
    magnitude rescales the angle. Naming records reusable symbol leaves;
    it does not postpone computation or mutate the input value.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra(3)
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return alg, e1, e2, e3


@app.cell
def _(mo):
    d_slider = mo.ui.slider(start=0, stop=360, step=5, value=60, label="angle d (degrees)")
    return (d_slider,)


@app.cell
def _(alg, d_slider, e1, e2, e3, exp, np, op, unit):
    a = unit(e1 + e2).named("a")
    b = e3.named("b")
    B = op(a, b).named("B")
    np.testing.assert_allclose((B * B).data, -alg.identity.data, rtol=0, atol=1e-12)
    d = alg.scalar(np.radians(d_slider.value)).named(r"\theta", latex=r"\theta")
    R = exp(-B * d / 2).named("R")
    return B, R, a, b


@app.cell
def _(R, d_slider, e1, e2, e3, gm, mo, mv_to_mermaid, sandwich):
    v = (3 * e1 + e2 - 2 * e3).named("v")
    v_rot = sandwich(R, v).named("v'")

    _diagram = mv_to_mermaid(v_rot, compact=True)

    mo.vstack(
        [
            d_slider,
            gm.md(t"""
        {v:full}

        {v_rot:full}
        """),
            mo.mermaid(_diagram),
        ]
    )
    return v, v_rot


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Boosting an Electromagnetic Field (STA)

    In spacetime algebra Cl(1,3), the EM field is a bivector F.
    A Lorentz boost $L = \exp(\gamma_0\gamma_3\phi/2)$ transforms it via
    $F' = L F \widetilde L$. For this field, $F^2$ is a scalar, so the
    invariant is directly visible. The notebook checks all coefficients.
    """)
    return


@app.cell
def _(Algebra, spacetime_blade_convention):
    sta = Algebra((1, -1, -1, -1), blades=spacetime_blade_convention())
    g0, g1, g2, g3 = sta.basis_vectors(expr=True)
    return g0, g1, g2, g3, sta


@app.cell
def _(mo):
    phi_slider = mo.ui.slider(start=0, stop=2.0, step=0.05, value=0.6, label="rapidity φ")
    return (phi_slider,)


@app.cell
def _(exp, g0, g1, g3, gm, gp, mo, mv_to_mermaid, np, phi_slider, sandwich, sta):
    _F = (2.0 * (g0 * g1) + 0.5 * (g1 * g3)).named("F")
    _phi = sta.scalar(phi_slider.value).named(r"\phi", latex=r"\phi")
    _L = exp(g0 * g3 * _phi / 2).named("L")
    _F_prime = sandwich(_L, _F).named(r"F'", latex=r"F'")
    _F_sq = gp(_F, _F).named(r"F^2", latex=r"F^2")
    _F_prime_sq = gp(_F_prime, _F_prime).named(r"F'^2", latex=r"F'^2")
    np.testing.assert_allclose(_F_prime_sq.data, _F_sq.data, atol=1e-12)
    em_field, boosted_field = _F, _F_prime

    _diagram = mv_to_mermaid(_F_prime, compact=True)

    mo.vstack(
        [
            phi_slider,
            gm.md(t"""
        {_F:full}

        {_L:full}

        {_F_prime:full}

        {_F_sq:full}

        {_F_prime_sq:full} — Lorentz invariant preserved
        """),
            mo.mermaid(_diagram),
        ]
    )
    return boosted_field, em_field


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Thomas-Wigner Rotation

    Two non-collinear boosts don't compose to a pure boost — there's a leftover
    spatial rotation. Factor the composite rotor $R = R_y R_x$ into a pure boost
    $L$ and a residual Wigner rotation $W = \widetilde{L} R$.
    """)
    return


@app.cell
def _(mo):
    tw_phi_x = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.7, label="x-rapidity")
    tw_phi_y = mo.ui.slider(start=0.0, stop=2.0, step=0.02, value=0.9, label="y-rapidity")
    return tw_phi_x, tw_phi_y


@app.cell
def _(
    exp,
    g0,
    g1,
    g2,
    gm,
    mo,
    mv_to_mermaid,
    np,
    sandwich,
    sta,
    tw_phi_x,
    tw_phi_y,
    unit,
):
    _Bx = (g0 * g1).named(r"B_x", latex=r"B_x", unicode="Bₓ")
    _By = (g0 * g2).named(r"B_y", latex=r"B_y", unicode="Bᵧ")
    _phi_x = sta.scalar(tw_phi_x.value).named(r"\phi_x", latex=r"\phi_x", unicode="ϕₓ")
    _phi_y = sta.scalar(tw_phi_y.value).named(r"\phi_y", latex=r"\phi_y", unicode="ϕᵧ")
    _Rx = exp(_phi_x / 2 * _Bx).named(r"R_x", latex=r"R_x", unicode="Rₓ")
    _Ry = exp(_phi_y / 2 * _By).named(r"R_y", latex=r"R_y", unicode="Rᵧ")
    _R = (_Ry * _Rx).named("R")

    _u = sandwich(_R, g0).named("u")
    _L = unit(1 + _u * g0).named("L")
    _W = (~_L * _R).named("W")
    np.testing.assert_allclose(sandwich(_W, g0).data, g0.data, atol=1e-12)
    np.testing.assert_allclose((_L * _W).data, _R.data, atol=1e-12)
    composite_boost, pure_boost, wigner_rotor = _R, _L, _W

    _direction = sandwich(_W, g1).vector_part
    wigner_angle = np.degrees(np.arctan2(_direction[2], _direction[1]))

    _diagram = mv_to_mermaid(_W, compact=True)

    mo.vstack(
        [
            tw_phi_x,
            tw_phi_y,
            gm.md(t"""
        {_Rx:full}

        {_Ry:full}

        {_R:full}

        {_u:full}

        {_L:full}

        {_W:full}

        Signed Wigner angle (from the spatial x-axis toward y): **{wigner_angle:.3f}°**
        """),
            mo.mermaid(_diagram),
        ]
    )
    return composite_boost, pure_boost, wigner_angle, wigner_rotor


if __name__ == "__main__":
    app.run()
