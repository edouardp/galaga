---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-022: Blade Lookup Rejects Digit-by-Digit Parsing Above 9 Dimensions

## Context and Problem Statement

`Algebra.blade("e12")` parses the name digit-by-digit: `"e12"` → indices
`[1, 2]` → `e₁∧e₂`. This is unambiguous for up to 9 basis vectors, but
at 10+ dimensions `"e110"` could mean `e₁∧e₁₀` or `e₁₁∧e₀` — there is
no way to tell.

## Decision Outcome

Raise `ValueError` when `blade()` is called with the default `"e"` naming
scheme on an algebra with `n > 9`. The error message directs the user to
provide custom names.

Custom name parsing (greedy longest-first concatenation) is unaffected and
works at any dimension.

```python
# Fails: ambiguous
alg = Algebra(tuple([1] * 10))
alg.blade("e110")  # → ValueError

# Works: custom names are unambiguous
names = ([f"v{i}" for i in range(10)], [f"v{i}" for i in range(10)])
alg = Algebra(tuple([1] * 10), names=names)
alg.blade("v0v1")  # → v₀∧v₁
```

### Consequences

* Good, because silent misinterpretation is impossible
* Good, because the fix (custom names) is straightforward
* Neutral, because algebras with n > 9 are rare in practice
