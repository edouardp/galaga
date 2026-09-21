"""Teach exterior algebra as the zero-metric Clifford algebra."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_annotation as ann
    import galaga_marimo as gm
    from galaga import Algebra, grade, metric_inner_product, outer_product

    return Algebra, ann, gm, grade, metric_inner_product, mo, outer_product


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exterior algebra inside Clifford algebra

    Exterior algebra and Clifford algebra use the same language of scalars,
    vectors, bivectors, and higher-grade multivectors—but they do not normally
    use the same multiplication.

    There is one revealing exception. When the quadratic form is zero, the
    Clifford product is exactly the wedge product:

    $$
    \boxed{\Lambda(V)\cong\operatorname{Cl}(V,0)}.
    $$

    This lesson starts there and then turns the metric on. The annotations mark
    precisely which terms the metric adds and which exterior terms remain
    unchanged.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. What “inside” means

    For a general metric $g$, it is tempting to say that $\Lambda(V)$ is a
    subalgebra of $\operatorname{Cl}(V,g)$. That is not quite right: the two
    algebras can be identified as vector spaces, but their products differ.

    The fully canonical statement is

    $$
    \operatorname{gr}\operatorname{Cl}(V,g)\cong\Lambda(V),
    $$

    where the left side is the associated graded algebra of the filtered
    Clifford algebra. In ordinary geometric-algebra calculations, the resulting
    grade decomposition lets us use one multivector representation for both
    products.

    At $g=0$ there is no qualification: the defining Clifford relation becomes

    $$
    v^2=0,
    $$

    so vectors anticommute and Clifford multiplication is exterior
    multiplication.
    """)
    return


@app.cell
def _(Algebra, outer_product):
    exterior_algebra = Algebra(0, 0, 3, expr=True)
    exterior_e1, exterior_e2, exterior_e3 = exterior_algebra.basis_vectors(expr=True)
    exterior_a = (exterior_e1 + exterior_e2).named("a")
    exterior_b = (exterior_e2 + exterior_e3).named("b")
    exterior_product = (exterior_a * exterior_b).named("P_0", latex="P_0")
    exterior_wedge = outer_product(exterior_a, exterior_b).named("W_0", latex="W_0")
    exterior_products_agree = exterior_product.almost_equal(exterior_wedge)
    exterior_zero = exterior_algebra.scalar(0)
    exterior_basis_squares_are_zero = tuple(
        (basis_vector * basis_vector).almost_equal(exterior_zero)
        for basis_vector in (exterior_e1, exterior_e2, exterior_e3)
    )
    exterior_basis_blades = tuple(
        blade
        for blade_grade in range(4)
        for blade in exterior_algebra.basis_blades(blade_grade)
    )
    exterior_all_basis_products_agree = all(
        (left_blade * right_blade).almost_equal(outer_product(left_blade, right_blade))
        for left_blade in exterior_basis_blades
        for right_blade in exterior_basis_blades
    )
    exterior_basis_product_count = len(exterior_basis_blades) ** 2
    exterior_metric_table = exterior_algebra.bilinear_form_table()
    exterior_wedge_table = exterior_algebra.wedge_product_table()
    return (
        exterior_a,
        exterior_algebra,
        exterior_all_basis_products_agree,
        exterior_b,
        exterior_basis_product_count,
        exterior_basis_squares_are_zero,
        exterior_e1,
        exterior_e2,
        exterior_e3,
        exterior_metric_table,
        exterior_product,
        exterior_products_agree,
        exterior_wedge,
        exterior_wedge_table,
    )


@app.cell
def _(ann, exterior_product, exterior_wedge):
    exterior_product_view = ann.annotator(
        ann.on(
            ann.operator("geometric_product"),
            label="Clifford product",
            marker="overbrace",
            color="#6F42C1",
        ),
        ann.on(
            ann.grade(2),
            label="only exterior grade survives",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
            join=True,
        ),
    )(exterior_product)
    exterior_wedge_view = ann.annotator(
        ann.on(
            ann.operator("outer_product"),
            label="wedge product",
            marker="overbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.grade(2),
            label="the same multivector",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
            join=True,
        ),
    )(exterior_wedge)
    return exterior_product_view, exterior_wedge_view


