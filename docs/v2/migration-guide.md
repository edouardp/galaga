# Migrating from Galaga 1 to Galaga 2

Galaga 2 keeps the familiar top-level import but replaces the numeric engine
with the Gram-matrix implementation. Most arithmetic expressions still read
naturally; construction, naming, expression tracking, and ambiguous operation
names are deliberately more explicit.

## Install the prerelease

Until stable `2.0.0` is published, opt into prereleases:

```bash
python -m pip install --pre "galaga>=2.0.0a1,<3"
```

For a reproducible report or notebook, pin the exact release being evaluated:

```bash
python -m pip install "galaga==2.0.0a1"
```

Galaga, `galaga-matrix`, and `galaga-mermaid` support Python 3.11 and later.
`galaga-marimo` requires Python 3.14 because its API uses t-strings.

## Use the top-level API

Application code imports Galaga 2 directly:

```python
from galaga import Algebra, geometric_product, outer_product
```

`galaga.facade` is the explicit architectural namespace that owns those public
objects, but ordinary user code does not need to import it. `galaga.core` is
the lower-level choice for presentation-free numeric work.

During the prerelease migration only, Galaga 1 is available as an isolated
oracle under `galaga.legacy`. Legacy and Galaga 2 values do not interoperate.
The legacy engine and migration-only bridge paths are scheduled for removal
before stable `2.0.0`.

## Prefer canonical operation names

Long names are the primary mathematical API:

| Galaga 1 spelling | Galaga 2 spelling |
|---|---|
| `gp(a, b)` | `geometric_product(a, b)` |
| `op(a, b)` | `outer_product(a, b)` |
| `involute(a)` | `grade_involution(a)` |
| `rev(a)` | `reverse(a)` |
| `sw(r, x)` | `sandwich(r, x)` |

Established short forms such as `gp`, `op`, `rev`, and `sw` remain exact
aliases where they are unambiguous. They are conveniences, not separate
implementations. Project-local notation can always use an import alias:

```python
from galaga import doran_lasenby_inner as ip
```

There is no unqualified `inner_product` or `ip` export because the Doran–
Lasenby, Hestenes, metric, scalar, and contraction operations disagree outside
restricted inputs.

## Account for corrected bracket scaling

Galaga 2 makes the factor of one half visible:

```python
commutator(a, b)             # ab - ba
anticommutator(a, b)         # ab + ba
lie_bracket(a, b)            # ab - ba
jordan_product(a, b)         # ab + ba
half_commutator(a, b)        # (ab - ba) / 2
half_anticommutator(a, b)    # (ab + ba) / 2
```

Code that relied on Galaga 1's scaled `commutator` or `anticommutator` must
select the corresponding `half_...` operation explicitly.

## Replace mutable naming with immutable values

Galaga 2 values are eager and immutable. Replace Galaga 1's mutating
configuration calls:

```python
# Galaga 1
v = value.name("v")
e1, e2, e3 = algebra.basis_vectors(symbolic=True)

# Galaga 2
v = value.named("v")
e1, e2, e3 = algebra.basis_vectors(expr=True)
```

`named()`, `unnamed()`, `with_expr()`, and `without_expr()` return new
facade values. Numeric coefficients are always computed eagerly; `expr=True`
adds optional provenance rather than enabling deferred symbolic arithmetic.

## Construct metrics and models explicitly

Signatures remain concise:

```python
euclidean = Algebra(3)
spacetime = Algebra(1, 3)
ordered = Algebra((1, -1, -1, -1))
```

Use `gram=` for a general real symmetric metric and `config=` for a complete
preset:

```python
from galaga import Algebra, p_cga, p_pga, p_rga, p_sta

sta = Algebra(config=p_sta("mostly-minus"))
pga = Algebra(config=p_pga(spatial_dim=3))
cga = Algebra(config=p_cga(spatial_dim=3))
rga = Algebra(config=p_rga(spatial_dim=3))
```

