---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-162: Sparse Notation Overrides

## Context

ADR-161 joins complete `Notation` objects by their rule keys, but applying a
complete notation to an algebra preset replaces its whole notation slot.
Changing only the reverse symbol then requires copying the preset's rules and
handling target-specific overrides by hand. In particular, a generic dagger
rule is hidden by the conventional LaTeX-only tilde rule.

## Decision

Add an immutable `NotationPatch` and the
`presets.notation.override(reverse="dagger" | "tilde")` factory. A patch
changes only the reverse operation in the existing notation, retaining its
identifier, other tokens, and other rules. Dagger removes the inherited
LaTeX-only reverse rule so its generic dagger is used consistently; tilde
installs the conventional generic and LaTeX-specific reverse rules.

`Notation | NotationPatch` applies the patch immediately. A patch composed
onto a complete algebra preset is stored in a `PresentationRecipe` and
applied to the preset's notation when `build()` resolves the configuration.
Repeated patches use right-hand precedence. A complete notation on the right
still replaces a preceding patch or notation slot.

## Consequences

`Algebra(config=presets.sta() |
presets.notation.override(reverse="dagger"))` preserves the STA metric, blade
names, model, and all unrelated notation. The patch is deliberately small;
more keyword overrides can be added when a common teaching need is clear.
