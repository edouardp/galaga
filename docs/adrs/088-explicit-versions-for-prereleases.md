---
status: accepted
date: 2026-07-24
deciders: edouard
---

# ADR-088: Explicit Versions for Prereleases

## Context and problem statement

Galaga's established release interface computes stable semantic-version bumps
through `make release-patch`, `make release-minor`, `make release-major`, or an
interactive chooser. That interface is convenient for routine releases and
should remain the default.

Galaga 2 needs an alpha, beta, and release-candidate cycle. A prerelease bump
cannot be selected accurately with only `patch`, `minor`, and `major`: the
maintainer must choose both the target phase and its serial number. Inferring
the next prerelease from repository state would add hidden policy to a workflow
whose most consequential input should be obvious at the command line.

The source currently carries the intended final version `2.0.0` even though it
has not been published. Bootstrapping the public cycle at `2.0.0a1` is therefore
a deliberate apparent downgrade that ordinary automatic version-bump tools
rightly refuse.

## Decision drivers

- Preserve the reliable stable-release commands unchanged.
- Make exceptional prerelease releases explicit and reviewable.
- Accept only canonical versions that PyPI, installers, and GitHub agree on.
- Keep version calculation testable without running the destructive release
  workflow.
- Mark GitHub prereleases consistently with the package metadata.
- Keep companion packages installable against the exact Galaga release.

## Decision outcome

`make release VERSION=<version>` is the explicit release path. It accepts only:

- `X.Y.Z` for an exact stable release;
- `X.Y.ZaN` for an alpha;
- `X.Y.ZbN` for a beta; and
- `X.Y.ZrcN` for a release candidate.

The Galaga 2 major-release train is five explicit, complete releases:

```bash
make release VERSION=2.0.0a1
make release VERSION=2.0.0a2
make release VERSION=2.0.0b1
make release VERSION=2.0.0rc1
make release VERSION=2.0.0
```

The sequence is policy rather than automatic inference. Each invocation runs
the complete release workflow and is followed by whatever validation is
appropriate to that lifecycle stage. More alphas, betas, or release candidates
may be inserted, but the final stable invocation may not be omitted.

In particular, `2.0.0rc1` remains a prerelease forever; PyPI does not mutate it
into `2.0.0`. The last command explicitly publishes the distinct stable
version, creates tag `v2.0.0`, and creates a GitHub release without the
prerelease marker. `make release-major` is not an RC-promotion command and is
rejected while the current source version is a prerelease.

Exact stable versions are therefore accepted so the final release can follow
an `rc` without inventing another command. After `2.0.0` is published, the
ordinary computed paths resume with `make release-patch`, `make release-minor`,
or `make release-major`.

The existing patch, minor, and major paths continue to calculate a version only
from a stable current version. During a prerelease cycle, automatic bumps are
rejected with guidance to use the explicit path.

Version parsing and bump calculation live in the pure
`scripts/release_version.py` helper. `scripts/release.sh` retains orchestration,
mutation, testing, publishing, tagging, and GitHub release creation. The helper
reports whether the resolved version is a prerelease, and the orchestrator adds
GitHub's `--prerelease` flag accordingly.

The jointly released `galaga`, `galaga-marimo`, and `galaga-matrix` packages
receive the exact version. Every companion package, including the independently
versioned experimental `galaga-mermaid`, receives a `galaga>=<version>`
dependency floor. `galaga-mermaid` is not added to the joint publication set by
this decision.

## Consequences

- Good, because routine stable releases retain their concise existing commands.
- Good, because a prerelease version is visible in shell history and review
  rather than inferred.
- Good, because the same validator covers alpha, beta, release candidate, and
  exact final transitions.
- Good, because final publication requires a visible, deliberate stable-version
  command rather than treating an RC as implicitly final.
- Good, because unsupported PEP 440 forms such as development, post, and local
  versions cannot accidentally enter this release policy.
- Good, because pure unit tests exercise release calculation without PyPI or
  GitHub side effects.
- Cost, because maintainers must type each prerelease serial explicitly.
- Cost, because starting at `2.0.0a1` from the unpublished `2.0.0` source
  version is intentionally non-monotonic.
- Deferred, because independent publication of `galaga-mermaid` remains a
  separate workflow decision.
