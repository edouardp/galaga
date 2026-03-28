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

    from ga import Algebra
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Deutsch-Jozsa as Interference

        The Deutsch-Jozsa algorithm is the cleanest early example of phase kickback
        and interference. The key geometric lesson is that the oracle writes sign
        information into amplitudes, and the final Hadamards recombine those signs.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), repr_unicode=True)
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(e1, e2, gm):
    gm.md(t"""
    Effective two-state basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    The oracle writes signs into a 2D superposition, and the final recombination
    reads those signs back out.
    """)
    return


@app.cell
def _(mo):
    oracle = mo.ui.dropdown(options=["constant 0", "constant 1", "balanced parity"], value="balanced parity", label="oracle")
    oracle
    return (oracle,)


@app.cell(hide_code=True)
def _(gm, oracle):
    if oracle.value == "constant 0":
        phases = np.array([1, 1])
        verdict = "constant"
    elif oracle.value == "constant 1":
        phases = np.array([-1, -1])
        verdict = "constant"
    else:
        phases = np.array([1, -1])
        verdict = "balanced"

    initial = np.array([1, 1]) / np.sqrt(2)
    after_oracle = phases * initial
    hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    final = hadamard @ after_oracle

    gm.md(t"""
    ## One-Bit Deutsch-Jozsa

    Start with the superposition

    $$
    |+\\rangle = \\frac{{1}}{{\\sqrt{{2}}}} (|0\\rangle + |1\\rangle).
    $$

    Oracle phases:

    $$
    ({phases[0]:+.0f}, {phases[1]:+.0f})
    $$

    After the oracle:

    $$
    \\frac{{1}}{{\\sqrt{{2}}}}
    \\begin{{pmatrix}}
    {after_oracle[0]:+.6f} \\\\
    {after_oracle[1]:+.6f}
    \\end{{pmatrix}}
    $$

    After the final Hadamard:

    $$
    \\begin{{pmatrix}}
    {final[0]:+.6f} \\\\
    {final[1]:+.6f}
    \\end{{pmatrix}}
    $$

    Measured verdict: **{verdict}**
    """)
    return final


@app.cell
def _(final, np, plt):
    _labels = ["|0>", "|1>"]
    _fig, _ax = plt.subplots(figsize=(6, 4))
    _ax.bar(_labels, np.abs(final) ** 2, color=["steelblue", "crimson"])
    _ax.set_ylim(0, 1)
    _ax.set_ylabel("probability")
    _ax.set_title("Output measurement distribution")
    _ax.grid(True, axis="y", alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
