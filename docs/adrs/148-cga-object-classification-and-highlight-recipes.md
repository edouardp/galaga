---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-148: CGA Object Classification and Highlight Recipes

## Context

Teaching a conformal calculation needs more than term selection: a dipole,
circle or sphere has semantic parts, and a highlight should follow the modeled
object rather than a hand-written blade list. SPEC-015's nested-span example
showed a dipole split into a carrier line and a flat point, and the Lengyel
display order keeps those families contiguous, so joined spans can render
them as continuous highlights.

The validated `ConformalModel` already exposes Lengyel's four component
families (`round_bulk_part`, `round_weight_part`, `flat_bulk_part`,
`flat_weight_part`) plus the origin and infinity roles. Classification has no
home yet.

## Decision

Add `galaga_annotation.cga` as an optional integration layer over the
existing model; core Galaga is unchanged.

`classify_cga(value, model)` currently targets three-dimensional Euclidean CGA
(the five-dimensional conformal algebra used by the Lengyel preset). It
requires a homogeneous multivector from the model's algebra and returns an
immutable `CGAObject` with `kind`, `grade`, `flat` and `simple` fields. Other
spatial dimensions are rejected rather than applying the five-dimensional
grade table incorrectly. A direct blade is **flat** exactly when it is
divisible by the infinity vector (`value ∧ e_∞ = 0`); its grade then selects
flat point, line or plane. Round objects follow the OPNS grade table: point,
dipole, circle and sphere. Object names are assigned only to decomposable
blades. In five-dimensional CGA, grade-two decomposability is checked by
`B ∧ B = 0`; grade-three values use the same check on their metric dual,
while grades zero, one, four and five are decomposable by dimension. A
non-simple homogeneous value falls back to `general` and cannot enter a
kind-specific highlight recipe.

Grade one necessarily admits both common representations. A null vector with
nonzero conformal weight is a direct round point, a vector proportional to
infinity is the point at infinity, a non-null weight-zero vector is a dual
plane, and another non-null weighted vector is a dual sphere. Thus Euclidean
vectors and `n + d e_∞` are not mislabeled as spheres.

Classification predicates operate on a coefficient-normalized copy, making
kind, simplicity and component-family selection invariant under nonzero
projective rescaling above the absolute zero floor. The supplied `atol` is
validated, is passed consistently to homogeneous-grade detection, and is used
for normalized residual checks. Scalar and pseudoscalar values report
`flat=None` because divisibility by infinity is not a meaningful geometric
flatness classification for those grades.

`cga_parts(value, model)` returns the nonempty Lengyel component families as
joined term targets.

`highlight_cga(model, decomposition=...)` returns a callable that classifies
one multivector and returns an annotated view. Two vocabularies remain
available rather than forcing one interpretation:

- `decomposition="incidence"` is the default and emphasizes geometric
  carrier/cocarrier relationships. A dipole highlights its carrier line and
  flat point, with cocarrier normal and position overlays. Following Lengyel's
  circle classification, a circle highlights the round families as its
  carrier plane and the flat families as its flat line; the round-weight
  `e423/e431/e412` family receives a cocarrier-direction overlay and the
  flat-weight `e415/e425/e435` family a cocarrier-moment overlay.
- `decomposition="components"` retains the component-role view. It groups the
  four round/flat bulk/weight families with kind-specific teaching labels such
  as plane part, center part, flat part, and flat weight.

Both views use continuous green round-family and purple flat-family spans.
Cyan overgroups in the incidence view use `overlay=True` with a `"4px"`
clearance, so a raised phantom lifts each smashed bracket above its enclosing
fill without moving the terms or splitting the fill. Sign placement follows
the joined-span rules: a span's leading sign stays inside its highlight and
the separator between spans stays unhighlighted. Objects without a specialized
incidence view fall back to their component-role labels.

## Consequences

- The classifier consumes only public model methods and the public algebra
  interface, so it stays optional and small.
- Span continuity depends on the active display order; the Lengyel order
  groups round then flat families, and other conventions degrade to separate
  runs rather than wrong output.
- Kind-specific labels are teaching vocabulary, not mathematical claims;
  callers can build custom recipes from `cga_parts`.
- The classifier identifies algebraic families, not real/imaginary radius,
  tangent, or other degeneracy subclasses; those require additional center,
  carrier, weight and radius invariants.
- Crossing joined spans remain rejected by the renderer (ADR-147).

## Validation

- Tests classify point, flat point, dipole, line, circle, plane and sphere in
  the Lengyel CGA preset; distinguish direct points, the point at infinity,
  dual planes and dual spheres; cover scalar/general/zero fallbacks; and
  verify algebraically that a non-simple bivector is not named or highlighted
  as a dipole.
- Projective rescaling, tolerance consistency, model-algebra compatibility and
  component-family stability are tested explicitly.
- Tests assert the dipole incidence highlight is exactly two continuous spans
  with one label each, and that the circle incidence families match Lengyel's
  `e423/e431/e412`, `e321`, `e415/e425/e435`, and `e235/e315/e125` groups.
  Separate tests preserve the circle component-role vocabulary.
- The gallery notebook renders classifier-driven dipole, round-point, circle,
  and sphere highlights from objects constructed by conformal outer products.

## Related

- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): span
  layers, joining and KaTeX lowering.
- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification.
