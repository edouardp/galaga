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
e1, e2, e3 = alg.basis_vectors(symbolic=True)
e12 = (e1 * e2).name(latex=r"e_{12}")
e23 = (e2 * e3).name(latex=r"e_{23}")
e31 = (e3 * e1).name(latex=r"e_{31}")
```

The `.name()` calls are unnecessary (the blade convention already knows the
names), and the lazy products create `Gp` expression trees instead of leaf
blades. Using `.eval()` avoids the tree but is still per-blade boilerplate.

## Decision

Add two methods to `Algebra`:

1. **`basis_blades(k, *, symbolic=False)`** — returns a tuple of all grade-k
   basis blades in canonical bitmask order. Mirrors `basis_vectors()` for
   arbitrary grades.

2. **`locals(*, grades=None, symbolic=False, prefix=None)`** — returns a
   `dict[str, Multivector]` of all non-scalar basis blades, keyed by compact
   Python-safe local names. Designed for `locals().update(alg.locals())` in
   notebook cells and top-level scripts. `prefix` optionally overrides the
   generated Python-local prefix without changing blade rendering.

Both methods apply `BasisBlade.sign` so that signed conventions (e.g.
`b_sta(sigmas=True)` where σ₁ = γ₁γ₀ has sign −1 at the canonical
bitmask) produce blades with the correct coefficient.

The `locals().update()` pattern is a known CPython hack that works at
module scope and in notebook cells (Marimo, Jupyter) but not inside
functions. This is acceptable because GA notebook code lives in cells.

## Consequences

- Notebook boilerplate drops from N lines to one:
  `locals().update(alg.locals(grades=[1, 2], symbolic=True))`
- Dict keys are valid local variable names derived from the blade convention's
  basis-vector names, but they do not follow display style. For example,
  `blades=b_default(prefix="v", style="wedge")` renders `v₁∧v₂` while
  `locals()` exposes it as `v12`.
- Gamma conventions render as `γ₀`, `γ₁`, etc. and default to Python keys
  `g0`, `g1`, etc. (the ASCII mapping γ → `g`). Users who prefer the visual
  resemblance of `y` to γ can call `locals(prefix="y")`.
- Display overrides (e.g. σ₁ for STA bivectors) do NOT affect `locals()` keys.
  All blades without a `variable_hint` use `prefix` + canonical subscript.
- `variable_hints` on the convention declare idiomatic names for specific
  blades (e.g. pseudoscalar → `"I"`, quaternion bivectors → `"i"`, `"j"`,
  `"k"`). These are respected by `locals()` and override the prefix pattern.
- `locals(pss="I")` is syntactic sugar for the most common variable hint
  override — naming the pseudoscalar at call time.
- `basis_blades(k)` parameter is named `k` to match the standard GA
  variable for grade and the existing `grade(x, k)` function.
