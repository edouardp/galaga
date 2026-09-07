import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        Name,
        Notation,
        RenderRule,
        doran_lasenby_inner,
        geometric_product,
        hestenes_inner,
        metric_inner_product,
        p_euclidean,
        reverse,
        scalar_product,
        transwedge,
        transwedge_antiproduct,
        unit,
    )

    return (
        Algebra,
        DisplayPolicy,
        Name,
        Notation,
        RenderRule,
        doran_lasenby_inner,
        geometric_product,
        gm,
        hestenes_inner,
        metric_inner_product,
        mo,
        p_euclidean,
        reverse,
        scalar_product,
        transwedge,
        transwedge_antiproduct,
        unit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Custom functional notation

    **Claim:** an operation's stable long name and its visible functional name
    are separate. We can make `hestenes_inner(a, b)` display as
    `hestenes_ip(a, b)` and `metric_inner_product(a, b)` display as
    `metric_ip(a, b)` without renaming either operation, changing its
    expression node, or changing how it evaluates.

    This lets a lesson use compact notation while the underlying API remains
    explicit about which inner product was selected.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Extend the built-in short functional notation

    `Notation.functional(short=True)` supplies Galaga's standard compact
    functional names. `with_rule(...)` returns a new immutable notation with
    one rule replaced.

    ```python
    custom_notation = (
        Notation.functional(short=True)
        .with_rule(
            "hestenes_inner",
            RenderRule("function", symbol="hestenes_ip"),
        )
        .with_rule(
            "doran_lasenby_inner",
            RenderRule("function", symbol="doran_lasenby_ip"),
        )
        .with_rule(
            "metric_inner_product",
            RenderRule("function", symbol="metric_ip"),
        )
        .with_rule(
            "scalar_product",
            RenderRule("function", symbol="scalar_ip"),
        )
        .with_rule(
            "geometric_product",
            RenderRule("function", symbol="mul"),
        )
    )
    ```

    The keys are stable operation IDs. The symbols are presentation choices.
    """)
    return


@app.cell
def _(Notation, RenderRule):
    custom_notation = (
        Notation.functional(short=True)
        .with_rule(
            "hestenes_inner",
            RenderRule("function", symbol="hestenes_ip"),
        )
        .with_rule(
            "doran_lasenby_inner",
            RenderRule("function", symbol="doran_lasenby_ip"),
        )
        .with_rule(
            "metric_inner_product",
            RenderRule("function", symbol="metric_ip"),
        )
        .with_rule(
            "scalar_product",
            RenderRule("function", symbol="scalar_ip"),
        )
        .with_rule(
            "geometric_product",
            RenderRule("function", symbol="mul"),
        )
    )
    return (custom_notation,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Install it while constructing the algebra

    `notation=` overrides only the notation component supplied by the preset.
    The preset still owns the metric, blade convention, local names, and
    display order. `display=` is another independent presentation component.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, custom_notation, p_euclidean):
    custom_algebra = Algebra(
        config=p_euclidean(3),
        notation=custom_notation,
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = custom_algebra.basis_vectors(expr=True)
    e12, e23 = custom_algebra.blades(e1^e2, e2^e3, expr=True)
    a = (e1 + 2 * e2).named("a")
    b = (3 * e1 - e2).named("b")
    return a, b, custom_algebra, e12, e23


@app.cell
def _(
    a,
    b,
    doran_lasenby_inner,
    e12,
    e23,
    geometric_product,
    hestenes_inner,
    metric_inner_product,
    scalar_product,
    transwedge,
    transwedge_antiproduct,
):
    product = geometric_product(a, b).named("M")
    hestenes_result = hestenes_inner(a, b).named("h")
    doran_lasenby_result = doran_lasenby_inner(a, b).named("d")
    metric_result = metric_inner_product(a, b).named("m")
    scalar_result = scalar_product(a, b).named("s")
    transwedge_term = transwedge(a, b, 1).named("T")
    antitranswedge_term = transwedge_antiproduct(e12, e23, 1).named("A")
    return (
        antitranswedge_term,
        doran_lasenby_result,
        hestenes_result,
        metric_result,
        product,
        scalar_result,
        transwedge_term,
    )


@app.cell
def _(
    antitranswedge_term,
    doran_lasenby_result,
    gm,
    hestenes_result,
    metric_result,
    product,
    scalar_result,
    transwedge_term,
):
    gm.md(rt"""
    The algebra's default presentation now uses our overrides together with
    the remaining built-in short forms:

    | Stable operation | Rendering |
    |---|---|
    | `geometric_product` | {product:expr} |
    | `hestenes_inner` | {hestenes_result:expr} |
    | `doran_lasenby_inner` | {doran_lasenby_result:expr} |
    | `metric_inner_product` | {metric_result:expr} |
    | `scalar_product` | {scalar_result:expr} |
    | `transwedge` | {transwedge_term:expr} |
    | `transwedge_antiproduct` | {antitranswedge_term:expr} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `_ip` suffix is only a vocabulary chosen by this lesson. Each name
    remains unambiguous because its rule names one stable operation. This does
    not restore an unqualified public `inner_product()` dispatcher.

    The built-in short functional notation contributes `tw` and `antitw` for
    the current canonical operations `transwedge` and
    `transwedge_antiproduct`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Compare long, built-in short, and custom rendering

    A per-render `notation=` argument has higher priority than the algebra's
    configured notation. It gives us three views of the same stored expression.
    """)
    return


@app.cell
def _(Notation, gm, hestenes_result):
    custom_ascii = hestenes_result.display("expr/ascii")
    built_in_short_ascii = hestenes_result.display(
        "expr/ascii",
        notation=Notation.functional(short=True),
    )
    long_ascii = hestenes_result.display(
        "expr/ascii",
        notation=Notation.functional(),
    )

    gm.md(rt"""
    | Presentation | Same expression |
    |---|---|
    | Long functional | `{long_ascii!s}` |
    | Built-in short functional | `{built_in_short_ascii!s}` |
    | This algebra's custom functional | `{custom_ascii!s}` |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Change notation temporarily

    A presentation can also be installed for one context. The context is
    thread- and async-safe because `use_presentation(...)` uses a `ContextVar`.
    The original custom notation is restored automatically.
    """)
    return


@app.cell
def _(Notation, custom_algebra, hestenes_result):
    long_presentation = custom_algebra.presentation.with_notation(
        Notation.functional()
    )
    before_scope = hestenes_result.display("expr/ascii")
    with custom_algebra.use_presentation(long_presentation):
        inside_scope = hestenes_result.display("expr/ascii")
    after_scope = hestenes_result.display("expr/ascii")
    return after_scope, before_scope, inside_scope


@app.cell
def _(after_scope, before_scope, gm, inside_scope):
    gm.md(rt"""
    Before: `{before_scope!s}`

    Inside long-functional scope: `{inside_scope!s}`

    After restoration: `{after_scope!s}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Python import aliases are independent

    If concise source code is also desirable, ordinary Python aliasing is
    enough:

    ```python
    from galaga import hestenes_inner as hestenes_ip

    result = hestenes_ip(a, b)
    ```

    That local import alias does not affect rendering. Conversely, the custom
    rendering rule does not add a new public `galaga.facade.hestenes_ip`
    function. Both routes still create a `hestenes_inner` expression node.
    """)
    return


@app.cell
def _(Name, Notation, RenderRule, custom_algebra, e12, gm, reverse, unit):
    # Derive the bivector square from the actual two-vector Gram minor.
    _B = e12.unnamed().named("B")
    _G = custom_algebra.gram
    _expected_square = _G[0, 1] ** 2 - _G[0, 0] * _G[1, 1]
    assert float(_B * _B) == _expected_square
    assert reverse(_B) == -_B
    _normalized = unit(_B).named(Name.from_latex(r"\hat{B}"))
    _fraction_notation = Notation.default().with_rule(
        "unit", RenderRule("unit_fraction")
    )
    _fraction_latex = _normalized.display("full/latex", notation=_fraction_notation)
    _dagger_latex = reverse(_B).display("expr/latex", notation=Notation.hestenes())
    assert _normalized.numeric == _B.numeric
    assert _normalized.expr.operation_id == "unit"
    assert _dagger_latex == r"B^{\dagger}"

    gm.md(rt"""
    ## Show the definition without changing the operation

    A hat name and a hat expression can look identical. The optional
    `RenderRule("unit_fraction")` makes normalization a separate teaching step:

    $$
    {_fraction_latex!s}
    $$

    `Name.from_latex` derives the three spellings of our hat name explicitly.
    The stored operation is still `unit`, and its numeric result was computed
    before rendering. The fraction is only a display of $B/\lVert B\rVert$.
    Its denominator means Galaga's metric norm
    $\sqrt{{|\langle B\widetilde{{B}}\rangle_0|}}$, not an assumption that
    every metric is positive definite.

    Use `target="latex"` in `with_rule` to change only that output target.
    With a non-default normalization tolerance, the renderer uses a function
    call to keep that control visible. Zero-norm inputs still fail eagerly.

    A different preset changes reverse to a dagger:

    $$
    \widetilde{{B}} = {_dagger_latex!s} = -B.
    $$

    Here dagger means **reverse**, not a separately defined Hermitian adjoint.
    The Hestenes preset now makes the same choice in Unicode and LaTeX.
    """)
    return


if __name__ == "__main__":
    app.run()
