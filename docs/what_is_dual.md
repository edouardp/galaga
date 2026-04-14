# What is the Dual?

There is no single "dual" in geometric algebra. Different libraries use
different definitions, producing different signs. This document surveys
the conventions and explains why.

## The test: `dual(e₁∧e₂)` in Cl(3,0)

In Cl(3,0), the pseudoscalar is I = e₁₂₃, and I² = −1, so I⁻¹ = −e₁₂₃.

| Library | `dual(e₁₂)` | Definition |
|---|---|---|
| **galaga** | `e₃` | `x ⌋ I⁻¹` |
| **clifford** (Python) | `e₃` | `x * I⁻¹` |
| **kingdon** (Python) | `e₃` | `x * I⁻¹` |
| **Grassmann.jl** (Julia) | `v₃` | `x ⌋ I⁻¹` |
| **galgebra** (Python) | `−e₃` | `I⁻¹ * x` (= `x * I`) |
| **ganja.js** (JS) | `−e₃` | `x * I` (Poincaré dual) |

## Full blade table in Cl(3,0)

All definitions agree on the grade mapping (grade k → grade n−k), but
differ in sign for certain grades.

| Blade | galaga / clifford / kingdon | galgebra / ganja.js |
|---|---|---|
| `1` | `−e₁₂₃` | `e₁₂₃` |
| `e₁` | `−e₂₃` | `e₂₃` |
| `e₂` | `e₁₃` | `−e₁₃` |
| `e₃` | `−e₁₂` | `e₁₂` |
| `e₁₂` | `e₃` | `−e₃` |
| `e₁₃` | `−e₂` | `e₂` |
| `e₂₃` | `e₁` | `−e₁` |
| `e₁₂₃` | `1` | `−1` |

The two columns differ by an overall factor of `−1` (because `I⁻¹ = −I`
in Cl(3,0), so `x * I⁻¹ = −x * I`).

## Why the disagreement?

There are at least four reasonable definitions of "dual":

1. **Right multiply by I⁻¹**: `x* = x I⁻¹`
   Used by clifford, kingdon. Simple, but requires I to be invertible.

2. **Left contraction into I⁻¹**: `x* = x ⌋ I⁻¹`
   Used by galaga, Grassmann.jl. Equivalent to (1) for blades in
   nondegenerate algebras. Preferred by Dorst, Fontijne & Mann.

3. **Right multiply by I** (Poincaré dual): `x* = x I`
   Used by ganja.js. Differs from (1) by a factor of I².

4. **Left multiply by I⁻¹**: `x* = I⁻¹ x`
   Used by galgebra. Differs from (1) by a sign that depends on the
   grade of x: `I⁻¹ x = (−1)^(k(n−k)) x I⁻¹` for a grade-k blade
   in n dimensions.

In Cl(3,0), definitions (1) and (2) agree on all blades. Definitions
(3) and (4) also agree with each other, and differ from (1)/(2) by a
global sign of −1.

## When does it matter?

- **Nondegenerate algebras (VGA, STA, CGA)**: all four definitions work,
  but signs differ. Pick one and be consistent.
- **Degenerate algebras (PGA)**: the pseudoscalar is not invertible
  (I² = 0), so definitions (1)–(4) all fail. Use `complement()` instead,
  which is purely combinatorial and works in all signatures.

## galaga's choice

galaga uses definition (2): `dual(x) = x ⌋ I⁻¹`. This matches Dorst et al.
and gives the same results as clifford and kingdon.

For degenerate algebras, `dual()` raises `ValueError` with a message
directing users to `complement()`. See ADR-010 for the rationale.
