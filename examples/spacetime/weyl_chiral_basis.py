import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    _gmat = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_matrix")
    for _p in [_root, _gamo, _gmat]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from galaga import Algebra, b_sta, exp
    import galaga_marimo as gm
    from galaga_matrix import MatrixRepr, from_spinor_column, to_matrix, to_spinor_column
    from galaga_matrix.matrix import compact_basis

    return (
        Algebra,
        MatrixRepr,
        b_sta,
        compact_basis,
        exp,
        from_spinor_column,
        gm,
        mo,
        np,
        to_matrix,
        to_spinor_column,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dirac, Weyl, and Majorana Bases

    `galaga_matrix` currently gives $Cl(1,3)$ spinor columns in the standard
    Dirac basis. This notebook shows how to keep the existing Dirac conversion,
    then apply unitary changes of basis to get Weyl and Majorana columns.

    The Weyl basis makes the stacked-Weyl form visible:

    $$
    \psi_W =
    \begin{pmatrix}
    \psi_L\\
    \psi_R
    \end{pmatrix}.
    $$

    The Majorana basis makes the real structure visible: charge conjugation is
    just componentwise complex conjugation, so a Majorana spinor is represented
    by a real four-component column.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Convention

    We use $Cl(1,3)$ with signature $(+,-,-,-)$. The current compact matrix
    representation uses the standard Dirac basis:

    $$
    \Gamma^0_D =
    \begin{pmatrix}
    I_2 & 0_2\\
    0_2 & -I_2
    \end{pmatrix}
    =
    \begin{pmatrix}
    1 & 0 & 0 & 0\\
    0 & 1 & 0 & 0\\
    0 & 0 & -1 & 0\\
    0 & 0 & 0 & -1
    \end{pmatrix}.
    $$

    Here $I_2$ is the $2\times2$ identity matrix and $0_2$ is the $2\times2$
    zero matrix. Neither is the STA pseudoscalar. The STA pseudoscalar is the
    grade-4 multivector $\gamma_0\gamma_1\gamma_2\gamma_3$.

    The Weyl basis used here has stack order

    $$
    \psi_W =
    \begin{pmatrix}
    \psi_L\\
    \psi_R
    \end{pmatrix},
    $$

    so the chirality matrix is

    $$
    \Gamma^5_W =
    \begin{pmatrix}
    -I_2 & 0_2\\
    0_2 & I_2
    \end{pmatrix}
    =
    \begin{pmatrix}
    -1 & 0 & 0 & 0\\
    0 & -1 & 0 & 0\\
    0 & 0 & 1 & 0\\
    0 & 0 & 0 & 1
    \end{pmatrix}.
    $$

    The Majorana basis used later is chosen from the charge-conjugation
    convention

    $$
    \psi_D^c = B_D\psi_D^*,
    \qquad
    B_D = i_{\mathbb C}\Gamma^2_D.
    $$

    Here $i_{\mathbb C}$ is the scalar complex imaginary, not the STA
    pseudoscalar. The Majorana change of basis is chosen so that

    $$
    U_{M\leftarrow D}B_DU_{M\leftarrow D}^T = I_4.
    $$

    Therefore in the Majorana basis,

    $$
    \psi_M^c = \psi_M^*.
    $$
    """)
    return


@app.cell
def _(Algebra, b_sta, compact_basis, np):
    sta = Algebra((1, -1, -1, -1), blades=b_sta(), repr_unicode=True)
    sta_g0, sta_g1, sta_g2, sta_g3 = sta.basis_vectors(lazy=True)

    dirac_gammas = compact_basis(sta)
    dirac_gamma0 = dirac_gammas[0]
    dirac_gamma5 = 1j * dirac_gammas[0] @ dirac_gammas[1] @ dirac_gammas[2] @ dirac_gammas[3]
    charge_conjugation_B_dirac = 1j * dirac_gammas[2]

    _I2 = np.eye(2, dtype=complex)
    weyl_from_dirac = (1 / np.sqrt(2)) * np.block(
        [
            [_I2, -_I2],
            [_I2, _I2],
        ]
    )
    dirac_from_weyl = weyl_from_dirac.conj().T

    weyl_gammas = [weyl_from_dirac @ _gamma @ dirac_from_weyl for _gamma in dirac_gammas]
    weyl_gamma0 = weyl_gammas[0]
    weyl_gamma5 = weyl_from_dirac @ dirac_gamma5 @ dirac_from_weyl
    left_chiral_projector = 0.5 * (np.eye(4, dtype=complex) - weyl_gamma5)
    right_chiral_projector = 0.5 * (np.eye(4, dtype=complex) + weyl_gamma5)

    majorana_from_dirac = (1 / np.sqrt(2)) * np.array(
        [
            [1j, 0, 0, -1j],
            [0, 1j, 1j, 0],
            [1, 0, 0, 1],
            [0, 1, -1, 0],
        ],
        dtype=complex,
    )
    dirac_from_majorana = majorana_from_dirac.conj().T
    majorana_gammas = [
        majorana_from_dirac @ _gamma @ dirac_from_majorana
        for _gamma in dirac_gammas
    ]
    majorana_gamma0 = majorana_gammas[0]
    majorana_gamma5 = majorana_from_dirac @ dirac_gamma5 @ dirac_from_majorana
    charge_conjugation_B_majorana = (
        majorana_from_dirac @ charge_conjugation_B_dirac @ majorana_from_dirac.T
    )
    return (
        charge_conjugation_B_dirac,
        charge_conjugation_B_majorana,
        dirac_from_majorana,
        dirac_from_weyl,
        dirac_gamma0,
        dirac_gamma5,
        dirac_gammas,
        left_chiral_projector,
        majorana_from_dirac,
        majorana_gamma0,
        majorana_gamma5,
        majorana_gammas,
        right_chiral_projector,
        sta,
        sta_g0,
        sta_g1,
        sta_g2,
        sta_g3,
        weyl_from_dirac,
        weyl_gamma0,
        weyl_gamma5,
        weyl_gammas,
    )


@app.cell
def _(
    MatrixRepr,
    dirac_gamma0,
    dirac_gamma5,
    gm,
    np,
    weyl_from_dirac,
    weyl_gamma0,
    weyl_gamma5,
):
    _unitary_ok = np.allclose(weyl_from_dirac.conj().T @ weyl_from_dirac, np.eye(4))
    _gamma0_shape_ok = np.allclose(
        weyl_gamma0,
        np.block(
            [
                [np.zeros((2, 2)), np.eye(2)],
                [np.eye(2), np.zeros((2, 2))],
            ]
        ),
    )
    _gamma5_shape_ok = np.allclose(weyl_gamma5, np.diag([-1, -1, 1, 1]))

    gm.md(t"""
    The basis-change matrix is:

    {MatrixRepr(weyl_from_dirac, label=r"U_{W\leftarrow D}"):block}

    It transforms gamma matrices by similarity:

    $$
    \\Gamma^\\mu_W =
    U_{{W\\leftarrow D}}\\Gamma^\\mu_DU_{{W\\leftarrow D}}^\\dagger.
    $$

    Dirac-basis $\\Gamma^0_D$ and $\\Gamma^5_D$:

    {MatrixRepr(dirac_gamma0, label=r"\Gamma^0_D"):block}

    {MatrixRepr(dirac_gamma5, label=r"\Gamma^5_D"):block}

    Weyl-basis $\\Gamma^0_W$ and $\\Gamma^5_W$:

    {MatrixRepr(weyl_gamma0, label=r"\Gamma^0_W"):block}

    {MatrixRepr(weyl_gamma5, label=r"\Gamma^5_W"):block}

    | Check | Result |
    |---|---:|
    | $U_{{W\\leftarrow D}}$ is unitary | {_unitary_ok} |
    | $\\Gamma^0_W$ is off-diagonal | {_gamma0_shape_ok} |
    | $\\Gamma^5_W=\\operatorname{{diag}}(-1,-1,+1,+1)$ | {_gamma5_shape_ok} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Majorana Basis: Making Charge Conjugation Real

    A Majorana basis is not another chirality split. It is a basis where the
    real structure of the Dirac representation is explicit.

    In the Dirac basis used here, charge conjugation is anti-linear:

    $$
    \psi_D^c = B_D\psi_D^*,
    \qquad
    B_D = i_{\mathbb C}\Gamma^2_D.
    $$

    In the Majorana basis,

    $$
    \psi_M = U_{M\leftarrow D}\psi_D,
    $$

    with $U_{M\leftarrow D}$ chosen so that

    $$
    B_M = U_{M\leftarrow D}B_DU_{M\leftarrow D}^T = I_4.
    $$

    Therefore charge conjugation becomes

    $$
    \psi_M^c = \psi_M^*.
    $$

    A generic Dirac spinor is still a complex four-component column in this
    basis. A Majorana spinor is the special case satisfying

    $$
    \psi_M = \psi_M^*.
    $$
    """)
    return


@app.cell
def _(
    MatrixRepr,
    charge_conjugation_B_dirac,
    charge_conjugation_B_majorana,
    dirac_gamma0,
    dirac_gamma5,
    gm,
    majorana_from_dirac,
    majorana_gamma0,
    majorana_gamma5,
    majorana_gammas,
    np,
):
    _I4 = np.eye(4, dtype=complex)
    _metric = np.diag([1, -1, -1, -1])
    _unitary_ok = np.allclose(
        majorana_from_dirac.conj().T @ majorana_from_dirac,
        _I4,
        atol=1e-10,
    )
    _charge_conjugation_ok = np.allclose(charge_conjugation_B_majorana, _I4, atol=1e-10)
    _pure_imaginary_ok = all(
        np.allclose(_gamma.real, 0, atol=1e-10)
        for _gamma in majorana_gammas
    )
    _clifford_ok = all(
        np.allclose(
            majorana_gammas[_mu] @ majorana_gammas[_nu]
            + majorana_gammas[_nu] @ majorana_gammas[_mu],
            2 * _metric[_mu, _nu] * _I4,
            atol=1e-10,
        )
        for _mu in range(4)
        for _nu in range(4)
    )
    _generators_real_ok = all(
        np.allclose((majorana_gammas[_mu] @ majorana_gammas[_nu]).imag, 0, atol=1e-10)
        for _mu in range(4)
        for _nu in range(_mu + 1, 4)
    )

    gm.md(t"""
    The Majorana basis-change matrix is:

    {MatrixRepr(majorana_from_dirac, label=r"U_{M\leftarrow D}"):block}

    Dirac-basis charge-conjugation matrix:

    {MatrixRepr(charge_conjugation_B_dirac, label=r"B_D=i_{\mathbb C}\Gamma^2_D"):block}

    Majorana-basis charge-conjugation matrix:

    {MatrixRepr(charge_conjugation_B_majorana, label=r"B_M"):block}

    Dirac-basis $\\Gamma^0_D$ and $\\Gamma^5_D$:

    {MatrixRepr(dirac_gamma0, label=r"\Gamma^0_D"):block}

    {MatrixRepr(dirac_gamma5, label=r"\Gamma^5_D"):block}

    Majorana-basis $\\Gamma^0_M$ and $\\Gamma^5_M$:

    {MatrixRepr(majorana_gamma0, label=r"\Gamma^0_M"):block}

    {MatrixRepr(majorana_gamma5, label=r"\Gamma^5_M"):block}

    | Check | Result |
    |---|---:|
    | $U_{{M\\leftarrow D}}$ is unitary | {_unitary_ok} |
    | $B_M=I_4$ | {_charge_conjugation_ok} |
    | all $\\Gamma^\\mu_M$ are pure imaginary | {_pure_imaginary_ok} |
    | Majorana gammas satisfy $\\{{\\Gamma^\\mu_M,\\Gamma^\\nu_M\\}}=2\\eta^{{\\mu\\nu}}I_4$ | {_clifford_ok} |
    | products $\\Gamma^\\mu_M\\Gamma^\\nu_M$ are real for $\\mu\\ne\\nu$ | {_generators_real_ok} |
    """)
    return


@app.cell
def _(
    charge_conjugation_B_dirac,
    dirac_from_majorana,
    dirac_from_weyl,
    majorana_from_dirac,
    np,
    weyl_from_dirac,
):
    def dirac_to_weyl_column(column):
        return weyl_from_dirac @ column

    def weyl_to_dirac_column(column):
        return dirac_from_weyl @ column

    def dirac_to_weyl_matrix(matrix):
        return weyl_from_dirac @ matrix @ dirac_from_weyl

    def weyl_to_dirac_matrix(matrix):
        return dirac_from_weyl @ matrix @ weyl_from_dirac

    def dirac_to_majorana_column(column):
        return majorana_from_dirac @ column

    def majorana_to_dirac_column(column):
        return dirac_from_majorana @ column

    def dirac_to_majorana_matrix(matrix):
        return majorana_from_dirac @ matrix @ dirac_from_majorana

    def majorana_to_dirac_matrix(matrix):
        return dirac_from_majorana @ matrix @ majorana_from_dirac

    def charge_conjugate_dirac_column(column):
        return charge_conjugation_B_dirac @ column.conj()

    def charge_conjugate_majorana_column(column):
        return column.conj()

    def dirac_adjoint(column, gamma0_matrix):
        return column.conj().T @ gamma0_matrix

    def dirac_scalar(column, gamma0_matrix):
        return float(np.real((dirac_adjoint(column, gamma0_matrix) @ column)[0, 0]))

    def dirac_pseudoscalar(column, gamma0_matrix, gamma5_matrix):
        return float(np.real((dirac_adjoint(column, gamma0_matrix) @ (1j * gamma5_matrix) @ column)[0, 0]))

    def dirac_current_components(column, gamma0_matrix, gamma_matrices):
        _bar = dirac_adjoint(column, gamma0_matrix)
        return np.array(
            [float(np.real((_bar @ _gamma @ column)[0, 0])) for _gamma in gamma_matrices]
        )

    return (
        charge_conjugate_dirac_column,
        charge_conjugate_majorana_column,
        dirac_current_components,
        dirac_pseudoscalar,
        dirac_scalar,
        dirac_to_majorana_column,
        dirac_to_majorana_matrix,
        dirac_to_weyl_column,
        dirac_to_weyl_matrix,
        majorana_to_dirac_column,
        majorana_to_dirac_matrix,
        weyl_to_dirac_column,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Vectors: Same Operator, New Coordinates

    A spacetime vector $v$ becomes a $4\times4$ Dirac-basis matrix
    $\rho_D(v)$. To view the same operator in another basis:

    $$
    \rho_X(v)
    =
    U_{X\leftarrow D}\rho_D(v)U_{X\leftarrow D}^\dagger.
    $$

    This changes matrix coordinates, not the underlying vector. The Clifford
    square is preserved:

    $$
    \rho_X(v)^2 = v^2 I_4.
    $$
    """)
    return


