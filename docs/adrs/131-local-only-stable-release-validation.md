---
status: accepted
date: 2026-09-11
deciders: edouard
---

# ADR-131: Local-Only Stable Release Validation

## Context

The user chose no CI and requested completion of the validation, documentation
and clean-artifact preparation for Galaga 2. The alpha-only follow-up in
[ADR-122](122-remove-the-legacy-engine-and-verify-artifacts.md) left the original
stable CI requirement unresolved. Also, `scripts/lint.sh` swallowed dependency
audit and type-check failures and could print success after either failed.

## Decision

Use an explicitly recorded local release gate for beta, RC and stable 2.0,
not a required CI workflow. This supersedes the CI requirement in the cutover
plan and extends ADR-122's alpha-only validation policy. Missing CI results
are neither passes nor blockers under this policy.

Every lint stage must fail the command on a tool failure, including audit
service errors. Preserve full type diagnostics. Regression tests execute the
real shell orchestration with failing tools, in normal and fix modes.

The maintainer records the source revision and any working-tree changes,
interpreter/dependency versions, full source tests, branch coverage, type/lint
and security results, documentation checks, builds, installed-wheel suites
and a benchmark comparison. Python 3.11 covers core, matrix, AnyWidget and the
experimental Mermaid integration; Python 3.14 additionally covers Marimo and
the maintained notebook gallery. Installed tests must verify runtime module
origins under site-packages, without editable runtime dependencies.

Coverage is compared with the prior recorded gate, with unexplained losses
investigated rather than hidden by exclusions. Timing is a reviewed local
comparison, not a cross-machine threshold. Missing advisory data for an
unpublished local project must be recorded separately from third-party
vulnerabilities; neither vulnerabilities nor service failures may be silently
ignored. Full companion suites include Mermaid, but joint publication does not.

Current alpha versions and Alpha classifiers stay accurate during preparation.
At the actual beta/RC release, set the four jointly released projects to
`Development Status :: 4 - Beta`; at final, use
`Development Status :: 5 - Production/Stable` and lead their READMEs and the
migration guide with stable installation commands. Mermaid remains experimental
and independently versioned. Changelog changes belong to the release itself.

## Consequences and boundaries

There is no automatic CI or publication. `make validate` is a fail-closed local
source gate, not a substitute for the full installed-artifact checklist in the
[release process](../RELEASE_PROCESS.md). The release script runs its documented
subset; the maintainer must run and record the additional stable checks.

A working-tree validation checkpoint does not certify the eventual release
commit. Rerun the gate from the clean, tracked candidate after integrating
changes. Install and review the published RC before final; explicitly authorize
the release, metadata changes and publication then. No merge, version bump,
tag or upload is implied by this preparation.
