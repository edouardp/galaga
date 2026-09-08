---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-119: Division Provenance and Exact Scalar Dispatch

## Context and problem statement

Migrating `test_redesign.py` exposed three division defects. The public facade
converted a scalar multivector denominator into a fixed numeric parameter,
losing its name or expression. Thus `hbar / (mass * speed)` could not rebind
the denominator. Both numeric layers also used the tolerant `is_scalar`
predicate to select scalar arithmetic, discarding small stored nonscalar
components. Reflected division formed an inverse first, which could overflow
even when a subnormal scalar divided by itself has the finite answer one.

These are arithmetic/provenance defects, not requests to restore lazy values.
The user approved fixing them within the redesign migration.

## Decision outcome

- Record multivector division as `Call("divide", (numerator, denominator))`.
  Both operand histories survive, including an unnamed product denominator.
  The catalog entry is structural, like `add`: no new public `divide` function.
  Python real-number denominators retain `scalar_divide` with a fixed parameter.
- Evaluate `divide` through core `left / right`. Exact scalar support means
  **every stored nonscalar coefficient is zero**, not below a tolerance.
  The tolerant diagnostic `is_scalar` remains unchanged.
- Direct scalar division avoids constructing a reciprocal. Reflected real
  numerators use an owned scalar value and the same division path.
- For genuinely nonscalar denominators, retain right multiplication by the
  existing checked inverse. This is generally noncommutative; do not move the
  inverse to the left. No inverse solver, conditioning policy, or equality/hash
  semantics change.
- Render the two-operand call as a fraction, with grouped plain-text operands.
  This replaces the earlier v2 product-of-inverse display, while preserving its
  numeric side. Functional notation displays `divide(a, b)`.
- Exact scalar zero divisors raise `ZeroDivisionError`, including reflected
  real/scalar division (previously an inverse `ValueError`). Noninvertible
  nonscalar divisors retain the inverse's `ValueError`.

Replay evaluates the current bindings: a symbol originally bound to a scalar
can later be bound to an invertible vector. It must not inherit a cached
scalar classification or alter the original eager quotient.

## Evidence and verification

Before the fix, 26 of the 46 new core/facade cases failed. All 46 pass after it.
The tests cover diagonal, oblique-indefinite and degenerate Gram matrices,
positive/negative tiny grades, named and literal operands, denominator-only
tracking, subnormals under strict floating-point error handling, zero and
foreign-algebra failures, replay, exact structure and all rendering targets.

For `1 / (1 + epsilon e1)`, derive the reference result from
`(1 - epsilon e1) / (1 - epsilon**2 * G11)`. Comparisons use zero absolute
tolerance so losing the tiny vector term cannot pass. General right-division
cases check the full coefficient array and multiply back by the denominator.
The existing independent reference-action rendering oracle remains in place;
only its reviewed fraction spelling changes.

CGA expanded homogenization and radius formulas now retain their weight
denominators too, instead of printing/replaying cached `3` and `9`. Six
regressions rebind coordinates, positive/negative/fractional weights and
zero/nonzero radii, checking complete coefficients against direct model
evaluation and independent weight/radius expectations.

The [eager-values lesson](../../examples/galaga_v2/eager_values_and_expressions.py)
teaches denominator rebinding, rounded supplied physical inputs, and finite
subnormal division; its new cells are executed by a regression test.
Full validation is recorded in the
[migration inventory](../v2/numeric-test-migration-inventory.md).

This refines the v2 operator contract and supersedes the lazy-node mechanism
of [ADR-026](026-expression-nodes-exp-div.md) without changing its intention to
preserve both sides of a symbolic fraction.
