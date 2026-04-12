# Review: Cohoe, "Rigorous Development of Geometric Algebra" (2024)

Source: `/Users/edouard/Downloads/geo.pdf`
David Cohoe, September 18, 2024

## Overview

This is a rigorous, axiom-from-scratch development of geometric algebra over
a commutative ring R with an arbitrary symmetric bilinear form B. It builds
the exterior algebra first, constructs isomorphisms E : G → ∧V and G : ∧V → G,
then derives grading, products, and versors. The paper is 30 pages, 6 sections.

The approach is more foundational than Chisolm — it proves things we typically
take as axioms (e.g. that ϕ: V → G is injective, that the grading exists).
Many results overlap with what we already test from Chisolm, but there are
several identities and structural properties that are new or stated differently.

## Comparison with Existing Chisolm Test Suite

Already covered by our Chisolm tests:
- Vector square is scalar (Axiom 4 / Thm 2.5 polarisation)
- Grade involution: A* = (-1)^k A for k-vectors (Thm 4.3)
- Reverse: A† = (-1)^{k(k-1)/2} A for k-vectors (Thm 4.4)
- Grade involution is involution: A** = A (Thm 2.3)
- Reverse is involution: A†† = A (Thm 2.4)
- Product grade structure: AB = Σ ⟨AB⟩_{|r-s|+2i} (Thm 4.14)
- vX = v⌋X + v∧X (Thm 5.6)
- Left/right contraction definitions via grade projection
- Scalar product symmetry: A*B = B*A (Thm 5.4)
- Versor grade preservation (Thm 6.3)

## New / Differently-Stated Testable Identities

### Section 2: Basic Definitions

**Thm 2.5 — Polarisation identity (anticommutator)**
```
ab + ba = 2B(a,b)   for vectors a, b
```
We test this in Chisolm, but Cohoe states it for arbitrary bilinear form B
(not just orthonormal bases). Worth ensuring our test covers non-orthogonal
random vectors, not just basis vectors.

### Section 3: Left Contraction Properties

**Thm 3.5 / 3.15 — Left contraction of vector with scalar is zero**
```
a⌋α = 0   for vector a, scalar α
```

**Thm 3.7 / 3.17 — Antisymmetry of iterated vector contractions**
```
a⌋(b⌋X) + b⌋(a⌋X) = 0   for vectors a, b and multivector X
```
This is a strong identity we don't currently test.

**Thm 3.8 / 3.20 — Left contraction is nilpotent on vectors**
```
a⌋(a⌋X) = 0   for vector a and multivector X
```

**Thm 3.18 — Grade involution commutes with left contraction (with sign)**
```
(a⌋X)* = -a⌋(X*)   for vector a and multivector X
```

**Thm 3.19 — Generalised anticommutator**
```
aX - X*a = 2(a⌋X)   for vector a and multivector X
```
This is a powerful generalisation of Thm 2.5. We should test this.

### Section 4: Grading

**Thm 4.3 — Grade involution on k-vectors**
```
X* = (-1)^k X   for k-vector X
```
(Already tested, but Cohoe proves it from the exterior algebra isomorphism.)

**Thm 4.4 — Reverse on k-vectors**
```
X† = (-1)^{k(k-1)/2} X   for k-vector X
```
(Already tested.)

