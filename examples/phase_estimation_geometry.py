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
        # Phase Estimation Geometry

        Phase estimation is the algorithmic version of a simple geometric fact:
        repeated applications of a rotor accumulate angle linearly. Controlled powers
        turn that angle into binary information that can be read out by interference.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm):
    gm.md(t"""
    Phase-estimation rotor plane:

    {e1 * e2} = {(e1 * e2).eval()}

    Reference axis:

    {e3} = {e3.eval()}
    """)
    return


@app.cell
def _(mo):
    phase = mo.ui.slider(start=0.0, stop=1.0, step=0.01, value=0.3125, label="eigenphase φ / 2π")
    bits = mo.ui.slider(start=1, stop=5, step=1, value=3, label="readout bits")
    mo.vstack([phase, bits])
    return bits, phase


@app.cell(hide_code=True)
def _(bits, e1, e2, e3, exp, gm, np, phase):
    _phi = 2 * np.pi * phase.value
    rotor = exp((-_phi / 2) * (e1 * e2))
    powers = [2**k for k in range(bits.value)]
    phases = [(p * phase.value) % 1.0 for p in powers]
    binary = format(int(round(phase.value * (2**bits.value))) % (2**bits.value), f"0{bits.value}b")
    state = (rotor * e3 * ~rotor).eval().vector_part

    with gm.doc() as d:
        d.md(t"""
        ## Repeated Powers

        Base rotor:
        {rotor} = {rotor.eval()}

        Rotated axis:
        $({state[0]:.6f}, {state[1]:.6f}, {state[2]:.6f})$
        """)
        d.text("| control power | fractional phase |")
        d.line("|---|---|")
        for p, frac in zip(powers, phases):
            d.line(f"| $2^{{{int(np.log2(p))}}}$ | {frac:.6f} |")
        d.md(t"""
        Approximate {bits.value}-bit readout:

        $$
        {binary:text}
        $$
        """)
    d.render()
    return phases


@app.cell
def _(bits, np, phase, phases, plt):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4))
    _x = np.arange(len(phases))
    _ax1.bar(_x, phases, color="steelblue")
    _ax1.set_xticks(_x)
    _ax1.set_xticklabels([f"$2^{k}$" for k in range(bits.value)])
    _ax1.set_ylim(0, 1)
    _ax1.set_ylabel("fractional phase")
    _ax1.set_title("Controlled powers accumulate phase")
    _ax1.grid(True, axis="y", alpha=0.2)

    _grid = np.arange(0, 2**bits.value) / (2**bits.value)
    _idx = np.argmin(np.abs(_grid - phase.value))
    _ax2.plot(_grid, np.zeros_like(_grid), "o", color="gray", alpha=0.6)
    _ax2.plot([_grid[_idx]], [0], "o", color="crimson", ms=10)
    _ax2.set_yticks([])
    _ax2.set_xlabel("phase fraction on binary grid")
    _ax2.set_title("Nearest binary approximation")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