@app.cell
def _(
    exterior_all_basis_products_agree,
    exterior_basis_product_count,
    exterior_basis_squares_are_zero,
    exterior_metric_table,
    exterior_product_view,
    exterior_products_agree,
    exterior_wedge_table,
    exterior_wedge_view,
    gm,
):
    gm.md(rt"""
    ## 2. Start with $\operatorname{{Cl}}(0,0,3)$

    Galaga's third signature entry counts degenerate directions. Thus
    `Algebra(0, 0, 3)` has three basis vectors and an identically zero bilinear
    form:

    {exterior_metric_table:block}

    Every basis-vector square vanishes:
    **{all(exterior_basis_squares_are_zero)}**.

    Take $a=e_1+e_2$ and $b=e_2+e_3$. Their Clifford and wedge products are
    computed independently:

    {exterior_product_view:block}

    {exterior_wedge_view:block}

    The values agree: **{exterior_products_agree}**. The repeated $e_2$ makes
    no contribution because $e_2^2=0$.

    This is not merely a feature of the example: Galaga checked all
    **{exterior_basis_product_count}** ordered pairs of basis blades, and every
    Clifford product agrees with the corresponding wedge product:
    **{exterior_all_basis_products_agree}**.

    The basis-vector wedge table is therefore also the multiplication table
    for the positive-grade generators of this Clifford algebra:

    {exterior_wedge_table:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Alternation is now a consequence of the Clifford relation. Since

    $$
    (u+v)^2=u^2+uv+vu+v^2=0,
    $$

    and both vector squares vanish, $uv=-vu$. Repeated directions vanish and
    exchanging two directions changes orientation—the familiar exterior
    algebra rules.
    """)
    return


@app.cell
def _(Algebra, exterior_wedge, outer_product):
    euclidean_algebra = Algebra(3, expr=True)
    euclidean_e1, euclidean_e2, euclidean_e3 = euclidean_algebra.basis_vectors(expr=True)
    euclidean_a = (euclidean_e1 + euclidean_e2).named("a")
    euclidean_b = (euclidean_e2 + euclidean_e3).named("b")
    euclidean_square = (euclidean_e1 * euclidean_e1).named("S", latex="S")
    euclidean_product = (euclidean_a * euclidean_b).named("P_E", latex="P_E")
    euclidean_wedge = outer_product(euclidean_a, euclidean_b).named("W_E", latex="W_E")
    euclidean_split_holds = euclidean_product.almost_equal(
        euclidean_algebra.scalar(1) + euclidean_wedge
    )
    euclidean_orthogonal_product = (euclidean_e1 * euclidean_e2).named("Q_E", latex="Q_E")
    euclidean_orthogonal_wedge = outer_product(euclidean_e1, euclidean_e2)
    euclidean_orthogonal_products_agree = euclidean_orthogonal_product.almost_equal(
        euclidean_orthogonal_wedge
    )
    euclidean_metric_table = euclidean_algebra.bilinear_form_table()
    same_exterior_coefficients_zero_euclidean = bool(
        (exterior_wedge.data == euclidean_wedge.data).all()
    )
    return (
        euclidean_a,
        euclidean_algebra,
        euclidean_b,
        euclidean_e1,
        euclidean_e2,
        euclidean_e3,
        euclidean_metric_table,
        euclidean_orthogonal_product,
        euclidean_orthogonal_products_agree,
        euclidean_product,
        euclidean_split_holds,
        euclidean_square,
        euclidean_wedge,
        same_exterior_coefficients_zero_euclidean,
    )


@app.cell
def _(ann, euclidean_product, euclidean_square):
    euclidean_product_view = ann.annotator(
        ann.on(
            ann.grade(0),
            label="metric overlap",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
            join=True,
        ),
        ann.on(
            ann.grade(2),
            label="unchanged exterior part",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
            join=True,
        ),
    )(euclidean_product)
    euclidean_square_view = ann.annotate(
        euclidean_square,
        ann.on(
            ann.grade(0),
            label="the metric is now visible",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
        ),
    )
    return euclidean_product_view, euclidean_square_view


