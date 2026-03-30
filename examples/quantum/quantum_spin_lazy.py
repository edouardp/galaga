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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Quantum Spin with Lazy Pauli Blades

    For a single spin-1/2 system, a normalized rotor in `Cl(3,0)` plays the role
    of a pure state. The observable spin direction is the rotated reference vector
    `ψ e₃ ψ̃`.

    This notebook is deliberately explicit about the symbolic construction so that
    the state-preparation pipeline is visible before evaluation.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    I = alg.I.name("I")
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm):
    _rows = [
        f"- {e1}: {e1 * e1} = {(e1 * e1).eval()}",
        f"- {e2}: {e2 * e2} = {(e2 * e2).eval()}",
        f"- {e3}: {e3 * e3} = {(e3 * e3).eval()}",
        f"- {(e1 ^ e2).name(latex=r'e_{12}')}: {((e1 ^ e2) * (e1 ^ e2)).eval()}",
    ]
    gm.md(t"""
    ## Spin Algebra

    {"\n".join(_rows):text}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Prepare a Spin State

    Start from `e₃` and rotate it by a polar tilt and an azimuth. The rotor
    construction mirrors the usual Bloch sphere coordinates.
    """)
    return


@app.cell
def _(mo):
    theta = mo.ui.slider(start=0, stop=180, step=1, value=55, label="polar angle θ")
    phi = mo.ui.slider(start=0, stop=360, step=1, value=35, label="azimuth φ")
    mo.vstack([theta, phi])
    return phi, theta


@app.cell
def _(e1, e2, e3, exp, gm, np, phi, theta):
    _theta = np.radians(theta.value)
    _phi = np.radians(phi.value)
    R_theta = exp((-_theta / 2) * (e3 * e1)).name(latex=r"R_\theta")
    R_phi = exp((-_phi / 2) * (e1 * e2)).name(latex=r"R_\phi")
    psi = (R_phi * R_theta).name("ψ", latex=r"\psi")
    spin = (psi * e3 * ~psi).name("s", latex=r"\mathbf{s}")

    gm.md(t"""
    {R_theta} = {R_theta.eval()}

    {R_phi} = {R_phi.eval()}

    {psi} = {psi.eval()}

    {spin} = {spin.eval()}
    """)
    return (spin,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Stern-Gerlach Measurement

    Measuring along a unit axis `a` gives the probabilities

    $$
    P_\pm =
    rac{1 \pm s \cdot a}{2}.
    $$

    In GA the expectation value is the scalar part of the geometric product of
    the spin vector with the measurement axis.
    """)
    return


@app.cell
def _(mo):
    meas = mo.ui.slider(start=0, stop=360, step=1, value=110, label="measurement axis in x-z plane")
    return (meas,)


@app.cell
def _(e1, e3, gm, meas, np, spin):
    _alpha = np.radians(meas.value)
    axis = (np.sin(_alpha) * e1 + np.cos(_alpha) * e3).name("a", latex=r"\mathbf{a}")
    overlap = ((spin * axis).eval()).scalar_part
    p_plus = 0.5 * (1 + overlap)
    p_minus = 0.5 * (1 - overlap)

    gm.md(t"""
    {axis} = {axis.eval()}

    $\\langle s a \\rangle_0 = {overlap:.4f}$

    $P_+ = {p_plus:.4f}$, $\\quad$ $P_- = {p_minus:.4f}$
    """)
    return axis, p_minus, p_plus


@app.cell
def _(axis, np, p_minus, p_plus, plt, spin):
    _s = spin.eval().vector_part
    _a = axis.eval().vector_part
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, _s[0], _s[1], _s[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, _a[0], _a[1], _a[2], color="steelblue", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title(f"Spin state and measurement axis\nP+={p_plus:.3f}, P-={p_minus:.3f}")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
