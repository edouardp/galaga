---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-021: Symbolic Basis Blades via basis_vectors(symbolic=True)

## Context and Problem Statement

With the unified naming/evaluation model (ADR-018), users can make any
multivector lazy with `.name()` or `.symbolic()`. But for fully symbolic
workflows — where every operation should build an expression tree — users
had to wrap each basis blade individually. This is tedious for exploratory
notebook work.

## Decision Drivers

* Fully symbolic workflows should be easy to set up
* The default numeric must remain zero-overhead for numeric work
* Basis blades should still carry correct names in all formats
* The choice should be per-algebra, at construction time

## Decision Outcome

Add a `lazy` parameter to `Algebra.basis_vectors()`:

```python
# Default: named + numeric (no change)
e1, e2, e3 = alg.basis_vectors()
e1 ^ e2   # → e₁₂ (concrete)

# Opt-in: named + symbolic (fully symbolic)
e1, e2, e3 = alg.basis_vectors(symbolic=True)
e1 ^ e2   # → e₁∧e₂ (expression tree)
```

With `symbolic=True`, all arithmetic on basis blades automatically builds
expression trees. Named scalars, `exp()`, `reverse()`, and all other
functions participate — the entire workflow stays symbolic until `.eval()`.

### Consequences

* Good, because one flag enables fully symbolic mode
* Good, because the default is unchanged (numeric, zero overhead)
* Good, because `.eval()` always gives the concrete result
* Neutral, because symbolic blades use more memory (expr trees)
