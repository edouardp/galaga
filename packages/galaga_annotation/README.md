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
- [ADR-149: Matrix Cell and Region Annotations](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/149-matrix-cell-and-region-annotations.md)
- [ADR-150: Sign-Only Annotation Targets](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/150-sign-only-annotation-targets.md)
- [ADR-151: Content-Part Annotation Targets](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/151-content-part-annotation-targets.md)
- [ADR-152: Subexpression Annotation Targets](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/152-subexpression-annotation-targets.md)
- [ADR-153: Configurable CGA Cocarrier Markers](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/153-configurable-cga-cocarrier-markers.md)
- [ADR-154: Independent External Span Overlays](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/154-independent-external-span-overlays.md)
- [ADR-156: Headless Browser Geometry Contracts](https://github.com/edouardp/galaga/blob/galaga_v2/docs/adrs/156-headless-browser-geometry-contracts-for-katex.md)

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

## Targeting a subtree

`ga.subexpression(value, occurrence=...)` finds a subtree by its recorded
provenance tree instead of its operand position, so the rule survives unrelated
edits to the enclosing expression. Matching is structural, not numeric.

```python
rotor = (1 + e1 * e2).named("R")
sandwich = (rotor * e1 * ~rotor).named("w")
subtree = ga.annotate(sandwich, ga.on(ga.subexpression(~rotor), label="reverse factor"))
assert r"\widetilde{R}" in subtree.latex()
```

It needs a tracked value (`expr=True`). Use `occurrence=n` to pick one of
several matches, or the default `"all"`.

## Annotating signs

`ga.sign(blade)` selects the displayed sign of a term on its own, so a rule
can highlight a `+` or `-` without touching the coefficient or blade.
`ga.signs(*blades)` selects several.

```python
value = (0.5 + 2 * e1 - 3 * (e1 ^ e2)).named("A")
signed = ga.annotate(value, ga.on(ga.sign(e1 ^ e2), background="#fff3cd"))
assert r"\colorbox{#fff3cd}{$-$}" in signed.latex()
assert r"2 e_{1}" in signed.latex()
```

A sign is only selectable when it is visible, so a positive leading term
matches nothing. Sign decorations reuse the ordinary styles and markers and
compose with grade fills and joined term spans.

Term and grade callouts include a visible negative sign in their measured
extent, including the minus on a non-leading term. Content-only backgrounds
continue to leave the separator between two disjoint highlights uncoloured.
To extend a joined fill through its leading sign, select that sign with the
same background; the renderer fuses the two targets into one continuous box.

## Targeting the name, expression, and value

A tracked value can display as `name = expr = value`. `ga.content(kind)`
selects one part, where `kind` is `"name"`, `"expr"`, or `"value"`.

```python
parts = ga.annotate(
    area,
    ga.on(ga.content("expr"), background="#fff3cd"),
    ga.on(ga.content("value"), color="royalblue"),
)
full = parts.latex(content="full")
assert r"\colorbox{#fff3cd}{$" in full
assert r"\textcolor{royalblue}{" in full
assert r"\quad = \quad" in full
```

A part target respects the active content setting: `ga.content("name")`
matches nothing when only the value side is displayed.

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

## Matrix cell and region annotations

Matrix representations from the optional `galaga_matrix` companion use the
same rules and styles. Targets select a cell, row, column, index list, or
rectangular block by zero-based coordinates, and a region label anchors to the
region's first cell.

```python
import importlib.util

if importlib.util.find_spec("galaga_matrix") is not None:
    import numpy as np
    from galaga_matrix import MatrixRepr

    matrix = MatrixRepr(np.arange(4).reshape(2, 2))
    view = ga.annotate(
        matrix,
        ga.on(ga.cell(0, 0), background="#e8f5e9", label="origin"),
        ga.on(ga.block(rows=slice(1, 2), columns=slice(0, 2)), border="seagreen"),
    )
    assert r"\overset{\text{origin}}" in view.latex()
    assert r"\fcolorbox{seagreen}{transparent}" in view.latex()
```

Out-of-range coordinates raise `ValueError`; a valid but empty selection
follows the rule's `missing` policy. The matrix adapter is optional, and
importing `galaga_annotation` never imports `galaga_matrix`.

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
position" overgroups overlaid above subsets of those highlights. Term-span
markers choose overlay lowering automatically: a raised phantom inside the
bracket body lifts it by `clearance`, while an outer zero-width phantom makes
KaTeX reserve the callout's height without enlarging the enclosing fill. Their
cyan colour applies to the bracket chrome only, and the "carrier line"/"flat
point" labels use darkened matching shades via `label_color`. `cga_parts`
exposes the Lengyel component families for custom recipes.

See [`examples/annotation/span_composition.py`](../../examples/annotation/span_composition.py)
for equal, nested, disjoint and crossing intervals, including one highlight
with independent callouts above and below.

The cocarrier callout style is selectable with `over_marker`: `"overgroup"`
(the default), `"overbrace"`, `"overline"`, or `"overbracket"`.
`ga.highlight_object` is an alias of `ga.highlight_cga`.

```python
overbraced = ga.highlight_object(cga, over_marker="overbrace")(dipole)
rendered = overbraced.latex(content="value")
assert r"\overbrace" in rendered
assert r"\overgroup" not in rendered
```

## Browser geometry tests

String and standalone-KaTeX tests run with the normal package suite. To verify
actual marker and label alignment in Marimo's KaTeX CSS using pinned headless
Chromium, run:

```console
make test-galaga-annotation-browser
```

The target installs Playwright's browser artifact through UV on first use; it
does not control or depend on a desktop browser.
