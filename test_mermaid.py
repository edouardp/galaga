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
    return g0, g1, g3, sta


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


if __name__ == "__main__":
    app.run()
