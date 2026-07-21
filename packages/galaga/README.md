# Galaga — Geometric Algebra for Python

Galaga 2 is a numeric geometric-algebra library built on a native Gram-matrix
core. Its public API composes eager multivector values with optional immutable
expression provenance, configurable blade conventions, and shared ASCII,
Unicode, and LaTeX rendering.

- General symmetric Gram matrices, not only diagonal signatures.
- Long, unambiguous operation names as the primary mathematical API.
- Optional concise aliases such as `gp`, `op`, `rev`, and `sw`.
- Explicit inner products and contractions rather than one overloaded `ip`.
- Immutable names and expression provenance over eager numeric values.
- Presets that configure the metric, blade convention, notation, and model
  metadata together while still permitting component-level overrides.
- Thread- and async-safe scoped presentation changes.
- NumPy array conversion and checked scalar conversion.

## Install

```bash
pip install galaga
```

Galaga requires Python 3.11 or newer and NumPy. The optional
`galaga_marimo` package requires Python 3.14 because it uses t-strings.

## Quick start

```python
from galaga import Algebra, DisplayPolicy, norm, outer_product

alg = Algebra((1, 1, 1), display=DisplayPolicy("full"))
e1, e2, e3 = alg.basis_vectors(expr=True)

u = (2 * e1 + e2).named("u")
v = (0.5 * e1 + 1.8 * e2).named("v")
area = outer_product(u, v)

print(area)
print(area.latex())
print(norm(area))
```

The operators are conveniences over named operations:

```python
u * v  # geometric_product(u, v)
u ^ v  # outer_product(u, v)
u | v  # doran_lasenby_inner(u, v)
~u     # reverse(u)
```

## Constructing an algebra

Diagonal algebras retain the familiar call shapes:

```python
from galaga import Algebra

cl3 = Algebra(3)                       # Cl(3, 0)
sta = Algebra(1, 3)                    # Cl(1, 3)
pga = Algebra(3, 0, 1)                 # Cl(3, 0, 1)
ordered = Algebra((1, -1, -1, -1))    # explicit basis order
```

A full symmetric Gram matrix defines a non-orthogonal or native-null basis:

```python
import numpy as np
from galaga import Algebra

null_plane = Algebra(
    gram=np.array(
        [
            [0.0, -1.0],
            [-1.0, 0.0],
        ]
    )
)
```

Complete presets configure numeric and presentation choices together:

```python
from galaga import Algebra, p_cga, p_pga, p_rga, p_sta

sta = Algebra(config=p_sta("mostly-minus"))
pga = Algebra(config=p_pga(spatial_dim=3))
cga = Algebra(config=p_cga(spatial_dim=3, frame="null"))
rga = Algebra(config=p_rga(spatial_dim=3))
```

`config=` owns the whole algebra definition. The lower-level `presentation=`,
`blades=`, `notation=`, `local_names=`, `display_order=`, and `display=`
parameters permit deliberate overrides when constructing an algebra directly.

## Values, names, and expressions

Multivectors are eager and immutable. Naming and expression tracking return a
new wrapper without changing the coefficients or the original value:

```python
from galaga import Algebra, exp

alg = Algebra(3)
e1, e2, _ = alg.basis_vectors(expr=True)

theta = alg.scalar(0.6).named(r"\theta")
B = (e1 ^ e2).named("B")
R = exp(-theta * B / 2).named("R")

R.name       # immutable semantic Name
R.expr       # immutable expression provenance
R.numeric    # presentation-independent galaga.core.Multivector
R.data       # read-only coefficient array
```

Useful state transformations include:

```python
R.named("Q")       # replace the semantic name
R.without_name()   # retain expression provenance
R.with_expr()      # attach literal provenance if absent
R.without_expr()   # retain the eager value and name
```

Factories accept `expr=True` when the construction itself should participate
in a later expression tree:

```python
e1, e2, e3 = alg.basis_vectors(expr=True)
scalar = alg.scalar(2, expr=True)
vector = alg.vector([1, 2, 3], expr=True)
```

## Blades

`blade()` accepts configured labels, bitmasks, signed blade references, or an
existing signed unit blade. `blades()` is the ordered plural form:

```python
rga = Algebra(config=p_rga())
e1, e2, e3, e4 = rga.basis_vectors(expr=True)
e23, e31, e41, e42 = rga.blades(
    e2 ^ e3,
    e3 ^ e1,
    e4 ^ e1,
    e4 ^ e2,
    expr=True,
)
```

