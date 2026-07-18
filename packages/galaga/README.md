# galaga — Geometric Algebra for Python

A numeric geometric algebra library with a stable, programmer-first API.

- **Single dependency** — only NumPy. No framework lock-in, installs in seconds
- **Named functions are the contract** — `gp`, `op`, `grade`, `reverse`, `dual`, `inverse` never change meaning
- **Operators are sugar** — `*`, `^`, `|`, `~` are convenience only
- **No ambiguity** — every inner product variant has its own name
- **Unicode pretty-printing** — `3 + 2e₁ - e₃`, `γ₀γ₁`, `σₓσᵧ`
- **Symbolic expression trees** — write `grade(R * v * ~R, 1)` and see `⟨RvR̃⟩₁`
- **Naming and evaluation** — `.name("B")`, `.anon()`, `.symbolic()`, `.numeric()` mutate in-place; `.eval()` returns a copy
- **LaTeX-driven naming** — `.name(latex=r"\theta")` auto-derives unicode (θ) and ASCII (theta)

## Install

```bash
pip install galaga
```

## Quick Start

```python
from galaga import *

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
alg.basis_vectors()              # (e₁, e₂, e₃) — named + numeric
alg.basis_vectors(symbolic=True) # (e₁, e₂, e₃) — named + symbolic
alg.basis_blades(2)              # (e₁₂, e₁₃, e₂₃) — all grade-k blades
alg.locals()                     # {"e1": e₁, "e12": e₁₂, …} for locals().update()
alg.pseudoscalar()               # e₁₂₃ (also alg.I)
alg.identity            # scalar 1 (𝟙)
alg.scalar(5.0)         # 5
alg.vector([1, 2, 3])   # e₁ + 2e₂ + 3e₃
alg.blade("e12")        # e₁₂
alg.rotor(B, radians=θ) # rotor for rotation by θ in plane B
```

### Bulk Blade Access

```python
# Unpack specific grades
e1, e2, e3 = alg.basis_blades(1)          # same as basis_vectors()
e12, e13, e23 = alg.basis_blades(2)        # all bivectors

# Alternatively, inject all blades into local scope (notebooks / top-level scripts)
d = alg.locals(grades=[1, 2], symbolic=True)
locals().update(d)
print("Injected:", ", ".join(d))           # Injected: e1, e2, e3, e12, e13, e23
```

## Products

Every product has a definitive named function. Operators are optional shorthand.

| Operation | Function | Operator | Unicode |
|---|---|---|---|
| Geometric product | `gp(a, b)` | `a * b` | juxtaposition |
| Outer (wedge) product | `op(a, b)` | `a ^ b` | `∧` |
| Left contraction | `left_contraction(a, b)` | | `⌋` |
| Right contraction | `right_contraction(a, b)` | | `⌊` |
| Doran–Lasenby inner | `doran_lasenby_inner(a, b)` | `a \| b` | `·` |
| Hestenes inner | `hestenes_inner(a, b)` | | `·` |
| Scalar product | `scalar_product(a, b)` | | `∗` |
| Commutator | `commutator(a, b)` | | `[a, b]` |
| Anticommutator | `anticommutator(a, b)` | | `{a, b}` |
| Lie bracket | `lie_bracket(a, b)` | | `½[a, b]` |
| Jordan product | `jordan_product(a, b)` | | `½{a, b}` |

```python
e1, e2, e3 = alg.basis_vectors()

gp(e1, e2)                  # e₁₂
op(e1, e2)                  # e₁₂
left_contraction(e1, e1^e2) # e₂
scalar_product(e1, e1)      # 1

# Operator shorthand
e1 * e2     # geometric product
e1 ^ e2     # outer product
e1 | (e1^e2)  # Doran–Lasenby inner product
```

### Unified Inner Product

The `ip` function dispatches to the specific inner product you want — no ambiguity.

```python
ip(e1, e1)                            # Doran–Lasenby (default)
ip(e1, e1, mode="hestenes")           # Hestenes
ip(e1, e1 ^ e2, mode="left")          # left contraction
ip(e1 ^ e2, e2, mode="right")         # right contraction
ip(e1, e2, mode="scalar")             # scalar product
```

