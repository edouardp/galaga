---
status: accepted
date: 2026-03-30
deciders: edouard
---

# ADR-044: Remove Standalone scalar() Function

## Context and Problem Statement

The library had three ways to extract the grade-0 coefficient:

- `scalar(mv)` — standalone function, returns `float`
- `mv.scalar_part` — property, returns `float`
- `grade(mv, 0)` — returns `Multivector`

`scalar()` was redundant with `.scalar_part` and created confusion with
`alg.scalar(value)` (the algebra method that creates scalar multivectors).

## Decision Outcome

Remove the standalone `scalar()` function. Use `.scalar_part` everywhere.

### Why Not Keep Both

- `scalar()` looks like it should be the inverse of `alg.scalar()` but it
  isn't — one creates an MV, the other extracts a float.
- `.scalar_part` is unambiguous — it's clearly a property accessor.
- `scalar()` didn't participate in the symbolic layer (no Expr node), so
  it had no advantage over the property.

### Consequences

- Good, because one fewer way to do the same thing
- Good, because no confusion with `alg.scalar()`
- Bad, because it's a breaking change for existing users
- Acceptable, because pre-1.0 and the migration is mechanical (`scalar(x)` → `x.scalar_part`)
