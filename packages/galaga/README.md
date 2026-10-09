# Galaga — Geometric Algebra for Python

Galaga 2 is a numeric geometric-algebra library for calculations and teaching.
Build an algebra from a signature or a full Gram matrix, compute with immutable
multivectors, and display the same calculation as values, named expressions,
or LaTeX. Expression tracking records how an eagerly computed value was
obtained; it is not a deferred symbolic algebra system.

- Real symmetric metrics, including nonorthogonal, indefinite and degenerate
  algebras, with native-null conformal bases.
- Explicit geometric, exterior, inner and regressive products; checked
  inverses, exponentials, principal logarithms and rotor generators.
- Composable presets for metrics, blade vocabulary and operation notation.
- Shared ASCII, Unicode and LaTeX rendering, including labelled Gram and
  wedge product tables for notebooks.
- Optional conformal and rigid model APIs, with separate companion packages
  for matrices, notebook Markdown, visualization and expression diagrams.

## Installation and status

Galaga 2 is in beta. To install the `2.0.0b1` release, opt into prereleases:

```bash
python -m pip install --pre "galaga>=2.0.0b1,<3"
```

For reproducible notebooks, pin the version you tested, for example
`galaga==2.0.0b1`. The core package requires **Python 3.11+ and NumPy**.
It does not require Marimo, Jupyter or a matrix package.

The examples below are self-contained Python snippets. Only the
`galaga_marimo` t-string example requires Python 3.14 and an optional package.
Documentation links target the `galaga_v2` branch while v2 is in development.
Existing v1 users should start with the [migration guide][migration].

## Quick start

```python
from galaga import Algebra, norm, outer_product, presets

alg = Algebra(config=presets.euclidean(3))
e1, e2, e3 = alg.basis_vectors(expr=True)

u = (2 * e1 + e2).named("u")
v = (e1 + 3 * e2).named("v")
area = outer_product(u, v).named("A")

print(area.display("value/unicode"))  # 5e₁₂
print(area.display("expr/unicode"))   # u ∧ v
print(area.display("full/latex"))     # Name = expression = value, as LaTeX.
assert area == 5 * (e1 ^ e2)
assert float(norm(area)) == 5
```

The wedge is an oriented area **bivector**, not a cross-product vector.
Names and expression history do not affect its numeric value.

Common operators are conveniences over named functions:

| Python | Named operation | Meaning |
|---|---|---|
| `a + b` | `add(a, b)` | Coefficient addition |
| `a - b` | `subtract(a, b)` | Coefficient subtraction |
| `-a` | `negate(a)` | Coefficient negation |
| `a * b` | `geometric_product(a, b)` | Clifford product |
| `a * s` | `scalar_multiply(a, s)` | Scaling by a real scalar |
| `a ^ b` | `outer_product(a, b)` | Exterior product |
| `a \| b` | `doran_lasenby_inner(a, b)` | Grade-difference inner product, including scalars |
| `~a` | `reverse(a)` | Reversion, not inversion |
| `a / b` | `divide(a, b)` | Right division, equivalent to `a * inverse(b)` |
| `a / s` | `scalar_divide(a, s)` | Direct coefficient division by a real scalar |
| `a ** k` | `power(a, k)` | Geometric power |

All named operations can be imported from `galaga`. In this table `a` and `b`
are multivectors and `s` is a real scalar. `add`, `subtract`, and `divide`
also accept a real scalar in either position, promoted into the other operand's
algebra; at least one operand must be a multivector. `divide(a, s)` uses
`scalar_divide(a, s)`. Multivector operands must belong to the same algebra.
Integer powers work in every metric; supported real powers in an all-null
exterior algebra are described below.

Parenthesize wedge expressions when mixing them with other Python operators.
Long names are the primary API; `gp`, `op`, `rev` and `sw` remain concise aliases.

## Define the metric

```python
from galaga import Algebra, metric_inner_product

euclidean = Algebra(3)                  # Cl(3, 0)
spacetime = Algebra(1, 3)                # Ordered squares: +1, -1, -1, -1.
projective = Algebra(3, 0, 1)            # One null vector, then three positive vectors.
time_first = Algebra((-1, 1, 1, 1))     # Explicit ordered signature.

oblique = Algebra(gram=[[2.0, 1.0], [1.0, 3.0]])
e1, e2 = oblique.basis_vectors()
assert float(metric_inner_product(e1, e2)) == oblique.gram[0, 1]
assert e1 * e2 == oblique.gram[0, 1] + (e1 ^ e2)
```

