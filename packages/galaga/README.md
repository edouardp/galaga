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
- Read-only coefficient access and checked scalar conversion.

## Install

For the Galaga 2 prerelease train:

```bash
python -m pip install --pre "galaga>=2.0.0a1,<3"
```

After stable `2.0.0` is published:

```bash
python -m pip install "galaga>=2,<3"
```

Galaga requires Python 3.11 or newer and NumPy. The optional
`galaga-anywidget` visualization package also supports Python 3.11, while
`galaga-marimo` requires Python 3.14 because it uses t-strings.

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
from galaga import Algebra, presets

sta = Algebra(config=presets.sta("mostly-minus"))
pga = Algebra(config=presets.pga(spatial_dim=3))
cga = Algebra(config=presets.cga(spatial_dim=3, frame="null"))
lengyel_cga = Algebra(config=presets.lengyel_cga())
rga = Algebra(config=presets.rga(spatial_dim=3))
```

`config=` owns the whole algebra definition. The lower-level `presentation=`,
`blades=`, `notation=`, `local_names=`, `display_order=`, and `display=`
parameters permit deliberate overrides when constructing an algebra directly.

The older `p_*` spellings remain available as compatibility names. New code
can select only a blade vocabulary when the metric is specified separately:

```python
sta = Algebra(1, 3, blades=presets.blades.sta())
named_sta = Algebra(3, 1, blades=presets.blades.sta(sigmas=True, pseudovectors=True))
```

Metric-aware STA names are derived from the algebra's actual ordered metric;
unsupported non-diagonal or non-unit metrics are rejected. A blade preset
changes names and signed aliases only—it does not change the Gram matrix or
install model metadata.

### Native-null conformal model

The conformal preset stores `eo` and `einf` as actual null basis vectors in a
non-diagonal Gram matrix. Attach the model-specific semantics explicitly:

```python
from galaga import Algebra, outer_product, p_cga
from galaga.cga import ConformalModel

algebra = Algebra(config=p_cga(spatial_dim=3))
cga = ConformalModel(algebra, expr=True)
expanded_cga = cga.with_expression_form("expanded")

a = cga.up((0, 0, 0))
b = cga.up((1, 0, 0))
line = outer_product(a, b, cga.infinity)

assert cga.carrier(cga.round_point((1, 2, 3))).homogeneous_grade() == 2

round_point = cga.round_point((3, 4, 0), radius_squared=4)
assert float(cga.center_norm(round_point)) == 5
assert float(cga.radius_norm(round_point)) == 2

# The same value can explain itself with compact CGA vocabulary or its formula.
compact = cga.carrier(round_point)
expanded = expanded_cga.carrier(round_point)
assert compact == expanded
```

The [native-null CGA guide](https://github.com/edouardp/galaga/blob/main/docs/cga/README.md)
covers round and flat
objects, operator/expanded expression forms,
`att`/`car`/`ccr`/`cen`/`con`/`par`, dual conventions, projection,
Eric Lengyel's ●/○/■/□ components and weighted norms, and transformation
recipes.

### Point-based rigid model

`p_rga()` selects Eric Lengyel's point-based interpretation of
`Cl(3, 0, 1)`. Attach `RigidModel` when coordinates, projective measurement,
projection, support, or validity constraints are needed:

```python
from galaga import Algebra, p_rga
from galaga.rga import RigidModel

algebra = Algebra(config=p_rga())
rga = RigidModel(algebra, expr=True)

p = rga.point((3, 4, 0)).named("P")
q = rga.point((1, 0, 0)).named("Q")
line = p ^ q

assert float(rga.bulk_norm(p)) == 5
assert rga.is_valid_line(line)
```

The [RGA guide](https://github.com/edouardp/galaga/blob/main/docs/rga-convention-layer.md)
covers the algebraic
convention layer, paired norms, homogeneous distance and angle, projections,
support, line/motor/flector constraints, transwedge correction, and the dual
relationship with plane-based PGA.

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

Generated conventions support compact, juxtaposed, and wedge blade products:

| Style | LaTeX example |
|---|---|
| `"compact"` | $e_{12}$ |
| `"juxtapose"` | $e_1 e_2$ |
| `"wedge"` | $e_1\wedge e_2$ |

Model-aware convention builders retain semantic roles while changing that
spelling. Their dimension argument is the model's spatial dimension, not the
total algebra dimension:

```python
from galaga import Algebra, null_cga_blade_convention, p_cga

