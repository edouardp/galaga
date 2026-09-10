---
status: accepted
date: 2026-09-10
deciders: edouard
---

# ADR-130: Retire Migration-Only API Adapters

## Context

[ADR-079](079-curated-compatibility-without-redundant-helpers.md) retained six
warning-emitting function spellings and three `galaga.gram_bridge` import paths
only for migration, with removal before stable 2.0. The engine was deleted in
[ADR-122](122-remove-the-legacy-engine-and-verify-artifacts.md), but these
adapters still ship in `2.0.0a4`. The user has now authorized completion of the
API cleanup before a release candidate.

## Decision

Remove the `gram_bridge` package and its `facade` and `catalog` re-exports.
Applications import `galaga` or `galaga.facade`; catalog consumers import
`galaga.facade.catalog`. Leave no empty bridge directory that Python could
import as a namespace package.

Remove `involute`, `mag2`, `magnitude_squared`, `norm_squared`, `normalise`
and `normalize` from attributes and exports of `galaga` and `galaga.facade`.
Their replacements remain `grade_involution`, `norm2` and `unit`. Remove the
duplicate direct `involute` alias from the numeric core and private facade
numeric module as well, so the retired spelling cannot survive through another
namespace. No numerical algorithm, operation ID or expression rule changes.

Delete the now-unused private `_compat` module, `GalagaDeprecationWarning`
class and `DEPRECATED_OPERATION_ALIASES` runtime export. Do not add tombstone
callables or another public compatibility registry. Missing function imports
raise `ImportError`, attribute access fails, and missing bridge imports raise
`ModuleNotFoundError` through normal Python import machinery.

Keep the eight permanent facade aliases unchanged. Keep complete `p_*` preset
factories and concrete preset classes under the independent compatibility
decision in [ADR-129](129-concise-complete-and-resolvable-blade-presets.md).
Do not remove unrelated names such as the catalog's parameter-normalization
callback or model-owned methods just because their spelling overlaps.

## Evidence and enforcement

Keep the frozen v1 API archive unchanged. In the independently maintained
disposition ledger, rename the temporary alias inventory to
`REMOVED_OPERATION_ALIASES`, retain canonical replacements, and classify the
three bridges as removed rather than supported. The historical module
partition now has 12 supported and 24 retired paths; this is not an exhaustive
list of every newer nested module such as `presets.notation`.

Extend the retired-import guard and wheel/sdist validator to the bridge root
and its descendants. Tests check source files, empty directories, artifact
members, live attributes, explicit imports, wildcard imports, core alias maps
and catalog IDs. Fresh-process import checks run without the test guard, so
guard exceptions cannot disguise an importable leftover shim. Canonical
replacement tests retain numeric and tracked-expression checks. Historical
test identities retain explicit current owners instead of being dropped.

Update migration guidance and affected example references. Historical snapshots
and migration-input fixtures may still contain old spellings: they describe
the input being migrated, not current API usage.

## Boundaries

This completes work item W9.2, not the entire stable-release gate. The removal
lands after `2.0.0a4`; no already published alpha is changed. Version numbers,
classifiers, the changelog, release publication, branch integration and the
separate no-CI policy are outside this change. A release candidate and final
artifact validation remain required by the release process.
