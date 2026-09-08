import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        BladeRef,
        DisplayPolicy,
        LocalNamePolicy,
        Notation,
        geometric_product,
        indexed_blade_convention,
        norm,
        p_euclidean,
    )
    from galaga.expression import evaluate

    return (
        Algebra,
        BladeRef,
        DisplayPolicy,
        LocalNamePolicy,
        Notation,
        evaluate,
        geometric_product,
        gm,
        indexed_blade_convention,
        mo,
        norm,
        p_euclidean,
    )


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
    return algebra, product, x


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

    `.display()` and `.latex()` return ordinary Python strings, not live
    display objects. A saved string will not change when a later scope changes
    the policy. Call the multivector's rendering method again for a new output.
    Python `repr(value)` selects ASCII; the rich LaTeX hook selects LaTeX.
    Wrapping in math delimiters does not change the requested content.
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
    return


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
    ## Python bindings are not blade labels

    A display convention answers “how does this blade look?” A
    `LocalNamePolicy` answers “which signed blade does this Python key bind?”
    Changing one does not regenerate the other. `locals()` returns a
    read-only mapping; unpack it explicitly rather than injecting names into
    a Marimo cell's namespace.

    Compute $e_2\wedge e_1$ first, then derive its signed reference. We keep
    compact Python keys even when the blade display uses wedge notation.
    Grade filtering selects references by their masks and preserves signs.
    """)
    return


@app.cell
def _(
    BladeRef,
    LocalNamePolicy,
    algebra,
    evaluate,
    gm,
    indexed_blade_convention,
):
    _e1, _e2 = algebra.basis_vectors()
    _reverse_plane = _e2 ^ _e1
    (_mask,) = (_index for _index, _coefficient in enumerate(_reverse_plane.data) if _coefficient)
    _ref = BladeRef(_mask, int(_reverse_plane.data[_mask]))
    _labels = indexed_blade_convention(algebra.n, prefix="v", style="wedge")
    _display_view = algebra.with_blades(_labels)
    assert list(_display_view.locals()) == list(algebra.locals())
    _policy = LocalNamePolicy(algebra.n, {"x": 1, "y": 2, "plane": _ref})
    _view = _display_view.with_local_names(_policy)
    _bindings = _view.locals(expr=True)
    _x, _y, _plane = (_bindings[_key] for _key in ("x", "y", "plane"))
    assert _plane == _reverse_plane
    assert _view.numeric is algebra.numeric
    _bivectors = LocalNamePolicy(
        algebra.n,
        ((_key, _signed) for _key, _signed in _policy.entries if _signed.mask.bit_count() == 2),
    )
    assert list(_view.with_local_names(_bivectors).locals()) == ["plane"]
    assert _view.with_local_names(_bivectors).locals()["plane"] == _reverse_plane
    _mixed = 2 * _x + 3 * _y + 5 * _plane
    assert _mixed == 2 * _e1 + 3 * _e2 + 5 * _reverse_plane
    assert evaluate(_mixed.expr, algebra=_view, environment=_bindings) == _mixed
    _literal = _view.blade(_plane, expr=True)
    assert evaluate(_literal.expr, algebra=_view) == _plane
    _plane_latex = _plane.latex(content="full")
    _mixed_latex = _mixed.latex(content="full")
    _literal_latex = _literal.latex(content="full")

    gm.md(rt"""
    The Python key `plane` binds the computed reversed exterior product:

    $${_plane_latex!s}.$$

    All coefficients are still in the native basis; the wedge display did
    not change the value:

    $${_mixed_latex!s}.$$

    The symbol `plane` needs an explicit evaluation environment. Literalizing
    the same value with `blade(value, expr=True)` produces a signed blade
    leaf that can be replayed without a symbol environment:

    $${_literal_latex!s}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `LocalNamePolicy.from_convention(...)` takes valid canonical ASCII
    identifiers literally. It excludes scalars, keywords, aliases, and
    roles; it neither sanitizes names nor compacts products. Thus `v1^v2`
    is omitted, while juxtaposed `v1v2` remains `v1v2`. Use a separate
    compact convention or explicit entries when you want a key such as `v12`.

    `locals(expr=False)` omits initial expression leaves, but its values
    still have names: later operations on them record symbolic provenance.
    In STA, preset local `s1` means $\gamma_1\gamma_0$, while native alias
    `g0g1` means $\gamma_0\gamma_1$. Renaming a key must preserve its reference,
    not reinterpret the letters as a product.
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
    saved_expression_latex = default_expression_latex
    _data_before, _expr_before, _hash_before = product.data.copy(), product.expr, hash(product)
    assert type(saved_expression_latex) is str

    with algebra.use_presentation(teaching_presentation):
        functional_expression_latex = product.latex(content="expr")
        assert functional_expression_latex != saved_expression_latex

    restored_expression_latex = product.latex(content="expr")
    assert restored_expression_latex == saved_expression_latex
    assert (product.data == _data_before).all()
    assert product.expr is _expr_before and hash(product) == _hash_before
    return (
        default_expression_latex,
        functional_expression_latex,
        restored_expression_latex,
        teaching_presentation,
    )


@app.cell
def _(
    default_expression_latex,
    functional_expression_latex,
    gm,
    restored_expression_latex,
):
    gm.md(rt"""
    Before the scope:

    $${default_expression_latex}$$

    Inside the scope:

    $${functional_expression_latex}$$

    After automatic restoration:

    $${restored_expression_latex}$$

    Each result above is a saved string. The first one stayed unchanged
    throughout; only a new rendering call observed the functional policy.
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
    return detailed_latex, quiet_latex, stored_coefficients


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
    Applying `.2f` to an already rendered string is an error; applying `.2`
    would merely truncate that string. Neither controls its coefficients.
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
    return


if __name__ == "__main__":
    app.run()
