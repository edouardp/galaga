---
status: partially superseded by ADR-165
date: 2026-03-25
deciders: edouard
---

# ADR-007: Integer-Only Multivector Exponentiation

ADR-165 extends `**` to finite real exponents for positive-scalar values in
all-null algebras. The integer rule here remains valid for every metric.

## Context and Problem Statement

Users expect `v ** 2` to work for squaring multivectors. Should we support
`__pow__`, and if so, for what exponents?

## Decision Drivers

* `v ** 2` is natural and common
* `R ** -1` is a clean way to write the inverse
* Fractional powers (e.g. `v ** 0.5`) are not well-defined for general multivectors
* Rotor square roots exist but require choosing conventions

## Considered Options

1. Support all numeric exponents
2. Support integer exponents only, return `NotImplemented` for floats
3. Don't implement `__pow__`

## Decision Outcome

Chosen option: "Integer exponents only" — `**0` returns scalar 1, positive
integers use repeated multiplication, negative integers use `inverse()`.
Non-integer exponents raise `TypeError`.

### Consequences

* Good, because `v ** 2`, `R ** -1`, `e1 ** 3` all work naturally
* Good, because no silent wrong answers for undefined operations
* Good, because rotor fractional powers can be added later via `exp(t * log(R))`
* Bad, because `R ** 0.5` doesn't work (users must use `exp(0.5 * log(R))`)
