---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-003: Use Exterior Bitmasks and Immutable Dense Values

## Context and problem statement

A nonorthogonal basis separates an exterior blade from the corresponding
geometric word. For example, `e_i wedge e_j` is a pure grade-two basis blade,
while `e_i e_j` also contains the scalar `G[i,j]`.

The implementation needs a stable coefficient meaning that does not depend on
whether the metric happens to be diagonal. It also needs safe sharing of basis
values and dimension metadata.

## Decision drivers

- Preserve familiar dense NumPy arithmetic for modest dimensions.
- Make grades and exterior products metric-independent.
- Give every coefficient slot the same meaning in every metric.
- Prevent mutation from invalidating caches, equality, or hashes.
- Retain simple interoperability through numeric arrays.

## Considered options

1. Store coefficients of geometric words in the native basis.
2. Store sparse dictionaries keyed by blades.
3. Store dense coefficients in a bitmask-indexed exterior basis.

## Decision outcome

Use a dense `float64` array of length `2**n`. Mask `S` always means the
ascending exterior blade selected by `S`, never an unexpanded geometric word.
The Gram matrix affects products, not storage layout.

Multivector constructors copy and freeze coefficient arrays. Every value holds
an identity reference to one algebra. Binary operations require identical
parent algebra objects.

Metric-independent metadata is cached by vector dimension and shared as
read-only arrays.

The public `.data` property is the explicit NumPy coefficient-array boundary.
`Multivector` does not implement `__array__`, `__array_ufunc__`, or
`__array_function__`. Checked scalar `__float__` conversion is separate from
coefficient-array interoperability.

## Consequences

- Good, because exterior coordinates survive arbitrary basis changes cleanly.
- Good, because wedge, grades, involutions, and complements do not depend on a
  multiplication backend.
- Good, because cached canonical basis values cannot be mutated accidentally.
- Good, because generic NumPy code cannot silently reinterpret a multivector
  as an unstructured coefficient array.
- Cost, because storage is exponential and includes zero coefficients.
- Cost, because sparse or grade-specialized values require a future separate
  representation decision.
