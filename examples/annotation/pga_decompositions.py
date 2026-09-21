"""Compare PGA decompositions in plane-based and point-based models."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_annotation as ann
    import galaga_marimo as gm
    from galaga import (
        Algebra,
        Presenter,
        bulk_part,
        commutator,
        complement,
        grade,
        grade_involution,
        outer_product,
        presets,
        weight_part,
    )
    from galaga.rga import RigidModel

    return (
        Algebra,
        Presenter,
        RigidModel,
        ann,
        bulk_part,
        commutator,
        complement,
        gm,
        grade,
        grade_involution,
        mo,
        np,
        outer_product,
        presets,
        weight_part,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # PGA decompositions: plane-based and point-based

    Projective geometric algebra for three-dimensional Euclidean geometry uses
    the degenerate algebra $\mathrm{Cl}(3,0,1)$. Two common interpretations
    assign different geometric meanings to the same exterior algebra:

    - **Plane-based PGA:** vectors represent planes, bivectors represent lines,
      and trivectors represent points.
    - **Point-based PGA** (Lengyel's RGA convention): vectors represent points,
      bivectors represent lines, and trivectors represent planes.

    The arithmetic coefficient arrays are the same shape, but the meanings of
    grades, products, and component families are dual. This lesson keeps four
    ideas separate:

    1. grade and even/odd decomposition;
    2. bulk and weight decomposition;
    3. the Playfair interpretation of the Euclidean/ideal split;
    4. object-specific readings such as normal/offset and direction/moment.

    The annotations identify which visible terms belong to each part; all
    reconstruction, square-zero, and closure claims are computed underneath.
    """)
    return


@app.cell
def _(Algebra, Presenter, RigidModel, np, presets):
    plane_algebra = Algebra(config=presets.pga(), expr=True)
    plane_e1, plane_e2, plane_e3, plane_e0 = plane_algebra.basis_vectors(expr=True)

    point_algebra = Algebra(config=presets.rga(), expr=True)
    point_model = RigidModel(point_algebra, expr=True)
    point_e1, point_e2, point_e3 = point_model.euclidean_basis_vectors(expr=True)
    point_e4 = point_model.projective

    pga_models_share_metric = bool(np.array_equal(plane_algebra.gram, point_algebra.gram))
    pga_models_have_distinct_semantics = plane_algebra.model.id != point_algebra.model.id
    value_presenter = Presenter(content="value")
    expression_presenter = Presenter(content="expr")
    return (
        expression_presenter,
        pga_models_have_distinct_semantics,
        pga_models_share_metric,
        plane_algebra,
        plane_e0,
        plane_e1,
        plane_e2,
        plane_e3,
        point_algebra,
        point_e1,
        point_e2,
        point_e3,
        point_e4,
        point_model,
        value_presenter,
    )


@app.cell
def _(
    gm,
    pga_models_have_distinct_semantics,
    pga_models_share_metric,
    plane_algebra,
    point_algebra,
):
    gm.md(rt"""
    ## 1. One metric, two model declarations

    Both presets have Gram matrix

    {plane_algebra.bilinear_form_table():block}

    The numeric Gram matrices agree: **{pga_models_share_metric}**. Their model
    identities remain distinct: **{pga_models_have_distinct_semantics}**.

    The plane-based preset names the radical vector $e_0$; the point-based
    preset names it $e_4$. The distinction is semantic, not a change to the
    diagonal metric. This is why a coefficient split can be shared while its
    geometric labels change.

    Point-based model: `{point_algebra.model.id}`.
    Plane-based model: `{plane_algebra.model.id}`.
    """)
    return


