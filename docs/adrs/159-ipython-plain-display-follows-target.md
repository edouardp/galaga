---
status: accepted
date: 2026-09-29
deciders: edouard
---

# ADR-159: IPython Plain Display Follows the Presentation Target

## Context

`DisplayPolicy.target` selects ASCII, Unicode, or LaTeX for Galaga rendering.
Terminal IPython obtains its `text/plain` output from Python `repr` unless an
object supplies a pretty-print hook. Galaga's portable `repr` is ASCII, so
`wedge_product_table()` and `bilinear_form_table()` appeared with ASCII basis
names even when the captured table target was Unicode. Multivectors and the
new basis and local collections had the same plain-output mismatch.

## Decision

Provide `_repr_pretty_` for multivectors, algebra tables, basis collections,
and local collections. It renders terminal IPython `text/plain` using each
object's active or captured `DisplayPolicy.target`. Basis and local collections
show indexed or named plain-text tables in their captured blade display order.

Keep Python `repr` ASCII for portable diagnostics. Keep `_repr_latex_` as a
separate rich representation for notebook frontends; explicit `.ascii()`,
`.unicode()`, and `.latex()` selectors continue to work independently.

## Consequences

Terminal IPython shows Unicode wedge symbols and blade subscripts when a
Unicode display policy is selected. The shared algebra-table hook applies to
both wedge and bilinear form tables. IPython formatter tests cover both table
types, multivectors, basis collections, and local collections in ASCII and
Unicode; Marimo rich-rendering tests retain their LaTeX output.
