# ga — Geometric Algebra for Python

A numeric geometric algebra library with a stable, programmer-first API.

- **Named functions are the contract** — `gp`, `op`, `grade`, `reverse`, `dual`, `inverse` never change meaning
- **Operators are sugar** — `*`, `^`, `|`, `~` are convenience only
- **No ambiguity** — every inner product variant has its own name
- **Unicode pretty-printing** — `3 + 2e₁ - e₃`, `γ₀γ₁`, `σₓσᵧ`
- **Symbolic expression trees** — write `grade(R * v * ~R, 1)` and see `⟨RvR̃⟩₁`

## Install

```bash
uv add numpy   # only dependency
```

## Quick Start

```python
from ga import *

# Create a 3D Euclidean algebra
alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

# Build multivectors naturally
v = 3*e1 + 4*e2
B = e1 ^ e2            # bivector
mv = 1 + 2*e1 + 3*B    # mixed grade

print(v)    # 3e₁ + 4e₂
print(B)    # e₁₂
print(mv)   # 1 + 2e₁ + 3e₁₂
```

## Algebra Construction

The signature tuple defines each basis vector's square: `+1`, `-1`, or `0`.

```python
cl3 = Algebra((1, 1, 1))           # Cl(3,0) — 3D Euclidean
sta = Algebra((1, -1, -1, -1))     # Cl(1,3) — Spacetime Algebra
pga = Algebra((1, 1, 1, 0))        # Cl(3,0,1) — Projective GA
```

### Constructors

```python
alg.basis_vectors()     # (e₁, e₂, e₃)
alg.pseudoscalar()      # e₁₂₃ (also alg.I)
alg.identity            # scalar 1 (𝟙)
alg.scalar(5.0)         # 5
alg.vector([1, 2, 3])   # e₁ + 2e₂ + 3e₃
alg.blade("e12")        # e₁₂
alg.rotor(B, radians=θ) # rotor for rotation by θ in plane B
```

## Products

Every product has a definitive named function. Operators are optional shorthand.

| Operation | Function | Operator | Unicode |
|---|---|---|---|
| Geometric product | `gp(a, b)` | `a * b` | juxtaposition |
| Outer (wedge) product | `op(a, b)` | `a ^ b` | `∧` |
| Left contraction | `left_contraction(a, b)` | | `⌋` |
| Right contraction | `right_contraction(a, b)` | | `⌊` |
| Hestenes inner | `hestenes_inner(a, b)` | `a \| b` | `·` |
| Scalar product | `scalar_product(a, b)` | | `∗` |
| Commutator | `commutator(a, b)` | | |
| Anticommutator | `anticommutator(a, b)` | | |

```python
e1, e2, e3 = alg.basis_vectors()

gp(e1, e2)                  # e₁₂
op(e1, e2)                  # e₁₂
left_contraction(e1, e1^e2) # e₂
scalar_product(e1, e1)      # 1

# Operator shorthand
e1 * e2     # geometric product
e1 ^ e2     # outer product
e1 | (e1^e2)  # Hestenes inner product
```

### Unified Inner Product

The `ip` function dispatches to the specific inner product you want — no ambiguity.

```python
ip(e1, e1)                       # Hestenes (default)
ip(e1, e1 ^ e2, mode="left")     # left contraction
ip(e1 ^ e2, e2, mode="right")    # right contraction
ip(e1, e2, mode="scalar")        # scalar product
```

### When Do the Inner Products Differ?

For vector-on-vector they all agree. The differences show up with mixed grades:

| Expression | Left contraction | Right contraction | Hestenes |
|---|---|---|---|
| `vector, bivector` | `e₂` (grade 2−1=1) | `0` (1−2 < 0) | `e₂` (\|1−2\|=1) |
| `bivector, vector` | `0` (1−2 < 0) | `e₂` (grade 2−1=1) | `-e₂` (\|2−1\|=1) |
| `scalar, vector` | `3e₁` (passes through) | `0` (0−1 < 0) | `0` (kills scalars) |
| `vector, scalar` | `0` (1−0 < 0) | `3e₁` (passes through) | `0` (kills scalars) |

```python
e12 = e1 ^ e2

left_contraction(e1, e12)      # e₂  — vector "removes" from bivector
left_contraction(e12, e1)      # 0   — can't remove higher from lower

right_contraction(e12, e1)     # e₂  — mirror of left contraction
right_contraction(e1, e12)     # 0

hestenes_inner(e1, e12)        # e₂  — uses |grade difference|
hestenes_inner(e12, e1)        # -e₂ — nonzero both ways (unlike left/right)
hestenes_inner(cl3.scalar(3), e1)  # 0 — always zero if either is scalar
```