`alg.locals()` returns a read-only mapping for environments where bulk name
injection is appropriate. In reactive notebooks, explicit `blade()` or
`blades()` calls preserve dependency tracking more clearly.

## Product and contraction family

The long names are canonical:

| Family | Canonical operation |
|---|---|
| Clifford product | `geometric_product` |
| Exterior product | `outer_product` |
| Left and right contractions | `left_contraction`, `right_contraction` |
| Doran–Lasenby inner | `doran_lasenby_inner` |
| Hestenes inner | `hestenes_inner` |
| Metric inner | `metric_inner_product` |
| Scalar product | `scalar_product` |
| Lengyel antidot | `antidot_product` |
| Regressive product | `regressive_product` |
| Transwedge family | `transwedge`, `transwedge_antiproduct` |

There is deliberately no top-level `ip` or `inner_product`: these operations
disagree for mixed grades and scalar inputs. Choose the intended definition
explicitly, or define a local notation:

```python
from galaga import doran_lasenby_inner as ip
```

Variadic geometric and outer products lower left-to-right through their binary
catalog operation:

```python
from galaga import geometric_product, outer_product

geometric_product(a, b, c)
outer_product(e1, e2, e3)
```

Commutators and anticommutators are unscaled:

```python
commutator(a, b)            # ab - ba
anticommutator(a, b)        # ab + ba
half_commutator(a, b)       # (ab - ba) / 2
half_anticommutator(a, b)   # (ab + ba) / 2
lie_bracket(a, b)           # unscaled commutator
jordan_product(a, b)        # unscaled anticommutator
```

## Grades and scalar conversion

```python
from galaga import grade, grades, scalar_part

scalar_component = grade(value, 0)      # scalar multivector
selected = grades(value, [0, 2, 4])
coefficient = float(grade(value, 0))
same_coefficient = scalar_part(value)   # optional helper
```

`float(value)` succeeds only when the entire multivector is scalar. It never
silently discards non-scalar grades. NumPy conversion exposes the coefficient
array:

```python
coefficients = np.asarray(value)
```

## Rendering and presentation

`DisplayPolicy` chooses content independently from the target format:

```python
from galaga import Algebra, DisplayPolicy

alg = Algebra(3, display=DisplayPolicy(content="full"))
e1, e2, _ = alg.basis_vectors(expr=True)
x = (2 * e1 + e2).named("x")

x.display("full/latex")
x.display("expr/unicode")
x.display("value/ascii")
x.latex()
```

Persistent presentation changes return cheap algebra views sharing the same
numeric algebra. Scoped overrides use `ContextVar`, so they are isolated by
thread and asynchronous task:

```python
teaching_alg = alg.with_presentation(teaching_presentation)

with alg.use_presentation(teaching_presentation):
    print(x.latex())
```

## Numeric core and explicit facade namespace

The public package is an exact re-export of the facade objects:

```python
import galaga
import galaga.facade

assert galaga.Algebra is galaga.facade.Algebra
assert galaga.Multivector is galaga.facade.Multivector
```

Use `galaga.core` when presentation, names, and expression provenance are not
needed:

```python
from galaga.core import Algebra, geometric_product

numeric = Algebra(gram=[[1.0, 0.2], [0.2, 1.0]])
e1, e2 = numeric.basis_vectors()
result = geometric_product(e1, e2)
```

## Phase 8 legacy access

Galaga 1 remains deliberately available as a temporary migration and test
oracle during Phase 8:

```python
from galaga import legacy

old_alg = legacy.Algebra(3)
old_e1, old_e2, _ = old_alg.basis_vectors()
old_value = legacy.gp(old_e1, old_e2)
```

Legacy and Galaga 2 values are separate domains and must not be mixed. The
`galaga.legacy` namespace, including `galaga.legacy.render` and
`galaga.legacy.simplify`, is scheduled for removal with the old table engine
in Phase 9.

## More documentation

- [Numeric core](../../docs/core/README.md)
- [Galaga 2 implementation overview](../../docs/v2/README.md)
- [Presentation configuration](../../docs/v2/presentation-configuration.md)
- [Expression provenance](../../docs/v2/expression-provenance.md)
- [Rendering implementation](../../docs/v2/rendering-implementation.md)
- [Compatibility policy](../../docs/v2/compatibility-shims.md)
- [Core cutover plan](../../docs/v2/core-cutover-plan.md)

Executable examples live under [`examples/galaga_v2`](../../examples/galaga_v2),
[`examples/algebra`](../../examples/algebra), and the model-specific example
directories.