The defining identity is $e_i e_j + e_j e_i = 2G_{ij}$. Use `gram=` for
scaled or nonorthogonal metrics; ordered signatures contain only `+1`, `-1`
and `0`. `Algebra(p, q, r)` counts positive, negative, and null vectors,
but orders their basis squares as **null, positive, negative**. For example,
`Algebra(3, 0, 1)` has Gram diagonal `(0, 1, 1, 1)`. The complete
`presets.pga(spatial_dim=3)` preset instead uses `(1, 1, 1, 0)`, placing
its null vector last. Use `signature=` to choose a different explicit order.
Thus `Algebra(3, 1)` is **not** the time-first mostly-plus frame
`Algebra(signature=(-1, 1, 1, 1))`.

Coefficients are real `float64` values in the **native exterior basis**.
In a nonorthogonal basis, `e1 ^ e2` is a pure bivector while `e1 * e2` also
contains the Gram entry. Blade labels do not turn exterior products into
geometric products or perform a basis change.

For `n` basis vectors, a multivector stores `2**n` coefficients. `alg.n` is
the vector-space dimension and `alg.dim` is the coefficient count. Dense
storage and some operations grow exponentially; this is not a sparse or
arbitrary-precision engine.

## Choose presets or individual presentation components

Complete presets select the metric, blade convention, notation, local-name
policy, display order and optional model metadata together:

```python
from galaga import Algebra, presets

sta = Algebra(config=presets.sta("mostly-minus"))
pga = Algebra(config=presets.pga(spatial_dim=3))
cga = Algebra(config=presets.cga(spatial_dim=3, frame="null"))
rga = Algebra(config=presets.rga())
lengyel_cga = Algebra(config=presets.lengyel_cga())

# Inspect the immutable expanded configuration before constructing an algebra.
config = presets.euclidean(3).build()
euclidean = Algebra(config=config)
```

Native-null CGA now defaults to $(e_o,e_1,\ldots,e_n,e_\infty)$.
Use `presets.cga(n, basis_order="euclidean-first")` for the former native
coordinate order, including when loading old coefficient arrays.
This is a real basis choice, not a display override: higher-grade coordinates
must be converted as well as vector coordinates. The default has
$e_o\wedge I_E\wedge e_\infty=\mathrm{algebra.I}$; the compatibility order
retains the factor $(-1)^n$. Orthogonal and Lengyel CGA remain unchanged.
The [CGA guide][cga-guide] explains orientation and migration.

CGA presets display the native pseudoscalar as `I`. Opt into paired
`IE`/`IC` Python names (LaTeX $I_E$/$I_C$) with `model_pseudoscalars=True`
and name `eo ^ einf` as `E`
with `pseudoscalar_null=True`. An explicit `pss="J"` overrides the native top
label; `pss=None` uses automatic naming. These are naming choices only:
in Euclidean-first 3D, native `I` displays as $-I_C$ when model names are
selected. In 1D, the Euclidean vector remains `e1`, with `IE` lookup-only.

The complete factories are `euclidean`, `oblique_plane`, `sta`, `pga`, `cga`, `rga`,
`lengyel_cga`, `csta`, `complex`, `quaternion` and `exterior`. Complex and quaternion
presets describe even subalgebras of real Euclidean algebras, not complex
coefficient storage. Import `presets` to use these complete factories.

For two unit basis vectors separated by an angle, use
`Algebra(config=presets.oblique_plane(degrees=60))` or
`Algebra(config=presets.oblique_plane(angle=math.pi / 3))`. Specify exactly one:
`degrees` takes degrees and `angle` takes radians. The preset derives the Gram
matrix with `cos(angle)` off the diagonal; the angle must lie strictly between
zero and 180 degrees so the basis vectors remain independent.

For a metric-free exterior algebra on three generators, use
`Algebra(config=presets.exterior(dimension=3))`. The default dimension is 3;
`dimension` counts generators rather than spatial metric directions. Its Gram
matrix is zero, so geometric and exterior products of basis vectors agree.
For a multivector with positive scalar part, this also gives a finite
binomial expression for every real power: `x ** 0.5`, `x ** 1.5`, and
`x ** (-1 / 3)` are supported. The square root agrees with `sqrt(x)`.
Integer powers work in every algebra; noninteger `**` on other metrics
remains unsupported. The [exterior algebra lesson](../../examples/algebra/exterior_algebra_intuition.py)
compares these cases and their zero-scalar boundaries.

