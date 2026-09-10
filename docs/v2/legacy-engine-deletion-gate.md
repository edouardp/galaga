# Legacy Engine Deletion and Release Gate

Date: 2026-09-08. Worktree based on `995aed6`,
`feature/remove-legacy-engine`. This is a local validation report, not a
publication or a declaration that Phase 9 is fully complete.

## Physical deletion

All twenty-one retired production modules are deleted. The live package has
thirty-one Python modules plus `py.typed`. Historical source/observations
remain in development-only baselines and Git. Neither the engine nor its
registries/renderers are relocated into another runtime package.

The real symbol converter remains at `galaga._latex_symbols` and is exposed
through `galaga.names`. Only its temporary old-path shim is deleted.
The `gram_bridge` and deprecated function adapters remain for their separate
stable-release removal decision.

Residual bytecode-only `legacy` and `symbolic_core` directories were moved to
`/tmp/galaga-retired-caches.0HlIfC`. They are recoverable there; deleted source
is recoverable from Git. Removing the directories prevents accidental
namespace-package imports, not just loading of old bytecode.

## Original deletion-checkpoint validation evidence

| Check | Result |
|---|---|
| Full source suite, Python 3.11.15 | 9,126 passed, 78 skipped |
| Full source suite, Python 3.14.4 | 9,276 passed, 20 skipped |
| Clean installed wheels, Python 3.11 | 8,970 package tests passed, 75 skipped; 38 loaded package-module origins verified |
| Clean installed wheels, Python 3.12.13 | 8,973 package tests passed, 75 skipped; 38 loaded package-module origins verified |
| Clean installed wheels, Python 3.13.13 | 8,973 package tests passed, 75 skipped; 38 loaded package-module origins verified |
| Clean installed wheels, Python 3.14 | 9,123 package tests passed, 20 skipped; 40 loaded package-module origins verified |
| New artifact validator | 100% line and branch coverage: 149 statements, 78 branches |
| Production coverage | 95% combined line/branch; no previously covered surviving line or arc lost |
| Wheels and sdists | All five packages built; all ten artifacts passed Twine |
| Galaga runtime contents | Wheel and sdist each contain 32 source-identical, legacy-free runtime files |
| Type check | 34 errors, 17 warnings; down from 295 errors, 18 warnings, not a pass |
| Ruff, shellcheck, Checkmake, Bandit | Pass; existing Bandit annotation warnings remain |
| Vulnerability audit | No known vulnerabilities among auditable installed packages; experimental `galaga-mermaid` is absent from PyPI and skipped |

The three additional cases in the later 3.12/3.13 runs are notebook-path
regressions, also checked separately on Python 3.11. The final release-workflow
suite passes 154 tests, including the standalone-publish gate added after the
full source checkpoint. Markdown lint passes for all thirteen changed
documents, all 356 local links in those documents resolve, and scanning tracked
Markdown finds no links newly broken by deletion. The 73-case historical
rendering audit still matches its reviewed difference ledger.

The surviving production coverage comparison uses source-line mapping for
the two updated package docstrings. All twenty-one deleted modules had zero
executed lines in the pre-deletion parent-process coverage run. Coverage of
live algorithms is unchanged; the aggregate increase from 60% to 95% comes
from removing unexecuted code, not new exclusions or a new claim about tested
branches. No coverage configuration changed.

Fresh environments initially installed only the Galaga wheel and its declared
NumPy dependency. Isolated imports, oblique/native-null Gram products, core
ownership, expression replay and absence of retired imports passed. NumPy
resolved to 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14, separately from the
locked source-tree Python 3.14 environment's 2.5.2.

The applicable companion wheels were then installed, followed by test tools.
The first Python 3.14 full package run exposed a missing development dependency,
Matplotlib, in notebook tests. After installing it, all package tests passed.
Matplotlib was not added to the Galaga runtime requirements. Notebook exports
now derive paths from the packages under test instead of forcing source-tree
imports, so installed-wheel notebook runs stay on installed implementations.
The existing matrix complex-to-real conversion warning remains unchanged.

