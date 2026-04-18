---
status: accepted
date: 2026-04-19
deciders: edouard
---

# ADR-067: Basis Vectors Are Protected from In-Place Mutation

## Context and Problem Statement

`basis_vectors()`, `basis_blades()`, `locals()`, `pseudoscalar()`, and
`blade()` return Multivector objects that represent the algebra's canonical
basis. Calling `.name()` on these mutates them in-place — turning a basis
vector into a named symbolic variable and destroying the original reference:

```python
e0, e1 = alg.basis_vectors()
e0.name("t")   # e0 is now a symbolic "t", the basis vector is gone
```

This is surprising and error-prone. Users expect `e0` to remain the basis
vector and `.name()` to produce a new named quantity.

## Decision

Add a `_is_basis` flag to Multivector, set to `True` when returned by
`basis_vectors()`, `basis_blades()`, `locals()`, `pseudoscalar()`, and
`blade()`.

When `.name()` is called on a protected MV (`_is_basis=True`), it operates
on a copy instead of mutating in-place. The copy has `_is_basis=False`.
The original basis vector is unchanged.

```python
e0, e1 = alg.basis_vectors()
t = e0.name("t")   # t is a new named MV; e0 is still the basis vector
e0.name("t")        # returns a copy (discarded) — e0 unchanged
```

### Scope

Only `.name()` is guarded. Other in-place methods are not:

- `symbolic()` / `numeric()` change evaluation mode, not identity — valid
  on basis vectors.
- `anon()` removes a name — a no-op on unnamed basis vectors, and if
  `.name()` returns a copy, basis vectors can't become named in the first
  place.

### What is NOT protected

- `scalar()`, `vector()`, `rotor()` — user-constructed values, not
  canonical basis elements.
- Copies from arithmetic, `grade()`, `_copy_with` — the flag defaults to
  `False` so derived MVs are not protected.

## Consequences

- Basis vectors obtained from the algebra are immutable with respect to
  `.name()`. Users must capture the return value.
- `v = e1.name("v")` continues to work — the return value is the named copy.
- `e1.name("x")` without capturing the result is a silent no-op on `e1`.
  This is intentional: mutating a basis vector was the bug.
- Existing code that uses the `v = e1.name(...)` pattern (the vast majority)
  is unaffected.
- Code that relies on in-place mutation of basis vectors must change to
  capture the return value.
