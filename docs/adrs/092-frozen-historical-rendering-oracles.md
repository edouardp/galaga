---
status: accepted
date: 2026-09-06
deciders: edouard
---

# ADR-092: Frozen Historical Rendering Oracles

## Context and problem statement

Phase 9 removes the temporary Galaga 1 engine retained by
[ADR-085](085-top-level-api-is-the-facade-with-explicit-legacy-oracle.md).
The rendering parity audit still executes that engine, even though its
73 cases already have reviewed outcomes. Deleting the audit with the engine
would discard useful semantic and rendering coverage.

The audit also has a regression gap: it checks that the set of differing case
IDs matches the accepted ledger. An already-accepted case can change its
output again, or start failing in the facade, without changing that set.

## Decision outcome

Preserve the old observations as versioned development-only JSON data captured
before retiring the live adapter. Record the source commit, Python and NumPy
versions, shared operation inventory, stable case metadata, exact output
channels, coefficients, and legacy errors. Validate the capture against the
original audit at its recorded commit.

Run the existing recipes only through the current facade. Keep the historical
v1/v2 difference ledger, and independently compare each facade output with its
reviewed v2 reference. A ledger entry is not a blanket exception for future
changes to that case. Reports must not pre-approve regressed output.

Text comparison remains exact. Numeric comparison retains the existing
`rtol=1e-12, atol=1e-12` tolerance and requires matching coefficient lengths.
This test policy is separate from public multivector equality and hashing.

The CLI check and tests enforce complete case and shared-operation inventories.
A fresh-process test blocks legacy imports while running the entire audit.
The parity test file leaves the legacy-construction allowlist.

Historical v1 data is immutable evidence. Updating a reviewed v2 observation
requires an explicit review and regression test, not automatic snapshot
acceptance. New v2-only capabilities use dedicated tests or the exact
configured rendering contracts instead of invented historical outputs.

## Scope and consequences

This decision originally superseded the live legacy-adapter requirement for
the rendering parity audit only. The benchmark has since retired its v1 path
under [ADR-093](093-benchmarks-use-core-reference-oracles.md), and the exact
configured suites preserve their observations under
[ADR-084](084-exact-configured-rendering-contracts.md). Other legacy tests
remain until their coverage has been preserved. No production engine file or
public alias is removed by these checkpoints, and Phase 9 is not yet complete.

- Good, because historical behavior survives independently of legacy code.
- Good, because reviewed differences can no longer conceal new regressions.
- Good, because the same case registry drives tests and the review report.
- Cost, because deliberate rendering changes require explicit reference-data
  review as well as ordinary implementation tests.
- Cost, because historical snapshots describe specific old behavior; they are
  not independent proofs of the underlying algebra. Direct-core identity tests
  remain the mathematical oracle.
