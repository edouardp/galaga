---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-005: Expose Explicit Product and Duality Families

## Context and problem statement

The phrase “inner product” denotes several incompatible operations across GA
texts and libraries. “Dual” likewise covers metric duality, Hodge duality,
Poincare complement, and antimetric polarity. These operations agree in enough
simple examples that an ambiguous default can remain unnoticed.

Degenerate PGA metrics add another constraint: an inverse pseudoscalar does not
exist, while exterior complements and complementary-minor maps remain useful.

## Decision drivers

- Make convention choices readable at the call site.
- Keep scalar-valued pairings distinct from grade-selected products.
- Preserve useful operations in degenerate metrics.
- Support Eric Lengyel's RGA operations without changing conventional GA names.
- Derive related operations from a small set of shared primitives.

## Considered options

1. Expose one `inner_product` and one `dual` default.
2. Use mode arguments to select conventions.
3. Expose one stable name per mathematical definition.

## Decision outcome

Expose distinct named families:

- scalar product and exterior metric pairing;
- left/right contractions;
- Hestenes and Doran–Lasenby inner products;
- left/right exterior complements;
- inverse-pseudoscalar dual and undual;
- Hodge and weight duals;
- complement-based and metric-based regressive products;
- RGA antidot, antiproduct, interior, and transwedge operations.

The `|` operator is fixed to Doran–Lasenby inner for Galaga compatibility.
There is no unqualified core `inner_product` dispatcher. A facade may provide
one as an explicitly documented compatibility convenience.

Operations that require an invertible pseudoscalar fail on a degenerate metric.
They do not silently substitute a complement or pseudoinverse.

## Consequences

- Good, because call sites reveal the convention being used.
- Good, because PGA retains meaningful complement and antimetric operations.
- Good, because the RGA layer coexists with conventional Clifford operations.
- Cost, because the public API has more names to learn.
- Cost, because documentation must carefully distinguish operations that agree
  on vectors but differ for scalars or mixed grades.
