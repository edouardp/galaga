---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-081: Optional Integrations Consume Public Protocols

## Context and problem statement

The experimental Mermaid package imports Galaga 1 expression subclasses and
walks private multivector expression fields. The Marimo adapter generally uses
the public LaTeX convention but reads private name fields when recognizing
known values. Both dependencies couple presentation tools to the legacy
engine, even though Galaga 2 now exposes immutable expression provenance,
names, and a shared semantic renderer.

The integrations also have different runtime requirements. Base Galaga and
Mermaid support Python 3.11, while Marimo's t-string interface requires Python
3.14.

## Decision drivers

- Keep optional packages out of the base Galaga dependency graph.
- Let mathematical content remain owned by the facade renderer.
- Traverse expressions through stable immutable fields.
- Preserve the deliberate separation of provenance and concrete value state.
- Keep the Python 3.14 requirement local to `galaga-marimo`.
- Make private-state removal executable through source architecture tests.

## Decision outcome

`galaga_mermaid` 0.2 accepts `galaga.expression.Expr` nodes. It traverses
`Call.operands` and public symbol/literal fields. A standalone expression needs
an explicit `PresentationConfig`; optional evaluation needs an algebra and
symbol environment. `mv_to_mermaid` derives these through facade protocols and
does not mutate the value.

`galaga_marimo` 2.0 continues to render any object supporting `.latex()` or
`_repr_latex_()`. Facade objects additionally support content-oriented t-string
format specifications through `.display()`. Recognition reads immutable
`Name.latex` and public coefficients. Marimo alone requires Python 3.14;
Galaga, galaga-matrix, and galaga-mermaid retain Python 3.11 minima.

Each optional package declares `galaga>=2.0.0`. Package-internal imports are
relative. Source tests reject the legacy expression imports and private
multivector fields.

The old notebook gallery and `MatrixRepr` symbolic base are explicitly not
covered by this decision and keep W7.4 open.

## Consequences

- Good, because renderer integrations no longer depend on numeric-engine
  representation details.
- Good, because Mermaid cannot accidentally evaluate provenance with hidden
  values or an inferred metric.
- Good, because teaching code can select expression versus concrete output
  without changing a value or its presentation persistently.
- Good, because installing base Galaga does not install Marimo or require
  Python 3.14.
- Cost, because standalone expression graphs need an explicit presentation.
- Cost, because old Mermaid callers must migrate from legacy `Expr.eval()`
  behavior to explicit environments.
- Deferred, because the notebook gallery needs a guarded semantic codemod and
  `MatrixRepr` still needs a v2-native symbolic boundary.
