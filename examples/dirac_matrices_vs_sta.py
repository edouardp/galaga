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

    from ga import Algebra, exp, sandwich
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dirac Matrices vs Spacetime Algebra

    This notebook compares two ways of expressing the same relativistic spin-1/2
    structure:

    - **matrix language:** $4 \times 4$ Dirac gamma matrices acting on bispinors
    - **STA language:** basis vectors and even multivectors in $\mathrm{Cl}(1,3)$

    The purpose is not to "replace" one formalism with the other in every context.
    The point is to show how much of the matrix machinery is really the spacetime
    geometric algebra written in a particular representation.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, g3


@app.cell
def _(np):
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    eye2 = np.eye(2, dtype=complex)

    gamma0 = np.block([[eye2, zero], [zero, -eye2]])
    gamma1 = np.block([[zero, sigma_x], [-sigma_x, zero]])
    gamma2 = np.block([[zero, sigma_y], [-sigma_y, zero]])
    gamma3 = np.block([[zero, sigma_z], [-sigma_z, zero]])
    eye4 = np.eye(4, dtype=complex)
    return gamma0, gamma1, gamma2, gamma3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Gamma Algebra

    The Dirac matrices satisfy

    $$
    \{\Gamma_\mu,\Gamma_\nu\} = 2 \eta_{\mu\nu} I_4.
    $$

    In STA the basis vectors satisfy the same Clifford relation directly:

    $$
    \gamma_\mu \gamma_\nu + \gamma_\nu \gamma_\mu = 2 \eta_{\mu\nu}.
    $$

    The matrix algebra is a representation. The STA basis vectors are the algebra.
    """)
    return


@app.cell
def _(g0, g1, g2, g3, gamma0, gamma1, gamma2, gamma3, gm):
    _anticomm_01 = gamma0 @ gamma1 + gamma1 @ gamma0
    gm.md(t"""
    | Object | Matrix side | STA side |
    |---|---|---|
    | $\\Gamma_0$ / $\\gamma_0$ | `{gamma0}` | {g0} = {g0.eval()} |
    | $\\Gamma_1$ / $\\gamma_1$ | `{gamma1}` | {g1} = {g1.eval()} |
    | $\\Gamma_2$ / $\\gamma_2$ | `{gamma2}` | {g2} = {g2.eval()} |
    | $\\Gamma_3$ / $\\gamma_3$ | `{gamma3}` | {g3} = {g3.eval()} |
    | $\\{{\\Gamma_0,\\Gamma_1\\}}$ / $\\gamma_0\\gamma_1 + \\gamma_1\\gamma_0$ | `{_anticomm_01}` | {g0 * g1 + g1 * g0} = {(g0 * g1 + g1 * g0).eval()} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Boost in Both Languages

    A boost in the $x$ direction with rapidity $\varphi$ is

    $$
    R = e^{(\varphi/2)\gamma_0\gamma_1}
    $$

    in STA.

    In the standard Dirac representation, the corresponding bispinor boost matrix is

    $$
    S = \cosh(\varphi/2) I_4 + \sinh(\varphi/2)\,\alpha_1,
    \qquad
    \alpha_1 = \Gamma_0 \Gamma_1.
    $$
    """)
    return


@app.cell
def _(mo):
    rapidity = mo.ui.slider(start=0.0, stop=3.0, step=0.02, value=0.9, label="boost rapidity φ")
    rapidity
    return (rapidity,)


@app.cell(hide_code=True)
def _(exp, g0, g1, gamma0, gamma1, gm, np, rapidity, sandwich):
    _phi = rapidity.value
    _R = exp((_phi / 2) * (g0 * g1))
    _boosted_time_axis = sandwich(_R, g0)
    _boosted_x_axis = sandwich(_R, g1)

    _alpha1 = gamma0 @ gamma1
    _S = np.cosh(_phi / 2) * np.eye(4, dtype=complex) + np.sinh(_phi / 2) * _alpha1
    _u_rest = np.array([[1], [0], [0], [0]], dtype=complex)
    _u_boosted = _S @ _u_rest

    gm.md(t"""
    ## Boosted Observer

    STA rotor:

    {_R} = {_R.eval()}

    Boosted time axis:

    {_boosted_time_axis} = {_boosted_time_axis.eval()}

    Boosted space axis:

    {_boosted_x_axis} = {_boosted_x_axis.eval()}

    Dirac boost matrix:

    `{_S}`

    Boosted rest bispinor:

    $$
    u' =
    \\begin{{pmatrix}}
    {_u_boosted[0,0].real:.6f} \\\\
    {_u_boosted[1,0].real:.6f} \\\\
    {_u_boosted[2,0].real:.6f} \\\\
    {_u_boosted[3,0].real:.6f}
    \\end{{pmatrix}}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dirac Operator vs STA Vector

    Matrix language often starts from the slashed operator

    $$
    \Gamma^\mu p_\mu - m.
    $$

    In STA the same momentum is just a spacetime vector

    $$
    p = E \gamma_0 + p_x \gamma_1 + p_y \gamma_2 + p_z \gamma_3.
    $$

    The on-shell condition is then the geometric statement

    $$
    p^2 = m^2.
    $$
    """)
    return


@app.cell
def _(mo):
    mass = mo.ui.slider(start=0.1, stop=5.0, step=0.1, value=1.0, label="mass m")
    px = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=0.8, label="momentum p_x")
    py = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=0.0, label="momentum p_y")
    pz = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=0.0, label="momentum p_z")
    mo.vstack([mass, px, py, pz])
    return mass, px, py, pz


@app.cell(hide_code=True)
def _(
    g0,
    g1,
    g2,
    g3,
    gamma0,
    gamma1,
    gamma2,
    gamma3,
    gm,
    mass,
    np,
    px,
    py,
    pz,
):
    _m = mass.value
    _px = px.value
    _py = py.value
    _pz = pz.value
    _E = np.sqrt(_m**2 + _px**2 + _py**2 + _pz**2)

    _p = _E * g0 + _px * g1 + _py * g2 + _pz * g3
    _slash = _E * gamma0 - _px * gamma1 - _py * gamma2 - _pz * gamma3
    _dirac_op = _slash - _m * np.eye(4, dtype=complex)

    gm.md(t"""
    Momentum vector in STA:

    {_p} = {_p.eval()}

    $p^2 = {(_p * _p).eval()}$

    Dirac operator matrix $(\\Gamma^\\mu p_\\mu - m)$:

    `{_dirac_op}`

    The matrix side packages the same on-shell momentum information in operator form.
    """)
    return


@app.cell
def _(np, plt, rapidity):
    _time = _boosted_time_axis.eval().vector_part[:2]
    _space = _boosted_x_axis.eval().vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6.5, 6.5))
    _cone = np.linspace(-2.2, 2.2, 200)
    _ax.plot(_cone, _cone, "k--", alpha=0.25)
    _ax.plot(_cone, -_cone, "k--", alpha=0.25)
    _ax.quiver(0, 0, 0, 1.6, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, 1.6, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, 1.6 * _time[0], 1.6 * _time[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, 1.6 * _space[0], 1.6 * _space[1], angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-2.2, 2.2)
    _ax.set_ylim(-2.2, 2.2)
    _ax.set_xlabel("$x$")
    _ax.set_ylabel("$t$")
    _ax.set_title(f"STA boost geometry at φ = {rapidity.value:.2f}, on-shell E = {_E:.3f}")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
