"""What do the three standard Clifford-algebra involutions do?"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo
    import numpy as np

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import (
        Algebra,
        Name,
        Notation,
        Presenter,
        RenderRule,
        clifford_conjugate,
        grade_involution,
        inverse,
        metric_inner_product,
        outer_product,
        presets,
        reverse,
    )

    return (
        Algebra,
        Name,
        Notation,
        Presenter,
        RenderRule,
        clifford_conjugate,
        ga,
        gm,
        grade_involution,
        inverse,
        metric_inner_product,
        mo,
        np,
        outer_product,
        presets,
        reverse,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Reversion and the Clifford involutions

    An **involution** is an operation that undoes itself:

    $$f(f(A))=A.$$

    Ordinary negation is a familiar example:

    $$N(A)=-A, \qquad N(N(A))=A.$$

    As a map of the underlying vector space, negation is an involution. It is
    not, however, a unital algebra automorphism or anti-automorphism:

    $$N(AB)=-AB, \qquad N(A)N(B)=(-A)(-B)=AB.$$

    Multivectors have exterior grades and a geometric product, which provide
    three additional canonical, grade-sensitive involutions that respect the
    product as either an automorphism or an anti-automorphism:

    | Operation | Vector $v$ | Product $AB$ | Grade-$k$ sign |
    |---|---:|---|---:|
    | Grade involution $\widehat{A}$ | $-v$ | $\widehat A\,\widehat B$ | $(-1)^k$ |
    | Reversion $\widetilde{A}$ | $v$ | $\widetilde B\,\widetilde A$ | $(-1)^{k(k-1)/2}$ |
    | Clifford conjugation $\overline{A}$ | $-v$ | $\overline B\,\overline A$ | $(-1)^{k(k+1)/2}$ |

    Grade involution is an **automorphism**: it preserves product order.
    Reversion and Clifford conjugation are **anti-automorphisms**: they reverse
    product order. Unlike uniform negation, they flip selected grades according
    to the patterns in the table. We begin with reversion because its name
    describes its defining action.

    Multiplicative inversion is also self-inverse wherever it is defined, but
    it is a different kind of operation: it is partial, nonlinear, and not a
    grade-sign map. We will separate it from reversion below.

    ## Reversion: reverse the factor order

    Reversion **reverses the order of the vector factors**:

    $$\widetilde{v_1 v_2} = \tilde v_2\,\tilde v_1 = v_2 v_1.$$

    There is no automatic minus sign. A sign appears only when orthogonal
    vectors are commuted past one another, and that is a property of the
    geometric product itself. This notebook uses annotation highlights to
    separate what reversion keeps from what it flips.
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(0, 180, step=1, value=55, label="angle between v₁ and v₂ (degrees)")
    return (angle,)


@app.cell
def _(Algebra, angle, np):
    algebra = Algebra(3, expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    theta = np.radians(angle.value)
    v1 = e1.named("v_1")
    v2 = (np.cos(theta) * e1 + np.sin(theta) * e2).named("v_2")
    R = (v1 * v2).named("R")
    a = (0.7 * e1 + 0.4 * e2).named("a")
    return R, a, e1, e2, e3, v1, v2


@app.cell
def _(Name, Notation, Presenter, RenderRule):
    dot_notation = Notation.default().with_rule(
        "metric_inner_product",
        RenderRule("infix", symbol=Name(".", "·", r"\cdot"), precedence=40, associativity="left"),
    )
    value_presenter = Presenter(content="value")
    expression_presenter = Presenter(content="expr")
    full_presenter = Presenter(content="full")
    dot_presenter = Presenter(notation=dot_notation, content="expr")
    return dot_presenter, expression_presenter, full_presenter, value_presenter


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reversion reverses the factors

    For vectors, reversion is the identity: $\tilde v_1 = v_1$ and
    $\tilde v_2 = v_2$. So $\widetilde{v_1 v_2}$ simply swaps the two factors.
    """)
    return


