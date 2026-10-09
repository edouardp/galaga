# Galaga 2 Development History

These records describe the development and migration of Galaga 2. Their API
examples, commands, test counts, and outstanding-work lists belong to the
checkout recorded in each document. For current usage, see the
[architecture guide](README.md) and [package guide](../../packages/galaga/README.md).

## Completed plans and inventories

| Record | Purpose |
|---|---|
| [Core cutover plan](core-cutover-plan.md) | Replacement sequence, work units, and original phase gates |
| [Presentation and expression layer plan](presentation-symbolic-layer-plan.md) | Design alternatives and implementation sequence above the numeric core |
| [Public API migration matrix](public-api-migration-matrix.md) | Historical classification of Galaga 1 APIs and their replacements |
| [Numeric test migration inventory](numeric-test-migration-inventory.md) | Original ownership and consolidation of mathematical tests |
| [Migration engineering techniques](migration-engineering-techniques.md) | Source rewriting, independent oracles, and staged validation methods |

## Recorded validation and reviews

| Record | Purpose |
|---|---|
| [Legacy engine deletion checkpoints](legacy-engine-deletion-gate.md) | Dated source, wheel, dependency, typing, and coverage observations |
| [Phase 8 performance baseline](phase8-performance.md) | Historical measurements on the recorded machine and interpreter |
| [Post-a4 documentation review](documentation-review.md) | September 2026 review scope and measured results |
| [Rendering review report](rendering-parity-reports/latex-parity-20260719-184624+1200.md) | Original comparison and review of v1/v2 LaTeX output |

## Decisions and retirement

The [ADR index](../adrs/README.md) records decisions and later supersessions.
[ADR-170](../adrs/170-retire-migration-scaffolding-before-stable-2.md) records
retirement of the migration tools, ownership ledgers, import guards, and
cutover benchmark. Their original source remains available in Git history.

Current numeric and presentation regressions continue in ordinary test suites.
The [rendering snapshot guide](rendering-parity.md) documents the retained
expression recipes and reviewed expectations. The
[release process](../RELEASE_PROCESS.md) is the operational checklist for each
new candidate.