**Rule of thumb:** left contraction is the most common in GA literature.
Hestenes inner is symmetric in grade but kills scalars. Right contraction is the mirror of left.

## Unary Operations

| Operation | Function | Operator | Unicode |
|---|---|---|---|
| Reverse | `reverse(x)` | `~x` | `x̃` |
| Grade involution | `involute(x)` | | `x̂` |
| Clifford conjugate | `conjugate(x)` | | `x̄` |

```python
B = e1 ^ e2

reverse(B)      # -e₁₂  (or ~B)
involute(B)     #  e₁₂  (even grade unchanged)
conjugate(B)    # -e₁₂  (reverse ∘ involute)
```

## Grade Operations

```python
mv = 3 + 2*e1 + (e1 ^ e2)

grade(mv, 0)    # 3
grade(mv, 1)    # 2e₁
grade(mv, 2)    # e₁₂
mv[0]           # 3       (shorthand for grade)
mv[1]           # 2e₁
mv[2]           # e₁₂
grades(mv, [0, 2])  # 3 + e₁₂

even_grades(mv)     # 3 + e₁₂  (grades 0, 2, ...)
odd_grades(mv)      # 2e₁      (grades 1, 3, ...)

scalar(mv)      # 3.0 (float)
```

You can also use `grade()` directly:

```python
grade(mv, "even")   # same as even_grades(mv)
grade(mv, "odd")    # same as odd_grades(mv)
```

## Norm, Unit, Inverse

```python
v = 3*e1 + 4*e2

norm(v)         # 5.0
norm2(v)        # 25.0
unit(v)         # 0.6e₁ + 0.8e₂
normalize(v)    # same as unit(v)
inverse(v)      # v⁻¹ such that v * inverse(v) = 1
```

Convenience properties on multivectors:

```python
v.inv           # inverse(v)
v.dag           # reverse(v)  — the "dagger"
v.sq            # gp(v, v)    — squared
v.scalar_part   # grade-0 coefficient as float
v.vector_part   # grade-1 coefficients as np.ndarray
```

Extract components for use with numpy, matplotlib, etc:

```python
v = 3*e1 + 4*e2 + 5*e3
v.vector_part           # np.array([3., 4., 5.])
v.scalar_part           # 0.0

mv = 7 + v + (e1^e2)
mv.vector_part          # np.array([3., 4., 5.])
mv.scalar_part          # 7.0
```

## Dual

```python
dual(e1 ^ e2)    # e₃  (in 3D Euclidean)
undual(e3)       # e₁₂
```

## Predicates

```python
is_scalar(alg.scalar(5))    # True
is_vector(e1 + e2)          # True
is_bivector(e1 ^ e2)        # True
is_even(1 + (e1 ^ e2))      # True
is_rotor(R)                 # True (even-graded and R*~R = 1)
```

## Rotation Example

Rotate `e₁` by 90° in the `e₁e₂` plane:

```python
import numpy as np

theta = np.pi / 2
B = e1 ^ e2
R = alg.rotor(B, radians=theta)

v_rotated = R * e1 * ~R    # sandwich product
print(v_rotated)            # e₂
```

Or manually:

```python
R = alg.scalar(np.cos(theta/2)) - np.sin(theta/2) * B
```

## Exponential & Logarithm

`exp(B)` builds a rotor from a bivector directly — no manual cos/sin:

```python
B = (np.pi / 4) * (e1 ^ e2)
R = exp(B)                      # cos(π/4) + sin(π/4) e₁₂
print(R * e1 * ~R)              # e₂ (90° rotation)
```

`exp` handles all signatures automatically:
- Euclidean bivector (B² < 0): uses cos/sin
- Timelike bivector (B² > 0): uses cosh/sinh (Lorentz boosts)
- Null bivector (B² = 0): returns 1 + B (translations in PGA)

`log(R)` is the inverse — extract the bivector from a rotor:

```python
B_back = log(R)                 # recovers the bivector
R_back = exp(log(R))            # roundtrip: R_back == R
```

Note: `alg.rotor(B, radians=θ)` computes `exp(-θ/2 * B)` for a unit bivector B.

## Projection, Rejection, Reflection

```python
v = 3*e1 + 4*e2 + 5*e3
plane = e1 ^ e2

project(v, plane)    # 3e₁ + 4e₂   (component in the plane)
reject(v, plane)     # 5e₃         (component perpendicular)
```