@app.cell
def _(mo):
    vector_t = mo.ui.slider(-2.0, 2.0, value=1.3, step=0.1, label="v0", show_value=True)
    vector_x = mo.ui.slider(-2.0, 2.0, value=0.5, step=0.1, label="v1", show_value=True)
    vector_y = mo.ui.slider(-2.0, 2.0, value=-0.4, step=0.1, label="v2", show_value=True)
    vector_z = mo.ui.slider(-2.0, 2.0, value=0.2, step=0.1, label="v3", show_value=True)
    return vector_t, vector_x, vector_y, vector_z


@app.cell
def _(
    MatrixRepr,
    dirac_to_majorana_matrix,
    dirac_to_weyl_matrix,
    gm,
    mo,
    np,
    sta_g0,
    sta_g1,
    sta_g2,
    sta_g3,
    to_matrix,
    vector_t,
    vector_x,
    vector_y,
    vector_z,
):
    _v = (
        vector_t.value * sta_g0
        + vector_x.value * sta_g1
        + vector_y.value * sta_g2
        + vector_z.value * sta_g3
    ).eval().name("v")
    _v_square = float((_v * _v).eval().data[0])
    _dirac_vector_matrix = to_matrix(_v, mode="compact")
    _weyl_vector_matrix = dirac_to_weyl_matrix(_dirac_vector_matrix)
    _majorana_vector_matrix = dirac_to_majorana_matrix(_dirac_vector_matrix)
    _weyl_square_ok = np.allclose(
        _weyl_vector_matrix @ _weyl_vector_matrix,
        _v_square * np.eye(4),
        atol=1e-10,
    )
    _majorana_square_ok = np.allclose(
        _majorana_vector_matrix @ _majorana_vector_matrix,
        _v_square * np.eye(4),
        atol=1e-10,
    )
    _majorana_vector_pure_imaginary_ok = np.allclose(
        _majorana_vector_matrix.real,
        0,
        atol=1e-10,
    )

    _md = gm.md(t"""
    Spacetime vector:

    {_v.display()}

    Dirac-basis matrix:

    {MatrixRepr(_dirac_vector_matrix, label=r"\rho_D(v)"):block}

    Weyl-basis matrix:

    {MatrixRepr(_weyl_vector_matrix, label=r"\rho_W(v)"):block}

    Majorana-basis matrix:

    {MatrixRepr(_majorana_vector_matrix, label=r"\rho_M(v)"):block}

    | Check | Result |
    |---|---:|
    | $v^2$ from GA | {_v_square:.6f} |
    | $\\rho_W(v)^2 = v^2I_4$ | {_weyl_square_ok} |
    | $\\rho_M(v)^2 = v^2I_4$ | {_majorana_square_ok} |
    | $\\rho_M(v)$ is pure imaginary | {_majorana_vector_pure_imaginary_ok} |
    """)

    mo.vstack([vector_t, vector_x, vector_y, vector_z, _md])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Spinors: Existing Dirac Roundtrip, Then Basis Views

    The existing API gives:

    $$
    \Psi
    \xrightarrow{\operatorname{to\_spinor\_column}}
    \psi_D.
    $$

    The Weyl- and Majorana-basis columns are then just:

    $$
    \psi_W = U_{W\leftarrow D}\psi_D,
    \qquad
    \psi_M = U_{M\leftarrow D}\psi_D.
    $$

    In this convention the top two entries are $\psi_L$ and the bottom two
    entries are $\psi_R$:

    $$
    \psi_W =
    \begin{pmatrix}
    \psi_L\\
    \psi_R
    \end{pmatrix}.
    $$

    In the Majorana basis, the generic column is still complex. It becomes a
    Majorana spinor only when it is real:

    $$
    \psi_M=\psi_M^*.
    $$

    To recover the GA spinor from either alternate basis, first transform back
    to the Dirac basis and then use the existing inverse:

    $$
    \Psi =
    \operatorname{from\_spinor\_column}
    \left(U_{X\leftarrow D}^\dagger\psi_X\right).
    $$
    """)
    return


@app.cell
def _(mo):
    source_boost = mo.ui.slider(-1.2, 1.2, value=0.45, step=0.01, label="source boost", show_value=True)
    source_rotation = mo.ui.slider(-3.14, 3.14, value=0.8, step=0.01, label="source rotation", show_value=True)
    source_phase = mo.ui.slider(-0.6, 0.6, value=0.25, step=0.01, label="pseudoscalar phase part", show_value=True)
    return source_boost, source_phase, source_rotation


@app.cell
def _(
    MatrixRepr,
    charge_conjugate_dirac_column,
    charge_conjugate_majorana_column,
    dirac_to_majorana_column,
    dirac_to_weyl_column,
    from_spinor_column,
    gm,
    left_chiral_projector,
    majorana_to_dirac_column,
    mo,
    np,
    right_chiral_projector,
    source_boost,
    source_phase,
    source_rotation,
    sta,
    sta_g0,
    sta_g1,
    sta_g2,
    sta_g3,
    to_spinor_column,
    weyl_gamma5,
    weyl_to_dirac_column,
):
    _I = sta.pseudoscalar()
    _source_spinor = (
        sta.scalar(1.0)
        + source_boost.value * (sta_g0 * sta_g1).eval()
        + 0.35 * (sta_g1 * sta_g2).eval()
        - 0.20 * (sta_g0 * sta_g3).eval()
        + source_phase.value * _I
        + 0.15 * source_rotation.value * (sta_g2 * sta_g3).eval()
    ).name(latex=r"\Psi")

    _dirac_column = to_spinor_column(_source_spinor)
    _weyl_column = dirac_to_weyl_column(_dirac_column)
    _majorana_column = dirac_to_majorana_column(_dirac_column)
    _left_column = _weyl_column[:2, :]
    _right_column = _weyl_column[2:, :]
    _projected_left = left_chiral_projector @ _weyl_column
    _projected_right = right_chiral_projector @ _weyl_column
    _left_projector_ok = np.allclose(_projected_left[:2, :], _left_column) and np.allclose(_projected_left[2:, :], 0)
    _right_projector_ok = np.allclose(_projected_right[:2, :], 0) and np.allclose(_projected_right[2:, :], _right_column)
    _left_chirality_ok = np.allclose(weyl_gamma5 @ _projected_left, -_projected_left)
    _right_chirality_ok = np.allclose(weyl_gamma5 @ _projected_right, _projected_right)
    _dirac_column_back = weyl_to_dirac_column(_weyl_column)
    _column_roundtrip_ok = np.allclose(_dirac_column_back, _dirac_column, atol=1e-10)
    _dirac_column_from_majorana = majorana_to_dirac_column(_majorana_column)
    _majorana_column_roundtrip_ok = np.allclose(
        _dirac_column_from_majorana,
        _dirac_column,
        atol=1e-10,
    )
    _charge_conjugation_commutes_ok = np.allclose(
        dirac_to_majorana_column(charge_conjugate_dirac_column(_dirac_column)),
        charge_conjugate_majorana_column(_majorana_column),
        atol=1e-10,
    )
    _spinor_back = from_spinor_column(sta, _dirac_column_back).name(latex=r"\Psi'")
    _ga_roundtrip_ok = np.allclose(_spinor_back.data, _source_spinor.data, atol=1e-10)

    _real_majorana_column = np.array([[1.0], [0.25], [-0.5], [0.75]], dtype=complex)
    _real_majorana_dirac_column = majorana_to_dirac_column(_real_majorana_column)
    _real_majorana_spinor = from_spinor_column(
        sta,
        _real_majorana_dirac_column,
    ).name(latex=r"\Psi_{\mathrm{real}\ M}")
    _real_majorana_is_real_ok = np.allclose(
        _real_majorana_column,
        charge_conjugate_majorana_column(_real_majorana_column),
        atol=1e-10,
    )
    _real_majorana_dirac_condition_ok = np.allclose(
        charge_conjugate_dirac_column(_real_majorana_dirac_column),
        _real_majorana_dirac_column,
        atol=1e-10,
    )
    _real_majorana_ga_roundtrip_ok = np.allclose(
        dirac_to_majorana_column(to_spinor_column(_real_majorana_spinor)),
        _real_majorana_column,
        atol=1e-10,
    )

    _md = gm.md(t"""
    Source STA spinor:

    {_source_spinor.display()}

    Dirac-basis column:

    {MatrixRepr(_dirac_column, label=r"\psi_D"):block}

    Weyl-basis column:

    {MatrixRepr(_weyl_column, label=r"\psi_W"):block}

    Majorana-basis column:

    {MatrixRepr(_majorana_column, label=r"\psi_M"):block}

    Left and right Weyl components:

    {MatrixRepr(_left_column, label=r"\psi_L"):block}

    {MatrixRepr(_right_column, label=r"\psi_R"):block}

    Recovered STA spinor:

    {_spinor_back.display()}

    Real Majorana-column example:

    {MatrixRepr(_real_majorana_column, label=r"\chi_M"):block}

    Same spinor recovered as an STA even multivector:

    {_real_majorana_spinor.display()}

    | Check | Result |
    |---|---:|
    | $\\psi_D \\to \\psi_W \\to \\psi_D$ | {_column_roundtrip_ok} |
    | $\\psi_D \\to \\psi_M \\to \\psi_D$ | {_majorana_column_roundtrip_ok} |
    | Weyl column back to GA roundtrips | {_ga_roundtrip_ok} |
    | charge conjugation maps to complex conjugation in Majorana basis | {_charge_conjugation_commutes_ok} |
    | $P_L\\psi_W$ keeps top block only | {_left_projector_ok} |
    | $P_R\\psi_W$ keeps bottom block only | {_right_projector_ok} |
    | $\\Gamma^5_WP_L\\psi_W=-P_L\\psi_W$ | {_left_chirality_ok} |
    | $\\Gamma^5_WP_R\\psi_W=+P_R\\psi_W$ | {_right_chirality_ok} |
    | real $\\chi_M$ satisfies $\\chi_M=\\chi_M^*$ | {_real_majorana_is_real_ok} |
    | same real $\\chi_M$ satisfies $\\psi_D^c=\\psi_D$ in Dirac basis | {_real_majorana_dirac_condition_ok} |
    | real Majorana-column example roundtrips through GA | {_real_majorana_ga_roundtrip_ok} |
    """)

    mo.vstack([source_boost, source_rotation, source_phase, _md])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lorentz Action in Weyl and Majorana Bases

    The same similarity transform applies to spinor-action matrices. If

    $$
    \psi'_D = \rho_D(L)\psi_D,
    $$

    then in any transformed basis:

    $$
    \psi'_X =
    \rho_X(L)\psi_X,
    \qquad
    \rho_X(L) =
    U_{X\leftarrow D}\rho_D(L)U_{X\leftarrow D}^\dagger.
    $$

    The Dirac bilinears should agree in all bases when the gamma matrices and
    columns are transformed together. In the Majorana basis, proper Lorentz
    rotor matrices are real because the bivector generators
    $\Gamma^\mu_M\Gamma^\nu_M$ are real.
    """)
    return


