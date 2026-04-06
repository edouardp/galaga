# Geometric Algebra Library Conventions Survey

A comparison of algebra construction, basis naming, and basis ordering across GA libraries.

## Algebra Construction

| Library | Language | Constructor forms | PGA example |
|---|---|---|---|
| **ganja.js** | JavaScript | `Algebra(p, q, r)` | `Algebra(2, 0, 1)` |
| **clifford** | Python | `Cl(p, q, r)` | `Cl(2, 0, 1)` |
| **kingdon** | Python | `Algebra(p, q, r)` | `Algebra(2, 0, 1)` |
| **galaga** | Python | `Algebra(p, q, r)` or `Algebra((m₁, m₂, …))` | `Algebra(2, 0, 1)` or `Algebra((0, 1, 1))` |
| **galgebra** | Python | `Ga('names', g=[m₁, m₂, …])` | `Ga('e1 e2 e0', g=[1, 1, 0])` |
| **GeometricAlgebra.jl** | Julia | `Cl(p, q, r)` or `Cl("+-0")` | `Cl(2, 0, 1)` or `Cl("++0")` |
| **Grassmann.jl** | Julia | `S"+-"` or `D"1,-1,0"` | `D"0,1,1"` or `D"1,1,0"` |

Notes:
- galaga accepts both tuples and lists: `Algebra((0, 1, 1))` or `Algebra([0, 1, 1])`. The explicit form gives direct control over which basis vector is null and where it sits in the ordering. The `(p, q, r)` form applies a fixed ordering convention (see below).
- galgebra has no `(p, q, r)` constructor — the user always specifies names and metric entries explicitly.
- Grassmann.jl's `S"..."` string form does not support `0` for null vectors (treats them as `+1`). Use `D"..."` for diagonal metrics with zeros.

## Basis Naming

| Library | Default names | Bivector style | Naming overrides |
|---|---|---|---|
| **ganja.js** | `e0, e1, e2, …` (0-indexed) | `e01, e12, …` (compact subscript) | None standard |
| **clifford** | `e1, e2, e3, …` (1-indexed) | `e12, e13, …` (compact subscript) | Custom via layout |
| **kingdon** | `e0, e1, e2, …` for degenerate; `e1, e2, …` otherwise | `e01, e12, …` (compact subscript) | None standard |
| **galaga** | `e₁, e₂, e₃, …` (1-indexed, unicode subscripts) | `e₁₂, e₁₃, …` (compact, default) | 7 factories: `b_default()`, `b_gamma()` (γ₀γ₁…), `b_sigma()` (σ₁σ₂…), `b_sigma_xyz()` (σₓσᵧ…), `b_pga()`, `b_sta()`, `b_cga()`. Custom: `BladeConvention(vector_names=...)`. 3 styles: `"compact"`, `"juxtapose"`, `"wedge"`. Per-blade overrides via metric-role keys. |
| **galgebra** | User-specified (e.g. `'e1 e2 e0'`, `'x y z'`) | `e1^e2`, `x^y` (wedge notation) | Fully user-controlled via constructor string |
| **GeometricAlgebra.jl** | `v1, v2, v3, …` (1-indexed, `v` prefix) | `v12, v13, …` (compact subscript) | `BasisDisplayStyle`: custom prefix, separator, index labels, ordering. E.g. `prefix="𝐞"`, `prefix="γ"` with `indices="⁰¹²³"`, `prefix="d"` with `sep=" ∧ "` |
| **Grassmann.jl** | `v1, v2, v3, …` or `v₁, v₂, …` (1-indexed) | `v₁₂, v₂₃, …` (compact subscript) | Named bases via `@basis (t=+1, x=-1)` |

## Basis Ordering for Cl(p, q, r)

When using the `(p, q, r)` constructor, libraries differ in which basis vectors get assigned to which indices:

| Library | Ordering | Cl(2,0,1) result |
|---|---|---|
| **ganja.js** | r, p, q (null first) | e0²=0, e1²=+1, e2²=+1 |
| **clifford** | r, p, q (null first) | e1²=0, e2²=+1, e3²=+1 |
| **kingdon** | r, p, q (null first) | e0²=0, e1²=+1, e2²=+1 |
| **galaga** | p, q, r → **r, p, q** (null first) | e₁²=0, e₂²=+1, e₃²=+1 |
| **GeometricAlgebra.jl** | p, q, r (null last) | v1²=+1, v2²=+1, v3²=0 |
| **galgebra** | user-specified | (no p,q,r constructor) |
| **Grassmann.jl** | user-specified | (no p,q,r constructor) |

### Consequences

In non-degenerate algebras (r=0), the ordering difference only affects whether negative-squaring vectors come before or after positive ones. In PGA (r≥1), the difference is more significant:

- **(r, p, q)** libraries (ganja.js, clifford, kingdon, galaga) place the null vector at the lowest index. This matches the common PGA convention where `e0` is the "origin" or "ideal" basis vector.
- **(p, q, r)** libraries (GeometricAlgebra.jl) place the null vector at the highest index. The null vector ends up named `v3` rather than `e0`.

The mathematical results are identical — the same algebra is constructed. But blade names and signs of compound blades (e.g. `e0∧e1` vs `e1∧e3`) differ, which can cause confusion when comparing code between libraries. Libraries with explicit metric constructors (galgebra, Grassmann.jl, and galaga's tuple form) avoid this by letting the user choose.

### STA Example: Cl(1,3,0)

| Library | Ordering | Result |
|---|---|---|
| ganja.js | `Algebra(1,3,0)` → e1²=+1, e2²=-1, e3²=-1, e4²=-1 | p then q |
| clifford | `Cl(1,3)` → e1²=+1, e2²=-1, e3²=-1, e4²=-1 | p then q |
| kingdon | `Algebra(1,3)` → e1²=+1, e2²=-1, e3²=-1, e4²=-1 | p then q |
| galaga | `Algebra(1,3)` → e₁²=+1, e₂²=-1, e₃²=-1, e₄²=-1 | p then q |
| GeometricAlgebra.jl | `Cl(1,3)` → v1²=+1, v2²=-1, v3²=-1, v4²=-1 | p then q |

When r=0, all libraries agree: positive basis vectors first, then negative.
