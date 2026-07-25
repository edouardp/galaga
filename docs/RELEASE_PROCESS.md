# Release Process

## One-Time Setup

### PyPI Accounts

1. Create a production PyPI account at <https://pypi.org/account/register/>
2. Create a Test PyPI account at <https://test.pypi.org/account/register/> (completely separate credentials)
3. Generate API tokens:
   - Production: <https://pypi.org/manage/account/token/>
   - Test: <https://test.pypi.org/manage/account/token/>

### Credential Storage

Store tokens in the system keyring (macOS Keychain):

```bash
# Production PyPI
keyring set https://upload.pypi.org/legacy/ __token__
# paste token when prompted

# Test PyPI
keyring set https://test.pypi.org/legacy/ __token__
# paste token when prompted
```

The publish scripts use `--keyring-provider subprocess --username __token__` to retrieve these automatically.

### Tool Installation

```bash
# Install dev dependencies (includes ruff, pre-commit, bandit, etc.)
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify keyring has the token
keyring get https://upload.pypi.org/legacy/ __token__
```

### GitHub CLI

The release script uses `gh` to create GitHub releases:

```bash
brew install gh
gh auth login
```

## Release Workflow

### Quick Reference

```bash
make release-patch   # 0.3.3 → 0.3.4  (bug fixes, docs)
make release-minor   # 0.3.3 → 0.4.0  (new features)
make release-major   # 0.3.3 → 1.0.0  (breaking changes)
make release         # choose patch, minor, or major interactively
```

These are the normal release paths. They calculate the next stable version and
require the current source version to be stable.

### Major-Release Alpha, Beta, RC, and Final Train

A breaking major release is a sequence of complete releases. For Galaga 2, run
this train in order:

```bash
make release VERSION=2.0.0a1
make release VERSION=2.0.0a2
make release VERSION=2.0.0b1
make release VERSION=2.0.0rc1
make release VERSION=2.0.0
```

Each command runs the whole release workflow: version and dependency
synchronization, changelog editing, tests, builds, publication, tagging, and a
GitHub release. Do not run the five commands back-to-back mechanically. Move to
the next stage only after the preceding release has been published, installed,
and evaluated. Additional alphas, betas, or release candidates can be inserted
when validation finds work that needs another public iteration.

| Stage | Command | Purpose |
|---|---|---|
| First alpha | `make release VERSION=2.0.0a1` | First public build of the breaking release |
| Second alpha | `make release VERSION=2.0.0a2` | Incorporate early API and migration feedback |
| Beta | `make release VERSION=2.0.0b1` | Feature-complete external validation |
| Release candidate | `make release VERSION=2.0.0rc1` | Final release-shaped validation |
| Final | `make release VERSION=2.0.0` | Publish the stable major release |

**The final command is mandatory.** `2.0.0rc1` is still a prerelease on PyPI
and GitHub. It does not become `2.0.0` automatically, and
`make release-major` must not be used to promote it. The exact
`make release VERSION=2.0.0` invocation removes the prerelease suffix,
publishes the stable artifacts, creates tag `v2.0.0`, and creates a stable
GitHub release.

For a future major version, substitute its exact target throughout the same
pattern—for example, `3.0.0a1` through `3.0.0`. After the final stable release,
the ordinary commands resume; `make release-patch` would advance `2.0.0` to
`2.0.1`.

Supported exact forms are `X.Y.Z`, `X.Y.ZaN`, `X.Y.ZbN`, and `X.Y.ZrcN`.
Development, post, local, noncanonical, and SemVer-style `-alpha` versions are
rejected.

The stored package version is release state, not merely a value supplied by
`VERSION=`. After publishing `2.0.0a1`, the package metadata remains
`2.0.0a1`; the next invocation must select a new target such as `2.0.0a2`.
Repeating an exact version is rejected locally, and PyPI never permits a file
for an already published project/version pair to be replaced.

### What the Release Script Does

`scripts/release.sh <patch|minor|major>` and
`scripts/release.sh --version <version>` run these steps in order:

