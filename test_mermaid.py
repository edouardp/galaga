import marimo

__generated_with = "0.22.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent)
    _gamo = str(Path(__file__).resolve().parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from galaga import Algebra, exp, gp, op, sandwich
    from galaga.blade_convention import b_sta
    from galaga.mermaid import mv_to_mermaid

    return Algebra, b_sta, exp, gp, mo, mv_to_mermaid, np, op, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Mermaid Expression Tree Demo

    Build a rotor from two vectors, apply it via sandwich product,
    then visualise the full expression tree as a Mermaid diagram.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra(3, repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return alg, e1, e2, e3


@app.cell
def _(mo):
    d_slider = mo.ui.slider(start=0, stop=360, step=5, value=60, label="angle d (degrees)")
    return (d_slider,)


@app.cell
def _(alg, d_slider, e1, e2, e3, exp, np, op):
    a = (e1 + e2).name("a")
    b = e3.eval().name("b")
    B = op(a, b).name("B")
    d = alg.scalar(np.radians(d_slider.value)).name(latex=r"\theta")
    R = exp(-B * d / 2).name("R")
    return (R,)


@app.cell
def _(R, d_slider, e1, e2, e3, mo, mv_to_mermaid, sandwich):
    v = (3 * e1 + e2 - 2 * e3).name("v")
    v_rot = sandwich(R, v).name("v'")

    _diagram = mv_to_mermaid(v_rot, compact=True)

    mo.vstack(
        [
            d_slider,
            mo.md(
                f"""
        ${v.display()}$ <br/>
        ${v_rot.display()}$ <br/>
        """
            ),
            mo.mermaid(_diagram),
        ]
    )
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Boosting an Electromagnetic Field (STA)

    In spacetime algebra Cl(1,3), the EM field is a bivector F.
    A Lorentz boost L = exp(γ₀γ₃ φ/2) transforms it via F′ = L F L̃.
    The Lorentz invariant F² is preserved.
    """)
    return


@app.cell
def _(Algebra, b_sta):
    sta = Algebra((1, -1, -1, -1), repr_unicode=True, blades=b_sta())
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, g3, sta


@app.cell
def _(mo):
    phi_slider = mo.ui.slider(start=0, stop=2.0, step=0.05, value=0.6, label="rapidity φ")
    return (phi_slider,)


@app.cell
def _(exp, g0, g1, g3, gp, mo, mv_to_mermaid, phi_slider, sandwich, sta):
    _F = (2.0 * (g0 * g1) + 0.5 * (g1 * g3)).name("F")
    _phi = sta.scalar(phi_slider.value).name(latex=r"\phi")
    _L = exp(g0 * g3 * _phi / 2).name("L")
    _F_prime = sandwich(_L, _F).name(latex=r"F'")
    _F_sq = gp(_F, _F).name(latex=r"F^2")
    _F_prime_sq = gp(_F_prime, _F_prime).name(latex=r"F'^2")

    _diagram = mv_to_mermaid(_F_prime, compact=True)

    mo.vstack(
        [
            phi_slider,
            mo.md(
                f"""
        ${_F.display()}$ <br/>
        ${_L.display()}$ <br/>
        ${_F_prime.display()}$ <br/>
        ${_F_sq.display()}$ <br/>
        ${_F_prime_sq.display()}$ ← Lorentz invariant preserved
        """
            ),
            mo.mermaid(_diagram),
        ]
    )
    return


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
    mo,
    mv_to_mermaid,
    np,
    sandwich,
    sta,
    tw_phi_x,
    tw_phi_y,
):
    from galaga import unit

    _Bx = (g0 * g1).name(latex=r"B_x", unicode="Bₓ")
    _By = (g0 * g2).name(latex=r"B_y", unicode="Bᵧ")
    _phi_x = sta.scalar(tw_phi_x.value).name(latex=r"\phi_x", unicode="ϕₓ")
    _phi_y = sta.scalar(tw_phi_y.value).name(latex=r"\phi_y", unicode="ϕᵧ")
    _Rx = exp(_phi_x / 2 * _Bx).name(latex=r"R_x", unicode="Rₓ")
    _Ry = exp(_phi_y / 2 * _By).name(latex=r"R_y", unicode="Rᵧ")
    _R = (_Ry * _Rx).name("R")

    _u = sandwich(_R, g0).name("u")
    _L = unit(1 + _u * g0).name("L")
    _W = (~_L * _R).name("W")

    _cos = np.clip(sandwich(_W, g1).eval().vector_part[1], -1.0, 1.0)
    _angle = np.degrees(np.arccos(_cos))

    _diagram = mv_to_mermaid(_W, compact=True)

    mo.vstack(
        [
            tw_phi_x,
            tw_phi_y,
            mo.md(
                f"""
        ${_Rx.display()}$ <br/>
        ${_Ry.display()}$ <br/>
        ${_R.display()}$ <br/>
        ${_u.display()}$ <br/>
        ${_L.display()}$ <br/>
        ${_W.display()}$ <br/>
        Wigner rotation angle: **{_angle:.3f}°**
        """
            ),
            mo.mermaid(_diagram),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
