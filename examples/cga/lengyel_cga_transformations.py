import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium")


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
    import math

    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        antireverse,
        exp,
        geometric_antiproduct,
        geometric_product,
        metric_inner_product,
        outer_product,
        p_lengyel_cga,
        sandwich,
    )
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        antireverse,
        exp,
        geometric_antiproduct,
        geometric_product,
        gm,
        math,
        metric_inner_product,
        mo,
        outer_product,
        p_lengyel_cga,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Native-null CGA with Eric Lengyel's notation

    **Claim:** the metric model, blade convention, and operation notation are
    independent presentation choices. The `p_lengyel_cga()` preset composes
    Galaga's native null Gram matrix with Eric's
    $(\mathbf e_1,\ldots,\mathbf e_5)$ blade convention, basis order, and
    operation symbols. The model roles still identify $\mathbf e_4$ as the
    conformal origin and $\mathbf e_5$ as infinity.

    The pseudoscalar is also displayed as Lengyel's antiunit $\text{𝟙}$.
    This is a label change, not a numeric change.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_lengyel_cga):
    algebra = Algebra(
        config=p_lengyel_cga(),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra, expr=True)
    e1, e2, e3 = cga.euclidean_basis_vectors()
    eo, einf = cga.origin, cga.infinity
    antiunit = algebra.pseudoscalar(expr=True)
    return antiunit, cga, e1, e2, e3, einf, eo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One algebra, a different notation

    In the rendered expressions below:

    - $\mathbin{\text{⟑}}$ is the geometric product;
    - $\mathbin{\text{⟇}}$ is the geometric antiproduct;
    - $\mathbin{\bullet}$ is Lengyel's metric inner product; and
    - $\wedge$ remains the exterior product.

    The Python API deliberately keeps the descriptive operation names. The
    notation policy changes their rendering without changing evaluation.
    """)
    return


@app.cell
def _(e1, e2, e3, geometric_product, gm, metric_inner_product, outer_product):
    u = (e1 + 2 * e2).named("u")
    v = (e2 - e3).named("v")
    _geometric = geometric_product(u, v).named("g")
    _inner = metric_inner_product(u, v).named("s")
    _outer = outer_product(u, v).named("B")

    gm.md(rt"""
    {u}

    {v}

    {_geometric}

    {_inner}

    {_outer}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lengyel's conformal semantic functions

    The CGA model preserves the identity of Eric's named operations instead
    of exposing only their expanded wedge-and-meet implementations. Their
    expression forms therefore use `att`, `car`, `ccr`, `cen`, `con`, and
    `par` under this notation policy.
    """)
    return


@app.cell
def _(cga, gm, outer_product):
    _a = cga.up((0.0, 0.0, 0.0))
    _b = cga.up((1.0, 0.0, 0.0))
    _c = cga.up((0.0, 1.0, 0.0))
    circle = outer_product(_a, _b, _c).named("C")

    _attitude = cga.att(circle)
    _carrier = cga.car(circle)
    _cocarrier = cga.ccr(circle)
    _center = cga.cen(circle)
    _container = cga.con(circle)
    _partner = cga.par(circle)

    gm.md(rt"""
    Starting with the circle:
    {circle:block}

    Then we have the following:

    {_attitude}

    {_carrier}

    {_cocarrier}

    {_center}

    {_container}

    {_partner}
    """)
    return (circle,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Four CGA component families and their norms

    Eric's CGA decomposition records independently whether a term contains
    $e_o$ and whether it contains $e_\infty$. The resulting round-bulk,
    round-weight, flat-bulk, and flat-weight projections render as
    ●, ○, ■, and □ subscripts.

    `weighted_center_norm` and `weighted_radius_norm` are homogeneous
    numerator quantities. Eric's `center_norm` and `radius_norm` divide them
    by `round_weight_norm`, cancelling the arbitrary projective scale.
    `center_distance` and `radius` remain descriptive aliases.
    """)
    return


@app.cell
def _(cga, circle, gm):
    _round_bulk = cga.round_bulk_part(circle)
    _round_weight = cga.round_weight_part(circle)
    _flat_bulk = cga.flat_bulk_part(circle)
    _flat_weight = cga.flat_weight_part(circle)

    _weighted_center_norm = cga.weighted_center_norm(circle)
    _weighted_radius_norm = cga.weighted_radius_norm(circle)
    _round_weight_norm = cga.round_weight_norm(circle)
    _center_norm = cga.center_norm(circle)
    _radius_norm = cga.radius_norm(circle)

    gm.md(rt"""
    {_round_bulk}

    {_round_weight}

    {_flat_bulk}

    {_flat_weight}

    {_weighted_center_norm}

    {_weighted_radius_norm}

    {_round_weight_norm}

    {_center_norm}

    {_radius_norm}
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lengyel's sandwich antiproduct translation

    In three Euclidean dimensions the complementary translation operator for
    a unit displacement in the $e_1$ direction is

    $$
    T=\text{𝟙}+\frac12 e_2\wedge e_3\wedge e_\infty.
    $$

    It acts with the geometric antiproduct and Lengyel's below-tilde
    antireverse:
    $P'=T\mathbin{\text{⟇}}P\mathbin{\text{⟇}}\utilde{T}$.
    """)
    return


