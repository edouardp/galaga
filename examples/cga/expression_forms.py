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
    from galaga import Algebra, DisplayPolicy, outer_product, p_lengyel_cga
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, mo, outer_product, p_lengyel_cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CGA expression forms

    A conformal helper has two useful stories to tell:

    - the **operator story** preserves the geometry vocabulary, such as
      $\operatorname{up}(x)$, $\operatorname{car}(C)$, or
      $\operatorname{cen}(C)$;
    - the **expanded story** exposes the generic geometric-algebra operations
      and native null-basis elements from which that helper is built.

    `expr` and `expression_form` control separate concerns. `expr=True` asks
    the model to retain expression provenance. `expression_form="operator"`
    or `"expanded"` selects the shape of that provenance. The numeric value is
    identical in either case.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_lengyel_cga):
    algebra = Algebra(
        config=p_lengyel_cga(),
        display=DisplayPolicy(content="full"),
    )

    # Operator provenance is the default because it normally communicates the
    # geometric intent most clearly.
    cga = ConformalModel(algebra, expr=True)

    # A model view shares the same Algebra and changes only the provenance form.
    expanded_cga = cga.with_expression_form("expanded")
    return algebra, cga, expanded_cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One point, two explanations

    The default model shows that the point was produced by the conformal
    `up` map. The derived model exposes the actual native-null embedding. Both
    results contain exactly the same coefficients.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm):
    point_operator = cga.up((1.0, 2.0, 3.0)).named(
        "P_operator",
        latex=r"P_{\mathrm{operator}}",
    )
    point_expanded = expanded_cga.up((1.0, 2.0, 3.0)).named(
        "P_expanded",
        latex=r"P_{\mathrm{expanded}}",
    )
    _same_point = point_operator == point_expanded

    gm.md(rt"""
    {point_operator}

    {point_expanded}

    Same numeric multivector: `{_same_point}`.
    """)
    return point_expanded, point_operator


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Override one call

    The model setting is only a default. Either direction can be overridden
    on a single helper call without mutating either model view. This is useful
    when a lesson normally uses compact notation but pauses to derive one
    construction.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm):
    _expanded_override = cga.up(
        (-1.0, 0.5, 2.0),
        expression_form="expanded",
    ).named("Q_expanded", latex=r"Q_{\mathrm{expanded\ override}}")
    _operator_override = expanded_cga.up(
        (-1.0, 0.5, 2.0),
        expression_form="operator",
    ).named("Q_operator", latex=r"Q_{\mathrm{operator\ override}}")

    gm.md(rt"""
    {_expanded_override}

    {_operator_override}

    Model defaults after the calls: `cga.expression_form =
    "{cga.expression_form}"`, `expanded_cga.expression_form =
    "{expanded_cga.expression_form}"`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Round points retain their own operation

    `up(x)` is the zero-radius convenience operation. `round_point(x,
    radius_squared=...)` retains both arguments in compact form, or shows the
    radius term in the expanded embedding.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm):
    _round_operator = cga.round_point(
        (1.0, 2.0, 3.0),
        radius_squared=4.0,
    ).named("A_operator", latex=r"A_{\mathrm{operator}}")
    _round_expanded = expanded_cga.round_point(
        (1.0, 2.0, 3.0),
        radius_squared=4.0,
    ).named("A_expanded", latex=r"A_{\mathrm{expanded}}")

    gm.md(rt"""
    {_round_operator}

    {_round_expanded}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Semantic geometry or algebraic definition

    The choice applies throughout the CGA vocabulary. Here the compact form
    foregrounds Lengyel's carrier and center operations; the expanded form
    shows their definitions in terms of antiduals, outer products, and
    regressive products.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm, outer_product):
    _a = cga.up((0.0, 0.0, 0.0))
    _b = cga.up((1.0, 0.0, 0.0))
    _d = cga.up((0.0, 1.0, 0.0))
    circle = outer_product(_a, _b, _d).named("C")

    _carrier_operator = cga.carrier(circle).named(
        "K_operator",
        latex=r"K_{\mathrm{operator}}",
    )
    _carrier_expanded = expanded_cga.carrier(circle).named(
        "K_expanded",
        latex=r"K_{\mathrm{expanded}}",
    )
    _center_operator = cga.center(circle).named(
        "M_operator",
        latex=r"M_{\mathrm{operator}}",
    )
    _center_expanded = expanded_cga.center(circle).named(
        "M_expanded",
        latex=r"M_{\mathrm{expanded}}",
    )

    gm.md(rt"""
    {circle}

    {_carrier_operator}

    {_carrier_expanded}

    {_center_operator}

    {_center_expanded}
    """)
    return circle


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Expanded point measurements

    Homogeneous weight, normalization, and signed squared radius also expose
    their formulas. Scaling the round point makes the normalization visible
    instead of allowing the renderer to simplify division by one.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm):
    scaled_round_point = (
        3.0 * cga.round_point((1.0, 2.0, 3.0), radius_squared=4.0)
    ).named("Q")
    _weight = expanded_cga.weight(scaled_round_point).named("w")
    _homogeneous = expanded_cga.homogenize(scaled_round_point).named(
        "Q_h",
        latex=r"Q_h",
    )
    _radius_squared = expanded_cga.radius_squared(scaled_round_point).named(
        "rho_squared",
        latex=r"\rho^2",
    )

    gm.md(rt"""
    {scaled_round_point}

    {_weight}

    {_homogeneous}

    {_radius_squared}
    """)
    return scaled_round_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where expansion deliberately stops

    `down()` selects Euclidean vector coefficients from a normalized conformal
    vector. That projection is model logic rather than a generic GA identity,
    so both settings retain an honest atomic `down(Q)` operation. Expanded
    provenance only expands helpers that have a lower-level algebraic formula.
    """)
    return


@app.cell
def _(cga, expanded_cga, gm, scaled_round_point):
    _down_operator = cga.down(scaled_round_point).named(
        "x_operator",
        latex=r"x_{\mathrm{operator}}",
    )
    _down_expanded = expanded_cga.down(scaled_round_point).named(
        "x_expanded",
        latex=r"x_{\mathrm{expanded}}",
    )

    gm.md(rt"""
    {_down_operator}

    {_down_expanded}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Provenance can still be disabled

    `expression_form` has no effect when provenance is absent. A model can
    default to `expr=False`, or a factory such as `up()` can override an
    expression-aware model with `expr=False`. Full display then shows only the
    name and eager value.
    """)
    return


@app.cell
def _(ConformalModel, algebra, cga, gm):
    plain_cga = ConformalModel(algebra)
    _plain_default = plain_cga.up((1.0, 2.0, 3.0)).named(
        "P_plain",
        latex=r"P_{\mathrm{plain\ model}}",
    )
    _plain_override = cga.up((1.0, 2.0, 3.0), expr=False).named(
        "P_override",
        latex=r"P_{\mathrm{expr=False}}",
    )

    gm.md(rt"""
    {_plain_default}

    {_plain_override}
    """)
    return


if __name__ == "__main__":
    app.run()
