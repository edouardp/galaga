---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-080: Matrix Representations Use Public Linear Actions

## Context and problem statement

Galaga 1's matrix package constructs left-regular representations by reading
`Algebra._mul_index` and `_mul_sign`. Those tables assume every basis-blade
product has one output blade and one coefficient. A general Gram matrix can
produce several grades and terms, so the representation is both private and
mathematically insufficient for Galaga 2.

Compact representations present a separate issue. Their gamma matrices model
an abstract Clifford signature, but multiplying vector matrices represents
native exterior basis blades directly only when that basis is normalized and
orthogonal.

## Decision drivers

- Support left-regular representations for every numeric product backend.
- Preserve the user's native coefficient basis and exact roundtrip convention.
- Classify the abstract metric without discarding the native Gram matrix.
- Retain validated Pauli, Dirac, quaternion, and general compact behavior.
- Fail explicitly rather than represent a general-Gram exterior basis wrongly.
- Make private-table removal mechanically enforceable.

## Decision outcome

`galaga_matrix` imports `Algebra` and `Multivector` from `galaga.facade`.
Left-regular conversion calls the public `Algebra.left_action(value)` method.
The inverse reads the first matrix column and constructs through the public
algebra multivector factory.

Mode selection uses both basis-independent inertia and the native Gram matrix.
A metric receives automatic compact mode only when it is nondegenerate,
orthogonal, and normalized to vector squares `+1` or `-1`. Every other metric
uses left-regular mode.

Explicit compact conversion rejects nonorthogonal and non-normalized Gram
matrices with guidance toward left-regular mode. A compact general-Gram basis
transform is deferred until it has an independently validated exterior-basis
mapping and roundtrip oracle.

Until the Phase 8 top-level cutover, matrix tests also exercise Galaga 1 values.
That compatibility path materializes columns through the public geometric
product and never reads multiplication tables.

Architecture tests search the implementation for the retired private fields
and legacy numeric imports. Numeric tests verify multiplication, roundtrip, and
the generator relation against oblique and native-null Gram matrices.

## Consequences

- Good, because one public representation boundary works across all product
  backends and Gram matrices.
- Good, because left-regular matrices use the same stored basis as multivector
  coefficients.
- Good, because native-null bases are classified correctly even though their
  diagonal contains zeros.
- Good, because compact behavior remains unchanged where its basis assumptions
  are valid.
- Good, because source checks prevent accidental return to private tables.
- Cost, because general-Gram matrices currently use the larger left-regular
  representation.
- Cost, because the temporary Galaga 1 fallback computes a product per column.
- Follow-up complete in [ADR-082](082-matrix-provenance-is-package-owned.md):
  `MatrixRepr` now owns immutable matrix provenance and consumes only public
  Galaga 2 names, expressions, and presentation objects.
