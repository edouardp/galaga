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
        # Measurement and Interference in GA

        A useful quantum-computing story is:

        1. start in $|0\rangle$
        2. create a superposition
        3. add a relative phase
        4. recombine and measure

        In GA, the "relative phase" is a rotor about the measurement axis, and the
        interference pattern appears when another rotor turns that phase information
        back into a measurable population difference.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## The Circuit

        We use the single-qubit sequence

        $$
        |0\rangle \xrightarrow{H}
        \frac{|0\rangle + |1\rangle}{\sqrt{2}}
        \xrightarrow{R_z(\phi)}
        \frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}}
        \xrightarrow{H}
        \text{measure in the computational basis.}
        $$

        On the GA side, the Hadamard and phase steps are rotors.
        """
    )
    return


@app.cell
def _(mo):
    phase = mo.ui.slider(start=0.0, stop=360.0, step=1.0, value=60.0, label="relative phase φ")
    phase
    return (phase,)


@app.cell(hide_code=True)
def _(e1, e2, e3, exp, gm, np, phase):
    _phi = np.radians(phase.value)

    ket0 = 1 + 0 * e1
    hadamard = exp((-(np.pi) / 2) * ((e2 * e3 + e1 * e2) / np.sqrt(2)))
    phase_rotor = exp((-_phi / 2) * (e1 * e2))

    after_h = hadamard * ket0
    after_phase = phase_rotor * after_h
    final_state = hadamard * after_phase
    final_bloch = (final_state * e3 * ~final_state).eval().vector_part

    p0 = 0.5 * (1 + final_bloch[2])
    p1 = 0.5 * (1 - final_bloch[2])

    gm.md(t"""
    ## Rotor Description

    Initial state:
    {ket0} = {ket0.eval()}

    Hadamard-like rotor:
    {hadamard} = {hadamard.eval()}

    Phase rotor:
    {phase_rotor} = {phase_rotor.eval()}

    After first H:
    {after_h} = {after_h.eval()}

    After phase:
    {after_phase} = {after_phase.eval()}

    After second H:
    {final_state} = {final_state.eval()}

    Final measurement probabilities:
    $P(0) = {p0:.6f}, \qquad P(1) = {p1:.6f}$
    """)
    return final_bloch, p0, p1


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Why This Is Interference

        The middle phase rotation does not change the $z$-measurement statistics by
        itself. It changes where the state sits around the equator. The final Hadamard
        rotates that phase information into the measurement axis, which is why the
        output probabilities oscillate with $\phi$.
        """
    )
    return


@app.cell
def _(final_bloch, np, p0, p1, phase, plt):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    _phis = np.linspace(0, 2 * np.pi, 400)
    _curve = 0.5 * (1 + np.cos(_phis))
    _ax1.plot(np.degrees(_phis), _curve, color="steelblue", linewidth=2.5)
    _ax1.plot([phase.value], [p0], "ko", ms=7)
    _ax1.set_xlabel("phase φ (degrees)")
    _ax1.set_ylabel("P(0)")
    _ax1.set_title("Ramsey / Mach-Zehnder interference curve")
    _ax1.grid(True, alpha=0.2)

    _ax2 = _fig.add_subplot(122, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax2.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax2.quiver(0, 0, 0, final_bloch[0], final_bloch[1], final_bloch[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax2.set_xlim(-1, 1)
    _ax2.set_ylim(-1, 1)
    _ax2.set_zlim(-1, 1)
    _ax2.set_box_aspect((1, 1, 1))
    _ax2.set_title(f"Final Bloch vector\nP(0)={p0:.3f}, P(1)={p1:.3f}")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
