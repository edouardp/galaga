---
status: accepted
date: 2026-07-08
deciders: edouard
---

# ADR-010: Replace MatrixRepr Labels with Symbolic Names

## Context and Problem Statement

`MatrixRepr.label` was introduced as a lightweight way to make matrices more
readable in notebooks. It let matrix values render as:

```latex
\sigma_1 = \begin{pmatrix} ... \end{pmatrix}
```

That was useful, but it was not the same concept as Galaga's Multivector
`.name()` system. A label was render-only metadata: it did not create a
symbolic leaf, did not participate in expression trees, and required separate
propagation rules.

SPEC-013 introduces a shared naming and symbolic-expression core. With that
capability, MatrixRepr no longer needs a separate label mechanism.

## Decision Outcome

Retire MatrixRepr's public label API and use `.name()` for matrix naming.

Target MatrixRepr behavior:

- `MatrixRepr(..., label=...)` is not accepted.
- `.label` is not part of the public MatrixRepr API.
- `MatrixRepr(...).name(...)` assigns a display name and makes the matrix a
  symbolic leaf.
- Operations on named MatrixRepr values build symbolic expression trees while
  preserving concrete matrix values.
- `to_matrix(named_mv)` uses symbolic representation-map naming, such as
  `\rho(B)`, instead of setting a render-only label.
- `to_matrix(symbolic_mv)` preserves unnamed symbolic multivector expressions
  as matrix representation-map expression trees, so `to_matrix(a * b)` can
  render as `\rho(a b)` even when `a * b` has no display name.
- `MatrixRepr.latex()` remains value-oriented by default, but when the matrix
  carries an algebra with `display_repr=True`, it mirrors `Multivector.latex()`
  and delegates to `.display()` for direct notebook interpolation.
- The default compact representation map is written as plain `\rho`. Explicit
  non-default Dirac-family basis views use superscripts, for example
  `\rho^{\mathrm{Weyl}}` and `\rho^{\mathrm{Majorana}}`.
- Quaternion-block mode is a distinct representation, not a Dirac-family basis
  view, so it uses `\rho_{\mathbb{H}}`.
- `from_matrix(named_matrix)` can infer the algebra and mode from a
  `MatrixRepr`, and uses the matrix's symbolic name or expression to name the
  recovered multivector, such as `\rho^{-1}(M)`.
- `from_matrix(alg, array, mode=...)` remains the explicit form for raw arrays
  and matrix wrappers that do not carry an algebra reference.

Because `galaga_matrix` is not yet published, this is an intentional breaking
change rather than a long-lived compatibility layer.

## Consequences

- Good, because MatrixRepr and Multivector use one naming vocabulary.
- Good, because matrix names participate in symbolic expression trees.
- Good, because matrix expressions respect the same `display_repr=True`
  notebook behavior as multivectors.
- Good, because provenance such as `\rho(B)` and `\rho^{-1}(M)` is represented
  symbolically rather than as display-only text.
- Neutral, because existing matrix tests and notebooks using `label=` must be
  migrated to `.name()`.
- Neutral, because ADR-007's auto-labeling decision is superseded by
  auto-naming.