### When Do the Inner Products Differ?

For vector-on-vector they all agree. The differences show up with mixed grades:

| Expression | Left contraction | Right contraction | Hestenes | Doran–Lasenby |
|---|---|---|---|---|
| `vector, bivector` | `e₂` (grade 2−1=1) | `0` (1−2 < 0) | `e₂` (\|1−2\|=1) | `e₂` (\|1−2\|=1) |
| `bivector, vector` | `0` (1−2 < 0) | `e₂` (grade 2−1=1) | `-e₂` (\|2−1\|=1) | `-e₂` (\|2−1\|=1) |
| `scalar, vector` | `3e₁` (passes through) | `0` (0−1 < 0) | `0` (kills scalars) | `3e₁` (\|0−1\|=1) |
| `vector, scalar` | `0` (1−0 < 0) | `3e₁` (passes through) | `0` (kills scalars) | `3e₁` (\|1−0\|=1) |

```python
e12 = e1 ^ e2

left_contraction(e1, e12)      # e₂  — vector "removes" from bivector
left_contraction(e12, e1)      # 0   — can't remove higher from lower

right_contraction(e12, e1)     # e₂  — mirror of left contraction
right_contraction(e1, e12)     # 0

hestenes_inner(e1, e12)        # e₂  — uses |grade difference|
hestenes_inner(e12, e1)        # -e₂ — nonzero both ways (unlike left/right)
hestenes_inner(cl3.scalar(3), e1)  # 0 — always zero if either is scalar

doran_lasenby_inner(e1, e12)        # e₂  — same as Hestenes for non-scalars
doran_lasenby_inner(cl3.scalar(3), e1)  # 3e₁ — includes scalars (unlike Hestenes)
```

**Rule of thumb:** Doran–Lasenby (the `|` operator) is the most general — it
includes scalars. Hestenes is the same but kills scalars. Left contraction is
the most common in GA literature.

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

mv.scalar_part   # 3.0 (float)
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
v.sq            # gp(v, v)    — squared (also v**2)
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
sta = Algebra(1, 3, blades=b_sta())
g0, g1, g2, g3 = sta.basis_vectors()

print(g0 * g0)      #  1   (timelike)
print(g1 * g1)      # -1   (spacelike)
print(g0 * g1)      # γ₀γ₁ (bivector)
print(sta.I)        # 𝑰
```

## Basis Naming

Control how basis blades display via the `blades=` parameter and convention factories.

### Convention Factories

```python
from galaga import Algebra, b_default, b_gamma, b_sigma, b_sigma_xyz, b_pga, b_sta, b_cga, b_complex, b_quaternion

# Default: e₁, e₂, e₃ — compact subscripts (e₁₂ for bivectors)
alg = Algebra(3)

# Gamma: γ₀, γ₁, γ₂, γ₃
sta = Algebra(1, 3, blades=b_gamma())

# STA with sigma bivector aliases, pseudoscalar → I
sta = Algebra(1, 3, blades=b_sta(sigmas=True, pss="I"))

# Sigma (numbered): σ₁, σ₂, σ₃
pauli = Algebra(3, blades=b_sigma())

# Sigma (xyz): σₓ, σᵧ, σz
pauli = Algebra(3, blades=b_sigma_xyz())

# PGA: 0-based, compact, pseudoscalar → I
pga = Algebra(3, 0, 1, blades=b_pga())

# CGA: orthogonal e₁…e₃, e₊, e₋ frame
cga = Algebra(4, 1, blades=b_cga())

# Complex numbers: Cl(2,0) with i = e₁₂
alg_c = Algebra(2, blades=b_complex())

# Quaternions: Cl(3,0) with i, j, k bivectors
alg_q = Algebra(3, blades=b_quaternion())
```

All factories accept `pss=` to name the pseudoscalar, `style=` to choose
blade display, and `overrides=` for per-blade customisation.

### Blade Styles

```python
Algebra(3, blades=b_default(style="compact"))      # e₁₂   (default)
Algebra(3, blades=b_default(style="juxtapose"))     # e₁e₂
Algebra(3, blades=b_default(style="wedge"))         # e₁∧e₂
```

### Custom Names and Overrides

```python
# Custom vector names
alg = Algebra((1, 1, 1), blades=BladeConvention(
    vector_names=[("a", "𝐚", "𝐚"), ("b", "𝐛", "𝐛"), ("c", "𝐜", "𝐜")]
))

