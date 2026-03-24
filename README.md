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
```

## Products

Every product has a definitive named function. Operators are optional shorthand.

| Operation | Function | Operator | Unicode |
|---|---|---|---|
| Geometric product | `gp(a, b)` | `a * b` | juxtaposition |
| Outer (wedge) product | `op(a, b)` | `a ^ b` | `∧` |
| Left contraction | `left_contraction(a, b)` | `a \| b` | `⌋` |
| Right contraction | `right_contraction(a, b)` | | `⌊` |
| Hestenes inner | `hestenes_inner(a, b)` | | `·` |
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
e1 | (e1^e2)  # left contraction
```

### Unified Inner Product

The `ip` function dispatches to the specific inner product you want — no ambiguity.

```python
ip(e1, e1)                        # Hestenes (default)
ip(e1, e1 ^ e2, mode="left")     # left contraction
ip(e1 ^ e2, e2, mode="right")    # right contraction
ip(e1, e2, mode="scalar")        # scalar product
```

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

even(mv)        # 3 + e₁₂  (grades 0, 2, ...)
odd(mv)         # 2e₁      (grades 1, 3, ...)

scalar(mv)      # 3.0 (float)
```

`even_grades` / `odd_grades` are the canonical names; `even` / `odd` are short aliases. You can also use `grade()` directly:

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
```

## Dual

```python
dual(e1 ^ e2)   # e₃  (in 3D Euclidean)
undual(e3)       # e₁₂
```

## Predicates

```python
is_scalar(alg.scalar(5))    # True
is_vector(e1 + e2)          # True
is_bivector(e1 ^ e2)        # True
is_even(1 + (e1 ^ e2))     # True
is_rotor(R)                  # True (even-graded and R*~R = 1)
```

## Rotation Example

Rotate `e₁` by 90° in the `e₁e₂` plane:

```python
import numpy as np

theta = np.pi / 2
B = e1 ^ e2
R = alg.rotor_from_plane_angle(B, theta)

v_rotated = R * e1 * ~R    # sandwich product
print(v_rotated)            # e₂
```

Or manually:

```python
R = alg.scalar(np.cos(theta/2)) - np.sin(theta/2) * B
```

## Cross Product (3D)

In 3D Euclidean space, the cross product is the dual of the wedge:

```python
# e₁ × e₂ = dual(e₁ ∧ e₂) = e₃
cross = dual(e1 ^ e2)
print(cross)    # e₃
```

## Spacetime Algebra

```python
sta = Algebra((1, -1, -1, -1), names="gamma")
g0, g1, g2, g3 = sta.basis_vectors()

print(g0 * g0)      #  1   (timelike)
print(g1 * g1)      # -1   (spacelike)
print(g0 * g1)      # γ₀γ₁ (bivector)
print(sta.I)         # 𝑰
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

`str()` uses unicode, `repr()` uses ASCII:

```python
mv = 3 + 2*e1 - e3

str(mv)     # '3 + 2e₁ - e₃'
repr(mv)    # '3 + 2e1 - e3'
```

The pseudoscalar always displays as `I` / `𝑰`:

```python
print(alg.I)        # 𝑰
print(repr(alg.I))  # I
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
print(R * v * ~R)                    # RvR̃
print(grade(R * v * ~R, 1))          # ⟨RvR̃⟩₁
print(op(sym(e1, "a"), sym(e2, "b"))) # a∧b
print(dual(sym(e1, "v")))            # v⋆
print(norm(sym(e1, "v")))            # ‖v‖
print(unit(sym(e1, "v")))            # v̂
print(inverse(sym(e1, "v")))         # v⁻¹
print(reverse(sym(e1*e2, "R")))      # R̃
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
| Even grades | `even(A)` | `⟨A⟩₊` |
| Odd grades | `odd(A)` | `⟨A⟩₋` |
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
print(expr.latex())  # \langle R v \tilde{R} \rangle_{1}
```

In Jupyter notebooks, expressions render automatically via `_repr_latex_()`.

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
| Even grades | `even(A)` | `⟨A⟩₊` | `\langle A \rangle_{\text{even}}` |
| Odd grades | `odd(A)` | `⟨A⟩₋` | `\langle A \rangle_{\text{odd}}` |
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

## Aliases

Short names for experienced users, long names for readability:

```python
gp  ↔  geometric_product
op  ↔  wedge  ↔  outer_product
ip  ↔  inner_product
reverse  ↔  rev
unit  ↔  normalize  ↔  normalise
even_grades  ↔  even
odd_grades   ↔  odd
```

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
| `rotor_from_plane_angle(B, θ)` | Rotor for rotation by θ in plane B |

### `Multivector`

| Property | Description |
|---|---|
| `[k]` | Grade-k projection (`x[2]` = `grade(x, 2)`) |
| `.inv` | Inverse |
| `.dag` | Reverse (dagger) |
| `.sq` | Squared (geometric product with self) |
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
| `even(x)` | Even-grade components |
| `odd(x)` | Odd-grade components |
| `is_scalar(x)` | True if pure scalar |
| `is_vector(x)` | True if pure 1-vector |
| `is_bivector(x)` | True if pure 2-vector |
| `is_even(x)` | True if even-graded |
| `is_rotor(x)` | True if even and `x*~x = 1` |

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

200+ tests, 99% coverage. Tests include:
- Algebraic identity property tests (associativity, distributivity, reverse-product)
- Golden tests for Cl(2,0), Cl(3,0), Cl(1,3)
- Symbolic rendering and evaluation tests
- Edge cases and error handling

$$v$$

$v$

$$
v
$$

