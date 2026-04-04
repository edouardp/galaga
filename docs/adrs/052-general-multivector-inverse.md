# ADR-052: General Multivector Inverse via Hitzer/Shirokov

## Status

Accepted

## Context

The previous `inverse()` used the versor inverse formula: `x⁻¹ = ~x / (x * ~x).scalar_part`. This only produces correct results for versors (products of non-null vectors). For general multivectors, it silently returned wrong answers — `mv * inverse(mv)` would not equal 1, with no error or warning.

Kingdon solves this with two algorithms that handle any invertible multivector:
- Hitzer closed-form inverse (Hitzer & Sangwine 2017) for d ≤ 5
- Shirokov iterative algorithm (arXiv:2005.04015) for d ≥ 6

## Decision

Replace the versor-only inverse with a general inverse that dispatches by algebra dimension:

- **d ≤ 5**: Hitzer closed-form formulas using conjugate, involute, reverse, and grade selection. Each dimension has a specific composition that produces the adjugate numerator; the denominator comes from the scalar product of x with that numerator.
- **d ≥ 6**: Shirokov iterative algorithm that builds an adjugate via a sequence of powers and traces, converging in at most `2^⌈(d+1)/2⌉` steps.

Both paths compute `(numerator, denominator)` where `x⁻¹ = numerator / denominator`, and raise `ValueError` if the denominator is near zero.

## Consequences

- `inverse()` now works correctly for any invertible multivector, not just versors.
- No silent wrong answers — non-invertible MVs raise `ValueError`.
- Versor inverse is a special case that still works (and produces the same result).
- The Shirokov path for d ≥ 6 is more expensive (O(2^(d/2)) geometric products) but is rarely needed in practice — most GA applications use d ≤ 5.

## References

- E. Hitzer, S. Sangwine, "Multivector and multivector matrix inverses in real Clifford algebras", Applied Mathematics and Computation, 2017.
- D. Shirokov, "On computing the determinant, other characteristic polynomial coefficients, and inverse in Clifford algebras of arbitrary dimension", arXiv:2005.04015, 2020.
