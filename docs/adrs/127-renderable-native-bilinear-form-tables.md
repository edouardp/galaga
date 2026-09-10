---
status: accepted
date: 2026-09-10
deciders: edouard
---

# ADR-127: Renderable Native Bilinear Form Tables

[ADR-128](128-wedge-product-tables-and-grade-colours.md) extends this table
pipeline to exterior products and optional grade colours. The two public
table types now share a private rich-display base; the Gram contract is
unchanged.

## Context

The user requested `Algebra.bilinear_form_table()` as a notebook-ready view
of the Gram matrix, with basis labels on both axes, a bullet in the corner,
and zeros coloured `#bbbbbb`. `MatrixRepr` renders unlabelled matrices but
belongs to an optional companion; the numeric package must not depend on it
or on Marimo merely to display its defining metric.

## Decision

Add the method to the public facade `Algebra`, not the presentation-free
numeric core. It returns an immutable `galaga.display.BilinearFormTable`
snapshot. Capture the active presentation's vector labels, coefficient
precision and default output target when the method is called. No numeric
operation, expression provenance or algebra identity changes.

Keep rows and columns in native Gram order, independent of multivector
display order. A signed convention label names a signed vector: if `u`
denotes `-e1`, the native table heading is `-u`, not `u`. Entries remain the
stored `G[i,j]`; never relabel a signed basis while silently retaining the
wrong pairings. Compute native products before specifying signs in tests.

Use a format-neutral square `Table` node in the existing semantic rendering
pipeline. The builder reads the Gram entries directly and constructs axis
headings in linear time without creating full multivector coefficient arrays.
The emitter owns array syntax, separators and colour. This extends
[ADR-078](078-shared-semantic-rendering-pipeline.md); it does not introduce an
independent LaTeX formatter for coefficients or a matrix-representation mode.

LaTeX uses `array`, a vertical rule after the row-label column, and a
horizontal rule after the column headings. Each exact zero is emitted as
`{\color{#bbbbbb}0}`. The scope prevents colour leaking into other cells;
there is no global `\newcommand` or dependence on notebook macro state.
Signed zeros display identically. Small nonzero metric coefficients must
remain visible regardless of the multivector display's zero tolerance;
significant-digit precision still applies. ASCII and Unicode use aligned
plain-text tables with the same labels and values.

The object supports `.latex()`, `.ascii()`, `.unicode()`, `.display()`,
formatting, and the `_repr_latex_()` rich-display protocol. Raw `.latex()`
has no math delimiters; `_repr_latex_()` supplies one display-math wrapper.
`galaga_marimo`'s existing block marker makes `gm.md(t"{table}")` work
without a companion change, and `{table:block}` is also supported. The
shared `render`/`build_tree` functions accept its value/full content; there
is no invented name or expression. Rendering overrides cannot change a
snapshot's presentation: create a new table from the configured algebra.

Empty algebras produce a corner-only table. The display remains a view of
an `n` by `n` bilinear form, not a full geometric-product multiplication
table, Gram factorization, or implicit basis change. Raw numeric access
remains `algebra.gram`.

## Verification and consequences

Tests compare every table entry to scalar products of the native basis in
Euclidean, indefinite, degenerate, oblique, STA, RGA and native-null CGA
algebras. They cover signed labels, presentation snapshots, display-order
independence, custom precision, signed zeros and subnormal nonzeros, empty
tables, immutable storage, invalid layouts, all output hooks and actual
Marimo standalone/template rendering. The CGA Gram notebook demonstrates
the method alongside its existing matrix display, with runtime regressions.

No new dependencies, release metadata changes, or legacy imports are added.
