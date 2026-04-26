---
status: accepted
date: 2026-04-26
deciders: edouard
---

# ADR-002: Compact Basis via Periodicity Recursion with Sign-Flip

## Context and Problem Statement

The compact representation needs gamma matrices (basis vector matrices) for
arbitrary Cl(p,q). The standard approach uses the periodicity isomorphism
`Cl(p+1, q+1) ≅ Cl(p, q) ⊗ M(2, ℝ)` to build larger algebras from smaller
ones. This works when both p and q are positive, but pure-positive Cl(p,0)
and pure-negative Cl(0,q) cannot be reduced this way.

Options considered:

1. **Pseudoscalar tensor product**: use the pseudoscalar of the sub-algebra
   to construct new generators via `P ⊗ σ₁`, `P ⊗ σ₃`. This fails when the
   pseudoscalar doesn't anticommute with all existing generators (odd
   dimensions).

2. **Sign-flip from mixed case**: build Cl(p-1, 1) (which the mixed recursion
   handles) and multiply the last generator by `i` to flip its square from
   -1 to +1, giving Cl(p, 0). Symmetric approach for Cl(0, q).

3. **Explicit construction per signature class**: hardcode matrices for each
   (p-q) mod 8 class. Correct but tedious and error-prone.

## Decision Outcome

Use approach 2: sign-flip from the mixed case.

- **Named base cases**: Cl(1,0), Cl(0,1), Cl(2,0), Cl(0,2), Cl(1,1) are
  hardcoded (1×1 or 2×2 matrices).
- **Named special cases**: Cl(3,0)/Cl(0,3) use Pauli matrices, Cl(1,3)/Cl(3,1)
  use Dirac matrices — matching textbook conventions exactly.
- **Mixed recursion** (p ≥ 1, q ≥ 1): `Cl(p+1,q+1) ≅ Cl(p,q) ⊗ M(2,ℝ)`.
  Existing generators are lifted as `γ_i ⊗ σ₃`, new positive generator is
  `I ⊗ σ₁`, new negative generator is `I ⊗ iσ₂`.
- **Pure positive** (p ≥ 3, q = 0): build Cl(p-1, 1) via mixed recursion,
  then multiply the last (negative-square) generator by `i`.
- **Pure negative** (p = 0, q ≥ 3): build Cl(1, q-1) via mixed recursion,
  then multiply the first (positive-square) generator by `i`.

### Consequences

- Good, because the mixed recursion is well-understood and provably correct
- Good, because the sign-flip trick is simple: `(iγ)² = i²γ² = -γ²`
- Good, because named special cases produce exactly the textbook Pauli/Dirac
  matrices, not some arbitrary equivalent representation
- Neutral: the resulting matrices for general signatures are not unique — a
  different recursion path would give a different (but equivalent)
  representation
- Verified: Clifford relations (squares and anticommutation) pass for all
  Cl(p,q) with p+q ≤ 8
