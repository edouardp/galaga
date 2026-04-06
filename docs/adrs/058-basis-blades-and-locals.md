---
status: accepted
date: 2026-04-06
deciders: edouard
---

# ADR-058: basis_blades(k) and locals() for Bulk Blade Access

## Context

Notebooks frequently need named variables for higher-grade basis blades.
`basis_vectors()` only returns grade-1 blades, so users wrote boilerplate:

```python
e1, e2, e3 = alg.basis_vectors(lazy=True)
e12 = (e1 * e2).name(latex=r"e_{12}")
e23 = (e2 * e3).name(latex=r"e_{23}")
e31 = (e3 * e1).name(latex=r"e_{31}")
```

The `.name()` calls are unnecessary (the blade convention already knows the
names), and the lazy products create `Gp` expression trees instead of leaf
blades. Using `.eval()` avoids the tree but is still per-blade boilerplate.

## Decision

Add two methods to `Algebra`:

1. **`basis_blades(k, *, lazy=False)`** — returns a tuple of all grade-k
   basis blades in canonical bitmask order. Mirrors `basis_vectors()` for
   arbitrary grades.

2. **`locals(*, grades=None, lazy=False)`** — returns a `dict[str, Multivector]`
   of all non-scalar basis blades, keyed by ASCII name from the blade
   convention. Designed for `locals().update(alg.locals())` in notebook
   cells and top-level scripts.

Both methods apply `BasisBlade.sign` so that signed conventions (e.g.
`b_sta(sigmas=True)` where σ₁ = γ₁γ₀ has sign −1 at the canonical
bitmask) produce blades with the correct coefficient.

The `locals().update()` pattern is a known CPython hack that works at
module scope and in notebook cells (Marimo, Jupyter) but not inside
functions. This is acceptable because GA notebook code lives in cells.

## Consequences

- Notebook boilerplate drops from N lines to one:
  `locals().update(alg.locals(grades=[1, 2], lazy=True))`
- Dict keys follow the blade convention: `e1`, `e12`, `y0y1`, `s1`, etc.
  Renaming a blade changes the key in subsequent `locals()` calls.
- `basis_blades(k)` parameter is named `k` to match the standard GA
  variable for grade and the existing `grade(x, k)` function.
