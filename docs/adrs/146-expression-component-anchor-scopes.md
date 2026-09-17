---
status: accepted
date: 2026-09-17
deciders: edouard
---

# ADR-146: Expression Component Anchor Scopes

## Context

Annotation rules must select grades, terms, coefficients and signs inside an
expression operand independently of the computed result. Presentation may
flatten a multivector literal into an enclosing sum or reuse its layout in a
definition. Neither changes the literal's original semantic scope.

## Decision

Record scalar, blade and multivector literal components alongside their layout
in the ordinary expression builder. Resolve them into immutable `RenderAnchor`
records using the existing source map and final layout, with `scope="expr"`
and `expression_path` identifying the original occurrence. Concrete result
anchors keep `scope="value"`.

`document.select(kind, scope="expr", path=...)` selects components at or below
the original occurrence path. Omitting the path selects all expression
components; `()` selects the entire expression subtree. Existing selection
defaults to result scope. A path is valid only with expression scope.

Flattened literal terms use their final sum indices; signs reflect the actual
displayed sign at that slot. Coefficient and blade anchors refer to actual
layout nodes, with distinct render paths for repeated definition displays.
Native masks, label orientations, omission of unit coefficients, tolerance,
and ordering continue to derive from the shared coefficient builder.

Use the deepest surviving source owner to assign a simplified literal's
components. A scalar produced by folding belongs to the folded expression's
scope, not to its removed operand scopes. Zero placeholders and omitted
components have no anchors. Scalar literals retain their existing rendering
policy: nonzero scalars are not hidden by multivector zero tolerance.

Named symbols are opaque references, not expanded values. This implementation
does not infer their internal components or run algebra operations while
rendering. Teaching documents combine these scoped anchors and rebase their
render paths without changing the original occurrence paths.

## Consequences

- Grade rules can select an entire operand subtree with one source path.
- Equal blade masks in two operands and the result remain distinguishable.
- Empty, removed and hidden matches continue to require no caller handling.
- Annotation recipes and rendering styles remain outside the core trees.
- Fine-grained component inference for arbitrary symbolic nodes is deferred.

## Validation

Tests cover flattened literal sums, nested operand prefix selection, computed
RGA label signs, negative singleton sign absorption, subtraction, repeated
definition displays, shared source literals, zero/tolerance/implicit omissions,
scalar folding scopes, existing scalar visibility, teaching equality rebasing,
and invalid scoped selectors.
