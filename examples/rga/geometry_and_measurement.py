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
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, p_rga, transwedge_antiproduct
    from galaga.rga import RigidModel

    return Algebra, DisplayPolicy, RigidModel, gm, mo, p_rga, transwedge_antiproduct


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # RGA geometry, measurement, and constraints

    Eric Lengyel's point-based Rigid Geometric Algebra uses one
    $\mathrm{Cl}(3,0,1)$ algebra for projective incidence and Euclidean
    measurement. `RigidModel` is a validated semantic layer: the generic
    `Algebra` still owns products and expression trees, while the model knows
    which basis vector is projective and which formulas mean distance,
    projection, support, and geometric validity.

    Points are vectors, lines are bivectors, and planes are trivectors.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, RigidModel, p_rga):
    algebra = Algebra(config=p_rga(), display=DisplayPolicy(content="full"))
    rga = RigidModel(algebra, expr=True)
    e1, e2, e3 = rga.euclidean_basis_vectors()
    e4 = rga.projective
    return e1, e2, e3, e4, rga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Homogeneous points and incidence

    A finite point is $P=x e_1+y e_2+z e_3+w e_4$. Its Euclidean coordinates
    are divided by $w$. The exterior product joins points, while the antiwedge
    meets planes; these incidence operations do not need the metric.
    """)
    return


@app.cell
def _(gm, rga):
    P = rga.point((3, 4, 0)).named("P")
    Q = rga.point((1, 0, 0)).named("Q")
    L = (P ^ Q).named("L")
    _coordinates = rga.coordinates(P)

    gm.md(rt"""
    {P}

    {Q}

    {L}

    Coordinates recovered from $P$: `{_coordinates!s}`.
    """)
    return L, P, Q


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bulk, weight, and geometric norms

    RGA carries two complementary magnitudes. The metric inner product gives
    the scalar **bulk norm**, and the antidot product gives the antiscalar
    **weight norm**. Their sum is Lengyel's geometric norm:

    $$
    \lVert X\rVert
      =\lVert X\rVert_{\text{●}}+\lVert X\rVert_{\text{○}}.
    $$

    For a finite point, bulk is the ordinary distance from the coordinate
    origin and weight records its homogeneous scale.
    """)
    return


@app.cell
def _(P, gm, rga):
    _bulk = rga.bulk_norm(P)
    _weight = rga.weight_norm(P)
    _geometric = rga.geometric_norm(P)

    gm.md(rt"""
    {_bulk}

    {_weight}

    {_geometric}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Homogeneous distance and angle

    The result retains both its Euclidean measurement and projective weight.
    For unit-weight points, the scalar part of `homogeneous_distance` is the
    ordinary Euclidean distance. For unit-weight planes, the scalar part of
    `homogeneous_angle` is the absolute cosine, while its antiscalar part keeps
    the homogeneous weight.
    """)
    return


@app.cell
def _(P, Q, gm, rga):
    plane_x = rga.algebra.blade("e423", expr=True).named(r"\pi_x")
    plane_y = rga.algebra.blade("e431", expr=True).named(r"\pi_y")
    _distance = rga.homogeneous_distance(P, Q)
    _parallel_angle = rga.homogeneous_angle(plane_x, plane_x)
    _right_angle = rga.homogeneous_angle(plane_x, plane_y)

    gm.md(rt"""
    {_distance}

    {_parallel_angle}

    {_right_angle}
    """)
    return (plane_x,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Projection and support

    `orthogonal_projection(P, plane)` keeps the object in homogeneous RGA
    form. `support(L)` returns the point on a line nearest the Euclidean
    coordinate origin; `antisupport` is its dual plane-side construction.
    """)
    return


@app.cell
def _(L, P, gm, plane_x, rga):
    _projected = rga.orthogonal_projection(P, plane_x)
    _support = rga.support(L)
    _antisupport = rga.antisupport(L)
    _projected_coordinates = rga.coordinates(_projected)

    gm.md(rt"""
    {_projected}

    Projected coordinates: `{_projected_coordinates!s}`.

    {_support}

    {_antisupport}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transwedge and the line constraint

    Eric's order-one transwedge antiproduct extracts the algebraic candidate
    for the common perpendicular of two skew lines. In general that candidate
    need not satisfy the Plücker line constraint. This is a geometric
    constraint, not a failure of the product.

    `orthogonalize_line` keeps the candidate direction and projects its moment
    perpendicular to that direction. The corrected bivector then satisfies
    $\mathbf v\mathbin{\bullet}\mathbf m=0$ and represents a genuine line.
    """)
    return


@app.cell
def _(gm, rga, transwedge_antiproduct):
    _a0 = rga.point((-1, -1, -1))
    _a1 = rga.point((0, 0, 0))
    _b0 = rga.point((0, 2, 1))
    _b1 = rga.point((2, 0, 2))
    line_a = (_a0 ^ _a1).named("A")
    line_b = (_b0 ^ _b1).named("B")

    raw_perpendicular = transwedge_antiproduct(line_a, line_b, 1).named("F")
    corrected_perpendicular = rga.orthogonalize_line(raw_perpendicular).named(
        r"\widehat F",
        latex=r"\widehat{F}",
    )
    _raw_constraint = rga.line_constraint(raw_perpendicular)
    _corrected_constraint = rga.line_constraint(corrected_perpendicular)
    _support_coordinates = rga.coordinates(rga.support(corrected_perpendicular))

    gm.md(rt"""
    {line_a}

    {line_b}

    {raw_perpendicular}

    Raw line constraint: `{_raw_constraint:.6g}`.

    {corrected_perpendicular}

    Corrected line constraint: `{_corrected_constraint:.6g}`.
    Its support point is `{_support_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The correction step is intentionally explicit. It prevents code from
    silently treating every algebraically generated bivector as a geometric
    line, and gives notebooks a useful place to teach the distinction between
    the ambient exterior algebra and the constrained projective model.
    """)
    return


if __name__ == "__main__":
    app.run()
