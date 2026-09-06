import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr, from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import Algebra, geometric_product

    return (
        Algebra,
        MatrixRepr,
        from_matrix,
        geometric_product,
        gm,
        mo,
        np,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A basis-independent compact-matrix workflow

    The previous notebook developed the two-dimensional algebra. Here we use
    a four-dimensional mixed-signature metric to show a practical workflow:

    1. construct a Gram matrix from a known basis transform;
    2. ask Galaga for explicit compact matrices in that native basis;
    3. verify the Clifford relations and product law numerically; and
    4. round-trip a full multivector.

    The calculations use public APIs only. The transform is shown to explain
    where a dense metric can come from; callers need supply only $G$.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, np):
    orthogonal_metric = np.diag([1.0, 1.0, -1.0, -1.0])
    basis_transform = np.array(
        [
            [1.0, 0.20, 0.10, -0.10],
            [0.3, 1.10, -0.20, 0.20],
            [-0.1, 0.25, 0.90, 0.15],
            [0.2, -0.10, 0.30, 1.20],
        ]
    )
    dense_gram = basis_transform @ orthogonal_metric @ basis_transform.T
    orthogonal_metric_matrix = MatrixRepr(orthogonal_metric).name(latex=r"\eta")
    basis_transform_matrix = MatrixRepr(basis_transform).name(latex=r"S")
    dense_gram_matrix = MatrixRepr(dense_gram).name(latex=r"G")
    dense_algebra = Algebra(gram=dense_gram)
    d1, d2, d3, d4 = dense_algebra.basis_vectors(expr=True)
    d1 = d1.named("d1", latex=r"d_1")
    d2 = d2.named("d2", latex=r"d_2")
    d3 = d3.named("d3", latex=r"d_3")
    d4 = d4.named("d4", latex=r"d_4")
    return (
        basis_transform,
        basis_transform_matrix,
        d1,
        d2,
        d3,
        d4,
        dense_algebra,
        dense_gram,
        dense_gram_matrix,
        orthogonal_metric,
        orthogonal_metric_matrix,
    )


@app.cell
def _(
    basis_transform,
    basis_transform_matrix,
    dense_algebra,
    dense_gram,
    dense_gram_matrix,
    gm,
    np,
    orthogonal_metric,
    orthogonal_metric_matrix,
):
    _factorization_holds = np.allclose(
        dense_gram,
        basis_transform @ orthogonal_metric @ basis_transform.T,
    )
    _inertia = dense_algebra.inertia
    gm.md(rt"""
    ## From an orthogonal frame to a native frame

    Starting from the normalized orthogonal metric

    {orthogonal_metric_matrix:block}

    choose a nonsingular basis transform

    {basis_transform_matrix:block}

    and define $G=S\eta S^{{\mathsf T}}$:

    {dense_gram_matrix:block}

    The factorization check is `{_factorization_holds!s}` and Galaga computes
    inertia `{_inertia!s}` directly from $G$.
    """)
    return


@app.cell
def _(d1, d2, d3, d4, dense_gram, np, to_matrix):
    dense_gammas = tuple(np.asarray(to_matrix(vector, mode="compact")) for vector in (d1, d2, d3, d4))
    _identity = np.eye(dense_gammas[0].shape[0], dtype=complex)
    _relation_errors = []
    for _row, _left in enumerate(dense_gammas):
        for _column, _right in enumerate(dense_gammas):
            _expected = 2.0 * dense_gram[_row, _column] * _identity
            _relation_errors.append(np.linalg.norm(_left @ _right + _right @ _left - _expected))
    maximum_relation_error = max(_relation_errors)
    return dense_gammas, maximum_relation_error


@app.cell
def _(dense_gammas, gm, maximum_relation_error):
    _generator_shape = dense_gammas[0].shape
    gm.md(rt"""
    ## Compact native generators

    Galaga constructs four native generators of shape `{_generator_shape!s}`.
    Across all sixteen pairs, the largest residual in

    $$
    \Gamma_i\Gamma_j+\Gamma_j\Gamma_i=2G_{{ij}}I
    $$

    is `{maximum_relation_error:.3e}`.

    This check is stronger than checking only the diagonal squares: the
    off-diagonal entries verify that the oblique geometry survived the matrix
    conversion.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A full multivector calculation

    The representation acts on all grades at once. We will multiply two mixed
    multivectors, compare geometric product with matrix multiplication, and
    recover all sixteen exterior-basis coefficients from the compact result.
    """)
    return


@app.cell
def _(
    d1,
    d2,
    d3,
    d4,
    dense_algebra,
    from_matrix,
    geometric_product,
    np,
    to_matrix,
):
    dense_left = (1 + 0.5 * d1 - d2 + 0.25 * (d1 ^ d3) + 0.1 * (d2 ^ d3 ^ d4)).named("a")
    dense_right = (-0.5 + d3 + 0.75 * d4 - 0.2 * (d1 ^ d2)).named("b")
    dense_product = geometric_product(dense_left, dense_right)

    represented_product = to_matrix(dense_product, mode="compact")
    multiplied_representations = to_matrix(dense_left, mode="compact") @ to_matrix(
        dense_right,
        mode="compact",
    )
    dense_product_holds = np.allclose(represented_product, multiplied_representations)

    coefficient_sample = dense_algebra.multivector(np.linspace(-1.0, 1.0, dense_algebra.dim), name="x", expr=True)
    compact_sample = to_matrix(coefficient_sample, mode="compact")
    automatic_sample = to_matrix(coefficient_sample)
    recovered_coefficients = from_matrix(compact_sample)
    dense_roundtrip_holds = np.allclose(recovered_coefficients.data, coefficient_sample.data)
    return (
        automatic_sample,
        coefficient_sample,
        compact_sample,
        dense_product,
        dense_product_holds,
        dense_roundtrip_holds,
        recovered_coefficients,
    )


@app.cell
def _(
    automatic_sample,
    coefficient_sample,
    compact_sample,
    dense_product,
    dense_product_holds,
    dense_roundtrip_holds,
    gm,
    recovered_coefficients,
):
    _automatic_mode = automatic_sample.mode
    _automatic_shape = automatic_sample.shape
    _compact_shape = compact_sample.shape
    gm.md(rt"""
    GA product:

    {dense_product}

    Its compact matrix agrees with multiplying the two input matrices:
    `{dense_product_holds!s}`.

    The test value {coefficient_sample:block} uses all grades. Automatic conversion
    chooses `{_automatic_mode!s}` with shape `{_automatic_shape!s}`, while
    explicit compact conversion has shape `{_compact_shape!s}`:

    {compact_sample:block}

    The compact inverse returns {recovered_coefficients:block}
    All sixteen native coefficients round-trip: `{dense_roundtrip_holds!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Practical guidance

    - Build `Algebra(gram=G)` in the basis where your model's coefficients
      have meaning. There is no need to diagonalize $G$ yourself.
    - Use explicit `mode="compact"` when matrix size matters and the metric is
      nondegenerate.
    - Verify equations involving geometry in the native algebra first, then
      use matrices as a representation of those computed values.
    - Keep the `MatrixRepr` wrapper if you will call `from_matrix`; it retains
      the source algebra and mode.
    - Automatic conversion intentionally remains left-regular for a general
      Gram matrix in this release step.
    """)
    return


if __name__ == "__main__":
    app.run()
