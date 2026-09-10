# Pyrefly Type-Checking Status

Pyrefly is a **blocking local validation gate** under
[ADR-131](adrs/131-local-only-stable-release-validation.md):

```bash
uv run pyrefly check
make lint
```

The configured scope is `packages/galaga/galaga/**/*.py`. This is the core
package's production tree, not a claim that every companion, example or test
is statically checked. `scripts/lint.sh` preserves the checker's diagnostics
and exits unsuccessfully on type-check failure; it no longer truncates output
or converts failure to a warning. `make validate` includes that gate.

## Latest recorded checkpoint

The 2026-09-11 [post-a4 validation](v2/legacy-engine-deletion-gate.md#post-a4-stable-release-preparation-checkpoint)
reported **zero errors and 18 non-error warnings**. Counts are observations,
not a permanent test contract; rerun the checker on each candidate.

The July 2026 report of 298 errors described the pre-deletion source tree.
Engine removal eliminated obsolete code; the surviving numeric typing issues
were fixed separately under
[ADR-126](adrs/126-align-static-types-with-existing-numeric-contracts.md).

## Release policy

- Type errors and tool failures block local validation.
- Warnings remain visible in the reported status and are reviewed separately.
- Do not add broad ignores or weaken checks to make the gate green.
- Runtime, artifact and supported-Python tests remain independent requirements.
- The release script does not run every local gate automatically; follow the
  complete [release checklist](RELEASE_PROCESS.md).

No CI workflow is required. The regression tests in
`tests/release/test_lint_gate.py` verify failure propagation through the actual
shell script, including normal and fix modes.