The fresh artifacts are under `/tmp/galaga-release-gate.6X2Tbo/artifacts`.
The validator is permanent:

```shell
make check-artifacts
make check
uv run python scripts/check_galaga_artifact.py --project packages/galaga \
  dist/galaga-2.0.0a2-py3-none-any.whl dist/galaga-2.0.0a2.tar.gz
```

Use filenames for the version actually built. The validator rejects missing
or changed runtime files, retired files/directories, cached runtime files,
unsafe/duplicate archive entries and metadata/dependency drift. Both the
Makefile and joint/standalone core release workflows invoke it before
fetching credentials or publishing. No release command was run.

## Performance comparison

Same machine, CPython 3.11.15, NumPy 2.4.6, seed `20260721`; median of seven
repeats of 2,000 calls. The benchmark independently checks products against the
reference backend and reverse against its grade-sign law before timing.

| Operation | Layer | Before deletion, µs | After deletion, µs |
|---|---|---:|---:|
| Geometric product | Core | 17.487 | 16.522 |
| Geometric product | Facade, untracked | 19.578 | 17.778 |
| Geometric product | Facade, tracked | 22.596 | 20.002 |
| Reverse | Core | 1.927 | 1.843 |
| Reverse | Facade, untracked | 2.736 | 2.567 |
| Reverse | Facade, tracked | 7.198 | 6.752 |

No slowdown is observed. These small local differences are timing variation,
not evidence that deleting unreachable code accelerated arithmetic. Compared
with the accepted [Phase 8 baseline](phase8-performance.md), the current core
product is 16.522 versus 16.947 µs and reverse is 1.843 versus 1.836 µs.
The archived baseline is not overwritten and v1 is not executed.

## Follow-up: remaining teaching files migrated

The user chose to migrate all six remaining files in place:

- [Batched NumPy benchmark](../../bench_batched.py): derive the structure
  tensor from public left actions, including multi-term Gram products.
- [Mermaid rotations and boosts](../../test_mermaid.py): normalised rotation
  plane, EM-field invariant, and signed Wigner rotation.
- [Dynamic notation](../../examples/basics/dynamic_notation.py): immutable
  reversal rules and presentation-only changes.
- [LaTeX layout](../../examples/basics/latex_rewrites_demo.py): current
  immutable layout semantics versus explicit expression simplification.
- [Marimo helpers](../../examples/basics/galaga_marimo_demo.py): eager
  provenance, semantic content specs, and coefficient display policy.
- [Quantum physics](../../examples/quantum/quantum_physics.py): checked spin
  signs, Bloch geometry, measurement, precession, phase, and interpolation.

All five notebooks now participate in the same source, dependency and
headless execution checks as the existing gallery: **84 notebooks total**.
The root Mermaid path is an explicit codemod allowlist entry, not a general
permission to rewrite root files. Regression tests cover the actual notebook
results at multiple control settings. These files no longer require removed
imports or private product tables. See
[ADR-123](../adrs/123-migrate-remaining-teaching-notebooks-and-benchmark.md).

Targeted Python 3.14 validation includes the full headless gallery and
mathematical notebook regressions. Benchmark and codemod tests also pass on
Python 3.11; the full 100,000-row benchmark executes successfully. A dedicated
pytest collection exclusion keeps the root t-string notebook out of ordinary
test-module imports on older Python, without excluding it from notebook tests.
The earlier engine-deletion and installed-artifact counts above describe
their original checkpoints, before these additional tests.

Full post-migration package and repository release suites also pass:

| Source environment | Result |
| --- | --- |
| Python 3.11 | 9,140 passed, 102 skipped |
| Python 3.14 | 9,314 passed, 20 skipped |

The additional Python 3.11 skips are the 24 new notebook-runtime regression
cases requiring Python 3.14 t-strings. Both runs retain the existing matrix
complex-to-real casting warning. No runtime algorithm or coverage exclusion
was changed by this teaching-file migration.

## Rotor predicate follow-up

