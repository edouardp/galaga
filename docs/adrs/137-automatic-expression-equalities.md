---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-137: Automatic Expression Equalities

## Context

`Algebra(..., expr=True)` successfully records provenance, but default `auto`
display previously showed full equalities only for named values. Consequently
`(e1 + e2) ^ e3` displayed only its evaluated coefficients even when the user
explicitly enabled tracking for a teaching notebook.

## Decision

For multivectors, `content="auto"` selects `full` whenever the individual value
has a name or expression, otherwise `value`. Reuse the existing full-content
pipeline and its target-specific deduplication: literal provenance need not
produce redundant equalities such as `e1 = e1`.

Use actual value metadata, not `algebra.expr`. The latter remains a factory
default, false unless requested. An explicit factory opt-out remains value-only
when its result has neither a name nor provenance; explicit tracking on an
otherwise untracked algebra also receives explanatory display.

Explicit `name`, `expr`, `value` and `full` content retain their meanings.
Persistent, scoped and per-render presentation overrides retain their existing
precedence. In particular, `DisplayPolicy(content="value")` hides provenance
without discarding it even when the algebra enables tracking.

This updates the automatic-content decision described in ADR-098 and clarifies
the display interaction of ADR-132. It changes neither expression construction
nor numerical evaluation, equality, hashing or storage. Table rendering and
standalone expression rendering keep their existing paths.

## Consequences

- Notebook outputs teach both the operation and its evaluated result after a
  single algebra-level tracking opt-in.
- Anonymous tracked results may produce longer output than before, including
  text representations and default template interpolation. Explicit `value`
  content is the supported way to request compact numeric output.
- Untracked anonymous values and duplicate literal displays stay unchanged.
- The shared ASCII, Unicode and LaTeX paths provide consistent behavior in
  ordinary Python, rich notebook display and Galaga-Marimo interpolation.

## Validation

Regression tests cover the reported Euclidean wedge expression, both tracking
entry points, algebra-level and scoped value policies, per-render overrides,
factory opt-outs, literal deduplication, all rendering targets and rich hooks.
Tests compare evaluated values and hashes with their untracked counterparts.
A Python 3.14 integration check exercises direct Marimo display and default
versus explicit-value template interpolation.
