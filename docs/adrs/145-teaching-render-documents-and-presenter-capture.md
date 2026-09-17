---
status: accepted
date: 2026-09-17
deciders: edouard
---

# ADR-145: Teaching Render Documents and Presenter Capture

## Context

Concrete and expression documents supply independent semantic anchors. A
teaching display combines a name, expression, and result, but the existing
emitter suppresses identical-looking parts after notation and output target
have been resolved. Anchors must represent the content actually displayed.
Reusable presenters must also provide documents with their captured settings.

## Decision

Add `content_document(value, content=None, presentation=None, notation=None,
target=None)` in `galaga.rendering`, and `PresentedMultivector.render_document`
with the same keyword overrides. The builder follows existing content policy,
including automatic content selection and fallback to concrete values.
Presented inputs use their captured presentation; explicit overrides retain
the same precedence as ordinary display.

Combine independent documents and rebase their layout paths into the visible
equality. Add immutable `ContentAnchor` records for name, expression, value,
and relation slots. Component anchors also gain document-relative render
paths. Original expression paths remain unchanged.

Share duplicate-part visibility with the ordinary equality emitter. Retain
the first occurrence of each emitted part, exactly as current display does.
Suppressed parts contribute no anchors; do not move their annotations to
another equal-looking part. If only one part survives, omit the equality and
its relation anchors. Equality relation indices identify the following part.

Content documents capture their output target because visibility may differ
between ASCII, Unicode and LaTeX. Rebuild for a different target. The shared
visibility helper emits parts for comparison but does not parse emitted text
or derive any mathematical identities from it.

## Consequences

- The annotation extension can independently select an operator on the
  expression side and a grade on the result side.
- Captured presenter views provide a stable document-building entry point.
- Core remains independent of any annotation wrapper or package. Accepting
  external annotation views in a presenter still needs an adapter contract.
- A result suppressed as a duplicate has no component anchors. Requesting
  value-only content exposes its components explicitly.
- Existing output and duplicate elimination remain unchanged.

## Validation

Tests compare documents to ordinary rendering across all content modes and
output targets, resolve all anchors into the combined tree, exercise multiple
equalities and target-dependent duplicates, check fallback content, validate
captured notation/order and explicit overrides, and reject invalid requests.
