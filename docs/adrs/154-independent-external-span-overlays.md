---
status: accepted
date: 2026-09-19
deciders: edouard
---

# ADR-154: Independent External Span Overlays

## Context

ADR-147 lowered every joined term annotation by wrapping its visible subtree.
That works when all selected intervals nest or remain disjoint, but a wrapper
tree cannot represent crossing intervals. A common teaching layout needs a
continuous joined highlight over one range and an overbrace, underbrace, group
accent, arrow, or label over a different range. The ranges may be equal,
nested in either direction, disjoint, or crossing.

Changing from nested to crossing after moving a marker by one term must not
silently change the annotation model or force a notebook author to split a
continuous highlight. Above and below callouts are also independent visual
channels rather than competing content owners.

## Decision

For annotations resolved to terms in a `Sum`, separate **base content styles**
from **external callouts** before lowering:

- foreground colour, background, border and emphasis remain content spans in
  the visible render tree;
- labels and markers become independent external span overlays;
- a rule containing both is split into those two internal effects while the
  public `Annotation` remains one immutable rule.

Every external span uses the same lowering regardless of its relationship to
other spans. The renderer inserts a zero-width `\mathrlap` at the first term
of the interval. The marker measures a `\phantom` copy of the selected terms,
and `\smash[t]` or `\smash[b]` keeps the visible marker in the appropriate
external channel without changing the base expression's dimensions. A second,
unsmashed copy is wrapped in an outer zero-width `\vphantom`. This makes KaTeX
reserve the marker's height or depth without placing that reservation inside a
joined `\colorbox`. The visible expression is emitted once; only invisible
measurement structures are repeated. A term target excludes its sign by
default or includes it explicitly with `include_sign=True`; base content and
its split external callout use that same extent. When included, the overlay is
inserted inside an explicit ordinary or binary math-class atom so its
zero-width prefix cannot change KaTeX's classification of the sign. The
isolated phantom keeps the sign ordinary and includes the corresponding
medium sign advance; this reproduces the visible signed extent. When excluded,
the marker measures only the coefficient-plus-blade body, just like its fill.
An implicit leading `+` is never synthesized. Separators between disjoint
fills remain unhighlighted.
Measurement uses the undecorated semantic sign glyph. Copying a decorated
sign into KaTeX's `\vphantom` is not visually inert: a nested `\colorbox` can
still paint its background at the zero-width reservation origin and obscure
visible content there.

KaTeX normally makes an over/under construct as wide as its wider child. A
label wider than its marked expression would therefore centre the expression's
phantom inside the label width and disconnect the marker from the visible terms
at the overlay anchor. External labels are wrapped in `\mathclap`: their ink
and vertical extent remain, but their horizontal layout width is zero. The
marker width is consequently determined only by the selected expression.
Term-span phantoms do not include a surrounding highlight horizontally because
the overlay is inserted at the highlighted content origin; including the box
would add its padding and misstate the selected mathematical extent. They do
include the fill's vertical extent: when a callout overlaps a span carrying a
background or border, the marker measures an invisible, zero-width copy of the
fill box. The copy substitutes `transparent` for the real fill colours, so it
cannot paint at the zero-width origin, and it is `\smash`ed on the side facing
back into the expression. A below marker therefore gains only depth and an
above marker only height. The marker clears the fill padding and border while
the visible highlight keeps exactly its original box.

Fill intervals form a forest of nested boxes with disjoint siblings. Measure
each outer box intersecting the callout using its complete subtree, including
descendants outside the callout interval: those descendants still determine
the enclosing box's height and depth. Each box combines its undecorated content
with its children's zero-width extents on the same baseline before adding its
own transparent padding and border. KaTeX therefore takes the maximum extent
of siblings and adds padding only through actual parent/child nesting. For
equal intervals, later rules wrap earlier ones, matching the visible renderer.
Apply the inward-side smash only after measuring the complete outer box.

The base layer continues to require content-style spans to nest or stay
disjoint. Crossing fills need a separate overlap policy because two different
backgrounds cannot both continuously own the same separators. One overlapping
external callout is supported in each vertical channel. An over-marker and an
under-marker may overlap each other and the highlight, but two overlapping
callouts resolved to the same side raise `SpanLayoutError`. Multi-lane stacking
on one side is deferred.

Direct annotations on non-sum nodes retain ADR-147's ordinary wrapper lowering.
The public `side`, `marker`, `clearance`, and `overlay` fields remain compatible;
term-span callouts choose overlay lowering automatically.

## Consequences

- Joined highlights remain continuous when a brace or label crosses their
  boundary.
- Equal, subset, superset, disjoint and crossing callout intervals share one
  implementation instead of switching between wrappers and overlays.
- A highlight may simultaneously carry one overlapping callout above and one
  below.
- The generated KaTeX contains phantom copies for measurement, but only one
  visible expression. KaTeX represents those copies with `mphantom` semantics.
- Overlay ink contributes to the equation's outer KaTeX bounds while the base
  highlight retains its original height and depth (GitHub issue #12).
- A label, arrow, rule, brace or group over a highlighted span is placed
  outside the fill's padding and border instead of crossing into it, without
  changing the fill's own geometry.
- Transparent extent copies are visible only to layout; they paint no ink and
  add no horizontal width.
- Same-side multi-lane layouts and crossing body-style conflict policies remain
  explicit future work rather than producing accidental collisions.

## Validation

- Span tests cover all interval relationships, explicit signed and unsigned
  leading terms (including a suppressed leading plus), continuous fills,
  simultaneous above/below overlays, and rejection of overlapping same-side
  callouts and crossing body styles. They also cover the transparent extent
  copies: depth-only for below markers, height-only for above markers, frame
  padding for bordered fills, full-fill extents for partial overlap, and no
  copy for disjoint intervals.
- Browser geometry tests assert that underbraces and overbraces sit outside a
  shared highlight's bottom and top edges, including a bordered fill and a
  crossing interval, and that the visible fill's height and width are
  unchanged by the extent copy. Nested-fill regressions also compare every
  painted box's position relative to an untouched basis blade. They cover a
  nested fill outside the callout interval and disjoint sibling fills inside
  the same outer box.
- Runtime tests compile the generated overlays with Marimo's bundled KaTeX
  0.16.47 through Node and inspect its render-tree height/depth to verify the
  outer bounds reservation. They also inspect KaTeX's MathML lowering for the
  zero-width `mpadded` node produced by `\mathclap` on a deliberately wide
  label. Nested sum, product, and wedge-expression regressions compare the
  measured extents against the actual visible box tree, including descendants
  outside the callout, siblings, deeper branches, equal intervals, borders,
  and unequal member heights.
- Playwright tests load the same JavaScript and CSS in headless Chromium and
  compare the target, brace and label bounding boxes for leading and
  non-leading signs and a deliberately over-wide label. See ADR-156.
- Every annotation teaching notebook executes headlessly and its emitted LaTeX
  is passed through the standalone KaTeX parser.

## Related

- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): original
  wrapper lowering and direct-node behavior.
- [ADR-156](156-headless-browser-geometry-contracts-for-katex.md): browser
  geometry validation for this lowering.
- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): annotation
  capability and API specification.
