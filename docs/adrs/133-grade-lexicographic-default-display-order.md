---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-133: Grade-Then-Lexicographic Default Display Order

## Context

Native bitmask order interleaves grades, placing `e12` before `e3`. This exposes
coefficient storage details rather than the mathematical structure readers
expect. Sorting by grade and then mask is insufficient: in four dimensions it
still places `e23` before `e14`.

The user requested grade-then-lexicographic display by default, while retaining
all existing explicit overrides, including RGA's convention. This supersedes
the default-order decisions recorded in ADR-059 and ADR-097, not their separation
of presentation from numeric storage and basis enumeration.

## Decision

`DisplayOrder(n)` and `DisplayOrder(n, None)` enumerate blades by increasing
grade, then lexicographically by the ascending tuple of numeric basis indices.
Generate the tuples with combinations of the ordered basis positions. This is
independent of the metric, rendered names, aliases, and signed blade labels.
Numeric index 2 precedes 10; there is no lexical sorting of rendered strings.

The four-dimensional bivector order is `e12, e13, e14, e23, e24, e34`.
The zero-dimensional algebra retains its sole scalar mask `0`.

All explicit mask permutations retain their exact order. Existing quaternion,
Lengyel RGA and Lengyel CGA preset overrides are unchanged. Constructor
overrides, presentation views and scoped presentation overrides keep their
existing precedence. Plain algebras and presets without an override inherit
the new default through the existing presentation constructors.

Native-mask display remains available as
`DisplayOrder(algebra.n, range(algebra.dim))`. No new flag or sorting API is
needed. Changing presentation does not rewrite already-created string output.

### Full wedge tables

`wedge_product_table(full=True)` uses the active `DisplayOrder` for both rows
and columns, superseding ADR-128's independent grade-then-mask axis order.
This makes full tables agree with multivector display, including RGA, Lengyel
CGA, quaternion and user overrides. Reorder the coefficients along both axes,
not only the headings. Preserve the native blades and their signed labels;
this is not a change of basis or a change of exterior-product signs.

The scalar heading remains literal `1`, at the position selected by the display
order. It is first by default but is not forcibly moved ahead of an explicit
override. Axis order is captured in the immutable table snapshot along with
labels and colouring. Previously created tables do not change with subsequent
presentation scopes. Vector-only wedge tables keep native vector order.

## Boundaries

- Coefficient arrays, numeric kernels, matrix coordinates, and basis factory
  enumeration stay in native bitmask order.
- Bilinear table axes and vector-only wedge table axes stay in native vector
  order, independently of multivector display order.
- Expression trees are not reordered or algebraically simplified. Concrete
  multivector terms use the selected display order in all rendering targets.
- Custom labels and their orientation signs are unchanged.
- No release changelog update is made outside a release.

## Validation

Tests verify complete permutations from dimension zero through dimension ten,
including the `e14`/`e23` and numeric-index-2/index-10 distinctions. Rendered
terms are checked against blades computed by exterior products. Tests cover
ASCII, Unicode and LaTeX, unchanged data/products/equality/hashes, native basis
enumeration, preset inheritance, exact existing preset overrides, and explicit
user overrides. Historical rendering archives remain unchanged and continue
to be tested with explicitly selected historical orders where required.

Full-table tests compare every entry against computed exterior products,
including signed preset conventions, reordered axes and general metrics.
Further checks cover arbitrary scalar position, grade colours after
permutation, immutable scoped snapshots, and unchanged vector/Gram tables.
