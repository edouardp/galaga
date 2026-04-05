# ADR-055: Dual Constructor — Signature or Cl(p,q,r)

## Status

Accepted

## Context

Every other GA library (kingdon, clifford, ganja.js) accepts `Algebra(p, q, r)` to construct Cl(p,q,r). Galaga only accepted an explicit signature tuple like `(1, -1, -1, -1)`. This made galaga code look unfamiliar to users coming from other libraries.

## Decision

Make the first positional argument polymorphic:

- If iterable → explicit signature (existing behavior): `Algebra((1, -1, -1, -1))`
- If int → p count, with optional q and r: `Algebra(1, 3)` for Cl(1,3)

The `names`, `repr_unicode`, and `notation` keyword arguments are unchanged but are now keyword-only (enforced by `*`).

The p,q,r form produces the signature `(0,)*r + (+1,)*p + (-1,)*q` — degenerate
first, then positive, then negative. This matches the convention used by
clifford, kingdon, ganja.js, and most PGA literature (where the null basis
vector is conventionally e₀).

## Consequences

- `Algebra(3, 0, 1)` now works alongside `Algebra((0, 1, 1, 1))`.
- `Algebra(3, 0, 1)` produces the same basis ordering as kingdon and clifford.
- Existing code using tuple signatures is unaffected — the tuple form respects
  the user's explicit ordering.
- `names` was already used as a keyword argument everywhere, so making it keyword-only is not a breaking change.
