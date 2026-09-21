"""Teach inner products, contractions, and interior products with semantic annotations."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_annotation as ann
    import galaga_marimo as gm
    from galaga import (
        Algebra,
        Presenter,
        antiwedge,
        doran_lasenby_inner,
        hestenes_inner,
        left_contraction,
        left_hodge_dual,
        left_interior_product,
        metric_inner_product,
        outer_product,
        presets,
        right_contraction,
        right_hodge_dual,
        right_interior_product,
        scalar_product,
    )

    return (
        Algebra,
        Presenter,
        ann,
        antiwedge,
        doran_lasenby_inner,
        gm,
        hestenes_inner,
        left_contraction,
        left_hodge_dual,
        left_interior_product,
        metric_inner_product,
        mo,
        outer_product,
        presets,
        right_contraction,
        right_hodge_dual,
        right_interior_product,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Inner products and interior products

    The names sound interchangeable, but they answer different questions:

    - an **inner product** pairs two objects and returns a scalar;
    - an **interior product** inserts one exterior object into another and
      lowers grade;
    - a **contraction** is a metric-dependent grade-lowering product, and many
      authors use that word as a synonym for interior product.

    The vector case hides these distinctions because most conventions reduce
    to the familiar dot product. Higher grades reveal the choices.

    This lesson follows the mathematics from exterior algebra to Clifford
    algebra and then to Galaga's Lengyel/RGA interior products. Annotations
    identify the operation being applied and the grades or signs that survive.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Exterior algebra starts with insertion

    The canonical exterior-algebra interior product acts on a differential
    form. For $v\in V$ and $\omega\in\Lambda^kV^*$,

    $$
    (\iota_v\omega)(v_1,\ldots,v_{k-1})
      =\omega(v,v_1,\ldots,v_{k-1}).
    $$

    It lowers degree by one and obeys the graded Leibniz rule

    $$
    \iota_v(\alpha\wedge\beta)
      =(\iota_v\alpha)\wedge\beta
       +(-1)^{\deg\alpha}\alpha\wedge(\iota_v\beta).
    $$

    Dually, a covector $\lambda\in V^*$ inserts canonically into a
    multivector $X\in\Lambda^kV$. These operations need no metric because the
    natural pairing is between vectors and covectors.

    Exterior algebra alone does **not** canonically contract a vector with
    another vector or multivector in $\Lambda V$. A metric supplies the
    missing identification $v^\flat=g(v,\cdot)\in V^*$.

    See the standard construction in
    [MIT's differential-forms notes](https://math.mit.edu/classes/18.952/2015SP/docs/chapter2.pdf).
    """)
    return


