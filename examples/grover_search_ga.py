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
        # Grover Search as Geometry

        Grover's algorithm is a sequence of reflections in a two-dimensional subspace:
        the marked state and the uniform superposition direction. That makes it a good
        geometric notebook even before discussing full multi-qubit implementations.
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
    Search-plane basis:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    Grover's algorithm is a repeated rotation inside this effective 2D subspace.
    """)
    return


@app.cell
def _(mo):
    theta = mo.ui.slider(start=1, stop=25, step=1, value=6, label="problem size N")
    iterations = mo.ui.slider(start=0, stop=10, step=1, value=1, label="Grover iterations")
    mo.vstack([theta, iterations])
    return iterations, theta


@app.cell(hide_code=True)
def _(gm, iterations, np, theta):
    N = theta.value
    k = iterations.value
    angle = np.arcsin(1 / np.sqrt(N))
    success = np.sin((2 * k + 1) * angle) ** 2

    gm.md(t"""
    ## Two-State Reduction

    Let $|w\\rangle$ be the marked state and $|r\\rangle$ the normalized superposition
    of all unmarked states. Then

    $$
    |s\\rangle = \\sin \\theta \\, |w\\rangle + \\cos \\theta \\, |r\\rangle,
    \qquad
    \\sin\\theta = \\frac{{1}}{{\\sqrt{{N}}}}.
    $$

    For $N = {N}$:

    $$
    \\theta = {angle:.6f}
    $$

    After {k} Grover iterations:

    $$
    P(\\text{{marked}}) = \\sin^2((2k+1)\\theta) = {success:.6f}
    $$
    """)
    return angle, success


@app.cell
def _(iterations, np, plt, success, theta):
    N = theta.value
    _ks = np.arange(0, max(10, iterations.value + 4))
    _theta = np.arcsin(1 / np.sqrt(N))
    _curve = np.sin((2 * _ks + 1) * _theta) ** 2

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4))
    _ax1.plot(_ks, _curve, color="steelblue", linewidth=2.5)
    _ax1.plot([iterations.value], [success], "ko", ms=7)
    _ax1.set_xlabel("Grover iterations")
    _ax1.set_ylabel("success probability")
    _ax1.set_title("Amplitude amplification")
    _ax1.grid(True, alpha=0.2)

    _angs = (2 * _ks + 1) * _theta
    _ax2.plot(np.cos(_angs), np.sin(_angs), "o-", color="crimson", alpha=0.8)
    _ax2.axhline(0, color="black", alpha=0.2)
    _ax2.axvline(0, color="black", alpha=0.2)
    _ax2.set_aspect("equal")
    _ax2.set_xlabel("unmarked component")
    _ax2.set_ylabel("marked component")
    _ax2.set_title("Repeated rotations in the search plane")
    _ax2.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