cga = Algebra(
    config=p_cga(spatial_dim=3),
    blades=null_cga_blade_convention(3, style="juxtapose"),
)
```

This is a five-dimensional algebra whose pseudoscalar renders as
$e_1 e_2 e_3 e_o e_\infty$. The convention adds the origin and infinity
vectors to the three Euclidean vectors itself.

## Logarithms and geometric generators

`log(A)` is the real principal **algebra** logarithm, with no rotor
requirement. It accepts positive scalar multivectors, vector exponentials,
compound rotors and general mixed-grade inputs on its supported principal
branch. Singular inputs, the spectral branch cut, and unresolved numerical
cases raise rather than silently returning another branch or complex values.

Use `rotor_generator(R)` when the result must generate a path of rotors,
or `is_rotor_generator(B)` to check a candidate independently. The generator
operation validates the principal logarithm; it does not search alternative
branches. A valid algebra logarithm need not be a geometric generator, even
when its input is a rotor. The returned generator includes its full scale
and any half-angle, rather than just a normalized plane.

The [logarithms and generators notebook](../../examples/algebra/logarithms_and_generators.py)
teaches these distinctions with computed Gram matrices, branch-cut examples,
and an interactive comparison of algebraic and geometric paths to one rotor.
From a checkout, run `make run-marimo` and open
`algebra/logarithms_and_generators.py` in the gallery (Python 3.14).

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
silently discards non-scalar grades. The explicit `.data` property exposes the
read-only NumPy coefficient array:

```python
coefficients = value.data
```

Multivectors deliberately do not implement NumPy's array or ufunc protocols;
`np.asarray(value)` is not a coefficient conversion.

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

### Display the bilinear form

`Algebra.bilinear_form_table()` returns a notebook-ready Gram table with
basis labels on both axes:

```python
from galaga import Algebra
from galaga.presets import p_cga

cga = Algebra(config=p_cga(3))
table = cga.bilinear_form_table()
table  # Rich display in Marimo/Jupyter; print(table) gives an aligned text table.
```

LaTeX uses a labelled array with grey (`#bbbbbb`) exact zeros. Small nonzero
entries remain visible even when the multivector display policy would hide
them. `table.latex()` returns raw LaTeX without math delimiters.

In Python 3.14 Marimo notebooks, the table also works as a display-math block
in a dynamic Markdown template:

```python
import galaga_marimo as gm

gm.md(t"""The native bilinear form is:

{table}
""")
```

The table captures the current presentation, keeps native Gram order, and
includes any sign needed to identify each native basis vector correctly.
For numeric entries use `cga.gram`. See the executable
[CGA Gram notebook](../../examples/matrix/cga_via_gram_matrix.py) and the
[presentation guide](../../docs/v2/presentation-configuration.md#labelled-bilinear-form-tables).

### Display wedge products

`Algebra.wedge_product_table()` uses the same rich-display protocol, with
a wedge in the corner and **row blade wedged with column blade** in each
cell:

```python
cga.wedge_product_table()                        # Native basis vectors only.
cga.wedge_product_table(color=True)              # Colour nonzero results by grade.
cga.wedge_product_table(full=True, colour=True)   # All blades, including scalar 1.
```

`color` and `colour` are aliases: either being `True` enables colouring.
All three flags default to `False` and require booleans. Zeros always stay
grey; ASCII and Unicode remain uncoloured. A stable eight-colour palette
is indexed by grade, repeating for grades above seven.

Full tables begin with `1`, then list every native exterior blade by grade
and bitmask, with signed convention names preserved. Unlike the Gram
matrix, wedge products do not depend on the metric. A full table has
`4**n` cells: 3D CGA gives a 32-by-32 table. For a smaller teaching example:

```python
Algebra(3).wedge_product_table(full=True, colour=True)  # An 8-by-8 table.
```

## Public API and numeric core

Import application APIs from `galaga`. Internally, those public objects are
owned by the composition facade:

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

## Legacy engine removed

The Galaga 1 table engine and its temporary `galaga.legacy` namespace no
longer ship. Use the public `galaga` API or `galaga.core` for numeric-only
work. Old `expr`, `symbolic_core`, `notation` and `latex_*` implementation
paths are removed too; their replacements are `galaga.expression`,
`galaga.presentation`, `galaga.rendering` and `galaga.names`.

Historical regression evidence remains in the repository, not in a second
installed engine. See the
[migration guide](https://github.com/edouardp/galaga/blob/main/docs/v2/migration-guide.md)
for explicit naming, provenance and rendering replacements.

## More documentation

- [Documentation index](https://github.com/edouardp/galaga/blob/main/docs/README.md)
- [Galaga 1 to 2 migration guide](https://github.com/edouardp/galaga/blob/main/docs/v2/migration-guide.md)
- [Numeric core](https://github.com/edouardp/galaga/blob/main/docs/core/README.md)
- [Galaga 2 implementation overview](https://github.com/edouardp/galaga/blob/main/docs/v2/README.md)
- [Native-null CGA](https://github.com/edouardp/galaga/blob/main/docs/cga/README.md)
- [Rigid Geometric Algebra](https://github.com/edouardp/galaga/blob/main/docs/rga-convention-layer.md)
- [Release process](https://github.com/edouardp/galaga/blob/main/docs/RELEASE_PROCESS.md)

Executable examples live in the
[repository gallery](https://github.com/edouardp/galaga/tree/main/examples).