@app.cell
def _(
    euclidean_metric_table,
    euclidean_orthogonal_product,
    euclidean_orthogonal_products_agree,
    euclidean_product_view,
    euclidean_split_holds,
    euclidean_square_view,
    gm,
    same_exterior_coefficients_zero_euclidean,
):
    gm.md(rt"""
    ## 3. Turn on a Euclidean metric

    Now use the same ordered basis with Gram matrix

    {euclidean_metric_table:block}

    A vector no longer squares to zero:

    {euclidean_square_view:block}

    With the same coordinate expressions $a=e_1+e_2$ and $b=e_2+e_3$:

    {euclidean_product_view:block}

    The shared $e_2$ direction has become the scalar $1$, while the bivector
    terms are unchanged. The computed decomposition holds:
    **{euclidean_split_holds}**. The wedge-product coefficient arrays in the
    zero and Euclidean metrics are identical:
    **{same_exterior_coefficients_zero_euclidean}**.

    There is a useful trap here. Distinct *orthogonal* basis vectors still give

    {euclidean_orthogonal_product:block}

    which agrees with $e_1\wedge e_2$:
    **{euclidean_orthogonal_products_agree}**. Looking only at orthogonal basis
    products can therefore hide the distinction between the two algebras.
    """)
    return


@app.cell
def _(Algebra, exterior_wedge, metric_inner_product, outer_product):
    oblique_algebra = Algebra(
        gram=[[1, 0.5, 0], [0.5, 1, 0], [0, 0, 1]],
        expr=True,
    )
    oblique_e1, oblique_e2, oblique_e3 = oblique_algebra.basis_vectors(expr=True)
    oblique_basis_product = (oblique_e1 * oblique_e2).named("P_O", latex="P_O")
    oblique_basis_pairing = metric_inner_product(oblique_e1, oblique_e2).named(
        "g_{12}", latex="g_{12}"
    )
    oblique_basis_wedge = outer_product(oblique_e1, oblique_e2).named("W_O", latex="W_O")
    oblique_split_holds = oblique_basis_product.almost_equal(
        oblique_basis_pairing + oblique_basis_wedge
    )
    oblique_metric_table = oblique_algebra.bilinear_form_table()
    oblique_coordinate_wedge = outer_product(
        oblique_e1 + oblique_e2,
        oblique_e2 + oblique_e3,
    )
    same_exterior_coefficients_zero_oblique = bool(
        (exterior_wedge.data == oblique_coordinate_wedge.data).all()
    )
    return (
        oblique_algebra,
        oblique_basis_pairing,
        oblique_basis_product,
        oblique_basis_wedge,
        oblique_e1,
        oblique_e2,
        oblique_e3,
        oblique_metric_table,
        oblique_split_holds,
        same_exterior_coefficients_zero_oblique,
    )


