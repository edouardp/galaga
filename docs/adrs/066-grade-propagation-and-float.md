---
status: accepted
date: 2026-04-13
deciders: edouard
---

# ADR-066: Grade Propagation via @ga_op and __float__ Conversion

## Context and Problem Statement

Multivectors had no systematic way to track their grade through operations.
The `_grade` field existed but was only set by `sym()` and `name()`. This
meant `float()` couldn't reliably determine whether a result was scalar,
and grade information was lost through operation chains.

## Decision

### Grade propagation

Each `@ga_op` can declare a `grade=` rule — a function that computes the
output grade from input grades. The `@ga_op` wrapper applies it
automatically after both symbolic and numeric paths. 18 of 29 operations
have rules; the remaining 11 (gp, commutator, exp, etc.) produce mixed
grades and return `_grade=None`.

Factory methods (`scalar()`, `basis_vectors()`, `pseudoscalar()`,
`vector()`, `basis_blades()`, `locals()`) and `grade(x, k)` now set
`_grade` on their results.

### `__float__` and `__abs__`

`float(mv)` returns the grade-0 coefficient if the MV is scalar. It raises
`TypeError` with a descriptive message for non-scalar MVs. Uses the `_grade`
cache for a fast path, falls back to `homogeneous_grade()`.

`abs(mv)` delegates to `abs(float(mv))`.

### `norm2` returns a Multivector

`norm2(x)` now returns `grade(gp(x, reverse(x)), 0)` — a scalar MV with
`_grade=0` — instead of a bare float. This lets `float(norm2(x))` work
naturally and keeps the grade chain intact.

## Consequences

- `float()` works on any grade-0 result: `scalar_product`, `grade(x, 0)`,
  `norm2`, scalar arithmetic, etc.
- `float()` on vectors, bivectors, rotors, or mixed-grade MVs raises
  `TypeError` with the specific grade in the message.
- Grade propagates through operation chains without recomputing from data.
- `norm2` callers that expected a float still work — `float()` is called
  explicitly where needed (e.g. in `norm()`).
