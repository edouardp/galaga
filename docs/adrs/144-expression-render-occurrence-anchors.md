---
status: accepted
date: 2026-09-17
deciders: edouard
---

# ADR-144: Expression Render Occurrence Anchors

## Context

ADR-143 supplies concrete value anchors. Expression annotations additionally
need to identify original operand and operation occurrences after display
simplification, associative flattening, argument reordering, and notation
changes. A geometric product may have no visible operator at all.

## Decision

Add `galaga.rendering.expression_document(expression, presentation, target=None)`.
It uses the ordinary simplification rewrites and layout builder with opt-in
occurrence recording. The normal expression tree and all emitter output stay
unchanged. Store immutable `ExpressionAnchor` records separately from the
layout tree, in `RenderDocument.expression_anchors`.

Each record carries an original binary expression path and a document-local
render path of field names and tuple indices. Render paths distinguish
multiple displayed uses of a shared layout node. Associative flattening maps
removed containers to half-open intervals in sum terms, product factors, or
infix operands. This is a layout range, not a LaTeX character range.

Whole-expression occurrences may map to their simplified result, while
removed operands and operations do not acquire unrelated anchors. Only the
deepest original occurrence owning a surviving operation gets its operator
anchor: removing an outer addition must not relabel a surviving inner one.
An operation rewritten into a different canonical operation does not retain
the old operator target. Valid selections with no matches return `()`.

Operator anchors identify function names, infix/prefix/postfix symbols, sum
signs, product separators, or accents. Structural notation such as fractions
uses the full notation extent. For an implicit product operator the anchor is
the local product extent, including any required internal operand grouping.
Flattened inner products retain their narrower intervals. Join indices name
the following term/factor/operand, preserving each binary occurrence's own
join instead of selecting all operators in a flattened row.

The simplification source mapper uses the same `_rewrite` implementation as
ordinary simplification. Its private mapping protocol is not a symbolic
transformation API. Layout locations resolve by occurrence identity and
shared-builder structural rewrites, never by searching output strings.

## Consequences

- The annotation package can explain operators under functional, explicit,
  and juxtaposition notation with the same semantic rule.
- Expression provenance remains immutable and has no annotation markers.
- Simplification may produce an empty operator selection without an error.
- Expression and value documents share one container but keep distinct anchor
  types. Teaching equalities, their emitted duplicate-part elimination,
  expression-literal coefficient anchors, and presenter integration still
  require follow-up work.
- Fraction/wrapper/script notation is anchored as a complete extent initially;
  finer selection of those structural marks is deferred.

ADR-145 subsequently implements teaching documents and document building
through captured presenter views. Extension wrapper adapters and component
anchors inside expression literals remain pending.

## Validation

Tests cover nested products and sums, individual joins after flattening,
functional and explicit operators, local juxtaposition extents, shared
symbols, repeated operand display in definition notation, all simplification
rewrite families, removal of same-named outer operations, negative signs
absorbed into sums, render path resolution, unchanged emitter output, empty
matches, and invalid requests.
