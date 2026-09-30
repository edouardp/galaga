---
status: accepted
date: 2026-09-29
deciders: edouard
---

# ADR-157: Display Algebras by Their Simplest Exact Metric Form

## Context and problem statement

The Galaga 2 facade represented an algebra as
`Algebra(numeric=<galaga.core.Algebra object at ...>)`. This exposed a memory
address instead of the algebra's defining metric, particularly when the final
expression in a Marimo cell was an `Algebra`. The earlier migration-time
contract is recorded in [ADR-097](097-concrete-display-contracts-outlive-legacy-rendering.md).

The numeric core normalizes every constructor form to a Gram matrix. A display
based only on how the object was constructed would give different descriptions
to equivalent metrics and could lose the order of a user-supplied signature.

## Decision outcome

Derive the facade algebra display from the stored metric, using the first exact
form that describes it in this order:

1. `Algebra(p=..., q=..., r=...)` when the ordered diagonal is precisely null,
   positive, then negative, with entries in `{0, 1, -1}`.
2. `Algebra(sig=[...])` when the diagonal has entries in `{0, 1, -1}` but its
   order is not the `p,q,r` default.
3. `Algebra(gram=[[...], ...])` for every other metric, retaining every Gram
   entry. In notebook LaTeX, show the Gram matrix inline as a `smallmatrix`.
   Colour exact zero entries `#bbbbbb`, matching the algebra product tables;
   leave nonzero entries unchanged, however small.

Format Gram entries with the active `DisplayPolicy.coefficient_precision`,
using the same significant-digit rule as `bilinear_form_table()`. Preserve
each numeric entry in the stored Gram matrix; formatting changes only the
displayed text. A small nonzero may use scientific notation and must never
be coloured as zero.

The same notebook colour applies to the entire `p=0`, `q=0`, or `r=0` term in
the first form, including its label and equals sign. Plain `repr` keeps these
terms uncoloured.

The plain `repr` and notebook `_repr_latex_` append `n`, the vector-space
dimension. They append `is_degenerate=True` only when the metric is degenerate
and `non_diagonal=True` only when the stored Gram matrix has off-diagonal
entries. For example:

`Algebra(p=3, q=0, r=1) [n=4, is_degenerate=True]`

`non_diagonal` describes the stored basis, not an invariant of the algebra:
the same form may have a diagonal Gram matrix after a basis change. The
degeneracy flag comes from the core's metric classification. `dim` is omitted
because it denotes the multivector coefficient-space dimension `2**n`, not
the number of basis vectors. Matrix numbers retain round-trip decimal
precision in the plain representation. This is a metric description, not a
stable serialization of presentation, provenance, model, backend, or
constructor arguments.

## Consequences

- Equivalent numeric metrics have the same displayed metric form, including
  algebras created from a preset or `Algebra.from_numeric`.
- Reordered signatures remain visibly reordered instead of being summarized by
  inertia alone. Off-diagonal and non-unit Gram entries are never discarded.
- Notebook output has no numeric-owner memory address and shows a real matrix
  for metrics that require one.
- This replaces only the algebra-repr contract in ADR-097; multivector display
  and arithmetic are unchanged.
