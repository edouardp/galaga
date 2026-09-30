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

`DisplayOrder` controls presentation, while factory enumeration remains in
native bitmask order under [ADR-059](059-display-ordering.md). In STA, the
grade-two sequence has masks `3, 5, 6, 9, 10, 12`, whereas the default display
order places mask `9` before mask `6`. CGA has a larger difference across its
ten bivectors. Reordering the sequence would change indexing and unpacking.

## Decision

`basis_vectors()` and `basis_blades(k)` return `BasisMultivectors`, a tuple
subclass containing exactly the same multivectors in the same native order.
Tuple indexing, slicing, unpacking, iteration, and equality remain available.

The collection captures the active presentation and renders a two-column
LaTeX table of sequence index and basis blade. Table rows follow the captured
`DisplayOrder`, as for `locals()`. Each row keeps its native sequence index so
the display still identifies the value obtained with `[index]`. Blade values
render through their multivectors, retaining preset signs and labels. The
factory's grade selection limits the table to the requested blades.

## Consequences

Notebook users can inspect the result of either basis factory directly and
still unpack or index it as before. Plain `tuple` comparisons continue to work.
The collection's rich display is a snapshot; later presentation changes do
not reorder or relabel an existing table. STA, CGA, custom display order, and
Marimo output have regression coverage.