Projection and rejection always sum back to the original:

```python
project(v, plane) + reject(v, plane) == v   # True
```

Reflection flips the component parallel to a normal vector:

```python
reflect(e1 + e2, e1)    # -e₁ + e₂   (flip the e₁ part)
reflect(e2, e1)         #  e₂        (perpendicular: unchanged)
reflect(e1, e1)         # -e₁        (parallel: negated)
```

Double reflection is always identity: `reflect(reflect(v, n), n) == v`.

## Spacetime Algebra

```python
sta = Algebra((1, -1, -1, -1), names="gamma")
g0, g1, g2, g3 = sta.basis_vectors()

print(g0 * g0)      #  1   (timelike)
print(g1 * g1)      # -1   (spacelike)
print(g0 * g1)      # γ₀γ₁ (bivector)
print(sta.I)        # 𝑰
```

## Basis Naming

Choose how basis vectors display — both in code (`repr`) and in print output (`str`).

### Presets

```python
# Default: e₁, e₂, e₃
alg = Algebra((1, 1, 1))

# Gamma: γ₀, γ₁, γ₂, γ₃
sta = Algebra((1, -1, -1, -1), names="gamma")

# Sigma (numbered): σ₁, σ₂, σ₃
pauli = Algebra((1, 1, 1), names="sigma")

# Sigma (xyz): σₓ, σᵧ, σz
pauli = Algebra((1, 1, 1), names="sigma_xyz")
```

### Custom Names

Provide `(code_names, unicode_names)` tuples:

```python
alg = Algebra((1, 1, 1), names=(["a", "b", "c"], ["𝐚", "𝐛", "𝐜"]))
a, b, c = alg.basis_vectors()
print(a + 2*b)      # 𝐚 + 2𝐛
print(repr(a + 2*b)) # a + 2b
```

### Blade Lookup

Works with both default and custom names:

```python
alg.blade("e12")         # e₁₂
sta.blade("g0g1")        # γ₀γ₁
```

## Display

`str()` uses unicode, `repr()` uses ASCII by default:

```python
mv = 3 + 2*e1 - e3

str(mv)     # '3 + 2e₁ - e₃'
repr(mv)    # '3 + 2e1 - e3'
```

To make `repr()` use unicode too (nicer in IPython/REPL), pass `repr_unicode=True`:

```python
alg = Algebra((1, 1, 1), repr_unicode=True)
e1, e2, e3 = alg.basis_vectors()

repr(3*e1 + 4*e2)  # '3e₁ + 4e₂'
```

The pseudoscalar always displays as `I` / `𝑰`:

```python
print(alg.I)        # 𝑰
print(repr(alg.I))  # I  (or 𝑰 with repr_unicode=True)
```

Coefficients of ±1 are suppressed: `e₁₂` not `1e₁₂`, `-e₃` not `-1e₃`.

## Symbolic Expressions

Build expression trees that render as mathematical notation, then evaluate to get numeric results.

```python
from ga.symbolic import sym, grade, reverse, dual, norm, unit, inverse, gp, op

alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

R = sym(e1 * e2, "R")
v = sym(e1 + 2*e2, "v")
```

### Rendering

```python
print(R * v * ~R)                     # RvR̃
print(grade(R * v * ~R, 1))           # ⟨RvR̃⟩₁
print(op(sym(e1, "a"), sym(e2, "b"))) # a∧b
print(dual(sym(e1, "v")))             # v⋆
print(norm(sym(e1, "v")))             # ‖v‖
print(unit(sym(e1, "v")))             # v̂
print(inverse(sym(e1, "v")))          # v⁻¹
print(reverse(sym(e1*e2, "R")))       # R̃
```

Full rendering table:

| Expression | Code | Renders as |
|---|---|---|
| Geometric product | `R * v * ~R` | `RvR̃` |
| Wedge | `a ^ b` | `a∧b` |
| Left contraction | `a \| b` | `a⌋b` |
| Right contraction | `right_contraction(a, b)` | `a⌊b` |
| Hestenes inner | `hestenes_inner(a, b)` | `A·B` |
| Scalar product | `scalar_product(a, b)` | `A∗B` |
| Reverse | `~R` | `R̃` |
| Involute | `involute(v)` | `v̂` |
| Conjugate | `conjugate(v)` | `v̄` |
| Dual | `dual(v)` | `v⋆` |
| Undual | `undual(v)` | `v⋆⁻¹` |
| Norm | `norm(v)` | `‖v‖` |
| Unit | `unit(v)` | `v̂` |
| Inverse | `v.inv` | `v⁻¹` |
| Grade projection | `grade(A * B, 2)` | `⟨AB⟩₂` |
| Even grades | `even_grades(A)` | `⟨A⟩₊` |
| Odd grades | `odd_grades(A)` | `⟨A⟩₋` |
| Squared | `squared(R)` or `R.sq` | `R²` |
| Addition | `a + b` | `a + b` |
| Scalar multiply | `3 * a` | `3a` |

