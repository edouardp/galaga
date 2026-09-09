import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr, from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        AlgebraConfig,
        AlgebraDefinition,
        DisplayPolicy,
        exp,
        p_cga,
        reverse,
        sandwich,
        scalar_product,
        squared,
    )
    from galaga.cga import ConformalModel

    return (
        Algebra,
        AlgebraConfig,
        AlgebraDefinition,
        ConformalModel,
        DisplayPolicy,
        MatrixRepr,
        exp,
        from_matrix,
        gm,
        mo,
        np,
        p_cga,
        reverse,
        sandwich,
        scalar_product,
        squared,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Conformal geometric algebra from its Gram matrix

    Three-dimensional CGA uses five basis vectors in the native order

    $$
    (e_1,e_2,e_3,e_o,e_\infty).
    $$

    The Euclidean vectors have unit positive square. The conformal origin and
    infinity are individually null but have mutual product $-1$. Those facts
    belong in one symmetric Gram matrix; they do not require hidden basis
    vectors with squares $+1$ and $-1$.

    We will construct that matrix explicitly, attach Galaga's CGA semantic
    roles, and represent points and translations with explicit compact
    matrices.
    """)
    return


@app.cell
def _(
    Algebra,
    AlgebraConfig,
    AlgebraDefinition,
    ConformalModel,
    DisplayPolicy,
    MatrixRepr,
    np,
    p_cga,
):
    spatial_dimension = 3
    null_pair_scale = -1.0
    cga_gram = np.zeros((spatial_dimension + 2, spatial_dimension + 2))
    cga_gram[:spatial_dimension, :spatial_dimension] = np.eye(spatial_dimension)
    cga_gram[spatial_dimension, spatial_dimension + 1] = null_pair_scale
    cga_gram[spatial_dimension + 1, spatial_dimension] = null_pair_scale

    cga_template = p_cga(spatial_dimension, frame="null", null_pair=null_pair_scale).build()
    cga_definition = AlgebraDefinition(cga_gram, id="cga-3d-explicit-gram")
    cga_config = AlgebraConfig(
        definition=cga_definition,
        presentation=cga_template.presentation,
        model=cga_template.model,
    )
    cga_algebra = Algebra(
        config=cga_config,
        display=DisplayPolicy(content="full"),
    )
    cga_model = ConformalModel(cga_algebra, expr=True)
    cga_gram_matrix = MatrixRepr(cga_gram).name(latex=r"G_{\mathrm{CGA}}")
    return cga_algebra, cga_gram_matrix, cga_model


@app.cell
def _(cga_algebra, cga_gram_matrix, cga_model, gm, scalar_product, squared):
    _origin_square = float(squared(cga_model.origin))
    _infinity_square = float(squared(cga_model.infinity))
    _null_pair_product = float(scalar_product(cga_model.origin, cga_model.infinity))
    _inertia = cga_algebra.inertia
    gm.md(rt"""
    ## The metric model

    {cga_gram_matrix:block}

    Galaga derives inertia `{_inertia!s}` from this matrix. The two null-vector
    identities and their nonzero mutual product are computed by the algebra:

    $$
    e_o^2={_origin_square:g},\qquad
    e_\infty^2={_infinity_square:g},\qquad
    e_o\mathbin{{\cdot}}e_\infty={_null_pair_product:g}.
    $$

    Therefore the form is nondegenerate even though two diagonal entries are
    zero. This is exactly the case that a diagonal-signature check misses.
    """)
    return


@app.cell
def _(cga_gram_matrix):
    cga_gram_matrix  # noqa: B018 - Marimo displays the cell's final expression.
    return


@app.cell
def _(cga_model, np, scalar_product, squared, to_matrix):
    origin_matrix = to_matrix(cga_model.origin, mode="compact")
    infinity_matrix = to_matrix(cga_model.infinity, mode="compact")
    _identity = np.eye(origin_matrix.shape[0], dtype=complex)
    anticommutator_scale = 2.0 * float(scalar_product(cga_model.origin, cga_model.infinity))
    null_generator_relations_hold = all(
        (
            np.allclose(origin_matrix @ origin_matrix, float(squared(cga_model.origin)) * _identity),
            np.allclose(infinity_matrix @ infinity_matrix, float(squared(cga_model.infinity)) * _identity),
            np.allclose(
                origin_matrix @ infinity_matrix + infinity_matrix @ origin_matrix, anticommutator_scale * _identity
            ),
        )
    )
    return (
        anticommutator_scale,
        infinity_matrix,
        null_generator_relations_hold,
        origin_matrix,
    )


@app.cell
def _(
    anticommutator_scale,
    gm,
    infinity_matrix,
    null_generator_relations_hold,
    origin_matrix,
):
    gm.md(rt"""
    ## Compact matrices for the null pair

    The explicit compact images are only $4\times4$:

    {origin_matrix:block}

    {infinity_matrix:block}

    Their matrix squares vanish and their anticommutator is ${anticommutator_scale:g}I$: `{null_generator_relations_hold!s}`.

    These are the matrix form of the three
    Gram entries we just computed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A conformal point

    For the normalization $e_o\mathbin{\cdot}e_\infty=-1$, an ordinary point
    at Euclidean position $x$ is

    $$
    P(x)=e_o+x+\tfrac12x^2e_\infty.
    $$

    It is a null vector. Consequently its compact matrix also squares to zero.
    This is a useful bridge between the geometric statement and ordinary
    linear algebra.
    """)
    return


@app.cell
def _(cga_model, from_matrix, np, squared, to_matrix):
    euclidean_position = cga_model.euclidean_vector((1.0, 2.0, -0.5)).named("x")
    conformal_point = cga_model.up(euclidean_position).named("P")
    point_matrix = to_matrix(conformal_point, mode="compact")
    point_is_null = np.isclose(float(squared(conformal_point)), 0.0)
    point_matrix_is_nilpotent = np.allclose(point_matrix @ point_matrix, 0.0)
    recovered_point = from_matrix(point_matrix)
    point_roundtrip_holds = np.allclose(recovered_point.data, conformal_point.data)
    return (
        conformal_point,
        euclidean_position,
        point_is_null,
        point_matrix,
        point_matrix_is_nilpotent,
        point_roundtrip_holds,
        recovered_point,
    )


@app.cell
def _(
    conformal_point,
    euclidean_position,
    gm,
    point_is_null,
    point_matrix,
    point_matrix_is_nilpotent,
    point_roundtrip_holds,
    recovered_point,
):
    gm.md(rt"""
    The Euclidean vector {euclidean_position:block} embeds as {conformal_point:block}.

    {point_matrix:block}

    The GA point is null: `{point_is_null!s}`. Its matrix squares to zero:
    `{point_matrix_is_nilpotent!s}`. Inverting the representation recovers
    {recovered_point:block}
    with every native coefficient preserved: `{point_roundtrip_holds!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Translation as a matrix sandwich

    A Euclidean displacement vector $d$ generates the translator

    $$
    T=\exp\left(-\tfrac12 d e_\infty\right).
    $$

    The geometric sandwich $T P \widetilde{T}$ becomes ordinary matrix
    multiplication $\rho(T)\rho(P)\rho(\widetilde{T})$.
    """)
    return


@app.cell
def _(cga_model, conformal_point, exp, np, reverse, sandwich, to_matrix):
    displacement = cga_model.euclidean_vector((0.5, -1.0, 0.25)).named("d")
    translator = exp(-0.5 * displacement * cga_model.infinity).named("T")
    translated_point = sandwich(translator, conformal_point).named("P_prime", latex=r"P'")
    translator_matrix = to_matrix(translator, mode="compact")
    translated_point_matrix = to_matrix(translated_point, mode="compact")
    matrix_sandwich = (
        translator_matrix
        @ to_matrix(conformal_point, mode="compact")
        @ to_matrix(
            reverse(translator),
            mode="compact",
        )
    )
    sandwich_homomorphism_holds = np.allclose(translated_point_matrix, matrix_sandwich)
    translated_coordinates = cga_model.coordinates(translated_point)
    return (
        displacement,
        sandwich_homomorphism_holds,
        translated_coordinates,
        translated_point,
        translator,
        translator_matrix,
    )


@app.cell
def _(
    displacement,
    gm,
    sandwich_homomorphism_holds,
    translated_coordinates,
    translated_point,
    translator,
    translator_matrix,
):
    gm.md(rt"""
    Displacement: {displacement}

    Translator: {translator}

    {translator_matrix:block}

    The matrix sandwich agrees with the geometric sandwich:
    `{sandwich_homomorphism_holds!s}`. The transformed point
    {translated_point} has Euclidean coordinates
    `{translated_coordinates!s}`.
    """)
    return


@app.cell
def _(conformal_point, to_matrix):
    automatic_point_matrix = to_matrix(conformal_point)
    explicit_point_matrix = to_matrix(conformal_point, mode="compact")
    return automatic_point_matrix, explicit_point_matrix


@app.cell
def _(automatic_point_matrix, explicit_point_matrix, gm):
    _automatic_mode = automatic_point_matrix.mode
    _automatic_shape = automatic_point_matrix.shape
    _explicit_shape = explicit_point_matrix.shape
    gm.md(rt"""
    ## Explicit versus automatic mode

    This release step keeps automatic dispatch conservative. The native-null
    Gram matrix automatically selects `{_automatic_mode!s}`, producing shape
    `{_automatic_shape!s}`. Explicit compact mode produces shape
    `{_explicit_shape!s}`.

    A later CGA-specific representation plan can pin recognizable matrix
    entries and make compact mode automatic. The generic congruence used here
    already guarantees the algebraic relations, product law, and injective
    coefficient round-trip.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaway

    - A native null pair is encoded by off-diagonal Gram entries, not by a
      degenerate signature.
    - The $5\times5$ Gram matrix defines a nondegenerate
      $\operatorname{Cl}(4,1)$ algebra.
    - Explicit compact conversion maps its 32 real coefficients injectively
      into $4\times4$ complex matrices.
    - CGA versor sandwiches then become ordinary matrix multiplication without
      changing the native geometric model.
    """)
    return


if __name__ == "__main__":
    app.run()
