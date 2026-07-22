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
    from galaga import Algebra, DisplayPolicy, outer_product, p_cga
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, mo, outer_product, p_cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Direct CGA objects and semantic operations

    **Claim:** points, lines, circles, planes, and spheres do not need wrapper
    classes or special constructors. They are homogeneous multivectors built
    with the ordinary outer product. `ConformalModel` adds only the semantic
    operations that depend on the distinguished $e_o/e_\infty$ frame.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    algebra = Algebra(
        config=p_cga(spatial_dim=3),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra)
    e1, e2, e3 = cga.euclidean_basis_vectors(expr=True)
    eo, einf = algebra.blades("origin", "infinity", expr=True)

    origin_point = cga.up((0.0, 0.0, 0.0), expr=True).named("O")
    x_point = cga.up((1.0, 0.0, 0.0), expr=True).named("X")
    y_point = cga.up((0.0, 1.0, 0.0), expr=True).named("Y")
    z_point = cga.up((0.0, 0.0, 1.0), expr=True).named("Z")
    return (
        algebra,
        cga,
        e1,
        e2,
        e3,
        einf,
        eo,
        origin_point,
        x_point,
        y_point,
        z_point,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Direct representations

    The construction pattern is deliberately uniform:

    | Object | Direct representation |
    |---|---|
    | round point | $A$ |
    | flat point | $A\wedge e_\infty$ |
    | dipole | $A\wedge B$ |
    | line | $A\wedge B\wedge e_\infty$ |
    | circle | $A\wedge B\wedge C$ |
    | plane | $A\wedge B\wedge C\wedge e_\infty$ |
    | sphere | $A\wedge B\wedge C\wedge D$ |
    """)
    return


@app.cell
def _(einf, gm, origin_point, outer_product, x_point, y_point, z_point):
    flat_point = outer_product(origin_point, einf).named("F")
    dipole = outer_product(origin_point, x_point).named("D")
    line = outer_product(origin_point, x_point, einf).named("L")
    circle = outer_product(origin_point, x_point, y_point).named("C")
    plane = outer_product(origin_point, x_point, y_point, einf).named("P")
    sphere = outer_product(origin_point, x_point, y_point, z_point).named("S")

    gm.md(rt"""
    {flat_point}

    {dipole}

    {line}

    {circle}

    {plane}

    {sphere}
    """)
    return circle, dipole, flat_point, line, plane, sphere


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Semantic vocabulary

    The long method names are the primary API. The short forms are exact
    aliases of the abbreviations used by the CGA wiki:

    | Primary | Wiki form | Meaning |
    |---|---|---|
    | `attitude` | `att` | purely directional object |
    | `carrier` | `car` | containing flat geometry |
    | `cocarrier` | `ccr` | carrier of the antidual |
    | `center` | `cen` | round center and signed radius |
    | `container` | `con` | smallest containing sphere |
    | `partner` | `par` | same center, opposite signed radius |
    | `projection` | `project` | projection onto a higher-grade object |
    """)
    return


@app.cell
def _(cga, circle, dipole, gm, line):
    _line_attitude = cga.att(line).named("A_L", latex=r"A_L")
    _dipole_carrier = cga.car(dipole).named("K_D", latex=r"K_D")
    _circle_carrier = cga.carrier(circle).named("K_C", latex=r"K_C")
    _circle_cocarrier = cga.ccr(circle).named("K_C_star", latex=r"K_C^\star")
    _circle_center = cga.cen(circle).named("C_o", latex=r"C_o")
    _circle_container = cga.con(circle).named("S_C", latex=r"S_C")
    _circle_partner = cga.par(circle).named("C_prime", latex=r"C^{\prime}")

    gm.md(rt"""
    {_line_attitude}

    {_dipole_carrier}

    {_circle_carrier}

    {_circle_cocarrier}

    {_circle_center}

    {_circle_container}

    {_circle_partner}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dual and antidual

    The wiki's dual is the metric Hodge dual; its antidual uses the
    antimetric map. These are explicit model methods because “dual” is not one
    globally interchangeable convention in geometric algebra.
    """)
    return


@app.cell
def _(cga, circle, gm):
    _dual_circle = cga.dual(circle).named("C_dual", latex=r"C^\ast")
    _antidual_circle = cga.antidual(circle).named(
        "C_antidual", latex=r"C^\star"
    )

    gm.md(rt"""
    {_dual_circle}

    {_antidual_circle}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Expansion and projection

    Projecting a point two units above the $xy$ plane produces a round point
    centred on the plane. Its signed squared radius is the squared projection
    distance, so the result retains more information than a Euclidean foot
    point alone.
    """)
    return


@app.cell
def _(cga, gm, plane):
    _source = cga.up((0.25, 0.5, 2.0), expr=True).named("Q")
    _expanded = cga.expansion(_source, plane).named("E")
    _projected = cga.project(_source, plane).named("Q_P", latex=r"Q_P")
    _projected_center = cga.coordinates(_projected)
    _projected_radius_squared = float(cga.radius_squared(_projected))

    gm.md(rt"""
    {_source}

    {_expanded}

    {_projected}

    Projected center: `{_projected_center!s}`.
    Signed squared radius: `{_projected_radius_squared:.6g}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The semantic methods compose existing operations; they do not introduce
    new value types. That keeps direct and dual representations, generic
    products, expression provenance, and rendering in one algebra.
    """)
    return


if __name__ == "__main__":
    app.run()