The high-dimensional `is_rotor` decision is resolved: the predicate now
requires native vector preservation as well as evenness and a full unit
reverse product. `rotor_generator` rejects the same unit even nonrotors,
while the mathematical `log` accepts their principal algebra logarithms.
General exponentiation and sandwich multiplication are unchanged. Regression
coverage includes singular and non-orthogonal metrics, valid higher-grade
compound rotors, and explicit floating-point tolerances. See
[ADR-124](../adrs/124-rotor-predicate-requires-vector-preservation.md).

Post-fix full suites pass with 9,227 tests (102 skipped) on Python 3.11
and 9,401 tests (20 skipped) on Python 3.14, including the extended rotor
notebook. Focused tests cover every statement and branch of `is_rotor`.
The subsequent logarithm/generator split is specified in
[ADR-125](../adrs/125-separate-algebra-logarithms-from-rotor-generators.md).
`log` now implements the real principal algebra logarithm, and
`rotor_generator` separately validates geometric use. Automatic alternative
generator-branch selection remains outside the current implementation.

The logarithm/generator checkpoint passes 9,330 tests (102 skipped) on
Python 3.11 and 9,504 tests (20 skipped) on Python 3.14. Its new numerical
functions have full statement/branch coverage in the 376 focused cases.
Fresh wheel and sdist checks verify all 33 source-identical runtime files;
an installed-wheel process exercises the new APIs independently of source
imports. These results supersede the earlier predicate-only test counts
for the current working tree, without implying a release or publication.

## Type-check follow-up

The eleven remaining type errors are resolved by
[ADR-126](../adrs/126-align-static-types-with-existing-numeric-contracts.md).
The configured production check reports **zero errors**, with the same
seventeen warnings. No ignores, exclusions, relaxed checks, or dependencies
were added. The fixes preserve numeric and rendering behavior, with 52 new
regression cases; all 264 focused cases pass. The earlier type counts above
are historical checkpoints, not the current result.

Full package and release-workflow suites now pass with 9,382 tests (103
skipped) on Python 3.11 and 9,557 tests (20 skipped) on Python 3.14,
including headless notebooks. Both retain only the existing matrix
complex-to-real conversion warning. This is source validation, not a fresh
release-artifact or publication checkpoint.

## Pre-a3 validation and integration checkpoint

Date: 2026-09-10. Validated source commit: `8805253`. This prepares the next
`2.0.0a3` release; it does not bump versions or publish packages. The fresh
public-package artifacts still carry the committed `2.0.0a2` metadata and
must not be uploaded as replacements for the already published alpha.

| Check | Result |
| --- | --- |
| Full source and release-workflow suite, Python 3.11.15 | 9,383 passed, 114 skipped |
| Full source and release-workflow suite, Python 3.14.4 | 9,569 passed, 20 skipped |
| Fresh installed wheels, Python 3.11.15 | 9,229 package tests passed, 114 skipped; 43 loaded package-module origins verified |
| Fresh installed wheels, Python 3.14.4 | 9,415 package tests passed, 20 skipped; 46 loaded package-module origins verified |
| Maintained gallery | All 85 notebooks pass dependency validation and headless execution |
| Clean integration-worktree gallery and logarithm regressions | 30 passed, including all 85 notebook exports |
| Galaga production coverage, Python 3.11 | 94.83% combined line/branch; direct core 98.48% |
| Marimo companion coverage, Python 3.14 | 95 focused tests passed; 86% combined line/branch |
| Production type check | Zero errors; 17 existing warnings |
| Wheels and sdists | All five repository packages built; all ten artifacts passed Twine |
| Galaga artifact inventory | Wheel and sdist each contain 33 source-identical, legacy-free runtime files |
| Declared-dependency-only core smoke tests | Pass on Python 3.11 and 3.14, with isolated site-packages imports |
| Installed dependency consistency | Pass in both fresh environments |
| Ruff, configured Python formatting, Shellcheck, Checkmake, Bandit | Pass; existing Bandit annotation warnings remain |
| Dependency vulnerability audit | No known vulnerabilities found in the audited source environment |
| Lockfile consistency | Pass; no dependency or version changes |
| Configured release Markdown lint | Pass for all 33 files |
| Branch-change Markdown lint | Pass for all 94 changed documents |
| Tracked local documentation file links | All 828 resolve; no broken targets on the pre-integration baseline either |
| Historical rendering parity | All 73 cases match the accepted ledger, including its ten intentional differences |