@app.cell
def _(R, expression_presenter, ga, gm, v1, v2):
    factor_R_view = ga.annotate(v1 * v2, label="R", marker="underbrace", color="#0072B2", label_color="#0072B2")
    factor_reverse_view = ga.annotate(
        v2 * v1,
        label_latex=r"\widetilde R",
        marker="underbrace",
        color="#D55E00",
        label_color="#D55E00",
    )
    factors_swapped = (~R).almost_equal(v2 * v1)
    gm.md(t"""
    **The two factors, bracketed:**

    {expression_presenter(factor_R_view):block}

    {expression_presenter(factor_reverse_view):block}

    They are the same object, so the reverse is the swapped product:
    **{factors_swapped}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### One, two, and three vector factors

    Reversion inserts no sign of its own. It writes a vector product in the
    opposite order. Signs then arise when orthogonal vectors are commuted back
    to the original order:

    $$
    \widetilde{e_1}=e_1,
    \qquad
    \widetilde{e_1e_2}=e_2e_1=-e_1e_2,
    \qquad
    \widetilde{e_1e_2e_3}=e_3e_2e_1=-e_1e_2e_3.
    $$

    The bivector requires one swap; the trivector requires three. Both counts
    are odd, so both signs are negative. Four factors require six swaps, so
    grade 4 is positive again.
    """)
    return


@app.cell
def _(e1, e2, e3, full_presenter, gm, reverse):
    simple_vector = e1.named("V_1", latex="V_1")
    simple_bivector = (e1 * e2).named("B_2", latex="B_2")
    simple_trivector = (e1 * e2 * e3).named("T_3", latex="T_3")
    simple_vector_reverse = reverse(simple_vector).named(r"\widetilde{V_1}", latex=r"\widetilde{V_1}")
    simple_bivector_reverse = reverse(simple_bivector).named(r"\widetilde{B_2}", latex=r"\widetilde{B_2}")
    simple_trivector_reverse = reverse(simple_trivector).named(r"\widetilde{T_3}", latex=r"\widetilde{T_3}")
    simple_reverse_checks = (
        simple_vector_reverse.almost_equal(simple_vector),
        simple_bivector_reverse.almost_equal(-simple_bivector),
        simple_trivector_reverse.almost_equal(-simple_trivector),
    )
    gm.md(t"""
    Galaga computes those three cases as:

    {full_presenter(simple_vector_reverse):block}

    {full_presenter(simple_bivector_reverse):block}

    {full_presenter(simple_trivector_reverse):block}

    The computed signs are respectively $+$, $-$, and $-$:
    **{simple_reverse_checks}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## No automatic minus sign

    Write out the product of two vectors. The symmetric part is the scalar
    product; the antisymmetric part is the outer product.

    $$v_1 v_2 = v_1\cdot v_2 + v_1\wedge v_2, \qquad
      v_2 v_1 = v_1\cdot v_2 - v_1\wedge v_2.$$

    Reversion reaches $v_2 v_1$ without ever inserting a sign: the scalar part
    is untouched and the bivector part is the same term written in the other
    order.
    """)
    return


@app.cell
def _(R, dot_presenter, ga, gm, metric_inner_product, outer_product, v1, v2):
    product_split = metric_inner_product(v1, v2) + outer_product(v1, v2)
    product_split_view = ga.annotator(
        ga.on(
            ga.operand(0),
            label="unchanged by reverse",
            marker="rule",
            color="#0072B2",
            label_color="#0072B2",
        ),
        ga.on(ga.operand(1), label="changes sign", marker="rule", color="#D55E00", label_color="#D55E00"),
    )(product_split)
    swapped_split = metric_inner_product(v1, v2) - outer_product(v1, v2)
    swapped_split_view = ga.annotator(
        ga.on(ga.operand(0), label="unchanged", marker="rule", color="#0072B2", label_color="#0072B2"),
        ga.on(ga.operand(1), label="reversed", marker="rule", color="#D55E00", label_color="#D55E00"),
    )(swapped_split)
    split_matches_R = product_split.almost_equal(R)
    gm.md(t"""
    **The product splits into independent scalar and bivector parts:**

    {dot_presenter(product_split_view):block}

    **The swapped product keeps the scalar and flips the bivector:**

    {dot_presenter(swapped_split_view):block}

    The first row reproduces $R$: **{split_matches_R}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reverse is not negation

    Negating $R$ flips **both** the scalar and the bivector. Reversion flips
    **only** the bivector. Watch the two labelled parts below.
    """)
    return


