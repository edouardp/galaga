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
        Notation,
        antireverse,
        complement,
        geometric_antiproduct,
        gp,
        reverse,
        squared,
    )

    return (
        Algebra,
        DisplayPolicy,
        Notation,
        antireverse,
        complement,
        geometric_antiproduct,
        gm,
        gp,
        mo,
        np,
        plt,
        reverse,
        squared,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Space and antispace move together

    A homogeneous object records both the basis directions it occupies—its
    **space**—and the complementary directions it does not occupy—its
    **antispace**. Eric Lengyel's
    [“Space-Antispace Transform Correspondence in Projective Geometric Algebra”](https://terathon.com/blog/space-antispace-pga.html)
    shows that a Euclidean transform of one facet is inseparable from a
    reciprocal transform of the other.

    We will compute the article's most practical example in
    $\mathbb R_{2,0,1}$:

    - a regular translation moves points rigidly in space;
    - its complementary translation acts projectively in antispace;
    - their homogeneous matrices are inverse transposes.

    Every sign, complement, fixed geometry, and matrix below is derived from
    the algebra.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The projective plane

    The basis vectors $e_1,e_2$ are Euclidean and $e_3$ is null. A finite
    homogeneous point is

    $$
    P=x e_1+y e_2+w e_3,
    $$

    normally with $w=1$. Its complement is the homogeneous line

    $$
    \overline P=x e_{23}+y e_{31}+w e_{12}.
    $$

    The same three coordinates therefore describe a point in space and a line
    in antispace.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, Notation, np, squared):
    space_algebra = Algebra(
        gram=np.diag((1.0, 1.0, 0.0)),
        notation=Notation.lengyel(),
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = space_algebra.basis_vectors(expr=True)
    e12, e23, e31 = space_algebra.blades(
        e1 ^ e2,
        e2 ^ e3,
        e3 ^ e1,
        expr=True,
    )
    e31 = e31.named("e₃₁", latex=r"e_{31}")
    antiunit = space_algebra.pseudoscalar(expr=True).named("𝟙", latex=r"\text{𝟙}")
    metric_squares = np.array([float(squared(_e)) for _e in (e1, e2, e3)])
    np.testing.assert_allclose(metric_squares, (1, 1, 0), rtol=0, atol=0)
    return antiunit, e1, e12, e2, e23, e3, e31, metric_squares, space_algebra


@app.cell
def _(gm, metric_squares):
    gm.md(rt"""
    The basis squares are computed as `{metric_squares!s}`. Thus $e_3$ supplies
    homogeneous weight without contributing Euclidean length.
    """)
    return


@app.cell
def _(
    antireverse,
    e1,
    e12,
    e2,
    e23,
    e3,
    e31,
    geometric_antiproduct,
    gp,
    np,
    reverse,
):
    def blade_component(value, blade):
        _mask = int(np.flatnonzero(blade.data)[0])
        return value.coefficient(_mask) / blade.coefficient(_mask)

    def point(coordinates, *, weight=1.0):
        _x, _y = coordinates
        return _x * e1 + _y * e2 + weight * e3

    def point_coordinates(value):
        _weight = blade_component(value, e3)
        if np.isclose(_weight, 0):
            raise ValueError("an ideal point has no finite Euclidean coordinates")
        return np.array(
            (
                blade_component(value, e1) / _weight,
                blade_component(value, e2) / _weight,
            )
        )

    def line_coefficients(value):
        return np.array(
            (
                blade_component(value, e23),
                blade_component(value, e31),
                blade_component(value, e12),
            )
        )

    def antiproduct_sandwich(operator, value):
        return geometric_antiproduct(
            geometric_antiproduct(operator, value),
            antireverse(operator),
        )

    def product_sandwich(operator, value):
        return gp(gp(operator, value), reverse(operator))

    def vector_action_matrix(action):
        _basis = (e1, e2, e3)
        return np.array(
            [
                [blade_component(action(_source), _target) for _source in _basis]
                for _target in _basis
            ]
        )

    return (
        antiproduct_sandwich,
        blade_component,
        line_coefficients,
        point,
        point_coordinates,
        product_sandwich,
        vector_action_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A point and its negative space

    For a point $(p_x,p_y)$, the dual line has equation

    $$
    p_x x+p_y y+1=0.
    $$

    If the point is a distance $d$ from the origin, the line is a distance
    $1/d$ from the origin. This reciprocal distance is a geometric consequence
    of using the same homogeneous coordinates on complementary basis blades.
    """)
    return


@app.cell
def _(complement, e1, e12, e2, e23, e3, e31, gm, line_coefficients, np, point):
    duality_point = point((1.0, 0.5)).named("P")
    duality_line = complement(duality_point)

    assert complement(e1) == e23
    assert complement(e2) == e31
    assert complement(e3) == e12

    dual_line_coefficients = line_coefficients(duality_line)
    point_distance = np.linalg.norm((1.0, 0.5))
    line_distance = abs(dual_line_coefficients[2]) / np.linalg.norm(dual_line_coefficients[:2])
    np.testing.assert_allclose(point_distance * line_distance, 1, rtol=0, atol=1e-12)

    gm.md(rt"""
    {duality_point}

    {duality_line}

    Line coefficients `(a, b, c)`: `{dual_line_coefficients!s}`.

    Point distance: `{point_distance:.6g}`.

    Dual-line distance: `{line_distance:.6g}`.

    Their product is `{point_distance * line_distance:.6g}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Translation and reciprocal translation

    Let $\tau$ be a translation along $+x$. Its regular point-based operator
    and complementary operator are

    $$
    Q=\text{𝟙}-\frac{\tau}{2}e_2,
    \qquad
    \overline Q=1-\frac{\tau}{2}e_{31}.
    $$

    The first uses the geometric antiproduct:

    $$
    A'=Q\mathbin{\text{⟇}}A
       \mathbin{\text{⟇}}\underset{\Large\text{~}}{Q}.
    $$

    The complementary operator uses the geometric product:

    $$
    A'=\overline Q A\widetilde{\overline Q}.
    $$
    """)
    return


@app.cell
def _(mo):
    translation = mo.ui.slider(
        start=0.0,
        stop=0.75,
        step=0.05,
        value=0.5,
        label="translation τ",
    )
    translation
    return (translation,)


@app.cell
def _(
    antiproduct_sandwich,
    antiunit,
    complement,
    e2,
    e31,
    gm,
    np,
    product_sandwich,
    space_algebra,
    translation,
    vector_action_matrix,
):
    regular_operator = (antiunit - 0.5 * translation.value * e2).named("Q")
    reciprocal_operator = complement(regular_operator)

    _expected_reciprocal = space_algebra.scalar(1) - 0.5 * translation.value * e31
    np.testing.assert_allclose(
        reciprocal_operator.data,
        _expected_reciprocal.data,
        rtol=0,
        atol=1e-12,
    )

    regular_matrix = vector_action_matrix(
        lambda _value: antiproduct_sandwich(regular_operator, _value)
    )
    reciprocal_matrix = vector_action_matrix(
        lambda _value: product_sandwich(reciprocal_operator, _value)
    )
    inverse_transpose = np.linalg.inv(regular_matrix).T
    np.testing.assert_allclose(reciprocal_matrix, inverse_transpose, rtol=0, atol=1e-12)

    gm.md(rt"""
    {regular_operator}

    {reciprocal_operator}

    Regular homogeneous matrix:

    `{regular_matrix!s}`

    Complementary homogeneous matrix:

    `{reciprocal_matrix!s}`

    Computed inverse transpose:

    `{inverse_transpose!s}`
    """)
    return reciprocal_operator, regular_operator


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The matrices expose the correspondence:

    $$
    H=
    \begin{bmatrix}
    1&0&\tau\\
    0&1&0\\
    0&0&1
    \end{bmatrix},
    \qquad
    \overline H=(H^{-1})^T=
    \begin{bmatrix}
    1&0&0\\
    0&1&0\\
    -\tau&0&1
    \end{bmatrix}.
    $$

    On a finite point, $H$ gives the ordinary translation
    $(x,y)\mapsto(x+\tau,y)$. The complementary matrix instead gives

    $$
    (x,y)\mapsto
    \left(
      \frac{x}{1-\tau x},
      \frac{y}{1-\tau x}
    \right),
    $$

    a projective transformation rather than a Euclidean isometry.
    """)
    return


@app.cell
def _(
    antiproduct_sandwich,
    complement,
    gm,
    np,
    point,
    point_coordinates,
    product_sandwich,
    reciprocal_operator,
    regular_operator,
    translation,
):
    sample_point = point((0.4, 0.8)).named("A")
    translated_point = antiproduct_sandwich(regular_operator, sample_point).named(r"A^{\prime}")
    reciprocal_point = product_sandwich(reciprocal_operator, sample_point).named(
        r"\overline A^{\prime}"
    )

    translated_coordinates = point_coordinates(translated_point)
    reciprocal_coordinates = point_coordinates(reciprocal_point)
    _expected_translation = np.array((0.4 + translation.value, 0.8))
    _denominator = 1 - translation.value * 0.4
    _expected_reciprocal = np.array((0.4 / _denominator, 0.8 / _denominator))
    np.testing.assert_allclose(translated_coordinates, _expected_translation, rtol=0, atol=1e-12)
    np.testing.assert_allclose(reciprocal_coordinates, _expected_reciprocal, rtol=0, atol=1e-12)

    transformed_dual = product_sandwich(reciprocal_operator, complement(sample_point))
    complement_of_transform = complement(translated_point)
    np.testing.assert_allclose(
        transformed_dual.data,
        complement_of_transform.data,
        rtol=0,
        atol=1e-12,
    )

    gm.md(rt"""
    {sample_point}

    Regular translation:

    {translated_point}

    Coordinates: `{translated_coordinates!s}`.

    Complement translation acting on the same point representation:

    {reciprocal_point}

    Coordinates: `{reciprocal_coordinates!s}`.

    Transforming the dual line with $\overline Q$ exactly equals complementing
    the point after translating it: `{np.allclose(transformed_dual.data, complement_of_transform.data)!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fixed geometry and the projective boundary

    A regular translation along $x$ fixes the ideal point $e_2$, perpendicular
    to its direction. The complementary translation fixes:

    - every point on $x=0$;
    - the line $y=0$ through the origin, parallel to the translation.

    Its denominator $1-\tau x$ also reveals a genuine projective boundary. For
    $\tau\ne0$, the line $x=1/\tau$ is mapped to the horizon instead of to a
    finite point.
    """)
    return


@app.cell
def _(
    antiproduct_sandwich,
    blade_component,
    e2,
    e3,
    e31,
    gm,
    np,
    point,
    product_sandwich,
    reciprocal_operator,
    regular_operator,
    translation,
):
    fixed_ideal_point = e2.named(r"C_{\infty}")
    fixed_origin_line = e31.named("m")
    fixed_finite_point = point((0.0, 1.0)).named("B")

    assert antiproduct_sandwich(regular_operator, fixed_ideal_point).almost_equal(fixed_ideal_point)
    assert product_sandwich(reciprocal_operator, fixed_origin_line).almost_equal(fixed_origin_line)
    assert product_sandwich(reciprocal_operator, fixed_finite_point).almost_equal(fixed_finite_point)

    if np.isclose(translation.value, 0):
        singular_x = np.inf
        singular_weight = 1.0
    else:
        singular_x = 1 / translation.value
        _singular_point = point((singular_x, 0.0))
        _singular_image = product_sandwich(reciprocal_operator, _singular_point)
        singular_weight = blade_component(_singular_image, e3)
        np.testing.assert_allclose(singular_weight, 0, rtol=0, atol=1e-12)

    gm.md(rt"""
    Fixed ideal point under the regular translation:

    {fixed_ideal_point}

    Fixed origin line and sample point under the complement translation:

    {fixed_origin_line}

    {fixed_finite_point}

    Projective boundary location: `{singular_x:.6g}`.

    Homogeneous weight after mapping a boundary point: `{singular_weight:.6g}`.
    """)
    return (singular_x,)


@app.cell
def _(
    antiproduct_sandwich,
    np,
    plt,
    point,
    point_coordinates,
    product_sandwich,
    reciprocal_operator,
    regular_operator,
    singular_x,
):
    plot_points = np.array(
        (
            (-1.1, -0.8),
            (-1.1, 0.8),
            (-0.4, -0.4),
            (-0.4, 0.4),
            (0.35, -0.75),
            (0.35, 0.75),
            (0.75, -0.5),
            (0.75, 0.5),
        )
    )
    regular_targets = np.array(
        [
            point_coordinates(antiproduct_sandwich(regular_operator, point(_coordinates)))
            for _coordinates in plot_points
        ]
    )
    reciprocal_targets = np.array(
        [
            point_coordinates(product_sandwich(reciprocal_operator, point(_coordinates)))
            for _coordinates in plot_points
        ]
    )

    def _draw_arrows(_ax, _starts, _targets, _color):
        for _start, _target in zip(_starts, _targets, strict=True):
            _ax.annotate(
                "",
                xy=_target,
                xytext=_start,
                arrowprops={"arrowstyle": "->", "color": _color, "alpha": 0.75},
            )
        _ax.scatter(_starts[:, 0], _starts[:, 1], color="black", s=20, zorder=3)
        _ax.scatter(_targets[:, 0], _targets[:, 1], color=_color, s=24, zorder=3)

    _fig, (_regular_ax, _reciprocal_ax) = plt.subplots(1, 2, figsize=(11, 4.8))
    _draw_arrows(_regular_ax, plot_points, regular_targets, "steelblue")
    _regular_ax.set_title("Regular translation in space")

    _draw_arrows(_reciprocal_ax, plot_points, reciprocal_targets, "crimson")
    _reciprocal_ax.axvline(0, color="seagreen", linewidth=2, label="fixed points: x=0")
    _reciprocal_ax.axhline(0, color="darkorange", linewidth=2, label="fixed line: y=0")
    if np.isfinite(singular_x) and singular_x <= 2.4:
        _reciprocal_ax.axvline(
            singular_x,
            color="purple",
            linestyle="--",
            label="maps to horizon",
        )
    _reciprocal_ax.set_title("Complement translation in antispace")
    _reciprocal_ax.legend(loc="upper left", fontsize=8)

    for _ax in (_regular_ax, _reciprocal_ax):
        _ax.set(xlim=(-1.5, 2.4), ylim=(-2.1, 2.1), xlabel="x", ylabel="y")
        _ax.set_aspect("equal")
        _ax.grid(alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The complement is doing more than relabeling basis blades. It intertwines
    two group actions:

    $$
    \overline{
      Q
      \mathbin{\text{⟇}}
      A
      \mathbin{\text{⟇}}
      \utilde{Q}
    }
    =
    \overline{Q} \mathbin{\text{⟑}} \overline{A} \mathbin{\text{⟑}} \widetilde{\overline{Q}}.
    $$

    On the space facet, this example is an ordinary distance-preserving
    translation. On the antispace facet, the same correspondence is a
    perspective projectivity with fixed geometry through the origin. The
    inverse-transpose matrix is the coordinate shadow of that complement
    relationship.
    """)
    return

if __name__ == "__main__":
    app.run()
