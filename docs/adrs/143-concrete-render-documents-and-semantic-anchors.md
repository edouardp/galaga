---
status: accepted
date: 2026-09-17
deciders: edouard
---

# ADR-143: Concrete Render Documents and Semantic Anchors

## Context

The proposed annotation extension needs to select concrete multivector terms,
coefficients, signs, and blades without searching emitted LaTeX. Render nodes
currently retain display labels but not their native blade identities. Adding
annotation start/end nodes to expression provenance would couple computation
to display and make overlapping selections difficult to represent.

## Decision

Expose `value_document(value, presentation=None)` in `galaga.rendering`.
It returns an immutable `RenderDocument` containing the ordinary render tree,
the resolved presentation, and a separate ordered tuple of `RenderAnchor`
records. Build these records alongside coefficient layout in the same shared
builder used by `value_tree`; never reconstruct blade identities from labels.

Anchors select terms, coefficient magnitudes, displayed signs, or blade
symbols by native mask. Grade derives from that mask. A term or sign in a
`Sum` references the shared sum node and its term index. Value documents retain
a one-term `Sum` for a visible singleton so its optional sign remains a real
slot; the ordinary `value_tree` may still collapse that structural wrapper.
Both forms emit identical text. Coefficient and blade anchors reference actual
nodes in the document. Displayed orientation composes the native coefficient
with the blade label's orientation.

Anchors describe only visible components. Zero and tolerance-hidden terms,
omitted unit coefficients, and implicit leading plus signs yield no anchors.
Valid selectors may return an empty tuple, including grades above dimension.
Selection errors concern malformed requests rather than absent matches.

Node references and term indices are local to one document; rebuild them
when presentation changes. Annotation rules and layout remain in the optional
extension. No numerical object or expression tree acquires annotation nodes.

## Consequences

- Existing emitted output remains identical. A value document deliberately
  retains one extra semantic `Sum` wrapper for a singleton term.
- The extension can store multiple independent selections over one sum.
- Native identity survives presentation ordering and signed blade labels.
- The core has no dependency on the annotation package.
- This initial implementation covers concrete facade multivectors only.
  Expression occurrences, simplification source mapping, explicit/implicit
  operator anchors, teaching equalities, tables, and matrix adapters require
  follow-up work. In particular it does not yet implement SPEC-015's required
  geometric-product operator annotation fallback.

ADR-144 subsequently implements expression occurrence mapping and the
implicit geometric-product anchor. The limitations above describe the
initial concrete-value milestone, not the current expression document API.

## Validation

Unit tests compare document and ordinary-tree output through all three
emitters, verify the singleton sign slot without a synthetic leading plus,
check that referenced nodes belong to the document, derive RGA sign checks
from actual algebra coefficients and blade orientations, and exercise display
ordering, tolerance, rounded unit coefficients, empty selections, immutability,
and invalid selectors.