@app.cell
def _(R, ga, gm, value_presenter):
    def graded(value, scalar_label, bivector_label):
        return ga.annotator(
            ga.on(ga.grade(0), label=scalar_label,  color="#0072B2", label_color="#0072B2", side="below"),
            ga.on(ga.grade(2), label=bivector_label,  color="#D55E00", label_color="#D55E00", side="below"),
        )(value)

    negated_view = graded(-R, "negated", "negated")
    reverse_value_view = graded(~R, "unchanged", "negated")
    gm.md(t"""
    **Negation flips both parts:** {value_presenter(negated_view):block}

    **Reversion flips only the bivector:** {value_presenter(reverse_value_view):block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## They agree only for orthogonal vectors

    Move the slider. When $v_1\cdot v_2 = 0$ the product is a pure bivector,
    and only then does reversing it equal negating it.
    """)
    return


@app.cell
def _(R, angle, gm, metric_inner_product, v1, v2):
    inner_product = metric_inner_product(v1, v2)
    reverse_is_negation = (~R).almost_equal(-R)
    verdict = "the vectors are orthogonal" if reverse_is_negation else "the vectors are not orthogonal"
    gm.md(t"""
    **Angle:** {angle.value}°

    **Scalar product $v_1 \\cdot v_2$:** {inner_product:value}

    **Reverse equals negation here?** **{reverse_is_negation}** ({verdict}).

    A pure bivector has no scalar part to keep, so there is nothing left for
    reversion to leave alone.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why this is exactly the two-reflection formula

    A rotor built from two unit vectors is $R = v_1 v_2$, and its sandwich
    leaves vectors alone up to the rotation it generates. The reverse does the
    return trip, because the two factors cancel in pairs:
    """)
    return


@app.cell
def _(R, a, expression_presenter, ga, gm):
    explicit_sandwich = R * a * ~R
    two_reflections_view = ga.annotator(
        ga.on(ga.variable("R", occurrence=0), label="R", marker="underbrace", color="#0072B2", label_color="#0072B2"),
        ga.on(
            ga.subexpression(~R),
            label_latex=r"\widetilde R",
            marker="underbrace",
            color="#D55E00",
            label_color="#D55E00",
        ),
    )(explicit_sandwich)
    unit_rotor_reverse_product = (R * ~R).almost_equal(R.algebra.scalar(1.0))
    gm.md(t"""
    **The rotor and its reverse, bracketed:**

    {expression_presenter(two_reflections_view):block}

    The rotor times its reverse is the unit scalar:
    **{unit_rotor_reverse_product}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reciprocal is a different involution

    The multiplicative inverse—also called the **reciprocal**—is defined by

    $$AA^{-1}=A^{-1}A=1.$$

    Wherever it exists, applying it twice returns the original element:

    $$(A^{-1})^{-1}=A.$$

    So inversion is an involution on the set of invertible multivectors, or
    **units**. It also reverses products,

    $$(AB)^{-1}=B^{-1}A^{-1},$$

    but it is not one of the three linear, grade-sensitive Clifford
    involutions. Inversion is nonlinear and is simply undefined for a
    non-invertible element.

    For the unit rotor above, the computed identity
    $R\widetilde R=1$ implies the special coincidence
    $R^{-1}=\widetilde R$. The equality is a consequence of normalization,
    not the definition of reversion. Scaling the same rotor immediately
    separates the two operations.
    """)
    return


@app.cell
def _(Algebra, R, inverse, presets, reverse):
    scaled_rotor = (2 * R).named("S")
    scaled_rotor_reverse = reverse(scaled_rotor).named(
        r"\widetilde S",
        latex=r"\widetilde S",
    )
    scaled_rotor_inverse = inverse(scaled_rotor).named(
        "S_inverse",
        latex=r"S^{-1}",
    )
    scaled_reverse_differs_from_inverse = not scaled_rotor_reverse.almost_equal(
        scaled_rotor_inverse
    )
    inverse_round_trip = inverse(inverse(scaled_rotor)).almost_equal(scaled_rotor)

    inverse_pga = Algebra(config=presets.pga(2), expr=True)
    inverse_pga_e1, inverse_pga_e2, inverse_pga_e0 = inverse_pga.basis_vectors(
        expr=True
    )
    pga_unit = (1 + 2 * inverse_pga_e0).named("U")
    pga_unit_inverse = inverse(pga_unit).named(
        "U_inverse",
        latex=r"U^{-1}",
    )
    pga_unit_inverse_is_expected = pga_unit_inverse.almost_equal(
        1 - 2 * inverse_pga_e0
    )
    pga_inverse_round_trip = inverse(pga_unit_inverse).almost_equal(pga_unit)
    pga_unit_product_is_one = (pga_unit * pga_unit_inverse).almost_equal(
        inverse_pga.identity
    )
    try:
        inverse(inverse_pga_e0)
    except ValueError as error:
        pga_null_inverse_error = str(error)
    else:
        raise AssertionError("PGA's null basis vector must not be invertible")
    return (
        inverse_round_trip,
        pga_inverse_round_trip,
        pga_null_inverse_error,
        pga_unit,
        pga_unit_inverse,
        pga_unit_inverse_is_expected,
        pga_unit_product_is_one,
        scaled_reverse_differs_from_inverse,
        scaled_rotor_inverse,
        scaled_rotor_reverse,
    )