@app.cell
def _(antireverse, antiunit, cga, e2, e3, einf, geometric_antiproduct, gm):
    source_point = cga.up([1.0, 2.0, 3.0]).named("P")

    anti_translator = (antiunit + 0.5 * (e2 ^ e3 ^ einf)).named("T")

    translated_by_antiproduct = geometric_antiproduct(
        geometric_antiproduct(anti_translator, source_point),
        antireverse(anti_translator),
    ).named("P'", latex=r"P^{\prime}")

    _anti_coordinates = cga.coordinates(translated_by_antiproduct)

    gm.md(rt"""
    Given the point:
    {source_point:block}

    Then the translation via the antiproduct sandwhich is:

    {anti_translator}

    {translated_by_antiproduct}

    Translated coordinates: `{_anti_coordinates!s}`.
    """)
    return source_point, translated_by_antiproduct


@app.cell
def _(
    antireverse,
    antiunit,
    cga,
    e1,
    geometric_antiproduct,
    gm,
    source_point,
    translated_by_antiproduct,
):
    _translation_plane = cga.dual(e1).named("g")
    _translation_attitude = cga.att(_translation_plane)
    _anti_translator_from_direction = (
        antiunit + 0.5 * _translation_attitude
    ).named("T", latex=r"T")

    _translated_from_direction = geometric_antiproduct(
        geometric_antiproduct(_anti_translator_from_direction, source_point),
        antireverse(_anti_translator_from_direction),
    ).named("P'", latex=r"P^{\prime}")

    _direction_coordinates = cga.coordinates(_translated_from_direction)
    _forms_agree = _translated_from_direction == translated_by_antiproduct

    gm.md(rt"""
    The same generator can be constructed from the translation direction:

    {_translation_plane}

    {_translation_attitude}

    {_anti_translator_from_direction}

    {_translated_from_direction}

    Translated coordinates: `{_direction_coordinates!s}`.
    The explicit and direction-derived forms agree numerically: `{_forms_agree!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The same translation as a geometric-product versor

    The ordinary conformal versor form is
    $U=\exp(-\tfrac12 e_1e_\infty)$ and acts through the generic `sandwich`
    operation. Both forms are evaluated by Galaga primitives and land at the
    same conformal point.
    """)
    return


@app.cell
def _(
    cga,
    e1,
    einf,
    exp,
    gm,
    sandwich,
    source_point,
    translated_by_antiproduct,
):
    translator = exp(-0.5 * e1 * einf).named("U")
    translated_by_product = sandwich(translator, source_point).named(
        "P", latex=r"P^{\prime}"
    )
    _product_coordinates = cga.coordinates(translated_by_product)
    _forms_agree = translated_by_product == translated_by_antiproduct

    gm.md(rt"""
    Given the same point:
    {source_point:block}

    Then the translation by the geometric-product versor is:

    {translator}

    {translated_by_product}

    Translated coordinates: `{_product_coordinates!s}`.
    The product and antiproduct forms agree numerically: `{_forms_agree!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rotation, dilation, and transversion

    CGA transformation constructors would only hide calls to `exp`, so Galaga
    leaves the generators visible. Each operator below uses the same generic
    exponential and sandwich product.
    """)
    return


@app.cell
def _(cga, e1, e2, einf, eo, exp, gm, math, sandwich):
    _test_point = cga.up((1.0, 0.0, 0.0)).named("Q")

    _rotor = exp(-0.25 * math.pi * (e1 ^ e2)).named("R")
    _rotated = sandwich(_rotor, _test_point).named("Q_R", latex=r"Q_R")

    _dilator = exp(0.5 * math.log(2.0) * (eo ^ einf)).named("D")
    _dilated = sandwich(_dilator, _test_point).named("Q_D", latex=r"Q_D")

    _parameter = (0.2 * e1).named("a")
    _transversor = exp(0.5 * _parameter * eo).named("K")
    _transverted = sandwich(_transversor, _test_point).named(
        "Q_K", latex=r"Q_K"
    )

    _rotation_coordinates = cga.coordinates(_rotated)
    _dilation_coordinates = cga.coordinates(_dilated)
    _transversion_coordinates = cga.coordinates(_transverted)

    gm.md(rt"""
    {_rotor}

    {_rotated}

    Rotation: `{_rotation_coordinates!s}`.

    {_dilator}

    {_dilated}

    Dilation: `{_dilation_coordinates!s}`.

    {_transversor}

    {_transverted}

    Transversion: `{_transversion_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This presentation uses Lengyel's notation without adopting a second CGA
    implementation. Switching back to `Notation.default()` changes the
    symbols, while the Gram matrix, coefficients, and semantic model remain
    unchanged.
    """)
    return


if __name__ == "__main__":
    app.run()