`spatial_dim` counts the Euclidean model dimensions, not the algebra's total
number of basis vectors. Thus `p_cga(spatial_dim=3)` and
`null_cga_blade_convention(3)` both describe a five-dimensional algebra:
$e_1,e_2,e_3,e_o,e_\infty$.

Model-specific geometry is attached explicitly:

```python
from galaga.cga import ConformalModel
from galaga.rga import RigidModel

cga_model = ConformalModel(cga, expr=True)
rga_model = RigidModel(rga, expr=True)
```

## Configure presentation independently

Presets provide coherent defaults, while constructor overrides can replace one
presentation component:

```python
from galaga import DisplayPolicy, null_cga_blade_convention

cga = Algebra(
    config=p_cga(spatial_dim=3),
    blades=null_cga_blade_convention(3, style="juxtapose"),
    display=DisplayPolicy(content="full"),
)
```

The three generated blade styles are:

| Style | Example |
|---|---|
| `"compact"` | $e_{12}$ |
| `"juxtapose"` | $e_1 e_2$ |
| `"wedge"` | $e_1\wedge e_2$ |

The native-null CGA pseudoscalar in the example renders as
$e_1 e_2 e_3 e_o e_\infty$. Changing blade presentation does not change the
Gram matrix, model roles, or coefficients.

Temporary teaching changes are context-local and safe across threads and
asynchronous tasks:

```python
with algebra.use_presentation(teaching_presentation):
    display(value)
```

## Use checked conversions

`float(value)` checks that nonscalar coefficients are within the grade
inspection tolerance (currently `1e-12`). It is not an exact scalarhood test:

```python
coefficient = float(value)              # scalar within the inspection tolerance
grade_zero = grade(value, 0)             # scalar multivector
scalar_coefficient = float(grade_zero)
same = scalar_part(value)                # optional grade-zero helper
```

`value.data` exposes the read-only NumPy coefficient array. Multivectors do not
implement `__array__`, `__array_ufunc__`, or `__array_function__`, so
`np.asarray(value)` is deliberately not a coefficient conversion.

## Use exact equality and compatible keys

`==` compares coefficients exactly within the same algebra object; use
`almost_equal` when a numerical tolerance is intended. Positive and negative
zero compare and hash alike, but tiny nonzero coefficients remain significant.
Names, presentation, and expression tracking do not affect equality or hashes.

An exactly scalar multivector compares and hashes like an equal real number,
so either can look up the same dictionary entry. This check does not use the
tolerance allowed by `float(value)`:

```python
algebra = Algebra(2)
assert {algebra.identity: "hit"}[1] == "hit"
assert {1: "hit"}[algebra.identity] == "hit"
assert algebra.multivector([1.0, 1e-14, 0.0, 0.0]) != 1
assert algebra.scalar(2**53) != 2**53 + 1
```

Construction still stores `float64` coefficients, potentially rounding its
input. Comparison does not round the other operand to force a match: stored
`0.1` is not equal to exact `Fraction(1, 10)`, and huge integers, NaN, or
infinities compare unequal without raising. Python and NumPy numeric scalar
comparisons preserve their actual values, including narrower or wider NumPy
floating-point precision.

Algebra identity remains part of multivector equality, even for scalars.
Consequently, scalars from different algebras can each equal `1` while being
unequal to each other. Mixing those values and native numeric keys can make
deduplication depend on insertion order; qualify keys explicitly as
`(algebra, value)` when algebra scope matters. See
[ADR-095](../adrs/095-exact-numeric-equality-and-compatible-hashes.md).

## Validate the migration

Run application tests against the top-level API, not against
`galaga.facade` merely to prove that the new implementation was selected.
Useful migration assertions include:

- exact numeric equality where the old suite used implicit tolerances;
- `almost_equal` where approximation is intended;
- explicit expected inner-product variants;
- exact rendering contracts for presentation-sensitive notebooks; and
- clean-environment wheel installation without repository path injection.

The exhaustive implementation ledger remains in the
[public API migration matrix](public-api-migration-matrix.md). It is a
maintainer reference; this guide is the user-facing migration path.
