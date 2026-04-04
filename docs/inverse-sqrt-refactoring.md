# Inverse and Square Root Refactoring

## Overview

Two significant gaps in galaga's numeric operations — identified by comparing against kingdon — have been closed. Both `inverse()` and `sqrt()` now handle general multivectors, not just the narrow special cases they were previously limited to.

## Inverse: from versor-only to general

### Before

`inverse(x)` used the versor inverse formula: `x⁻¹ = ~x / (x * ~x)`. This only works for versors (products of non-null vectors). For general multivectors it silently returned wrong answers:

```python
>>> mv = 1 + e₁ + e₁₂ + e₁₂₃
>>> inverse(mv) * mv
1 + 0.5e₁ - 0.5e₂ + 0.5e₃    # wrong — should be 1
```

### After

`inverse(x)` now dispatches by algebra dimension:

- **d ≤ 5**: Hitzer closed-form inverse (Hitzer & Sangwine 2017). Each dimension has a specific formula built from conjugate, involute, reverse, and grade selection.
- **d ≥ 6**: Shirokov iterative algorithm (arXiv:2005.04015). Works in any algebra via an adjugate construction that converges in at most 2^⌈(d+1)/2⌉ steps.

```python
>>> mv = 1 + e₁ + e₁₂ + e₁₂₃
>>> inverse(mv) * mv
1    # correct
```

What galaga can now invert:

- Scalars, vectors, bivectors, rotors (as before)
- Arbitrary mixed-grade multivectors in any signature
- Elements in degenerate algebras (PGA) where the versor formula applies
- High-dimensional algebras (d ≥ 6) via the Shirokov fallback
- Non-invertible elements raise `ValueError` (no more silent wrong answers)

## Square Root: from scalar-only to Study numbers

### Before

`scalar_sqrt(x)` only accepted pure scalar multivectors or plain numbers. Attempting to take the square root of a rotor or translator raised `ValueError`.

### After

A new `sqrt(x)` function uses the Study number decomposition (Roelfs & De Keninck 2022):

```
sqrt(a + bI) = bI / (2·cp) + cp
where cp = √(½(a + √(a² - bI²)))
```

This works for any element where the non-scalar part squares to a scalar.

```python
>>> R = exp(0.7 * (e₁ ^ e₂))
>>> sqrt(R) * sqrt(R) == R       # rotor: halves the rotation angle
True

>>> T = 1 + 0.5 * (e₀ ^ e₁)
>>> sqrt(T) * sqrt(T) == T       # PGA translator
True
```

What galaga can now take the square root of:

- Pure scalars and plain numbers (as before, also via `scalar_sqrt`)
- Rotors — `sqrt(R)` halves the rotation angle
- PGA translators — `sqrt(T)` halves the translation distance
- Any Study number (scalar + part that squares to a scalar)
- Non-Study inputs raise `ValueError` with a clear message

## API

Both functions are exported from `galaga`:

```python
from galaga import inverse, sqrt, scalar_sqrt
```

- `inverse(x)` — general multivector inverse
- `sqrt(x)` — Study number square root
- `scalar_sqrt(x)` — preserved for backward compatibility (scalar-only)

The `.inv` property on `Multivector` uses the new general inverse. Lazy/expression-tree paths are fully supported for both operations.

## References

- ADR-052: General Multivector Inverse via Hitzer/Shirokov
- ADR-053: General Square Root via Study Number Decomposition
