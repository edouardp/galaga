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
    import math

    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        BladeConvention,
        BladeLabel,
        DisplayPolicy,
        Name,
        Notation,
        antireverse,
        exp,
        geometric_antiproduct,
        geometric_product,
        metric_inner_product,
        outer_product,
        p_cga,
        sandwich,
    )
    from galaga.cga import ConformalModel

    return (
        Algebra,
        BladeConvention,
        BladeLabel,
        ConformalModel,
        DisplayPolicy,
        Name,
        Notation,
        antireverse,
        exp,
        geometric_antiproduct,
        geometric_product,
        gm,
        math,
        metric_inner_product,
        mo,
        outer_product,
        p_cga,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Native-null CGA with Eric Lengyel's notation

    **Claim:** the metric model, blade convention, and operation notation are
    independent presentation choices. This notebook keeps Galaga's native
    $(e_1,e_2,e_3,e_o,e_\infty)$ conformal frame while selecting Eric
    Lengyel's geometric-product, antiproduct, and metric-inner-product
    symbols.

    The pseudoscalar is also displayed as Lengyel's antiunit $\text{𝟙}$.
    This is a label change, not a numeric change.
    """)
    return


@app.cell
def _(
    Algebra,
    BladeConvention,
    BladeLabel,
    ConformalModel,
    DisplayPolicy,
    Name,
    Notation,
    p_cga,
):
    _preset = p_cga(spatial_dim=3, frame="null")
    _base_blades = _preset.build().presentation.blades
    _labels = list(_base_blades.labels)
    _labels[-1] = BladeLabel(
        Name("I", "𝟙", r"\text{𝟙}"),
        _base_blades.labels[-1].ref,
    )
    _lengyel_blades = BladeConvention(
        _base_blades.dimension,
        _labels,
        aliases=_base_blades.aliases,
        roles=_base_blades.roles,
    )

    algebra = Algebra(
        config=_preset,
        blades=_lengyel_blades,
        notation=Notation.lengyel(),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra)
    e1, e2, e3 = cga.euclidean_basis_vectors(expr=True)
    eo, einf = algebra.blades("origin", "infinity", expr=True)
    antiunit = algebra.pseudoscalar(expr=True)
    return algebra, antiunit, cga, e1, e2, e3, einf, eo


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
def _(
    e1,
    e2,
    e3,
    geometric_product,
    gm,
    metric_inner_product,
    outer_product,
):
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
    return u, v


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
def _(
    antiunit,
    antireverse,
    cga,
    e2,
    e3,
    einf,
    geometric_antiproduct,
    gm,
):
    source_point = cga.up((1.0, 2.0, 3.0), expr=True).named("P")
    anti_translator = (antiunit + 0.5 * (e2 ^ e3 ^ einf)).named("T")
    translated_by_antiproduct = geometric_antiproduct(
        geometric_antiproduct(anti_translator, source_point),
        antireverse(anti_translator),
    ).named("P_a", latex=r"P_a^{\prime}")
    _anti_coordinates = cga.coordinates(translated_by_antiproduct)

    gm.md(rt"""
    {anti_translator}

    {translated_by_antiproduct}

    Translated coordinates: `{_anti_coordinates!s}`.
    """)
    return anti_translator, source_point, translated_by_antiproduct


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
def _(cga, e1, einf, exp, gm, sandwich, source_point, translated_by_antiproduct):
    translator = exp(-0.5 * e1 * einf).named("U")
    translated_by_product = sandwich(translator, source_point).named(
        "P_g", latex=r"P_g^{\prime}"
    )
    _product_coordinates = cga.coordinates(translated_by_product)
    _forms_agree = translated_by_product == translated_by_antiproduct

    gm.md(rt"""
    {translator}

    {translated_by_product}

    Translated coordinates: `{_product_coordinates!s}`.
    The product and antiproduct forms agree numerically: `{_forms_agree!s}`.
    """)
    return translated_by_product, translator


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
    _test_point = cga.up((1.0, 0.0, 0.0), expr=True).named("Q")

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
