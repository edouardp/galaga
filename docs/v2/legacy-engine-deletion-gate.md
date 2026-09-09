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

## Release gate remains open

- Keep the now-passing type check green while completing the remaining
  source and artifact release checks. Seventeen non-error warnings remain.
- Finish the published retirement of `gram_bridge` and six temporary function
  spellings before stable 2.0.
- Obtain CI evidence on the intended tracked branch. This branch has no
  upstream; GitHub reports the committed checkpoint is not present remotely.
  No push or CI configuration change is inferred from local validation.
- At the actual release, choose the version, update the changelog/classifiers
  and installation guidance as appropriate, and verify the required clean
  branch, release-candidate and publication prerequisites. None were changed
  during this verification.

Concurrent user edits to `examples/matrix/cga_via_gram_matrix.py` and
`examples/galaga_v2/presentation_contexts.py` are preserved and are not part
of the engine-removal changes.

See [ADR-122](../adrs/122-remove-the-legacy-engine-and-verify-artifacts.md),
the [cutover plan](core-cutover-plan.md#w93-run-the-release-gate), and the
[release process](../RELEASE_PROCESS.md).
