# Terathon/RGA Convention Layer — Implementation Plan

## Problem Statement

The Terathon review (`docs/review-terathon-ga-foundations.md`) identifies a
coherent set of exterior-algebra operations that complement Galaga's existing
GA operations. These provide an alternative mathematical lens — particularly
useful for PGA where degenerate metrics make some GA-standard operations
ill-defined.

Galaga's posture: keep existing GA operations stable; add RGA-style operations
under explicit names as a parallel convention layer.

## Key Formulas

### Metric Exomorphism Matrix G

For a diagonal metric with signature `(s₁, s₂, ..., sₙ)`, the extended metric
G is a 2ⁿ × 2ⁿ diagonal matrix:

    G[bitmask, bitmask] = prod(signature[i] for each bit i set in bitmask)

All off-diagonal entries are zero. The scalar entry G[0,0] = 1 (empty product).

### Metric Antiexomorphism Matrix 𝔾

The antimetric is also diagonal:

    𝔾[bitmask, bitmask] = prod(signature[i] for each bit i NOT in bitmask)

Satisfies the identity: `G · 𝔾 = det(metric) · I`

For non-degenerate metrics, `𝔾 = det(metric) · G⁻¹`. For degenerate metrics
(det=0), both G and 𝔾 are independently meaningful even though their product
is zero.

### Transwedge Product

    transwedge(a, b, k) = Σ over grade-k basis blades c of:
        (left_complement(c) ∨ a) ∧ (b ∨ right_hodge_dual(c))

- Order 0 reduces to wedge: `transwedge(a, b, 0) = a ∧ b`
- Signed sum reconstructs GP: `gp(a, b) = Σₖ (-1)^(k(k-1)/2) · transwedge(a, b, k)`
- For vectors: `transwedge(a, b, 1) = metric_inner_product(a, b)`

### Duals

- Right Hodge dual: `right_hodge_dual(u) = right_complement(G · u)`
- Left Hodge dual: `left_hodge_dual(u) = left_complement(G · u)`
- Non-degenerate identity: `right_hodge_dual(u) = gp(reverse(u), I)`
- Hodge identity: `a ∧ right_hodge_dual(b) = metric_inner_product(a, b) · I`
  for same-grade a, b
- Double-dual: `dual(dual(u)) = (-1)^(gr·ag) · det(metric) · u`

### Antidot Product

    antidot_product(a, b) = a^T · 𝔾 · b

De Morgan identity: `antidot(a, b) = complement(metric_inner_product(left_complement(a), left_complement(b)))`

## Task Breakdown

### Task 1: `extended_metric_matrix()` and `metric_inner_product()`

Add `Algebra.extended_metric_matrix()` returning the cached 2ⁿ×2ⁿ diagonal
numpy array G. Add `metric_inner_product(A, B)` computing `A.data @ G @ B.data`
as a scalar multivector.

Key identity: `metric_inner_product(A, B) == scalar_product(A, reverse(B))`
for diagonal metrics.

Tests:

- `metric_inner_product(e12, e12) == 1` in Cl(3,0)
- Mixed grades return 0
- Identity with `scalar_product(A, reverse(B))` for random MVs
- Indefinite signatures produce correct signs
- PGA: null blade self-product is 0

### Task 2: `left_complement()` and `right_complement()` alias

Add `left_complement(A)` where the sign differs from right complement by
`(-1)^(grade × antigrade)`. Add `right_complement = complement` as alias.

Tests:

- `left_complement(right_complement(A)) == (-1)^(gr*ag) * A`
- `left_complement(e_S) ∧ e_S` gives correct sign × I
- Random MVs in Cl(3,0), Cl(1,3), Cl(3,0,1)

### Task 3: Antimetric operations

Add `Algebra.metric_antiexomorphism_matrix()` (diagonal, `𝔾[B,B] = prod(sig[i]
for i NOT in B)`), `metric_apply(A)`, `antimetric_apply(A)`, and
`antidot_product(A, B)`.

Tests:

- `G @ 𝔾 == det(metric) * I` for non-degenerate
- PGA: `G @ 𝔾 == 0` but both individually meaningful
- De Morgan identity for antidot