# Override specific blades using metric-role keys
alg = Algebra(3, blades=b_default(overrides={
    "+1+2": "B",     # e₁₂ → B
    "pss":  "I",     # pseudoscalar → I
}))
```

### Blade Lookup

```python
alg.blade("e12")         # prefix + digits
alg.blade("+1+2")        # metric-role key
alg.blade("pss")         # pseudoscalar shorthand
alg.blade("I")           # display name match (if overridden)
```

### Post-hoc Renaming

```python
alg.get_basis_blade("+1+2").rename("B")                    # all formats
alg.get_basis_blade("+1+2").rename(("B12", "B₁₂", r"B_{12}"))  # per-format
```

## Display

`str()` and `repr()` both use unicode by default:

```python
mv = 3 + 2*e1 - e3

str(mv)     # '3 + 2e₁ - e₃'
repr(mv)    # '3 + 2e₁ - e₃'
```

The pseudoscalar always displays as `I` / `𝑰`:

```python
print(alg.I)        # 𝑰
print(repr(alg.I))  # 𝑰  (repr_unicode=True by default)
```

Coefficients of ±1 are suppressed: `e₁₂` not `1e₁₂`, `-e₃` not `-1e₃`.

## Symbolic Expressions

Name multivectors and build expression trees that render as mathematical notation.

### Naming and Evaluation

Any multivector can be named and made symbolic with `.name()`.
All configuration methods (`.name()`, `.anon()`, `.symbolic()`, `.numeric()`)
**mutate in-place** and return `self`. Only `.eval()` returns a new copy.

```python
alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

B = (e1 ^ e2).name("B")   # mutates, sets lazy
print(B)              # B
print(B.anon())       # e₁₂  (name removed in-place)

B.name("B")           # re-name it
print(B.eval())       # e₁₂  (new copy, B unchanged)
```

#### LaTeX-driven naming

Pass `latex=` and unicode/ASCII are derived automatically:

```python
theta = alg.scalar(0.5).name(latex=r"\theta")
# unicode: θ, ascii: theta, latex: \theta — all auto-derived

F = (e1 ^ e2).name(latex=r"\mathbf{F}")
# unicode: 𝐅, ascii: F — derived from \mathbf{F}

n = e1.name(latex=r"\hat{n}")
# unicode: n̂, ascii: hat_n — combining accent
```

The `label` parameter is optional when `latex` is provided. User-supplied
`unicode=` and `ascii=` always take precedence over auto-derivation.

Naming and evaluation are orthogonal axes:

| | **Anonymous** | **Named** |
|---|---|---|
| **Eager** | `e1 + e2` → `e₁ + e₂` | `e1` → `e₁` (basis blades) |
| **Lazy** | `B.anon()` → expr tree | `B = (e1^e2).name("B")` → `B` |

### Lazy Propagation

When a lazy value participates in an operation, the result is lazy:

```python
B = (e1 ^ e2).name("B")
x = B + e3
print(x)              # B + e₃  (symbolic)
print(x.eval())       # e₁₂ + e₃  (concrete)
```

Names don't propagate — the result is anonymous but named operands appear by name in the expression tree.

### Symbolic Basis Blades

For fully symbolic workflows, use `symbolic=True` — every operation builds an
expression tree automatically:

```python
e1, e2, e3 = alg.basis_vectors(symbolic=True)

e1 ^ e2              # e₁∧e₂  (not e₁₂)
e1 * e2              # e₁e₂
3 * e1 + e2          # 3e₁ + e₂
(e1 ^ e2).eval()     # e₁₂  (concrete when you need it)
```

Division renders as fractions, `exp()` renders symbolically:

```python
theta = alg.scalar(0.5).name("θ")
B = (e1 ^ e2).name("B")
print(-B * theta / 2)     # -Bθ/2
print(exp(-B * theta / 2))  # exp(-Bθ/2)
```

### sym() Compatibility

`sym()` still works as a convenience alias. Unlike `.name()`, it **copies**
the original (does not mutate):

```python
from galaga import sym, grade, reverse, simplify