@app.cell
def _(
    full_presenter,
    gm,
    inverse_round_trip,
    pga_inverse_round_trip,
    pga_null_inverse_error,
    pga_unit,
    pga_unit_inverse,
    pga_unit_inverse_is_expected,
    pga_unit_product_is_one,
    scaled_reverse_differs_from_inverse,
    scaled_rotor_inverse,
    scaled_rotor_reverse,
):
    gm.md(rt"""
    For the scaled rotor $S=2R$, Galaga computes different values:

    {full_presenter(scaled_rotor_reverse):block}

    {full_presenter(scaled_rotor_inverse):block}

    They differ: **{scaled_reverse_differs_from_inverse}**. Inverting twice
    nevertheless returns $S$: **{inverse_round_trip}**.

    Metric degeneracy does not prevent an algebra from having units. In
    two-dimensional PGA, $e_0^2=0$, so

    $$U=1+2e_0,\qquad U^{-1}=1-2e_0.$$

    Galaga computes

    {full_presenter(pga_unit):block}

    {full_presenter(pga_unit_inverse):block}

    The displayed formula is correct: **{pga_unit_inverse_is_expected}**;
    $UU^{{-1}}=1$: **{pga_unit_product_is_one}**; and inversion still makes a
    round trip: **{pga_inverse_round_trip}**.

    The null vector $e_0$ itself has no reciprocal—Galaga reports:
    `{pga_null_inverse_error}`. Degeneracy therefore changes which elements
    are invertible; it does not invalidate inversion for every element.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Higher grades: the sign becomes a grade pattern

    Reversing $k$ vector factors requires
    $\binom{k}{2}=k(k-1)/2$ pair swaps. For a simple $k$-blade made from
    mutually orthogonal vectors, every swap contributes a minus sign:

    $$
    \widetilde{a_1a_2\cdots a_k}
      =a_k\cdots a_2a_1
      =(-1)^{k(k-1)/2}a_1a_2\cdots a_k.
    $$

    By linearity, the same sign applies to every grade-$k$ component, simple
    or not. In $\mathrm{Cl}(6)$ the pattern is:

    | grade $k$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
    |---|---|---|---|---|---|---|---|
    | reverse sign | $+$ | $+$ | $-$ | $-$ | $+$ | $+$ | $-$ |

    Grades 2, 3 and 6 flip; grades 0, 1, 4 and 5 are kept. The six-vector
    pseudoscalar is a high-grade case that flips.
    """)
    return


