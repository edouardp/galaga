---
status: accepted
date: 2026-09-16
deciders: edouard
---

# ADR-142: Reusable Callable Annotators

## Context

Teaching notebooks need helpers such as `highlight_grade(2)` that can be
prepared once and applied to many multivectors. Binding all rules to a value
at construction would duplicate annotation recipes and differ unnecessarily
from the reusable presenter workflow in ADR-139.

## Decision

Specify an optional `galaga_annotation` package with immutable annotation
rules, callable `Annotator` recipes, and rendering-only annotated views.
`annotator(*rules)` constructs a recipe; calling it binds a value without
changing the value or rendering it eagerly. `annotate(value, *rules)` is the
one-off equivalent.

Functional rules and fluent `.highlight`, `.label`, and `.mark` builders
produce the same ordered plan. Builders return new recipes, not mutable
selection state. Semantic targets resolve against the actual value and final
presentation. Valid selectors with no visible matches silently produce no
decoration by default (`missing="ignore"`); a rule can opt into
`missing="error"` to require at least one visible match. Empty selections do
not reserve annotation space or emit detached labels. Malformed selectors,
incompatible algebras, and invalid matrix regions remain errors.

Annotators select content; presenters choose its presentation. Integration
must preserve both the rules and captured presentation settings. Neither
core Galaga nor its ordinary imports require the extension. Annotated views
have no arithmetic; explicit `.value` access returns the original object.

Operator targets use the displayed glyph or function name when present.
For notation with an implicit operator, such as geometric-product
juxtaposition, the anchor is the displayed extent of that operation
occurrence (`ab`). The renderer records this distinction explicitly. An
operation removed by simplification or hidden by the content mode remains
an empty selection, rather than invoking this fallback.

`zero_subexpressions(atol=0)` is a deliberately value-dependent semantic
target. At resolution time it walks retained expression provenance, evaluates
self-contained operation subtrees against the value's algebra, and selects
the innermost calls whose coefficients are all within the absolute tolerance.
Innermost selection explains the first vanishing operations without producing
nested cancellation wrappers around every zero-valued ancestor. Literal zeros
are not selected. Calls that depend on unresolved named symbols are skipped,
while independently evaluable descendants remain eligible. The convenience
factory `cancel_zeros(...)` is ordinary immutable `Annotator` construction over
that target with a cancellation marker.

Flattened expression containers retain their semantic half-open interval in a
resolved placement. The annotation renderer wraps only that sum-term,
product-factor, or infix-operand interval; it does not widen a nested zero
subexpression to the complete flattened expression.

## Consequences

- Parameterized annotation factories are ordinary Python functions.
- Grade rules can be algebra-independent; blade-bound rules validate algebra
  compatibility instead of matching display names.
- Recipes naturally work across different grade supports. Zero or hidden
  terms and content removed by simplification need no special caller logic;
  removed targets must never be silently reassigned to surviving content.
- Functional and fluent APIs share validation, serialization, and rendering.
- Existing presenter support needs an explicit adapter contract; this ADR
  does not claim that integration is already implemented.
- Comparison rules and arithmetic propagation remain deferred.
- Automatic zero cancellation is rendering-only numeric inspection of existing
  provenance, not symbolic simplification and not arithmetic propagation.

## Validation

This is a proposed design, not an implementation. Implementation tests must
cover recipe immutability and reuse, functional/fluent plan equivalence,
empty and partially visible selections, opt-in missing-target errors,
simplification removing a target, algebra compatibility, presenter composition,
explicit and implicit operator anchors (including nested occurrences),
unchanged numerical identity, and render-time semantic target resolution.
See [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md).

Implemented by `galaga_annotation`, with the KaTeX lowering, decoration
wrapper node, presenter adapter hook and first milestone scope recorded in
[ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md).