### Evaluation

Every symbolic expression can be evaluated to a concrete `Multivector`:

```python
expr = grade(R * v * ~R, 1)
print(expr)          # ⟨RvR̃⟩₁
print(expr.eval())   # -e₁ - 2e₂
```

### LaTeX Output

Every expression has a `.latex()` method for use in documents, notebooks, and markdown:

```python
expr = grade(R * v * ~R, 1)
expr.latex()            # \langle R v \tilde{R} \rangle_{1}
expr.latex(wrap='$')    # $\langle R v \tilde{R} \rangle_{1}$
expr.latex(wrap='$$')   # $$\n...\n$$  (display block)
```

The `wrap` parameter is handy in f-strings for marimo/Jupyter markdown cells:

```python
mo.md(f"{expr.latex(wrap='$')} = {expr.eval().latex(wrap='$')}")
```

In Jupyter notebooks, expressions render automatically via `_repr_latex_()`.

Concrete `Multivector` objects also have `.latex()`:

```python
v = 3*e1 + 4*e2
v.latex()  # 3 e_{12}
```

Full LaTeX rendering table:

| Expression | Code | Unicode | LaTeX |
|---|---|---|---|
| Geometric product | `R * v * ~R` | `RvR̃` | `R v \tilde{R}` |
| Wedge | `a ^ b` | `a∧b` | `a \wedge b` |
| Left contraction | `a \| b` | `a⌋b` | `a \;\lrcorner\; b` |
| Right contraction | `right_contraction(a, b)` | `a⌊b` | `a \;\llcorner\; b` |
| Hestenes inner | `hestenes_inner(a, b)` | `A·B` | `A \cdot B` |
| Scalar product | `scalar_product(a, b)` | `A∗B` | `A * B` |
| Reverse | `~R` | `R̃` | `\tilde{R}` |
| Involute | `involute(v)` | `v̂` | `v^\dagger` |
| Conjugate | `conjugate(v)` | `v̄` | `\bar{v}` |
| Dual | `dual(v)` | `v⋆` | `v^*` |
| Undual | `undual(v)` | `v⋆⁻¹` | `v^{*^{-1}}` |
| Norm | `norm(v)` | `‖v‖` | `\lVert v \rVert` |
| Unit | `unit(v)` | `v̂` | `\hat{v}` |
| Inverse | `v.inv` | `v⁻¹` | `v^{-1}` |
| Grade projection | `grade(A * B, 2)` | `⟨AB⟩₂` | `\langle A B \rangle_{2}` |
| Even grades | `even_grades(A)` | `⟨A⟩₊` | `\langle A \rangle_{\text{even}}` |
| Odd grades | `odd_grades(A)` | `⟨A⟩₋` | `\langle A \rangle_{\text{odd}}` |
| Squared | `squared(R)` or `R.sq` | `R²` | `R^2` |
| Addition | `a + b` | `a + b` | `a + b` |
| Scalar multiply | `3 * a` | `3a` | `3 a` |

### Drop-in Functions

The symbolic module provides drop-in replacements for all `ga` functions. They detect `Expr` arguments and build trees; with plain `Multivector` arguments they delegate to the numeric core:

```python
from ga.symbolic import gp, grade, reverse

# With Sym → builds expression tree
grade(R * v * ~R, 1)   # returns Expr

# With Multivector → returns Multivector directly
grade(e1 + e2, 1)      # returns Multivector
```

### Simplification

`simplify()` applies algebraic rewrite rules to expression trees:

```python
from ga.symbolic import sym, simplify, grade, norm, unit, inverse, op

alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

v = sym(e1, "v")
R = sym(alg.rotor(e1^e2, radians=0.5), "R")
a = sym(e1, "a")
B = sym(e1^e2, "B")

simplify(~~v)              # v         (double reverse)
simplify(inverse(inverse(v)))  # v     (double inverse)
simplify(a ^ a)            # 0         (wedge self = 0)
simplify(a + a)            # 2a        (collection)
simplify(3 * (2 * v))      # 6v        (scalar collapse)
simplify(R * ~R)           # 1         (rotor normalization)
simplify(norm(unit(v)))    # 1         (unit has norm 1)
simplify(grade(v, 1))      # v         (v is known grade-1)
simplify(grade(v, 2))      # 0         (v has no grade-2)
```

