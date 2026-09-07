---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-094: Numeric Contracts Outlive the Legacy Engine

## Context and problem statement

The shared numeric contract proved the v2 facade during the overlap with v1.
Its seven protocol tests run twice, its four seeded cases compare live
implementations, and its correction ledger constructs old values to show
intentional differences. These tests now prevent retirement of the v1 engine.

Deleting them would discard public protocol coverage and historical evidence.
Merely comparing two current paths could also miss a defect shared by both.
The replacement must preserve the old evidence without declaring v1 behavior
the oracle for intentional v2 corrections or new Gram-native capabilities.

## Decision outcome

The seven protocol tests in `facade/test_numeric_contract.py` now construct
the facade directly, without a version adapter or implementation fixture. They
retain construction, factories, operators, scalar conversion, grades,
products, involutions, dualities, inverse, predicates, norms, and numeric
functions. The separate operation-catalog export gate remains unchanged.

The development-only
[numeric-contract archive](../../packages/galaga/tools/baselines/numeric-contract-v1.json)
preserves all 146 seeded v1 operation results over the original four ordered
diagonal signatures. It records explicit input coefficients as well as seeds,
native exterior coefficient order, operation inventory, tolerances, capture
date, source test and commit, and Python and NumPy versions. Keeping the actual
inputs avoids depending on future random-generator behavior.

The observations were computed before adapter removal at
`fe99fd5d6fddee02af31a9f1278965b2606e7bc0`, using Python 3.14.4 and NumPy 2.5.2.
Both the default facade and forced core `reference` backend were checked
against every result. The maximum absolute residual in either comparison was
approximately $6.7\times10^{-16}$.

Each operation now has an individually named regression case. Both the
current facade and the forced core-reference result must independently match
the historical observation. This also checks that each result retains its
correct algebra owner. Product samples additionally use the reference's public
left action; reverse samples use signs derived from exterior grade. These
checks avoid calling the same public operation as its own oracle.

Seeded comparisons retain `rtol=1e-12, atol=1e-12`, require matching shapes,
and reject nonfinite coefficients. This numerical test tolerance does not
change public exact equality. Corruption tests demonstrate rejection of a bad
facade result, a bad reference result, or the same bad result in both paths;
broadcasting and NaN equality cannot conceal a regression.

The correction ledger retains the observed v1 half-scaled Lie and Jordan
products as data. V2 full and half-scaled outputs are checked against products
derived from public reference left actions, not merely against one another's
aliases. Additional tests deliberately halve both aliases together and require
failure. Old mutable storage, scalar-member presence, and approximate equality
are recorded as observations; live tests assert immutable facade data, absence
of the member, and exact inequality even for representable subnormal vector
perturbations. Singular duality errors have an explicit live test rather than
being silently omitted with the unavailable historical dual results.

The main contract leaves the legacy-construction ledger. A fresh process runs
it in full with legacy imports forbidden. As with the configured-rendering
gate, this process omits the parent conftest because that temporary guard
itself imports v1 to poison its constructors. Normal full-suite runs continue
to use the parent guard.

## Consequences and boundaries

- Good, because public facade coverage and every original seeded comparison
  survive without a running v1 implementation.
- Good, because correlated current-path regressions cannot pass by agreement
  alone, and intentional correction tests have independent expectations.
- Good, because the archive is development evidence, not another shipped
  numeric implementation or an automatically accepted snapshot.
- Limitation, because four historical samples do not prove every algebraic
  identity. Core reference operations still share some definitions with the
  default core; source-derived core tests remain the mathematical authority.
- Boundary, because new v2-only capabilities need their own algebraic tests,
  not invented historical observations.
- Boundary, because this changes test ownership, not production arithmetic,
  equality, or hashing. The independently reproduced hash inconsistency is
  tracked as the next release-blocking correction in the
  [cutover plan](../v2/core-cutover-plan.md#immediate-release-blocker-equalityhash-consistency).
- Pending, because compatibility introspection, other legacy tests, and the
  engine itself still need retirement before the final release.
