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

    from galaga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Quantum Teleportation with GA Geometry

    Full teleportation is a three-qubit protocol, so the exact tensor-product
    bookkeeping lives outside the current single-spin rotor API. This notebook
    therefore teaches the protocol geometrically:

    - the unknown input qubit is a Bloch vector
    - the Bell pair supplies shared correlation
    - Alice's two classical bits tell Bob which correction rotor to apply

    The central idea survives cleanly in GA: the "state to be teleported" is a
    direction encoded by a rotor, and the correction is another rotor chosen from
    a small discrete set.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm):
    gm.md(t"""
    Single-spin basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}

    Teleportation will move an unknown Bloch vector from Alice's side to Bob's side.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Unknown Qubit

    The state to be teleported is represented by a rotor

    $$
    \psi = e^{-(\phi/2)e_{12}} e^{-(\theta/2)e_{31}},
    $$

    with Bloch vector $s = \psi e_3 \tilde\psi$.
    """)
    return


@app.cell
def _(mo):
    theta = mo.ui.slider(start=0, stop=180, step=1, value=65, label="input polar angle θ")
    phi = mo.ui.slider(start=0, stop=360, step=1, value=35, label="input azimuth φ")
    alice_bits = mo.ui.dropdown(
        options=["00", "01", "10", "11"],
        value="10",
        label="Alice's measurement bits",
    )
    mo.vstack([theta, phi, alice_bits])
    return alice_bits, phi, theta


@app.cell(hide_code=True)
def _(alice_bits, e1, e2, e3, exp, gm, np, phi, theta):
    _theta = np.radians(theta.value)
    _phi = np.radians(phi.value)
    psi = exp((-_phi / 2) * (e1 * e2)) * exp((-_theta / 2) * (e3 * e1))
    source = (psi * e3 * ~psi).eval().vector_part

    if alice_bits.value == "00":
        correction = 1 + 0 * e1
    elif alice_bits.value == "01":
        correction = exp((-(np.pi) / 2) * (e2 * e3))
    elif alice_bits.value == "10":
        correction = exp((-(np.pi) / 2) * (e1 * e2))
    else:
        correction = exp((-(np.pi) / 2) * (e2 * e3)) * exp((-(np.pi) / 2) * (e1 * e2))

    received_before = (
        correction
        * (source[0] * e1.eval() + source[1] * e2.eval() + source[2] * e3.eval())
        * ~correction
    ).vector_part

    recovered = (
        ~correction
        * (received_before[0] * e1.eval() + received_before[1] * e2.eval() + received_before[2] * e3.eval())
        * correction
    ).vector_part

    gm.md(t"""
    ## Geometric Protocol

    Unknown rotor:
    {psi} = {psi.eval()}

    Input Bloch vector:
    $({source[0]:.6f}, {source[1]:.6f}, {source[2]:.6f})$

    Bob's pre-correction state for Alice bits `{alice_bits.value}`:
    $({received_before[0]:.6f}, {received_before[1]:.6f}, {received_before[2]:.6f})$

    Correction rotor:
    {correction} = {correction.eval()}

    Recovered state after correction:
    $({recovered[0]:.6f}, {recovered[1]:.6f}, {recovered[2]:.6f})$
    """)
    return recovered, source


@app.cell
def _(np, plt, recovered, source):
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, source[0], source[1], source[2], color="steelblue", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, recovered[0], recovered[1], recovered[2], color="crimson", linewidth=2.0, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Teleportation as rotor correction on the Bloch sphere")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
