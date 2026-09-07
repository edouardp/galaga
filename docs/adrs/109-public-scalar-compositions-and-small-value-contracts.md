---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-109: Public Scalar Compositions and Small-Value Contracts

## Context and problem statement

`test_scalar_helpers.py` still exercises the legacy fraction/constant members,
mutable scientific-notation styles, and private LaTeX builders. Its 51 cases
pass before migration, but the three tiny-constant/product checks also accept
zero because `np.isclose` uses a nonzero default absolute tolerance.

Compute the current behavior before changing tests: the facade stores those
tiny floats unchanged. The default `DisplayPolicy.zero_tolerance=1e-12` hides
them in value rendering, not in storage or exact equality. Literal scalar
division is float arithmetic and can simplify to a decimal. Naming does not
enable tracking, supply units, or derive a physical constant.

## Decision outcome

Retain all 51 historical method identities using explicit public scalar
construction, division, naming, `scalar_sqrt`, immutable display policy and
semantic render nodes. Fix the vacuous tests, not the existing numeric/display
policies. No production package API or algorithm changes.

The [archive](../../packages/galaga/tools/baselines/scalar-helpers-v1.json)
was captured at `83a89f4` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2.
It retains the complete test source and SHA-256 digest, all 51 identities,
six fraction observations, seven constants, four compositions, eight private
scientific-node observations, six coefficient-node observations, three notation
styles and the zero-denominator error.

### Preserve the existing v2 boundaries

- `Algebra.fraction`, `frac` and constant properties remain absent, following
  the public surface ledger and helper policy. Use `algebra.scalar(p) / q`
  and explicit supplied scalar values with `.named(...)` as appropriate.
- Division by zero raises the public `ZeroDivisionError`, not the retired
  fraction constructor's `ValueError`. Both signed zeros are rejected.
- A scalar division's stored coefficients are floating-point values.
  `expr=True` retains provenance; render-time structural simplification may
  fold literal arithmetic. `galaga.rendering.tree.Fraction` is a semantic
  layout node, distinct from Python's `fractions.Fraction` and not an exact
  rational numeric backend.
- A named numerator in a tracked division becomes a symbol operand.
  Explicit replay needs its environment. Changing that environment changes
  the replayed result, not the original stored coefficients.
- Use `scalar_sqrt(algebra.scalar(2, expr=True))` for the square-root
  expression. Late v1 already used a real square-root node for `sqrt2`;
  the earlier wording in [ADR-051](051-scalar-constants.md) predates that
  implementation. Preserve the observed expression, not an invented name.
- Historical supplied `hbar` is a rounded input. Its value is not exactly the
  floating-point quotient of the supplied `h` by `2*pi`. Keep the observation
  as evidence without introducing a physical-constants catalogue or silently
  changing the input. Applications own their domain values and units.
- Small-value rendering requires an explicit `zero_tolerance=0` when every
  stored coefficient should be visible. Filtering a coefficient does not make
  it equal to zero or change its hash. A tolerance-filtered teaching equality
  must not be interpreted as exact numeric equality.
- Scientific LaTeX uses `\times`; ASCII and Unicode use general-format
  scientific strings. Legacy `cdot`/`raw` LaTeX selectors stay retired.
  `coefficient_precision` specifies significant digits, not decimal places
  or trailing-zero padding. Use Python formatting after `float(value)` when
  fixed numeric formatting is required.

These follow [ADR-097](097-concrete-display-contracts-outlive-legacy-rendering.md),
[ADR-101](101-immutable-notation-contracts-and-unit-fraction-layout.md), and
the [exact equality policy](095-exact-numeric-equality-and-compatible-hashes.md).

### Add independent numeric and deletion evidence

Replay every archived numeric observation with zero absolute tolerance.
Compare fraction arithmetic to Python rational values converted to floats,
rotor coefficients to sine/cosine after computing the plane square, and
scientific output to an independent numeric parser. Explicit literal/name
replay, both tracking modes and all three targets remain checked.

Probe both sides of the display threshold, positive/negative subnormals,
negative unit mantissas, signed-zero denominators, and tiny mixed-grade values
in oblique-indefinite and degenerate metrics. Exact storage/equality/hash tests
are separate from display-precision assertions. Corruption probes reject
malformed/nonfinite archive data, erased tiny values and changed magnitudes.
The original `np.isclose(0, tiny)` weakness is explicitly demonstrated before
requiring the new assertion to reject zero.

The existing eager-values notebook teaches these boundaries with an executed
small-value example and literal versus named thirds. Its runtime test checks
the actual coefficients, replay and generated math output. Python 3.11 skips
that t-string notebook execution; the numeric contracts still run.

## Consequences

All 273 focused cases pass on Python 3.14 with 100% line and branch coverage
in their three files. Both public suites pass all 260 cases directly from the
built wheel, with package origins verified and legacy imports blocked.
Full package/release suites pass 6,695 cases (61 skipped) on Python 3.11 and
6,828 (20 skipped) on Python 3.14, including maintained notebook exports.
Core/facade coverage remains unchanged; the negative-unit scientific test
raises emitter coverage from 95% to 96%. The existing matrix warning and
295-error type-check baseline remain.

The construction-exemption ledger falls from four files to three:
`test_coverage.py`, `test_coverage_gaps.py` and `test_redesign.py`.
Their mixed contracts, namespace/construction guards, engine deletion and
final release gates remain pending. This completes one dependency-retirement
unit, not the release.
