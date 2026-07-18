---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-074: Long Operation Names Are Canonical in Galaga 2

## Context and problem statement

Galaga v1 made short names such as `gp`, `op`, and `involute` the implementation
names, then assigned longer aliases to them. Galaga 2 uses stable operation
identifiers to connect the facade, expression provenance, notation, and
rendering. Abbreviations and historical terminology are a poor foundation for
those identifiers because they obscure meaning and make later convention
changes look like simple renames.

A broad text replacement is also unsafe. Some old names denote exact aliases,
while others encode a convention. For example, Chisholm's bracket includes a
factor of one half and therefore maps to `half_commutator`, not to Galaga 2's
unscaled `lie_bracket`.

## Decision drivers

- Canonical operation identifiers should be readable without library-specific
  abbreviation knowledge.
- One mathematical operation must have one implementation and one catalog
  entry.
- Users may still prefer concise functional notation.
- Expression identifiers must not depend on a temporary compatibility alias.
- Numeric-test migration must separate mechanical renaming from mathematical
  convention changes.

## Decision outcome

Long, explicit names are the canonical Galaga 2 function and operation
identifiers. In the first naming work unit:

| Compatibility name | Canonical identifier |
|---|---|
| `gp` | `geometric_product` |
| `op` | `outer_product` |
| `involute` | `grade_involution` |

The established explicit names for contractions and competing inner products
remain canonical. We do not introduce an unqualified `inner_product` or `ip`
operation.

Compatibility aliases are the same function object as their canonical
operation. They do not receive another catalog entry, expression node, or
notation identity. `galaga.core.OPERATION_ALIASES` is the executable manifest
of retained aliases, and tests verify every entry with object identity.

Other existing aliases such as `join`, `meet`, `dorst_inner`, and `sw` remain
classified aliases. This ADR does not rename already explicit operations such
as `reverse` or `conjugate`; any such change requires another reviewed naming
decision.

Source-derived test migration uses two stages:

1. port a test to the core while binding canonical imports to its old local
   names, minimizing the semantic diff; then
2. canonicalize only the migrated destination with a syntax-aware change and
   run the original and migrated tests together.

Convention-sensitive names, scalar extraction, and facade-only helpers are
reviewed manually and are not eligible for the lexical codemod.

## Consequences

- Good, because the operation catalog and future expressions use readable,
  durable identifiers.
- Good, because short functional notation remains available without a second
  implementation.
- Good, because the executable alias manifest prevents documentation and code
  from drifting.
- Good, because test migration keeps the legacy file as an unchanged oracle
  while its core destination is adapted.
- Cost, because Galaga 2 code and tests need a staged naming migration.
- Cost, because old ADRs and documentation that called short names canonical
  must be treated as historical v1 decisions.

## Superseded decisions

This decision partially supersedes ADR-002 and ADR-009. Their decisions to use
named operations and same-object aliases remain valid. Their choice of short
names as the canonical API is superseded for Galaga 2.
