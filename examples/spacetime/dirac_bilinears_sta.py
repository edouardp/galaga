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

    from galaga.facade import Algebra, spacetime_blade_convention, exp, reverse
    import galaga_marimo as gm
    from galaga_matrix import MatrixRepr, from_spinor_column, to_matrix, to_spinor_column
    from galaga_matrix.matrix import compact_basis

    return (
        Algebra,
        MatrixRepr,
        spacetime_blade_convention,
        compact_basis,
        exp,
        from_spinor_column,
        gm,
        mo,
        np,
        reverse,
        to_matrix,
        to_spinor_column,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dirac Bilinears in STA and Matrix QM

    A Dirac column has four complex entries, but the quantities that carry
    geometric and physical meaning are usually quadratic in the column. These
    are the Dirac bilinears.

    This notebook compares the matrix formulas with their spacetime algebra
    counterparts using the local `galaga_matrix` package.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Setup

    We use spacetime algebra

    $$
    Cl(1,3),
    \qquad
    \eta = \operatorname{diag}(1,-1,-1,-1).
    $$

    A GA spinor is an even multivector

    $$
    \Psi \in Cl^0(1,3).
    $$

    The matrix spinor column is obtained from a fixed reference column $u$:

    $$
    \psi = \rho(\Psi)u,
    \qquad
    u =
    \begin{pmatrix}
    1\\0\\0\\0
    \end{pmatrix}.
    $$

    The Dirac adjoint is

    $$
    \bar\psi = \psi^\dagger \Gamma^0.
    $$
    """)
    return


@app.cell
def _(Algebra, spacetime_blade_convention, compact_basis, np):
    sta = Algebra((1, -1, -1, -1), blades=spacetime_blade_convention(), )
    g0, g1, g2, g3 = sta.basis_vectors(expr=True)
    gamma_matrices = compact_basis(sta)
    gamma0_matrix = gamma_matrices[0]
    gamma5_matrix = 1j * gamma_matrices[0] @ gamma_matrices[1] @ gamma_matrices[2] @ gamma_matrices[3]
    eta_diag = np.array([1.0, -1.0, -1.0, -1.0])
    return g0, g1, g2, g3, gamma0_matrix, gamma5_matrix, gamma_matrices, sta


@app.cell
def _(np):
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

    def lower_spatial_components(raised_components):
        _lowered = np.array(raised_components, dtype=float).copy()
        _lowered[1:] *= -1
        return _lowered

    return (
        dirac_current_components,
        dirac_pseudoscalar,
        dirac_scalar,
        lower_spatial_components,
    )


@app.cell
def _(MatrixRepr, gamma0_matrix, gamma5_matrix, gamma_matrices, gm):
    _gamma0 = MatrixRepr(gamma0_matrix).name(latex=r"\Gamma^0")
    _gamma1 = MatrixRepr(gamma_matrices[1]).name(latex=r"\Gamma^1")
    _gamma5 = MatrixRepr(gamma5_matrix).name(latex=r"\Gamma^5")

    gm.md(rt"""
    The compact matrix representation supplies the gamma matrices:

    {_gamma0:block}

    {_gamma1:block}

    and

    {_gamma5:block}

    where

    $$
    \\Gamma^5 = i\\Gamma^0\\Gamma^1\\Gamma^2\\Gamma^3.
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Bilinear Dictionary

    The notebook checks these translations:

    $$
    \sigma = \bar\psi\psi
    =
    \langle \Psi\widetilde{\Psi} \rangle_0,
    $$

    $$
    \pi = \bar\psi\, i\Gamma^5\psi
    =
    \langle \Psi\widetilde{\Psi} \rangle_I,
    $$

    and the Dirac current:

    $$
    j^\mu = \bar\psi\Gamma^\mu\psi.
    $$

    The matching STA vector is

    $$
    J = \Psi\gamma_0\widetilde{\Psi}.
    $$

    Since the displayed STA basis has signature $(+,-,-,-)$, the matrix
    component list $j^\mu$ and the coefficients printed on
    $\{\gamma_0,\gamma_1,\gamma_2,\gamma_3\}$ differ by metric lowering:

    $$
    J =
    j^0\gamma_0 -
    j^1\gamma_1 -
    j^2\gamma_2 -
    j^3\gamma_3.
    $$
    """)
    return


@app.cell
def _(mo):
    source_phase = mo.ui.slider(
        -0.6,
        0.6,
        value=0.2,
        step=0.01,
        label="pseudoscalar part of source spinor",
        show_value=True,
    )
    return (source_phase,)


@app.cell
def _(
    MatrixRepr,
    dirac_current_components,
    dirac_pseudoscalar,
    dirac_scalar,
    from_spinor_column,
    g0,
    g1,
    g2,
    gamma0_matrix,
    gamma5_matrix,
    gamma_matrices,
    gm,
    lower_spatial_components,
    mo,
    np,
    reverse,
    source_phase,
    sta,
    to_spinor_column,
):
    _I = sta.pseudoscalar()
    _source = (
        sta.scalar(0.9)
        + 0.20 * (g0 * g1)
        - 0.10 * (g0 * g2)
        + 0.30 * (g1 * g2)
        + source_phase.value * _I
    ).named(r"\Psi", latex=r"\Psi")

    _column = to_spinor_column(_source)
    _roundtrip = from_spinor_column(sta, _column).named(r"\Psi'", latex=r"\Psi'")
    _roundtrip_ok = np.allclose(_roundtrip.data, _source.data, atol=1e-10)

    _rho = (_source * reverse(_source)).named(r"\Psi\widetilde{\Psi}", latex=r"\Psi\widetilde{\Psi}")
    _sigma_matrix = dirac_scalar(_column, gamma0_matrix)
    _pi_matrix = dirac_pseudoscalar(_column, gamma0_matrix, gamma5_matrix)
    _sigma_ga = float(_rho.data[0])
    _pi_ga = float(_rho.data[-1])
    _scalar_ok = np.isclose(_sigma_matrix, _sigma_ga, atol=1e-10)
    _pseudoscalar_ok = np.isclose(_pi_matrix, _pi_ga, atol=1e-10)

    _current_components = dirac_current_components(_column, gamma0_matrix, gamma_matrices)
    _lowered_current = lower_spatial_components(_current_components)
    _current_ga = (_source * g0 * reverse(_source)).named(r"J", latex=r"J")
    _current_ok = np.allclose(_current_ga.vector_part, _lowered_current, atol=1e-10)
    _current_square = float((_current_ga * _current_ga).data[0])
    _fierz_rhs = _sigma_matrix**2 + _pi_matrix**2
    _fierz_ok = np.isclose(_current_square, _fierz_rhs, atol=1e-10)

    _md = gm.md(rt"""
    Source even multivector:

    {_source.display()}

    Its Dirac column:

    {MatrixRepr(_column).name(latex=r"\psi"):block}

    Roundtrip through the column map:

    {_roundtrip.display()}

    The scalar-plus-pseudoscalar product is:

    {_rho.display()}

    The current vector is:

    {_current_ga.display()}

    | Check | Result |
    |---|---:|
    | `from_spinor_column(sta, to_spinor_column(Ψ)) == Ψ` | {_roundtrip_ok} |
    | $\\bar\\psi\\psi = \\langle\\Psi\\widetilde{{\\Psi}}\\rangle_0$ | {_scalar_ok} |
    | $\\bar\\psi\\,i\\Gamma^5\\psi = \\langle\\Psi\\widetilde{{\\Psi}}\\rangle_I$ | {_pseudoscalar_ok} |
    | $j^\\mu$ matches $J=\\Psi\\gamma_0\\widetilde{{\\Psi}}$ after metric lowering | {_current_ok} |
    | $J^2 = \\sigma^2 + \\pi^2$ | {_fierz_ok} |
    | $\\sigma$ from matrix | {_sigma_matrix:.6f} |
    | $\\sigma$ from GA | {_sigma_ga:.6f} |
    | $\\pi$ from matrix | {_pi_matrix:.6f} |
    | $\\pi$ from GA | {_pi_ga:.6f} |
    | $j^\\mu$ from matrix | $({_current_components[0]:.6f}, {_current_components[1]:.6f}, {_current_components[2]:.6f}, {_current_components[3]:.6f})$ |
    | coefficients of $J$ in the displayed GA basis | $({_current_ga.vector_part[0]:.6f}, {_current_ga.vector_part[1]:.6f}, {_current_ga.vector_part[2]:.6f}, {_current_ga.vector_part[3]:.6f})$ |
    """)

    mo.vstack([source_phase, _md])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lorentz Covariance

    A proper Lorentz spin transformation is represented by a normalized even
    multivector $L$:

    $$
    L\widetilde L = 1.
    $$

    The matrix spin representation acts on the column by left multiplication:

    $$
    \psi' = \rho(L)\psi.
    $$

    The matching STA spinor is

    $$
    \Psi' = L\Psi.
    $$

    Scalars and pseudoscalars are invariant under this left action, while the
    current transforms as a spacetime vector:

    $$
    J' = L J \widetilde L.
    $$

    The ordinary positive-definite column norm $\psi^\dagger\psi$ is not a
    Lorentz scalar. The Dirac bilinears are the invariant or covariant objects.
    """)
    return


