# ADR-054: Outer (Wedge) Transcendental Functions

## Status

Accepted

## Context

Kingdon provides `outerexp`, `outersin`, `outercos`, and `outertan` — transcendental functions defined over the outer (wedge) product instead of the geometric product. Galaga had no equivalent.

These are unambiguous: there is only one outer product, so unlike the inner product family, no convention variants exist.

## Decision

Add four functions:

- `outerexp(x)` = `1 + x + x∧x/2! + x∧x∧x/3! + ...` (terminates at grade n)
- `outersin(x)` = odd terms of the outer exponential series
- `outercos(x)` = even terms of the outer exponential series
- `outertan(x)` = `outersin(x) * inverse(outercos(x))`

The series always terminates because wedging more than n vectors in an n-dimensional algebra gives zero. All four support the lazy expression tree path.

## Consequences

- Galaga now matches kingdon's outer transcendental support.
- `outertan` raises `ValueError` when `outercos` is not invertible, matching the behavior of kingdon's `ZeroDivisionError`.
