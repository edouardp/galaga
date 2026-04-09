---
status: accepted
date: 2026-04-10
deciders: edouard
---

# ADR-060: Chisolm Paper as Reference Test Suite

## Context and Problem Statement

Geometric algebra libraries need algebraic identity tests that go beyond
unit-level coverage of individual functions. We need a systematic,
externally-grounded set of tests that verify the mathematical relationships
between operations — the kind of tests that catch sign errors in
multiplication tables, incorrect grade projections, or broken product
identities.

## Decision Drivers

* Tests should be traceable to a published, peer-reviewed source
* The source should cover the full breadth of GA operations galaga implements
* Identities should be testable numerically with random multivectors
* The source should use conventions compatible with (or clearly mappable to)
  galaga's API

## Considered Options

1. Hestenes & Sobczyk, "Clifford Algebra to Geometric Calculus" (1984)
2. Doran & Lasenby, "Geometric Algebra for Physicists" (2003)
3. Dorst, Fontijne & Mann, "Geometric Algebra for Computer Science" (2007)
4. **Chisolm, "Geometric Algebra" (arXiv:1205.5935)**

## Decision Outcome

Chosen option: **Chisolm (arXiv:1205.5935)**, because it is a comprehensive,
self-contained introduction that derives all major identities from axioms,
numbers every equation and theorem, and covers the full range of operations
galaga implements — from axioms through products, involutions, duality,
commutators, projections, reflections, rotations, and Lorentz boosts.

Paper URL: https://arxiv.org/abs/1205.5935

### Test Files and Categories

Five test files in `packages/galaga/tests/`, totalling 309 tests:

**test_chisolm_foundations.py** — Axioms and foundational properties (§2–3)
- Axiom 4: vector square is scalar
- Symmetrized product = inner product
- GP decomposition: uv = u·v + u∧v (Eq. 1.6)
- Outer product vanishes iff dependent (Theorem 2)
- Blade subspace membership via wedge (Theorem 3)
- Same subspace iff scalar multiple (Theorem 4)
- Orthogonal wedge = geometric product (Theorem 1)
- Orthogonality via contraction (Theorem 5)
- Vector inverse (Eq. 1.4)

**test_chisolm_products.py** — Product identities (§4)
- Inner product lowers grade (Theorem 5)
- Outer product raises grade (Theorem 7)
- aA_r = a⌋A_r + a∧A_r (Eq. 1.48)
- Grade structure of A_r B_s (Theorem 6)
- Outer product associativity (Theorem 10)
- Contraction-wedge associativity: A⌋(B⌋C) = (A∧B)⌋C (Theorem 10)
- Wedge is highest grade of GP (Eq. 1.80)
- Outer commutativity: A_r∧B_s = (-1)^{rs} B_s∧A_r (Eq. 2.38)
- Inner commutativity: A_r⌋B_s = (-1)^{r(s-1)} B_s⌊A_r (Eq. 2.36)
- Contraction expansion (Theorem 9, Eq. 1.72)
- Useful identities (Eq. 1.62, Eq. 1.85)

**test_chisolm_involutions.py** — Involutions and scalar product (§5.1–5.4)
- Grade involution: (-1)^r per grade (Eq. 2.2)
- Double involution = identity
- Even/odd extraction via involution (Eq. 2.4)
- Involution is algebra homomorphism
- Reversion: (-1)^{r(r-1)/2} per grade (Eq. 2.14)
- Double reversion = identity
- Reversion is anti-homomorphism (Eq. 2.12)
- Clifford conjugation (Eq. 2.42)
- Scalar part commutes and is cyclic (Eq. 2.25, 2.26)
- Scalar product symmetry and invariance (Eq. 2.29, 2.30)
- Reversion of inner/outer products (Eq. 2.20)
- Term-by-term sign relation (Eq. 2.22)
- Versor inverse via reverse/norm (Theorem 14)
- Blade squared is scalar
- Versor norm product (Theorem 13)

**test_chisolm_transformations.py** — Geometry and physics (§6–7, §9.5.2)
- Projection + rejection = original (Theorem 15)
- Projection lies in subspace, rejection is orthogonal
- Reflection preserves inner product (Eq. 3.22)
- Reflection formula: v' = -nvn⁻¹ (Eq. 1.28)
- Reflection in subspace (Eq. 3.24)
- Reflection of pseudoscalar (Eq. 3.28)
- Rotation formula and grade/inner-product preservation (Eq. 3.30)
- Pseudoscalar invariant under rotation
- Rotor properties: R~R = 1, double reflection = rotation
- Complex structure in Cl(2,0): (e₁e₂)² = -1
- Quaternion structure in Cl(3,0)
- Cross product via duality (§6.2)
- Hyperbolic rotors (Lorentz boosts) in Cl(1,3) (§9.5.2)

**test_chisolm_dual_commutator.py** — Duality and commutators (§5.5–5.6, §9.4)
- dual(AB) = A·dual(B)
- dual(A∧B) = A⌋dual(B) (Eq. 2.58)
- dual(A⌋B) = A∧dual(B) (Eq. 2.58)
- Pseudoscalar commutation (Eq. 2.54)
- A∧dual(A) ∝ I for invertible blades (Eq. 2.57)
- Leibniz rule for commutator (Eq. 2.62)
- Jacobi identity
- Bivector commutator preserves grade
- Vector commutator decomposition (Eq. 2.65)
- Bivectors closed under commutation (Lie algebra)
- Skew-symmetric operator via bivector contraction (§9.4)

### Convention Mapping

| Chisolm | galaga | Notes |
|---------|--------|-------|
| [A, B] = ½(AB−BA) | `lie_bracket(A, B)` | NOT `commutator` which omits the ½ |
| {A, B} = ½(AB+BA) | `jordan_product(A, B)` | NOT `anticommutator` which omits the ½ |
| A⌋B (left inner) | `left_contraction(A, B)` | |
| A⌊B (right inner) | `right_contraction(A, B)` | |
| dual(A) = A·I⁻¹ | `dual(A)` | |
| A† (reverse) | `reverse(A)` | |
| A* (grade involution) | `involute(A)` | |
| A‡ (Clifford conjugate) | `conjugate(A)` | |

### Test Design

- All tests run across multiple algebras via parametrized fixtures:
  Cl(2,0), Cl(3,0), Cl(1,3), and Cl(3,0,1) where applicable
- Random multivectors with fixed seeds for reproducibility
- Tests that require minimum dimension skip gracefully (17 skips total,
  all for Cl(2,0) where the identity is vacuous)
- Each test class docstring cites the exact equation/theorem number

### Consequences

* Good, because every identity is traceable to a specific equation in a
  published paper
* Good, because random testing catches edge cases that hand-picked examples miss
* Good, because the tests cover all four metric signatures (Euclidean,
  Minkowski, degenerate, mixed)
* Neutral, because the paper doesn't cover PGA-specific operations (meet, join)
  or CGA — those need separate test sources
