---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-161: Right-Biased Presentation Composition

## Context

Complete algebra presets produce an `AlgebraConfig` with a numeric definition,
presentation, and optional model. Blade, notation, local-name, display-order,
and display-policy values are independent presentation components. Combining
components required spelling out a complete configuration or constructor
overrides, while named notations could not be combined at all.

## Decision

Use `|` for immutable dictionary-style composition. Two `Notation` values
merge legacy tokens by operation ID and rendering rules by
`(operation_id, target)`, with a right-hand value replacing the same key.
The right-hand notation ID labels the merged value. Absent right-hand keys
leave left-hand keys in place, including target-specific rules and the
empty-rule functional notation.

Different presentation component types promote to `PresentationRecipe`, which
holds optional blades, notation, local names, display order, and display policy.
Combining recipes replaces a repeated slot with the right-hand slot. Applying
a recipe to a complete preset or `AlgebraConfig` returns `ConfiguredPreset`,
whose `build()` resolves blade recipes against the numeric Gram matrix and
returns a validated `AlgebraConfig`. The numeric definition and model remain
those of the base preset. Combining two complete algebra presets is undefined.

[ADR-169](169-sparse-display-overrides.md) refines repeated display-policy
composition: supplied display fields merge with right-hand precedence instead
of replacing the whole display slot.

## Consequences

Users can write `Algebra(config=presets.sta() | (presets.blades.sta() |
presets.notation.hestenes()))`. Parentheses distinguish merging notation
rules first from replacing a whole notation slot in a presentation recipe.
Target-specific notation rules retain their existing precedence over generic
rules unless that exact target-specific key is replaced on the right.
