---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-009: Build Metric Extensions from Ordinary and Complementary Minors

## Context and problem statement

Eric Lengyel's metric and antimetric operations act on the full exterior
algebra. For a diagonal signature, these maps look like products of present or
absent basis squares. A native nonorthogonal Gram matrix requires the true
exterior extension: grade blocks contain determinants of minors.

For a nonsingular metric, the antimetric can be written using an inverse. That
formula is unusable in PGA, where complementary-minor operations are among the
main reasons to expose the antimetric.

## Decision drivers

- Generalize diagonal metric/RGA operations to native Gram bases.
- Preserve meaningful antimetric operations for singular metrics.
- Avoid a pseudoinverse and its tolerance-dependent semantics.
- Keep derived full-algebra matrices lazy and immutable.

## Considered options

1. Support metric extensions only for diagonal signatures.
2. Build the metric compound matrix and derive the antimetric through inverse
   or pseudoinverse.
3. Build both maps directly from ordinary and signed complementary minors.

## Decision outcome

Construct `extended_metric_matrix()` grade by grade from minors of the vector
Gram matrix. Construct `metric_antiexomorphism_matrix()` from signed minors of
the complementary row and column sets.

Use direct products of present or absent diagonal entries as an equivalent
fast path for diagonal metrics. Cache both dense matrices lazily and return
them read-only.

The antidot product is pseudoscalar-valued, and Hodge/weight duals compose the
appropriate metric map with explicit left or right complements.

## Consequences

- Good, because oblique exterior pairings use the correct Gram determinants.
- Good, because antimetric and weight operations remain defined in PGA.
- Good, because no reciprocal null vector or pseudoinverse is manufactured.
- Cost, because each full exterior matrix requires quadratic space in `dim`.
- Future, because larger dimensions need an allocation guard or operator form
  that avoids materializing the dense matrices.
