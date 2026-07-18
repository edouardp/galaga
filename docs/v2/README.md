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
- [Public API migration matrix](public-api-migration-matrix.md) is the
  human-readable Phase 1 contract for every v1 export, type member, expression
  constructor, protocol, supported module, and known private dependency.
- [Presentation and expression layer plan](presentation-symbolic-layer-plan.md)
  explains the composition-facade, operation-catalog, configuration,
  expression-provenance, and rendering architecture.
- [Numeric-algebra replacement roadmap](galaga-replacement-roadmap.md) records
  remaining numeric capabilities and companion-package work.

## Current status

Phases 0 through 3 of the core cutover plan are complete on `galaga_v2`. The
proven Gram-matrix implementation lives in `galaga.core`; the exhaustive v1
replacement contract is checked in and executable; `galaga.facade` owns the
complete eager numeric facade; and the applicable legacy numeric contract has
been migrated to or rerun against that facade. `galaga.gram_bridge` is now
only a compatibility re-export of the same facade objects.

Phase 4 is next: presentation configuration, blade conventions, and presets.
Top-level `galaga.Algebra` and `galaga.Multivector` deliberately remain on the
legacy engine until the presentation, expression, rendering, and integration
phases make the final shadow cutover safe.

## Supporting documents

- [Numeric core documentation](../core/README.md)
- [ADR-073: Move the numeric core into Galaga](../adrs/073-move-the-numeric-core-into-galaga.md)
- [ADR-075: Promote the core-backed facade](../adrs/075-promote-the-core-backed-facade.md)
- [Historical v2 issue inventory](../../V2-PLANNING.md)

The historical issue inventory predates the Gram-matrix core. It remains useful
for design context, but the core cutover plan and accepted ADRs take precedence
for implementation sequencing.
