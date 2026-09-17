# galaga-annotation

Semantic annotations and KaTeX rendering for
[galaga](https://github.com/edouardp/galaga) calculations.

Annotations are presentation metadata: they never change numerical values,
expression evaluation, equality or hashing. The package is optional; importing
`galaga` never imports `galaga_annotation`.

- [Package source](https://github.com/edouardp/galaga/tree/galaga_v2/packages/galaga_annotation)
- [SPEC-015: Expression and Matrix Annotations](https://github.com/edouardp/galaga/blob/galaga_v2/docs/specs/SPEC-015-expression-and-matrix-annotations.md)
- [ADR-142: Reusable Callable Annotators](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/142-reusable-callable-annotators.md)
- [ADR-147: KaTeX Annotation Lowering](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/147-katex-annotation-lowering-and-decoration-wrappers.md)
- [ADR-148: CGA Object Classification](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/148-cga-object-classification-and-highlight-recipes.md)

## Quick start

```python
from galaga import Algebra, outer_product

import galaga_annotation as ga

algebra = Algebra(3, expr=True)
e1, e2, e3 = algebra.basis_vectors(expr=True)
area = outer_product(e1 + e2, e3).named("A")

view = ga.annotate(area, label="oriented area")
assert r"\overset{\text{oriented area}}" in view.latex()
assert view.plain is area
```

`ga.annotate(value, ...)` is the one-off spelling of
`ga.annotator(ga.on(...))(value)`. Annotated views are rendering-only: use
`view.plain` or `view.value` for further calculations.

## Reusable recipes

```python
def highlight_grade(grade):
    return ga.annotator(ga.on(ga.grade(grade), background="#fff3cd"))


value = (0.5 + 2 * e1 - 3 * (e1 ^ e2)).named("C")
rendered = highlight_grade(1)(value).latex()
assert r"\colorbox{#fff3cd}{$2 e_{1}$}" in rendered
```

Recipes are immutable and reusable. Fluent builders such as
`.highlight(...)`, `.label(...)` and `.mark(...)` return new recipes and
produce the same ordered plan as the functional `ga.on(...)` spelling.

## Annotating operations and operands

```python
lesson = ga.annotator(
    ga.on(ga.operand(0), label="vector sum", side="below"),
    ga.on(ga.operator("outer_product"), label="alternating product", marker="arrow"),
)
rendered = lesson(area).latex()
assert r"\underset{\text{vector sum}}" in rendered
assert r"\overset{\substack{\text{alternating product} \\ \downarrow}}" in rendered
```

Operator targets use the displayed glyph or function name when one exists.
For notation with an implicit operator, such as geometric-product
juxtaposition, the label spans the whole product occurrence.

## Presenter composition

```python
from galaga import presets

presented = presets.presenters.lengyel()(ga.annotate(area, label="area"))
assert isinstance(presented, ga.Annotated)
assert r"\overset{\text{area}}" in presented.latex()

annotator_presenter = ga.AnnotationPresenter(base=presets.presenters.functional())
composed = annotator_presenter(ga.annotate(area, label="area"))
assert isinstance(composed, ga.Annotated)
assert composed.rules == presented.rules
```

Ordinary presenters compose through the core adapter hook, and
`AnnotationPresenter` applies a base presenter explicitly. Both preserve the
annotation rules and the captured presentation.

## CGA object highlights

```python
from galaga import Algebra, outer_product, presets
from galaga.cga import ConformalModel

cga = ConformalModel(Algebra(config=presets.lengyel_cga(), expr=True), expr=True)
dipole = outer_product(cga.up((0.75, 1.0, 2.0)), cga.up((-0.25, 0.1, 0.2)))

object_highlight = ga.highlight_cga(cga)
assert ga.classify_cga(dipole, cga).kind == "dipole"
object_view = object_highlight(dipole)
assert object_view.latex().count(r"\colorbox{#b8e6bf}") == 1
assert object_view.latex().count(r"\colorbox{#d8c4ee}") == 1
assert (
    r"\underset{\textcolor{#2f7d4f}{\text{carrier line}}}{\colorbox{#b8e6bf}{$"
    r"\smash[t]{\textcolor{#0099cc}{\overset{\text{cocarrier normal}}{\overgroup{"
    r"\textcolor{black}{\vphantom{\raisebox{4px}{" in object_view.latex()
)
assert r"\overgroup{\textcolor{#0099cc}{" not in object_view.latex()

round_point = cga.up((0.5, -0.75, 1.25)).without_expr()
p = cga.up((0.75, 1.0, 2.0))
q = cga.up((-0.25, 0.1, 0.2))
r = cga.up((0.0, 1.0, 0.0))
s = cga.up((0.0, 0.0, 1.0))
circle = outer_product(p, q, r).without_expr()
sphere = outer_product(p, q, r, s).without_expr()

round_point_view = object_highlight(round_point)
circle_view = object_highlight(circle)
sphere_view = object_highlight(sphere)
assert ga.classify_cga(round_point, cga).kind == "round point"
assert ga.classify_cga(circle, cga).kind == "circle"
assert ga.classify_cga(sphere, cga).kind == "sphere"
assert all(label in round_point_view.latex() for label in ("origin", "position", "infinity"))
assert all(
    label in circle_view.latex()
    for label in ("carrier plane", "flat line", "cocarrier direction", "cocarrier moment")
)
component_circle_view = ga.highlight_cga(cga, decomposition="components")(circle)
assert all(
    label in component_circle_view.latex()
    for label in ("plane part", "center part", "flat part", "flat weight")
)
assert "origin part" in sphere_view.latex()
```

`classify_cga` currently targets three-dimensional Euclidean CGA. It recognizes
round points, flat points, dipoles, lines, circles, planes and spheres, while
distinguishing grade-one dual planes from dual spheres and rejecting
non-simple candidates or models with a different spatial dimension. Its
predicates and `cga_parts()` selections are stable under ordinary nonzero
projective rescaling. `highlight_cga(model)` defaults to an **incidence
decomposition**, using carrier/cocarrier geometry where a specialized layout
is available. `highlight_cga(model, decomposition="components")` keeps the
**component-role decomposition**, which explains the four Lengyel
round/flat bulk/weight families with object-specific labels. For circles, the
incidence view labels the carrier plane, flat line, cocarrier direction, and
cocarrier moment shown in Lengyel's classification. The incidence view of a
dipole shows its carrier line and flat
point as contiguous highlights, with "cocarrier normal" and "cocarrier
position" overgroups overlaid above subsets of those highlights. The
overgroups use `overlay=True`, so a raised phantom inside the bracket body
lifts the bracket by `clearance` while the terms stay on the baseline, and
`\smash[t]` keeps an enclosing fill tight. Their cyan colour applies to the
bracket chrome only, and the "carrier line"/"flat point" labels use
darkened matching shades via `label_color`. `cga_parts` exposes the Lengyel
component families for custom recipes.