Presentation components compose with `|` using right-hand precedence:

```python
from galaga import Algebra, presets

notation = presets.notation.hestenes() | presets.notation.doran_lasenby()
recipe = presets.blades.euclidean(2) | notation | presets.display.override(coefficient_precision=4)
algebra = Algebra(config=presets.oblique_plane(degrees=60) | recipe)
```

The recipe changes presentation only. Notation unions merge tokens by operation
ID and rules by `(operation_id, target)`; an absent right-hand entry leaves the
left-hand entry intact. When a presentation slot appears twice, the right-hand
component replaces it; display overrides merge supplied fields instead.
Two complete algebra presets cannot be combined with
`|` because that would leave the numeric metric ambiguous.

Rename only the pseudoscalar without specifying the algebra dimension:

```python
from galaga import Algebra, Name, presets

complex_algebra = Algebra(0, 1, blades=presets.blades.pss("i"))
(i,) = complex_algebra.basis_vectors()
assert i * i == -complex_algebra.identity
assert (2 + 3 * i).display("value/ascii") == "2 + 3i"

# Retain the other blade labels in an existing convention.
sta = Algebra(config=presets.sta() | presets.blades.pss("J"))
custom = presets.blades.indexed(3, prefix="v") | presets.blades.pss(Name("J", "𝒥", r"\mathcal{J}"))
algebra = Algebra(3, blades=custom)
```

`presets.blades.pss(...)` preserves the top blade's orientation and changes
only its label. Python keys returned by `locals()` remain independently
configured. The same patch works with `algebra.with_blades(...)`,
`Presenter(blades=...)`, and presenter composition.

`presets.display.override(content="full", coefficient_precision=4)` changes
only those two choices. Omitted target and zero tolerance settings inherit from
the algebra or an earlier recipe. `DisplayPolicy(...)` remains available for
direct `display=` arguments and has the same sparse override behavior.

To change only the reverse symbol of a complete preset, use
`presets.notation.override(reverse="dagger")` or `reverse="tilde"`. For example,
`Algebra(config=presets.sta() | presets.notation.override(reverse="dagger"))`
keeps the preset's other notation rules. For target-specific layout choices, pass a `RenderRule` in a target map:

```python
from galaga import RenderRule, presets

notation = presets.notation.override(
    reverse="dagger",
    latex={"right_hodge_dual": RenderRule("superscript", symbol=r"\star")},
)
```

`rules={"dual": RenderRule("function", symbol="my_dual")}` changes a generic
rule; tuple keys such as `("dual", "latex")` select one target. The factory
also accepts `ascii=` and `unicode=` mappings. See the
[notation override notebook](../../examples/galaga_v2/notation_overrides.py).

Common layouts also accept compact strings as operation keywords:

```python
from galaga import presets

presets.notation.override(
    left_hodge_dual="prefix:star",
    half_commutator="wrapper:1/2[,]",
)
```

These set all three output targets. The same strings work in TOML notation
rules; full `RenderRule` values remain available for every layout option.

Select only blade names or operation notation when the metric is already known:

```python
from galaga import Algebra, presets

sta = Algebra(
    1, 3,
    blades=presets.blades.sta(sigmas=True, pseudovectors=True),
    notation=presets.notation.functional(),
)
g0, g1, g2, g3 = sta.basis_vectors()
assert sta.blade("s1") == g1 * g0

# config= defines the metric; presentation components can still override it.
cga = Algebra(
    config=presets.cga(3),
    notation=presets.notation.doran_lasenby(),
)
```

`config=` cannot be combined with numeric constructor arguments such as
`gram=` or `(p, q, r)`. It **can** be combined with `presentation=`, `blades=`,
`notation=`, `local_names=`, `display_order=` and `display=` overrides.

Blade recipes resolve against the target algebra. Metric-aware STA sigma and
pseudovector signs are derived from the actual ordered unit-diagonal metric;
unsupported metrics are rejected. CGA recipes validate the selected null or
orthogonal frame. Blade-only recipes do not install model metadata or change
the metric; arbitrary vocabulary choices do not guarantee model semantics.

`presets.notation` offers `default()`, `functional()`, `functional_short()`,
`doran_lasenby()`, `hestenes()`, `lengyel()`, `lengyel_rga()` and `override()`.
These change
rendering, not the operation called. See the [preset lesson][preset-lesson]
and [presentation guide][presentation] for lower-level customization.

## Save presentation preferences in TOML

