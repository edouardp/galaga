---
status: accepted
date: 2026-09-10
deciders: edouard
---

# ADR-128: Wedge Product Tables and Grade Colours

## Context

After the labelled Gram table in
[ADR-127](127-renderable-native-bilinear-form-tables.md), the user requested
the same rich display for exterior products: vector-only axes by default,
every exterior basis blade including scalar `1` with `full=True`, and
optional result-grade colouring using either English spelling.

## Decision

Add the public facade method
`Algebra.wedge_product_table(full=False, *, color=False, colour=False)`.
All flags must be Python booleans. Either colour flag being true enables
colouring; supplying both is allowed and a false spelling does not veto a
true one. Zero remains `#bbbbbb` regardless of these flags.

The result is an immutable `galaga.display.WedgeProductTable` snapshot.
Factor the existing rich-display hooks into a private shared table base;
the Gram and wedge wrappers remain distinct public types. Both retain the
same raw/rich LaTeX, aligned text, formatting and Marimo block contracts.

Each cell is **row blade wedged with column blade**. Vector-only axes use
native vector order. Full axes originally used grade-then-bitmask order;
[ADR-133](133-grade-lexicographic-default-display-order.md) supersedes this
with the active multivector `DisplayOrder` on both axes, including explicit
preset and user overrides. Scalar `1` appears at its selected position, first
by default. Signed convention labels describe the actual native
blades, including signs in axis headings and results. The scalar identity
is literal `1`, not a convention alias. These are exterior basis blades,
not ordered geometric products in a nonorthogonal basis.

The facade reads the exact wedge coefficients from the numeric core's
cached dimension metadata, which is also used by `outer_product`. It
passes selected masks and coefficients into the semantic builder. The
builder only lays out this already-computed data: no numeric evaluation,
parallel sign algorithm, metric-dependent inference, or dense multivector
allocation per cell. Tests independently compare every rendered entry to
the public algebra's computed outer products. Presentation zero tolerance
cannot hide a nonzero exterior coefficient.

Introduce a semantic `GradeColor` decoration carrying a body and a
non-negative integer grade. Apply it only to nonzero result cells, using
the resulting mask's grade, never to the headers or zero cells. The LaTeX
emitter owns scoped colour syntax; ASCII and Unicode ignore the decoration
and carry no terminal control sequences. The decoration preserves its
body's precedence and includes any minus sign inside the colour scope.

Grades use a stable eight-colour cycle: `#111827`, `#0072B2`, `#D55E00`,
`#009E73`, `#CC79A7`, `#E69F00`, `#56B4E9`, `#F0E442`. Grade zero starts
with the neutral colour; higher grades index the cycle modulo eight.
These hues match the plotting companion's palette, but the core renderer
has no dependency on that optional companion. Colour is an aid, not a
unique grade identifier for arbitrarily high grades.

## Consequences and verification

A vector table has `n*n` result cells; a full table has `4**n`. Document
that cost and demonstrate a readable full three-dimensional table next
to the vector-only native-null CGA table. Teach the scalar identity,
repeated-factor zeros and graded commutation, including a computed
vector/bivector example. Full 3D CGA is explicitly available as 32 by 32.

Regression tests cover full and vector tables, scalar-only algebras,
Euclidean/oblique/degenerate/STA/RGA/CGA products, signed names, metric
independence, scoped snapshots, both colour flags, strict flag validation,
grade colours, zero precedence, all display hooks and actual Marimo
standalone/template rendering. Existing Gram-table tests must still pass.

No release metadata, optional dependencies or numeric semantics change.
