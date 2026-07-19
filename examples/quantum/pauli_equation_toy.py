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

    from galaga.facade import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Pauli Equation Toy Model

    The Pauli equation is the nonrelativistic spin sector of Dirac theory in an
    external magnetic field. In geometric algebra, spin evolution is a rotor
    problem rather than a matrix-exponential problem.

    This notebook focuses on the cleanest toy case: a uniform magnetic field and
    a single spin-1/2 state undergoing Larmor precession.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), )
    e1, e2, e3 = alg.basis_vectors(expr=True)
    I = alg.I.named("I")
    return I, e1, e2, e3


@app.cell
def _(I, e1, e2, e3, gm):
    sigma_x = e1.named(r"\sigma_1", latex=r"\sigma_1")
    sigma_y = e2.named(r"\sigma_2", latex=r"\sigma_2")
    sigma_z = e3.named(r"\sigma_3", latex=r"\sigma_3")
    generator = (I * sigma_z).named(r"I \sigma_3", latex=r"I \sigma_3")
    gm.md(rt"""
    ## Pauli Algebra

    {sigma_x} = {sigma_x:value}

    {sigma_y} = {sigma_y:value}

    {sigma_z} = {sigma_z:value}

    Field generator {generator} = {generator:value}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Time Evolution Rotor

    For a magnetic field along `e₃`, the spinor evolves as

    $$
    \psi(t) = e^{-\Omega t \, e_1 e_2 / 2}\,\psi(0).
    $$

    The bivector generator encodes the Zeeman splitting and acts as the angular
    velocity in spin space.
    """)
    return


@app.cell
def _(mo):
    omega = mo.ui.slider(start=0.1, stop=5.0, step=0.05, value=1.2, label="Larmor frequency Ω")
    tilt = mo.ui.slider(start=0, stop=180, step=1, value=60, label="initial tilt θ")
    time = mo.ui.slider(start=0.0, stop=8.0, step=0.05, value=1.7, label="time t")
    mo.vstack([omega, tilt, time])
    return omega, tilt, time


@app.cell
def _(e1, e2, e3, exp, gm, np, omega, tilt, time):
    _theta = np.radians(tilt.value)
    psi0 = exp((-_theta / 2) * (e3 * e1)).named(r"\psi_0", latex=r"\psi_0")
    propagator = exp((-(omega.value * time.value) / 2) * (e1 * e2)).named("U", latex=r"U(t)")
    psi_t = (propagator * psi0).named(r"\psi(t)", latex=r"\psi(t)")
    spin = (psi_t * e3 * ~psi_t).named("s", latex=r"\mathbf{s}(t)")

    gm.md(rt"""
    {psi0} = {psi0:value}

    {propagator} = {propagator:value}

    {psi_t} = {psi_t:value}

    {spin} = {spin:value}
    """)
    return psi0, spin


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Precession on the Bloch Sphere

    The spin vector circles the magnetic-field axis. The rotor handles the full
    time evolution, and the observable is again the sandwich `ψ e₃ ψ̃`.
    """)
    return


@app.cell(hide_code=True)
def _(e1, e2, e3, exp, np, omega, plt, psi0, spin, time):
    _s = spin.vector_part
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")

    _u = np.linspace(0, 2 * np.pi, 36)
    _v = np.linspace(0, np.pi, 18)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)

    _ts = np.linspace(0, max(4.0, time.value), 220)
    _track = []
    _spin0 = (psi0 * e3 * ~psi0).vector_part
    for _t in _ts:
        _propagator = exp((-(omega.value * _t) / 2) * (e1 * e2))
        _spin_t = (_propagator * (psi0 * e3 * ~psi0) * ~_propagator).vector_part
        _track.append([
            _spin_t[0],
            _spin_t[1],
            _spin_t[2],
        ])
    _track = np.array(_track)

    _ax.plot(_track[:, 0], _track[:, 1], _track[:, 2], color="steelblue", linewidth=2)
    _ax.quiver(0, 0, 0, 0, 0, 1.2, color="darkorange", linewidth=2, arrow_length_ratio=0.08)
    _ax.quiver(0, 0, 0, _spin0[0], _spin0[1], _spin0[2], color="gray", linewidth=1.8, arrow_length_ratio=0.08)
    _ax.quiver(0, 0, 0, _s[0], _s[1], _s[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title(f"Pauli spin precession at t = {time.value:.2f}")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