Galaga reads `~/.config/galaga_python/config.toml` and any `.galaga_python.toml`
files from the filesystem root through the working directory when it creates
a facade `Algebra`. Closer files override earlier preferences. For example:

```toml
version = 1

[defaults.presentation]
notation = "@textbook"

[defaults.presentation.display]
coefficient_precision = 4

[notations.textbook.rules.right_hodge_dual.latex]
kind = "superscript"
symbol = '\star'
```

No explicit load call is needed for the default preferences:

```python
from galaga import Algebra

space = Algebra(3)  # reads the current TOML preferences automatically
```

Each new facade algebra reads the current files, so edits affect new algebras
without changing existing ones. Use `from galaga import config` and
`settings = config.load()` when selecting named presentations, presenters, or
algebras, or when inspecting the resolved files. A complete
`AlgebraConfig` is an exact snapshot and bypasses file defaults. See the
[user configuration guide](../../docs/v2/user-configuration-spec.md) for the
file schema and precedence rules.

Pass `user_config_files=False` to `Algebra(...)` or `Algebra.from_numeric(...)`
to skip user configuration files for one construction. The default is `True`.
To select a named algebra from the discovered files, use
`Algebra(config="@spacetime_article")`. The name must refer to an `algebras`
profile; this form requires `user_config_files=True` and reads the profile's
numeric definition.

## Values, blades, names and expressions

Multivector values display by grade, then lexicographically by numeric basis
indices (`e12, e13, e14, e23, ...`). Explicit preset conventions, including RGA
and quaternion order, are preserved. `DisplayOrder` controls presentation only;
coefficient storage and basis enumeration remain in native bitmask order.

```python
from galaga import Algebra, Name, exp
from galaga.expression import evaluate

alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors(expr=True)
B = (e1 ^ e2).named("B")
theta = alg.scalar(0.6).named(Name.from_latex(r"\theta"))
R = exp(-theta * B / 2).named("R")

print(R.display("full/latex"))
assert R.unnamed() == R.without_expr() == R

mass = alg.scalar(3).named("m")
square = mass**2
replayed = evaluate(square.expr, algebra=alg, environment={"m": 5})
assert float(replayed) == 25
assert float(square) == 9  # Rebinding does not change the original eager value.
```

`named()`, `unnamed()`, `with_expr()` and `without_expr()` return new
wrappers. Naming alone does not attach an expression to that value, but
operations on named or tracked operands record provenance. `expr=True` on
factories records construction provenance. Replay of symbols requires explicit
bindings; expression history does not make coefficients symbolic.

To opt in once, use `Algebra(..., expr=True)` (also with `config=`). The default
is `False`. Factories inherit it unless overridden, as do `ConformalModel` and
`RigidModel`; presentation-derived algebra views preserve it.

```python
from galaga import Algebra

tracked_alg = Algebra(2, expr=True)
a, b = tracked_alg.basis_vectors()
assert (a * b).expr is not None
plain = tracked_alg.vector([1, 2], expr=False)
assert (plain + 1).expr is None
```

`Name` holds ASCII, Unicode and LaTeX spellings. Use `Name.from_latex(...)`
for supported LaTeX-to-name conversion, or supply each spelling explicitly;
ordinary strings are literal and are not automatically parsed as LaTeX.

`blade()` accepts configured labels, native bitmasks, signed blade references
or existing signed unit blades. `blades()` is the ordered plural form:

```python
from galaga import Algebra, presets

alg = Algebra(config=presets.rga())
e1, e2, e3, e4 = alg.basis_vectors()
e23, e31 = alg.blades(e2 ^ e3, e3 ^ e1, expr=True)
assert e31 == alg.blade("e31") == -alg.blade(0b0101)

vector = alg.vector([1, 2, 3, 0])
assert vector == e1 + 2 * e2 + 3 * e3
```

`alg.locals()` returns a read-only mapping of configured local names. Prefer
explicit bindings in reactive notebooks so dependencies remain visible.
Presentation order never changes coefficient storage or native basis order.

### Grades, scalar conversion and floating-point comparisons

