import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, exp, sandwich, scalar
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich, scalar


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Special Relativity with Lazy STA Blades

    This notebook treats Lorentz boosts as rotor sandwiches in spacetime algebra
    `Cl(1,3)`. The emphasis is on the library workflow:

    1. build expressions from **lazy named basis blades**
    2. inspect the symbolic construction
    3. call `.eval()` when you want the concrete multivector

    Rapidity is the natural parameter. In GA it appears in the rotor directly,
    so Einstein velocity addition becomes ordinary addition of boost generators.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    I = sta.I.name("I")
    return g0, g1, g2, g3


@app.cell
def _(g0, g1, g2, g3, gm, scalar):
    _basis_rows = [
        f"- {g0}: {g0 * g0} = {(g0 * g0).eval()}",
        f"- {g1}: {g1 * g1} = {(g1 * g1).eval()}",
        f"- {g2}: {g2 * g2} = {(g2 * g2).eval()}",
        f"- {g3}: {g3 * g3} = {(g3 * g3).eval()}",
        f"- Boost generator {g0 * g1}: {(g0 * g1).eval()} with square {scalar((g0 * g1).eval() * (g0 * g1).eval()):+.0f}",
    ]
    gm.md(t"""
    ## Metric and Boost Generator

    {"\n".join(_basis_rows):text}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## One Boost

    The boost rotor in the `γ₀γ₁` plane is

    $$
    \Lambda(    arphi) = e^{(    arphi/2)\,\gamma_0 \gamma_1}.
    $$

    The same symbolic object can be read two ways:

    - as an algebraic expression tree
    - as a concrete multivector after evaluation
    """)
    return


@app.cell
def _(mo):
    rapidity = mo.ui.slider(start=-2.5, stop=2.5, step=0.05, value=0.9, label="rapidity φ")
    rapidity
    return (rapidity,)


@app.cell
def _(exp, g0, g1, gm, np, rapidity, sandwich):
    phi = rapidity.value
    half_phi = (phi / 2) * (1 + 0 * g0).name("φ/2", latex=r"\varphi/2")
    Bx = (g0 * g1).name("B_x", latex=r"\gamma_0 \gamma_1")
    Lambda = exp(half_phi * Bx).name("Λ", latex=r"\Lambda")
    time_axis = sandwich(Lambda, g0).name(latex=r"\gamma_0'")
    space_axis = sandwich(Lambda, g1).name(latex=r"\gamma_1'")
    beta = np.tanh(phi)
    gamma = np.cosh(phi)

    gm.md(t"""
    {Bx} = {Bx.eval()}

    {Lambda} = {Lambda.eval()}

    {time_axis} = {time_axis.eval()}

    {space_axis} = {space_axis.eval()}

    $\\beta = \\tanh \\varphi = {beta:.4f}$, $\\gamma = \\cosh \\varphi = {gamma:.4f}$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Minkowski Diagram

    The boosted basis vectors tilt toward the light cone. Because the boost is a
    rotor sandwich, orthogonality and normalization are preserved automatically.
    """)
    return


@app.cell
def _(exp, g0, g1, np, plt, rapidity, sandwich):
    _phi = rapidity.value
    _Lambda = exp((_phi / 2) * (g0 * g1))
    _g0p = sandwich(_Lambda, g0).eval()
    _g1p = sandwich(_Lambda, g1).eval()
    _t0, _x0 = _g0p.data[1], _g0p.data[2]
    _t1, _x1 = _g1p.data[1], _g1p.data[2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _cone = np.linspace(-2.2, 2.2, 100)
    _ax.plot(_cone, _cone, "k--", alpha=0.35)
    _ax.plot(_cone, -_cone, "k--", alpha=0.35)
    _ax.quiver(0, 0, 0, 1.8, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.01)
    _ax.quiver(0, 0, 1.8, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.01)
    _ax.quiver(0, 0, 1.8 * _x0, 1.8 * _t0, angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, 1.8 * _x1, 1.8 * _t1, angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.012)
    _ax.text(0.08, 1.9, r"$\gamma_0$", color="steelblue")
    _ax.text(1.85, 0.08, r"$\gamma_1$", color="steelblue")
    _ax.text(1.8 * _x0 + 0.05, 1.8 * _t0 + 0.05, r"$\gamma_0'$", color="crimson")
    _ax.text(1.8 * _x1 + 0.05, 1.8 * _t1 + 0.05, r"$\gamma_1'$", color="darkorange")
    _ax.set_xlim(-2.3, 2.3)
    _ax.set_ylim(-2.3, 2.3)
    _ax.set_aspect("equal")
    _ax.set_xlabel("$x$")
    _ax.set_ylabel("$t$")
    _ax.set_title(f"Minkowski diagram for φ = {_phi:.2f}")
    _ax.grid(True, alpha=0.2)
    _fig


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Velocity Addition

    Compose two boosts in the same plane. In rapidity language the result is
    immediate:

    $$
    \Lambda(    arphi_2)\Lambda(    arphi_1) = \Lambda(    arphi_1 +     arphi_2).
    $$

    The symbolic expression shows the composition, and `.eval()` confirms the
    numeric result.
    """)
    return


@app.cell
def _(mo):
    phi_one = mo.ui.slider(start=-1.5, stop=1.5, step=0.05, value=0.5, label="φ₁")
    phi_two = mo.ui.slider(start=-1.5, stop=1.5, step=0.05, value=0.7, label="φ₂")
    mo.vstack([phi_one, phi_two])
    return phi_one, phi_two


@app.cell
def _(exp, g0, g1, gm, np, phi_one, phi_two):
    _phi1 = phi_one.value
    _phi2 = phi_two.value
    _B = (g0 * g1).name("B", latex=r"\gamma_0 \gamma_1")
    _L1 = exp((_phi1 / 2) * _B).name(latex=r"\Lambda_1")
    _L2 = exp((_phi2 / 2) * _B).name(latex=r"\Lambda_2")
    _composed = (_L2 * _L1).name(latex=r"\Lambda_2 \Lambda_1")
    _direct = exp(((_phi1 + _phi2) / 2) * _B).name(latex=r"\Lambda(\varphi_1+\varphi_2)")
    _beta_rel = (_phi1 + _phi2)
    _beta = np.tanh(_beta_rel)
    _beta1 = np.tanh(_phi1)
    _beta2 = np.tanh(_phi2)
    _einstein = (_beta1 + _beta2) / (1 + _beta1 * _beta2)

    gm.md(t"""
    {_L1} = {_L1.eval()}

    {_L2} = {_L2.eval()}

    {_composed} = {_composed.eval()}

    {_direct} = {_direct.eval()}

    $\\tanh(\\varphi_1 + \\varphi_2) = {_beta}$ and Einstein addition gives { _einstein}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
