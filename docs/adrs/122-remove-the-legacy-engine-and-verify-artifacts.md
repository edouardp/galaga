---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-122: Remove the Legacy Engine and Verify Artifacts

> The separately deferred bridge and function-adapter removal is completed
> after `2.0.0a4` in [ADR-130](130-retire-migration-only-api-adapters.md).
> Historical validation checkpoints below are retained; this follow-up does
> not declare the remaining stable-release gates complete.
> The historical CI requirement and alpha-only no-CI scope below are superseded
> by [ADR-131](131-local-only-stable-release-validation.md): stable validation
> also uses an explicit local source-and-artifact gate.

## Context and problem statement

The user requested physical engine removal after the committed dependency
checkpoint `995aed6`. Public contracts and historical evidence now outlive the
v1 implementation. An import guard alone cannot prove deletion: artifacts
could still ship unreachable code, and empty retired directories can become
importable namespace packages.

## Decision outcome

Delete all twenty-one production paths in `LEGACY_ONLY_SUBMODULES`: the
table-backed algebra, basis/convention helpers, operation and expression
registries, symbolic/lazy adapters, old LaTeX pipeline, `legacy` and
`symbolic_core` packages, and temporary `latex_symbols` shim.
Keep the real converter at `galaga._latex_symbols`, owned publicly through
`galaga.names`, and all current core/facade/expression/rendering algorithms.

Historical source and observations remain in development-only baselines and
Git, not in a relocated executable engine. The compatibility manifest retains
every historical disposition. Its existence tests now require supported paths
to exist and retired files/directories to be absent. A fresh-process check
without the test import guard verifies real `ModuleNotFoundError` failures.
The converter shim test now checks removal plus the public conversion result.

Move leftover bytecode-only retired directories out of the package so they
cannot create namespace packages. No coverage exclusion is added. The only
surviving production edits document the removed oracle; numeric, provenance
and rendering algorithms do not change.

### Make artifact verification a release requirement

[check_galaga_artifact.py](../../scripts/check_galaga_artifact.py) is a
standard-library, read-only validator. It checks wheel and sdist without
extracting or importing them:

- runtime files must match local source byte-for-byte;
- retired files and even empty retired directory entries are rejected;
- required core, facade, expression, rendering, converter and typing files
  must exist;
- runtime source cannot import retired modules or access private product
  tables, including nested scopes and literal dynamic lookups;
- runtime caches, unsafe/duplicate archive members and nonregular sdist
  members fail explicitly; and
- name, version, Python requirement and dependencies must match the project.

`make check-artifacts` builds first and runs this validator. `make check`
includes it, and both joint-release and standalone core-publication scripts
run it after Twine checks but before credential access or publication.
These additions do not perform a release.
Corruption controls exercise files, metadata, directories and the real CLI.

Headless notebook tests derive subprocess import paths from the packages
actually under test. They no longer force repository packages when the parent
is testing installed wheels. Isolated wheel runs additionally verify loaded
package origins. Plotting libraries remain development/example dependencies,
not dependencies of the numeric package.

### Separate physical deletion from release decisions

The `gram_bridge` warning adapter and temporary function spellings remain
unchanged; their removal milestone is before stable 2.0. The high-dimensional
`is_rotor` decision remains separate. No version, classifier, changelog, tag,
commit or publication is implied.

The branch has no configured upstream and its committed checkpoint has no
GitHub CI result. Local deletion and artifact validation do not satisfy the
independent CI/clean-release-branch gate. Repository-wide scanning also found
five older notebooks and a benchmark outside the maintained gallery.
The user subsequently chose migration in place, implemented by
[ADR-123](123-migrate-remaining-teaching-notebooks-and-benchmark.md), rather
than authorising removal of teaching work.

## Verification and consequences

### Alpha preparation follow-up, 2026-09-10

For the next `2.0.0a3` preparation, the user explicitly chose no CI setup.
Use the refreshed local source, installed-wheel and notebook validation
recorded in the gate report, then integrate into the clean tracked
`galaga_v2` branch. Do not describe absent workflows or empty commit-status
lists as passing CI. This alpha-specific validation choice does not assert
completion of the original stable Phase 9 gate, change runtime architecture,
or authorize publication. Concurrent uncommitted user work is excluded from
integration by using a separate clean worktree.

Full tests, before/after branch coverage, clean wheel installations, package
metadata, security checks and benchmarks are recorded in the
[deletion gate report](../v2/legacy-engine-deletion-gate.md). It distinguishes
passing deletion checks from remaining release requirements. Removing dead
modules reduces type debt but does not make the surviving code type-clean.

This completes production-oracle removal planned by
[ADR-085](085-top-level-api-is-the-facade-with-explicit-legacy-oracle.md) and
builds on [ADR-121](121-deletion-ready-namespace-and-import-guards.md).
