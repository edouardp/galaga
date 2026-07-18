# SPEC-004: Product Backend Selection and Diagnostics

**Status:** Implemented

## Intent

Product backends may trade construction time, product time, and memory, but
must implement identical geometric and grade-selected products. Automatic
selection must avoid an unsafe eager general-Gram allocation.

## Backend contract

Every backend must provide:

- `multiply(left, right)` for the complete geometric product;
- `grade_selected_product(left, right, selector)` using homogeneous input
  grades and selected output grades;
- `left_action(bitmask)` returning a read-only dense matrix for left
  multiplication by one exterior basis blade;
- a stable diagnostic name.

The public `Algebra.left_action(value)` must combine basis-blade actions
linearly and return a read-only matrix. The general inverse uses this matrix as
its solve representation; the general exponential currently uses its infinity
norm to choose a safe scaling factor.

## Available backends

| Name | Allowed metric | Required behavior |
|---|---|---|
| `diagonal` | Exactly diagonal only | Store one output mask and factor for every blade pair |
| `packed` | Any | Eagerly pack every sparse blade-pair expansion |
| `lazy` | Any | Build higher left-blade actions on demand with bounded caching |
| `reference` | Any | Use dense Chevalley left-action matrices as a test oracle |
| `auto` | Any | Resolve by the policy below |

Explicit `diagonal` selection on a non-diagonal Gram matrix must fail. Explicit
`packed`, `lazy`, and `reference` selection overrides automatic policy and is
intended primarily for tests and diagnostics.

## Automatic policy

1. An exactly diagonal Gram matrix must select `diagonal`.
2. A general Gram matrix whose conservative packed estimate is at most
   64 MiB must select `packed`.
3. A larger general Gram estimate must select `lazy`.

The estimate is

```text
(dim * dim + 1) * sizeof(intp)
+ dim**3 * (sizeof(output_mask) + sizeof(float64))
```

where the output mask uses the smallest unsigned integer dtype capable of
holding `dim - 1`.

This is a worst-case final-storage estimate, not a measurement of actual term
density. It prevents an unexpectedly large eager table but may conservatively
choose lazy for a sparse high-dimensional metric.

## Exact diagonal classification

After accepted symmetry canonicalization, diagonal classification must use
exact array equality. It must not use `allclose`; ignoring a tiny nonzero cross
term would change the requested Clifford algebra.

## General-Gram construction

Packed and lazy backends must share the same sparse Chevalley recurrence.
Terms with the same output mask must be combined deterministically and sorted
by output mask. Only coefficients equal to exactly zero after combination may
be removed.

The packed backend stores flattened pair offsets, output masks, and factors in
read-only arrays.

The lazy backend must:

- retain scalar and vector actions as fixed base actions;
- build higher actions only when requested;
- retain cacheable higher actions in least-recently-used order;
- protect cache mutation for concurrent access;
- keep retained higher-action bytes at or below 64 MiB;
- return an oversized action without caching it;
- preserve correctness when recursive dependencies are evicted.

## Diagnostics

`Algebra.product_backend` returns the selected backend name.

`Algebra.packed_product_byte_estimate` returns the estimate used by automatic
selection.

`Algebra.product_cache_info` returns:

- `None` for non-lazy backends; or
- `(entries, retained_bytes, byte_budget)` for the lazy backend.

The cache counter covers retained higher-grade sparse actions. It does not
claim to measure fixed scalar/vector actions, shared dimension metadata,
multivector arrays, temporary construction objects, or Python object overhead.

## Backend equivalence

For every metric within the feasible reference dimension, tests must compare:

- dense multivector geometric products;
- basis-blade left actions;
- left and right contractions;
- Hestenes and Doran–Lasenby products;
- general multivector exponentials whose square is nonscalar;
- cache and no-cache lazy execution.

The dense reference backend must remain available even though it is not an
automatic production selection.
