import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_anywidget.viz as viz
    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, meet, p_cga
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, meet, mo, p_cga, viz


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Circle–circle intersection is one dipole

    Drag either solid center point. The two dotted circles are ordinary direct
    CGA circles. Their meet is one grade-2 dipole: two real intersection
    points, one repeated tangent point, or an imaginary point pair depending
    on the relative positions of the circles.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    circle_algebra = Algebra(
        config=p_cga(spatial_dim=2),
        display=DisplayPolicy(content="full"),
    )
    circle_model = ConformalModel(circle_algebra, expr=True)
    return (circle_model,)


@app.cell
def _(circle_model, viz):
    intersection_viz = viz.CGA2D(
        circle_model,
        colors=["#0072B2", "#D55E00", "#56B4E9", "#E69F00", "#7C3AED"],
        xlim=(-4.0, 4.0),
        ylim=(-3.0, 3.0),
    )
    return (intersection_viz,)


@app.cell
def _():
    circle_a_radius = 2.0
    circle_b_radius = 1.5
    return circle_a_radius, circle_b_radius


@app.cell
def _(circle_model, intersection_viz):
    _ax, _ay = intersection_viz.coordinates("A", default=(-1.0, 0.0))
    _bx, _by = intersection_viz.coordinates("B", default=(1.1, 0.25))

    A = circle_model.up(_ax, _ay).named("A")
    B = circle_model.up(_bx, _by).named("B")
    return A, B


@app.cell
def _(A, B, circle_a_radius, circle_b_radius, circle_model):
    _center_a = circle_model.coordinates(A)
    _center_b = circle_model.coordinates(B)
    _dual_circle_a = circle_model.round_point(
        _center_a,
        radius_squared=-(circle_a_radius**2),
    )
    _dual_circle_b = circle_model.round_point(
        _center_b,
        radius_squared=-(circle_b_radius**2),
    )
    circle_a = circle_model.dual(_dual_circle_a).named("C1", latex=r"C_1")
    circle_b = circle_model.dual(_dual_circle_b).named("C2", latex=r"C_2")
    return circle_a, circle_b


@app.cell
def _(circle_a, circle_b, meet):
    intersection_dipole = meet(circle_a, circle_b).named("D")
    return (intersection_dipole,)


@app.cell
def _(A, B, circle_a, circle_b, intersection_dipole, intersection_viz):
    intersection_viz.display(
        [A, B],
        immutable=[circle_a, circle_b, intersection_dipole],
    )
    return


@app.cell
def _(
    A,
    B,
    circle_a,
    circle_a_radius,
    circle_b,
    circle_b_radius,
    circle_model,
    gm,
    intersection_dipole,
    intersection_viz,
    mo,
):
    _dipole_attitude = circle_model.attitude(intersection_dipole).named(
        "att_D",
        latex=r"\operatorname{att}(D)",
    )
    _dipole_carrier = circle_model.carrier(intersection_dipole).named(
        "car_D",
        latex=r"\operatorname{car}(D)",
    )
    _dipole_container = circle_model.container(intersection_dipole).named(
        "con_D",
        latex=r"\operatorname{con}(D)",
    )
    try:
        _dipole_center = circle_model.center(intersection_dipole).named(
            "M_D",
            latex=r"\operatorname{cen}(D)",
        )
        _dipole_midpoint = circle_model.down(_dipole_center).named(
            "m_D",
            latex=r"m_D",
        )
        _dipole_radius_squared = circle_model.radius_squared(_dipole_center).named(
            "rho_D_squared",
            latex=r"\rho_D^2",
        )
        _signed_separation_squared = float(_dipole_radius_squared)
        if _signed_separation_squared > 1e-9:
            _intersection_status = "two real intersection points"
        elif _signed_separation_squared >= -1e-9:
            _intersection_status = "one repeated tangent point"
        else:
            _intersection_status = "an imaginary point pair (no real intersections)"
        _separation_text = f"{_signed_separation_squared:.6g}"
        _dipole_semantics = gm.md(t"""
        ## Point-pair semantics

        “Point pair” is the common descriptive name for this intersection;
        Galaga's CGA vocabulary calls the general grade-2 round object a
        **dipole**.

        Dipole: {intersection_dipole} <br/>
        Attitude (the pair axis): {_dipole_attitude} <br/>
        Carrier (the line containing the pair): {_dipole_carrier} <br/>
        Center: {_dipole_center} <br/>
        Euclidean midpoint: {_dipole_midpoint} <br/>
        Signed squared half-separation: {_dipole_radius_squared} <br/>
        Container: {_dipole_container}
        """)
    except ValueError:
        _intersection_status = "a degenerate or concentric meet"
        _separation_text = "undefined"
        _dipole_semantics = gm.md(t"""
        ## Point-pair semantics

        The meet is a degenerate dipole with no finite round center.

        Dipole: {intersection_dipole} <br/>
        Attitude: {_dipole_attitude} <br/>
        Carrier: {_dipole_carrier} <br/>
        Container: {_dipole_container}
        """)

    mo.vstack(
        [
            gm.md(t"""
            ## Live circle meet

            A real direct circle is the dual of a round-point vector with
            negative signed radius squared. The circle intersection itself is
            the generic regressive product:

            $$
            D = C_1 \\vee C_2.
            $$

            {A} <br/>
            {B} <br/>
            {circle_a} <br/>
            {circle_b} <br/>
            {intersection_dipole}

            Fixed radii: $r_1={circle_a_radius}$ and
            $r_2={circle_b_radius}$.

            Dipole center radius squared: `{_separation_text}`.

            Current interpretation: **{_intersection_status}**.
            """),
            _dipole_semantics,
            intersection_viz,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The renderer does not solve two Euclidean circle equations. Python first
    computes `D = meet(C1, C2)`. The widget classifies that grade-2 direct
    object as a dipole and uses its CGA center, signed radius, and attitude to
    draw its real factors. A negative signed radius remains a valid imaginary
    dipole, but it has no real endpoint markers.
    """)
    return


if __name__ == "__main__":
    app.run()
