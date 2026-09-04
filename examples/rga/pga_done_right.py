import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import matplotlib.pyplot as plt
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        antireverse,
        antiwedge,
        geometric_antiproduct,
        gp,
        p_pga,
        p_rga,
        sandwich,
        squared,
    )
    from galaga.rga import RigidModel

    return (
        Algebra,
        DisplayPolicy,
        RigidModel,
        antireverse,
        antiwedge,
        geometric_antiproduct,
        gm,
        gp,
        mo,
        np,
        p_pga,
        p_rga,
        plt,
        sandwich,
        squared,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Projective geometric algebra, done both ways

    Two reflections in parallel planes produce a translation by twice the
    distance between the planes. This notebook computes that familiar geometry
    with both forms of $\mathrm{Cl}(3,0,1)$ discussed in Eric Lengyel's
    [“Projective Geometric Algebra Done Right”](https://terathon.com/blog/pga-done-right.html):

    - **point-based PGA (RGA):** points are vectors and plane reflections use
      the geometric antiproduct;
    - **plane-based PGA:** planes are vectors and plane reflections use the
      geometric product.

    The representations reverse the grade ladder, but they must return the
    same Euclidean coordinates and preserve the same incidence relations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One metric, two geometric readings

    Both algebras have three positive Euclidean directions and one null
    projective direction. The metric alone does not decide whether vectors
    mean points or planes, so Galaga makes the semantic choice explicit through
    separate presets.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, RigidModel, p_pga, p_rga):
    point_algebra = Algebra(config=p_rga(), display=DisplayPolicy(content="full"))
    point_model = RigidModel(point_algebra, expr=True)
    plane_algebra = Algebra(config=p_pga(), display=DisplayPolicy(content="full"))
    return plane_algebra, point_algebra, point_model


@app.cell
def _(np, plane_algebra, point_algebra, point_model, squared):
    point_e1, point_e2, point_e3 = point_model.euclidean_basis_vectors()
    point_e4 = point_model.projective
    point_e23, point_e423, point_e321 = point_algebra.blades(
        point_e2 ^ point_e3,
        point_e4 ^ point_e2 ^ point_e3,
        point_e3 ^ point_e2 ^ point_e1,
        expr=True,
    )

    plane_e1, plane_e2, plane_e3, plane_e0 = plane_algebra.basis_vectors(expr=True)
    plane_e123, plane_e230, plane_e310, plane_e120 = plane_algebra.blades(
        plane_e1 ^ plane_e2 ^ plane_e3,
        plane_e2 ^ plane_e3 ^ plane_e0,
        plane_e3 ^ plane_e1 ^ plane_e0,
        plane_e1 ^ plane_e2 ^ plane_e0,
        expr=True,
    )

    point_metric = np.array(
        [float(squared(_e)) for _e in (point_e1, point_e2, point_e3, point_e4)]
    )
    plane_metric = np.array(
        [float(squared(_e)) for _e in (plane_e1, plane_e2, plane_e3, plane_e0)]
    )
    np.testing.assert_allclose(point_metric, (1, 1, 1, 0), rtol=0, atol=0)
    np.testing.assert_allclose(plane_metric, point_metric, rtol=0, atol=0)
    return (
        plane_e0,
        plane_e1,
        plane_e120,
        plane_e123,
        plane_e2,
        plane_e230,
        plane_e3,
        plane_e310,
        plane_metric,
        point_e1,
        point_e2,
        point_e23,
        point_e3,
        point_e321,
        point_e4,
        point_e423,
        point_metric,
    )


@app.cell
def _(gm, plane_metric, point_metric):
    gm.md(rt"""
    Computed point-based basis squares: `{point_metric!s}`.

    Computed plane-based basis squares: `{plane_metric!s}`.

    The numeric metrics agree exactly; only the geometric interpretation
    changes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | Geometric object or operation | Point-based PGA | Plane-based PGA |
    |---|---:|---:|
    | point | grade 1 | grade 3 |
    | line | grade 2 | grade 2 |
    | plane | grade 3 | grade 1 |
    | join two points | $\wedge$ | $\vee$ |
    | meet two planes | $\vee$ | $\wedge$ |
    | plane-reflection product | geometric antiproduct $\mathbin{\text{⟇}}$ | geometric product |
    """)
    return


@app.cell
def _(
    antireverse,
    geometric_antiproduct,
    np,
    plane_e120,
    plane_e123,
    plane_e230,
    plane_e310,
):
    def plane_point(coordinates):
        _x, _y, _z = coordinates
        return plane_e123 + _x * plane_e230 + _y * plane_e310 + _z * plane_e120

    def plane_coordinates(point):
        def _component(blade):
            _mask = int(np.flatnonzero(blade.data)[0])
            return point.coefficient(_mask) / blade.coefficient(_mask)

        _weight = _component(plane_e123)
        return np.array(
            (
                _component(plane_e230) / _weight,
                _component(plane_e310) / _weight,
                _component(plane_e120) / _weight,
            )
        )

    def antiproduct_sandwich(operator, value):
        return geometric_antiproduct(
            geometric_antiproduct(operator, value),
            antireverse(operator),
        )

    return antiproduct_sandwich, plane_coordinates, plane_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The grade reversal is concrete

    We encode the same two Euclidean points in both models. Joining them
    produces a bivector line in either case, but the point-based model joins
    with the exterior product while the plane-based model joins with the
    antiwedge.
    """)
    return


@app.cell
def _(gm, np, plane_coordinates, plane_point, point_model):
    source_coordinates = np.array((-1.0, 0.75, 0.0))
    other_coordinates = np.array((0.5, -0.25, 0.0))

    point_P = point_model.point(source_coordinates).named("P")
    point_Q = point_model.point(other_coordinates).named("Q")
    plane_P = plane_point(source_coordinates).named(r"P^{\star}", latex=r"P^{\star}")
    plane_Q = plane_point(other_coordinates).named(r"Q^{\star}", latex=r"Q^{\star}")

    np.testing.assert_allclose(point_model.coordinates(point_P), source_coordinates)
    np.testing.assert_allclose(plane_coordinates(plane_P), source_coordinates)
    np.testing.assert_allclose(point_model.coordinates(point_Q), other_coordinates)
    np.testing.assert_allclose(plane_coordinates(plane_Q), other_coordinates)

    _point_grades = (point_P.homogeneous_grade(), point_Q.homogeneous_grade())
    _plane_grades = (plane_P.homogeneous_grade(), plane_Q.homogeneous_grade())
    gm.md(rt"""
    Point-based points (grades `{_point_grades!s}`):

    {point_P}

    {point_Q}

    Plane-based points (grades `{_plane_grades!s}`):

    {plane_P}

    {plane_Q}
    """)
    return other_coordinates, plane_P, plane_Q, point_P, point_Q, source_coordinates


@app.cell
def _(antiwedge, gm, np, plane_P, plane_Q, point_P, point_Q):
    point_line = (point_P ^ point_Q).named("L")
    plane_line = antiwedge(plane_P, plane_Q).named(r"L^{\star}", latex=r"L^{\star}")

    _point_incidence = np.allclose((point_P ^ point_line).data, 0)
    _plane_incidence = np.allclose(antiwedge(plane_P, plane_line).data, 0)
    assert point_line.homogeneous_grade() == 2
    assert plane_line.homogeneous_grade() == 2
    assert _point_incidence and _plane_incidence

    gm.md(rt"""
    Point-based join:

    {point_P ^ point_Q}

    Plane-based join:

    {antiwedge(plane_P, plane_Q)}

    Both results have grade 2, and substituting $P$ back into its line gives
    zero in both incidence conventions: `{(_point_incidence, _plane_incidence)!s}`.
    """)
    return plane_line, point_line


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two parallel reflections

    Put one unit plane at $x=0$ and the other at $x=s$. Reflecting first in
    $x=s$ and then in $x=0$ translates every object by $2s$ along $+x$.

    The homogeneous plane formulas differ with the grade convention:

    $$
    \begin{aligned}
    g_{\vee}&=e_{423}-s e_{321}, & h_{\vee}&=e_{423},\\
    g_{\wedge}&=e_1+s e_0,       & h_{\wedge}&=e_1.
    \end{aligned}
    $$

    Move the planes and watch both products derive the same translation.
    Setting $s=0$ makes the planes coincide and both compositions become the
    identity.
    """)
    return