@app.cell
def _(Algebra, clifford_conjugate, grade_involution, np, reverse):
    high_algebra = Algebra(6, expr=True)
    high_grades = {grade: (1 << grade) - 1 for grade in range(7)}
    high_data = np.zeros(high_algebra.dim)
    for _grade, _mask in high_grades.items():
        high_data[_mask] = 1.0 + 0.3 * _grade
    M = high_algebra.multivector(high_data, expr=False).named("M")
    reverse_M = reverse(M).named(r"\widetilde{M}", latex=r"\widetilde{M}")
    grade_involuted_M = grade_involution(M).named(r"\widehat{M}", latex=r"\widehat{M}")
    clifford_conjugated_M = clifford_conjugate(M).named(r"\overline{M}", latex=r"\overline{M}")

    def computed_grade_signs(operation):
        signs = []
        for _grade, _mask in high_grades.items():
            _blade = high_algebra.blade(_mask, expr=False)
            _result = operation(_blade)
            if _result.almost_equal(_blade):
                signs.append(1)
            elif _result.almost_equal(-_blade):
                signs.append(-1)
            else:
                raise AssertionError(f"involution did not preserve grade {_grade}")
        return tuple(signs)

    reverse_grade_signs = computed_grade_signs(reverse)
    grade_involution_grade_signs = computed_grade_signs(grade_involution)
    clifford_conjugate_grade_signs = computed_grade_signs(clifford_conjugate)
    expected_sign_patterns = {
        "grade involution": tuple((-1) ** grade for grade in range(7)),
        "reversion": tuple((-1) ** (grade * (grade - 1) // 2) for grade in range(7)),
        "Clifford conjugation": tuple((-1) ** (grade * (grade + 1) // 2) for grade in range(7)),
    }
    sign_formulas_match = (
        grade_involution_grade_signs == expected_sign_patterns["grade involution"]
        and reverse_grade_signs == expected_sign_patterns["reversion"]
        and clifford_conjugate_grade_signs == expected_sign_patterns["Clifford conjugation"]
    )

    kept_grades = tuple(grade for grade, sign in enumerate(reverse_grade_signs) if sign > 0)
    flipped_grades = tuple(grade for grade, sign in enumerate(reverse_grade_signs) if sign < 0)
    expected_reverse = sum(
        (
            (1.0 if grade in kept_grades else -1.0) * (1.0 + 0.3 * grade) * high_algebra.blade(mask, expr=False)
            for grade, mask in high_grades.items()
        ),
        start=high_algebra.scalar(0.0),
    )
    grade_signs_match = reverse(M).almost_equal(expected_reverse)

    N = (
        0.25 * high_algebra.identity
        + 0.7 * high_algebra.blade(0b000010, expr=False)
        - 0.3 * high_algebra.blade(0b001100, expr=False)
        + 0.2 * high_algebra.blade(0b110001, expr=False)
    ).named("N")
    reverse_product_law = reverse(M * N).almost_equal(reverse(N) * reverse(M))
    reverse_is_not_plain_factor_swap = not reverse(M * N).almost_equal(N * M)
    grade_involution_product_law = grade_involution(M * N).almost_equal(grade_involution(M) * grade_involution(N))
    clifford_conjugate_product_law = clifford_conjugate(M * N).almost_equal(
        clifford_conjugate(N) * clifford_conjugate(M)
    )
    involution_round_trips = {
        "grade involution": grade_involution(grade_involution(M)).almost_equal(M),
        "reversion": reverse(reverse(M)).almost_equal(M),
        "Clifford conjugation": clifford_conjugate(clifford_conjugate(M)).almost_equal(M),
    }
    conjugation_is_composition = clifford_conjugate(M).almost_equal(grade_involution(reverse(M))) and clifford_conjugate(
        M
    ).almost_equal(reverse(grade_involution(M)))
    return (
        M,
        clifford_conjugate_grade_signs,
        clifford_conjugate_product_law,
        clifford_conjugated_M,
        conjugation_is_composition,
        flipped_grades,
        grade_involuted_M,
        grade_involution_grade_signs,
        grade_involution_product_law,
        grade_signs_match,
        high_algebra,
        high_grades,
        involution_round_trips,
        reverse_M,
        reverse_is_not_plain_factor_swap,
        reverse_product_law,
        sign_formulas_match,
    )


@app.cell
def _(
    M,
    flipped_grades,
    full_presenter,
    ga,
    gm,
    grade_signs_match,
    high_algebra,
    high_grades,
    reverse_M,
):
    def grade_pattern_highlights(value, flipped, *, background, colour):
        run_starts = []
        previous = None
        for grade in flipped:
            if previous is None or grade != previous + 1:
                run_starts.append(grade)
            previous = grade
        rules = [
            ga.on(ga.grades(*flipped), background=background, color=colour, join=True),
            ga.on(
                ga.signs(*(high_algebra.blade(high_grades[grade], expr=False) for grade in run_starts)),
                background=background,
            ),
        ]
        for grade in range(7):
            label_colour = colour if grade in flipped else "#0072B2"
            rules.append(
                ga.on(
                    ga.grade(grade),
                    label=f"grade {grade}",
                    marker="rule",
                    label_color=label_colour,
                    join=True, side="below"
                )
            )
        return ga.annotator(*rules)(value)

    highlighted_reverse = grade_pattern_highlights(
        reverse_M,
        flipped_grades,
        background="#FDE7D9",
        colour="#D55E00",
    )
    gm.md(t"""
    **Original — nothing is highlighted:**

    {full_presenter(M):block}

    **Reversed — the flipped grades are filled (joined) and every grade is
    labelled:**

    {full_presenter(highlighted_reverse):block}

    Reversing applies exactly that sign to each grade: **{grade_signs_match}**.
    """)
    return (grade_pattern_highlights,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The general rule is an anti-automorphism

    The familiar identity $\widetilde{ab}=ba$ is special to vectors because
    $\tilde a=a$ and $\tilde b=b$. For arbitrary multivectors $A$ and $B$,
    the correct law is

    $$\widetilde{AB}=\widetilde B\,\widetilde A,$$

    not generally $BA$. Reversion reverses the two factors **and** reverses
    whatever vector products are hidden inside each factor. That reversal of
    multiplication order is what makes it an anti-automorphism.
    """)
    return


@app.cell
def _(gm, reverse_is_not_plain_factor_swap, reverse_product_law):
    gm.md(t"""
    With the mixed-grade $M$ above and a second mixed-grade multivector $N$,
    Galaga verifies

    $$\\widetilde{{MN}}=\\widetilde N\\,\\widetilde M: \\quad
    \\text{{{reverse_product_law!s}}}.$$

    It also verifies that $\\widetilde{{MN}}\\ne NM$ for this example:
    **{reverse_is_not_plain_factor_swap}**. The vector-only shorthand must not
    be promoted to a rule for general multivectors.
    """)
    return


@app.cell
def _(gm, high_algebra):
    pseudoscalar = high_algebra.I.named("I", latex="I")
    pseudoscalar_flips = (~pseudoscalar).almost_equal(-pseudoscalar)
    gm.md(t"""
    The six-vector pseudoscalar has grade 6, which flips, so its reverse is its
    negation: **{pseudoscalar_flips}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Grade involution: distinguish even and odd parity

    Grade involution negates every vector and preserves multiplication order:

    $$
    \widehat v=-v,
    \qquad
    \widehat{AB}=\widehat A\,\widehat B.
    $$

    A product of $k$ vectors therefore collects $k$ minus signs:

    $$\widehat{A_k}=(-1)^k A_k.$$

    So a vector and trivector flip, while a bivector is kept:

    $$
    \widehat{e_1}=-e_1,
    \qquad
    \widehat{e_1e_2}=e_1e_2,
    \qquad
    \widehat{e_1e_2e_3}=-e_1e_2e_3.
    $$

    **Why use it?** It is the algebra's parity operation. Its fixed part is the
    even subalgebra; comparing $A$ with $\widehat A$ separates the even and odd
    parts. Because it preserves product order, parity composes exactly as one
    expects under the geometric product.
    """)
    return


@app.cell
def _(
    full_presenter,
    gm,
    grade_involuted_M,
    grade_involution_grade_signs,
    grade_involution_product_law,
    grade_pattern_highlights,
):
    grade_involution_flipped_grades = tuple(
        grade for grade, sign in enumerate(grade_involution_grade_signs) if sign < 0
    )
    highlighted_grade_involution = grade_pattern_highlights(
        grade_involuted_M,
        grade_involution_flipped_grades,
        background="#FFF3CD",
        colour="#9A6700",
    )
    grade_involution_pattern_matches = grade_involution_grade_signs == (1, -1, 1, -1, 1, -1, 1)
    gm.md(t"""
    **Grade-involuted — every odd grade is filled and every grade is labelled:**

    {full_presenter(highlighted_grade_involution):block}

    The Cl(6) sign pattern is $+,-,+,-,+,-,+$:
    **{grade_involution_pattern_matches}**.

    The mixed-grade product obeys
    $\\widehat{{MN}}=\\widehat M\\,\\widehat N$ without swapping $M$ and $N$:
    **{grade_involution_product_law}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Clifford conjugation: negate vectors and reverse products

    Clifford conjugation combines grade involution with reversion. The two
    operations commute, so either order gives the same result:

    $$
    \overline A =\widehat{\widetilde A} =\widetilde{\widehat A}.
    $$

    It negates vectors like grade involution, but reverses multiplication order
    like reversion:

    $$
    \overline v=-v,
    \qquad
    \overline{AB}=\overline B\,\overline A.
    $$

    Combining the two grade signs gives

    $$\overline{A_k}=(-1)^{k(k+1)/2}A_k.$$

    Thus the first three non-scalar examples are

    $$
    \overline{e_1}=-e_1,
    \qquad
    \overline{e_1e_2}=-e_1e_2,
    \qquad
    \overline{e_1e_2e_3}=e_1e_2e_3.
    $$

    **Why use it?** It is the closest Clifford-algebra analogue of ordinary
    conjugation: it combines parity reversal with order reversal. Products
    such as $A\overline A$ are therefore useful in norm and inverse formulas
    when the relevant algebraic element makes that product scalar. For a
    completely general mixed multivector, scalarity is not automatic.
    """)
    return


@app.cell
def _(
    clifford_conjugate_grade_signs,
    clifford_conjugate_product_law,
    clifford_conjugated_M,
    conjugation_is_composition,
    full_presenter,
    gm,
    grade_pattern_highlights,
):
    clifford_conjugate_flipped_grades = tuple(
        grade for grade, sign in enumerate(clifford_conjugate_grade_signs) if sign < 0
    )
    highlighted_clifford_conjugate = grade_pattern_highlights(
        clifford_conjugated_M,
        clifford_conjugate_flipped_grades,
        background="#E8DDF5",
        colour="#6F42C1",
    )
    clifford_conjugate_pattern_matches = clifford_conjugate_grade_signs == (1, -1, -1, 1, 1, -1, -1)
    gm.md(t"""
    **Clifford-conjugated — grades 1, 2, 5, and 6 are filled:**

    {full_presenter(highlighted_clifford_conjugate):block}

    The Cl(6) sign pattern is $+,-,-,+,+,-,-$:
    **{clifford_conjugate_pattern_matches}**.

    Both the composition identity and the anti-automorphism law are computed,
    not assumed:

    - $\\overline M=\\widehat{{\\widetilde M}}=\\widetilde{{\\widehat M}}$:
      **{conjugation_is_composition}**.
    - $\\overline{{MN}}=\\overline N\\,\\overline M$:
      **{clifford_conjugate_product_law}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Compare the three patterns in Cl(6)

    | grade $k$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
    |---|---:|---:|---:|---:|---:|---:|---:|
    | Grade involution | $+$ | $-$ | $+$ | $-$ | $+$ | $-$ | $+$ |
    | Reversion | $+$ | $+$ | $-$ | $-$ | $+$ | $+$ | $-$ |
    | Clifford conjugation | $+$ | $-$ | $-$ | $+$ | $+$ | $-$ | $-$ |

    The patterns repeat every two grades for grade involution and every four
    grades for the two order-reversing involutions. The Cl(6) example makes
    that wider pattern visible while the vector, bivector, and trivector cases
    explain where it comes from.
    """)
    return


@app.cell
def _(gm, involution_round_trips, sign_formulas_match):
    all_round_trips = all(involution_round_trips.values())
    gm.md(t"""
    The algebra independently confirms every formula in the table:
    **{sign_formulas_match}**.

    Applying each operation twice returns the original mixed-grade $M$:
    **{all_round_trips}**.

    That last self-inverse property is precisely what the word *involution*
    means. Preserving or reversing product order is an additional property,
    not part of the definition of an involution itself.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - An involution is self-inverse. Familiar negation qualifies in that broad
      sense, but it does not preserve the unit or respect geometric products as
      an automorphism or anti-automorphism.
    - Grade involution, reversion, and Clifford conjugation are the three
      canonical grade-sensitive involutions considered here. They all return
      $A$ when applied twice and also respect the product structure.
    - Grade involution negates vectors and preserves product order. It detects
      even/odd parity and contributes the grade sign $(-1)^k$.
    - Reversion fixes vectors and reverses product order. For vectors,
      $\widetilde{v_1 v_2}=v_2v_1$; for arbitrary multivectors the full rule is
      $\widetilde{AB}=\widetilde B\,\widetilde A$.
    - The geometric product splits into a symmetric scalar part and an
      antisymmetric bivector part. Reversion keeps the scalar and reverses the
      bivector.
    - Negation flips both parts, so $\tilde R \ne -R$ in general. They coincide
      only when the scalar part vanishes — that is, when the vectors are
      orthogonal and $R$ is a pure bivector.
    - Inversion is a separate, partial involution on the invertible
      multivectors. It can work in a degenerate algebra even though some
      elements—especially null vectors—have no inverse.
    - A unit rotor satisfies $R\widetilde R=1$. Only under that normalization
      does its reverse coincide with its reciprocal; scaling the rotor makes
      the distinction visible.
    - Clifford conjugation combines grade involution and reversion. It negates
      vectors, reverses product order, and contributes
      $(-1)^{k(k+1)/2}$ on grade $k$.
    """)
    return


if __name__ == "__main__":
    app.run()
