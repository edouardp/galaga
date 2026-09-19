---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-149: Matrix Cell and Region Annotations

## Context

SPEC-015 specifies matrix-region annotations as a later milestone: selecting a
matrix entry, row, column, or block and colouring, bordering, or labelling it.
ADR-147 delivered the first `galaga_annotation` milestone and deliberately left
matrix regions out. Implementing them raised four questions the expression
annotator could not answer:

1. Where do matrix targets live, and how do they resolve when the expression
   resolver only understands `RenderDocument`?
2. How does the adapter read displayed cell content without re-implementing the
   companion package's complex and quaternion formatting?
3. How is cell/region lowering kept consistent with expression decoration,
   including the KaTeX trust boundary?
4. What does a label mean for a region that KaTeX cannot group as a single
   `array` span?

## Decision

Add `MatrixCell(row, column)` and `MatrixRegion(rows, columns)` as immutable
target dataclasses in `galaga_annotation.targets`, plus `cell`, `row`,
`column`, and `block` selector factories. Each region axis is an `int`, a
half-open positive-step `slice`, or a sequence of indices; the whole matrix is
`MatrixRegion()`. Matrix targets are accepted by `Annotation` through a new
`ANNOTATION_TARGET_TYPES` tuple, but they are **not** resolved by the
expression `resolve`. The expression resolver raises a typed error directing
callers to the matrix renderer, because a matrix representation is a companion
object rather than an expression render document. The matrix resolver does
accept `WholeExpression`, whose meaning (*the complete displayed value*) is
representation-agnostic, so the one-off `annotate(matrix, label=...)`
shorthand keeps working; every other expression target is rejected.

Resolution lives in the optional `galaga_annotation.matrix` adapter and is
performed by `resolve_matrix(matrix, rules)`. It validates coordinates against
the representation's shape before rendering. Out-of-range coordinates are
invalid requests and raise `ValueError`; a valid but empty selector (such as
`slice(2, 2)`) follows the rule's `missing` policy exactly like expression
annotations. `MatrixRegion` axis helpers expand and validate against a concrete
dimension through `resolve_axis`.

`galaga_matrix.MatrixRepr` gains two public hooks: `logical_shape` (the
displayed cell grid, half the underlying array in quaternion mode) and
`cell_latex(row, column)` (the LaTeX body of one display entry). `_body_latex`
is refactored to use them, so annotation lowering reads cell content through
the companion package's own formatter and never re-implements complex or
quaternion formatting. This follows SPEC-015's rule that the adapter consumes
existing provenance rather than introducing a competing representation.

Lowering reuses the package's target-independent decoration boundary. Each cell
is wrapped in a core `Decorated` node with the raw cell LaTeX as its opening
string, then passed through the package-private `_decoration` module's
`style_body`/`decorate` interface. Cell colours, fills,
borders, emphasis, labels, braces, group accents, underlines, boxes, arrows,
and rules therefore lower through exactly the same code path and trust
boundary as expression decorations. Whole-matrix selections are detected
(`len(cells) == rows * columns`) and lowered as a matrix-level marker around
the `pmatrix` environment. A partial-region label or marker anchors to the
region's first cell as a callout; the remaining cells receive content styling
only. Block-level region callouts and separate row/column header labels remain
a later refinement, following the SPEC-015 section 10 sketch.

`galaga_annotation.Annotator.__call__` dispatches a bound `MatrixRepr` to a new
rendering-only `AnnotatedMatrix` view. It mirrors `Annotated`: it exposes
`.plain`/`.value`, `.latex()`, `_repr_latex_`, a Marimo `_repr_html_` rich
block, delegates read-only matrix attributes, and defines no arithmetic. The
adapter imports `galaga_matrix` lazily, so `galaga_annotation` remains
importable and usable without the companion package; `is_matrix` returns
`False` when it is absent.

Trust is unchanged from ADR-147. Cell LaTeX comes from the companion package's
own trusted formatter, not from user input. Annotation labels use the existing
plain-label escaping, and `label_latex` remains the single named trusted KaTeX
escape hatch.

## Consequences

- Matrix annotations reuse one decoration implementation, so expression and
  matrix styling cannot drift apart or acquire separate escaping rules.
- Target-specific renderers do not import underscore helpers from one another;
  `_decoration` is private as a module but exposes a named internal interface.
- `galaga_matrix` exposes a small, documented cell-rendering surface instead
  of leaking private `_fmt`/`_body_latex` helpers to the adapter.
- The companion package stays optional; importing `galaga_annotation` never
  imports `galaga_matrix`.
- Region labels anchor to the first selected cell rather than a draggable
  block callout. Region-level block callouts, row/column header labels, and
  expression-to-matrix provenance remain later milestones.
- The annotation test environment installs `galaga_matrix` so the adapter
  contracts are exercised; a `matrix` extra declares the optional dependency.

## Validation

- `galaga_matrix` tests cover `logical_shape` and `cell_latex` for real and
  quaternion matrices, and confirm `_body_latex` is unchanged.
- `galaga_annotation` tests cover target validation, axis expansion, region
  resolution, whole-matrix detection, out-of-range errors, empty selections
  and the missing policy, cell/region colour, fill, border, label and marker
  lowering, named matrices, quaternion mode, view transparency and dispatch,
  arithmetic rejection, and the Marimo rich-display boundary.
- Repository linting keeps Ruff C901 scoped to the annotation implementation.

## Related

- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification.
- [ADR-082](082-matrix-provenance-is-package-owned.md): matrix provenance owned by
  `galaga_matrix`.
- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  annotation lowering and the `Decorated` extension point.
