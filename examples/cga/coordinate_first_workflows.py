import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, outer_product, p_cga
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, mo, outer_product, p_cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Coordinate-first CGA workflows

    `ConformalModel.up()` and `round_point()` accept ordinary positional
    coordinates, so Cartesian data can enter a conformal workflow directly:

    ```python
    point = cga.up(1.0, 2.0, 3.0)
    round_point = cga.round_point(1.0, 2.0, 3.0, radius_squared=4.0)
    ```

    Coordinate sequences and Euclidean multivectors remain available for
    array-oriented and algebra-oriented code.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    algebra = Algebra(
        config=p_cga(spatial_dim=3),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra, expr=True)
    return cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Three input forms, one conformal point

    Positional coordinates are a convenience at the geometry boundary. The
    model still constructs the same Euclidean vector and evaluates the same
    native-null embedding

    $$
    \operatorname{up}(x)
      = e_o + x - \frac{x^2}{2(e_o\mathbin{\cdot}e_\infty)}e_\infty.
    $$
    """)
    return


@app.cell
def _(cga, gm):
    positional_point = cga.up(1.0, 2.0, 3.0).named(
        "P_positional",
        latex=r"P_{\mathrm{positional}}",
    )
    _sequence_point = cga.up((1.0, 2.0, 3.0))
    _euclidean_position = cga.euclidean_vector((1.0, 2.0, 3.0)).named("x")
    vector_point = cga.up(_euclidean_position).named(
        "P_vector",
        latex=r"P_{\mathrm{vector}}",
    )
    _all_equal = positional_point == _sequence_point == vector_point

    gm.md(t"""
    {positional_point}

    {_euclidean_position}

    {vector_point}

    All three input forms produce the same multivector: `{_all_equal}`.
    """)
    return positional_point, vector_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A circle from Cartesian coordinates

    Three embedded points determine a direct circle. The construction remains
    the ordinary outer product; `ConformalModel` then supplies geometric
    queries such as `center()` and `radius()`.
    """)
    return


@app.cell
def _(cga, gm, outer_product):
    _circle_p1 = cga.up(1.0, 0.0, 0.0).named("P_1")
    _circle_p2 = cga.up(0.0, 1.0, 0.0).named("P_2")
    _circle_p3 = cga.up(-1.0, 0.0, 0.0).named("P_3")
    circle = outer_product(_circle_p1, _circle_p2, _circle_p3).named("C")
    circle_center = cga.center(circle).named("K")
    _circle_center_coordinates = cga.coordinates(circle_center)
    _circle_radius = float(cga.radius(circle))

    gm.md(t"""
    {circle}

    {circle_center}

    Euclidean center: `{_circle_center_coordinates!s}`.

    Radius: `{_circle_radius:.6g}`.
    """)
    return circle, circle_center


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A finite-radius round point

    `up()` is the zero-radius case. `round_point()` also encodes a signed
    squared radius while using the same coordinate grammar.
    """)
    return


@app.cell
def _(cga, gm):
    finite_round_point = cga.round_point(
        1.0,
        -2.0,
        0.5,
        radius_squared=4.0,
    ).named("A")
    _round_center = cga.coordinates(finite_round_point)
    _round_radius_squared = float(cga.radius_squared(finite_round_point))

    gm.md(t"""
    {finite_round_point}

    Center: `{_round_center!s}`.

    Signed squared radius: `{_round_radius_squared:.6g}`.
    """)
    return finite_round_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Project a point onto a plane

    The plane $z=0$ is the direct join of three points and $e_\infty$.
    Projection returns a round point whose center is the Euclidean foot and
    whose signed squared radius records the squared distance to the plane.
    """)
    return


@app.cell
def _(cga, gm, outer_product):
    _plane_origin = cga.up(0.0, 0.0, 0.0)
    _plane_x = cga.up(1.0, 0.0, 0.0)
    _plane_y = cga.up(0.0, 1.0, 0.0)
    plane = outer_product(
        _plane_origin,
        _plane_x,
        _plane_y,
        cga.infinity,
    ).named("Pi", latex=r"\Pi")
    query_point = cga.up(0.25, 0.5, 2.0).named("Q")
    projected_point = cga.projection(query_point, plane).named(
        "Q_projected",
        latex=r"Q_{\Pi}",
    )
    _nearest_coordinates = cga.coordinates(projected_point)
    _distance_squared = float(cga.radius_squared(projected_point))

    gm.md(t"""
    {plane}

    {query_point}

    {projected_point}

    Projected center: `{_nearest_coordinates!s}`.

    Squared distance to the plane: `{_distance_squared:.6g}`.
    """)
    return plane, projected_point, query_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The new positional spelling changes only the input boundary. The resulting
    values remain ordinary Galaga multivectors, and construction, projection,
    measurement, and extraction continue to use the validated native-null
    model and generic geometric-algebra products.
    """)
    return


if __name__ == "__main__":
    app.run()