| Step | What | Fails if |
|---|---|---|
| 1. Guard | Resolve the current branch/upstream and check the working tree | Detached HEAD, missing upstream, or dirty repo |
| 2. Resolve | Calculate a stable bump or validate an exact stable/prerelease version | Invalid or repeated version |
| 3. Synchronize | Update the three released packages and all companion galaga dependency floors | — |
| 4. Changelog | Open `$EDITOR` for release notes, auto-fix markdown | Placeholder not replaced |
| 5. Commit | `git commit -m "Release vX.Y.Z"` | Pre-commit hooks fail |
| 6. Test release workflow | `python -m pytest tests/release/` | Any repository-tooling test failure |
| 7. Test galaga | `pytest packages/galaga/tests/` | Any test failure |
| 8. Test galaga-matrix | `pytest packages/galaga_matrix/tests/` | Any test failure |
| 9. Test galaga-marimo | `pytest` in a temporary Python 3.14 venv | Any test failure |
| 10. Build | `uv build` all three released packages | Build failure |
| 11. Twine check | Validate wheel/sdist metadata | Bad metadata or README |
| 12. Publish | Publish galaga, then Marimo and matrix companions | Auth failure or version conflict |
| 13. Push and tag | Push the commit and `vX.Y.Z` tag | Git failure |
| 14. GitHub release | Create from CHANGELOG; mark non-final versions as prereleases | GitHub failure |

If any step fails, the script stops. Nothing is published or tagged until all
tests and artifact checks pass. Publication itself is sequential rather than
transactional: a failure after the first upload can leave some packages
published and others absent. Follow the failure-stage rules below rather than
blindly rerunning the command.

Release-workflow tests live at repository level because they exercise the
Makefile, shell scripts, Git state, and repository version policy rather than
the installable `galaga` package. Run them independently with
`make test-release`.

### Release Branch Policy

Releases are not restricted to `main`. The shared publish guard accepts any
clean attached branch with a configured upstream. This lets the Galaga 2
prerelease train run directly from `galaga_v2`:

```bash
git switch galaga_v2
git status --short --branch
git branch --verbose --verbose
make release VERSION=2.0.0a1
```

Before continuing, verify that the status is clean and that the branch tracks
the intended remote—for example, `origin/galaga_v2`. The release commit is
created on the checked-out branch, and the script's `git push` updates that
branch's configured upstream. Tags and GitHub releases still identify the
exact release commit independently of the branch name.

### Files Modified by a Release

- `packages/galaga/pyproject.toml` — version bumped
- `packages/galaga_marimo/pyproject.toml` — version bumped + galaga dep pin updated
- `packages/galaga_matrix/pyproject.toml` — version bumped + galaga dep pin updated
- `packages/galaga_mermaid/pyproject.toml` — galaga dep pin updated; its own version is independent
- `uv.lock` — regenerated for the workspace version
- `CHANGELOG.md` — new section added

### Packages Published

| Package | PyPI | Import | Python |
|---|---|---|---|
| `galaga` | <https://pypi.org/project/galaga/> | `from galaga import Algebra` | ≥ 3.11 |
| `galaga-matrix` | <https://pypi.org/project/galaga-matrix/> | `import galaga_matrix` | ≥ 3.11 |
| `galaga-marimo` | <https://pypi.org/project/galaga-marimo/> | `import galaga_marimo as gm` | ≥ 3.14 |

`galaga` is always published first because both companion packages depend on
it. `galaga-mermaid` remains experimental and independently versioned; the
joint release updates its dependency floor but does not publish it.

## Versioning Policy