Grade is auto-detected from the multivector data, so `sym(e1, "v")` knows it's grade-1 and `sym(e1^e2, "B")` knows it's grade-2. Simplification runs to a fixed point, so cascading rules like `a - (-a) → a + a → 2a` resolve fully.

## Sandwich Product

The sandwich product `R x R̃` is common enough to deserve a shortcut:

```python
sandwich(R, e1)     # R * e1 * ~R
sw(R, e1)           # same thing, short alias
```

Works in the symbolic layer too:

```python
from ga.symbolic import sym, sandwich

R = sym(alg.rotor(e1^e2, radians=np.pi/2), "R")
v = sym(e1, "v")
print(sandwich(R, v))        # RvR̃
print(sandwich(R, v).eval()) # e₂
```

## Aliases

Short names for experienced users, long names for readability:

| Short | Long |
|---|---|
| `gp` | `geometric_product` |
| `op` | `wedge`, `outer_product` |
| `ip` | `inner_product` |
| `rev` | `reverse` |
| `unit` | `normalize`, `normalise` |
| `sw` | `sandwich` |
| `alg.rotor` | `alg.rotor_from_bivector`, `alg.rotor_from_plane_angle` |

## Recipes

Things you can build from the primitives — no extra functions needed.

### Angle Between Vectors

```python
angle = np.arctan2(norm(a ^ b), scalar(a | b))
```

Uses `atan2` for numerical stability (works even when vectors are nearly parallel or perpendicular). The wedge magnitude is `|a||b|sin θ`, the inner product is `|a||b|cos θ`.

### Check Parallel / Perpendicular

```python
parallel      = np.isclose(norm(a ^ b), 0)    # wedge vanishes
perpendicular = np.isclose(scalar(a | b), 0)  # inner product vanishes
```

### Compose Rotations

Rotors compose by geometric product — apply `R1` first, then `R2`:

```python
R_total = R2 * R1
v_rotated = R_total * v * ~R_total
```

Order matters: `R2 * R1` means "do R1, then R2" (right-to-left, like matrix multiplication).

### Interpolate a Rotation (SLERP)

```python
R_half = exp(0.5 * log(R))       # 50% of the rotation
R_t    = exp(t * log(R))         # fraction t ∈ [0, 1]
```

`log` extracts the bivector, scaling it interpolates the angle, `exp` rebuilds the rotor.

### Gram–Schmidt (Orthogonalize)

Make `b` orthogonal to `a` by removing the parallel component:

```python
b_orth = reject(b, a)            # component of b perpendicular to a
```

For a full basis, chain rejections:

```python
u1 = unit(a)
u2 = unit(reject(b, a))
u3 = unit(reject(reject(c, a), u2))
```

### Rotate 90° Within a Plane

```python
B = e1 ^ e2
R90 = alg.rotor(B, degrees=90)
perp = R90 * v * ~R90            # v rotated 90° in the e₁e₂ plane
```

Useful for finding the perpendicular direction within a subspace.

### Area and Volume

The wedge product directly gives oriented area and volume:

```python
area = norm(u ^ v)               # parallelogram area
vol  = norm(u ^ v ^ w)           # parallelepiped volume
```

These work in any dimension — `norm(a ^ b)` is the area of the parallelogram spanned by `a` and `b`, regardless of the ambient space.

### Cross Product (3D Only)

```python
cross = dual(a ^ b)              # a × b as a vector
```

The wedge gives a bivector (oriented plane); the dual converts it to the normal vector. Only meaningful in 3D where bivectors and vectors are dual.

### Bivector Commutator Algebra

Bivectors form a Lie algebra under the commutator product:

```python
commutator(e1^e2, e2^e3)         # e₁₃ — the "cross product" of bivectors
```

In 3D Euclidean space, this is isomorphic to the vector cross product. In Cl(1,3), it gives the Lorentz algebra.

## API Reference

### `Algebra(signature, names=None)`

