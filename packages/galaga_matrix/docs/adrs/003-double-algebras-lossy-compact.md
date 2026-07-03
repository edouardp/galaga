---
status: superseded
date: 2026-04-26
deciders: edouard
superseded_by: 005-strict-inverses-and-spinor-conventions.md
---

# ADR-003: Double Algebras Have Lossy Compact from_matrix

Superseded by [ADR-005](005-strict-inverses-and-spinor-conventions.md).
Compact `from_matrix` now raises when the selected compact representation is
not injective, instead of silently returning a least-squares projection.

## Context and Problem Statement

The Atiyah-Bott-Shapiro classification shows that some Clifford algebras are
"double" — isomorphic to a direct sum of two matrix algebras:

- `(q - p) mod 8 = 7`: Cl(p,q) ≅ M(k, ℝ) ⊕ M(k, ℝ)
- `(q - p) mod 8 = 3`: Cl(p,q) ≅ M(k, ℍ) ⊕ M(k, ℍ)

Examples: Cl(1,0), Cl(0,3), Cl(2,1), Cl(5,0).

For these algebras, the compact representation is an irreducible representation
of one summand. It maps 2ⁿ basis blades into a k×k matrix space that has fewer
real degrees of freedom than 2ⁿ. Multiple distinct multivectors map to the same
matrix — the representation is not injective.

Options considered:

1. **Block-diagonal representation**: use two copies of the irreducible
   representation, one for each summand. This doubles the matrix size but
   makes `from_matrix` exact.

2. **Accept the loss**: document that `from_matrix` is lossy for double
   algebras. `to_matrix` still works (it's a valid algebra homomorphism),
   but the roundtrip loses information.

3. **Refuse to convert**: raise an error for double algebras in compact mode.

## Decision Outcome

Accept the loss (option 2).

- `to_matrix(mv, mode="compact")` works for all non-degenerate algebras —
  it's a valid algebra homomorphism regardless of whether the algebra is
  simple or double.
- `from_matrix(alg, mat, mode="compact")` uses least-squares to recover
  coefficients. For simple algebras this is exact. For double algebras it
  returns the best-fit multivector, which may differ from the original.
- Users who need exact roundtrips should use `mode="left-regular"`.

### Consequences

- Good, because `to_matrix` compact is universally available for non-degenerate
  algebras — no surprising errors
- Good, because the product homomorphism `M(ab) = M(a)M(b)` holds regardless
- Bad, because `from_matrix` silently returns wrong results for double algebras
  rather than raising an error
- Mitigation: documented in README and in this ADR. The `_classify` function
  identifies double algebras, so a future version could warn or raise.

### Double algebras up to n=8

| Algebra | s = (q-p) mod 8 | Type |
|---|---|---|
| Cl(1,0) | 7 | ℝ ⊕ ℝ |
| Cl(2,1) | 7 | ℝ ⊕ ℝ |
| Cl(3,2) | 7 | ℝ ⊕ ℝ |
| Cl(4,3) | 7 | ℝ ⊕ ℝ |
| Cl(0,3) | 3 | ℍ ⊕ ℍ |
| Cl(1,4) | 3 | ℍ ⊕ ℍ |
| Cl(5,0) | 3 | ℍ ⊕ ℍ |
