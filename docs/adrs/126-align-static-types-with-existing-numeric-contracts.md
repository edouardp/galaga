---
status: accepted
date: 2026-09-09
deciders: edouard
---

# ADR-126: Align Static Types with Existing Numeric Contracts

## Context and problem statement

After [ADR-125](125-separate-algebra-logarithms-from-rotor-generators.md),
the configured production type check retained eleven errors. They came
from real-number annotations, unbounded keyword forwarding, reuse of a
rendering variable across incompatible types, and operator return inference.
The affected runtime operations already passed their numeric contracts.

## Decision outcome

- Extend the facade scalar factory, RGA point weight, and its private
  validator annotations to `Real | float`, matching the core scalar factory.
  Built-in floats and integers remain accepted, as do supported `Real`
  implementations such as `Fraction` and NumPy real scalars. Keep the existing
  runtime validation: do not broaden acceptance to arbitrary float-convertible
  objects. RGA weights still reject booleans and nonfinite values.
- Describe the private CGA role-projection keyword parameters with a
  `TypedDict` and `Unpack`. Only the existing `origin` and `infinity` selectors
  are forwarded. This distinguishes replay parameters from `_semantic`'s
  separate tracking and expanded-expression controls, without changing calls,
  expression IDs, stored parameters, or replay behavior.
- Give product-factor strings their own local rendering variable, separate
  from the sum-term list. Preserve all target-specific grouping and output.
- Construct `outerexp`'s final result from the scaled sum of the even/odd
  coefficient arrays. This performs the same addition then scalar
  multiplication and returns an owned, immutable multivector explicitly.
  Do not weaken the arithmetic operators' `NotImplemented` annotations,
  insert a cast, or add an unnecessary geometric product to resolve inference.

Keep the configured type-check scope and severity unchanged. Add no `Any`,
type ignores, exclusions, or dependencies. The seventeen existing warnings
remain separately visible: dynamic export analysis, a redundant cast, and
explicit conversions. Removing conversions merely to suppress warnings is
outside this change, particularly at Python/NumPy scalar boundaries.

## Consequences and verification

The public mathematical domains, storage, expression behavior, and rendering
are unchanged. No package version or changelog update belongs to this task.

Regression tests cover supported and rejected scalar/weight types, CGA role
selection and changed-binding replay in both expression forms, nested
sum/product rendering in all targets, and mixed-grade outer exponentials
including subnormal and zero-underflow results in different metrics.

The configured `pyrefly check` reports zero errors and seventeen warnings,
also when explicitly targeting Python 3.11 or 3.14. All 264 focused tests
pass, including 52 new regression cases. Full package and release-workflow
suites pass with 9,382 tests (103 skipped) on Python 3.11 and 9,557 tests
(20 skipped) on Python 3.14, including headless notebook execution. Both
runs retain only the existing matrix complex-to-real conversion warning.
Changed-file Ruff, formatting, Markdown lint, and whitespace checks pass.

The type check must continue to pass for subsequent release candidates;
these source checks do not replace fresh release-artifact validation.
