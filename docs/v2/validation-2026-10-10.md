# Local Release Validation — 2026-10-10

## Validated revision

Source revision: `244bf1d995d9b04cc1500ebf9b20ed70b1514da8` on
`galaga_v2`, with a clean working tree. The checks passed after the two fixes
listed below. This report records local validation; publication and approval
of a release candidate follow the [release process](../RELEASE_PROCESS.md).

The five jointly released distributions still carry `2.0.0b1` metadata.
Mermaid carries its independent `0.2.0` version. These locally rebuilt files
contain subsequent development work and require a new version before publication.

## Results

| Check | Result |
|---|---|
| `make validate` | Passed: lint, security checks, repository tooling and all package targets |
| Production Pyrefly gate | Zero errors; 12 reviewed warnings |
| `make pre-commit` | All repository hooks passed |
| `make check` | All six wheels and source distributions built; runtime inventory and Twine checks passed |
| `uv lock --check --offline` | Passed |
| Full source suites, Python 3.11.15 | 10,325 passed, 172 skipped |
| Full source suites, Python 3.14.4 | 10,561 passed, 37 skipped |
| Dedicated browser rendering run, Python 3.14.4 | All 17 tests passed after installing headless Chromium |
| Full installed-wheel suites, Python 3.11.15 | 10,342 passed, 155 skipped |
| Full installed-wheel suites, Python 3.14.4 | 10,578 passed, 20 skipped |
| Installed runtime origins | All 72 loaded modules on 3.11 and 75 on 3.14 came from the fresh environments |
| Core wheel with declared dependencies only | Import and numeric/model smoke checks passed on both interpreters with NumPy alone |
| Fresh environment dependency consistency | `uv pip check` passed on both interpreters |
| Fresh environment vulnerability audits | Zero known vulnerabilities among auditable dependencies; Mermaid exception below |
| Repository documentation targets | 1,187 file and heading targets checked across 317 Markdown documents before this report was added |

The full suites include the repository release tests and all companion packages.
Python 3.14 compiled, checked, and exported the 122 discovered Marimo notebooks.
The installed-wheel gallery used the installed runtime packages for its exports.

The source suites ran before Chromium was downloaded, so their skip counts
include 17 browser tests. The dedicated browser run subsequently passed all of
those tests; the installed-wheel runs executed them as part of their full suites.
The remaining skips are declared interpreter, dimensional, or platform cases:
Python 3.11 skips native t-string lessons and the Python 3.14 Marimo package;
small-dimensional fixtures and this machine's `longdouble` precision account
for the other skips. No tests were deselected to make these runs pass.

## Fixes made during validation

- `baa9eb0`: declare shared model attributes and typed provenance parameters,
  narrow the classifier's blade span once, and define public `weight()` on
  the concrete models. CGA retains a tracked scalar multivector; CSTA retains
  a float. Regression tests check both against the actual metric product.
- `244bf1d`: use default factories for matrix-region slices. Python 3.11
  rejects an unhashable slice used directly as a dataclass default, preventing
  annotation imports. The new regression checks whole-matrix defaults and
  independent axis instances; targeted tests passed on both interpreters.

No runtime dependency, package version, coverage exclusion, or lint/type
suppression was added by these fixes.

## Coverage

Coverage was collected with `--cov-branch`. The combined figure divides
covered statements plus covered branches by total statements plus branches.
The core figures below filter the Galaga report to `galaga/core/`.

| Scope | Line coverage | Branch coverage | Combined |
|---|---:|---:|---:|
| Galaga production, Python 3.11 | 95.77% | 90.36% | 94.33% |
| Galaga production, Python 3.14 | 95.76% | 90.36% | 94.32% |
| Numeric core, either interpreter | 97.26% | 94.98% | 96.60% |
| Marimo companion, Python 3.14 | 89.21% | 79.59% | 86.43% |

The Python 3.11 Galaga report covers 8,209 of 8,572 statements and 2,812 of
3,112 branches. There are 363 missing statements and 300 missing branches.
Marimo's separate coverage run passed all 104 tests.

The [September checkpoint](legacy-engine-deletion-gate.md#coverage-review)
recorded 94.85% combined for Galaga, 98.48% for the core, and approximately
86% for Marimo. The current totals are lower for Galaga and the core. The
code and test scopes have changed since that checkpoint, and its raw coverage
files are unavailable for a line-by-line comparison; these percentages do
not establish whether each previously covered line remains covered.

The largest current coverage gaps are configuration loading (81.07% combined),
composition (84.32%), and facade catalog dispatch (88.76%). Model files range
from 91.03% to 100%. The core's missed cases include reflected operator
branches, representation formatting, and numerical rejection paths. These
are concrete targets for further tests; the current reports retain all misses.

## Environments and reviewed diagnostics

Both explicit interpreter runs used isolated environments on macOS ARM64:

| Component | Python 3.11 environment | Python 3.14 environment |
|---|---|---|
| Python | 3.11.15 | 3.14.4 |
| NumPy | 2.4.6 | 2.5.3 |
| pytest | 9.1.1 | 9.1.1 |
| coverage.py | 7.16.2 | 7.16.2 |
| Marimo | 0.24.2 | 0.24.2 |
| Playwright | 1.63.0 | 1.63.0 |

The production type checker reports one dynamic `__all__` warning, redundant
casts, and unnecessary `int`/`bool` conversions. They were inspected with
`pyrefly check --min-severity warn`; no type errors remain and no warning
suppression was added.

`pip-audit` cannot audit the experimental local `galaga-mermaid==0.2.0`
distribution because it is absent from PyPI. Both JSON audit reports explicitly
record that exception. Its declared dependencies were audited normally.
Audit-cache deserialization warnings caused cached entries to be ignored;
both audits completed successfully.

## Reproduction and retained evidence

The repository-level commands were:

```shell
make validate
make check
make pre-commit
uv lock --check --offline
```

The explicit source runs installed all applicable packages as editables into
separate Python 3.11 and 3.14 environments, together with pytest, pytest-cov,
Matplotlib, Playwright and pip-audit. Their pytest invocation included:

```shell
python -m pytest packages tests -q -ra \
  --cov=galaga --cov-branch \
  --cov-report=term --cov-report=json:coverage.json \
  --cov-report=html:htmlcov --junitxml=tests.xml
```

Marimo coverage was collected separately:

```shell
python -m pytest packages/galaga_marimo/tests -q \
  --cov=galaga_marimo --cov-branch --cov-report=json:marimo-coverage.json
```

The artifact runs installed the core wheel first and exercised it with only
NumPy present. They then installed all applicable companion wheels and test
tools. The complete suites used importlib test collection, an import-origin
guard, and a gallery environment selecting the installed packages. The runner
verified loaded runtime modules and rejected editable distribution metadata.
It retained development-only rendering helpers separately from runtime packages.

Logs, interpreter/package inventories, JUnit XML, audit JSON, coverage JSON,
HTML reports, and the temporary runners are retained under
`/tmp/galaga-244bf1d-release`. The top-level command logs are
`/tmp/galaga-244bf1d-validate.log`,
`/tmp/galaga-244bf1d-artifacts.log`, and
`/tmp/galaga-244bf1d-precommit.log`. These paths describe this machine's run;
the test and artifact commands above are the reproducible repository contracts.
