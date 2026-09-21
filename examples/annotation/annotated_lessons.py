"""Annotate geometric-algebra calculations for teaching without changing them."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo

    import galaga_marimo as gm
    import galaga_annotation as ga
    from galaga import (
        Algebra,
        Symbol,
        exp,
        geometric_product,
        metric_inner_product,
        outer_product,
        presets,
        sandwich,
    )
    from galaga.expression import Call
    from galaga.cga import ConformalModel

    return (
        Algebra,
        Call,
        ConformalModel,
        Symbol,
        exp,
        ga,
        geometric_product,
        gm,
        metric_inner_product,
        mo,
        outer_product,
        presets,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Annotating a geometric-algebra calculation

    An annotation explains the **role** of a whole result, an operand, an
    operation or a multivector component. It is presentation metadata: the
    value, its expression provenance, its equality and its numeric
    coefficients do not change.

    Every label below is attached by semantic target, never by character
    offset, so annotations follow the active presenter and blade order.
    """)
    return


@app.cell
def _(Algebra, exp, outer_product, sandwich):
    algebra = Algebra(3, expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    plane = (e1 ^ e2).named("B")
    rotor = exp(-0.35 * plane).named("R")
    vector = (2 * e1 + e2).named("v")
    rotated = sandwich(rotor, vector).named("v'")
    area = outer_product(e1 + e2, e3).named("A")
    mixed = (0.5 + 2 * e1 - 3 * (e1 ^ e2)).named("C")
    return algebra, area, e1, e2, e3, mixed, plane, rotated, vector


@app.cell
def _(e1, gm, metric_inner_product, rotated):
    gm.md(t"""
    ## A calculation worth explaining

    A rotor first rotates a vector, and the metric pairing of the plane
    generator is checked for context.

    Rotation: {rotated}

    Metric pairing: {metric_inner_product(e1, e1)}

    The calculation itself is ordinary Galaga; the next cells add the
    explanatory layer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One-off annotation

    `ga.annotate(value, ...)` is the one-off spelling of a recipe. The view is
    read-only: `view.plain` is the original multivector, and arithmetic is
    deliberately unavailable on the view.
    """)
    return


@app.cell
def _(area, ga, gm):
    view_whole = ga.annotate(area, ga.on(ga.content("expr"), label="oriented area"))
    transparent = view_whole.plain is area and view_whole.plain == area
    gm.md(t"""
    _Transparent:_ {transparent}

    {view_whole:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reusable recipes

    A recipe is immutable and callable. Functional `ga.on(...)` rules and the
    fluent `.mark` / `.label` / `.highlight` builders produce the same ordered
    plan; every builder returns a new recipe.
    """)
    return


@app.cell
def _(ga, gm, mixed):
    def highlight_grade(grade, background="#fff3cd"):
        return ga.annotator(ga.on(ga.grade(grade), background=background))

    highlight_vectors = highlight_grade(1)
    view_recipe = highlight_vectors(mixed)
    view_fluent = (
        ga.annotator()
        .mark(ga.grade(2), background="#e8f5e9")
        .label("bivector\npart", target=ga.grade(2), marker="brace", color="#2f6f4f")
    )(mixed)
    gm.md(t"""
    **Functional factory:** {view_recipe:block}

    **Fluent chain:** {view_fluent:block}
    """)
    return (highlight_vectors,)


@app.cell
def _(area, ga, gm, highlight_vectors, vector):
    reused_recipe = highlight_vectors(vector)
    reused_other_algebra = ga.annotate(vector, label="reused label")
    gm.md(t"""
    **Same recipe, new value:** {reused_recipe:block}

    **Recipes still compose with one-off rules:** {reused_other_algebra:block}

    The recipe above was prepared once and applied to both a 3D vector and
    {area} without capturing a value at construction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Targets: operands and operations

    `ga.operand(n)` selects a node of the recorded expression tree.
    `ga.operator(...)` selects operation occurrences by canonical id; aliases
    such as `"op"` and `"gp"` resolve to the same identity.
    """)
    return


@app.cell
def _(area, ga, gm):
    view_operands = ga.annotator(
        ga.on(ga.operand(0), label="vector sum", side="below"),
        ga.on(ga.operator("outer_product"), label="alternating product", marker="arrow"),
    )(area)
    gm.md(t"**Operand and operator labels:** {view_operands:block}")
    return


@app.cell
def _(ga, geometric_product, gm, plane, vector):
    product_value = geometric_product(vector, plane).named("P")
    view_implicit = ga.annotator(ga.on(ga.operator("gp"), label="geometric product", marker="brace"))(
        product_value
    )
    gm.md(t"""
    Juxtaposition has no separate operator glyph, so an operator annotation
    spans the complete product occurrence:

    {view_implicit:block}
    """)
    return (product_value,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Grouping a span

    `undergroup` and `overgroup` draw group accents, visually distinct from
    braces. Here each factor of the implicit product is grouped with its role.
    """)
    return


@app.cell
def _(ga, gm, product_value):
    view_grouped = ga.annotator(
        ga.on(ga.operand(0), label="vector", marker="undergroup"),
        ga.on(ga.operand(1), label="plane", marker="overgroup"),
    )(product_value)
    gm.md(t"**Under-group and over-group annotations:** {view_grouped:block}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Targets: grades, terms and coefficients

    Value-component selectors default to the visible result side of a
    definition: `ga.grade(r)`, `ga.term(blade)`, `ga.terms(*blades)`,
    `ga.coefficient(blade)` and `ga.coefficients(*blades)`.
    """)
    return


@app.cell
def _(e1, e2, ga, gm, mixed):
    view_terms = ga.annotator(
        ga.on(ga.term(e1), color="royalblue"),
        ga.on(ga.coefficient(e1), emphasis="bold"),
        ga.on(ga.term(e1 ^ e2), background="#e8f5e9", label="bivector\nterm", side="below"),
    )(mixed)
    gm.md(t"**A vector term, its coefficient, and the bivector term:** {view_terms:block}")
    return


@app.cell
def _(e2, e3, ga, gm, mixed):
    view_selection = ga.annotator(
        ga.on(ga.grades(1, 2), border="#b8c7d9"),
        ga.on(ga.term(e2), label="e2 term", marker="overbrace"),
        ga.on(ga.term(e3), label="absent term"),
    )(mixed)
    gm.md(t"""
    **Selected grades and a named term:** {view_selection:block}

    The absent `e3` rule silently produces no decoration; strict selection is
    opt-in with `missing="error"`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Grade colouring

    A palette keyed by grade colours each grade's coefficients and blades
    together. Grades are contiguous in the default order, so `join` keeps one
    colour span per grade.
    """)
    return


@app.cell
def _(e1, e2, e3, ga, gm):
    grade_sample = (0.5 + 2 * e1 - 3 * (e1 ^ e2) + 0.4 * (e1 ^ e2 ^ e3)).named("G")
    grade_palette = {
        0: "#111827",
        1: "#0072B2",
        2: "#D55E00",
        3: "#009E73",
    }
    colour_by_grade = ga.annotator(
        *[ga.on(ga.grade(grade), color=colour, join=True) for grade, colour in grade_palette.items()]
    )
    view_grades = colour_by_grade(grade_sample)
    gm.md(t"**Grade colouring (coefficients and blades):** {view_grades:block}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Nested spans: carrier highlights and cocarrier brackets

    SPEC-015's reference diagram nests two levels of annotation: a fill covers
    a semantic term set, while a bracket covers a subset of it. We build a
    dipole (a point pair) in Lengyel's native-null CGA and derive the spans
    from the computed value rather than from hardcoded blade names.

    Carrier-line terms exclude the conformal infinity direction, and the
    cocarrier normal is the direction subset that also contains the origin.
    Flat-point terms contain infinity, and the cocarrier position is the one
    that contains the origin as well.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, ga, outer_product, presets):
    lengyel_algebra = Algebra(config=presets.lengyel_cga(), expr=True)
    lengyel_cga = ConformalModel(lengyel_algebra, expr=True)
    dipole = outer_product(
        lengyel_cga.up((0.75, 1.0, 0.0)),
        lengyel_cga.up((-0.25, 0.0, 0.2)),
    ).named("d")

    infinity_mask, _ = ga.blade_mask(lengyel_cga.infinity)
    origin_mask, _ = ga.blade_mask(lengyel_cga.origin)
    nonzero_masks = tuple(
        mask for mask in range(lengyel_algebra.dim) if dipole.coefficient(mask) != 0.0
    )
    carrier_masks = tuple(mask for mask in nonzero_masks if not mask & infinity_mask)
    direction_masks = tuple(mask for mask in carrier_masks if mask & origin_mask)
    flat_point_masks = tuple(mask for mask in nonzero_masks if mask & infinity_mask)
    position_masks = tuple(mask for mask in flat_point_masks if mask & origin_mask)
    return (
        carrier_masks,
        dipole,
        direction_masks,
        flat_point_masks,
        lengyel_algebra,
        lengyel_cga,
        position_masks,
    )


@app.cell
def _(
    carrier_masks,
    dipole,
    direction_masks,
    flat_point_masks,
    ga,
    gm,
    lengyel_algebra,
    position_masks,
):
    def terms_for(masks):
        return ga.terms(*(lengyel_algebra.blade(mask) for mask in masks))

    def lead_mask(masks):
        display_order = lengyel_algebra.presentation.display_order.masks
        return next(mask for mask in display_order if mask in masks)

    carrier_lead = lead_mask(carrier_masks)
    direction_lead = lead_mask(direction_masks)
    flat_lead = lead_mask(flat_point_masks)
    other_directions = tuple(mask for mask in direction_masks if mask != direction_lead)
    view_nested = ga.annotator(
        ga.on(terms_for(carrier_masks), background="#b8e6bf", join=True),
        ga.on(ga.term(lengyel_algebra.blade(carrier_lead)), label="carrier line", side="below"),
        ga.on(terms_for(other_directions), marker="overbracket", color="#0099cc", join=True),
        ga.on(
            ga.term(lengyel_algebra.blade(direction_lead)),
            label="cocarrier normal",
            marker="overbracket",
            color="#0099cc",
        ),
        ga.on(terms_for(flat_point_masks), background="#d8c4ee", join=True),
        ga.on(ga.term(lengyel_algebra.blade(flat_lead)), label="flat point", side="below"),
        ga.on(terms_for(position_masks), label="cocarrier position", marker="underbrace", color="#0099cc"),
    )(dipole)
    gm.md(t"**Highlighted spans with an overbracket and underbrace:** {view_nested:block}")
    return


@app.cell
def _(dipole, ga, gm, lengyel_cga):
    classified = ga.classify_cga(dipole, lengyel_cga)
    highlight_object = ga.highlight_cga(lengyel_cga)
    view_object = highlight_object(dipole)
    gm.md(t"**Object:** `{classified.kind}`.\n\n**Classifier-driven continuous spans:** {view_object:block}")
    return highlight_object, view_object


@app.cell
def _(ga, gm, highlight_object, lengyel_cga, outer_product):
    round_point_example = lengyel_cga.up((0.5, -0.75, 1.25)).named("P").without_expr()
    _circle_a = lengyel_cga.up((0.75, 1.0, 2.0))
    _circle_b = lengyel_cga.up((-0.25, 0.1, 0.2))
    _circle_c = lengyel_cga.up((0.0, 1.0, 0.0))
    _sphere_d = lengyel_cga.up((0.0, 0.0, 1.0))
    circle_example = outer_product(_circle_a, _circle_b, _circle_c).named("C").without_expr()
    sphere_example = outer_product(_circle_a, _circle_b, _circle_c, _sphere_d).named("S").without_expr()

    round_point_kind = ga.classify_cga(round_point_example, lengyel_cga)
    circle_kind = ga.classify_cga(circle_example, lengyel_cga)
    sphere_kind = ga.classify_cga(sphere_example, lengyel_cga)
    highlighted_round_point = highlight_object(round_point_example)
    highlighted_circle = highlight_object(circle_example)
    highlighted_sphere = highlight_object(sphere_example)
    component_highlight = ga.highlight_cga(lengyel_cga, decomposition="components")
    highlighted_circle_components = component_highlight(circle_example)
    gm.md(t"""
    **Round point** — `{round_point_kind.kind}`: {highlighted_round_point:block}

    **Circle incidence decomposition** — `{circle_kind.kind}`: {highlighted_circle:block}

    **Circle component-role decomposition:** {highlighted_circle_components:block}

    **Sphere through four points** — `{sphere_kind.kind}`: {highlighted_sphere:block}
    """)
    return


@app.cell
def _(mo, view_object):
    mo.md(f"""
    $$ {view_object.latex(content="value")} $$
    """)
    return


@app.cell
def _(mo):
    d_a = mo.ui.slider(-2.0,2.0,step=0.1,label="a",show_value=True)
    d_b = mo.ui.slider(-2.0,2.0,step=0.1,label="b",show_value=True)
    d_c = mo.ui.slider(-2.0,2.0,step=0.1,label="c",show_value=True)
    d_d = mo.ui.slider(-2.0,2.0,step=0.1,label="d",show_value=True)
    mo.hstack([d_a,d_b,d_c,d_d])
    return d_a, d_b, d_c, d_d


@app.cell
def _(d_a, d_b, d_c, d_d, lengyel_cga):
    _a,_b,_c,_d = d_a.value, d_b.value, d_c.value, d_d.value

    d = (lengyel_cga.up(_a, _b, 0.0) ^ lengyel_cga.up(_c, 0.0, _d)).named("d").without_expr()
    return (d,)


@app.cell
def _(d):
    d
    return


@app.cell
def _(d, highlight_object):
    highlight_object( d )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    $$ \overbracket{e_1 + e_2} $$
    """)
    return


@app.cell
def _(dipole, ga, gm, lengyel_algebra):
    position_term_rule = ga.on(
        ga.term(lengyel_algebra.blade("e45")),
        label="position term",
        marker="overbrace",
        color="#0099cc",
    )
    position_weight_rule = ga.on(
        ga.coefficient(lengyel_algebra.blade("e45")),
        label="position weight",
        marker="overbrace",
        color="#0099cc",
    )
    gm.md(t"""
    **Bracket the whole term:** {ga.annotate(dipole, position_term_rule):block}

    **Bracket only its coefficient:** {ga.annotate(dipole, position_weight_rule):block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Targets: named symbols

    `ga.variable(name)` selects recorded symbol occurrences, optionally by
    occurrence index or `"all"`. Symbols are opaque references: the renderer
    does not expand them or evaluate algebra while rendering.
    """)
    return


@app.cell
def _(Call, Symbol, algebra, ga, gm):
    x = Symbol("x")
    y = Symbol("y")
    symbolic_value = algebra.multivector(
        [0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        expr=Call("add", (x, y)),
    ).named("s")
    view_symbols = ga.annotator(
        ga.on(ga.variable("x"), label="first input"),
        ga.on(ga.variable("y"), label="second input"),
    )(symbolic_value)
    gm.md(t"**Named-symbol occurrences:** {view_symbols:block}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Styles and markers

    Colour, fill, border and emphasis are renderer-neutral styles. Markers
    choose the visual vocabulary: labels above or below, arrows, leader rules,
    braces, group braces, underlines and boxes. Multi-line labels become a
    stack; `clearance` adds outward distance without shifting the content.
    """)
    return


@app.cell
def _(e1, e2, ga, mo):
    sample = e1 + e2
    styles = {
        "Text colour": ga.annotate(sample, color="royalblue"),
        "Background": ga.annotate(sample, background="#fff3cd"),
        "Border and fill": ga.annotate(sample, border="seagreen", background="#e8f5e9"),
        "Emphasis": ga.annotate(sample, emphasis="bold"),
        "Arrow above": ga.annotate(sample, label="above", marker="arrow"),
        "Arrow below": ga.annotate(sample, label="below", marker="arrow", side="below"),
        "Brace below": ga.annotate(sample, label="underbrace", marker="brace"),
        "Brace above": ga.annotate(sample, label="overbrace", marker="overbrace"),
        "Group below": ga.annotate(sample, label="undergroup", marker="undergroup"),
        "Group above": ga.annotate(sample, label="overgroup", marker="overgroup"),
        "Box": ga.annotate(sample, label="box", marker="box"),
        "Leader rule": ga.annotate(sample, label="leader", marker="rule", side="below", clearance="0.3em"),
        "Multi-line": ga.annotate(sample, label="first line\nsecond line"),
    }
    blank_line = chr(10) + chr(10)
    style_gallery = mo.md(
        blank_line.join(f"**{name}:**{blank_line}$${view.latex()}$$" for name, view in styles.items())
    )
    style_gallery
    return


@app.cell
def _(e1, e2, ga, gm):
    view_equation_label = ga.annotate(
        e1 ^ e2,
        label_latex=r"\substack{\text{carrier line} \\ e_{1} \wedge e_{2}}",
        marker="overbrace",
        overlay=True,
        clearance="4px",
        color="#0099cc",
    )
    gm.md(t"**Equation labels, stacked over two lines:** {view_equation_label:block}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Combining annotations and avoiding collisions

    Adjacent labels on the same side are laid out approximately: estimated
    widths are compared, and a label moves to the free side when that avoids
    an overlap. Residual collisions are reported in the solved layout rather
    than hidden with renderer-specific offsets.
    """)
    return


@app.cell
def _(algebra, e1, e2, ga, gm):
    untracked = algebra.multivector([0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], expr=False)
    adjacent_view = ga.annotator(
        ga.on(ga.term(e1), label="first term"),
        ga.on(ga.term(e2), label="second term"),
    )(untracked)
    adjacent_result = adjacent_view.katex()
    adjacent_layout = "\n".join(
        f"- {label.side}: collided={label.collided}, estimated width {label.estimated_width:.1f}em"
        for label in adjacent_result.labels
    )
    gm.md(t"""
    {adjacent_view:block}

    {adjacent_layout}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Empty selections

    A valid rule may match nothing: zero, tolerance-suppressed or hidden
    terms produce no decoration and reserve no space. Opt into an error when
    a lesson requires a visible match.
    """)
    return


@app.cell
def _(e1, e2, ga, gm):
    absent_view = ga.annotator(ga.on(ga.grade(3), label="no grade three"))(e1 + e2)
    absent_labels = [rule.label for rule in absent_view.katex().missing]
    strict_rule = ga.on(ga.grade(3), label="strict", missing="error")
    strict_result = "not raised"
    try:
        ga.annotator(strict_rule)(e1 + e2).latex()
    except ga.MissingTargetError as error:
        strict_result = type(error).__name__
    gm.md(t"**Ignored empty selection:** {absent_labels}. **Opt-in error:** {strict_result}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Annotations follow the presenter

    Presenters choose notation, blade names and ordering. Annotators choose
    what to explain. The two compose: annotation targets resolve against the
    final presentation, and the captured rules survive the composition.
    """)
    return


@app.cell
def _(mo):
    presenter_choice = mo.ui.dropdown(
        ["Conventional", "Functional", "Lengyel"],
        value="Lengyel",
        label="Operation notation",
    )
    presenter_choice
    return (presenter_choice,)


@app.cell
def _(area, ga, gm, presenter_choice, presets):
    presenter_by_name = {
        "Conventional": presets.presenters.default(),
        "Functional": presets.presenters.functional(),
        "Lengyel": presets.presenters.lengyel(),
    }
    annotated_area = ga.annotate(area, label="oriented area")
    presented_area = presenter_by_name[presenter_choice.value](annotated_area)
    gm.md(t"**Same annotation, selected presentation:** {presented_area:block}")
    return (presented_area,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inspect the solved plan

    `view.katex()` returns the annotated LaTeX plus the solved label layout
    and any empty selections, which keeps lesson diagnostics testable.
    """)
    return


@app.cell
def _(presented_area):
    solved = presented_area.katex()
    solved_summary = (
        f"labels={len(solved.labels)}, "
        f"missing={len(solved.missing)}, "
        f"collisions={sum(label.collided for label in solved.labels)}"
    )
    solved_summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - Annotations are presentation metadata; values, provenance and equality
      are untouched.
    - Rules are immutable. Recipes are reusable and can be combined
      functionally or fluently.
    - Targets are semantic: whole values, expression paths, operators, named
      symbols, grades, terms and coefficients.
    - The KaTeX renderer escapes ordinary labels, confines explicit trusted
      LaTeX labels to the math element, reports empty selections, and solves
      approximate label placement without moving mathematical content.
    - Presenters and annotators compose; each keeps its own responsibility.
    """)
    return


if __name__ == "__main__":
    app.run()