@app.cell
def _(ann, oblique_basis_product):
    oblique_product_view = ann.annotator(
        ann.on(
            ann.grade(0),
            label="basis vectors are not orthogonal",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
        ),
        ann.on(
            ann.grade(2),
            label="oriented plane",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )(oblique_basis_product)
    return (oblique_product_view,)


@app.cell
def _(
    gm,
    oblique_basis_pairing,
    oblique_basis_wedge,
    oblique_metric_table,
    oblique_product_view,
    oblique_split_holds,
    same_exterior_coefficients_zero_oblique,
):
    gm.md(rt"""
    ## 4. An oblique basis makes the split impossible to miss

    Keep Euclidean geometry but choose $e_1\mathbin{{\bullet}}e_2=0.5$:

    {oblique_metric_table:block}

    Two distinct basis vectors now produce both grades:

    {oblique_product_view:block}

    Computed separately, the pieces are

    {oblique_basis_pairing:block}

    {oblique_basis_wedge:block}

    and reconstruct the product: **{oblique_split_holds}**. Again, changing the
    metric did not change the wedge coefficients for the same coordinate
    vectors: **{same_exterior_coefficients_zero_oblique}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For vectors $a$ and $b$, the metric and exterior pieces can be recovered by
    symmetrising and antisymmetrising the Clifford product:

    $$
    \boxed{
      a\mathbin{\bullet}b=\frac{ab+ba}{2},
      \qquad
      a\wedge b=\frac{ab-ba}{2}
    }.
    $$

    Equivalently,

    $$
    \boxed{ab=a\mathbin{\bullet}b+a\wedge b}.
    $$

    The first term is symmetric and metric-dependent. The second is
    antisymmetric and metric-independent.
    """)
    return


@app.cell
def _(metric_inner_product, oblique_e1, oblique_e2, outer_product):
    symmetric_part = (0.5 * (oblique_e1 * oblique_e2 + oblique_e2 * oblique_e1)).named(
        "S", latex="S"
    )
    antisymmetric_part = (0.5 * (oblique_e1 * oblique_e2 - oblique_e2 * oblique_e1)).named(
        "A", latex="A"
    )
    symmetric_identity_holds = symmetric_part.almost_equal(
        metric_inner_product(oblique_e1, oblique_e2)
    )
    antisymmetric_identity_holds = antisymmetric_part.almost_equal(
        outer_product(oblique_e1, oblique_e2)
    )
    vector_product_identities_hold = symmetric_identity_holds and antisymmetric_identity_holds
    return antisymmetric_part, symmetric_part, vector_product_identities_hold


@app.cell
def _(ann, antisymmetric_part, symmetric_part):
    symmetric_part_view = ann.annotate(
        symmetric_part,
        ann.on(
            ann.grade(0),
            label="symmetric metric part",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
        ),
    )
    antisymmetric_part_view = ann.annotate(
        antisymmetric_part,
        ann.on(
            ann.grade(2),
            label="antisymmetric exterior part",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )
    return antisymmetric_part_view, symmetric_part_view


@app.cell
def _(antisymmetric_part_view, gm, symmetric_part_view, vector_product_identities_hold):
    gm.md(rt"""
    Galaga verifies both identities in the oblique basis:

    {symmetric_part_view:block}

    {antisymmetric_part_view:block}

    Both computed identities hold: **{vector_product_identities_hold}**.
    """)
    return


@app.cell
def _(mo):
    metric_coupling = mo.ui.slider(
        start=-0.9,
        stop=0.9,
        step=0.1,
        value=0.5,
        label=r"off-diagonal metric entry $g_{12}$",
    )
    return (metric_coupling,)


@app.cell
def _(Algebra, ann, gm, metric_coupling, metric_inner_product, mo, outer_product):
    metric_parameter = metric_coupling.value
    parameter_algebra = Algebra(
        gram=[[1, metric_parameter], [metric_parameter, 1]],
        expr=True,
    )
    parameter_e1, parameter_e2 = parameter_algebra.basis_vectors(expr=True)
    parameter_product = (parameter_e1 * parameter_e2).named("P(t)", latex="P(t)")
    parameter_pairing = metric_inner_product(parameter_e1, parameter_e2)
    parameter_wedge = outer_product(parameter_e1, parameter_e2)
    parameter_decomposition_holds = parameter_product.almost_equal(
        parameter_pairing + parameter_wedge
    )
    parameter_metric_table = parameter_algebra.bilinear_form_table()
    parameter_product_view = ann.annotator(
        ann.on(
            ann.grade(0),
            label="moves with the metric",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
        ),
        ann.on(
            ann.grade(2),
            label="stays fixed",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )(parameter_product)
    mo.vstack(
        [
            metric_coupling,
            gm.md(rt"""
            ## 5. Vary the metric, not the exterior algebra

            Move the off-diagonal Gram entry while retaining the same ordered
            basis and coordinate vectors:

            {parameter_metric_table:block}

            {parameter_product_view:block}

            The scalar coefficient follows $g_{{12}}$; the $e_{{12}}$
            coefficient remains $1$. The decomposition is still exact:
            **{parameter_decomposition_holds}**.
            """),
        ]
    )
    return (
        metric_parameter,
        parameter_algebra,
        parameter_decomposition_holds,
        parameter_e1,
        parameter_e2,
        parameter_pairing,
        parameter_product,
        parameter_product_view,
        parameter_wedge,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The same pattern at higher grades

    For homogeneous multivectors $A_r$ and $B_s$, the geometric product can
    contain grades

    $$
    |r-s|,\ |r-s|+2,\ldots,r+s,
    $$

    subject to the dimension of the algebra. The exterior product is the
    highest possible component:

    $$
    A_r\wedge B_s=\langle A_rB_s\rangle_{r+s}.
    $$

    A repeated direction illustrates what the metric changes. Let
    $A=e_{12}$ and $B=e_{23}+e_{34}$ in four dimensions. The first part of $B$
    overlaps $A$; the second is disjoint.
    """)
    return


@app.cell
def _(Algebra, grade, outer_product):
    routing_algebra = Algebra(4, expr=True)
    routing_e1, routing_e2, routing_e3, routing_e4 = routing_algebra.basis_vectors(expr=True)
    routing_A = outer_product(routing_e1, routing_e2).named("A")
    routing_B = (
        outer_product(routing_e2, routing_e3) + outer_product(routing_e3, routing_e4)
    ).named("B")
    routing_product = (routing_A * routing_B).named("P_4", latex="P_4")
    routing_wedge = outer_product(routing_A, routing_B).named("W_4", latex="W_4")
    routing_grade_two = grade(routing_product, 2)
    routing_grade_four = grade(routing_product, 4)
    routing_top_grade_is_wedge = routing_grade_four.almost_equal(routing_wedge)

    zero_routing_algebra = Algebra(0, 0, 4, expr=True)
    zero_routing_e1, zero_routing_e2, zero_routing_e3, zero_routing_e4 = (
        zero_routing_algebra.basis_vectors(expr=True)
    )
    zero_routing_A = outer_product(zero_routing_e1, zero_routing_e2).named("A")
    zero_routing_B = (
        outer_product(zero_routing_e2, zero_routing_e3)
        + outer_product(zero_routing_e3, zero_routing_e4)
    ).named("B")
    zero_routing_product = (zero_routing_A * zero_routing_B).named("P_0", latex="P_0")
    zero_routing_wedge = outer_product(zero_routing_A, zero_routing_B)
    zero_routing_products_agree = zero_routing_product.almost_equal(zero_routing_wedge)
    return (
        routing_A,
        routing_B,
        routing_algebra,
        routing_grade_four,
        routing_grade_two,
        routing_product,
        routing_top_grade_is_wedge,
        routing_wedge,
        zero_routing_A,
        zero_routing_B,
        zero_routing_algebra,
        zero_routing_product,
        zero_routing_products_agree,
    )


@app.cell
def _(ann, routing_product, zero_routing_product):
    routing_product_view = ann.annotator(
        ann.on(
            ann.grade(2),
            label="metric resolves the overlap",
            marker="underbrace",
            background="#FFF3CD",
            label_color="#9A6700",
        ),
        ann.on(
            ann.grade(4),
            label="exterior product",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )(routing_product)
    zero_routing_product_view = ann.annotate(
        zero_routing_product,
        ann.on(
            ann.grade(4),
            label="only the disjoint directions survive",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )
    return routing_product_view, zero_routing_product_view


@app.cell
def _(
    gm,
    routing_product_view,
    routing_top_grade_is_wedge,
    routing_wedge,
    zero_routing_product_view,
    zero_routing_products_agree,
):
    gm.md(rt"""
    In Euclidean $\operatorname{{Cl}}(4)$:

    {routing_product_view:block}

    The independently computed wedge product is

    {routing_wedge:block}

    and equals the grade-four projection of $AB$:
    **{routing_top_grade_is_wedge}**.

    In $\operatorname{{Cl}}(0,0,4)$, the repeated $e_2$ kills the overlapping
    term instead of contracting it:

    {zero_routing_product_view:block}

    Here the complete Clifford product again equals the wedge product:
    **{zero_routing_products_agree}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. The construction to remember

    The exterior algebra is not an extra collection of objects bolted onto a
    Clifford algebra. It is the zero-metric starting point:

    $$
    \underbrace{\operatorname{Cl}(V,0)}_{\text{wedge only}}
      \quad\longrightarrow\quad
    \underbrace{\operatorname{Cl}(V,g)}_{
      \substack{\text{wedge}\,+\\\text{metric contractions}}}.
    $$

    Galaga can therefore teach both with the same multivectors:

    - `Algebra(0, 0, n)` gives the exterior algebra exactly;
    - `^` computes the metric-independent wedge product in every algebra;
    - `*` computes the metric-dependent Clifford product;
    - grade projection isolates the exterior part of a homogeneous product;
    - arbitrary Gram matrices show why orthogonal coordinates are only a
      convenient special case.

    This covers the algebra of multivectors. Differential forms require
    additional geometric structure—fields, pullbacks, and the exterior
    derivative $d$—which Galaga does not currently model as first-class
    objects. The companion lesson on inner and interior products continues at
    the point where a metric identifies vectors with covectors.
    """)
    return


if __name__ == "__main__":
    app.run()
