---
status: accepted
date: 2026-09-29
deciders: edouard
---

# ADR-158: Renderable Basis Factory Sequences

## Context

`Algebra.locals()` displays its names and blades as a LaTeX table. The
`basis_vectors()` and `basis_blades(k)` factories return tuples, which are
useful for unpacking and indexing but render as raw Python collections in
notebooks. A table should show only the blades selected by the factory.

Native coefficient storage and conventional presentation can differ. For
example, quaternion bivectors occupy native masks `3, 5, 6`, labeled `k, j, i`,
while their conventional presentation is `i, j, k`. Showing one order and
iterating in another makes indexing and unpacking difficult to predict.

## Decision

`basis_vectors()` and `basis_blades(k)` return `BasisMultivectors`, a tuple
subclass containing the requested native multivectors in the captured
`DisplayOrder`, filtered to the requested grade. Tuple indexing, slicing,
unpacking, iteration, and equality remain available.

The collection captures the active presentation and renders a two-column
LaTeX table of sequence index and basis blade. Table rows follow iteration
order, with consecutive zero-based indices identifying the values obtained
with `[index]`. Blade values
render through their multivectors, retaining preset signs and labels. The
factory's grade selection limits the table to the requested blades.

### Enumeration revision (2026-10-10)

The public collection's iteration order follows its presentation rather than
native bitmask order. This revises the initial decision to reorder only table
rows: `i, j, k = Algebra(config=presets.quaternion()).basis_blades(grade=2)`
now agrees with the table and the preset's conventional unit order. Both basis
factories use the same collection policy, including custom vector orders.
The numeric core's basis factories and multivector coefficient storage remain
in native order. To request native order publicly, select
`DisplayOrder(algebra.n, range(algebra.dim))` on the algebra.

## Consequences

Notebook users can inspect the result of either basis factory directly and
still unpack or index it as before. Plain `tuple` comparisons continue to work.
The collection's rich display is a snapshot; later presentation changes do
not reorder or relabel an existing table. STA, CGA, custom display order, and
Marimo output have regression coverage.
