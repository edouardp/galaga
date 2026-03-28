# PyPI Release Plan

Release plan for the `galaga` and `galaga-marimo` packages.

## Package Overview

| Package | Description | Python | Dependencies |
|---|---|---|---|
| `galaga` | Numeric geometric algebra library | ≥ 3.11 | numpy |
| `galaga-marimo` | Marimo notebook helpers with t-string LaTeX rendering | ≥ 3.14 | galaga, marimo |

Both packages are MIT licensed, authored by Edouard Poor.

---

## Pre-Release Checklist

### 1. Name availability ✅

```
galaga          — available on PyPI
galaga-marimo   — available on PyPI
```

### 2. Fix project URLs

The `pyproject.toml` URLs currently point to `github.com/edouard/galaga` — update
to the correct repo URL `github.com/edouardp/ga` (or rename the repo to match).

```toml
# packages/galaga/pyproject.toml
[project.urls]
Homepage = "https://github.com/edouardp/ga"
Repository = "https://github.com/edouardp/ga"
Issues = "https://github.com/edouardp/ga/issues"
Documentation = "https://github.com/edouardp/ga/tree/main/docs"
```

### 3. Fix gamo workspace dependency

`packages/galaga_marimo/pyproject.toml` has `[tool.uv.sources] galaga = { workspace = true }`
which only works locally. For PyPI, the `dependencies` list is sufficient — remove
the `[tool.uv.sources]` section from gamo's pyproject.toml before publishing.

### 4. Pin dependency ranges

```toml
# galaga
dependencies = ["numpy>=1.24"]  # not >=2.4.3 — support older numpy

# galaga-marimo
dependencies = ["galaga>=0.1.0", "marimo>=0.21.1"]
```

### 5. Add py.typed marker

Create `packages/galaga/ga/py.typed` (empty file) so type checkers recognise the
package as typed (the `Typing :: Typed` classifier is already set).

### 6. Verify README renders on PyPI

PyPI renders README.md — check that:
- No relative links that break (images, internal docs links)
- Code blocks render correctly
- Tables render correctly

Test with: `uv build && twine check dist/*`

### 7. Add CHANGELOG.md

Create a changelog for the initial release:

```markdown
# Changelog

## 0.1.0 (2026-03-25)

Initial release.

- Algebra construction from signature tuples
- Full product suite: gp, op, left/right contraction, Doran–Lasenby inner,
  Hestenes inner, scalar product, commutator, anticommutator, lie_bracket,
  jordan_product
- Unary operations: reverse, involute, conjugate, grade, dual, undual,
  complement, norm, unit, inverse, exp, log
- Symbolic expression trees with LaTeX/Unicode rendering
- Simplification engine with fixed-point iteration
- Unicode pretty-printing with opt-in flag
- Rotor construction with validation and auto-normalisation
```

---

## Build and Test

### Local build

```bash
cd packages/galaga && uv build
cd packages/galaga_marimo && uv build
```

### Install into clean venv and test

```bash
uv venv /tmp/galaga-test --python 3.13
source /tmp/galaga-test/bin/activate
pip install packages/galaga/dist/galaga-0.1.0-py3-none-any.whl
python -c "from ga import Algebra; alg = Algebra((1,1,1)); print(alg)"
python -m pytest packages/galaga/tests/
deactivate

uv venv /tmp/gamo-test --python 3.14
source /tmp/gamo-test/bin/activate
pip install packages/galaga/dist/galaga-0.1.0-py3-none-any.whl
pip install packages/galaga_marimo/dist/galaga_marimo-0.1.0-py3-none-any.whl
python -c "import galaga_marimo; print('OK')"
deactivate
```

---

## Publish

### Dry run on Test PyPI

```bash
# Publish galaga first (gamo depends on it)
cd packages/galaga
uv build
uv publish --publish-url https://test.pypi.org/legacy/

# Then gamo
cd packages/galaga_marimo
uv build
uv publish --publish-url https://test.pypi.org/legacy/
```

Verify installation from Test PyPI:
```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ galaga
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ galaga-marimo
```

### Publish to production PyPI

```bash
cd packages/galaga && uv build && uv publish
cd packages/galaga_marimo && uv build && uv publish
```

Order matters: `galaga` must be published before `galaga-marimo`.

### Tag the release

```bash
git tag v0.1.0
git push origin v0.1.0
```

Create a GitHub release with the changelog content.

---

## CI/CD Automation

### GitHub Actions: Test on PR

`.github/workflows/test.yml`:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv venv --python ${{ matrix.python-version }}
        env:
          UV_PYTHON: ${{ matrix.python-version }}
      - run: uv sync
      - run: uv run pytest packages/galaga/tests/ -v
```

### GitHub Actions: Publish on tag

`.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # for trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv venv --python 3.14
      - run: uv sync
      - run: uv run pytest packages/galaga/tests/ -v
      - run: cd packages/galaga && uv build && uv publish
      - run: cd packages/galaga_marimo && uv build && uv publish
```

Configure trusted publishing on PyPI (Settings → Publishing → Add publisher)
for both packages, linked to the GitHub repo and workflow.

---

## Ongoing Custodianship

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- **Patch** (0.1.x): bug fixes, docstring updates, new tests
- **Minor** (0.x.0): new operations, new symbolic classes, new examples
- **Major** (x.0.0): breaking changes to named functions, changed operator mappings

The commutator convention change and `|` operator change would have been major
version bumps post-1.0. Pre-1.0, minor bumps are acceptable for breaking changes.

### Release cadence

- No fixed schedule — release when there's meaningful new content
- Bug fixes: release promptly
- New features: batch into minor releases
- Breaking changes: document in CHANGELOG, bump version appropriately

### Quality gates

Before every release:
- [ ] All tests pass (`pytest packages/galaga/tests/ -v`)
- [ ] All examples run (`for f in examples/*.py; do python "$f"; done`)
- [ ] No syntax warnings (`python -W error -c "ast.parse(open(f).read())"`)
- [ ] CHANGELOG updated
- [ ] Version bumped in `pyproject.toml`
- [ ] README renders correctly (`twine check dist/*`)

### Dependency management

- **numpy**: support the oldest numpy that works (currently ≥1.24). Test against
  latest numpy in CI. Bump minimum only when using new numpy features.
- **marimo**: track marimo releases. The t-string API is new — watch for breaking
  changes in `string.templatelib`.
- **Python**: `galaga` supports 3.11+. `galaga-marimo` requires 3.14+ (t-strings).
  When 3.15 ships, test and add to CI matrix.

### Documentation

- Keep ADRs up to date — new design decisions get new ADRs
- Keep DESIGN_DECISIONS.md in sync with ADR index
- README is the primary user-facing doc — keep examples working
- Example notebooks are integration tests — if they break, something is wrong

### Community

- GitHub Issues for bug reports and feature requests
- PRs welcome with tests
- Breaking changes require an ADR before implementation

### Monitoring

- Watch PyPI download stats (pypistats.org)
- Watch GitHub issues for common pain points
- Watch numpy/marimo release notes for compatibility issues

---

## Implementation Timeline

| Step | Action | Effort |
|---|---|---|
| 1 | Fix URLs, pin deps, remove workspace source from gamo | 15 min |
| 2 | Add py.typed, CHANGELOG.md | 10 min |
| 3 | Local build + clean venv test | 20 min |
| 4 | Test PyPI dry run | 15 min |
| 5 | Production PyPI publish | 5 min |
| 6 | Git tag + GitHub release | 5 min |
| 7 | Set up GitHub Actions (test + publish) | 30 min |
| **Total** | | **~1.5 hours** |