**Thm 4.5 / 4.6 — Involutions commute with E and G maps**
Not directly testable (we don't expose E/G maps), but the consequence is
that involutions respect grade, which we do test.

**Thm 4.7 — Grade involution preserves grade**
```
⟨X⟩_k is a k-vector  ⟹  (⟨X⟩_k)* is a k-vector
```

**Thm 4.8 — Reverse preserves grade**
```
⟨X⟩_k is a k-vector  ⟹  (⟨X⟩_k)† is a k-vector
```

**Thm 4.9 — Grade projection commutes with grade involution**
```
⟨X⟩_n* = ⟨X*⟩_n
```

**Thm 4.10 — Grade projection commutes with reverse**
```
⟨X⟩_n† = ⟨X†⟩_n
```

**Thm 4.11 — Scalar part is invariant under reverse**
```
⟨A†⟩ = ⟨A⟩
```

**Thm 4.12 — Grade projection commutes with vector left contraction**
```
⟨a⌋X⟩_n = a⌋⟨X⟩_{n+1}   for vector a
```

**Thm 4.14 — Product grade structure (the "grade selection rule")**
```
AB = Σ_{i=0}^{min(r,s)} ⟨AB⟩_{|r-s|+2i}
```
for r-vector A and s-vector B. (Already tested, but worth cross-checking.)

### Section 5: Other Operations

**Thm 5.2 — Vector left contraction equals grade-lowering part**
```
⟨aX⟩_{n-1} = a⌋X   for vector a and n-vector X
```

**Thm 5.6 — Vector product decomposition**
```
vX = v⌋X + v∧X
Xv = X⌊v + X∧v
```
(Already tested for the first form.)

**§5.2 — Inner product identities (stated without proof)**
```
(A⌋B)* = A*⌋B*
(A⌊B)* = A*⌊B*
(A·B)* = A*·B*
(A⌋B)† = B†⌊A†
(A⌊B)† = B†⌋A†
(A·B)† = B†·A†
```
These are important identities relating involutions to contractions.
The reverse-contraction swap identities are particularly useful.

**§5.2 — Vector inner products all agree**
```
a⌋b = a⌊b = a·b = B(a,b)   for vectors a, b
```

**Thm 5.3 — Scalar product of different-grade homogeneous elements is zero**
```
A*B = 0   when grade(A) ≠ grade(B)
```
(where * is scalar product ⟨AB⟩)

**Thm 5.4 — Scalar product is symmetric**
```
A*B = B*A
```

**Thm 5.5 — Norm squared is invariant under reverse**
```
|A†|² = |A|²
```

### Section 6: Versors

**Thm 6.1 — Involutions of versors are versors**
Not directly testable numerically (versor-ness isn't a property we check),
but the consequence is that involutions of products of vectors are products
of vectors.

**Thm 6.2 — Versor norm identity**
```
A†A = AA† = |A|²   for versor A
```

**Thm 6.3 — Sandwich product preserves grade**
```
grade(A†XA) = grade(X)   for versor A, homogeneous X
```
(Already tested.)

**Thm 6.4 — Sandwich product distributes over outer product**
```
(A†XA) ∧ (A†YA) = |A|² A†(X∧Y)A   for versor A
```
This is a very nice identity we don't currently test.

## Recommended New Tests (Priority Order)

### High Priority — New identities not in Chisolm suite

1. **Generalised anticommutator** (Thm 3.19):
   `aX - X*a = 2(a⌋X)` for vector a, arbitrary multivector X

2. **Antisymmetry of iterated contractions** (Thm 3.7/3.17):
   `a⌋(b⌋X) + b⌋(a⌋X) = 0` for vectors a, b

3. **Nilpotency of vector contraction** (Thm 3.8/3.20):
   `a⌋(a⌋X) = 0` for vector a

4. **Contraction-involution identities** (§5.2):
   - `(A⌋B)* = A*⌋B*`
   - `(A⌊B)* = A*⌊B*`
   - `(A⌋B)† = B†⌊A†`
   - `(A⌊B)† = B†⌋A†`

5. **Sandwich distributes over outer product** (Thm 6.4):
   `(A†XA) ∧ (A†YA) = |A|² A†(X∧Y)A`

6. **Versor norm identity** (Thm 6.2):
   `A†A = AA† = |A|²` for products of vectors

### Medium Priority — Structural / grade properties

7. **Scalar part invariant under reverse** (Thm 4.11):
   `⟨A†⟩ = ⟨A⟩`

8. **Grade projection commutes with involutions** (Thm 4.9/4.10):
   - `⟨X⟩_n* = ⟨X*⟩_n`
   - `⟨X⟩_n† = ⟨X†⟩_n`

9. **Grade projection commutes with vector contraction** (Thm 4.12):
   `⟨a⌋X⟩_n = a⌋⟨X⟩_{n+1}`

10. **Vector contraction with scalar is zero** (Thm 3.15):
    `a⌋α = 0`

11. **Norm squared invariant under reverse** (Thm 5.5):
    `|A†|² = |A|²`

12. **Scalar product vanishes for different grades** (Thm 5.3):
    `⟨AB⟩ = 0` when grade(A) ≠ grade(B)

13. **Xv decomposition** (Thm 5.6, second form):
    `Xv = X⌊v + X∧v`

### Low Priority — Already well-covered or hard to test

14. Polarisation identity (Thm 2.5) — already tested
15. Grade involution/reverse formulas (Thm 4.3/4.4) — already tested
16. Product grade structure (Thm 4.14) — already tested
17. Vector product decomposition first form (Thm 5.6) — already tested

## Notes

- The paper works over commutative rings, not just fields. Our library works
  over floats, so all identities apply.
- Cohoe uses † for reverse (same as our convention) and * for grade involution
  (we use `involute`). His "scalar product" A*B = ⟨AB⟩ uses * differently
  from grade involution — context-dependent in the paper.
- The paper's left contraction definition via universal property construction
  matches the standard grade-projection definition we use.
- Degenerate signatures (PGA) should be included in test fixtures since
  Cohoe's proofs don't require non-degeneracy.