The installed package suites exclude the 154 repository release-workflow
tests already exercised by the source runs. All four full runs retain the
existing matrix complex-to-real conversion warning. Older-Python notebook
skips are explicit; the Python 3.14 runs execute the notebook runtime tests.
No coverage exclusions or production algorithms changed during validation.

Both fresh environments initially contained only the new Galaga wheel and
its declared NumPy dependency. Core-only smoke tests checked general-Gram and
native-null products, logarithms, generator predicates, equality/hashing,
and absence of retired imports before installing any test tools. The full
package runs then used installed companion wheels, never runtime source
directories; development-only test helpers remained separate. NumPy resolved
to 2.4.6 on Python 3.11 and 2.5.3 on Python 3.14. The experimental Mermaid
package was also built and tested, but remains outside joint publication.

Artifacts, coverage data, installed-test XML reports and benchmark output
are retained under `/tmp/galaga-a3-validation.F55xCA`. The fresh benchmark
measures direct-core product at 16.444 microseconds versus 16.947 in the
accepted baseline, and reverse at 1.910 versus 1.836. These are local
microbenchmark observations, not a cross-machine performance threshold;
the archived baseline is unchanged.

A broader Markdown scan reports 324 findings in 30 older documents,
including `AGENTS.md`. Every affected document is byte-identical to the
pre-integration `origin/galaga_v2` baseline; none belongs to the 94 changed
documents. This is existing documentation-formatting debt, not a globally
clean Markdown result.

The fetched `origin/galaga_v2` was an ancestor of the validated commit, with
38 feature commits to integrate and no remote-only commits. Integration
uses a separate clean worktree to exclude a concurrent uncommitted edit to
`examples/matrix/general_gram_compact_foundations.py`. The committed gallery
was revalidated there after the fast-forward. User work remains untouched.

GitHub reports no Actions workflows, check runs or external commit statuses.
The user explicitly chose **no CI** for this alpha preparation. This is a
local source-and-artifact validation checkpoint, not a CI pass or completion
of every stable-2.0 gate. See the follow-up in
[ADR-122](../adrs/122-remove-the-legacy-engine-and-verify-artifacts.md).

## Post-a4 API retirement checkpoint

Date: 2026-09-11. The working tree completes W9.2 under
[ADR-130](../adrs/130-retire-migration-only-api-adapters.md), without changing
the committed `2.0.0a4` version or publishing replacement artifacts.

| Check | Result |
|---|---|
| Full package and release-workflow suite, Python 3.11.15 | 9,578 passed, 169 skipped |
| Full package and release-workflow suite, Python 3.14.4 | 9,819 passed, 20 skipped |
| Wheel and sdist runtime validation | 31 source-identical files in each; bridge root and descendants rejected |
| Isolated installed-wheel checks, Python 3.11 and 3.14 | Site-packages origins verified; retired imports/exports absent; canonical operations and retained aliases pass |
| Twine metadata/README checks | Both artifacts pass |
| Ruff and configured Python formatting | Pass |
| Production type check | Zero errors; 18 warnings |
| Changed Markdown and whitespace checks | Pass |

The full runs exercise source with an installed editable Galaga distribution;
the separate wheel checks use isolated Python processes without repository
paths. These are API-cleanup checks, not a rerun of every companion's complete
installed-wheel suite, coverage comparison or security/release gate.
Temporary artifacts remain under `/tmp/galaga-api-cleanup.6q0oBy/artifacts`
and must not be uploaded over the already published alpha. The bridge's
bytecode-only remainder was moved to `/tmp/galaga-retired-bridge.rNZzsO` so
the source directory cannot survive as an importable namespace package.
Deleted tracked adapter sources remain recoverable from Git.

