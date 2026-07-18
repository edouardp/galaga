---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-002: Make the Native Gram Matrix Canonical

## Context and problem statement

Galaga's numeric engine used an ordered signature both as its metric and as
proof that the stored basis was orthogonal. That cannot represent a native
oblique basis or a conformal origin/infinity pair with zero individual squares
and nonzero mutual pairing.

Internally diagonalizing a supplied matrix would recover an orthogonal product
algorithm, but it would replace the user's basis with hidden coordinates and
introduce basis-change roundoff into every value.

## Decision drivers

- Represent nonorthogonal and degenerate bases directly.
- Preserve the user's basis as the coefficient basis.
- Keep legacy `Cl(p,q,r)` construction convenient.
- Avoid parallel metric models that can disagree.
- Ensure tiny nonzero cross terms retain their mathematical effect.

## Considered options

1. Keep signatures canonical and derive nonorthogonal vectors as multivectors.
2. Diagonalize every supplied bilinear form internally.
3. Make a real symmetric native-basis Gram matrix canonical.

## Decision outcome

Every `Algebra` owns one copied, symmetric, read-only `float64` Gram matrix.
`Cl(p,q,r)` and explicit signature forms construct diagonal instances of that
same model. General `gram=` input remains in the supplied basis.

Exact equality after accepted symmetry canonicalization determines whether the
basis is diagonal. Metric classification tolerances affect inertia only; they
do not alter matrix entries or product coefficients.

`signature` is a compatibility property only for normalized diagonal metrics.
General callers use `gram`, `basis_squares`, or `inertia` according to the
property they actually need.

## Consequences

- Good, because native null CGA vectors can be one-hot exterior vectors.
- Good, because arbitrary oblique frames use the same public representation.
- Good, because diagonal algebras remain a fast special case rather than a
  separate semantic path.
- Cost, because a general basis-blade product may have several outputs.
- Cost, because companion packages must stop inferring all metric information
  from `signature`.
