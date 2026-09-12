---
status: accepted
date: 2026-09-10
deciders: edouard
---

# ADR-129: Concise Complete and Resolvable Blade Presets

## Context

The existing public preset factories use a redundant `p_` prefix:
`p_cga()`, `p_sta()`, and `p_euclidean()`. The same API also needs a clear
way to select blade vocabulary independently from the metric, for example:

```python
Algebra(1, 3, blades=presets.blades.sta())
```

Some vocabularies, especially STA sigma and pseudovector names, contain signs
derived from the ordered metric. Resolving those names before the target
algebra exists would make the convention silently wrong for another metric.

## Decision

Expose `galaga.presets` as a package whose advertised namespace contains only
the concise complete preset factories—`euclidean`, `sta`, `pga`, `cga`, `rga`,
`lengyel_cga`, `complex`, `quaternion`, and `exterior`—plus `blades`. The
implementation submodule retains compatibility attributes such as `p_cga` and
`CGAPreset` for explicit legacy imports, but they are resolved lazily and
omitted from `dir(galaga.presets)` and the preferred discovery surface.
Complete presets still build
the entire immutable `AlgebraConfig`: Gram definition, presentation, model,
notation, local-name policy, and display order.

Expose `presets.blades` as a namespace of immutable `BladePreset` recipes.
Recipes are resolved by the facade constructor or `with_blades()` only after
the numeric algebra and its Gram matrix exist. `PresentationConfig` continues
to contain concrete `BladeConvention` objects, never unresolved recipes.

Expose `presets.notation` as a parallel namespace of named immutable notation
recipes. These delegate to the canonical `Notation` constructors and can be
passed directly to `Algebra(..., notation=presets.notation.functional())`.

Blade-only recipes affect the blade convention only. They do not alter the
metric, model metadata, notation, display order, or local-name policy unless
the caller explicitly supplies those components separately. Existing concrete
`BladeConvention` inputs remain supported.

The `sta` blade recipe validates its dimension and, when sigma or pseudovector
names are requested, derives the ordered signature from the target Gram matrix.
It permits only diagonal unit entries and rejects off-diagonal, scaled, and
otherwise unsupported metrics. This reuses the existing product-derived sign
logic in `spacetime_blade_convention`; no sign table or metric inference from
inertia is added. Plain gamma-only STA naming does not require metric-derived
signs, but still requires four dimensions.

Other blade recipes delegate to the existing convention builders and validate
their expected dimensions. The recipes are immutable and reusable across
different algebras; no resolved convention or metric is cached in the recipe.
The CGA recipe additionally validates that its `null` or `orthogonal` frame
actually describes the target Gram matrix, preventing names such as an
orthogonal conformal pair from being applied to a native-null metric.

[ADR-134](134-origin-first-native-null-cga.md) additionally makes null CGA
origin-first by default and adds the explicit Euclidean-first compatibility
order to both complete and blade-only CGA recipes. Blade-only resolution
validates the selected coordinate positions; it does not permute the metric.

## Consequences and verification

Users can write `Algebra(config=presets.cga(3))` and retain a compact,
discoverable namespace, while `Algebra(1, 3, blades=presets.blades.sta())`
makes the metric/vocabulary boundary explicit. `from galaga import presets`
exposes the small advertised namespace while preserving normal module imports.
The old spellings remain available through lazy compatibility imports until a
separate deprecation and removal decision.

Tests compare every concise complete preset with its `p_*` counterpart,
exercise complete configuration identity, resolve plain and metric-aware STA
recipes against both ordered Lorentzian signatures, verify signed products
against the algebra, test reusable recipes and `with_blades()`, and reject
unsupported metrics, dimensions, flags, and recipe types. Documentation uses
the concise spelling while preserving compatibility guidance.

No CHANGELOG, release version, CI, or numeric-core changes are part of this
decision.
