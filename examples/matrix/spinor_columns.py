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
    from galaga_matrix import (
        from_spinor_column,
        to_matrix,
        to_spinor_column,
    )

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        exp,
        p_euclidean,
        p_sta,
        reverse,
    )

    return (
        Algebra,
        DisplayPolicy,
        exp,
        from_spinor_column,
        gm,
        mo,
        np,
        p_euclidean,
        p_sta,
        reverse,
        to_matrix,
        to_spinor_column,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Spinor columns from even-multivector representatives

    **Convention:** after choosing a spin frame, matrix representation, and
    fixed reference column $u$, a Pauli or Dirac spinor can be represented by
    an even multivector $\psi$. Its conventional column is

    $$
    |\psi\rangle=\varrho(\psi)u.
    $$

    The even multivector is therefore a convention-dependent spinor
    representative, not an intrinsic identification of every even element
    with a physical spinor. The conversion is reversible only when this
    concrete real-linear map is full rank.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Pauli spinor from a $Cl(3,0)$ rotor

    `to_spinor_column` accepts any even multivector, not only a normalized
    rotor. For $Cl(3,0)$ it returns a two-component complex `MatrixRepr` with
    `kind="ket"` and `basis="pauli"`.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, exp, np, p_euclidean):
    pauli_algebra = Algebra(
        config=p_euclidean(3),
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = pauli_algebra.basis_vectors(expr=True)
    theta = pauli_algebra.scalar(np.pi / 3).named("theta", latex=r"\theta")
    plane = (e1 ^ e2).named("B")
    rotor = exp(-theta * plane / 2).named("R")
    return (rotor,)


@app.cell
def _(rotor, to_spinor_column):
    pauli_ket = to_spinor_column(rotor)
    pauli_bra = pauli_ket.H
    pauli_overlap = pauli_bra @ pauli_ket
    return pauli_bra, pauli_ket, pauli_overlap


@app.cell
def _(gm, pauli_bra, pauli_ket, pauli_overlap, rotor):
    _overlap_magnitude = abs(pauli_overlap)

    gm.md(rt"""
    GA rotor:

    {rotor}

    Ket:

    {pauli_ket:block}

    Bra from the Hermitian adjoint `.H`:

    {pauli_bra:block}

    A normalized rotor gives $|\langle R|R\rangle| =
    {_overlap_magnitude:.6f}$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Matrix multiplication understands ket/bra kinds:

    - `ket.H` is a bra;
    - `bra @ ket` is a complex scalar;
    - `operator @ ket` is another ket; and
    - `ket @ bra` is an operator.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Faithful reconstruction

    `from_spinor_column(ket)` infers the algebra and basis from the wrapper.
    The inverse solves the real linear system for the even-blade coefficients
    and rejects a column outside the image instead of silently projecting it.
    """)
    return


@app.cell
def _(from_spinor_column, np, pauli_ket, rotor):
    recovered_rotor = from_spinor_column(pauli_ket)
    pauli_spinor_roundtrip = np.allclose(
        recovered_rotor.data,
        rotor.data,
        atol=1e-10,
    )
    return pauli_spinor_roundtrip, recovered_rotor


@app.cell
def _(gm, pauli_spinor_roundtrip, recovered_rotor):
    gm.md(rt"""
    Recovered even multivector:

    {recovered_rotor}

    Coefficients round-trip: `{pauli_spinor_roundtrip!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A regular Dirac-Hestenes spinor in spacetime algebra

    For mostly-minus $Cl(1,3)$, the same API returns a four-component complex
    column in the Dirac basis. `to_basis("weyl")` changes the column basis;
    the inverse conversion accounts for that basis metadata.

    A general **regular** Dirac-Hestenes spinor has the polar form

    $$
    \psi=\sqrt{\rho}\,e^{I\beta/2}R,
    \qquad
    R\widetilde R=1,
    $$

    where $\rho>0$ is the density, $R$ is a Lorentz rotor, $I$ is the STA
    pseudoscalar, and $\beta$ is the Yvon--Takabayasi angle. A rotor-only
    example fixes the special values $\rho=1$ and $\beta=0$ and therefore
    hides two genuine spinor degrees of freedom.

    The pseudoscalar factor $e^{I\beta/2}$ is not generally a Lorentz rotor:
    reverse leaves $I$ unchanged, so

    $$
    \psi\widetilde\psi=\rho e^{I\beta},
    $$

    rather than $1$. It is also distinct from ordinary complex phase in the
    selected column convention, where multiplication by the scalar imaginary
    $i$ is represented geometrically by right multiplication by
    $\gamma_2\gamma_1$.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, exp, np, p_sta):
    spacetime_algebra = Algebra(
        config=p_sta("mostly-minus"),
        display=DisplayPolicy(content="full"),
    )
    gamma0, gamma1, gamma2, gamma3 = spacetime_algebra.basis_vectors(expr=True)
    spacetime_pseudoscalar = spacetime_algebra.pseudoscalar(expr=True).named(
        "I",
        latex=r"I",
    )
    density = spacetime_algebra.scalar(1.7).named("rho", latex=r"\rho")
    sqrt_density = spacetime_algebra.scalar(np.sqrt(1.7)).named(
        "sqrt_rho",
        latex=r"\sqrt{\rho}",
    )
    beta = spacetime_algebra.scalar(0.6).named("beta", latex=r"\beta")
    lorentz_rotor = exp(-0.2 * (gamma0 * gamma1)).named("R")
    yt_phase = exp(beta * spacetime_pseudoscalar / 2).named(
        "Q_beta",
        latex=r"Q_\beta",
    )
    regular_spinor = (sqrt_density * yt_phase * lorentz_rotor).named(
        "Psi",
        latex=r"\Psi",
    )
    return (
        beta,
        density,
        gamma0,
        lorentz_rotor,
        regular_spinor,
        spacetime_pseudoscalar,
        sqrt_density,
        yt_phase,
    )


@app.cell
def _(
    beta,
    density,
    exp,
    gamma0,
    lorentz_rotor,
    np,
    regular_spinor,
    reverse,
    spacetime_pseudoscalar,
):
    polar_product = (regular_spinor * reverse(regular_spinor)).named(
        "polar_product",
        latex=r"\Psi\widetilde{\Psi}",
    )
    expected_polar_product = density * exp(beta * spacetime_pseudoscalar)
    polar_decomposition_ok = np.allclose(
        polar_product.data,
        expected_polar_product.data,
        atol=1e-10,
    )
    dirac_current = (regular_spinor * gamma0 * reverse(regular_spinor)).named(
        "J",
    )
    expected_dirac_current = (
        density * lorentz_rotor * gamma0 * reverse(lorentz_rotor)
    )
    current_independent_of_beta = np.allclose(
        dirac_current.data,
        expected_dirac_current.data,
        atol=1e-10,
    )
    return (
        current_independent_of_beta,
        dirac_current,
        polar_decomposition_ok,
        polar_product,
    )


@app.cell
def _(
    beta,
    current_independent_of_beta,
    density,
    dirac_current,
    gm,
    lorentz_rotor,
    polar_decomposition_ok,
    polar_product,
    regular_spinor,
    sqrt_density,
    yt_phase,
):
    gm.md(rt"""
    Density and Yvon--Takabayasi angle:

    {density}

    {beta}

    Polar factors:

    {sqrt_density}

    {yt_phase}

    {lorentz_rotor}

    General regular spinor:

    {regular_spinor}

    Its scalar--pseudoscalar polar product:

    {polar_product}

    Its Dirac current, $J=\Psi\gamma_0\widetilde{{\Psi}}$:

    {dirac_current}

    | Check | Result |
    |---|---|
    | $\Psi\widetilde{{\Psi}}=\rho e^{{I\beta}}$ | `{polar_decomposition_ok!s}` |
    | $J=\rho R\gamma_0\widetilde{{R}}$ is independent of $\beta$ | `{current_independent_of_beta!s}` |
    """)
    return


@app.cell
def _(regular_spinor, to_spinor_column):
    dirac_ket = to_spinor_column(regular_spinor)
    weyl_ket = dirac_ket.to_basis("weyl")
    return dirac_ket, weyl_ket


@app.cell
def _(dirac_ket, gm, weyl_ket):
    gm.md(rt"""
    Dirac basis:

    {dirac_ket:block}

    Weyl basis:

    {weyl_ket:block}
    """)
    return


@app.cell
def _(from_spinor_column, np, regular_spinor, weyl_ket):
    recovered_from_weyl = from_spinor_column(weyl_ket)
    weyl_roundtrip = np.allclose(
        recovered_from_weyl.data,
        regular_spinor.data,
        atol=1e-10,
    )
    return (weyl_roundtrip,)


@app.cell
def _(gamma0, gm, to_matrix, weyl_ket):
    gamma0_weyl = to_matrix(gamma0, mode="dirac").to_basis("weyl")
    transformed_weyl_ket = gamma0_weyl @ weyl_ket
    _result_kind = transformed_weyl_ket.kind

    gm.md(rt"""
    Applying the Weyl-basis $\gamma^0$ matrix preserves the column kind:
    `{_result_kind!s}`.

    {transformed_weyl_ket:block}
    """)
    return


@app.cell
def _(gm, weyl_roundtrip):
    gm.md(rt"""
    The Weyl-basis column reconstructs the original even multivector:
    `{weyl_roundtrip!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Preconditions are part of the API

    - The input multivector must contain only even grades.
    - The actual reference-column map must have full real rank on the even
      subalgebra; dimension counting alone is insufficient.
    - The supplied column must lie in the image of that map.
    - `Cl(3,0)` and mostly-minus `Cl(1,3)` are supported faithful examples;
      unsupported signatures raise rather than returning a lossy inverse.

    `to_spinor_matrix` and `from_spinor_matrix` remain compatibility aliases;
    the canonical names are `to_spinor_column` and `from_spinor_column`.
    """)
    return


if __name__ == "__main__":
    app.run()
