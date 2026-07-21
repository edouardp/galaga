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

    import galaga_marimo as gm
    from galaga.facade import (
        Algebra,
        DisplayPolicy,
        Notation,
        geometric_product,
        norm,
        p_euclidean,
    )

    return Algebra, DisplayPolicy, Notation, geometric_product, gm, mo, norm, p_euclidean


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Changing presentation without changing mathematics

    **Claim:** blade convention, notation, content selection, output target,
    ordering, and numeric formatting can change independently. None of them
    changes coefficients, expression identity, equality, or evaluation.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, geometric_product, p_euclidean):
    algebra = Algebra(
        config=p_euclidean(2),
        display=DisplayPolicy(content="full"),
    )
    e1, e2 = algebra.basis_vectors(expr=True)
    x = (e1 + 2 * e2).named("x")
    y = (3 * e1 - e2).named("y")
    product = geometric_product(x, y).named("M")
    return algebra, e1, e2, product, x, y


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Content is selected at interpolation time

    Galaga-aware t-string format specs select semantic content. They do not
    mean Python numeric coefficient formatting for a multivector.

    - `{value:name}` requests its semantic name.
    - `{value:expr}` requests its provenance expression.
    - `{value:value}` requests its eager numeric value.
    - `{value:full}` requests the complete teaching equality.

    Explicit requests are not deduplicated. Automatic full display removes a
    repeated expression/value only when their emitted rendering is identical.
    """)
    return


@app.cell
def _(gm, product):
    gm.md(rt"""
    | Requested content | Rendering |
    |---|---|
    | name | {product:name} |
    | expression | {product:expr} |
    | value | {product:value} |
    | full | {product:full} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The same separation exists on the Python API:

    ```python
    value.display(content="expr", target="ascii")
    value.display("full/unicode")
    value.latex(content="value")
    ```

    Content and target are independent axes. `ascii`, `unicode`, and `latex`
    are output targets; `name`, `expr`, `value`, and `full` are content.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Immutable persistent views

    `with_presentation(...)` and the component helpers return cheap facade
    views over the exact same numeric algebra. Use these when a presentation
    should persist as an ordinary object rather than only inside one block.
    """)
    return


@app.cell
def _(Notation, algebra, geometric_product, gm):
    functional_view = algebra.with_notation(Notation.functional(short=True))
    _functional_e1, _functional_e2 = functional_view.basis_vectors(expr=True)
    _functional_x = (_functional_e1 + 2 * _functional_e2).named("x")
    _functional_y = (3 * _functional_e1 - _functional_e2).named("y")
    _functional_product = geometric_product(_functional_x, _functional_y).named("M")
    _shares_numeric_algebra = functional_view.numeric is algebra.numeric

    gm.md(rt"""
    The view shares its numeric algebra: `{_shares_numeric_algebra!s}`.

    {_functional_product}
    """)
    return (functional_view,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Available component helpers are `with_blades`, `with_notation`,
    `with_local_names`, `with_display_order`, and `with_display`. The grouped
    `PresentationConfig` also has corresponding `with_*` methods, so one
    concern can be replaced without rebuilding the others.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Scoped presentation with `use_presentation`

    A context manager is useful for teaching, where the same value may be
    shown conventionally in one paragraph and functionally in the next.
    The scope affects future rendering calls only.
    """)
    return


@app.cell
def _(Notation, algebra, product):
    teaching_presentation = algebra.presentation.with_notation(Notation.functional())
    default_expression_latex = product.latex(content="expr")

    with algebra.use_presentation(teaching_presentation):
        functional_expression_latex = product.latex(content="expr")

    restored_expression_latex = product.latex(content="expr")
    return (
        default_expression_latex,
        functional_expression_latex,
        restored_expression_latex,
        teaching_presentation,
    )


@app.cell
def _(default_expression_latex, functional_expression_latex, gm, restored_expression_latex):
    gm.md(rt"""
    Before the scope:

    $${default_expression_latex}$$

    Inside the scope:

    $${functional_expression_latex}$$

    After automatic restoration:

    $${restored_expression_latex}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `use_presentation(...)` uses a `ContextVar` owned by that algebra. Nested
    scopes restore in last-in, first-out order, exceptional exits still
    restore the previous value, and interleaved async tasks or threads do not
    overwrite each other's effective presentation. It is not a process-global
    display mode.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One explicit render override

    For one output, pass the component directly. The resolution order is:

    ```text
    explicit per-render presentation or notation
        > current use_presentation(...) scope
        > algebra's persistent default presentation
    ```
    """)
    return


@app.cell
def _(Notation, algebra, gm, product, teaching_presentation):
    with algebra.use_presentation(teaching_presentation):
        _scoped_ascii = product.display("expr/ascii")
        _explicit_ascii = product.display(
            "expr/ascii",
            notation=Notation.functional(short=True),
        )

    gm.md(rt"""
    Scoped long form: `{_scoped_ascii!s}`

    Explicit short-form override: `{_explicit_ascii!s}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Display policy controls numeric visibility

    `DisplayPolicy` owns default content and target, the zero cutoff used only
    for display, and coefficient precision in significant digits. It never
    rounds or deletes stored coefficients.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy):
    detailed_algebra = Algebra(
        1,
        display=DisplayPolicy(
            content="value",
            zero_tolerance=0,
            coefficient_precision=10,
        ),
    )
    detailed_value = detailed_algebra.multivector((1.23456789, 1.4524e-16))
    detailed_latex = detailed_value.latex()
    quiet_presentation = detailed_algebra.presentation.with_display(
        DisplayPolicy(
            content="value",
            zero_tolerance=1e-12,
            coefficient_precision=6,
        )
    )
    with detailed_algebra.use_presentation(quiet_presentation):
        quiet_latex = detailed_value.latex()
    stored_coefficients = detailed_value.data.copy()
    return detailed_latex, detailed_value, quiet_latex, quiet_presentation, stored_coefficients


@app.cell
def _(detailed_latex, gm, quiet_latex, stored_coefficients):
    gm.md(rt"""
    Detailed rendering:

    $${detailed_latex}$$

    Quiet rendering:

    $${quiet_latex}$$

    The stored array is unchanged:

    ```text
    {stored_coefficients!s}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Numeric Python format specs

    For multivectors, the t-string format namespace is the semantic content
    namespace shown above. To apply a Python numeric format such as `.3f` to a
    scalar multivector, perform the checked conversion explicitly.
    """)
    return


@app.cell
def _(gm, norm, x):
    x_length = norm(x)
    _numeric_length = float(x_length)

    gm.md(rt"""
    Expression-aware scalar result:

    {x_length}

    Python numeric formatting after checked conversion: `{_numeric_length:.3f}`.
    """)
    return (x_length,)


if __name__ == "__main__":
    app.run()