@app.cell
def _(mo):
    action_boost = mo.ui.slider(-1.2, 1.2, value=0.7, step=0.01, label="action boost", show_value=True)
    action_rotation = mo.ui.slider(-3.14, 3.14, value=-0.45, step=0.01, label="action rotation", show_value=True)
    return action_boost, action_rotation


@app.cell
def _(
    MatrixRepr,
    action_boost,
    action_rotation,
    dirac_current_components,
    dirac_gamma0,
    dirac_gamma5,
    dirac_gammas,
    dirac_pseudoscalar,
    dirac_scalar,
    dirac_to_majorana_column,
    dirac_to_majorana_matrix,
    dirac_to_weyl_column,
    dirac_to_weyl_matrix,
    exp,
    from_spinor_column,
    gm,
    majorana_gamma0,
    majorana_gamma5,
    majorana_gammas,
    mo,
    np,
    source_boost,
    source_phase,
    source_rotation,
    sta,
    sta_g0,
    sta_g1,
    sta_g2,
    sta_g3,
    to_matrix,
    to_spinor_column,
    weyl_gamma0,
    weyl_gamma5,
    weyl_gammas,
):
    _I = sta.pseudoscalar()
    _source_spinor = (
        sta.scalar(1.0)
        + source_boost.value * (sta_g0 * sta_g1).eval()
        + 0.35 * (sta_g1 * sta_g2).eval()
        - 0.20 * (sta_g0 * sta_g3).eval()
        + source_phase.value * _I
        + 0.15 * source_rotation.value * (sta_g2 * sta_g3).eval()
    ).name(latex=r"\Psi")

    _action = (
        exp((action_boost.value / 2) * (sta_g0 * sta_g1).eval())
        * exp((-action_rotation.value / 2) * (sta_g2 * sta_g3).eval())
    ).name(latex=r"L")

    _dirac_action_matrix = to_matrix(_action, mode="compact")
    _weyl_action_matrix = dirac_to_weyl_matrix(_dirac_action_matrix)
    _majorana_action_matrix = dirac_to_majorana_matrix(_dirac_action_matrix)
    _dirac_column = to_spinor_column(_source_spinor)
    _weyl_column = dirac_to_weyl_column(_dirac_column)
    _majorana_column = dirac_to_majorana_column(_dirac_column)
    _dirac_after = _dirac_action_matrix @ _dirac_column
    _weyl_after_from_dirac = dirac_to_weyl_column(_dirac_after)
    _weyl_after_direct = _weyl_action_matrix @ _weyl_column
    _majorana_after_from_dirac = dirac_to_majorana_column(_dirac_after)
    _majorana_after_direct = _majorana_action_matrix @ _majorana_column
    _action_commutes_with_basis_change = np.allclose(_weyl_after_from_dirac, _weyl_after_direct, atol=1e-10)
    _majorana_action_commutes_with_basis_change = np.allclose(
        _majorana_after_from_dirac,
        _majorana_after_direct,
        atol=1e-10,
    )
    _majorana_action_real_ok = np.allclose(
        _majorana_action_matrix.imag,
        0,
        atol=1e-10,
    )

    _ga_after = from_spinor_column(sta, _dirac_after).name(latex=r"\Psi'")
    _ga_expected = (_action * _source_spinor).eval()
    _ga_action_ok = np.allclose(_ga_after.data, _ga_expected.data, atol=1e-10)

    _scalar_dirac = dirac_scalar(_dirac_after, dirac_gamma0)
    _scalar_weyl = dirac_scalar(_weyl_after_direct, weyl_gamma0)
    _scalar_majorana = dirac_scalar(_majorana_after_direct, majorana_gamma0)
    _pseudoscalar_dirac = dirac_pseudoscalar(_dirac_after, dirac_gamma0, dirac_gamma5)
    _pseudoscalar_weyl = dirac_pseudoscalar(_weyl_after_direct, weyl_gamma0, weyl_gamma5)
    _pseudoscalar_majorana = dirac_pseudoscalar(
        _majorana_after_direct,
        majorana_gamma0,
        majorana_gamma5,
    )
    _current_dirac = dirac_current_components(_dirac_after, dirac_gamma0, dirac_gammas)
    _current_weyl = dirac_current_components(_weyl_after_direct, weyl_gamma0, weyl_gammas)
    _current_majorana = dirac_current_components(
        _majorana_after_direct,
        majorana_gamma0,
        majorana_gammas,
    )
    _scalar_basis_ok = (
        np.isclose(_scalar_dirac, _scalar_weyl, atol=1e-10)
        and np.isclose(_scalar_dirac, _scalar_majorana, atol=1e-10)
    )
    _pseudoscalar_basis_ok = (
        np.isclose(_pseudoscalar_dirac, _pseudoscalar_weyl, atol=1e-10)
        and np.isclose(_pseudoscalar_dirac, _pseudoscalar_majorana, atol=1e-10)
    )
    _current_basis_ok = (
        np.allclose(_current_dirac, _current_weyl, atol=1e-10)
        and np.allclose(_current_dirac, _current_majorana, atol=1e-10)
    )

    _md = gm.md(t"""
    Lorentz action:

    {_action.display()}

    Weyl-basis action matrix:

    {MatrixRepr(_weyl_action_matrix, label=r"\rho_W(L)"):block}

    Majorana-basis action matrix:

    {MatrixRepr(_majorana_action_matrix, label=r"\rho_M(L)"):block}

    Transformed Weyl column:

    {MatrixRepr(_weyl_after_direct, label=r"\psi'_W"):block}

    Transformed Majorana column:

    {MatrixRepr(_majorana_after_direct, label=r"\psi'_M"):block}

    Recovered GA spinor:

    {_ga_after.display()}

    | Compatibility check | Result |
    |---|---:|
    | $U(\\rho_D(L)\\psi_D)=\\rho_W(L)(U\\psi_D)$ | {_action_commutes_with_basis_change} |
    | $U(\\rho_D(L)\\psi_D)=\\rho_M(L)(U\\psi_D)$ | {_majorana_action_commutes_with_basis_change} |
    | $\\rho_M(L)$ is real | {_majorana_action_real_ok} |
    | recovered GA spinor equals $L\\Psi$ | {_ga_action_ok} |
    | scalar bilinear agrees in all bases | {_scalar_basis_ok} |
    | pseudoscalar bilinear agrees in all bases | {_pseudoscalar_basis_ok} |
    | current components agree in all bases | {_current_basis_ok} |
    | scalar after action | {_scalar_weyl:.6f} |
    | pseudoscalar after action | {_pseudoscalar_weyl:.6f} |
    | $j^\\mu$ after action | $({_current_weyl[0]:.6f}, {_current_weyl[1]:.6f}, {_current_weyl[2]:.6f}, {_current_weyl[3]:.6f})$ |
    """)

    mo.vstack([action_boost, action_rotation, _md])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What This Proves

    This notebook does not need a new core representation yet. The current
    Dirac-basis machinery already gives faithful STA spinor columns. Weyl and
    Majorana views can be layered on top by:

    $$
    \psi_W = U_{W\leftarrow D}\psi_D,
    \qquad
    \psi_M = U_{M\leftarrow D}\psi_D,
    $$

    and

    $$
    M_X = U_{X\leftarrow D}M_DU_{X\leftarrow D}^\dagger.
    $$

    That gives a practical implementation path:

    - keep `to_spinor_column` and `to_matrix` in the current Dirac basis;
    - add explicit helper functions for named basis changes;
    - test gamma matrices, charge conjugation, projectors, roundtrips, and bilinears;
    - only later promote this into a basis-aware public API.
    """)
    return


if __name__ == "__main__":
    app.run()
