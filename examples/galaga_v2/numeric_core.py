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
    ):
        _path = str(_source)
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga.core import Algebra as NumericAlgebra
    from galaga.core import geometric_product as numeric_geometric_product
    from galaga.facade import Algebra, DisplayPolicy, geometric_product

    return (
        Algebra,
        DisplayPolicy,
        NumericAlgebra,
        geometric_product,
        gm,
        mo,
        np,
        numeric_geometric_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The numeric core beneath Galaga 2

    **Claim:** `galaga.core` is the small, presentation-free geometric algebra
    engine. `galaga.facade` composes naming, provenance, configuration, and
    rendering around that same engine without changing its arithmetic.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Use the core when coefficients are the complete problem

    The core knows Gram matrices, basis masks, grades, and numeric operations.
    It deliberately knows nothing about presets, semantic names, expression
    trees, notation, or LaTeX.
    """)
    return


@app.cell
def _(NumericAlgebra, np, numeric_geometric_product):
    numeric_algebra = NumericAlgebra(
        gram=np.array(
            [
                [1.0, 0.5],
                [0.5, -1.0],
            ]
        )
    )
    numeric_e1, numeric_e2 = numeric_algebra.basis_vectors()
    numeric_symmetric_product = numeric_geometric_product(
        numeric_e1,
        numeric_e2,
    ) + numeric_geometric_product(numeric_e2, numeric_e1)
    return numeric_algebra, numeric_e1, numeric_e2, numeric_symmetric_product


@app.cell
def _(gm, numeric_algebra, numeric_symmetric_product):
    _gram = numeric_algebra.gram
    _expected_scalar = 2 * _gram[0, 1]
    _core_result = repr(numeric_symmetric_product)

    gm.md(rt"""
    For any basis, the geometric product satisfies
    $e_1e_2 + e_2e_1 = 2G_{{12}}$.

    ```text
    Gram matrix:
    {_gram!s}

    Core result:
    {_core_result!s}

    Expected scalar coefficient:
    {_expected_scalar!s}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Add the facade without rebuilding the metric

    `Algebra.from_numeric(...)` creates a facade view over an existing core
    algebra. It is useful at integration boundaries where numeric ownership is
    already established. The default presentation may be replaced explicitly.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, geometric_product, numeric_algebra):
    facade_algebra = Algebra.from_numeric(numeric_algebra).with_display(
        DisplayPolicy(content="full")
    )
    facade_e1, facade_e2 = facade_algebra.basis_vectors(expr=True)
    facade_symmetric_product = (
        geometric_product(facade_e1, facade_e2)
        + geometric_product(facade_e2, facade_e1)
    ).named("S")
    same_numeric_owner = facade_algebra.numeric is numeric_algebra
    return facade_algebra, facade_symmetric_product, same_numeric_owner


@app.cell
def _(facade_symmetric_product, gm, same_numeric_owner):
    gm.md(rt"""
    The facade wraps the exact same core algebra: `{same_numeric_owner!s}`.

    It can now retain and render the calculation:

    {facade_symmetric_product}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Public linear actions replace private multiplication tables

    `left_action(a)` materializes the linear map $x \mapsto ax$. Matrix and
    other integration packages can consume this public operation without
    reaching into a product-table implementation detail.
    """)
    return


@app.cell
def _(facade_algebra, geometric_product, gm, np):
    _left, _right = facade_algebra.basis_vectors(expr=True)
    _matrix_result = facade_algebra.left_action(_left) @ _right.data
    _product_result = geometric_product(_left, _right).data
    _actions_agree = np.allclose(_matrix_result, _product_result)

    gm.md(rt"""
    The left-action matrix and direct geometric product agree:
    `{_actions_agree!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Boundary rule

    - Import from `galaga.core` for a minimal numeric engine or for building
      integrations that should not depend on presentation.
    - Import from `galaga.facade` for user-facing work: presets, configured
      blades, names, optional expressions, rendering, and scoped notation.
    - Cross the boundary through `.numeric` or `Algebra.from_numeric(...)`,
      not through private coefficient-product tables.
    """)
    return


if __name__ == "__main__":
    app.run()
