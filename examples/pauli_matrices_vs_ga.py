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
    mo.md("""
    # Pauli Matrices vs Geometric Algebra

    This notebook compares two descriptions of the same Spin(3) / SU(2) physics:

    - **matrix language:** Pauli matrices acting on 2-component spinors
    - **geometric algebra language:** Cl(3,0) acting on multivectors and rotors

    The point is not that one side is "wrong". The point is to show that the GA
    side packages the same structure with fewer representational layers:

    - vectors stay vectors instead of becoming matrices
    - rotations are rotor sandwiches instead of matrix conjugations
    - observables come from geometric products instead of separate bra/ket machinery
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    I = alg.I
    return I, e1, e2, e3


@app.cell
def _(np):
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    eye2 = np.eye(2, dtype=complex)
    return sigma_x, sigma_y, sigma_z


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Algebra Side by Side

    The Pauli matrices satisfy

    $$
    \sigma_i \sigma_j = \delta_{ij} I_2 + i \varepsilon_{ijk}\sigma_k,
    \qquad
    [\sigma_i,\sigma_j] = 2 i \varepsilon_{ijk}\sigma_k.
    $$

    In Cl(3,0), the basis vectors satisfy

    $$
    e_i e_j = \delta_{ij} + e_i \wedge e_j,
    \qquad
    e_i e_j = - e_j e_i \text{ for } i \neq j.
    $$

    The bivectors play the role of the Lie algebra generators, and the
    pseudoscalar $I = e_1 e_2 e_3$ plays the role of the matrix imaginary unit.
    """)
    return


@app.cell
def _(I, e1, e2, e3, gm, sigma_x, sigma_y, sigma_z):
    gm.md(t"""
    | Object | Matrix side | GA side |
    |---|---|---|
    | generator 1 | `{sigma_x}` | {e1} = {e1.eval()} |
    | generator 2 | `{sigma_y}` | {e2} = {e2.eval()} |
    | generator 3 | `{sigma_z}` | {e3} = {e3.eval()} |
    | imaginary / oriented volume | $i$ | {I} = {I.eval()} |
    | $\sigma_x \sigma_y$ / $e_1 e_2$ | `{sigma_x @ sigma_y}` | {e1 * e2} = {(e1 * e2).eval()} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## States

    For a pure spin-1/2 state with Bloch angles $(\theta,\phi)$, the matrix spinor
    can be written as

    $$
    |\psi\rangle =
    \begin{pmatrix}
    \cos(\theta/2) \\
    e^{i\phi}\sin(\theta/2)
    \end{pmatrix}.
    $$

    On the GA side, the same state is a rotor

    $$
    \psi = e^{-(\phi/2)e_{12}} e^{-(\theta/2)e_{31}},
    $$

    and the observable spin direction is the rotated vector $\psi e_3 \tilde\psi$.
    """)
    return


@app.cell
def _(mo):
    theta = mo.ui.slider(start=0, stop=180, step=1, value=55, label="polar angle θ")
    phi = mo.ui.slider(start=0, stop=360, step=1, value=35, label="azimuth φ")
    mo.vstack([theta, phi])
    return phi, theta


@app.cell(hide_code=True)
def _(e1, e2, e3, exp, gm, np, phi, sigma_x, sigma_y, sigma_z, theta):
    _theta = np.radians(theta.value)
    _phi = np.radians(phi.value)

    _psi_matrix = np.array(
        [
            [np.cos(_theta / 2)],
            [np.exp(1j * _phi) * np.sin(_theta / 2)],
        ],
        dtype=complex,
    )

    _psi_ga = exp((-_phi / 2) * (e1 * e2)) * exp((-_theta / 2) * (e3 * e1))
    _spin_ga = (_psi_ga * e3 * ~_psi_ga).eval().vector_part

    _expect_x = (_psi_matrix.conj().T @ sigma_x @ _psi_matrix)[0, 0].real
    _expect_y = (_psi_matrix.conj().T @ sigma_y @ _psi_matrix)[0, 0].real
    _expect_z = (_psi_matrix.conj().T @ sigma_z @ _psi_matrix)[0, 0].real

    gm.md(t"""
    ## Same State, Two Representations

    Matrix spinor:

    $$
    |\\psi\\rangle =
    \\begin{{pmatrix}}
    {_psi_matrix[0,0].real:.6f} \\\\
    {_psi_matrix[1,0].real:+.6f} { _psi_matrix[1,0].imag:+.6f} i
    \\end{{pmatrix}}
    $$

    GA rotor:

    {_psi_ga} = {_psi_ga.eval()}

    Matrix Bloch vector:
    $({ _expect_x:.6f}, { _expect_y:.6f}, { _expect_z:.6f})$

    GA Bloch vector:
    $({ _spin_ga[0]:.6f}, { _spin_ga[1]:.6f}, { _spin_ga[2]:.6f})$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rotations

    A spatial rotation by angle $\alpha$ about the $z$ axis is

    $$
    U_z(\alpha) = e^{- i \alpha \sigma_z / 2}
    $$

    on the matrix side, and

    $$
    R_z(\alpha) = e^{- \alpha e_{12} / 2}
    $$

    on the GA side.
    """)
    return


@app.cell
def _(mo):
    alpha = mo.ui.slider(start=0, stop=360, step=1, value=70, label="rotation angle α about z")
    alpha
    return (alpha,)


@app.cell(hide_code=True)
def _(alpha, e1, e2, e3, exp, gm, np, sigma_z):
    _alpha = np.radians(alpha.value)
    _U = np.cos(_alpha / 2) * np.eye(2, dtype=complex) - 1j * np.sin(_alpha / 2) * sigma_z
    _psi_rot = _U @ _psi_matrix

    _R = exp((-_alpha / 2) * (e1 * e2))
    _v = _expect_x * e1.eval() + _expect_y * e2.eval() + _expect_z * e3.eval()
    _v_rot = (_R * _v * ~_R).vector_part

    gm.md(t"""
    Rotated matrix spinor:

    $$
    U_z |\\psi\\rangle =
    \\begin{{pmatrix}}
    {_psi_rot[0,0].real:.6f} { _psi_rot[0,0].imag:+.6f} i \\\\
    {_psi_rot[1,0].real:+.6f} { _psi_rot[1,0].imag:+.6f} i
    \\end{{pmatrix}}
    $$

    GA rotor:

    {_R} = {_R.eval()}

    Rotated observable vector:

    $({ _v_rot[0]:.6f}, { _v_rot[1]:.6f}, { _v_rot[2]:.6f})$
    """)
    return


@app.cell
def _(np, plt):
    _fig = plt.figure(figsize=(6, 6))
    _ax = _fig.add_subplot(111, projection="3d")
    _u = np.linspace(0, 2 * np.pi, 32)
    _v = np.linspace(0, np.pi, 16)
    _x = np.outer(np.cos(_u), np.sin(_v))
    _y = np.outer(np.sin(_u), np.sin(_v))
    _z = np.outer(np.ones_like(_u), np.cos(_v))
    _ax.plot_wireframe(_x, _y, _z, color="gray", alpha=0.08)
    _ax.quiver(0, 0, 0, _expect_x, _expect_y, _expect_z, color="steelblue", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, _spin_ga[0], _spin_ga[1], _spin_ga[2], color="darkorange", linewidth=2.0, arrow_length_ratio=0.1)
    _ax.quiver(0, 0, 0, _v_rot[0], _v_rot[1], _v_rot[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.1)
    _ax.set_xlim(-1, 1)
    _ax.set_ylim(-1, 1)
    _ax.set_zlim(-1, 1)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Matrix and GA descriptions on the same Bloch sphere")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
