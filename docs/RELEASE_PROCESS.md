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
```

### What the Release Script Does

`scripts/release.sh <patch|minor|major>` runs these steps in order:

| Step | What | Fails if |
|---|---|---|
| 1. Guard | Check on `main`, clean working tree | Dirty repo or wrong branch |
| 2. Bump | Update version in both `pyproject.toml` files + galaga dep pin | — |
| 3. Changelog | Open `$EDITOR` for release notes, auto-fix markdown | Placeholder not replaced |
| 4. Commit | `git commit -m "Release vX.Y.Z"` | Pre-commit hooks fail |
| 5. Test galaga | `pytest packages/galaga/tests/` (Python 3.13) | Any test failure |
| 6. Test galaga-marimo | `pytest` in temp Python 3.14 venv | Any test failure |
| 7. Build | `uv build` both packages | Build failure |
| 8. Twine check | Validate wheel/sdist metadata | Bad metadata or README |
| 9. Publish galaga | `uv publish` to PyPI | Auth failure or version conflict |
| 10. Publish galaga-marimo | `uv publish` to PyPI | Auth failure or version conflict |
| 11. Push | `git push` the release commit | — |
| 12. Tag | `git tag vX.Y.Z && git push origin vX.Y.Z` | — |
| 13. GitHub release | `gh release create` from CHANGELOG | — |

If any step fails, the script stops. Nothing is published or tagged until tests pass.

### Files Modified by a Release

- `packages/galaga/pyproject.toml` — version bumped
- `packages/galaga_marimo/pyproject.toml` — version bumped + galaga dep pin updated
- `CHANGELOG.md` — new section added

### Packages Published

| Package | PyPI | Import | Python |
|---|---|---|---|
| `galaga` | <https://pypi.org/project/galaga/> | `from galaga import Algebra` | ≥ 3.11 |
| `galaga-marimo` | <https://pypi.org/project/galaga-marimo/> | `import galaga_marimo as gm` | ≥ 3.14 |

`galaga` is always published first because `galaga-marimo` depends on it.

## Versioning Policy

Follow [Semantic Versioning](https://semver.org/):

| Bump | When | Example |
|---|---|---|
| Patch | Bug fixes, docs, tests, internal cleanup | `0.3.3 → 0.3.4` |
| Minor | New operations, new features, pre-1.0 breaking changes | `0.3.4 → 0.4.0` |
| Major | Breaking changes to public API (post-1.0) | `0.4.0 → 1.0.0` |

Pre-1.0, minor bumps are acceptable for breaking changes. Document them clearly in the CHANGELOG.

## Quality Gates

Before every release, the script enforces:

- [ ] All galaga tests pass (Python 3.13)
- [ ] All galaga-marimo tests pass (Python 3.14)
- [ ] Pre-commit hooks pass (ruff, shellcheck, bandit, rumdl, checkmake)
- [ ] Twine check passes (metadata + README render)
- [ ] CHANGELOG has been edited (placeholder removed)
- [ ] Working tree is clean
- [ ] On `main` branch

### Manual Checks (Not Automated)

- [ ] Examples still run: `uv run marimo edit examples/basics/naming_demo.py`
- [ ] README renders correctly on PyPI after publish
- [ ] `pip install galaga` in a clean venv works

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

The release script runs `git commit` which triggers pre-commit. Fix the issues, then re-run the release. The script is safe to re-run — it will re-bump from the current version.

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