@app.cell
def _(ann, np):
    bulk_background = "#DCEEFF"
    bulk_colour = "#0072B2"
    weight_background = "#FDE7D9"
    weight_colour = "#D55E00"
    grade_palette = ("#E5E7EB", "#DCEEFF", "#FDE7D9", "#DDF4E7", "#E8DDF5")

    def basis_mask(vector):
        return int(np.flatnonzero(vector.data)[0])

    def selected_terms(value, masks):
        return ann.terms(*(value.algebra.blade(mask) for mask in masks))

    def partition_view(value, projective_vector, *, bulk_label, weight_label):
        projective_mask = basis_mask(projective_vector)
        masks = tuple(int(mask) for mask in np.flatnonzero(value.data))
        bulk_masks = tuple(mask for mask in masks if not mask & projective_mask)
        weight_masks = tuple(mask for mask in masks if mask & projective_mask)
        rules = []
        if bulk_masks:
            rules.append(
                ann.on(
                    selected_terms(value, bulk_masks),
                    background=bulk_background,
                    color=bulk_colour,
                    label=bulk_label,
                    marker="overbrace",
                    join=True,
                )
            )
        if weight_masks:
            rules.append(
                ann.on(
                    selected_terms(value, weight_masks),
                    background=weight_background,
                    color=weight_colour,
                    label=weight_label,
                    marker="underbrace",
                    join=True,
                )
            )
        return ann.annotator(*rules)(value)

    def grade_decomposition_view(value):
        rules = tuple(
            ann.on(
                ann.grade(grade_number),
                background=grade_palette[grade_number],
                label=f"grade {grade_number}",
                marker="underbrace",
                join=True,
            )
            for grade_number in range(value.algebra.n + 1)
        )
        return ann.annotator(*rules)(value)

    return grade_decomposition_view, partition_view


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Grade and parity: decompositions before geometry

    Every Clifford algebra has the vector-space decomposition

    $$\mathrm{Cl}(V)=\bigoplus_{k=0}^{n}\mathrm{Cl}^k(V).$$

    Collecting the even and odd grades gives

    $$X=X^+ + X^-.$$

    These decompositions do not depend on whether vectors mean points or
    planes. Grade identifies homogeneous exterior objects; parity identifies
    the even subalgebra and odd subspace. Neither decomposition uses the
    radical direction.
    """)
    return


@app.cell
def _(
    grade,
    grade_decomposition_view,
    plane_algebra,
    plane_e0,
    plane_e1,
    plane_e2,
    plane_e3,
):
    plane_e12 = plane_e1 ^ plane_e2
    plane_e23 = plane_e2 ^ plane_e3
    plane_e31 = plane_e3 ^ plane_e1
    plane_I = plane_algebra.I
    graded_value = (
        1
        + 2 * plane_e1
        - plane_e2
        + 0.5 * plane_e12
        + 0.75 * (plane_e12 ^ plane_e3)
        - 0.25 * plane_I
        + 1.5 * plane_e0
    ).named("X")
    graded_parts = tuple(grade(graded_value, grade_number) for grade_number in range(5))
    graded_reconstruction = sum(graded_parts, start=plane_algebra.scalar(0))
    grade_decomposition_holds = graded_reconstruction.almost_equal(graded_value)
    even_part = sum((graded_parts[index] for index in (0, 2, 4)), start=plane_algebra.scalar(0)).named(
        "X_even", latex=r"X^+"
    )
    odd_part = sum((graded_parts[index] for index in (1, 3)), start=plane_algebra.scalar(0)).named(
        "X_odd", latex=r"X^-"
    )
    parity_reconstruction_holds = (even_part + odd_part).almost_equal(graded_value)
    graded_value_view = grade_decomposition_view(graded_value)
    return (
        even_part,
        grade_decomposition_holds,
        graded_value_view,
        odd_part,
        parity_reconstruction_holds,
        plane_e12,
        plane_e23,
        plane_e31,
    )


@app.cell
def _(
    even_part,
    gm,
    grade_decomposition_holds,
    graded_value_view,
    odd_part,
    parity_reconstruction_holds,
    value_presenter,
):
    gm.md(rt"""
    {value_presenter(graded_value_view):block}

    The coloured grade projections reconstruct $X$:
    **{grade_decomposition_holds}**.

    The coarser parity split is

    {even_part:block}

    {odd_part:block}

    and $X=X^+ + X^-$: **{parity_reconstruction_holds}**.

    A homogeneous point, line, or plane occupies one grade. A motor/flector
    classification instead begins with parity—but expected parity alone does
    not prove that an arbitrary multivector is a valid transformation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Bulk and weight: the radical split

    Let $e_0$ span the radical in plane-based PGA and choose the standard
    complement $W=\operatorname{span}\{e_1,e_2,e_3\}$. Every multivector has a
    unique form

    $$X=A+B e_0,\qquad A,B\in\mathrm{Cl}(W).$$

    The terms in $A$ do not contain $e_0$; the terms in $Be_0$ do. Lengyel
    calls these **bulk** and **weight**. Bamberg and Saunders identify the same
    coefficient split as the standard-coordinate case of the
    **Playfair decomposition**, calling the parts Euclidean and ideal.

    The ideal is square-zero: any two elements containing the radical factor
    multiply to zero. Multiplication is consequently not a pair of independent
    Clifford products. It obeys the grade-involution twist

    $$(A+B e_0)(C+D e_0)
      =AC+\bigl(AD+B\widehat C\bigr)e_0.$$
    """)
    return


@app.cell
def _(
    bulk_part,
    grade_involution,
    partition_view,
    plane_algebra,
    plane_e0,
    plane_e1,
    plane_e12,
    plane_e2,
    plane_e23,
    weight_part,
):
    playfair_A = 1 + 2 * plane_e1 + 0.5 * plane_e12
    playfair_B = 3 - plane_e2 + 0.25 * plane_e23
    playfair_C = 2 + plane_e1 - 0.5 * plane_e23
    playfair_D = -1 + 0.75 * plane_e2
    playfair_base = playfair_A
    playfair_ideal = playfair_B * plane_e0
    second_playfair_ideal = playfair_D * plane_e0
    playfair_value = (playfair_base + playfair_ideal).named("X")
    second_playfair_value = (playfair_C + second_playfair_ideal).named("Y")
    playfair_value_view = partition_view(
        playfair_value,
        plane_e0,
        bulk_label="Euclidean: Cl(W)",
        weight_label="ideal: Cl(W)e0",
    )
    playfair_parts_reconstruct = (
        bulk_part(playfair_value) + weight_part(playfair_value)
    ).almost_equal(playfair_value)
    playfair_ideal_is_square_zero = (playfair_ideal * second_playfair_ideal).almost_equal(
        plane_algebra.scalar(0)
    )
    twisted_product_actual = playfair_value * second_playfair_value
    twisted_product_expected = playfair_A * playfair_C + (
        playfair_A * playfair_D + playfair_B * grade_involution(playfair_C)
    ) * plane_e0
    twisted_product_holds = twisted_product_actual.almost_equal(twisted_product_expected)
    twisted_bulk_product_holds = bulk_part(twisted_product_actual).almost_equal(
        playfair_A * playfair_C
    )
    return (
        playfair_ideal_is_square_zero,
        playfair_parts_reconstruct,
        playfair_value_view,
        twisted_bulk_product_holds,
        twisted_product_holds,
    )


@app.cell
def _(
    gm,
    playfair_ideal_is_square_zero,
    playfair_parts_reconstruct,
    playfair_value_view,
    twisted_bulk_product_holds,
    twisted_product_holds,
    value_presenter,
):
    gm.md(rt"""
    {value_presenter(playfair_value_view):block}

    Galaga verifies:

    - bulk plus weight reconstructs $X$: **{playfair_parts_reconstruct}**;
    - the product of two ideal parts vanishes:
      **{playfair_ideal_is_square_zero}**;
    - the grade-involution-twisted product formula holds:
      **{twisted_product_holds}**;
    - the bulk of $XY$ is just the product of the two bulk parts:
      **{twisted_bulk_product_holds}**.

    Thus the split is more than visual grouping. The ideal terms form a
    square-zero ideal, while the Euclidean terms form a copy of
    $\mathrm{{Cl}}(3)$ inside the degenerate algebra.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Playfair decomposition at a chosen point

    Plane-based PGA turns the abstract section into affine geometry. A plane

    $$g=d e_0+n_1e_1+n_2e_2+n_3e_3$$

    has equation $d+n\cdot x=0$. For a chosen point $P$, its parallel class
    contains exactly one plane through $P$:

    $$g_P=n-(n\cdot P)e_0.$$

    The Playfair decomposition is

    $$g=g_P+(g-g_P).$$

    The first term is the representative at $P$; the second is an ideal term.
    Unlike the fixed-origin bulk/weight labels, this decomposition depends on
    the selected section $V_P$.
    """)
    return


@app.cell
def _(ann, partition_view, plane_e0, plane_e1, plane_e2):
    playfair_point_coordinates = (1.0, 1.0, 0.0)
    original_plane = (plane_e1 + 2 * plane_e2 - plane_e0).named("g")
    plane_at_point = (plane_e1 + 2 * plane_e2 - 3 * plane_e0).named(
        "g_P", latex=r"g_P"
    )
    plane_at_infinity = (original_plane - plane_at_point).named(
        "g_infinity_P", latex=r"g_{\infty,P}"
    )
    playfair_sum = plane_at_point + plane_at_infinity
    playfair_at_point_view = ann.annotator(
        ann.on(
            ann.operand(0),
            background="#DCEEFF",
            color="#0072B2",
            label="parallel plane through P",
            marker="rule",
        ),
        ann.on(
            ann.operand(1),
            background="#FDE7D9",
            color="#D55E00",
            label="ideal residual",
            clearance="5px",
            marker="rule",
        ),
    )(playfair_sum)
    playfair_at_point_reconstructs = playfair_sum.almost_equal(original_plane)
    plane_at_point_incidence = bool(
        abs(-3 + playfair_point_coordinates[0] + 2 * playfair_point_coordinates[1])
        < 1e-12
    )
    playfair_parallel_normals_agree = partition_view(
        original_plane,
        plane_e0,
        bulk_label="shared normal",
        weight_label="original offset",
    )
    return (
        original_plane,
        plane_at_point_incidence,
        playfair_at_point_reconstructs,
        playfair_at_point_view,
        playfair_parallel_normals_agree,
        playfair_point_coordinates,
    )


@app.cell
def _(
    expression_presenter,
    gm,
    original_plane,
    plane_at_point_incidence,
    playfair_at_point_reconstructs,
    playfair_at_point_view,
    playfair_parallel_normals_agree,
    playfair_point_coordinates,
    value_presenter,
):
    gm.md(rt"""
    Start with {original_plane}, representing $x+2y-1=0$, and choose
    $P={playfair_point_coordinates}$. Its parallel representative through $P$
    is $x+2y-3=0$.

    {expression_presenter(playfair_at_point_view):block}

    The two terms reconstruct the original plane:
    **{playfair_at_point_reconstructs}**. Substitution confirms that the first
    plane passes through $P$: **{plane_at_point_incidence}**.

    The ordinary origin-based split remains visible on the original plane:

    {value_presenter(playfair_parallel_normals_agree):block}

    The fixed bulk projection selects the common normal. The full Playfair
    projection additionally adjusts the ideal coefficient so the selected
    representative is incident with $P$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The same bulk/weight split has dual object meanings

    Bulk always means “terms without the projective basis vector”; weight
    always means “terms containing it”. Those are algebraic definitions.
    Their geometric readings depend on whether vectors represent planes or
    points.

    For corresponding point and plane objects, the semantic roles exchange:

    | Object | Plane-based PGA | Point-based PGA |
    |---|---|---|
    | Point | bulk = homogeneous weight; ideal = position | bulk = position; weight = homogeneous weight |
    | Plane | bulk = normal; ideal = offset | bulk = offset; weight = normal |
    | Line | bulk = direction; ideal = moment | bulk = moment; weight = direction |

    The next examples annotate the actual blade families rather than relying
    on the table.
    """)
    return


@app.cell
def _(
    bulk_part,
    partition_view,
    plane_e0,
    plane_e1,
    plane_e2,
    plane_e3,
    point_e1,
    point_e2,
    point_e3,
    point_e4,
    point_model,
    weight_part,
):
    plane_e123 = plane_e1 ^ plane_e2 ^ plane_e3
    plane_e230 = plane_e2 ^ plane_e3 ^ plane_e0
    plane_e310 = plane_e3 ^ plane_e1 ^ plane_e0
    plane_e120 = plane_e1 ^ plane_e2 ^ plane_e0
    plane_based_point = (
        plane_e123 + plane_e230 + 2 * plane_e310 - plane_e120
    ).named("P")
    plane_based_plane = (plane_e1 + 2 * plane_e2 - plane_e3 - 3 * plane_e0).named(
        "g"
    )

    point_e423 = point_e4 ^ point_e2 ^ point_e3
    point_e431 = point_e4 ^ point_e3 ^ point_e1
    point_e412 = point_e4 ^ point_e1 ^ point_e2
    point_e321 = point_e3 ^ point_e2 ^ point_e1
    point_based_point = point_model.point((1, 2, -1)).named("p")
    point_based_plane = (
        point_e423 + 2 * point_e431 - point_e412 - 3 * point_e321
    ).named("g")

    plane_point_view = partition_view(
        plane_based_point,
        plane_e0,
        bulk_label="homogeneous weight",
        weight_label="position",
    )
    point_point_view = partition_view(
        point_based_point,
        point_e4,
        bulk_label="position",
        weight_label="homogeneous weight",
    )
    plane_plane_view = partition_view(
        plane_based_plane,
        plane_e0,
        bulk_label="normal",
        weight_label="offset",
    )
    point_plane_view = partition_view(
        point_based_plane,
        point_e4,
        bulk_label="offset",
        weight_label="normal",
    )
    object_bulk_weight_reconstructions = tuple(
        (bulk_part(value) + weight_part(value)).almost_equal(value)
        for value in (
            plane_based_point,
            point_based_point,
            plane_based_plane,
            point_based_plane,
        )
    )
    return (
        object_bulk_weight_reconstructions,
        plane_plane_view,
        plane_point_view,
        point_based_plane,
        point_based_point,
        point_plane_view,
        point_point_view,
    )


@app.cell
def _(
    gm,
    object_bulk_weight_reconstructions,
    plane_plane_view,
    plane_point_view,
    point_plane_view,
    point_point_view,
    value_presenter,
):
    gm.md(rt"""
    ### Points

    **Plane-based point:**

    {value_presenter(plane_point_view):block}

    **Point-based point:**

    {value_presenter(point_point_view):block}

    ### Planes

    **Plane-based plane:**

    {value_presenter(plane_plane_view):block}

    **Point-based plane:**

    {value_presenter(point_plane_view):block}

    Every displayed pair reconstructs its object from `bulk_part` plus
    `weight_part`: **{object_bulk_weight_reconstructions}**.

    “Bulk” does not universally mean position or direction. It names a
    coefficient projection; the model supplies the geometric interpretation.
    """)
    return


@app.cell
def _(
    outer_product,
    partition_view,
    plane_algebra,
    plane_e0,
    plane_e1,
    plane_e12,
    plane_e2,
    plane_e23,
    plane_e3,
    plane_e31,
    point_algebra,
    point_e1,
    point_e2,
    point_e3,
    point_e4,
):
    line_direction = (1.0, 2.0, 3.0)
    line_moment = (3.0, 0.0, -1.0)
    plane_e01 = plane_e0 ^ plane_e1
    plane_e02 = plane_e0 ^ plane_e2
    plane_e03 = plane_e0 ^ plane_e3
    plane_based_line = (
        line_direction[0] * plane_e23
        + line_direction[1] * plane_e31
        + line_direction[2] * plane_e12
        + line_moment[0] * plane_e01
        + line_moment[1] * plane_e02
        + line_moment[2] * plane_e03
    ).named("L")

    point_e23 = point_e2 ^ point_e3
    point_e31 = point_e3 ^ point_e1
    point_e12 = point_e1 ^ point_e2
    point_e41 = point_e4 ^ point_e1
    point_e42 = point_e4 ^ point_e2
    point_e43 = point_e4 ^ point_e3
    point_based_line = (
        line_direction[0] * point_e41
        + line_direction[1] * point_e42
        + line_direction[2] * point_e43
        + line_moment[0] * point_e23
        + line_moment[1] * point_e31
        + line_moment[2] * point_e12
    ).named("l")

    plane_line_view = partition_view(
        plane_based_line,
        plane_e0,
        bulk_label="direction",
        weight_label="moment",
    )
    point_line_view = partition_view(
        point_based_line,
        point_e4,
        bulk_label="moment",
        weight_label="direction",
    )
    plane_line_is_simple = outer_product(plane_based_line, plane_based_line).almost_equal(
        plane_algebra.scalar(0)
    )
    point_line_is_simple = outer_product(point_based_line, point_based_line).almost_equal(
        point_algebra.scalar(0)
    )
    plucker_constraint = sum(
        direction * moment
        for direction, moment in zip(line_direction, line_moment, strict=True)
    )
    return (
        plane_line_is_simple,
        plane_line_view,
        plucker_constraint,
        point_line_is_simple,
        point_line_view,
    )


@app.cell
def _(
    gm,
    plane_line_is_simple,
    plane_line_view,
    plucker_constraint,
    point_line_is_simple,
    point_line_view,
    value_presenter,
):
    gm.md(rt"""
    ### Lines: the Plücker direction/moment split

    **Plane-based line:**

    {value_presenter(plane_line_view):block}

    **Point-based line:**

    {value_presenter(point_line_view):block}

    The same direction and moment triples occupy complementary blade families.
    Their Plücker constraint is $d\cdot m={plucker_constraint:.1f}$. Both
    bivectors pass the simplicity test $L\wedge L=0$:
    **{plane_line_is_simple}**, **{point_line_is_simple}**.

    Direction/moment is therefore an object-specific interpretation of the
    radical split, not a new projection independent of bulk and weight.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Bivector generators: rotation and translation

    In plane-based PGA, the bivector Lie algebra inherits the split

    $$\mathrm{Cl}^2(V)=\mathrm{Cl}^2(W)\ltimes W e_0
      \cong\mathfrak{so}(3)\ltimes\mathbb R^3
      =\mathfrak{se}(3).$$

    Pure Euclidean bivectors generate rotations; ideal bivectors generate
    translations. The commutator relations have the expected semidirect form:

    $$[\mathfrak{so}(3),\mathfrak{so}(3)]\subseteq\mathfrak{so}(3),$$
    $$[\mathfrak{so}(3),\mathbb R^3]\subseteq\mathbb R^3,$$
    $$[\mathbb R^3,\mathbb R^3]=0.$$

    Point-based PGA encodes the same Euclidean motions through the complementary
    antiproduct representation. The coefficient split still exists, but one
    must not silently transfer plane-based product semantics to it.
    """)
    return


@app.cell
def _(
    bulk_part,
    commutator,
    partition_view,
    plane_algebra,
    plane_e0,
    plane_e1,
    plane_e12,
    plane_e2,
    plane_e23,
    weight_part,
):
    rotation_generator_a = plane_e12
    rotation_generator_b = plane_e23
    translation_generator_a = plane_e1 ^ plane_e0
    translation_generator_b = plane_e2 ^ plane_e0
    rigid_motion_generator = (
        0.4 * rotation_generator_a
        - 0.2 * rotation_generator_b
        + 0.7 * translation_generator_a
        + 0.3 * translation_generator_b
    ).named("B")
    rigid_motion_generator_view = partition_view(
        rigid_motion_generator,
        plane_e0,
        bulk_label="rotation: so(3)",
        weight_label="translation: R3",
    )
    rotation_rotation_bracket = commutator(rotation_generator_a, rotation_generator_b)
    rotation_translation_bracket = commutator(rotation_generator_a, translation_generator_a)
    translation_translation_bracket = commutator(
        translation_generator_a, translation_generator_b
    )
    rotation_bracket_stays_bulk = weight_part(rotation_rotation_bracket).almost_equal(
        plane_algebra.scalar(0)
    )
    mixed_bracket_stays_ideal = bulk_part(rotation_translation_bracket).almost_equal(
        plane_algebra.scalar(0)
    )
    translations_commute = translation_translation_bracket.almost_equal(
        plane_algebra.scalar(0)
    )
    return (
        mixed_bracket_stays_ideal,
        rigid_motion_generator_view,
        rotation_bracket_stays_bulk,
        translations_commute,
    )


@app.cell
def _(
    gm,
    mixed_bracket_stays_ideal,
    rigid_motion_generator_view,
    rotation_bracket_stays_bulk,
    translations_commute,
    value_presenter,
):
    gm.md(rt"""
    {value_presenter(rigid_motion_generator_view):block}

    Galaga verifies the three closure claims:

    - rotation with rotation stays rotational:
      **{rotation_bracket_stays_bulk}**;
    - rotation with translation stays translational:
      **{mixed_bracket_stays_ideal}**;
    - translation generators commute: **{translations_commute}**.

    This is the infinitesimal counterpart of splitting a motor into rotational
    and translational information. Unlike direction/moment labels, the
    semidirect-product statement also specifies how multiplication couples the
    two parts.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Complement duality is not another additive decomposition

    Complement maps occupied basis directions to absent directions. It swaps
    the point-based and plane-based grade readings:

    $$1\leftrightarrow I,\qquad
      \text{vector}\leftrightarrow\text{trivector},\qquad
      \text{bivector}\leftrightarrow\text{bivector}.$$

    This explains why points and planes exchange grades and why line
    direction/moment families exchange roles. But $X\mapsto\operatorname{comp}(X)$
    is a correspondence, not a decomposition $X=X_1+X_2$.
    """)
    return


@app.cell
def _(complement, point_based_plane, point_based_point):
    point_complement = complement(point_based_point).named(
        "comp_p", latex=r"\operatorname{comp}(p)"
    )
    plane_complement = complement(point_based_plane).named(
        "comp_g", latex=r"\operatorname{comp}(g)"
    )
    complement_swaps_point_plane_grades = (
        point_complement.homogeneous_grade() == 3
        and plane_complement.homogeneous_grade() == 1
    )
    return (
        complement_swaps_point_plane_grades,
        plane_complement,
        point_complement,
    )


@app.cell
def _(
    complement_swaps_point_plane_grades,
    gm,
    plane_complement,
    point_complement,
):
    gm.md(rt"""
    {point_complement:block}

    {plane_complement:block}

    The computed grades exchange vector and trivector:
    **{complement_swaps_point_plane_grades}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Which decomposition should a lesson use?

    | Question | Useful decomposition |
    |---|---|
    | Which exterior dimensions are present? | Grade |
    | Is the element even or odd? | Parity |
    | Which coefficients contain the radical basis vector? | Bulk/weight |
    | Which parallel representative is incident with a chosen point? | Playfair at $P$ |
    | What do a line's two triples mean? | Direction/moment reading of bulk/weight |
    | What do infinitesimal rigid-motion terms do? | $\mathfrak{so}(3)\ltimes\mathbb R^3$ |
    | How do point- and plane-based representations correspond? | Complement duality—not an additive decomposition |

    The main lesson is that a decomposition consists of projections and a
    reconstruction law. Semantic labels come afterwards. “Terms containing
    $e_0$” is stable algebraic information; whether they mean point position,
    plane offset, line moment, or translation depends on the selected model and
    object grade.

    ## Sources

    - J. Bamberg and J. Saunders,
      [*Exploiting Degeneracy in Projective Geometric Algebra*](https://link.springer.com/article/10.1007/s00006-025-01392-9),
      especially the Playfair decomposition and Theorems 3.11 and 4.4.
    - E. Lengyel,
      [*Bulk and weight*](https://www.rigidgeometricalgebra.org/wiki/index.php?title=Bulk_and_weight),
      for the metric/antimetric component families.
    - E. Lengyel,
      [*Dual Approaches to Projective Geometric Algebra*](https://terathon.com/blog/dual-pga.html),
      for the point-based and plane-based interpretations.
    - L. Dorst and S. De Keninck,
      [*A Guided Tour to the Plane-Based Geometric Algebra PGA*](https://bivector.net/PGA4CS.html),
      for the plane-based Euclidean split and geometric constructions.
    """)
    return


if __name__ == "__main__":
    app.run()
