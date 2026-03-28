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

    from ga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Qubits and Superposition in Geometric Algebra

    A qubit is often introduced as

    $$
    |\psi\rangle = \alpha |0\rangle + \beta |1\rangle,
    \qquad
    |\alpha|^2 + |\beta|^2 = 1.
    $$

    In geometric algebra, the same pure state can be represented by a rotor
    $\psi$ in Cl(3,0). The observable state is the Bloch vector

    $$
    s = \psi e_3 \tilde\psi.
    $$

    Superposition is not an extra mysterious ingredient on the GA side. It is the
    same physical state, seen as a rotor whose Bloch vector is not aligned with
    the measurement axis.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell(hide_code=True)
def _(e1, e2, e3, gm):
    gm.md(t"""
    ## Basis Algebra

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}

    The bivectors {e2 * e3}, {e3 * e1}, and {e1 * e2} generate rotations of the Bloch sphere.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Basis States and the $x$-Basis Superposition

    With the computational basis defined relative to the $e_3$ axis:

    - $|0\rangle$ corresponds to Bloch vector $+e_3$
    - $|1\rangle$ corresponds to Bloch vector $-e_3$
    - $|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$ corresponds to $+e_1$

    The last line is the key superposition example: equal amplitudes in the
    computational basis become a rotated vector on the Bloch sphere.
    """)
    return


@app.cell
def _(e1, e3, exp, gm, np):
    ket_0 = 1 + 0 * e1
    ket_1 = exp((-(np.pi) / 2) * (e3 * e1))
    ket_plus = exp((-(np.pi / 2) / 2) * (e3 * e1))
    ket_minus = exp(((np.pi / 2) / 2) * (e3 * e1))

    gm.md(t"""
    | State | GA representative | Bloch vector |
    |---|---|---|
    | $|0\\rangle$ | {ket_0} = {ket_0.eval()} | {(ket_0 * e3 * ~ket_0).eval()} |
    | $|1\\rangle$ | {ket_1} = {ket_1.eval()} | {(ket_1 * e3 * ~ket_1).eval()} |
    | $|+\\rangle$ | {ket_plus} = {ket_plus.eval()} | {(ket_plus * e3 * ~ket_plus).eval()} |
    | $|-\\rangle$ | {ket_minus} = {ket_minus.eval()} | {(ket_minus * e3 * ~ket_minus).eval()} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A General Pure Qubit

    For Bloch angles $(\theta,\phi)$ we use

    $$
    \psi = e^{-(\phi/2)e_{12}} e^{-(\theta/2)e_{31}}.
    $$

    The corresponding amplitudes in the usual column-vector picture are

    $$
    \alpha = \cos(\theta/2), \qquad
    \beta = e^{i\phi}\sin(\theta/2).
    $$

    On the GA side, the same information is stored geometrically in the rotor and
    in the measurement probabilities derived from $s = \psi e_3 \tilde\psi$.
    """)
    return


@app.cell
def _(mo):
    theta = mo.ui.slider(start=0, stop=180, step=1, value=60, label="polar angle θ")
    phi = mo.ui.slider(start=0, stop=360, step=1, value=30, label="azimuth φ")
    mo.vstack([theta, phi])
    return phi, theta


@app.cell(hide_code=True)
def _(e1, e2, e3, exp, gm, np, phi, theta):
    _theta = np.radians(theta.value)
    _phi = np.radians(phi.value)
    psi = exp((-_phi / 2) * (e1 * e2)) * exp((-_theta / 2) * (e3 * e1))
    s = (psi * e3 * ~psi).eval().vector_part

    alpha = np.cos(_theta / 2)
    beta = np.exp(1j * _phi) * np.sin(_theta / 2)
    p0 = 0.5 * (1 + s[2])
    p1 = 0.5 * (1 - s[2])

    gm.md(t"""
    ## Rotor View vs Amplitude View

    {psi} = {psi.eval()}

    Bloch vector:
    $({s[0]:.6f}, {s[1]:.6f}, {s[2]:.6f})$

    Matrix amplitudes:

    $$
    \\alpha = {alpha:.6f}, \qquad
    \\beta = {beta.real:+.6f} {beta.imag:+.6f} i
    $$

    Computational-basis measurement probabilities:

    $$
    P(0) = {p0:.6f}, \qquad P(1) = {p1:.6f}
    $$

    In GA, "superposition of $|0\\rangle$ and $|1\\rangle$" means exactly that the
    Bloch vector is not sitting at either pole.
    """)
    return (s,)


@app.cell
def _(np, plt, s):
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, 0, 0, 1, color="steelblue", linewidth=2.0, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, s[0], s[1], s[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Pure qubit state on the Bloch sphere")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