| Method / Property | Description |
|---|---|
| `basis_vectors()` | Tuple of basis 1-vectors |
| `pseudoscalar()` | Unit pseudoscalar |
| `I` | Unit pseudoscalar (property) |
| `identity` | Scalar 1 |
| `scalar(value)` | Scalar multivector |
| `vector(coeffs)` | 1-vector from list |
| `blade(name)` | Basis blade by name |
| `rotor(B, radians=, degrees=)` | Rotor for rotation in plane B |

### `Multivector`

| Property | Description |
|---|---|
| `[k]` | Grade-k projection (`x[2]` = `grade(x, 2)`) |
| `.inv` | Inverse |
| `.dag` | Reverse (dagger) |
| `.sq` | Squared (geometric product with self) |
| `.scalar_part` | Grade-0 coefficient as `float` |
| `.vector_part` | Grade-1 coefficients as `np.ndarray` |
| `.algebra` | Parent algebra |
| `.data` | NumPy coefficient array |

### Functions

| Function | Description |
|---|---|
| `gp(a, b)` | Geometric product |
| `op(a, b)` | Outer (wedge) product |
| `left_contraction(a, b)` | Left contraction `a ⌋ b` |
| `right_contraction(a, b)` | Right contraction `a ⌊ b` |
| `hestenes_inner(a, b)` | Hestenes inner product |
| `scalar_product(a, b)` | Scalar product |
| `ip(a, b, mode=...)` | Unified inner product dispatcher |
| `commutator(a, b)` | `(ab - ba) / 2` |
| `anticommutator(a, b)` | `(ab + ba) / 2` |
| `reverse(x)` | Reverse `x̃` |
| `involute(x)` | Grade involution `x̂` |
| `conjugate(x)` | Clifford conjugate `x̄` |
| `grade(x, k)` | Grade-k projection |
| `grades(x, ks)` | Multi-grade projection |
| `scalar(x)` | Extract scalar coefficient |
| `dual(x)` | Dual |
| `undual(x)` | Undual |
| `norm(x)` | `√\|x x̃\|` |
| `norm2(x)` | `⟨x x̃⟩₀` |
| `unit(x)` | Normalize to unit |
| `inverse(x)` | Versor inverse |
| `squared(x)` | `x²` — geometric product with self |
| `sandwich(r, x)` | Sandwich product `r x r̃` |
| `exp(B)` | Bivector exponential → rotor |
| `log(R)` | Rotor logarithm → bivector |
| `project(v, B)` | Component of v in subspace B |
| `reject(v, B)` | Component of v perpendicular to B |
| `reflect(v, n)` | Reflect v in hyperplane orthogonal to n |
| `even_grades(x)` | Even-grade components |
| `odd_grades(x)` | Odd-grade components |
| `is_scalar(x)` | True if pure scalar |
| `is_vector(x)` | True if pure 1-vector |
| `is_bivector(x)` | True if pure 2-vector |
| `is_even(x)` | True if even-graded |
| `is_rotor(x)` | True if even and `x*~x = 1` |

## Examples

Interactive [marimo](https://marimo.io) notebooks in `examples/`:

- **`symbolic_demo.py`** — Symbolic expression trees, rendering, simplification, LaTeX output
- **`spacetime_algebra.py`** — Spacetime Algebra Cl(1,3): boosts, rotations, EM field, Thomas–Wigner rotation
- **`quantum_physics.py`** — Quantum spin-½: Bloch sphere, measurement, Stern–Gerlach, Larmor precession
- **`pga_demo.py`** — Projective GA Cl(3,0,1): translations, reflections, motors, screw interpolation

```bash
uv run marimo edit examples/quantum_physics.py
```

## Internals

- Basis blades are represented as **bitmasks** — `e₁ = 0b001`, `e₂ = 0b010`, `e₁₂ = 0b011`
- Multiplication tables are **precomputed** at algebra creation time
- Multivector coefficients are **dense NumPy arrays** of length `2ⁿ`
- The `Algebra` object is **immutable** after creation
- `Multivector` is lightweight: just an algebra reference + data array

## Testing

```bash
uv run pytest tests/ -v                          # run all tests
uv run pytest tests/ --cov=ga --cov-report=term  # with coverage
```

349 tests, 99% coverage. Tests include:
- Algebraic identities (associativity, distributivity, reverse-of-product)
- Golden tests for Cl(2,0), Cl(3,0), Cl(1,3)
- All five inner products with mixed-grade cases where they diverge
- Exponential/logarithm roundtrips (Euclidean, hyperbolic, null)
- Projection/rejection complement property, reflection involution
- Symbolic rendering, evaluation, simplification rules
- LaTeX output for both `Multivector` and `Expr`
- Edge cases and error handling

