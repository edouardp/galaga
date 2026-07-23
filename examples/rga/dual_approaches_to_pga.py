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
    import numpy as np

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        antireverse,
        antiwedge,
        exp,
        geometric_antiproduct,
        p_pga,
        p_rga,
        sandwich,
    )
    from galaga.rga import RigidModel

    return (
        Algebra,
        DisplayPolicy,
        RigidModel,
        antireverse,
        antiwedge,
        exp,
        geometric_antiproduct,
        gm,
        mo,
        np,
        p_pga,
        p_rga,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Two dual approaches to projective geometric algebra

    Eric Lengyel describes two fully dual uses of $\mathrm{Cl}(3,0,1)$:

    | Point-based RGA | Plane-based PGA |
    |---|---|
    | vectors represent points | vectors represent planes |
    | bivectors represent lines | bivectors represent lines |
    | trivectors represent planes | trivectors represent points |
    | joins use the exterior product | joins use the antiwedge |
    | rigid motions use the geometric antiproduct | rigid motions use the geometric product |

    Galaga keeps both conventions explicit. They share the same signature and
    numeric core, but use different model semantics and presentation policies.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, RigidModel, p_pga, p_rga):
    point_algebra = Algebra(config=p_rga(), display=DisplayPolicy(content="full"))
    point_model = RigidModel(point_algebra, expr=True)
    plane_algebra = Algebra(config=p_pga(), display=DisplayPolicy(content="full"))
    return plane_algebra, point_model


@app.cell
def _(plane_algebra, point_model):
    r_e1, r_e2, r_e3 = point_model.euclidean_basis_vectors()
    r_e4 = point_model.projective

    p_e1, p_e2, p_e3, p_e0 = plane_algebra.basis_vectors(expr=True)
    p_e123, p_E1, p_E2, p_E3 = plane_algebra.blades(
        p_e1 ^ p_e2 ^ p_e3,
        p_e2 ^ p_e3 ^ p_e0,
        -(p_e1 ^ p_e3 ^ p_e0),
        p_e1 ^ p_e2 ^ p_e0,
        expr=True,
    )
    return p_E1, p_E2, p_E3, p_e0, p_e1, p_e123, r_e1, r_e2, r_e3, r_e4


@app.cell
def _(np, p_E1, p_E2, p_E3, p_e123):
    def plane_point(x, y, z):
        return p_e123 + x * p_E1 + y * p_E2 + z * p_E3

    def plane_coordinates(point):
        def component(blade):
            _mask = int(np.flatnonzero(blade.data)[0])
            return point.data[_mask] / blade.data[_mask]

        _weight = component(p_e123)
        return np.array(
            [component(p_E1) / _weight, component(p_E2) / _weight, component(p_E3) / _weight]
        )

    return plane_coordinates, plane_point


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The grade ladder is reversed

    The two representations encode the same Euclidean coordinates but place a
    point at opposite ends of the grade ladder. Consequently, joining two
    point-based vectors uses $\wedge$, while joining two plane-based
    trivectors uses $\vee$. Both results are lines and therefore bivectors.
    """)
    return


@app.cell
def _(antiwedge, gm, plane_point, point_model):
    point_P = point_model.point((1, 2, 3)).named("P")
    point_Q = point_model.point((-1, 1, 0)).named("Q")
    point_line = (point_P ^ point_Q).named("L")

    plane_P = plane_point(1, 2, 3).named(r"P^{\star}", latex=r"P^{\star}")
    plane_Q = plane_point(-1, 1, 0).named(r"Q^{\star}", latex=r"Q^{\star}")
    plane_line = antiwedge(plane_P, plane_Q).named(r"L^{\star}", latex=r"L^{\star}")

    _point_grades = (
        point_P.homogeneous_grade(),
        point_line.homogeneous_grade(),
    )
    _plane_grades = (
        plane_P.homogeneous_grade(),
        plane_line.homogeneous_grade(),
    )

    gm.md(rt"""
    Point-based representation:

    {point_P}

    {point_P ^ point_Q}

    Its point and line grades are `{_point_grades!s}`.

    Plane-based representation:

    {plane_P}

    {antiwedge(plane_P, plane_Q)}

    Its point and line grades are `{_plane_grades!s}`.
    """)
    return plane_P, point_P


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The same translation through dual products

    A unit translation in the $e_1$ direction has complementary operators:

    $$
    T_{\vee}=\text{𝟙}+\tfrac12 e_{23},
    \qquad
    T_{\wedge}=\exp\!\left(-\tfrac12 e_{10}\right).
    $$

    The point-based operator acts by the geometric antiproduct and antireverse.
    The plane-based motor acts by the usual geometric-product sandwich. The
    differing formulas are not competing hacks; they are De Morgan duals.
    """)
    return


@app.cell
def _(
    antireverse,
    exp,
    geometric_antiproduct,
    gm,
    np,
    p_e0,
    p_e1,
    plane_P,
    plane_coordinates,
    point_P,
    point_model,
    r_e2,
    r_e3,
    sandwich,
):
    point_translator = (point_model.antiscalar + 0.5 * (r_e2 ^ r_e3)).named(r"T_{\vee}")
    translated_point = geometric_antiproduct(
        geometric_antiproduct(point_translator, point_P),
        antireverse(point_translator),
    ).named(r"P^{\prime}", latex=r"P^{\prime}")

    plane_translator = exp(-0.5 * (p_e1 ^ p_e0)).named(r"T_{\wedge}")
    translated_plane_point = sandwich(plane_translator, plane_P).named(
        r"P^{\star\prime}",
        latex=r"P^{\star\prime}",
    )

    _point_coordinates = point_model.coordinates(translated_point)
    _plane_coordinates = plane_coordinates(translated_plane_point)
    _coordinates_agree = np.allclose(_point_coordinates, _plane_coordinates)

    gm.md(rt"""
    {point_translator}

    {translated_point}

    {plane_translator}

    {translated_plane_point}

    Point-based coordinates: `{_point_coordinates!s}`.

    Plane-based coordinates: `{_plane_coordinates!s}`.

    The two computations agree: `{_coordinates_agree!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Which convention is preferable depends on the problem and the explanation:
    point-based RGA makes points and their joins especially direct;
    plane-based PGA makes planes, intersections, and conventional motor formulas
    especially direct. Galaga exposes both without hiding their duality behind
    one overloaded model object.

    This notebook follows Eric Lengyel's “Dual Approaches to Projective
    Geometric Algebra” distinction.
    """)
    return


if __name__ == "__main__":
    app.run()
