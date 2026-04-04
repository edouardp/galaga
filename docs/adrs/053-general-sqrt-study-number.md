# ADR-053: General Square Root via Study Number Decomposition

## Status

Accepted

## Context

`scalar_sqrt` only works on pure scalar multivectors, raising `ValueError` for anything else. This means common operations like taking the square root of a rotor (to halve a rotation angle) or a PGA translator are not supported.

Kingdon implements `sqrt()` using the Study number decomposition (Roelfs & De Keninck 2022, doi:10.1002/mma.8639), which works for any element that decomposes as `a + bI` where `a` is scalar and `bI` squares to a scalar.

## Decision

Add a `sqrt()` function alongside the existing `scalar_sqrt()`:

- Decomposes `x = a + bI` where `a` is the scalar part
- Checks that `bI² = (x - a)²` is a pure scalar
- Computes `sqrt(x) = bI / (2·cp) + cp` where `cp = sqrt(½(a + sqrt(a² - bI²)))`
- Falls back to `scalar_sqrt` for pure scalars and plain numbers
- Raises `ValueError` if `bI` does not square to a scalar

`scalar_sqrt` is preserved unchanged for backward compatibility.

## Consequences

- Rotor square roots work: `sqrt(R)² = R`, halving the rotation angle.
- PGA translator square roots work: `sqrt(1 + ½d·e₀₁)² = 1 + ½d·e₀₁`.
- Clear error message when the input is not a Study number.
- `scalar_sqrt` remains available for code that explicitly wants scalar-only behavior.

## References

- M. Roelfs, S. De Keninck, "Graded Symmetry Groups: Plane and Simple", Advances in Applied Clifford Algebras, 2023. doi:10.1002/mma.8639