@app.cell
def _(mo):
    separation = mo.ui.slider(
        start=0.0,
        stop=2.5,
        step=0.05,
        value=0.75,
        label="plane separation s",
    )
    separation
    return (separation,)


@app.cell
def _(
    geometric_antiproduct,
    gm,
    gp,
    np,
    plane_algebra,
    plane_e0,
    plane_e1,
    point_e23,
    point_e321,
    point_e423,
    point_model,
    separation,
):
    point_moving_plane = (point_e423 - separation.value * point_e321).named(r"g_{\vee}")
    point_fixed_plane = point_e423.named(r"h_{\vee}")
    plane_moving_plane = (plane_e1 + separation.value * plane_e0).named(r"g_{\wedge}")
    plane_fixed_plane = plane_e1.named(r"h_{\wedge}")

    point_translator = geometric_antiproduct(point_moving_plane, point_fixed_plane).named(r"T_{\vee}")
    plane_translator = gp(plane_moving_plane, plane_fixed_plane).named(r"T_{\wedge}")

    _expected_point_translator = point_model.antiscalar + separation.value * point_e23
    _expected_plane_translator = plane_algebra.scalar(1) - separation.value * (plane_e1 ^ plane_e0)
    np.testing.assert_allclose(
        point_translator.data,
        _expected_point_translator.data,
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        plane_translator.data,
        _expected_plane_translator.data,
        rtol=0,
        atol=1e-12,
    )

    gm.md(rt"""
    Point-based plane reflections:

    {point_moving_plane}

    {point_fixed_plane}

    {geometric_antiproduct(point_moving_plane, point_fixed_plane)}

    Plane-based plane reflections:

    {plane_moving_plane}

    {plane_fixed_plane}

    {gp(plane_moving_plane, plane_fixed_plane)}

    The identities are different—$\text{{𝟙}}$ for the antiproduct and $1$ for
    the geometric product—but each bivector coefficient stores the same
    half-translation $s={separation.value:.2f}$.
    """)
    return (
        plane_fixed_plane,
        plane_moving_plane,
        plane_translator,
        point_fixed_plane,
        point_moving_plane,
        point_translator,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transform points and lines without casting

    Each operator now acts directly on every object in its own representation:

    $$
    X'_{\vee}=T_{\vee}\mathbin{\text{⟇}}X_{\vee}
      \mathbin{\text{⟇}}\underset{\Large\text{~}}{T_{\vee}},
    \qquad
    X'_{\wedge}=T_{\wedge}X_{\wedge}\widetilde{T}_{\wedge}.
    $$

    This is the article's practical goal: points remain points and lines remain
    lines throughout the sandwich action.
    """)
    return


@app.cell
def _(
    antiproduct_sandwich,
    antiwedge,
    gm,
    np,
    other_coordinates,
    plane_P,
    plane_Q,
    plane_coordinates,
    plane_line,
    plane_translator,
    point_P,
    point_Q,
    point_line,
    point_model,
    point_translator,
    sandwich,
    separation,
    source_coordinates,
):
    point_P_moved = antiproduct_sandwich(point_translator, point_P).named(r"P^{\prime}")
    point_Q_moved = antiproduct_sandwich(point_translator, point_Q).named(r"Q^{\prime}")
    point_line_moved = antiproduct_sandwich(point_translator, point_line).named(r"L^{\prime}")

    plane_P_moved = sandwich(plane_translator, plane_P).named(
        r"P^{\star\prime}",
        latex=r"P^{\star\prime}",
    )
    plane_Q_moved = sandwich(plane_translator, plane_Q).named(
        r"Q^{\star\prime}",
        latex=r"Q^{\star\prime}",
    )
    plane_line_moved = sandwich(plane_translator, plane_line).named(
        r"L^{\star\prime}",
        latex=r"L^{\star\prime}",
    )

    point_result_coordinates = point_model.coordinates(point_P_moved)
    point_other_result_coordinates = point_model.coordinates(point_Q_moved)
    plane_result_coordinates = plane_coordinates(plane_P_moved)
    plane_other_result_coordinates = plane_coordinates(plane_Q_moved)
    expected_coordinates = source_coordinates + np.array((2 * separation.value, 0, 0))

    np.testing.assert_allclose(point_result_coordinates, expected_coordinates, rtol=0, atol=1e-12)
    np.testing.assert_allclose(plane_result_coordinates, expected_coordinates, rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        point_other_result_coordinates,
        other_coordinates + (expected_coordinates - source_coordinates),
    )
    np.testing.assert_allclose(plane_other_result_coordinates, point_other_result_coordinates)
    np.testing.assert_allclose(
        point_line_moved.data,
        (point_P_moved ^ point_Q_moved).data,
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        plane_line_moved.data,
        antiwedge(plane_P_moved, plane_Q_moved).data,
        rtol=0,
        atol=1e-12,
    )

    _distance_before = np.linalg.norm(source_coordinates - other_coordinates)
    _distance_after = np.linalg.norm(point_result_coordinates - point_other_result_coordinates)
    _point_incidence_after = np.allclose((point_P_moved ^ point_line_moved).data, 0)
    _plane_incidence_after = np.allclose(antiwedge(plane_P_moved, plane_line_moved).data, 0)
    assert np.isclose(_distance_before, _distance_after)
    assert _point_incidence_after and _plane_incidence_after

    gm.md(rt"""
    {point_P_moved}

    Point-based coordinates: `{point_result_coordinates!s}`.

    {plane_P_moved}

    Plane-based coordinates: `{plane_result_coordinates!s}`.

    Expected real-world coordinates: `{expected_coordinates!s}`.

    The endpoint distance is preserved:
    `{_distance_before:.6g} → {_distance_after:.6g}`.
    The transformed point remains incident with the directly transformed line
    in both models: `{(_point_incidence_after, _plane_incidence_after)!s}`.
    """)
    return (
        expected_coordinates,
        plane_other_result_coordinates,
        plane_result_coordinates,
        point_other_result_coordinates,
        point_result_coordinates,
    )


@app.cell
def _(
    expected_coordinates,
    other_coordinates,
    plt,
    point_other_result_coordinates,
    separation,
    source_coordinates,
):
    _fig, _ax = plt.subplots(figsize=(8, 3.8))
    _ax.axvline(0, color="slategray", linewidth=2, label=r"$h: x=0$")
    _ax.axvline(separation.value, color="darkorange", linewidth=2, label=r"$g: x=s$")
    _ax.plot(
        (source_coordinates[0], other_coordinates[0]),
        (source_coordinates[1], other_coordinates[1]),
        "o-",
        color="steelblue",
        label="original line segment",
    )
    _ax.plot(
        (expected_coordinates[0], point_other_result_coordinates[0]),
        (expected_coordinates[1], point_other_result_coordinates[1]),
        "o-",
        color="crimson",
        label="after two reflections",
    )
    _ax.annotate(
        "",
        xy=(expected_coordinates[0], source_coordinates[1]),
        xytext=(source_coordinates[0], source_coordinates[1]),
        arrowprops={"arrowstyle": "->", "color": "black", "linewidth": 1.5},
    )
    _ax.text(
        (source_coordinates[0] + expected_coordinates[0]) / 2,
        source_coordinates[1] + 0.08,
        f"2s = {2 * separation.value:.2f}",
        ha="center",
    )
    _ax.set(xlim=(-1.5, 4.5), ylim=(-0.7, 1.25), xlabel="x", ylabel="y")
    _ax.set_aspect("equal")
    _ax.grid(alpha=0.2)
    _ax.legend(loc="lower right")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why the product must follow the representation

    A product is not a convention-free “multiply” button. For the point-based
    trivector planes, the geometric product cannot supply the antiscalar
    identity term needed by the translator. For the plane-based vector planes,
    the geometric antiproduct cannot supply the scalar identity term. The
    product and the object representation have to be chosen together.
    """)
    return


@app.cell
def _(
    geometric_antiproduct,
    gm,
    gp,
    plane_fixed_plane,
    plane_moving_plane,
    point_fixed_plane,
    point_moving_plane,
):
    wrong_point_product = gp(point_moving_plane, point_fixed_plane)
    wrong_plane_product = geometric_antiproduct(plane_moving_plane, plane_fixed_plane)

    gm.md(rt"""
    Geometric product of point-based planes (no antiscalar identity):

    {wrong_point_product}

    Geometric antiproduct of plane-based planes (no scalar identity):

    {wrong_plane_product}

    These are valid algebra elements, but they are not the two-reflection
    translators derived above.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The two PGA models are De Morgan dual descriptions of the same Euclidean
    geometry. Point-based PGA makes point joins direct and pairs plane
    reflections with the geometric antiproduct. Plane-based PGA makes planes
    direct and pairs their reflections with the geometric product. Galaga keeps
    both combinations explicit, and the computed coordinates, distances, and
    incidences provide the reality check.

    Next, try replacing the parallel planes with intersecting planes: their two
    reflections produce a rotation by twice the angle between them.
    """)
    return


if __name__ == "__main__":
    app.run()