Follow [Semantic Versioning](https://semver.org/):

| Bump | When | Example |
|---|---|---|
| Patch | Bug fixes, docs, tests, internal cleanup | `0.3.3 → 0.3.4` |
| Minor | New operations, new features, pre-1.0 breaking changes | `0.3.4 → 0.4.0` |
| Major | Breaking changes to public API (post-1.0) | `0.4.0 → 1.0.0` |
| Alpha | Early breaking-release validation | `2.0.0a1 → 2.0.0a2` |
| Beta | Feature-complete external validation | `2.0.0b1 → 2.0.0b2` |
| RC | Final-candidate validation | `2.0.0rc1 → 2.0.0` |

Pre-1.0, minor bumps are acceptable for breaking changes. Document them clearly in the CHANGELOG.

PyPI derives prerelease status from the PEP 440 version. GitHub needs an
explicit prerelease flag, which the release workflow adds for `a`, `b`, and
`rc` versions. Installers do not normally choose a prerelease unless the user
opts in, requests it exactly, or uses a requirement whose available candidates
require prerelease consideration.

The release command does not infer lifecycle progress. In particular, it never
turns an RC into a final release. The maintainer explicitly chooses
`make release VERSION=X.Y.Z` after accepting the release candidate.

## Quality Gates

Before every release, the script enforces:

- [ ] Repository release-workflow tests pass
- [ ] All galaga tests pass (release environment, Python ≥3.11)
- [ ] All galaga-matrix tests pass (Python 3.11+)
- [ ] All galaga-marimo tests pass (Python 3.14)
- [ ] Pre-commit hooks pass (ruff, shellcheck, bandit, rumdl, checkmake)
- [ ] Twine check passes (metadata + README render)
- [ ] CHANGELOG has been edited (placeholder removed)
- [ ] Working tree is clean
- [ ] Current branch is attached and tracks the intended remote branch

### Manual Checks (Not Automated)

- [ ] Examples still run: `make run-marimo`
- [ ] README renders correctly on PyPI after publish
- [ ] The exact release installs in a clean venv without repository paths
- [ ] Each jointly released companion imports against that installed wheel

### Stable 2.0 RC and Final Gates

Before `2.0.0rcN` and again before stable `2.0.0`:

- [ ] Phase 9 of the
  [core cutover plan](v2/core-cutover-plan.md) is complete
- [ ] The table-backed engine and `galaga.legacy` do not ship in the wheel
- [ ] Migration-only `galaga.gram_bridge` paths follow their final removal
  policy
- [ ] The [Galaga 1 to 2 migration guide](v2/migration-guide.md) reflects every
  removal and corrected mathematical convention
- [ ] Package classifiers no longer describe a stable release as Alpha
- [ ] Published READMEs lead with the stable install command rather than the
  prerelease opt-in command
- [ ] Companion dependency floors resolve to the intended final Galaga version
- [ ] `make validate` passes from a clean checkout
- [ ] Built wheels install and pass import/numeric smoke tests in clean Python
  3.11 and 3.14 environments as applicable
- [ ] The release candidate has been installed from PyPI and reviewed before
  invoking `make release VERSION=2.0.0`

## Ongoing Custodianship

### After Each Release

1. Check the PyPI pages render correctly
2. Verify install from PyPI: `pip install galaga==X.Y.Z`
3. Monitor GitHub issues for install/import problems

### Dependency Management

| Dependency | Policy |
|---|---|
| numpy | Support ≥1.24. Test against latest in CI. Bump minimum only when using new features. |
| marimo | Track releases. Watch for t-string API changes in `string.templatelib`. |
| Python | galaga supports 3.11+. galaga-marimo requires 3.14+. Add new versions to CI matrix when released. |

### Monitoring

- PyPI download stats: <https://pypistats.org/packages/galaga>
- GitHub issues for common pain points
- numpy/marimo release notes for compatibility issues
- `make lint` includes `pip-audit` for dependency CVEs

### When to Release

- Bug fixes: release promptly
- New features: batch into minor releases
- Breaking changes: document in CHANGELOG, bump version appropriately
- No fixed schedule — release when there's meaningful new content

## Troubleshooting

### "Missing credentials" on publish

```bash
# Check keyring has the token
keyring get https://upload.pypi.org/legacy/ __token__

# If empty, re-add it
keyring set https://upload.pypi.org/legacy/ __token__
```

### "Version already exists" on PyPI

You can't re-publish the same version. Bump the version and release again.

### Pre-commit hooks fail on release commit

The release script updates version files and the changelog before it attempts
the commit. Fix the reported files, then inspect `git status` and the stored
version before deciding how to continue. Do not assume that rerunning the same
exact-version command is safe: once the files already contain the target,
version resolution rejects the repeated target.

### A post-commit test or build failed

The release commit now exists, but no package has yet been published. Fix the
failure in a new commit. To run the complete orchestration again for the same
target, restore the jointly released package metadata to the previous released
version in another explicit commit, confirm a clean tracked branch, and then
invoke the exact target again. Do not amend the original release commit.

The safer alternative for a public prerelease train is to choose the next
serial after fixing the problem, for example `2.0.0a2`.

### Publication failed partway through

First check each PyPI project page. Published artifacts are immutable. If any
package for the target version exists, do not try to replace it and do not
delete tags or rewrite pushed history. Fix the failure and publish a new
prerelease serial. Record the partial release in the changelog or GitHub
release notes so dependency resolution is understandable.

### galaga-marimo tests fail (Python 3.14 not found)

```bash
# Install Python 3.14
brew install python@3.14
# Or via pyenv
pyenv install 3.14
```

### Test PyPI (for testing the publish flow)

```bash
# Build and publish to Test PyPI
uv build
uv publish --publish-url https://test.pypi.org/legacy/ --keyring-provider subprocess --username __token__ dist/*

# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ galaga
```