## Post-a4 stable-release preparation checkpoint

Date: 2026-09-11. Base commit: `22e9db2` on `galaga_v2`, plus the uncommitted
lint-gate fix, README regression tests and release-documentation changes in
this checkpoint. This completes the requested local preparation checks, not
the clean release-candidate or publication gate. No versions, classifiers,
dependency floors, lockfile or changelog were changed; no CI was added.
The stable local-only validation policy is now explicit in
[ADR-131](../adrs/131-local-only-stable-release-validation.md).

| Check | Result |
|---|---|
| Full source package and release-workflow suite, Python 3.11.15 | 9,601 passed, 170 skipped |
| Full source package and release-workflow suite, Python 3.14.4 | 9,843 passed, 20 skipped |
| Full installed-wheel package and release-workflow suite, Python 3.11.15 | 9,601 passed, 170 skipped; 41 loaded runtime module origins verified |
| Full installed-wheel package and release-workflow suite, Python 3.14.4 | 9,843 passed, 20 skipped; 44 loaded runtime module origins verified |
| Maintained gallery | All 88 notebooks pass dependency validation and headless execution |
| README examples | Core and all four companion READMEs execute; Marimo examples require Python 3.14 |
| Lint-gate regressions | 16 tests cover every failing stage and successful normal/fix runs |
| `make lint` and `make validate` | Pass, including dependency audit and production type checking |
| Production type check | Zero errors; 18 non-error warnings remain |
| Ruff, Python formatting, Shellcheck, Checkmake and Markdown lint | Pass |
| Bandit | No issues; existing annotation warnings remain |
| Wheels and source distributions | All five packages built; all ten artifacts pass Twine |
| Core artifact inventory | Wheel and sdist each contain 31 source-identical runtime files; retired paths absent |
| Declared-dependency-only core smoke | Pass on Python 3.11 and 3.14 before installing companions/test tools |
| Installed dependency consistency | Both wheel environments pass |
| Dependency vulnerability audit | Source environment and both wheel environments report no known vulnerabilities |
| Lockfile consistency | Pass; lockfile unchanged |
| Local Markdown file targets | No missing targets; headings and external HTTP availability are not part of this check |
| Historical rendering audit | 73 cases checked; zero reviewed-v2 regressions; ten already-reviewed differences from v1 |

The first installed Python 3.14 run failed only because the sandbox blocked
Marimo's local kernel sockets. The complete suite was rerun outside that
sandbox and passed; the successful numbers above are from that rerun.
Both installed environments load Galaga and its companions from site-packages,
not editable runtime trees. The runner exposes only repository test helpers
and verifies runtime module origins before and after the suite. Notebook
subprocesses derive their package paths from those installed modules.

The dependency audit cannot look up `galaga-mermaid==0.2.0` because this
experimental local project is absent from PyPI. That explicit exception is
not a vulnerability waiver: its code is scanned by Bandit and its third-party
dependencies are audited. Audit cache-deserialization warnings caused stale
cache entries to be ignored; the online audits completed successfully.

### Coverage review

| Scope | Previous pre-a3 checkpoint | This checkpoint |
|---|---:|---:|
| Galaga production, combined line/branch | 94.83% | 94.85% |
| Direct numeric core, combined line/branch | 98.48% | 98.48% |
| Marimo companion, combined line/branch | 86% | 86% |

Galaga production line coverage is 96.07%; branch coverage is 91.37%.
The comparison filters the older combined report to `packages/galaga/galaga/`
so development helpers and companion code do not distort the baseline.
Marimo's separate Python 3.14 run passes all 95 focused tests.

No coverage exclusions were added during this preparation. Relative to the
older pre-a3 checkpoint, the production exclusion count is 72 rather than 69:
the existing presets work added a type-only import line and a two-line
defensive `with_blades` guard. The protocol stub moved into the private preset
implementation without increasing that count. These are not hidden engine
remnants. Lower-coverage presentation/catalog and model validation paths
remain future coverage opportunities; no runtime code changed in this work.

### Performance review