@app.cell
def _(mo, np):
    boost_rapidity = mo.ui.slider(
        -1.4,
        1.4,
        value=0.65,
        step=0.01,
        label="boost rapidity",
        show_value=True,
    )
    rotation_angle = mo.ui.slider(
        -float(np.pi),
        float(np.pi),
        value=0.55,
        step=0.01,
        label="spatial rotation angle",
        show_value=True,
    )
    return boost_rapidity, rotation_angle


@app.cell
def _(
    MatrixRepr,
    boost_rapidity,
    dirac_current_components,
    dirac_pseudoscalar,
    dirac_scalar,
    exp,
    from_spinor_column,
    g0,
    g1,
    g2,
    g3,
    gamma0_matrix,
    gamma5_matrix,
    gamma_matrices,
    gm,
    lower_spatial_components,
    mo,
    np,
    reverse,
    rotation_angle,
    source_phase,
    sta,
    to_matrix,
    to_spinor_column,
):
    _I = sta.pseudoscalar()
    _source = (
        sta.scalar(0.9)
        + 0.20 * (g0 * g1)
        - 0.10 * (g0 * g2)
        + 0.30 * (g1 * g2)
        + source_phase.value * _I
    ).named(r"\Psi", latex=r"\Psi")

    _L = (
        exp((boost_rapidity.value / 2) * (g0 * g1))
        * exp((-rotation_angle.value / 2) * (g2 * g3))
    ).named(r"L", latex=r"L")
    _L_matrix = to_matrix(_L, mode="compact")
    _lorentz_metric_ok = np.allclose(_L_matrix.conj().T @ gamma0_matrix @ _L_matrix, gamma0_matrix, atol=1e-10)

    _column = to_spinor_column(_source)
    _column_after = _L_matrix @ _column
    _source_after = from_spinor_column(sta, _column_after).named(r"\Psi'", latex=r"\Psi'")
    _expected_source_after = (_L * _source)
    _left_action_ok = np.allclose(_source_after.data, _expected_source_after.data, atol=1e-10)

    _sigma_before = dirac_scalar(_column, gamma0_matrix)
    _sigma_after = dirac_scalar(_column_after, gamma0_matrix)
    _pi_before = dirac_pseudoscalar(_column, gamma0_matrix, gamma5_matrix)
    _pi_after = dirac_pseudoscalar(_column_after, gamma0_matrix, gamma5_matrix)
    _scalar_invariant_ok = np.isclose(_sigma_before, _sigma_after, atol=1e-10)
    _pseudoscalar_invariant_ok = np.isclose(_pi_before, _pi_after, atol=1e-10)

    _norm_before = float(np.real((_column.conj().T @ _column)[0, 0]))
    _norm_after = float(np.real((_column_after.conj().T @ _column_after)[0, 0]))

    _current_before = (_source * g0 * reverse(_source)).named(r"J", latex=r"J")
    _current_after = (_source_after * g0 * reverse(_source_after)).named(r"J'", latex=r"J'")
    _expected_current_after = (_L * _current_before * reverse(_L))
    _current_covariant_ok = np.allclose(_current_after.data, _expected_current_after.data, atol=1e-10)

    _matrix_current_after = dirac_current_components(_column_after, gamma0_matrix, gamma_matrices)
    _lowered_matrix_current_after = lower_spatial_components(_matrix_current_after)
    _matrix_current_ok = np.allclose(_current_after.vector_part, _lowered_matrix_current_after, atol=1e-10)

    _md = gm.md(rt"""
    Lorentz spinor:

    {_L.display()}

    Matrix representative:

    {MatrixRepr(_L_matrix).name(latex=r"\rho(L)"):block}

    Transformed column:

    {MatrixRepr(_column_after).name(latex=r"\psi'"):block}

    Transformed GA spinor:

    {_source_after.display()}

    Transformed current:

    {_current_after.display()}

    | Lorentz-covariance check | Result |
    |---|---:|
    | $\\rho(L)^\\dagger\\Gamma^0\\rho(L)=\\Gamma^0$ | {_lorentz_metric_ok} |
    | column action reconstructs $L\\Psi$ | {_left_action_ok} |
    | $\\bar\\psi\\psi$ is invariant | {_scalar_invariant_ok} |
    | $\\bar\\psi\\,i\\Gamma^5\\psi$ is invariant | {_pseudoscalar_invariant_ok} |
    | $J'$ equals $LJ\\widetilde{{L}}$ | {_current_covariant_ok} |
    | matrix current matches GA current after metric lowering | {_matrix_current_ok} |
    | ordinary norm before | {_norm_before:.6f} |
    | ordinary norm after | {_norm_after:.6f} |
    | scalar before | {_sigma_before:.6f} |
    | scalar after | {_sigma_after:.6f} |
    | pseudoscalar before | {_pi_before:.6f} |
    | pseudoscalar after | {_pi_after:.6f} |
    """)

    mo.vstack([boost_rapidity, rotation_angle, _md])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What This Notebook Is Not Doing

    The full Dirac bilinear family also includes an axial vector and an
    antisymmetric tensor:

    $$
    \bar\psi\Gamma^\mu\Gamma^5\psi,
    \qquad
    \bar\psi\,i[\Gamma^\mu,\Gamma^\nu]\psi.
    $$

    Those are useful, but they add another layer of sign and index conventions.
    The purpose here is the first translation bridge:

    - even STA multivector $\Psi$
    - Dirac column $\psi$
    - scalar and pseudoscalar bilinears
    - vector current
    - Lorentz covariance checks

    Once these are comfortable, the axial and tensor bilinears are natural
    follow-up notebooks.
    """)
    return


if __name__ == "__main__":
    app.run()