```python
from galaga import Algebra, grade, grades, scalar_part

alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()
value = 2 + e1 + 3 * (e1 ^ e2)
assert grade(value, 1) == e1
assert grades(value, [0, 2]) == 2 + 3 * (e1 ^ e2)
assert float(grade(value, 0)) == scalar_part(value) == 2

coefficients = value.data  # Read-only NumPy array, indexed by blade bitmask.
assert coefficients[0b0011] == 3
assert not coefficients.flags.writeable

a = alg.scalar(0.1) + alg.scalar(0.2)
b = alg.scalar(0.3)
assert a != b
assert a.almost_equal(b, atol=1e-12)

nearly_scalar = 2 + 1e-13 * e1
assert nearly_scalar != 2          # Equality sees every nonzero coefficient.
assert float(nearly_scalar) == 2   # Scalar conversion has a 1e-12 tolerance.
assert nearly_scalar.data[1] != 0  # Conversion does not change the stored value.
```

`float(value)` checks scalarity with an absolute coefficient tolerance of
`1e-12`: larger nonscalar components raise `TypeError`, but components at or
below that threshold can be ignored. It is **not an exact scalarity check**.
For deliberate scalar extraction from any multivector, use `grade(value, 0)`
for a scalar multivector or `scalar_part(value)` for its Python float
coefficient. To require exact scalarity, check that every entry of
`value.data[1:]` is zero before conversion.

Equality and hashing use exact stored values, not rounded display text or a
tolerance. Multivector comparisons require the same underlying numeric algebra;
presentation views share that identity, independently constructed algebras do
not. Use `.almost_equal(..., atol=...)` for absolute-tolerance comparisons
within one algebra. Display zero tolerance does not erase coefficients.

Multivectors do not implement NumPy array or ufunc protocols; use `.data`
explicitly rather than `np.asarray(value)` to obtain coefficients.

## Choose the intended inner product

There is deliberately no unqualified `ip` or `inner_product`. For homogeneous
grades `r` and `s`, the operations have different definitions and purposes:

| Operation | Definition | Typical intent |
|---|---|---|
| `scalar_product(A, B)` | Scalar part of `A * B` | Scalar coefficient of the geometric product |
| `metric_inner_product(A, B)` | Scalar part of `A * ~B` | Metric-induced pairing on exterior blades |
| `left_contraction(A, B)` | Grade `s-r` of `A * B` if `r <= s`, else zero | Remove the left grade from the right |
| `right_contraction(A, B)` | Grade `r-s` of `A * B` if `r >= s`, else zero | Remove the right grade from the left |
| `hestenes_inner(A, B)` | Grade `abs(r-s)` of `A * B` if both grades are nonzero | Symmetric grade selection excluding scalars |
| `doran_lasenby_inner(A, B)` | Grade `abs(r-s)` of `A * B`, including scalar grades | Symmetric grade selection including scalars |

Mixed-grade inputs are handled by summing over homogeneous pairs. “Symmetric
grade selection” does not mean the operation commutes. All six agree on vector
inputs, but a bivector's metric pairing differs from its scalar product:

```python
from galaga import Algebra, metric_inner_product, scalar_product

alg = Algebra(gram=[[2.0, 1.0], [1.0, 3.0]])
e1, e2 = alg.basis_vectors()
B = e1 ^ e2
G = alg.gram
determinant = G[0, 0] * G[1, 1] - G[0, 1] * G[1, 0]
assert float(metric_inner_product(B, B)) == determinant
assert float(scalar_product(B, B)) == -determinant
```

`norm2(A)` is `metric_inner_product(A, A)` and `norm(A)` is
`sqrt(abs(norm2(A)))`. These are metric quantities, not Euclidean norms of
the coefficient array: a nonzero null value can have zero norm. With named or
tracked inputs, `norm` returns a scalar multivector to retain provenance;
`float(norm(A))` obtains the magnitude in either case.

The [inner-products lesson][inner-lesson] explains the intent, scalar cases,
contraction signs and differing author conventions. Related APIs include
`regressive_product`, `antidot_product`, `transwedge` and
`transwedge_antiproduct`; see the [RGA guide][rga-guide] for their model context.

`geometric_product(a, b, c)` and `outer_product(a, b, c)` fold left-to-right.
`commutator` and `lie_bracket` return `ab - ba`; `anticommutator` and
`jordan_product` return `ab + ba`. Use `half_commutator` or
`half_anticommutator` when the definition includes a factor of one half.

## Rotors, logarithms and generators

```python
import math
from galaga import (
    Algebra, exp, is_rotor, is_rotor_generator, log, rotor_generator, sandwich,
)

alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()
generator = -(math.pi / 4) * (e1 ^ e2)  # Half-angle for a quarter-turn.
R = exp(generator)
assert is_rotor_generator(generator)
assert is_rotor(R)
assert sandwich(R, e1).almost_equal(e2)  # R * e1 * ~R
assert rotor_generator(R).almost_equal(generator)

# The mathematical logarithm is not restricted to rotors.
A = exp(0.3 * e1)
assert log(A).almost_equal(0.3 * e1)
```

