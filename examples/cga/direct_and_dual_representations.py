import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        geometric_product,
        left_contraction,
        outer_product,
        p_cga,
        reverse,
        scalar_product,
    )
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        geometric_product,
        gm,
        left_contraction,
        mo,
        outer_product,
        p_cga,
        reverse,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Direct and dual representations in one CGA model

    Direct/OPNS and dual/IPNS conformal geometry are two interpretations of
    one conformal algebra. They share the metric, multivector storage,
    Euclidean basis, $e_o$, $e_\infty$, and the canonical point embedding
    `up()`.

    There are two related operations to keep separate:

    1. **Change interpretation:** keep the same coefficients and change what
       each grade means geometrically.
    2. **Convert the same locus:** apply the full conformal Hodge dual to its
       representing blade.

    This notebook performs the second operation explicitly. It needs one
    `ConformalModel`, not a direct model and a dual model.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    conformal_algebra = Algebra(
        config=p_cga(spatial_dim=2),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(conformal_algebra, expr=True)
    conformal_dimension = conformal_algebra.n
    conformal_metric_determinant = conformal_algebra.metric_determinant
    return (
        cga,
        conformal_algebra,
        conformal_dimension,
        conformal_metric_determinant,
    )


@app.cell
def _(cga, conformal_dimension, conformal_metric_determinant, gm):
    gm.md(rt"""
    ## What gets dualized?

    The model embeds 2D Euclidean space in a conformal vector space of
    dimension $N={conformal_dimension}$. Its Hodge dual therefore sends grade
    $k$ to grade $N-k$ across the **complete conformal space**, including the
    null plane spanned by $e_o$ and $e_\infty$.

    The two representations use the same basis values:

    {cga.origin}$,\;$ {cga.infinity}.

    The metric determinant is derived from the model's Gram matrix:
    $\det(G)={conformal_metric_determinant:.6g}$.
    """)
    return


@app.cell
def _(cga, conformal_algebra, geometric_product, outer_product, reverse):
    e1, e2 = cga.euclidean_basis_vectors()
    conformal_pseudoscalar = conformal_algebra.I.named("I_C", latex=r"I_C")
    e1_dual = cga.dual(e1).named("e1_star", latex=r"e_1^\star")
    e1_dual_from_product = geometric_product(
        reverse(e1),
        conformal_pseudoscalar,
    )
    e1_dual_expected_support = outer_product(
        e2,
        cga.origin,
        cga.infinity,
    )
    full_hodge_identity_holds = e1_dual.almost_equal(e1_dual_from_product)
    null_plane_participates = e1_dual.almost_equal(e1_dual_expected_support)
    return (
        conformal_pseudoscalar,
        e1_dual,
        e2,
        full_hodge_identity_holds,
        null_plane_participates,
    )


@app.cell
def _(
    conformal_pseudoscalar,
    e1_dual,
    full_hodge_identity_holds,
    gm,
    null_plane_participates,
):
    gm.md(rt"""
    With Galaga's right-Hodge convention,

    $$
    A^\star=\overline{{G(A)}}=\widetilde A I_C.
    $$

    Here the conformal pseudoscalar is

    {conformal_pseudoscalar}

    and dualizing the first Euclidean basis vector gives

    {e1_dual}

    The product identity holds: `{full_hodge_identity_holds}`. The result is
    proportional to $e_2\wedge e_o\wedge e_\infty$:
    `{null_plane_participates}`. Thus the conversion is not a spatial-only
    dual, even though the spatial attitude may be the most visible part of
    the result.
    """)
    return


@app.cell
def _(cga, outer_product):
    circle_radius = 1.0
    P = cga.up(-circle_radius, 0.0).named("P")
    Q = cga.up(0.0, circle_radius).named("Q")
    R = cga.up(circle_radius, 0.0).named("R")

    C_opns = outer_product(P, Q, R).named("C_opns", latex=r"C_{\mathrm{OPNS}}")
    C_ipns = cga.dual(C_opns).named("C_ipns", latex=r"C_{\mathrm{IPNS}}")

    circle_center = cga.up(0.0, 0.0)
    C_ipns_analytic = (
        circle_center
        + (circle_radius**2 / (2.0 * cga.null_pair)) * cga.infinity
    ).named("C_ipns_analytic", latex=r"\widehat C_{\mathrm{IPNS}}")

    _circle_pivot = next(
        _index
        for _index, _coefficient in enumerate(C_ipns_analytic.data)
        if abs(_coefficient) > 1e-12
    )
    circle_projective_scale = (
        C_ipns.data[_circle_pivot] / C_ipns_analytic.data[_circle_pivot]
    )
    circle_forms_agree = C_ipns.almost_equal(
        circle_projective_scale * C_ipns_analytic
    )
    return (
        C_ipns,
        C_ipns_analytic,
        C_opns,
        P,
        Q,
        R,
        circle_forms_agree,
        circle_projective_scale,
    )


@app.cell
def _(
    C_ipns,
    C_ipns_analytic,
    C_opns,
    circle_forms_agree,
    circle_projective_scale,
    gm,
):
    gm.md(rt"""
    ## One circle, two blades

    Three embedded points construct the direct/OPNS circle:

    {C_opns:block}

    Applying the full conformal dual gives its dual/IPNS vector:

    {C_ipns:block}

    Independently, a circle with centre $c$ and radius $r$ has IPNS form

    $$
    P(c)+\frac{{r^2}}{{2(e_o\mathbin{{\cdot}}e_\infty)}}e_\infty.
    $$

    e.g.

    {C_ipns_analytic:block}

    The computed and analytic forms agree projectively with scale
    `{circle_projective_scale:.6g}`: `{circle_forms_agree}`.
    """)
    return


@app.cell
def _(C_ipns, C_opns, cga, outer_product, scalar_product):
    X_on = cga.up(0.0, -1.0).named("X_on", latex=r"X_{\mathrm{on}}")
    X_off = cga.up(0.0, 0.0).named("X_off", latex=r"X_{\mathrm{off}}")

    opns_on_residual = outer_product(X_on, C_opns).named(
        "opns_on_residual",
        latex=r"X_{\mathrm{on}}\wedge C_{\mathrm{OPNS}}",
    )
    ipns_on_residual = scalar_product(X_on, C_ipns).named(
        "ipns_on_residual",
        latex=r"X_{\mathrm{on}}\mathbin{\cdot}C_{\mathrm{IPNS}}",
    )
    opns_off_residual = outer_product(X_off, C_opns).named(
        "opns_off_residual",
        latex=r"X_{\mathrm{off}}\wedge C_{\mathrm{OPNS}}",
    )
    ipns_off_residual = scalar_product(X_off, C_ipns).named(
        "ipns_off_residual",
        latex=r"X_{\mathrm{off}}\mathbin{\cdot}C_{\mathrm{IPNS}}",
    )
    return (
        X_off,
        X_on,
        ipns_off_residual,
        ipns_on_residual,
        opns_off_residual,
        opns_on_residual,
    )


@app.cell
def _(
    X_off,
    X_on,
    gm,
    ipns_off_residual,
    ipns_on_residual,
    opns_off_residual,
    opns_on_residual,
):
    gm.md(rt"""
    ## The incidence equation changes

    A direct blade describes its locus by $X\wedge A=0$; the corresponding
    dual blade describes it by contraction, which for this grade-1 circle is
    $X\mathbin{{\cdot}}A^\star=0$.

    The point {X_on} is on the circle:

    {opns_on_residual}

    {ipns_on_residual}

    The centre {X_off} is not on the circle:

    {opns_off_residual}

    {ipns_off_residual}
    """)
    return


@app.cell
def _(P, Q, cga, left_contraction, outer_product, scalar_product):
    P_strict_dual = cga.dual(P).named("P_strict_dual", latex=r"P^\star")
    point_direct_on = outer_product(P, P)
    point_strict_dual_on = left_contraction(P, P_strict_dual)
    point_zero_sphere_on = scalar_product(P, P)
    point_direct_off = outer_product(Q, P)
    point_strict_dual_off = left_contraction(Q, P_strict_dual)
    point_zero_sphere_off = scalar_product(Q, P)
    return (
        P_strict_dual,
        point_direct_off,
        point_direct_on,
        point_strict_dual_off,
        point_strict_dual_on,
        point_zero_sphere_off,
        point_zero_sphere_on,
    )


@app.cell
def _(
    P,
    P_strict_dual,
    gm,
    point_direct_off,
    point_direct_on,
    point_strict_dual_off,
    point_strict_dual_on,
    point_zero_sphere_off,
    point_zero_sphere_on,
):
    gm.md(rt"""
    ## Why points look exceptional

    The uniform full-space conversion of the grade-1 point {P} is the
    complementary grade-3 blade

    {P_strict_dual}

    It gives the same point locus through contraction. At $P$, the direct and
    strict-dual residuals are `{point_direct_on}` and
    `{point_strict_dual_on}`; at a different conformal point they are
    `{point_direct_off}` and `{point_strict_dual_off}`.

    But the original null vector $P$ can also be read as an IPNS zero-radius
    circle. Its residual $X \mathbin{{\cdot}} P$ is {point_zero_sphere_on:block} at $P$ and {point_zero_sphere_off:block} at the other
    point. This useful second description is why CGA tables often say that a
    point has the same direct and dual representation. It does not mean
    $P^\star=P$.
    """)
    return


@app.cell
def _(P, R, cga, e2, outer_product):
    L_opns = outer_product(P, R, cga.infinity).named(
        "L_opns",
        latex=r"L_{\mathrm{OPNS}}",
    )
    L_ipns = cga.dual(L_opns).named(
        "L_ipns",
        latex=r"L_{\mathrm{IPNS}}",
    )
    _line_pivot = next(
        _index
        for _index, _coefficient in enumerate(e2.data)
        if abs(_coefficient) > 1e-12
    )
    line_normal_scale = L_ipns.data[_line_pivot] / e2.data[_line_pivot]
    line_is_x_axis = L_ipns.almost_equal(line_normal_scale * e2)
    return L_ipns, L_opns, line_is_x_axis, line_normal_scale


@app.cell
def _(L_ipns, L_opns, gm, line_is_x_axis, line_normal_scale):
    gm.md(rt"""
    ## A flat example

    The direct x-axis includes the conformal point at infinity:

    $$
    L_{{\mathrm{{OPNS}}}}=P(-1,0)\wedge P(1,0)\wedge e_\infty.
    $$

    {L_opns}

    Its full conformal dual is the IPNS normal vector

    {L_ipns}

    It is proportional to $e_2$ with scale `{line_normal_scale:.6g}`:
    `{line_is_x_axis}`.
    """)
    return


@app.cell
def _(C_ipns, C_opns, cga, conformal_dimension, conformal_metric_determinant):
    circle_opns_grade = C_opns.homogeneous_grade()
    circle_ipns_grade = conformal_dimension - circle_opns_grade
    circle_double_dual_factor = (
        (-1) ** (circle_opns_grade * circle_ipns_grade)
    ) * conformal_metric_determinant
    C_opns_projective_return = cga.dual(C_ipns).named(
        "C_opns_projective_return",
        latex=r"(C_{\mathrm{IPNS}})^\star",
    )
    circle_return_agrees = C_opns_projective_return.almost_equal(
        circle_double_dual_factor * C_opns
    )
    return (
        C_opns_projective_return,
        circle_double_dual_factor,
        circle_return_agrees,
    )


@app.cell
def _(
    C_opns_projective_return,
    circle_double_dual_factor,
    circle_return_agrees,
    gm,
):
    gm.md(rt"""
    ## Converting back

    Applying the same Hodge operation twice gives a metric- and grade-derived
    scale:

    $$
    (A_k^\star)^\star
      =(-1)^{{k(N-k)}}\det(G)A_k.
    $$

    For this circle the factor is `{circle_double_dual_factor:.6g}` and the
    returned blade is

    {C_opns_projective_return}

    It agrees with the original direct blade at that scale:
    `{circle_return_agrees}`. Since geometric blades are homogeneous, this is
    the same represented locus. An exact coefficient round-trip can divide by
    the derived factor when exact normalization matters.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Practical rule

    - Construct Euclidean points once with the model's canonical `up()`.
    - Build OPNS objects with wedges of points and, for flats, $e_\infty$.
    - Convert an object to IPNS explicitly with `cga.dual(object)`.
    - Use outer products for direct joins and IPNS intersections.
    - Use the appropriate contraction or inner-product incidence equation for
      an IPNS object.
    - Treat overall nonzero scale as projectively irrelevant unless a
      particular normalization is required.

    Direct and dual are properties of how a blade is being interpreted—not
    mutable state carried by `ConformalModel`.
    """)
    return


if __name__ == "__main__":
    app.run()
