---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-152: Subexpression Annotation Targets

## Context

Expression paths (`ga.operand(2)`, `ga.path(1, 0)`) address a subtree by its
position in the recorded tree. That is precise but brittle: adding or removing
an operand silently retargets the annotation. A lesson that wants to explain
"the reverse factor" should be able to name that subtree instead of counting
operands.

The provenance model already makes this tractable. `expression_document`
anchors every surviving source path, and the facade value keeps its
`galaga.expression.Expr` tree, whose frozen nodes compare structurally. For
`R * v * ~R`, the `~R` factor is the anchor at `(1,)` and its recorded tree is
`Call("reverse", (Symbol("R"),))`.

## Decision

Add `SubexpressionTarget(expression, occurrence)` and the
`ga.subexpression(value, occurrence="all")` factory. `value` may be a
`galaga.expression.Expr` or a tracked value whose `expr` is one.

Resolution compares the target tree against the recorded source subtree at
every surviving expression anchor path and returns the matching layout paths.
Matching is **structural, never numeric**: `e1 + e1` and `2 * e1` are equal
after eager evaluation but are different provenance trees, and only the former
matches. Subtrees removed by the renderer's simplification have no anchor and
therefore match nothing, following the ordinary `missing` policy.

The default `occurrence="all"` annotates every copy; `occurrence=n` selects one
in the document's anchor order, the same order `ga.variable(...)` uses. This
lets a repeated subtree such as `~R` in `(~R)(~R)` be addressed precisely.

Subexpression targets require a tracked value (`expr=True`). A value without
provenance is an invalid request, not an empty match, because there is no tree
to compare against; resolution raises `ValueError` rather than guessing from
numbers.

To make this work, `resolve` now passes the whole annotated `value` to target
selectors instead of only its algebra. The blade-bound selectors read
`value.algebra` themselves; the provenance selector reads `value.expr`. This
removes a lossy projection at the resolver boundary without changing the public
`resolve` signature.

A named value is referenced by its `Symbol` inside a parent expression, so
`ga.subexpression(R)` compares `R`'s *definition* tree and will not match the
`R` symbol occurrences. `ga.variable("R", occurrence=...)` remains the selector
for those. `subexpression` is for composite subtrees such as `~R`, `R*~R`, or
`(e1 + e2)`.

## Consequences

- Annotations can name a subtree and survive unrelated edits to the enclosing
  expression.
- Matching consumes provenance only; it never infers equality between
  numerically equal but structurally different expressions.
- Untracked values raise a clear error for subexpression rules instead of
  silently matching nothing, which keeps the failure mode explicit.
- The resolver boundary now carries the full value, so future provenance-aware
  selectors have what they need.

## Validation

- `galaga_annotation` tests cover factory validation and hashing, subtree
  resolution, occurrence selection among duplicates, structural-versus-numeric
  distinction, operation-tree distinction, the untracked-value error, lowering
  of the matched subtree, and accepting a bare provenance node.
- `examples/annotation/subexpressions.py` is executed by the annotation
  notebook test and the maintained example gallery.

## Related

- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification.
- [ADR-144](144-expression-render-occurrence-anchors.md): expression render
  occurrence anchors.
- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  lowering.
