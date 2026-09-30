---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-166: Composed Presenter Recipes

## Context

ADR-161 made independent presentation components composable with `|` for
`Algebra(config=...)`. `Presenter` could already accept `blades=`,
`notation=`, and the other components separately, but it had no way to accept
the resulting `PresentationRecipe`. A presenter must leave the numeric algebra
and all unspecified presentation components as they are when it is applied.

## Decision

Add `Presenter(config=recipe)` for a `PresentationRecipe`. Resolve that recipe
against the value's current or captured presentation and its actual Gram
matrix when the presenter is called. Reuse the same recipe application logic as
`Algebra(config=...)`, so blade presets and sparse notation patches have the
same meaning in both contexts.

The presenter's existing `presentation=` argument selects a complete base
snapshot before the recipe is applied. Its individual component arguments
override matching recipe slots; `content=` overrides the final display
policy's content. Keep the individual `blades=`, `notation=`, `display=`, and
other keyword forms available without a recipe. A direct `notation=` may be a
complete `Notation` or a sparse `NotationPatch`, applied after the recipe.
Reject a complete algebra
preset in `config=` because a presenter cannot change the value's metric.

## Consequences

One presentation recipe can be used to configure an algebra or to render a
value from an existing algebra. Applying a presenter continues to return an
immutable view without changing the multivector, its numeric algebra, or its
expression provenance. Metric-sensitive blade presets remain checked against
the value's actual Gram matrix at application time.

The same recipe can be passed to `Algebra.with_presentation(recipe)` or
`Algebra.use_presentation(recipe)`. These methods apply it to the current
presentation, using the algebra's Gram matrix. The narrower
`Algebra.with_notation(patch)` and `Algebra.use_notation(patch)` methods accept
`NotationPatch` as well as complete `Notation` values; the patch applies to
the current notation. Rendering entry points still require a complete
`PresentationConfig` for explicit per-render overrides.
