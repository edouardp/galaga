---
status: accepted
date: 2026-10-05
deciders: edouard
---

# ADR-173: Renderable Operation Notation Overview

## Context

Sparse notation patches are easy to compose but hard to inspect in a notebook.
The configuration objects expose rules, yet they do not show how an operation
will look with the algebra's blade names. This is especially noticeable for
custom left and right Hodge dual symbols.

## Decision

Add `Algebra.show_presentation(all=False)`, returning an immutable
`PresentationTable`. Each row names one expression-producing catalog operation
and gives two rendered calls using the algebra's basis vectors. Unary examples
show a vector and a wedge of two vectors; contractions vary the operand
grades; scalar-only operations use scalar examples. These are symbolic notation
examples; do not evaluate metric-dependent operations to produce the table.
The first sandwich example uses the conventional rotor symbol $R$; the second
uses a compound rotor so its grouping is visible.
Lower-dimensional algebras use symbolic placeholders when the needed basis
vectors do not exist. Predicate operations return plain booleans and do not
retain expression provenance, so they are omitted even from `all=True`.
`rotor_generator` remains included because it returns a tracked multivector;
its sample input is the exponential of a basis bivector.

`basis=True` is the default example vocabulary. `basis=False` replaces the
basis blades with symbolic `A`, `B`, and `C` while retaining the same
operation-specific sample shapes. This allows a notation comparison that is
independent of the algebra's naming convention.
For `transwedge` and `transwedge_antiproduct`, use order one in the first
example and order two in the second to expose their parameterized notation.
For `power`, use exponents two and three in the respective examples.

The default view includes operations whose effective notation or token differs
from `Notation.default()`. This is a best-effort standard baseline, so built-in
preset conventions may also appear. `all=True` includes every operation whose
result can retain an expression. Capture the active presentation and display target when
the table is created. Its LaTeX representation uses three columns for the
operation and two examples, with a vertical separator after the operation name.
Plain-text targets
remain available for terminals and explicit calls.
When the compact view has no rows, explain that `all=False` selected only
overrides and point to `alg.show_presentation(all=True)` in every display
target.

## Consequences

Learners can inspect the notation that a value will use without evaluating an
operation that might be undefined for the example basis vectors. The complete
view can be long, but it is explicitly requested with `all=True`. The compact
view gives immediate feedback on custom notation and inherited preset choices.
