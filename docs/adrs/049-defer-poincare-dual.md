---
status: deferred
date: 2026-03-31
deciders: edouard
---

# ADR-049: Defer Poincaré/Hodge Dual as Separate Function

## Context and Problem Statement

The library has `dual(x) = x ⌋ I⁻¹` (left contraction into inverse
pseudoscalar). The Poincaré/Hodge dual is `⋆x = xI⁻¹` (right geometric
product with inverse pseudoscalar). Should we add a separate function?

## How They Differ

For a grade-k blade, both give the same result — left contraction and
geometric product are equivalent when the left operand's grade ≤ the
right operand's grade.

They differ only on **mixed-grade multivectors**:

- `dual(x) = x ⌋ I⁻¹` — applies left contraction, which grade-filters.
  Each grade component is mapped independently.
- `poincare_dual(x) = x * I⁻¹` — applies the full geometric product,
  which can produce cross-grade terms.

For homogeneous blades (the vast majority of use cases), the results
are identical.

Both fail in degenerate algebras (PGA) where I is not invertible.
Use `complement()` for non-metric duality in those algebras.

## Decision Outcome

Defer. Do not add `poincare_dual()` as a library function.

### Rationale

- Identical to `dual()` on blades, which covers ~99% of use cases
- Adds API surface for a distinction most users will never encounter
- The mixed-grade case is niche enough that an explicit expression is clearer

### Workaround

Users who need the Hodge star on mixed-grade multivectors can write:

```python
from galaga import inverse

def poincare_dual(x):
    return x * inverse(x.algebra.pseudoscalar())
```

### Consequences

- Good, because the API stays simple
- Good, because users aren't confused by two near-identical dual functions
- Neutral, because the workaround is a two-line function
- Revisit if mixed-grade duality becomes a common request
