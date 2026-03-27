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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Quantum Gates in Geometric Algebra

        Single-qubit gates are rotations of the Bloch sphere. In matrix language they
        are 2x2 unitaries. In geometric algebra they are rotors in Cl(3,0).
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(mo):
    gate = mo.ui.dropdown(options=["X", "Y", "Z", "H", "S"], value="H", label="gate")
    theta = mo.ui.slider(start=0, stop=180, step=1, value=55, label="initial polar angle")
    phi = mo.ui.slider(start=0, stop=360, step=1, value=20, label="initial azimuth")
    mo.vstack([gate, theta, phi])
    return gate, phi, theta


@app.cell(hide_code=True)
def _(e1, e2, e3, exp, gate, gm, np, phi, theta):
    _theta = np.radians(theta.value)
    _phi = np.radians(phi.value)
    psi = exp((-_phi / 2) * (e1 * e2)) * exp((-_theta / 2) * (e3 * e1))
    spin = (psi * e3 * ~psi).eval().vector_part

    if gate.value == "X":
        rotor = exp((-(np.pi) / 2) * (e2 * e3))
    elif gate.value == "Y":
        rotor = exp((-(np.pi) / 2) * (e3 * e1))
    elif gate.value == "Z":
        rotor = exp((-(np.pi) / 2) * (e1 * e2))
    elif gate.value == "S":
        rotor = exp((-(np.pi / 2) / 2) * (e1 * e2))
    else:
        axis = ((e1 + e3) / np.sqrt(2)).eval()
        rotor = exp((-(np.pi) / 2) * (axis.dual() if False else (axis.vector_part[0] * (e2 * e3) + axis.vector_part[2] * (e1 * e2))))

    spin_out = (rotor * (spin[0] * e1.eval() + spin[1] * e2.eval() + spin[2] * e3.eval()) * ~rotor).vector_part

    gm.md(t"""
    ## Gate Action

    Input rotor:

    {psi} = {psi.eval()}

    Selected gate rotor:

    {rotor} = {rotor.eval()}

    Input Bloch vector:

    $({spin[0]:.6f}, {spin[1]:.6f}, {spin[2]:.6f})$

    Output Bloch vector:

    $({spin_out[0]:.6f}, {spin_out[1]:.6f}, {spin_out[2]:.6f})$
    """)
    return spin, spin_out


@app.cell
def _(np, plt, spin, spin_out):
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, spin[0], spin[1], spin[2], color="steelblue", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, spin_out[0], spin_out[1], spin_out[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Single-qubit gate as Bloch-sphere rotation")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
