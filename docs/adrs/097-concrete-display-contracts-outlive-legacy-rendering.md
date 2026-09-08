---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-097: Concrete Display Contracts Outlive Legacy Rendering

## Context and problem statement

The remaining display-order and numeric-formatting suites still constructed
v1 values and inspected private presentation state. Their 25 tests covered
useful behavior, but also encoded old defaults and protocols that differ from
the implemented v2 presentation model. Simply changing imports would either
lose coverage or accidentally reinstate those old contracts.

Before migration, both suites passed against the old engine. Direct algebra
checks established the quaternion unit coefficients and Hamilton products,
the half-turn rotor result, and both implementations' actual rendering and
basis enumeration. V2 already uses native-mask factories, separate immutable
display order, semantic format selectors, and significant-digit precision.

## Decision outcome

Retain the observed v1 behavior in a development-only
[concrete-display archive](../../packages/galaga/tools/baselines/concrete-display-v1.json),
captured at `c05d800d4df4b92b7141d6c990a190721cce84c1` with Python 3.14.4
and NumPy 2.5.2. It contains eleven concrete samples with coefficients and
ASCII, Unicode, LaTeX, and repr outputs; six fixed-decimal format observations;
three algebra repr observations; resolved default and quaternion orders;
quaternion basis values for every grade; and seven quaternion products.

The two suites now use the public facade. Preserve and strengthen permutation
validation, exact term order and signs in every target, native coefficient
storage, basis values, products, semantic format hooks, precision control,
and near-unit coefficient elision. Tests also cover scoped order changes in
Euclidean, degenerate, oblique, and native-null metrics without changing
coefficients, provenance, equality, or hashes.

The following distinctions are explicit rather than presented as v1 parity:

| Concern | Captured v1 behavior | Existing v2 contract |
|---|---|---|
| Default concrete order | Grade-sorted | Native bitmask order; grade order can be selected explicitly |
| Quaternion basis enumeration | Display-ordered `i, j, k` | Native masks give `k, j, i`; named roles select semantic units |
| Coefficient formatting | Numeric specs such as `.3f` | Significant digits through `DisplayPolicy`; format specs select content/target |
| Multivector repr | Unicode by default | ASCII; `str` remains Unicode by default |
| Algebra repr | `Cl(p,q,r)` summary | Diagnostic numeric-owner wrapper, not a stable serialization |

In particular, significant digits do not provide fixed decimal places or
trailing-zero padding. V2 currently rejects numeric multivector format specs;
this is a compatibility limitation, not equivalent support under a new name.
Adding fixed-decimal formatting or a compact algebra repr would be separate
production work, not a prerequisite for removing these tests' live v1 imports.

Current sample values are computed from public operations, not reconstructed
from archived coefficients. Numeric comparisons require matching shapes,
finite data, and `rtol=0, atol=1e-12`. All three visible targets then match
the archive, with the old grade order selected explicitly where necessary.
Quaternion products also match independent public core left actions. Legacy
repr and fixed-decimal observations remain explicitly recorded; they are not
used as expected v2 renderings.

Fresh-process tests run both complete suites with legacy imports forbidden.
Both files leave the constructor-exemption ledger. Mutation tests demonstrate
rejection of incorrect rotor results or renderings even if the other aspect
still agrees; malformed shapes, nonfinite values, and genuine coefficient
drift cannot pass as numerical agreement.

## Consequences and boundaries

[ADR-110](110-public-factory-and-display-edge-contracts.md) carries the later
factory/display edge suite onto the same public contracts. It explicitly
preserves rendered-string snapshots, target-specific hooks, wrapping/content
independence and the retired factory-flag boundary, without production changes.

- Good, because the two suites no longer keep the old engine alive while
  their numerical and presentation responsibilities remain tested.
- Good, because existing public v2 contracts and compatibility limitations
  become explicit in the migration guide and historical specification.
- Boundary, because this refines the test migration under
  [ADR-076](076-immutable-presentation-configuration.md) and
  [ADR-078](078-shared-semantic-rendering-pipeline.md), not production
  arithmetic, rendering, presets, or public API behavior.
- Boundary, because [ADR-059](059-display-ordering.md) and SPEC-011 describe
  the older presentation-coupled enumeration; v2 keeps enumeration native.
- Pending, because seventeen files still require legacy numeric construction.
  Other symbol, notation, expression, namespace, and engine-deletion work
  remains separate. This is not completion of the stable-release gates.
