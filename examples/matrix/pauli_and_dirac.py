import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _repository = Path(__file__).resolve().parent.parent.parent
    for _source in (
        _repository,
        _repository / "packages" / "galaga",
        _repository / "packages" / "galaga_marimo",
        _repository / "packages" / "galaga_matrix",
    ):
        _path = str(_source)
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        p_euclidean,
        p_sta,
    )

    return (
        Algebra,
        DisplayPolicy,
        from_matrix,
        gm,
        mo,
        np,
        p_euclidean,
        p_sta,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Pauli, Dirac, and quaternion representations

    **Claim:** the familiar Pauli and Dirac matrices are concrete
    representations of Clifford generators. Their matrix identities follow
    from the metric relations already enforced by the geometric algebra.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pauli matrices from $Cl(3,0)$

    In `mode="pauli"`, the three Euclidean basis vectors map to
    $\sigma_1$, $\sigma_2$, and $\sigma_3$.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_euclidean, to_matrix):
    pauli_algebra = Algebra(
        config=p_euclidean(3),
        display=DisplayPolicy(content="full"),
    )
    pauli_e1, pauli_e2, pauli_e3 = pauli_algebra.basis_vectors(expr=True)
    sigma1 = to_matrix(pauli_e1.named("e_1"), mode="pauli")
    sigma2 = to_matrix(pauli_e2.named("e_2"), mode="pauli")
    sigma3 = to_matrix(pauli_e3.named("e_3"), mode="pauli")
    return sigma1, sigma2, sigma3


@app.cell
def _(gm, sigma1, sigma2, sigma3):
    gm.md(rt"""
    {sigma1:block}

    {sigma2:block}

    {sigma3:block}
    """)
    return


@app.cell
def _(np, sigma1, sigma2, sigma3):
    _identity2 = np.eye(2)
    pauli_squares_hold = all(
        np.allclose(sigma @ sigma, _identity2)
        for sigma in (sigma1, sigma2, sigma3)
    )
    pauli_anticommutation_holds = all(
        np.allclose(left @ right + right @ left, 0)
        for left, right in ((sigma1, sigma2), (sigma2, sigma3), (sigma3, sigma1))
    )
    pauli_orientation_holds = np.allclose(sigma1 @ sigma2, 1j * sigma3)
    return (
        pauli_anticommutation_holds,
        pauli_orientation_holds,
        pauli_squares_hold,
    )


@app.cell
def _(
    gm,
    pauli_anticommutation_holds,
    pauli_orientation_holds,
    pauli_squares_hold,
):
    gm.md(rt"""
    - $\sigma_i^2=I$: `{pauli_squares_hold!s}`
    - $\sigma_i\sigma_j+\sigma_j\sigma_i=0$ for $i\ne j$:
      `{pauli_anticommutation_holds!s}`
    - $\sigma_1\sigma_2=i\sigma_3$: `{pauli_orientation_holds!s}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `MatrixRepr` keeps ordinary matrix operations inside the wrapper: `@`,
    addition, scalar arithmetic, transpose `.T`, adjoint `.H`, conjugation,
    inverse `.inv()`, trace, determinant, powers, and Kronecker products.
    """)
    return


@app.cell
def _(gm, np, sigma2):
    _sigma2_is_hermitian = np.allclose(sigma2.H, sigma2)
    _sigma2_inverse = sigma2.inv()
    _sigma2_trace = sigma2.trace()
    _sigma2_determinant = sigma2.det()

    gm.md(rt"""
    $\sigma_2$ is Hermitian: `{_sigma2_is_hermitian!s}`.

    Trace: `{_sigma2_trace!s}`; determinant: `{_sigma2_determinant!s}`.

    Its inverse remains a renderable `MatrixRepr`:

    {_sigma2_inverse:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dirac matrices from spacetime algebra

    The mostly-minus `p_sta()` preset has signature $(+---)`. `mode="dirac"`
    produces the standard $4\times4$ complex gamma representation in the
    package's Dirac basis.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_sta, to_matrix):
    spacetime_algebra = Algebra(
        config=p_sta("mostly-minus"),
        display=DisplayPolicy(content="full"),
    )
    gamma0, gamma1, gamma2, gamma3 = spacetime_algebra.basis_vectors(expr=True)
    gamma0_dirac = to_matrix(gamma0.named("gamma0", latex=r"\gamma^0"), mode="dirac")
    gamma1_dirac = to_matrix(gamma1.named("gamma1", latex=r"\gamma^1"), mode="dirac")
    return gamma0, gamma0_dirac, gamma1_dirac


@app.cell
def _(gamma0_dirac, gamma1_dirac, gm):
    gm.md(rt"""
    {gamma0_dirac:block}

    {gamma1_dirac:block}
    """)
    return


@app.cell
def _(gamma0_dirac, gamma1_dirac, np):
    _identity4 = np.eye(4)
    time_square_holds = np.allclose(gamma0_dirac @ gamma0_dirac, _identity4)
    space_square_holds = np.allclose(gamma1_dirac @ gamma1_dirac, -_identity4)
    time_space_anticommute = np.allclose(
        gamma0_dirac @ gamma1_dirac + gamma1_dirac @ gamma0_dirac,
        0,
    )
    return space_square_holds, time_space_anticommute, time_square_holds


@app.cell
def _(gm, space_square_holds, time_space_anticommute, time_square_holds):
    gm.md(rt"""
    - $(\gamma^0)^2=I$: `{time_square_holds!s}`
    - $(\gamma^1)^2=-I$: `{space_square_holds!s}`
    - $\gamma^0\gamma^1+\gamma^1\gamma^0=0$:
      `{time_space_anticommute!s}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Matrix basis changes do not change the multivector

    `to_basis("weyl")` and `to_basis("majorana")` apply validated similarity
    transforms to Dirac representations. The wrapper records the selected
    basis, and `from_matrix` transforms back before reconstructing the abstract
    Clifford element.
    """)
    return


@app.cell
def _(from_matrix, gamma0, gamma0_dirac, np):
    gamma0_weyl = gamma0_dirac.to_basis("weyl")
    gamma0_majorana = gamma0_dirac.to_basis("majorana")
    gamma0_from_weyl = from_matrix(gamma0_weyl)
    basis_roundtrip_holds = np.allclose(gamma0_from_weyl.data, gamma0.data)
    return basis_roundtrip_holds, gamma0_majorana, gamma0_weyl


@app.cell
def _(basis_roundtrip_holds, gamma0_majorana, gamma0_weyl, gm):
    gm.md(rt"""
    Weyl basis:

    {gamma0_weyl:block}

    Majorana basis:

    {gamma0_majorana:block}

    Weyl matrix reconstructs the original $\gamma^0$:
    `{basis_roundtrip_holds!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Quaternion blocks for $Cl(1,3)$

    Quaternion mode uses a separate faithful $M(2,\mathbb H)$ basis rather
    than reinterpreting the entries of the standard Dirac matrices. The same
    `MatrixRepr` wrapper provides complex storage plus a `.quat` block view.
    """)
    return


@app.cell
def _(gamma0, gm, to_matrix):
    gamma0_quaternion = to_matrix(gamma0, mode="quaternion")
    _quaternion_block_shape = (
        len(gamma0_quaternion.quat),
        len(gamma0_quaternion.quat[0]),
    )

    gm.md(rt"""
    Quaternion-block shape: `{_quaternion_block_shape!s}`.

    {gamma0_quaternion:block}
    """)
    return


if __name__ == "__main__":
    app.run()
