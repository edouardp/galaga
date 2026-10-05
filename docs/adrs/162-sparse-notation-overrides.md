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
names, model, and all unrelated notation. The initial factory covered only
the reverse style.

## Amendment: operation and target rules

TOML presentation preferences can replace a rule for one operation and
output target without replacing the rest of the notation. Give the Python
factory the same expressive range. Keep `reverse=` as the common shorthand,
and accept `rules=` with the key forms used by `Notation`: an operation ID
for a generic rule, or `(operation_id, target)` for a target-specific rule.
Add `ascii=`, `unicode=`, and `latex=` mappings as concise target-grouped
spellings. Complete values use an explicit `RenderRule`, so the rule kind remains
clear. Repeated keys across arguments are errors. An explicit reverse rule
applies after the `reverse=` shorthand.

```python
presets.notation.override(
    reverse="dagger",
    latex={"right_hodge_dual": RenderRule("superscript", symbol=r"\star")},
)
```

The factory returns the existing `NotationPatch`; the composition and
inheritance rules above are unchanged.

## Amendment: concise render rules

Accept compact `kind:symbol` strings for common layouts and
`wrapper:opening,closing` for fixed delimiters. Operation keyword arguments,
such as `left_hodge_dual="prefix:star"`, are concise rules for all three
targets. Strings in `rules=` without a target have the same all-target
meaning; strings in `ascii=`, `unicode=`, or `latex=` affect only that target.
The parser uses `Name.from_latex` for recognized symbol names, so `star`
resolves to `*`, `⋆`, and `\star`. The `1/2` wrapper prefix resolves to
`1/2`, `½`, and `\tfrac{1}{2}`. Full `RenderRule` values remain available
for every layout option and retain their existing generic-rule behavior.

## Amendment: discoverable operation keywords

Declare the public expression-catalog operation names explicitly in the
`presets.notation.override` signature so editors can complete them. Keep the
implementation's shared rule normalization and the `rules=`, target-map, and
keyword forms. A contract test compares the manual signature with the catalog
to expose omissions as operations are added. The special `reverse=` style
argument retains its existing `"tilde"` and `"dagger"` choices; arbitrary
reverse rules remain available through `rules=`.