R = sym(e1 * e2, "R")   # copy of e1*e2, named "R"
v = sym(e1, "v")         # copy of e1, named "v" — e1 unchanged
v = sym(e1 + 2*e2, "v")
```

### Rendering

```python
R = (e1 * e2).name("R")
v = e1.name("v")

print(R * v * ~R)                     # RvR̃
print(grade(R * v * ~R, 1))           # ⟨RvR̃⟩₁
```

Full rendering table:

| Expression | Code | Renders as |
|---|---|---|
| Geometric product | `R * v * ~R` | `RvR̃` |
| Wedge | `a ^ b` | `a∧b` |
| Left contraction | `left_contraction(a, b)` | `a⌋b` |
| Right contraction | `right_contraction(a, b)` | `a⌊b` |
| Doran–Lasenby inner | `a \| b` | `A·B` |
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

Every lazy multivector can be evaluated to its concrete form:

```python
expr = grade(R * v * ~R, 1)
print(expr)          # ⟨RvR̃⟩₁
print(expr.eval())   # concrete Multivector result
```

`.eval()` returns a new anonymous numeric copy (non-mutating).
`.numeric()` mutates in-place.

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
v.latex()  # 3 e_{1} + 4 e_{2}
```

Full LaTeX rendering table:

| Expression | Code | Unicode | LaTeX |
|---|---|---|---|
| Geometric product | `R * v * ~R` | `RvR̃` | `R v \tilde{R}` |
| Wedge | `a ^ b` | `a∧b` | `a \wedge b` |
| Left contraction | `left_contraction(a, b)` | `a⌋b` | `a \;\lrcorner\; b` |
| Right contraction | `right_contraction(a, b)` | `a⌊b` | `a \;\llcorner\; b` |
| Doran–Lasenby inner | `a \| b` | `A·B` | `A \cdot B` |
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

The symbolic module provides drop-in replacements for all `galaga` functions. They detect lazy `Multivector` or `Expr` arguments and build trees; with plain eager `Multivector` arguments they delegate to the numeric core:

```python
from galaga import gp, grade, reverse

# With lazy/named MV → builds expression tree
R = (e1 * e2).name("R")
v = e1.name("v")
grade(R * v * ~R, 1)   # returns lazy Multivector with expr tree

# With eager MV → returns Multivector directly (zero overhead)
grade(e1 + e2, 1)      # returns eager Multivector
```

### Notation

Override how operations render — per-algebra:

```python
from galaga.notation import Notation, NotationRule

# Use Hestenes convention (reverse as dagger)
alg = Algebra((1, 1, 1), notation=Notation.hestenes())
e1, e2, _ = alg.basis_vectors(symbolic=True)
v = e1.name("v")
print(reverse(v))   # v†

# Or override individual rules
alg.notation.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
alg.notation.set("Dual", "unicode", NotationRule(kind="prefix", symbol="*"))
```

Built-in presets: `Notation.default()`, `Notation.hestenes()`, `Notation.doran_lasenby()`.

### Simplification

`simplify()` applies algebraic rewrite rules to expression trees:

```python
from galaga import sym, simplify, grade, norm, unit, inverse, op

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

`simplify()` accepts both `Expr` objects and lazy `Multivector` objects.

Grade is auto-detected from the multivector data, so `sym(e1, "v")` knows it's grade-1 and `sym(e1^e2, "B")` knows it's grade-2. Simplification runs to a fixed point, so cascading rules like `a - (-a) → a + a → 2a` resolve fully.

## Sandwich Product

The sandwich product `R x R̃` is common enough to deserve a shortcut:

```python
sandwich(R, e1)     # R * e1 * ~R
sw(R, e1)           # same thing, short alias
```

Works in the symbolic layer too:

```python
from galaga import sandwich