`is_rotor` checks evenness, the full unit reverse product and preservation of
vectors under the reverse sandwich. Evenness alone is insufficient.
`sandwich(R, x)` uses reversion, not a substituted inverse or automatic
normalization. `R.dag` also means reverse; `.bar`, `.inv` and `.sq` mean
grade involution, inverse and geometric square respectively.

`log(A)` computes the **real principal algebra logarithm** where supported.
It accepts more than rotors, but not every invertible value: singular inputs,
the nonpositive-real spectral branch cut and unresolved numerical cases raise.
It does not complexify the algebra or search alternative logarithm branches.

`rotor_generator(R)` checks the rotor's principal logarithm as a geometric
generator; `is_rotor_generator(B)` checks a candidate independently. A valid
algebra logarithm need not generate a path of rotors, even if its exponential
is a rotor. The returned generator retains its full scale and any half-angle.
Explore the [logarithms and generators lesson][log-lesson].

## Rendering and notebook tables

Default `auto` content shows a deduplicated expression/name = value equality
when provenance or a name is present; unnamed, untracked values show just their
value. Enable tracking once for a notebook:

```python
from galaga import Algebra, presets

alg = Algebra(config=presets.euclidean(3), expr=True)
e1, e2, e3 = alg.basis_vectors()
result = (e1 + e2) ^ e3
result  # Rich display: (e₁ + e₂) ∧ e₃ = e₁₃ + e₂₃
```

Use `result.latex(content="value")` for just the result, or set
`display=DisplayPolicy(content="value")` on the algebra to keep provenance
without displaying it by default.

Rendering content (`auto`, `name`, `expr`, `value`, `full`) is independent of the
target (`ascii`, `unicode`, `latex`). Persistent presentation changes return
cheap algebra views; scoped changes are isolated by thread and async task:

```python
from galaga import Algebra, DisplayPolicy, presets

alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors(expr=True)
x = (e1 ^ e2).named("x")
teaching = alg.with_notation(presets.notation.functional()).with_display(
    DisplayPolicy(content="full")
)
assert teaching.numeric is alg.numeric
with alg.use_presentation(teaching.presentation):
    print(x.latex())
print(x.display("value/ascii"))
```

Rich notebook display works directly on multivectors and algebra tables.
Raw `.latex()` output has no math delimiters; the rich-display hook adds them.

To scope just operation notation, use `alg.use_notation(...)`. In Marimo,
explicitly render inside the scope so the selected notation is still active:

```python
import marimo as mo
from galaga import Algebra, metric_inner_product as mip, presets

alg = Algebra(config=presets.euclidean(3), expr=True)
e1, _, _ = alg.basis_vectors()

with alg.use_notation(presets.notation.lengyel()):
    mo.output.replace(mo.as_html(mip(e1, e1)))
```

This preserves other presentation settings. A multivector displayed after the
scope exits uses the restored notation, not the notation at calculation time.

For a reusable notebook display choice, use an immutable presenter. It captures
the selected rendering on a view while leaving the mathematical value unchanged:

```python
from galaga import Algebra, Presenter, metric_inner_product as mip, presets

alg = Algebra(config=presets.euclidean(3), expr=True)
e1, e2, e3 = alg.basis_vectors()

lengyel = presets.presenters.lengyel()
teaching = Presenter(content="full")
named = presets.presenters.short_functional() | presets.blades.indexed(3, prefix="v")

pairing_view = lengyel(mip(e1, e1))
result_view = teaching((e1 + e2) ^ e3)
named_view = named(e1 * e2)
pairing_view  # e₁ • e₁ = 1
result_view   # (e₁ + e₂) ∧ e₃ = e₁₃ + e₂₃
named_view.ascii()  # gp(v1, v2) = v12

next_value = pairing_view.value + e1  # views deliberately are not arithmetic
```