Python 3.11.15, NumPy 2.4.6, macOS 26.6.2, seed `20260721`; median of seven
repeats of 2,000 calls. Each path is checked against the independent numeric
reference before timing. The archived Phase 8 baseline remains unchanged.

| Operation / layer | Phase 8 median µs | Current median µs |
|---|---:|---:|
| Geometric product / direct core | 16.947 | 16.268 |
| Geometric product / untracked facade | 18.518 | 17.715 |
| Geometric product / tracked facade | 20.576 | 19.765 |
| Reverse / direct core | 1.836 | 1.884 |
| Reverse / untracked facade | 2.574 | 2.582 |
| Reverse / tracked facade | 6.832 | 6.676 |

There is no material regression in this local comparison. The small reverse
variation is not evidence of a new slowdown; host/OS and timing noise prevent
treating these microsecond measurements as a cross-machine threshold.

### Reproduction and artifact boundary

Temporary artifacts, the installed-suite runner, JUnit reports, coverage JSON
and raw benchmark/rendering reports are retained in
`/tmp/galaga-stable-gate.xI4eiC`. The four public projects still carry
`2.0.0a4`; these are validation artifacts and must not replace published alpha
files. Mermaid retains its independent `0.2.0` metadata.

Source suites used explicit Python 3.11 and 3.14 isolated `uv run --no-project`
environments with an editable Galaga distribution for metadata and repository
runtime paths. The installed suites instead use fresh `uv venv` environments,
explicit local wheels, `python -I`, and Pytest's `--import-mode=importlib`.
Key commands, with `GATE` set to the temporary directory above:

```shell
"$GATE/py311/bin/python" -I "$GATE/installed_gate.py" tests
"$GATE/py314/bin/python" -I "$GATE/installed_gate.py" tests
uv pip check --python "$GATE/py311/bin/python"
uv pip check --python "$GATE/py314/bin/python"
"$GATE/py311/bin/python" -m pip_audit
"$GATE/py314/bin/python" -m pip_audit
uvx twine check "$GATE"/artifacts/*
uv run python scripts/check_galaga_artifact.py --project packages/galaga \
  "$GATE"/artifacts/galaga-*
PYTHONPATH="$GATE/test-support" "$GATE/py311/bin/python" \
  -m tools.benchmark_phase8 --output "$GATE/performance.md"
```

`make validate` also passed with `UV_PROJECT_ENVIRONMENT` pointing to a
separate temporary project environment and all companion source roots on
`PYTHONPATH`. Its existing Makefile recipes select Python 3.13, 3.11 and 3.14
for different steps; this does not replace the explicit full 3.11/3.14 suites
above. The user's Python 3.13 `.venv` was preserved.

## Remaining release actions

- API retirement is complete after `2.0.0a4` under
  [ADR-130](../adrs/130-retire-migration-only-api-adapters.md): `gram_bridge`,
  the six temporary function spellings and unused adapter infrastructure are
  removed. Earlier checkpoints above correctly describe their then-live state.
- Review and commit this preparation, then validate the intended clean,
  tracked candidate. Merge to `main` only when explicitly authorized.
- Use the now-documented local gate for stable as well as prereleases;
  no CI setup is outstanding. Keep the zero-error type check green.
- At the actual beta/RC/final release, select the version and update the
  stage-specific classifiers and README installation guidance. The release
  script does not do those wording/classifier edits automatically. Follow the
  exact checklist in the release process; only then edit the changelog and
  synchronize package versions/dependency floors through the release workflow.
- Install and review the published release candidate before approving stable
  `2.0.0`. Publication, credentials, tags and a clean release commit are not
  certified by this working-tree checkpoint.

Concurrent edits mentioned in earlier checkpoints were preserved separately
from the engine-removal changes; the post-a4 preparation checkpoint above
records the current validation boundary.

See [ADR-122](../adrs/122-remove-the-legacy-engine-and-verify-artifacts.md),
the [cutover plan](core-cutover-plan.md#w93-run-the-release-gate), and the
[release process](../RELEASE_PROCESS.md).
