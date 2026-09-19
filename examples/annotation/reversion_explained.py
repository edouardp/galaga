"""What does reversion do? Reverse reorders factors; the sign is not automatic."""

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
        metric_inner_product,
        outer_product,
    )

    return (
        Algebra,
        Name,
        Notation,
        Presenter,
        RenderRule,
        ga,
        gm,
        metric_inner_product,
        mo,
        np,
        outer_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What does reversion do?

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
    algebra = Algebra(2, expr=True)
    e1, e2 = algebra.basis_vectors(expr=True)
    theta = np.radians(angle.value)
    v1 = e1.named("v_1")
    v2 = (np.cos(theta) * e1 + np.sin(theta) * e2).named("v_2")
    R = (v1 * v2).named("R")
    a = (0.7 * e1 + 0.4 * e2).named("a")
    return R, a, v1, v2


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
        label_latex=r"\tilde R = R^{-1}",
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
            marker="underbrace",
            color="#0072B2",
            label_color="#0072B2",
        ),
        ga.on(ga.operand(1), label="changes sign", marker="underbrace", color="#D55E00", label_color="#D55E00"),
    )(product_split)
    swapped_split = metric_inner_product(v1, v2) - outer_product(v1, v2)
    swapped_split_view = ga.annotator(
        ga.on(ga.operand(0), label="unchanged", marker="underbrace", color="#0072B2", label_color="#0072B2"),
        ga.on(ga.operand(1), label="reversed", marker="underbrace", color="#D55E00", label_color="#D55E00"),
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
            ga.on(ga.grade(0), label=scalar_label, marker="underbrace", color="#0072B2", label_color="#0072B2"),
            ga.on(ga.grade(2), label=bivector_label, marker="underbrace", color="#D55E00", label_color="#D55E00"),
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
    inverse job, because the two factors cancel in pairs:
    """)
    return


@app.cell
def _(R, a, expression_presenter, ga, gm):
    explicit_sandwich = R * a * ~R
    two_reflections_view = ga.annotator(
        ga.on(ga.variable("R", occurrence=0), label="R", marker="underbrace", color="#0072B2", label_color="#0072B2"),
        ga.on(
            ga.subexpression(~R),
            label_latex=r"\tilde R = R^{-1}",
            marker="underbrace",
            color="#D55E00",
            label_color="#D55E00",
        ),
    )(explicit_sandwich)
    reverse_is_inverse = (R * ~R).almost_equal(R.algebra.scalar(1.0))
    gm.md(t"""
    **The rotor and its reverse, bracketed:**

    {expression_presenter(two_reflections_view):block}

    The rotor times its reverse is the unit scalar, so the reverse is the
    inverse: **{reverse_is_inverse}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Higher grades: the sign becomes a grade pattern

    The factor-order rule generalises to a grade rule. Reversing a $k$-vector
    multiplies it by $(-1)^{k(k-1)/2}$, so in $\mathrm{Cl}(6)$:

    | grade $k$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
    |---|---|---|---|---|---|---|---|
    | reverse sign | $+$ | $+$ | $-$ | $-$ | $+$ | $+$ | $-$ |

    Grades 2, 3 and 6 flip; grades 0, 1, 4 and 5 are kept. The six-vector
    pseudoscalar is a high-grade case that flips.
    """)
    return


@app.cell
def _(Algebra, np):
    high_algebra = Algebra(6, expr=True)
    high_grades = {grade: (1 << grade) - 1 for grade in range(7)}
    high_data = np.zeros(high_algebra.dim)
    for _grade, _mask in high_grades.items():
        high_data[_mask] = 1.0 + 0.3 * _grade
    M = high_algebra.multivector(high_data, expr=False).named("M")
    reverse_M = (~M).named(r"\widetilde{M}", latex=r"\widetilde{M}")
    kept_grades = tuple(grade for grade in range(7) if (-1) ** (grade * (grade - 1) // 2) > 0)
    flipped_grades = tuple(grade for grade in range(7) if (-1) ** (grade * (grade - 1) // 2) < 0)
    expected_reverse = sum(
        (
            (1.0 if grade in kept_grades else -1.0) * (1.0 + 0.3 * grade) * high_algebra.blade(mask, expr=False)
            for grade, mask in high_grades.items()
        ),
        start=high_algebra.scalar(0.0),
    )
    grade_signs_match = (~M).almost_equal(expected_reverse)
    return (
        M,
        flipped_grades,
        grade_signs_match,
        high_algebra,
        high_grades,
        reverse_M,
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
    def reverse_highlights(value):
        run_starts = []
        previous = None
        for grade in flipped_grades:
            if previous is None or grade != previous + 1:
                run_starts.append(grade)
            previous = grade
        rules = [
            ga.on(ga.grades(*flipped_grades), background="#FDE7D9", color="#D55E00", join=True),
            ga.on(
                ga.signs(*(high_algebra.blade(high_grades[grade], expr=False) for grade in run_starts)),
                background="#FDE7D9",
            ),
        ]
        for grade in range(7):
            colour = "#D55E00" if grade in flipped_grades else "#0072B2"
            rules.append(
                ga.on(
                    ga.grade(grade),
                    label=f"grade {grade}",
                    marker="underbrace",
                    label_color=colour,
                    join=True,
                )
            )
        return ga.annotator(*rules)(value)

    highlighted_reverse = reverse_highlights(reverse_M)
    gm.md(t"""
    **Original — nothing is highlighted:**

    {full_presenter(M):block}

    **Reversed — the flipped grades are filled (joined) and every grade is
    labelled:**

    {full_presenter(highlighted_reverse):block}

    Reversing applies exactly that sign to each grade: **{grade_signs_match}**.
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
    ## Takeaways

    - Reversion reverses the order of vector factors. For vectors it is the
      identity, so $\widetilde{v_1 v_2} = v_2 v_1$ with no sign inserted.
    - The geometric product splits into a symmetric scalar part and an
      antisymmetric bivector part. Reversion keeps the scalar and reverses the
      bivector.
    - Negation flips both parts, so $\tilde R \ne -R$ in general. They coincide
      only when the scalar part vanishes — that is, when the vectors are
      orthogonal and $R$ is a pure bivector.
    - For a unit rotor $R = v_1 v_2$, $R\tilde R = 1$, which is why the
      reverse is the inverse needed by the sandwich $\widetilde{R}\,a\,R$.
    """)
    return


if __name__ == "__main__":
    app.run()
