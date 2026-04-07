---
status: accepted
date: 2026-04-07
deciders: edouard
---

# ADR-059: Custom Basis Blade Display Ordering

## Context and Problem Statement

Multivector terms display in bitmask order (ascending binary index). This
matches the internal `data[]` layout but not always conventional notation.
Quaternions via Cl(3,0) bivectors display as `1 + 4k + 3j + 2i` instead
of the expected `1 + 2i + 3j + 4k`.

## Decision Drivers

* Quaternion convention expects i, j, k order
* All other algebras (STA, PGA, CGA) are fine with bitmask order
* Must not affect computation — display only

## Decision Outcome

Add an optional `display_order` field to `BladeConvention` — a tuple
specifying the bitmask iteration order for rendering and `basis_blades()`.

### Implementation

* `display_order: tuple[int, ...] | None` on `BladeConvention` (default `None`)
* Validated as a permutation of `range(dim)` at algebra construction
* Stored as `Algebra._display_order` (defaults to `tuple(range(dim))`)
* Used by `_format()`, `__format__()`, `latex()`, and `basis_blades()`
* `b_quaternion()` sets it; all other factories leave it as `None`

See SPEC-011 for the full specification.

### Consequences

* Good, because `1 + 2i + 3j + 4k` displays correctly
* Good, because `i, j, k = alg.basis_blades(k=2)` unpacks in conventional order
* Good, because no computation is affected
* Neutral, because only `b_quaternion()` uses it currently