R = (alg.rotor(e1^e2, radians=np.pi/2)).name("R")
v = e1.name("v")
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
angle = np.arctan2(norm(a ^ b), (a | b).scalar_part)
```

Uses `atan2` for numerical stability (works even when vectors are nearly parallel or perpendicular). The wedge magnitude is `|a||b|sin θ`, the inner product is `|a||b|cos θ`.

### Check Parallel / Perpendicular

```python
parallel      = np.isclose(norm(a ^ b), 0)    # wedge vanishes
perpendicular = np.isclose((a | b).scalar_part, 0)  # inner product vanishes
```

### Compose Rotations

Rotors compose by geometric product — apply `R1` first, then `R2`:

```python
R_final = R2 * R1
v_rotated = R_final * v * ~R_final
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

### Hodge Star (Poincaré Dual)

The Hodge star `⋆x = xI⁻¹` uses the full geometric product instead of left contraction. It agrees with `dual()` on blades but differs on mixed-grade multivectors:

```python
def hodge_star(x):
    return x * inverse(x.algebra.pseudoscalar())
```

Like `dual()`, this requires an invertible pseudoscalar — it does not work in degenerate algebras (PGA). Use `complement()` there instead.

### Bivector Commutator Algebra

Bivectors form a Lie algebra under the commutator product:

```python
commutator(e1^e2, e2^e3)         # 2e₁₃ — unnormalised (ab - ba)
lie_bracket(e1^e2, e2^e3)        # e₁₃  — normalised ½(ab - ba)
```

The library provides both conventions:

| Function | Definition | Use case |
|---|---|---|
| `commutator(a, b)` | `ab - ba` | Raw commutator |
| `anticommutator(a, b)` | `ab + ba` | Raw anticommutator |
| `lie_bracket(a, b)` | `½(ab - ba)` | Lie algebra with clean structure constants |
| `jordan_product(a, b)` | `½(ab + ba)` | Symmetric product (equals inner product for vectors) |

In 3D Euclidean space, the Lie bracket of bivectors is isomorphic to the vector cross product. In Cl(1,3), it gives the Lorentz algebra.

## API Reference

### `Algebra(p_or_signature, q=0, r=0, *, blades=None, repr_unicode=True, notation=None, display=False)`

| Method / Property | Description |
|---|---|
| `basis_vectors(symbolic=False)` | Tuple of basis 1-vectors (symbolic=True for expression trees) |
| `pseudoscalar()` | Unit pseudoscalar |
| `I` | Unit pseudoscalar (property) |
| `identity` | Scalar 1 |
| `scalar(value)` | Scalar multivector |
| `vector(coeffs)` | 1-vector from list |
| `blade(name)` | Basis blade by name |
| `rotor(B, radians=, degrees=)` | Rotor for rotation in plane B |

### `Multivector`

| Property / Method | Description |
|---|---|
| `[k]` | Grade-k projection (`x[2]` = `grade(x, 2)`) |
| `.name(label, *, latex=, unicode=, ascii=)` | Set display name, set symbolic (mutates). `label` optional if `latex` given. |
| `.anon()` | Remove display name (mutates) |
| `.symbolic()` | Set symbolic mode (mutates) |
| `.numeric()` | Force numeric, strip name (mutates) |
| `.numeric("B")` | Force numeric, keep/set name (mutates) |
| `.eval()` | Return a new anonymous numeric copy (non-mutating) |
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
| `commutator(a, b)` | `ab - ba` |
| `anticommutator(a, b)` | `ab + ba` |
| `reverse(x)` | Reverse `x̃` |
| `involute(x)` | Grade involution `x̂` |
| `conjugate(x)` | Clifford conjugate `x̄` |
| `grade(x, k)` | Grade-k projection |
| `grades(x, ks)` | Multi-grade projection |
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

### `basics/` — Library Features

- **`naming_demo.py`** — `.name()`, `.anon()`, `.symbolic()`, `.numeric()`, real-world examples
- **`lazy_blades_demo.py`** — `basis_vectors(symbolic=True)` for fully symbolic workflows
- **`latex_naming_demo.py`** — LaTeX-driven naming across physics domains
- **`rendering_gallery.py`** — Visual gallery of all expression types with LaTeX rendering
- **`symbolic_demo.py`** — Expression trees, rendering, simplification, LaTeX output
- **`notation_demo.py`** — Notation presets and overrides
- **`dynamic_notation.py`** — Runtime notation switching
- **`latex_rewrites_demo.py`** — LaTeX rewrite pipeline demo
- **`galaga_marimo_demo.py`** — galaga-marimo t-string rendering demo
- **`blade_renaming.py`** — Basis blade renaming API
- **`blade_conventions.py`** — Blade convention gallery
- **`complex_and_quaternions.py`** — Complex numbers and quaternions via b_complex() and b_quaternion()

