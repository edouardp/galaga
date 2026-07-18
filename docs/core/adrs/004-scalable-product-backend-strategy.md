---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-004: Select Scalable Product Backends Behind One Contract

## Context and problem statement

An orthogonal basis-blade pair has one product output, but a general-Gram pair
can expand across several grades. A dense rank-three product tensor grows as
`dim**3`; eagerly using it as the only representation is unsafe. Conversely,
forcing every diagonal product through a general sparse expansion would discard
a valuable fast path.

## Decision drivers

- Preserve diagonal performance and storage.
- Compute directly in the native basis without diagonalization.
- Avoid a large eager general-product allocation.
- Use one semantic contract for products and grade-selected products.
- Retain an independent correctness oracle.

## Considered options

1. Use a dense product tensor for all metrics.
2. Compute every general product from scratch.
3. Use a diagonal fast path and one fully packed general table.
4. Select among diagonal, packed, bounded lazy, and reference strategies.

## Decision outcome

Define a backend contract for multiplication, grade-selected multiplication,
and basis-blade left action.

The public linear combination of those basis actions supports regular matrix
representations and the general inverse. It also supplies the norm bound used
to scale a general multivector exponential; no exponential-specific product
table is introduced.

- Exactly diagonal metrics use monomial output/factor tables.
- Moderate general metrics use complete CSR-like sparse pair expansions.
- General metrics whose conservative packed estimate exceeds 64 MiB use
  on-demand sparse left actions with a thread-safe 64 MiB LRU cache.
- A dense Chevalley-action backend remains available as a small-dimension
  correctness oracle.

Packed and lazy backends share one grade-ordered Chevalley recurrence. Only
their construction time and retention policy differ.

Explicit backend selection and diagnostics are available for tests and
inspection. `auto` is the normal user choice.

## Consequences

- Good, because product semantics do not expose storage strategy.
- Good, because large predicted tables switch before eager allocation.
- Good, because the lazy cache reuses a left blade across every right operand.
- Good, because reference and production paths can be cross-checked.
- Cost, because dense multivectors on a lazy backend may request many actions
  and create cache pressure.
- Cost, because the conservative worst-case estimate may choose lazy for a
  structurally sparse high-dimensional metric.
