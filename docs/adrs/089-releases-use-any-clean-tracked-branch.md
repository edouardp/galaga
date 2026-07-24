---
status: accepted
date: 2026-07-24
deciders: edouard
---

# ADR-089: Releases Use Any Clean Tracked Branch

## Context and problem statement

The shared publish guard originally required the checked-out branch to be
named `main`. Galaga 2 is developed and externally validated on the
long-running `galaga_v2` branch, and its explicit alpha, beta, and
release-candidate train should be publishable from that branch.

A branch name is a workflow convention, not an artifact-integrity property.
Requiring `main` would force an otherwise unnecessary merge before every
prerelease and would make the release commit less useful as a record of the
branch actually under validation.

Removing the name check entirely still leaves one operational risk:
`release.sh` uses an unqualified `git push` after publication. A detached
checkout or a branch without an upstream could therefore publish artifacts and
then fail to push the release commit.

## Decision drivers

- Allow Galaga 2 prereleases directly from `galaga_v2`.
- Avoid encoding a permanent branch-name convention in publication tooling.
- Keep releases reproducible from a committed source state.
- Fail before artifact publication if the eventual `git push` cannot identify
  its destination.
- Retain the clean-worktree protection shared by release and direct-publish
  scripts.

## Decision outcome

The shared publish guard does not allowlist `main` or any other branch name.
A release or direct publication may run from any branch that:

1. is attached rather than a detached `HEAD`;
2. has a configured upstream; and
3. has a clean working tree.

The guard reports the resolved local branch and upstream before work begins.
The release commit remains on the branch being validated, the script's
unqualified `git push` updates that configured upstream, and the version tag
continues to identify the exact release commit independently of branch name.

For the first Galaga 2 alpha, this permits:

```bash
git switch galaga_v2
git status --short --branch
make release VERSION=2.0.0a1
```

provided `galaga_v2` tracks the intended remote branch and the worktree is
clean.

## Consequences

- Good, because prereleases can follow the branch where their code and review
  history live.
- Good, because the policy works for future release branches without changing
  shell code.
- Good, because missing-upstream and detached-head failures occur before
  package publication.
- Good, because the clean-worktree invariant remains enforced.
- Cost, because maintainers must confirm that the configured upstream is the
  intended publication branch.
- Cost, because repository policy—not the release script—decides when a
  release branch is merged into `main`.
