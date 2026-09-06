import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        geometric_product,
        p_euclidean,
    )

    return (
        Algebra,
        DisplayPolicy,
        from_matrix,
        geometric_product,
        gm,
        mo,
        np,
        p_euclidean,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Matrix representations and round-trips

    **Claim:** a matrix representation is a view of the same Clifford element,
    chosen for a particular linear-algebra task. `galaga_matrix` preserves the
    source algebra and representation mode so supported matrices can return to
    the original multivector without private implementation access.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two general-purpose modes

    | Mode | Shape | Entries | Applicability |
    |---|---:|---|---|
    | `compact` | typically $2^{\lfloor n/2\rfloor}$ square | complex | non-degenerate symmetric Gram matrices |
    | `left-regular` | $2^n \times 2^n$ | real | every symmetric Gram matrix, including degenerate and oblique bases |

    With `mode=None`, `to_matrix` conservatively selects compact mode for a
    normalized orthogonal basis and otherwise selects the faithful
    left-regular representation. General Gram matrices can request compact
    mode explicitly.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_euclidean):
    cl3 = Algebra(
        config=p_euclidean(3),
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = cl3.basis_vectors(expr=True)
    vector = (1 + 2 * e1 - e2).named("a", latex=r"\mathbf{a}")
    return e1, e2, e3, vector


@app.cell
def _(to_matrix, vector):
    compact_matrix = to_matrix(vector, mode="compact")
    regular_matrix = to_matrix(vector, mode="left-regular")
    return compact_matrix, regular_matrix


@app.cell
def _(compact_matrix, gm, regular_matrix, vector):
    _compact_shape = compact_matrix.shape
    _regular_shape = regular_matrix.shape

    gm.md(rt"""
    The same multivector,

    {vector}

    has a compact `{_compact_shape!s}` representation:

    {compact_matrix:block}

    Its left-regular representation has shape `{_regular_shape!s}`. That
    larger matrix is the linear action $x \mapsto \mathbf{{a}}x$ on the full
    coefficient space.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `MatrixRepr` is a NumPy-compatible wrapper. `.mat` exposes its array;
    `.algebra`, `.mode`, `.basis`, and `.kind` preserve representation
    metadata. A named or expression-tracked multivector also gives the matrix
    a package-owned representation expression such as $\rho(a)$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The representation is an algebra homomorphism

    For a supported representation $\rho$,

    $$
    \rho(ab)=\rho(a)\rho(b).
    $$

    Geometric product becomes ordinary matrix multiplication with `@`.
    """)
    return


@app.cell
def _(e1, e2, e3, geometric_product, np, to_matrix):
    left_value = (1 + e1 + 2 * e2).named("a")
    right_value = (e2 - 0.5 * e3).named("b")
    product_in_ga = geometric_product(left_value, right_value)
    represented_product = to_matrix(product_in_ga, mode="compact")
    product_of_matrices = to_matrix(left_value, mode="compact") @ to_matrix(
        right_value,
        mode="compact",
    )
    homomorphism_holds = np.allclose(represented_product, product_of_matrices)
    return (
        homomorphism_holds,
        product_in_ga,
        product_of_matrices,
        represented_product,
    )


@app.cell
def _(
    gm,
    homomorphism_holds,
    product_in_ga,
    product_of_matrices,
    represented_product,
):
    gm.md(rt"""
    GA product:

    {product_in_ga}

    Representation of the GA product:

    {represented_product:block}

    Product of the two representations:

    {product_of_matrices:block}

    The matrices agree: `{homomorphism_holds!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Round-trip from wrapper metadata

    `from_matrix(matrix_repr)` can infer the algebra, mode, and basis from the
    wrapper. Raw arrays cannot carry that information, so they use
    `from_matrix(algebra, array, mode=...)`.
    """)
    return


@app.cell
def _(compact_matrix, from_matrix, np, vector):
    recovered_vector = from_matrix(compact_matrix)
    compact_roundtrip = np.allclose(recovered_vector.data, vector.data)
    return compact_roundtrip, recovered_vector


@app.cell
def _(compact_roundtrip, gm, recovered_vector):
    gm.md(rt"""
    Recovered value:

    {recovered_vector}

    Coefficients round-trip: `{compact_roundtrip!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## General Gram matrices: conservative default, explicit compact mode

    For a nondegenerate oblique metric, explicit compact mode constructs a
    congruent normalized basis and lifts that change of basis to every
    exterior blade. Automatic mode remains left-regular, so existing code does
    not silently change representation size or convention.
    """)
    return


@app.cell
def _(Algebra, from_matrix, np, to_matrix):
    oblique_algebra = Algebra(
        gram=np.array(
            [
                [1.0, 0.25],
                [0.25, -1.0],
            ]
        )
    )
    oblique_value = oblique_algebra.multivector(
        (1.0, 2.0, -1.0, 0.5),
        name="x",
        expr=True,
    )
    oblique_matrix = to_matrix(oblique_value)
    oblique_compact_matrix = to_matrix(oblique_value, mode="compact")
    oblique_recovered = from_matrix(oblique_compact_matrix)
    oblique_roundtrip = np.allclose(oblique_recovered.data, oblique_value.data)
    return oblique_compact_matrix, oblique_matrix, oblique_roundtrip, oblique_value


@app.cell
def _(gm, oblique_compact_matrix, oblique_matrix, oblique_roundtrip, oblique_value):
    _selected_mode = oblique_matrix.mode
    _compact_shape = oblique_compact_matrix.shape
    _regular_shape = oblique_matrix.shape

    gm.md(rt"""
    {oblique_value}

    Automatic mode: `{_selected_mode!s}`, shape `{_regular_shape!s}`.

    Explicit compact shape: `{_compact_shape!s}`.

    {oblique_compact_matrix:block}

    Native exterior-basis coefficients round-trip through the compact matrix:
    `{oblique_roundtrip!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Choosing a mode

    - Prefer explicit `compact` for small matrices over any numerically
      suitable nondegenerate Gram matrix.
    - Use `pauli` or `dirac` when you specifically require those named
      normalized-orthogonal conventions.
    - Prefer `left-regular` for degenerate algebras, automatic conservative
      dispatch, and public left-action integration.
    - Keep the `MatrixRepr` wrapper while metadata, names, expressions, or a
      later inverse conversion matter; use `.mat` as the explicit NumPy escape
      hatch.
    """)
    return


if __name__ == "__main__":
    app.run()
