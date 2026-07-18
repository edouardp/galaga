---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-011: Evaluate Numeric Functions with Explicit Real Branches

## Context and problem statement

Adding square roots, exponentials, logarithms, and outer power series to a
real Clifford algebra requires more than porting names. A fixed unscaled
Taylor loop is unreliable for a general multivector. A rotor logarithm must
distinguish elliptic, hyperbolic, and null generators. An exterior power series
terminates for positive-grade elements but not for a nonzero scalar part.

The implementation must work in native nonorthogonal and degenerate Gram
bases without introducing a second product engine or silently complexifying
coefficients.

## Decision drivers

- Reuse the backend-neutral geometric and exterior products.
- Preserve tiny nonzero generators.
- Handle all three signs of a scalar generator square.
- Make unsupported real branches fail explicitly.
- Avoid truncating the non-nilpotent scalar part of an outer series.
- Provide independent identities for testing each algorithm.

## Considered options

1. Port fixed-length Taylor series and permissive branch formulas directly.
2. Delegate every function to a dense matrix-function dependency.
3. Use scalar-square closed forms, a scaled general series, explicit
   Study-number branches, and a factored exterior series.

## Decision outcome

For `exp(X)`, use the scalar exponential for pure scalars and trigonometric,
null, or hyperbolic closed forms whenever `X*X` is scalar. For a general input,
use the infinity norm of `Algebra.left_action(X)` to select a binary scale,
evaluate the geometric Taylor series at that scale, and restore it by repeated
squaring. Failure to converge or a nonfinite action raises.

For `sqrt(a + N)`, require `N*N` to be scalar, select the principal real Study
branch, and verify the candidate by squaring it. For `log(a + N)`, first
require a normalized rotor and scalar `N*N`, then select the elliptic,
hyperbolic, or null formula. In particular, `log(1 + N) = N` when `N*N == 0`.
A general non-Study rotor, scalar `-1` without a plane, and branches requiring
complex coefficients raise.

For outer functions, split `x = a + X` into scalar and positive-grade parts.
Evaluate scalar dependence analytically and only iterate wedge powers of `X`,
which terminate by dimension. Define outer sine and cosine as the odd- and
even-power parts of the outer exponential, and outer tangent as their quotient
when the outer cosine is invertible.

## Consequences

- Good, because closed forms cover negative-, positive-, and zero-square
  generators without unnecessary series error.
- Good, because general exponentials have convergence control tied to the
  actual left-regular action.
- Good, because native Gram bases use the same products and branch rules.
- Good, because null PGA translators round-trip through exponential and
  logarithm.
- Good, because outer functions remain metric-independent and handle scalar
  components without false finite truncation.
- Cost, because general exponential scaling currently materializes a dense
  left action.
- Cost, because `sqrt` and `log` deliberately reject general multivectors or
  non-Study rotors that need a broader matrix or bivector-factor algorithm.

## Specification

Observable behavior is defined by
[SPEC-005](../specs/SPEC-005-numeric-functions.md).
