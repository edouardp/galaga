---
status: accepted
date: 2026-10-03
deciders: edouard
---

# ADR-170: Retire Migration Scaffolding Before Stable Galaga 2

## Context

The Galaga 1 to 2 migration is complete and the first 2.0 beta is published.
The repository still contains one-time codemods, historical test-ownership
ledgers, and compatibility spellings created during that migration. The Marimo
notebooks are editable examples rather than stable test fixtures for every
lesson detail.

## Decision

Remove the prefixed complete-preset factory spellings (`p_cga`, `p_sta`, and
their peers). `galaga.presets` exposes the concise factory names, and the
factory implementations use those names directly. Keep the inspectable preset
classes as configuration types.

Remove the redundant matrix spellings `to_spinor_matrix`,
`from_spinor_matrix`, and `QuatMatrixRepr`. The supported column conversions
are `to_spinor_column` and `from_spinor_column`; quaternion matrices use
`MatrixRepr` with quaternion mode.

Retire completed source-rewrite tools and their tests. Historical source
ownership assertions may be removed once their live public contracts have
independent tests. Keep numeric, presentation, rendering, import-boundary, and
artifact checks that protect current behavior. Frozen observations may remain
as development evidence where they check current output.

Treat notebooks as human-editable examples. Discover them from the gallery
instead of maintaining a migration ledger. Keep a small smoke gate for Python
compilation, Marimo dependency validation, and headless execution. Do not
assert specific lesson text, cell layout, or source patterns in unit tests.
The local editable-package Marimo launcher remains the development entry point.
Move older, unported Galaga 1 examples under `examples/legacy`; they remain
editable in the gallery but are outside the Galaga 2 execution gate.
Retire ADRs that prescribe the contents of particular lessons; notebook content
belongs with the editable notebook itself. Keep ADRs for library behavior and
repository-wide development policy.

## Consequences

The stable API has one spelling for each complete preset and spinor-column
conversion. Removing beta-era aliases is an intentional API change before the
release candidate. The example gallery can evolve without updating a source
assertion suite, while execution failures still surface. Retiring migration
bookkeeping reduces test maintenance without discarding current API contracts.

This decision updates the compatibility portion of ADR-129, the alias portion
of galaga-matrix ADR-005, and the notebook testing policy of ADR-083 and
ADR-090.

## Completion of the cleanup

The completed API disposition manifest, source ownership ledgers, archive
provenance assertions, and mutation tests of migration checks are retired.
Tests of current aliases, numeric domains, protocols, imports, and call shapes
remain ordinary facade and core contracts. The test-wide import hook and
repeated subprocess runs that install a retired-module finder are removed.
The release artifact checker still validates source contents, forbidden
dependencies, runtime files, and distribution metadata.

The remaining operation-name codemod and cutover microbenchmark are retired,
along with their tests. LibCST is removed from the development dependencies.
Historical timing reports remain records of their original environment;
they do not prescribe a current benchmark command.

The differential rendering auditor and accepted-difference ledger are replaced
by ordinary snapshot tests. All 73 expression recipes retain their reviewed
expression, value, full-display, rich-display, and coefficient expectations.
The new fixture contains current expectations rather than a pair of engines.
Independent coefficient, basis transport, quaternion, and configured-rendering
tests remain. Unused ownership and source-capture archives are removed; their
historical versions are available through Git.

Configured rendering contexts also drop the implementation selector and the
cutover prefix in configuration names. Names identify the algebra and display
profile, such as `cl3/full-default`; all recipes use the public facade.

This completes retirement of the tools established by ADR-092, ADR-093,
ADR-096, and ADR-121. Their mathematical and architectural runtime contracts
continue to be covered without requiring their migration bookkeeping.