See [presentation configuration](../../docs/v2/presentation-configuration.md#reusable-presenters)
and the [reusable presenters lesson](../../examples/galaga_v2/reusable_presenters.py).

```python
from galaga import Algebra, presets

cga = Algebra(config=presets.cga(3))
gram_table = cga.bilinear_form_table()
print(gram_table)  # Aligned text with the default Unicode presentation.

vector_table = cga.wedge_product_table(colour=True)
full_table = Algebra(3).wedge_product_table(full=True, color=True)
gram_table  # Last line of a notebook cell: rich display. Try vector_table/full_table too.
```

`bilinear_form_table()` labels the native Gram matrix; numeric entries remain
available as `alg.gram`. Its `full=True` option shows the induced pairing
`metric_inner_product(A, B) = <A * ~B>_0` on every blade, not geometric-product
scalar extraction. An orthonormal Euclidean basis gives an identity table.
`wedge_product_table()` shows **row blade wedged with
column blade**, using basis vectors by default. For either table, `full=True` includes scalar
`1` and all exterior blades in the algebra's display order, including preset
and user overrides (grade-then-lexicographic by default). A full table has
`4**n` result cells: an 8-by-8 table for `Algebra(3)`, but 32-by-32 for 3D CGA.

Both are immutable presentation snapshots with signed native blade headings.
Exact zeros render in grey (`#bbbbbb`) in LaTeX; small nonzero entries are not
hidden by display tolerance. Either `color=True` or `colour=True` enables
wedge-result grade colouring; all flags default to `False` and require booleans.
Text output has no colour escapes. Unlike Gram entries, exterior products in
the fixed native basis are independent of the metric.

On **Python 3.14+**, install the helper with
`python -m pip install --pre "galaga-marimo>=2.0.0b1,<3"`, then interpolate
values and tables into dynamic Markdown:

```python
import galaga_marimo as gm
from galaga import Algebra, presets

alg = Algebra(config=presets.cga(3))
table = alg.bilinear_form_table()
document = gm.md(t"""The native bilinear form is:

{table}
""")
document
```

The table supplies its display-math block; do not add another `$$` wrapper
around `{table}`. The [bilinear and wedge lesson][table-lesson] teaches the
underlying geometry, including null vectors versus degenerate metrics.

## Geometric models

Import runtime geometry models from `galaga.models`. Each model validates the
preset's semantic roles and metric before interpreting objects. All models
provide `point()` and immutable `coordinates()`; classifications expose kind,
grade, simplicity, finiteness, representation, and model-specific properties.
See the [runtime model guide](../../docs/v2/runtime-geometry-models.md) for the
hierarchy, capability protocols, and conformal spacetime.

### Plane-based projective geometric algebra (PGA)

```python
from galaga import Algebra, presets
from galaga.models import PGAModel

pga = PGAModel(Algebra(config=presets.pga(3)))
p = pga.point((1, 2, 3))
q = pga.point((2, 2, 3))
line = pga.join(p, q)
plane = pga.plane((1, 0, 0, -1))  # x - 1 = 0
assert pga.meet(plane, p) == 0
assert pga.classify(line).kind == "line"
assert pga.bulk_part(line) + pga.weight_part(line) == line
```

PGA supports 2D and 3D. Its points have grade equal to the spatial dimension;
vectors are hyperplanes. `join` uses the antiwedge and `meet` the outer product.
Ideal points use `weight=0` and have no finite coordinates. PGA and RGA own
validated bulk/weight projections; these meanings do not apply to arbitrary
degenerate metrics.

### Native-null conformal geometric algebra (CGA)

The null-frame preset stores origin and infinity as actual null basis vectors,
with their mutual pairing in the Gram matrix. Attach `ConformalModel` for
lifting coordinates and working with geometric objects:

```python
from galaga import Algebra, outer_product, presets
from galaga.models import ConformalModel

alg = Algebra(config=presets.cga(spatial_dim=3, frame="null"))
cga = ConformalModel(alg, expr=True)
a = cga.up((0, 0, 0))
b = cga.up((1, 0, 0))
line = outer_product(a, b, cga.infinity)
assert line.homogeneous_grade() == 3

round_point = cga.round_point((3, 4, 0), radius_squared=4)
assert float(cga.center_norm(round_point)) == 5
assert float(cga.radius_norm(round_point)) == 2
expanded = cga.with_expression_form("expanded")
assert cga.carrier(round_point) == expanded.carrier(round_point)
```

The [CGA guide][cga-guide] covers rounds, flats, duality, projection,
transformations, weighted norms and operator versus expanded expression forms.
The [CGA Gram lesson][cga-gram] constructs the model from its bilinear form.
Here `spatial_dim=3` means five algebra basis vectors, not three.

### Point-based rigid geometric algebra (RGA)

`presets.rga()` selects Eric Lengyel's point-based interpretation of
`Cl(3, 0, 1)`. It shares a signature with plane-based PGA but has different
geometric meanings and conventions:

```python
from galaga import Algebra, presets
from galaga.models import RigidModel

alg = Algebra(config=presets.rga())
rga = RigidModel(alg, expr=True)
p = rga.point((3, 4, 0)).named("P")
q = rga.point((1, 0, 0)).named("Q")
line = p ^ q
assert float(rga.bulk_norm(p)) == 5
assert rga.is_valid_line(line)
```

The [RGA guide][rga-guide] covers paired norms, projective measurements,
projection, support, line/motor/flector constraints and the dual relationship
with plane-based PGA. Merely changing blade labels does not attach a model.

## Optional packages and learning resources

These are separate installations, not dependencies of the numeric package:

| Package | Python | Purpose |
|---|---|---|
| [galaga-matrix][matrix] | 3.11+ | Rich matrix representations, conversions and supported spinor/quaternion modes |
| [galaga-annotation][annotation] | 3.11+ | Semantic annotations and KaTeX callouts for expressions and matrices |
| [galaga-marimo][marimo] | 3.14+ | T-string Markdown interpolation and notebook helpers |
| [galaga-anywidget][anywidget] | 3.11+ | Interactive geometric visualizations |
| [galaga-mermaid][mermaid] | 3.11+ | Expression-tree diagrams |

For example, install `galaga-matrix` with
`python -m pip install --pre "galaga-matrix>=2.0.0b1,<3"`. Its left-regular
representation supports any symmetric Gram matrix; compact conversion is
explicit for numerically suitable general nondegenerate Gram metrics and
round-trips only when the selected representation is injective. Complex matrices
do not change the real coefficient domain of Galaga multivectors. See the
[matrix lessons][matrix-lessons].

From a repository checkout, `make run-marimo` opens the example gallery using
Python 3.14 and editable local companion packages. Start with
[construction][construction], [presets][preset-lesson],
[eager values and expressions][expression-lesson], [tables][table-lesson],
and [inner products][inner-lesson]. See the [documentation index][docs] for
the full collection. README Python snippets are executed by the test suite;
the maintained notebooks also have headless execution coverage.

## Numeric-only use

Application code normally imports from `galaga`. Use `galaga.core` when names,
expression provenance and rendering are not needed:

```python
from galaga.core import Algebra, geometric_product

alg = Algebra(gram=[[1.0, 0.2], [0.2, 1.0]])
e1, e2 = alg.basis_vectors()
result = geometric_product(e1, e2)
assert float(result.grade(0)) == alg.gram[0, 1]
```

The public facade composes these numeric values with presentation; it is not
a second engine. See the [numeric core guide][core] for its lower-level API.

Use `metric_apply(value)` and `antimetric_apply(value)` for algebra-level
metric maps. Geometric component decompositions belong to model methods such
as `cga.bulk_part(value)` or `pga.weight_part(value)`.

For older construction, naming, operation, and import patterns, follow the
[migration guide][migration].

[migration]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/v2/migration-guide.md
[presentation]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/v2/presentation-configuration.md
[preset-lesson]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/galaga_v2/preset_namespaces.py
[inner-lesson]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/galaga_v2/inner_products.py
[table-lesson]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/galaga_v2/bilinear_and_wedge_tables.py
[log-lesson]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/algebra/logarithms_and_generators.py
[cga-guide]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/cga/README.md
[rga-guide]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/rga-convention-layer.md
[cga-gram]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/matrix/cga_via_gram_matrix.py
[matrix]: https://github.com/edouardp/galaga/blob/galaga_v2/packages/galaga_matrix/README.md
[annotation]: https://github.com/edouardp/galaga/blob/galaga_v2/packages/galaga_annotation/README.md
[marimo]: https://github.com/edouardp/galaga/blob/galaga_v2/packages/galaga_marimo/README.md
[anywidget]: https://github.com/edouardp/galaga/blob/galaga_v2/packages/galaga_anywidget/README.md
[mermaid]: https://github.com/edouardp/galaga/blob/galaga_v2/packages/galaga_mermaid/README.md
[matrix-lessons]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/matrix/README.md
[construction]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/galaga_v2/algebra_construction.py
[expression-lesson]: https://github.com/edouardp/galaga/blob/galaga_v2/examples/galaga_v2/eager_values_and_expressions.py
[docs]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/README.md
[core]: https://github.com/edouardp/galaga/blob/galaga_v2/docs/core/README.md
