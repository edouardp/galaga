import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr, from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import Algebra, geometric_product, outer_product

    return (
        Algebra,
        MatrixRepr,
        from_matrix,
        geometric_product,
        gm,
        mo,
        np,
        outer_product,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Compact matrices in an oblique basis

    A Clifford algebra does not require an orthonormal basis. Its vector
    products are controlled by a symmetric Gram matrix $G$, where

    $$
    e_i e_j + e_j e_i = 2G_{ij}.
    $$

    This notebook builds a compact representation directly from a dense Gram
    matrix. Along the way, it separates two ideas that coincide only in an
    orthogonal basis: the Clifford product $e_i e_j$ and the exterior blade
    $e_i\wedge e_j$.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, np):
    gram_2d = np.array([[2.0, 0.5], [0.5, -1.0]])
    gram_matrix = MatrixRepr(gram_2d).name(latex=r"G")
    oblique = Algebra(gram=gram_2d)
    e1_oblique, e2_oblique = oblique.basis_vectors(expr=True)
    return e1_oblique, e2_oblique, gram_2d, gram_matrix, oblique


@app.cell
def _(e1_oblique, e2_oblique, gm, gram_2d, gram_matrix, oblique):
    _off_diagonal_inner_product = gram_2d[0, 1]
    _inertia = oblique.inertia
    gm.md(rt"""
    We choose the Gram matrix

    {gram_matrix:block}

    whose inertia is `{_inertia!s}`. The basis vectors {e1_oblique} and
    {e2_oblique} are not orthogonal because
    $e_1\mathbin{{\cdot}}e_2={_off_diagonal_inner_product}$.

    The metric is nevertheless nondegenerate, so a compact representation is
    available when requested explicitly.
    """)
    return


@app.cell
def _(e1_oblique, e2_oblique, gram_2d, np, to_matrix):
    gamma_1 = to_matrix(e1_oblique, mode="compact")
    gamma_2 = to_matrix(e2_oblique, mode="compact")
    compact_identity = np.eye(gamma_1.shape[0], dtype=complex)
    clifford_relations_hold = all(
        (
            np.allclose(gamma_1 @ gamma_1, gram_2d[0, 0] * compact_identity),
            np.allclose(gamma_2 @ gamma_2, gram_2d[1, 1] * compact_identity),
            np.allclose(gamma_1 @ gamma_2 + gamma_2 @ gamma_1, 2.0 * gram_2d[0, 1] * compact_identity),
        )
    )
    return clifford_relations_hold, gamma_1, gamma_2


@app.cell
def _(clifford_relations_hold, gamma_1, gamma_2, gm):
    gm.md(rt"""
    ## Vector generators

    Explicit `mode="compact"` produces the native vector matrices
    $\Gamma_1=\rho(e_1)$ and $\Gamma_2=\rho(e_2)$:

    {gamma_1:block}

    {gamma_2:block}

    Their squares and anticommutator reproduce every entry of $G$:
    `{clifford_relations_hold!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why the bivector is not an ordered matrix product

    In an orthogonal basis, $e_1e_2=e_1\wedge e_2$. Here the inner product is
    nonzero, so

    $$
    e_1e_2=G_{12}+e_1\wedge e_2.
    $$

    A correct representation must therefore construct the exterior blade by
    antisymmetrization:

    $$
    \rho(e_1\wedge e_2)
      =\tfrac12(\Gamma_1\Gamma_2-\Gamma_2\Gamma_1).
    $$
    """)
    return


@app.cell
def _(
    e1_oblique,
    e2_oblique,
    gamma_1,
    gamma_2,
    gram_2d,
    np,
    outer_product,
    to_matrix,
):
    exterior_bivector = outer_product(e1_oblique, e2_oblique).named("B")
    exterior_matrix = to_matrix(exterior_bivector, mode="compact")
    ordered_product_matrix = gamma_1 @ gamma_2
    metric_part_matrix = gram_2d[0, 1] * np.eye(gamma_1.shape[0], dtype=complex)
    decomposition_holds = np.allclose(
        ordered_product_matrix,
        exterior_matrix + metric_part_matrix,
    )
    return (
        decomposition_holds,
        exterior_bivector,
        exterior_matrix,
        ordered_product_matrix,
    )


@app.cell
def _(
    decomposition_holds,
    exterior_bivector,
    exterior_matrix,
    gm,
    ordered_product_matrix,
):
    gm.md(rt"""
    The exterior blade {exterior_bivector:block} maps to

    {exterior_matrix:block}

    whereas the ordered product $\Gamma_1\Gamma_2$ is

    {ordered_product_matrix:block}

    The latter equals $G_{{12}}I+\rho(e_1\wedge e_2)$:
    `{decomposition_holds!s}`. This is the central reason the basis change must
    be lifted through exterior powers instead of multiplying transformed
    generators blindly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Products and round-trips

    Once every exterior blade is represented correctly, the map is an algebra
    homomorphism: geometric products become ordinary matrix products. For an
    injective compact representation, the wrapper also contains enough
    metadata for `from_matrix` to recover native-basis coefficients.
    """)
    return


@app.cell
def _(
    e1_oblique,
    e2_oblique,
    from_matrix,
    geometric_product,
    np,
    oblique,
    to_matrix,
):
    left_oblique = (1 + 2 * e1_oblique - e2_oblique).named("a")
    right_oblique = (e1_oblique + 0.25 * e2_oblique).named("b")
    ga_product = geometric_product(left_oblique, right_oblique)
    represented_ga_product = to_matrix(ga_product, mode="compact")
    matrix_product = to_matrix(left_oblique, mode="compact") @ to_matrix(
        right_oblique,
        mode="compact",
    )
    homomorphism_holds = np.allclose(represented_ga_product, matrix_product)

    sample_value = oblique.multivector([1.0, -2.0, 0.75, 3.0], name="x", expr=True)
    explicit_compact = to_matrix(sample_value, mode="compact")
    automatic_regular = to_matrix(sample_value)
    recovered_sample = from_matrix(explicit_compact)
    roundtrip_holds = np.allclose(recovered_sample.data, sample_value.data)
    return (
        automatic_regular,
        explicit_compact,
        homomorphism_holds,
        recovered_sample,
        roundtrip_holds,
        sample_value,
    )


@app.cell
def _(
    automatic_regular,
    explicit_compact,
    gm,
    homomorphism_holds,
    recovered_sample,
    roundtrip_holds,
    sample_value,
):
    _automatic_mode = automatic_regular.mode
    _automatic_shape = automatic_regular.shape
    _compact_shape = explicit_compact.shape
    gm.md(rt"""
    The product law holds: `{homomorphism_holds!s}`.

    For {sample_value}, automatic mode remains `{_automatic_mode!s}` with
    shape `{_automatic_shape!s}`. Explicit compact mode has shape
    `{_compact_shape!s}`:

    {explicit_compact:block}

    It recovers {recovered_sample}, preserving native coefficients:
    `{roundtrip_holds!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaway

    - The supplied Gram matrix—not a presumed diagonal signature—defines the
      vector relations.
    - Native exterior blades require antisymmetrization or, equivalently, the
      exterior-power lift of the basis transform.
    - Request `mode="compact"` explicitly for a nondegenerate general Gram
      matrix. Automatic dispatch remains conservatively left-regular.
    - A compact inverse is available only when the selected representation is
      injective; Galaga checks that before reconstructing coefficients.
    """)
    return


if __name__ == "__main__":
    app.run()
