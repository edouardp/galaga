---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-079: Curated Compatibility without Redundant Generic Helpers

## Context and problem statement

The Galaga 2 facade now has canonical long operation names, optional concise
notation, and a complete numeric operation catalog. Galaga 1 also exports short
spellings, ambiguous inner-product names, generic geometry conveniences, and
the transitional `galaga.gram_bridge` namespace. Copying that whole surface
would preserve ambiguity and make migration-only vocabulary look permanent.

Compatibility still needs to be deliberate. Existing users need actionable
replacements, expression provenance must retain canonical operation identity,
and warnings must point at user code. At the same time, functions that merely
spell a primitive composition should not become new architectural layers.

## Decision drivers

- Keep one implementation and one operation ID for each mathematical operation.
- Preserve concise functional notation where it is established and unambiguous.
- Make temporary compatibility observable and mechanically removable.
- Do not choose an inner-product convention through an unqualified name.
- Do not add a generic helper without numeric capability, domain meaning, or
  validation.
- Keep documentation and implementation policy synchronized by tests.

## Decision outcome

Eight established concise names (`dorst_inner`, `gp`, `join`, `meet`, `op`,
`rev`, `sw`, and `wedge`) remain permanent exact-object aliases. They have no
separate catalog entries or evaluators.

Six Galaga 1 spellings (`involute`, `mag2`, `magnitude_squared`, `normalise`,
`normalize`, and `norm_squared`) are explicit warning adapters. An immutable
manifest maps each spelling to its canonical operation. The adapters issue
`GalagaDeprecationWarning` at the user's callsite and then invoke the canonical
facade function, so tracked expressions record the canonical operation ID.

`inner_product` and `ip` are absent from the facade. Attribute access explains
the available explicit inner-product and contraction families. Users retain
full control over local concise notation through ordinary import aliases.

The three `galaga.gram_bridge` import paths remain temporarily importable but
warn with their stable facade replacement.

The legacy `project`, `reject`, and `reflect` exports are classified for
removal, not copied into a generic helper namespace. Their arithmetic is
already expressible with facade primitives, while their useful meaning depends
on a subspace or geometry model. A future model-specific API may add such
operations when it also provides relevant metadata and validation. The same
rule excludes a redundant rotor constructor when `exp` is the complete
primitive.

The executable v1 surface ledger owns every disposition and warning. Tests
cross-check exact aliases, warning behavior and stack level, canonical tracked
operation IDs, ambiguous-name guidance, bridge imports, removal classification,
and the human migration guide.

## Consequences

- Good, because concise notation does not create duplicate implementations.
- Good, because temporary names are easy to find, test, and remove in Phase 9.
- Good, because inner-product convention remains an explicit user decision.
- Good, because provenance, notation, and numeric dispatch share canonical IDs.
- Good, because model-specific helpers can later provide more meaning than a
  generic one-line wrapper.
- Cost, because some Galaga 1 code must make its compositions or imports
  explicit during migration.
- Cost, because import-time compatibility warnings require careful test
  isolation and stack-level assertions.
