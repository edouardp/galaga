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
        r"""
        # Single-Qubit Circuits in GA

        A single-qubit circuit is just a product of rotors. The algebraic picture is:

        $$
        \psi_{\mathrm{out}} = R_n \cdots R_2 R_1 \psi_{\mathrm{in}}.
        $$

        The measurement outcome is then read from the rotated Bloch vector
        $\psi_{\mathrm{out}} e_3 \tilde{\psi}_{\mathrm{out}}$.
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
    first = mo.ui.dropdown(options=["I", "H", "X", "Y", "Z", "S"], value="H", label="gate 1")
    second = mo.ui.dropdown(options=["I", "H", "X", "Y", "Z", "S"], value="S", label="gate 2")
    third = mo.ui.dropdown(options=["I", "H", "X", "Y", "Z", "S"], value="H", label="gate 3")
    mo.vstack([first, second, third])
    return first, second, third


@app.cell
def _(e1, e2, e3, exp, np):
    def gate_rotor(name):
        if name == "I":
            return 1 + 0 * e1
        if name == "X":
            return exp((-(np.pi) / 2) * (e2 * e3))
        if name == "Y":
            return exp((-(np.pi) / 2) * (e3 * e1))
        if name == "Z":
            return exp((-(np.pi) / 2) * (e1 * e2))
        if name == "S":
            return exp((-(np.pi / 2) / 2) * (e1 * e2))
        axis = ((e1 + e3) / np.sqrt(2)).eval().vector_part
        return exp((-(np.pi) / 2) * (axis[0] * (e2 * e3) + axis[2] * (e1 * e2)))

    return (gate_rotor,)


@app.cell(hide_code=True)
def _(first, gate_rotor, gm, second, third):
    R1 = gate_rotor(first.value)
    R2 = gate_rotor(second.value)
    R3 = gate_rotor(third.value)
    total = R3 * R2 * R1
    state_out = total * (1 + 0 * total)

    gm.md(t"""
    ## Circuit Rotor

    {R1} = {R1.eval()}

    {R2} = {R2.eval()}

    {R3} = {R3.eval()}

    Total rotor:
    {total} = {total.eval()}

    Output state representative:
    {state_out} = {state_out.eval()}
    """)
    return state_out


@app.cell(hide_code=True)
def _(e3, gm, state_out):
    bloch = (state_out * e3 * ~state_out).eval().vector_part
    p0 = 0.5 * (1 + bloch[2])
    p1 = 0.5 * (1 - bloch[2])

    gm.md(t"""
    ## Readout

    Bloch vector:
    $({bloch[0]:.6f}, {bloch[1]:.6f}, {bloch[2]:.6f})$

    Computational-basis probabilities:
    $P(0) = {p0:.6f}, \qquad P(1) = {p1:.6f}$
    """)
    return bloch


@app.cell
def _(bloch, np, plt):
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, bloch[0], bloch[1], bloch[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Single-qubit circuit output")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