### Task 4: `right_hodge_dual()` and `left_hodge_dual()`

Compose metric application with complement:

- `right_hodge_dual(A) = complement(metric_apply(A))`
- `left_hodge_dual(A) = left_complement(metric_apply(A))`

Tests:

- Hodge identity: `op(A, right_hodge_dual(B)) == metric_inner_product(A,B) * I`
- Non-degenerate: `right_hodge_dual(A) == gp(reverse(A), I)`
- PGA: works where `dual()` raises
- Double-dual formula

### Task 5: Audit `antiwedge` vs `regressive_product`

Compare Galaga's `rp(A,B) = complement(op(complement(A), complement(B)))` with
RGA antiwedge on all basis blade pairs. If signs match, alias. If differ,
implement separately and document the relationship.

Tests:

- All basis blade pairs in Cl(3,0) and Cl(3,0,1)
- PGA meet examples

### Task 6: `antireverse()` and `geometric_antiproduct()`

- `antireverse(A)`: sign `(-1)^(ag*(ag-1)/2)` where ag = n - grade
- `geometric_antiproduct(A, B) = complement(gp(left_complement(A), left_complement(B)))`

Tests:

- Sign pattern verification
- De Morgan relationship with GP
- PGA sandwich formula

### Task 7: `transwedge(A, B, k)` (experimental)

Reference implementation iterating over grade-k basis blades. Mark experimental.

Tests:

- `transwedge(A, B, 0) == op(A, B)`
- Signed sum reconstructs `gp(A, B)` for random MVs
- For vectors: order-1 = metric_inner_product
- Zero when k > gr(A) or k > gr(B)

### Task 8: Bulk/weight parts and weight duals

- `bulk_part(A) = metric_apply(A)` (semantic alias)
- `weight_part(A) = antimetric_apply(A)` (semantic alias)
- `right_weight_dual(A) = right_complement(antimetric_apply(A))`
- `left_weight_dual(A) = left_complement(antimetric_apply(A))`

Tests:

- PGA line decomposition
- Weight dual identities

### Task 9: `Notation.lengyel()` and `b_rga()` blade convention

Notation preset:

- GP → ⟑, antiproduct → ⟇
- Right complement → overline, left complement → underline
- Hodge dual → A^★, weight dual → A^☆
- Clifford conjugation → A^‡ (double dagger) — NOT overline
- Reverse → tilde, antireverse → tilde-below

Blade convention `b_rga()`:

- 1-indexed, e₄ null
- Cyclic bivector order: e₂₃, e₃₁, e₁₂, e₄₁, e₄₂, e₄₃
- Trivector order: e₄₂₃, e₄₃₁, e₄₁₂, e₃₂₁
- Antiscalar as 𝟙

### Task 10: Documentation — conventions comparison

A docs page explaining the relationship between GA and RGA operations: where
they agree, where they disagree, when to use which, with formulas.

## Dependency Graph

```
Task 1 (metric G, metric_inner_product)
  ├── Task 3 (antimetric, antidot, metric_apply)
  │     ├── Task 8 (bulk/weight parts and weight duals)
  │     └── Task 4 (Hodge duals) ← also needs Task 2
  ├── Task 7 (transwedge) ← also needs Tasks 2, 4, 5
  └── Task 4 (Hodge duals)

Task 2 (left_complement)
  ├── Task 3 (antidot De Morgan test)
  ├── Task 5 (antiwedge audit)
  ├── Task 6 (antiproduct)
  └── Task 7 (transwedge)

Task 5 (antiwedge)
  └── Task 7 (transwedge uses ∨)

Task 6 (antireverse, antiproduct)
  └── Task 8 (weight dual identity test)

Tasks 1–8 → Task 9 (notation preset)
Tasks 1–9 → Task 10 (documentation)
```

## Actions to Avoid

- Do not rename `scalar_product()` to mean the metric-induced inner product.
- Do not change `dual()` semantics.
- Do not change the `|` operator.
- Do not adopt "the only correct convention" wording in docs.
- Do not add Python operators for transwedge or antiwedge before named functions
  and sign conventions are stable.