### `algebra/` — Core GA Operations

- **`exterior_algebra_intuition.py`** — Wedge-product intuition for oriented length, area, and volume
- **`inner_product_family.py`** — Comparison of the library's inner-product family
- **`commutator_lie_jordan.py`** — Symmetric and antisymmetric product splits
- **`involutions_and_grade_ops.py`** — Reverse, involute, conjugate, grade projection, even/odd
- **`norms_units_inverses.py`** — Norms, unitization, and inverses
- **`duality_and_complements.py`** — Metric duality vs combinatorial complements
- **`duality_and_subspaces.py`** — Duality with project/reject/reflect
- **`projectors_ga.py`** — Projection and rejection onto lines and planes
- **`exp_log_rotors.py`** — Rotor exponentials and logarithms
- **`rotor_demo.py`** — Rotor construction and rotation
- **`rotors_from_reflections.py`** — How rotors arise from reflection composition
- **`rotations_from_bivectors.py`** — Rotations from bivectors
- **`sandwich_products.py`** — Reflections and rotor sandwiches
- **`meets_joins_pga.py`** — Projective joins using PGA complement patterns

### `physics/` — Classical Physics

- **`special_relativity_lazy.py`** — Boosts, Minkowski diagrams, rapidity addition
- **`twin_paradox.py`** — Worldline and proper-time twin paradox
- **`relativistic_rocket_equation.py`** — Rapidity-first rocket equation with burn and coast
- **`one_g_travel_calculator.py`** — Relativistic 1g travel calculator
- **`thomas_precession.py`** — Non-collinear boost composition and Thomas-Wigner rotation
- **`kepler_orbits_ga.py`** — Kepler orbit and hodograph with orbital bivectors
- **`coupled_oscillators_modes.py`** — Normal modes in configuration-space GA
- **`planar_kinematics_lazy.py`** — Rotor-based planar rigid-body kinematics
- **`robot_kinematics_pga.py`** — Two-link planar robot with PGA-style motors
- **`polarisation.py`** — Polarisation states and Jones calculus in GA
- **`optics_polarisation_lazy.py`** — Polariser projectors and wave-plate rotors
- **`fresnel_polarisation_ga.py`** — Fresnel reflection with GA polarisation decomposition

### `quantum/` — Quantum Mechanics

- **`quantum_physics.py`** — Spin-½: Bloch sphere, measurement, Stern–Gerlach, Larmor precession
- **`qubits_and_superposition_ga.py`** — Qubits and superposition via rotors and Bloch vectors
- **`quantum_gates_ga.py`** — Single-qubit gates as Bloch-sphere rotations
- **`single_qubit_circuits_ga.py`** — Single-qubit circuit builder using rotor composition
- **`quantum_spin_lazy.py`** — Lazy Pauli-blade spin states and Stern-Gerlach probabilities
- **`measurement_and_interference_ga.py`** — Phase, recombination, and interference
- **`pauli_equation_toy.py`** — Spin precession as rotor evolution
- **`aharonov_bohm.py`** — Holonomy-first Aharonov-Bohm with internal phase rotors
- **`bell_states_and_correlations.py`** — Bell singlet correlations with geometric measurement axes
- **`quantum_teleportation_ga.py`** — Teleportation as Bloch-vector correction
- **`grover_search_ga.py`** — Grover search as repeated rotations in a search plane
- **`deutsch_jozsa_ga.py`** — Deutsch-Jozsa interference with oracle phases
- **`phase_estimation_geometry.py`** — Phase estimation as repeated rotor-angle accumulation

### `pga/` — Projective Geometric Algebra

- **`pga_demo.py`** — Cl(3,0,1): translations, reflections, motors, screw interpolation
- **`pga_geometry_constructions.py`** — Point-line-triangle constructions with lazy joins
- **`camera_geometry_pga.py`** — Pinhole camera geometry and image-plane intersections
- **`thin_lens_and_rays_pga.py`** — Thin-lens image construction with projective optics
- **`screw_motion_pga.py`** — Screw-motion combining rotation and axial drift