@app.cell
def _(Algebra, Presenter, presets):
    algebra = Algebra(3, expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    insertion_vector = (e1 + 2 * e2).named("a")
    insertion_plane = (e2 ^ e3).named("B")
    comparison_plane = (e1 ^ e2).named("E")
    scalar_two = algebra.scalar(2, expr=True).named("s")
    functional_full = Presenter(notation=presets.notation.functional(), content="full")
    return (
        comparison_plane,
        e1,
        e2,
        functional_full,
        insertion_plane,
        insertion_vector,
        scalar_two,
    )


@app.cell
def _(comparison_plane, gm, insertion_plane, insertion_vector):
    gm.md(t"""
    We work in Euclidean $\\mathrm{{Cl}}(3)$ so signs caused by product
    conventions are not mixed with signature changes.

    {insertion_vector:block}

    {insertion_plane:block}

    {comparison_plane:block}

    The first vector and plane expose both grade-lowering and grade-raising
    parts. The second plane $E=e_1\\wedge e_2$ makes the sign comparisons
    especially transparent.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. A vector–blade product has an interior and an exterior direction

    Once the metric identifies vectors and covectors, vector insertion becomes
    the grade-lowering part of the Clifford product. For a vector $a$ and a
    homogeneous $s$-vector $B_s$,

    $$
    aB_s
      =\langle aB_s\rangle_{s-1}
       +\langle aB_s\rangle_{s+1}.
    $$

    The first term removes one exterior direction; the second adds one.
    Galaga calls the first term a left contraction and the second the outer
    product.
    """)
    return


@app.cell
def _(
    ann,
    functional_full,
    gm,
    insertion_plane,
    insertion_vector,
    left_contraction,
    outer_product,
):
    vector_plane_product = (insertion_vector * insertion_plane).named("P")
    grade_lowering_part = left_contraction(insertion_vector, insertion_plane).named("P_1", latex="P_1")
    grade_raising_part = outer_product(insertion_vector, insertion_plane).named("P_3", latex="P_3")
    product_decomposition_holds = vector_plane_product.almost_equal(grade_lowering_part + grade_raising_part)
    product_decomposition_view = ann.annotator(
        ann.on(
            ann.operator("geometric_product"),
            label="Clifford product",
            marker="overbrace",
            color="#6F42C1",
        ),
        ann.on(
            ann.grade(1),
            label="grade lowering",
            marker="underbrace",
            background="#DDEBFF",
            label_color="#005EA8",
            join=True,
        ),
        ann.on(
            ann.grade(3),
            label="grade raising",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
            join=True,
        ),
    )(vector_plane_product)
    gm.md(t"""
    {functional_full(product_decomposition_view):block}

    Separately computed:

    {functional_full(grade_lowering_part):block}

    {functional_full(grade_raising_part):block}

    The two selected grades reconstruct the complete product:
    **{product_decomposition_holds}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Scalar-valued inner products

    For homogeneous $A_r$ and $B_s$, Galaga distinguishes two scalar
    operations:

    $$
    \operatorname{scalar\_product}(A_r,B_s)
      =\langle A_rB_s\rangle_0,
    $$

    $$
    \operatorname{metric\_inner\_product}(A_r,B_s)
      =\langle A_r\widetilde{B_s}\rangle_0.
    $$

    Both vanish when $r\ne s$. The reversion in the second formula makes it
    the bilinear form induced by the vector metric on the exterior algebra.
    For blades it measures signed squared volume.

    With $E=e_{12}$, $E^2=-1$ but
    $E\widetilde E=E(-E)=+1$. The two operations therefore answer different
    scalar questions.
    """)
    return


@app.cell
def _(
    ann,
    comparison_plane,
    functional_full,
    gm,
    metric_inner_product,
    scalar_product,
):
    bivector_scalar_product = scalar_product(comparison_plane, comparison_plane).named("S")
    bivector_metric_pairing = metric_inner_product(comparison_plane, comparison_plane).named("G")
    scalar_product_view = ann.annotator(
        ann.on(
            ann.operator("scalar_product"),
            label_latex=r"\langle EE\rangle_0",
            marker="overbrace",
            color="#D55E00",
        ),
        ann.on(
            ann.grade(0),
            label="geometric square",
            marker="underbrace",
            background="#FDE7D9",
            label_color="#A33A00",
        ),
    )(bivector_scalar_product)
    metric_pairing_view = ann.annotator(
        ann.on(
            ann.operator("metric_inner_product"),
            label_latex=r"\langle E\widetilde E\rangle_0",
            marker="overbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.grade(0),
            label="squared area",
            marker="underbrace",
            background="#DDEBFF",
            label_color="#005EA8",
        ),
    )(bivector_metric_pairing)
    bivector_pairings_have_opposite_signs = bivector_scalar_product.almost_equal(-bivector_metric_pairing)
    gm.md(t"""
    {functional_full(scalar_product_view):block}

    {functional_full(metric_pairing_view):block}

    The computed pairings have opposite signs:
    **{bivector_pairings_have_opposite_signs}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Products called “inner” that need not return scalars

    Historical GA terminology also calls grade-difference operations inner
    products:

    $$
    \operatorname{hestenes\_inner}(A_r,B_s)
      =\langle A_rB_s\rangle_{|r-s|},
      \qquad r,s>0,
    $$

    $$
    \operatorname{doran\_lasenby\_inner}(A_r,B_s)
      =\langle A_rB_s\rangle_{|r-s|},
    $$

    where the second operation retains scalar interactions. Both can return a
    vector or higher-grade result, so they are not inner products in the
    strict scalar-valued sense.

    Galaga exposes their names rather than hiding the choice behind a generic
    “inner product” function. Scalar operands reveal the difference.
    """)
    return


@app.cell
def _(
    ann,
    doran_lasenby_inner,
    e1,
    functional_full,
    gm,
    hestenes_inner,
    scalar_two,
):
    hestenes_scalar_vector = hestenes_inner(scalar_two, e1).named("H")
    doran_scalar_vector = doran_lasenby_inner(scalar_two, e1).named("D")
    hestenes_scalar_view = ann.annotator(
        ann.on(
            ann.content("expr"),
            label="scalar pair omitted",
            marker="underbrace",
            color="#6B7280",
        ),
    )(hestenes_scalar_vector)
    doran_scalar_view = ann.annotator(
        ann.on(
            ann.operator("doran_lasenby_inner"),
            label="scalar multiplication retained",
            marker="overbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.grade(1),
            label="vector result",
            marker="underbrace",
            background="#DDEBFF",
            label_color="#005EA8",
        ),
    )(doran_scalar_vector)
    scalar_policy_distinguished = hestenes_scalar_vector.almost_equal(
        scalar_two.algebra.scalar(0)
    ) and doran_scalar_vector.almost_equal(2 * e1)
    gm.md(t"""
    {functional_full(hestenes_scalar_view):block}

    {functional_full(doran_scalar_view):block}

    The computed results distinguish the scalar policies:
    **{scalar_policy_distinguished}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Left and right contractions choose a direction

    For homogeneous grades $r$ and $s$, Galaga's conventional contractions are

    $$
    A_r\mathbin{\rfloor}B_s
      =\langle A_rB_s\rangle_{s-r},
      \qquad r\le s,
    $$

    $$
    A_r\mathbin{\lfloor}B_s
      =\langle A_rB_s\rangle_{r-s},
      \qquad r\ge s.
    $$

    One removes the left operand's grade from the right; the other removes the
    right operand's grade from the left. Reversing the operand order can change
    both which operation is defined and the sign of its result.
    """)
    return


@app.cell
def _(
    ann,
    comparison_plane,
    e1,
    e2,
    functional_full,
    gm,
    left_contraction,
    right_contraction,
):
    left_contraction_value = left_contraction(e1, comparison_plane).named("L")
    right_contraction_value = right_contraction(comparison_plane, e1).named("R")
    forbidden_right_contraction = right_contraction(e1, comparison_plane)
    forbidden_left_contraction = left_contraction(comparison_plane, e1)
    contraction_direction_checks = (
        left_contraction_value.almost_equal(e2),
        right_contraction_value.almost_equal(-e2),
        forbidden_right_contraction.almost_equal(e1.algebra.scalar(0)),
        forbidden_left_contraction.almost_equal(e1.algebra.scalar(0)),
    )
    left_contraction_view = ann.annotator(
        ann.on(
            ann.operator("left_contraction"),
            label="remove grade 1 from grade 2",
            marker="overbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.grade(1),
            label="+ direction",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )(left_contraction_value)
    right_contraction_view = ann.annotator(
        ann.on(
            ann.operator("right_contraction"),
            label="same removal, opposite order",
            marker="overbrace",
            color="#D55E00",
        ),
        ann.on(
            ann.grade(1),
            label="− direction",
            marker="underbrace",
            background="#FDE7D9",
            label_color="#A33A00",
        ),
    )(right_contraction_value)
    gm.md(t"""
    {functional_full(left_contraction_view):block}

    {functional_full(right_contraction_view):block}

    The two displayed identities and the two forbidden-direction zeros are all
    checked: **{contraction_direction_checks}**.
    """)
    return left_contraction_value, right_contraction_value


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Galaga's RGA interior products

    The canonical Cartan operation inserts a vector into a form. To define
    multivector-on-multivector insertion, one must choose how metric duality,
    operand order, and repeated insertion interact.

    Galaga's explicitly named RGA/Lengyel operations use metric Hodge duals and
    the antiwedge:

    $$
    \operatorname{left\_interior}(A,B)=A_\star\vee B,
    \qquad
    \operatorname{right\_interior}(A,B)=A\vee B^\star.
    $$

    For homogeneous operands,

    $$
    \operatorname{left\_interior}(A_r,B_s)
      =\langle B_s\widetilde{A_r}\rangle_{s-r},
      \qquad r\le s,
    $$

    $$
    \operatorname{right\_interior}(A_r,B_s)
      =\langle\widetilde{B_s}A_r\rangle_{r-s},
      \qquad r\ge s.
    $$

    These are established multivector contractions, but not the same sign
    convention as Galaga's conventional left and right contractions. The
    literature contains several such conventions; see
    [Multivector Contractions Revisited](https://arxiv.org/abs/2205.07608)
    and [Lengyel's projection construction](https://terathon.com/blog/symmetries-pga.html).
    """)
    return


@app.cell
def _(
    ann,
    antiwedge,
    comparison_plane,
    e1,
    e2,
    functional_full,
    gm,
    left_hodge_dual,
    left_interior_product,
    right_hodge_dual,
    right_interior_product,
):
    left_interior_value = left_interior_product(e1, comparison_plane).named("I_L", latex="I_L")
    right_interior_value = right_interior_product(comparison_plane, e1).named("I_R", latex="I_R")
    left_interior_construction = antiwedge(left_hodge_dual(e1), comparison_plane).named(
        "I_L^{built}", latex=r"I_L^{\mathrm{built}}"
    )
    right_interior_construction = antiwedge(comparison_plane, right_hodge_dual(e1)).named(
        "I_R^{built}", latex=r"I_R^{\mathrm{built}}"
    )
    interior_constructions_hold = (
        left_interior_value.almost_equal(left_interior_construction),
        right_interior_value.almost_equal(right_interior_construction),
        left_interior_value.almost_equal(-e2),
        right_interior_value.almost_equal(e2),
    )
    left_interior_construction_view = ann.annotator(
        ann.on(
            ann.operator("left_hodge_dual"),
            label="metric dual",
            marker="underbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.operator("antiwedge"),
            label="antiwedge",
            marker="overbrace",
            color="#6F42C1",
        ),
        ann.on(
            ann.grade(1),
            label="interior result",
            marker="underbrace",
            background="#FDE7D9",
            label_color="#A33A00",
        ),
    )(left_interior_construction)
    right_interior_construction_view = ann.annotator(
        ann.on(
            ann.operator("right_hodge_dual"),
            label="metric dual",
            marker="underbrace",
            color="#0072B2",
        ),
        ann.on(
            ann.operator("antiwedge"),
            label="antiwedge",
            marker="overbrace",
            color="#6F42C1",
        ),
        ann.on(
            ann.grade(1),
            label="interior result",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )(right_interior_construction)
    gm.md(t"""
    **Left construction:**

    {functional_full(left_interior_construction_view):block}

    **Right construction:**

    {functional_full(right_interior_construction_view):block}

    The Hodge/antiwedge definitions and the expected signs all agree:
    **{interior_constructions_hold}**.
    """)
    return left_interior_value, right_interior_value


@app.cell
def _(
    ann,
    functional_full,
    gm,
    left_contraction_value,
    left_interior_value,
    right_contraction_value,
    right_interior_value,
):
    e2_blade = left_interior_value.algebra.blade(0b010)
    contraction_interior_views = (
        ann.annotate(
            left_contraction_value,
            ann.on(ann.grade(1), label="left contraction", marker="underbrace", background="#DDEBFF"),
        ),
        ann.annotate(
            left_interior_value,
            ann.on(
                ann.grade(1),
                label="left interior",
                marker="underbrace",
                background="#FFF3CD",
                label_color="#9A6700",
            ),
            ann.on(ann.sign(e2_blade), background="#FFF3CD"),
        ),
        ann.annotate(
            right_contraction_value,
            ann.on(ann.grade(1), label="right contraction", marker="underbrace", background="#FDE7D9"),
        ),
        ann.annotate(
            right_interior_value,
            ann.on(
                ann.grade(1),
                label="right interior",
                marker="underbrace",
                background="#E3F4E8",
                label_color="#2F7D4F",
            ),
        ),
    )
    contraction_interior_signs_differ = (
        left_interior_value.almost_equal(-left_contraction_value)
        and right_interior_value.almost_equal(-right_contraction_value)
    )
    gm.md(t"""
    ## 7. Same grade reduction, different convention

    {functional_full(contraction_interior_views[0]):block}

    {functional_full(contraction_interior_views[1]):block}

    {functional_full(contraction_interior_views[2]):block}

    {functional_full(contraction_interior_views[3]):block}

    In this vector–bivector example, each RGA interior product is the negative
    of the corresponding conventional contraction:
    **{contraction_interior_signs_differ}**.

    This is why “interior product” should never be translated to a library
    function from its name alone. Check operand order, reversal, and sign
    convention.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Equal grades expose the intended pairing

    Galaga's RGA interior products are arranged so that equal-grade operands
    return the metric inner product:

    $$
    \operatorname{left\_interior}(A_r,B_r)
      =\operatorname{right\_interior}(A_r,B_r)
      =A_r\bullet B_r.
    $$

    Conventional contractions instead return the scalar part of $A_rB_r$.
    For a Euclidean bivector, those differ by a sign.
    """)
    return


@app.cell
def _(
    ann,
    comparison_plane,
    functional_full,
    gm,
    left_contraction,
    left_interior_product,
    metric_inner_product,
    right_contraction,
    right_interior_product,
):
    equal_grade_metric = metric_inner_product(comparison_plane, comparison_plane).named("G_E")
    equal_grade_left_contraction = left_contraction(comparison_plane, comparison_plane).named("L_E")
    equal_grade_right_contraction = right_contraction(comparison_plane, comparison_plane).named("R_E")
    equal_grade_left_interior = left_interior_product(comparison_plane, comparison_plane).named("I_{LE}")
    equal_grade_right_interior = right_interior_product(comparison_plane, comparison_plane).named("I_{RE}")
    equal_grade_identity_holds = (
        equal_grade_metric.almost_equal(equal_grade_left_interior)
        and equal_grade_metric.almost_equal(equal_grade_right_interior)
        and equal_grade_left_contraction.almost_equal(-equal_grade_metric)
        and equal_grade_right_contraction.almost_equal(-equal_grade_metric)
    )
    equal_grade_metric_view = ann.annotate(
        equal_grade_metric,
        ann.on(
            ann.grade(0),
            label="metric pairing",
            marker="underbrace",
            background="#DDEBFF",
            label_color="#005EA8",
        ),
    )
    equal_grade_interior_view = ann.annotate(
        equal_grade_left_interior,
        ann.on(
            ann.grade(0),
            label="same value",
            marker="underbrace",
            background="#E3F4E8",
            label_color="#2F7D4F",
        ),
    )
    equal_grade_contraction_view = ann.annotate(
        equal_grade_left_contraction,
        ann.on(
            ann.grade(0),
            label="geometric-product scalar",
            marker="underbrace",
            background="#FDE7D9",
            label_color="#A33A00",
        ),
    )
    gm.md(t"""
    {functional_full(equal_grade_metric_view):block}

    {functional_full(equal_grade_interior_view):block}

    {functional_full(equal_grade_contraction_view):block}

    Metric pairing, both interior products, and both contractions satisfy the
    stated sign relations: **{equal_grade_identity_holds}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Mixed grades are evaluated pair by pair

    Every Galaga operation below extends bilinearly: split each multivector
    into homogeneous components, apply the operation's rule to each grade
    pair, and add the surviving results.

    A mixed input therefore need not produce a homogeneous output. The
    selector below uses one reusable annotation recipe to label whichever
    grades actually appear; absent grades produce no decoration.
    """)
    return


@app.cell
def _(
    comparison_plane,
    doran_lasenby_inner,
    e1,
    e2,
    hestenes_inner,
    left_contraction,
    left_interior_product,
    metric_inner_product,
    right_contraction,
    right_interior_product,
    scalar_product,
):
    mixed_left = (1 + e1 + comparison_plane).named("M")
    mixed_right = (2 + e2 + comparison_plane).named("N")
    mixed_operations = {
        "Scalar product": (scalar_product, "S"),
        "Metric inner product": (metric_inner_product, "G"),
        "Left contraction": (left_contraction, "L"),
        "Right contraction": (right_contraction, "R"),
        "Hestenes": (hestenes_inner, "H"),
        "Doran–Lasenby": (doran_lasenby_inner, "D"),
        "Left RGA interior": (left_interior_product, "I_L"),
        "Right RGA interior": (right_interior_product, "I_R"),
    }
    mixed_results = {
        label: operation(mixed_left, mixed_right).named(symbol, latex=symbol)
        for label, (operation, symbol) in mixed_operations.items()
    }
    return mixed_left, mixed_results, mixed_right


@app.cell
def _(mo):
    operation_selector = mo.ui.dropdown(
        options=[
            "Scalar product",
            "Metric inner product",
            "Left contraction",
            "Right contraction",
            "Hestenes",
            "Doran–Lasenby",
            "Left RGA interior",
            "Right RGA interior",
        ],
        value="Doran–Lasenby",
        label="Choose a product",
    )
    return (operation_selector,)


@app.cell
def _(
    ann,
    functional_full,
    gm,
    mixed_left,
    mixed_results,
    mixed_right,
    mo,
    operation_selector,
):
    def annotate_output_grades(value):
        return ann.annotator(
            ann.on(
                ann.content("expr"),
                label="selected operation",
                marker="overbrace",
                color="#6F42C1",
            ),
            ann.on(
                ann.grade(0),
                label="grade 0",
                marker="underbrace",
                background="#ECEFF3",
                label_color="#4B5563",
                join=True,
            ),
            ann.on(
                ann.grade(1),
                label="grade 1",
                marker="underbrace",
                background="#DDEBFF",
                label_color="#005EA8",
                join=True,
            ),
            ann.on(
                ann.grade(2),
                label="grade 2",
                marker="underbrace",
                background="#FDE7D9",
                label_color="#A33A00",
                join=True,
            ),
            ann.on(
                ann.grade(3),
                label="grade 3",
                marker="underbrace",
                background="#E3F4E8",
                label_color="#2F7D4F",
                join=True,
            ),
        )(value)

    selected_mixed_result = mixed_results[operation_selector.value]
    selected_mixed_view = annotate_output_grades(selected_mixed_result)
    mo.vstack(
        [
            operation_selector,
            gm.md(t"""
            **Inputs**

            {functional_full(mixed_left):block}

            {functional_full(mixed_right):block}

            **Result**

            {functional_full(selected_mixed_view):block}
            """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Choosing the operation

    | Intent | Galaga operation |
    |---|---|
    | Pair vectors or blades using the metric | **metric_inner_product(A, B)** |
    | Extract exactly $\langle AB\rangle_0$ | **scalar_product(A, B)** |
    | Remove the left grade from the right | **left_contraction(A, B)** |
    | Remove the right grade from the left | **right_contraction(A, B)** |
    | Select $\|r-s\|$ but exclude scalar interactions | **hestenes_inner(A, B)** |
    | Select $\|r-s\|$ and retain scalar multiplication | **doran_lasenby_inner(A, B)** |
    | Follow the Hodge/antiwedge RGA convention | **left_interior_product(A, B)** or **right_interior_product(A, B)** |

    The safe translation procedure is:

    1. identify the operand grades;
    2. ask whether the result must be scalar or grade-lowering;
    3. check which side is inserted into which;
    4. check reversion and sign conventions; and
    5. only then choose the function.

    “Dot”, “inner”, “interior”, and “contraction” are not sufficient API
    specifications by themselves.
    """)
    return


if __name__ == "__main__":
    app.run()
