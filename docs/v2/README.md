# Galaga 2 Planning

## Start here

- [Core cutover plan](core-cutover-plan.md) is the normative execution plan
  for replacing the legacy `Algebra` and `Multivector`, completing the facade,
  and performing the Galaga 2.0 cutover. It defines numbered work units, tests,
  and phase exit gates.
- [Numeric test migration inventory](numeric-test-migration-inventory.md)
  identifies, by existing file and test class, which Galaga tests move to
  `galaga.core`, which become facade contracts, and which remain in outer
  layers.
- [Presentation and expression layer plan](presentation-symbolic-layer-plan.md)
  explains the composition-facade, operation-catalog, configuration,
  expression-provenance, and rendering architecture.
- [Numeric-algebra replacement roadmap](galaga-replacement-roadmap.md) records
  remaining numeric capabilities and companion-package work.

## Current status

Phase 0 of the core cutover plan is complete on `galaga_v2`: the proven
Gram-matrix implementation and its tests live in `galaga.core`, the opt-in
facade delegates to it, and the built Galaga package no longer depends on a
standalone `gram` distribution.

Phase 1 is next. Top-level `galaga.Algebra` and `galaga.Multivector` still use
the legacy engine until the replacement contract and facade-specific numeric
suite pass their gates.

## Supporting documents

- [Numeric core documentation](../core/README.md)
- [ADR-073: Move the numeric core into Galaga](../adrs/073-move-the-numeric-core-into-galaga.md)
- [Historical v2 issue inventory](../../V2-PLANNING.md)

The historical issue inventory predates the Gram-matrix core. It remains useful
for design context, but the core cutover plan and accepted ADRs take precedence
for implementation sequencing.