### `spacetime/` — Spacetime Algebra

- **`spacetime_algebra.py`** — Cl(1,3): boosts, rotations, EM field, Thomas–Wigner rotation
- **`pauli_matrices_vs_ga.py`** — Pauli matrices/spinors vs Cl(3,0) rotors/vectors
- **`dirac_matrices_vs_sta.py`** — Dirac gamma matrices vs STA boosts/vectors
- **`electromagnetism_lazy.py`** — Faraday bivector, invariants, boosted field components
- **`em_waves_sta.py`** — Plane-wave EM fields and null invariants
- **`maxwell_equations_sta.py`** — Maxwell's equations in compact STA form
- **`lorentz_force_sta.py`** — Lorentz-force motion in the STA field picture
- **`null_geometry_sta.py`** — Null vectors, light cones, and observer geometry

```bash
uv run marimo edit examples/quantum/quantum_physics.py
```

## Internals

- Basis blades are represented as **bitmasks** — `e₁ = 0b001`, `e₂ = 0b010`, `e₁₂ = 0b011`
- Multiplication tables are **precomputed** at algebra creation time
- Multivector coefficients are **dense NumPy arrays** of length `2ⁿ`
- The `Algebra` object is **immutable** after creation
- `Multivector` is lightweight: just an algebra reference + data array

## Testing

```bash
uv run pytest packages/galaga/tests/ -v                                    # run all tests
uv run pytest packages/galaga/tests/ --cov=galaga --cov-report=term        # with coverage
```

1600+ tests. Tests include:
- Algebraic identities (associativity, distributivity, reverse-of-product)
- Golden tests for Cl(2,0), Cl(3,0), Cl(1,3)
- All five inner products with mixed-grade cases where they diverge
- Exponential/logarithm roundtrips (Euclidean, hyperbolic, null)
- Projection/rejection complement property, reflection involution
- Symbolic rendering, evaluation, simplification rules
- LaTeX output for both `Multivector` and `Expr`
- Naming/evaluation semantics: `.name()`, `.anon()`, `.symbolic()`, `.numeric()`
- Symbolic propagation through all operators
- Symbolic basis blades: `basis_vectors(symbolic=True)`
- MV / MV division, ScalarDiv/Div/Exp expression nodes
- Precedence-aware rendering (93 dedicated tests)
- LaTeX symbol mapping (101 tests) and auto-derivation
- Small value display with explicit format specs
- All 10 spec use cases from the symbolic redesign
- Edge cases and error handling

## Documentation

### Architecture Decision Records (ADRs)

Design decisions are documented in `docs/adrs/`. Each ADR records the context,
decision, and consequences for a significant design choice. 59 ADRs covering
the symbolic layer, rendering pipeline, notation system, linting, packaging,
and more.

```bash
ls docs/adrs/
```

### Specifications

Formal rendering and formatting specs live in `docs/specs/`. Each spec defines
authoritative rules with decision tables and examples that map to tests.

| Spec | Description |
|---|---|
| SPEC-001 | LaTeX coefficient formatting and scientific notation |
| SPEC-002 | Precedence and parenthesisation rules |
| SPEC-003 | Notation system: kinds, dispatch, and override semantics |
| SPEC-004 | Display method: name/reveal/eval deduplication |
| SPEC-005 | Accent width selection (narrow vs wide) |
| SPEC-006 | Postfix wrapping: compound names, superscripts, fractions |
| SPEC-007 | Unicode coefficient formatting |
| SPEC-008 | Lazy/eager propagation rules |
| SPEC-009 | Expression tree rendering (SlashFrac, Frac, Sup interactions) |
| SPEC-010 | Blade naming and display system |
| SPEC-011 | Custom basis blade display ordering |

### Other Documentation

- `docs/RELEASE_PROCESS.md` — release workflow, PyPI publishing, custodianship
- `docs/PYREFLY_STATUS.md` — type checking status and remaining work
- `docs/DESIGN_DECISIONS.md` — high-level design summary
