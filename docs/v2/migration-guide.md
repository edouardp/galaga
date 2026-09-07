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

The captured Galaga 1 implementation already had unscaled `commutator` and
`anticommutator`, but its `lie_bracket` and `jordan_product` included one
half. Migrate uses of those old half-scaled Lie/Jordan conventions to
`half_commutator` and `half_anticommutator` explicitly. Naming or tracking
does not change any v2 operation's scale.

The v2 simplifier also does not rewrite Jordan products to Hestenes inner.
For vectors, `half_anticommutator(a, b)` equals their metric pairing;
`jordan_product(a, b)` is twice that pairing. A saved symbolic call remains
valid when replayed with different grades, so simplification cannot assume
the original bindings are always vectors.

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

Naming alone does not create an expression on that value. An operation on a
named or tracked operand does create provenance, so a named scalar needs no
extra tracking call:

```python
from galaga import Algebra, scalar_sqrt
from galaga.expression import evaluate

algebra = Algebra(3)
mass = algebra.scalar(3).named("m")
momentum = algebra.scalar(4).named("p")
energy = scalar_sqrt(mass**2 + momentum**2).named("E")

assert mass.expr is None
assert float(energy) == 5
assert energy.display("expr/latex") == r"\sqrt{m^2 + p^2}"
assert energy.display("full/latex") == r"E \quad = \quad \sqrt{m^2 + p^2} \quad = \quad 5"
assert float(evaluate(energy.expr, algebra=algebra, environment={"m": 5, "p": 12})) == 13
assert float(energy) == 5  # replay does not mutate the eagerly computed value
```

Use explicit `expr` content when you want the derivation. Tracking alone does
not replace an anonymous value's concrete default display; a named value's
default display is a teaching equality. Standalone replay requires an
environment for symbols, rather than a legacy `.eval()` call with hidden
bindings.

Expression spelling is target-specific: ASCII is now ASCII-safe, Unicode
uses combining accents, and some parentheses and spacing differ from v1.
The conventional hat still serves both `unit` and `grade_involution`; use
`notation=Notation.functional()` with `Notation` imported from `galaga` when
those operations must be visibly distinguished. Their numeric meanings and
stored operation IDs are always separate. See
[ADR-098](../adrs/098-expression-contracts-outlive-legacy-provenance.md).

The curated unary shortcuts remain available as read-only properties:

| Shorthand | Equivalent function |
|---|---|
| `value.bar` | `grade_involution(value)` |
| `value.dag` | `reverse(value)` |
| `value.inv` | `inverse(value)` |
| `value.sq` | `squared(value)` |

They return eager facade values and preserve canonical operation provenance.
`bar` means grade involution, not Clifford conjugation; `dag` means reverse,
not a separate Hermitian-adjoint operation. `inv` uses the default controls
and raises the same error for a singular value; call `inverse(value, ...)`
for non-default controls. See
[ADR-099](../adrs/099-symbolic-contracts-and-curated-unary-properties.md).

## Derive a name from LaTeX explicitly

Replace v1's `value.name(latex=...)` with an immutable name:

```python
from galaga import Algebra, Name

value = Algebra(3).blade(1)
normal = value.named(Name.from_latex(r"\hat{n}"))
assert normal.display("name/ascii") == "hat_n"
assert normal.display("name/unicode") == "n\u0302"
assert normal.display("name/latex") == r"\hat{n}"
assert normal.numeric is value.numeric

# Nested TeX is outside the converter's grammar: supply explicit spellings.
theta = value.named(Name.from_latex(r"\hat{\theta}", ascii="hat_theta", unicode="θ̂"))
```

This is an opt-in lookup, not a general TeX parser. It retains the explicit
Greek/common-symbol/operator/relation/arrow mappings, five math fonts
(`\mathbf`, `\mathit`, `\mathcal`, `\mathfrak`, `\mathbb`) on one
ASCII Latin letter, bold/double-struck ASCII digits, and six accents
(`\hat`, `\tilde`, `\bar`, `\vec`, `\dot`, `\ddot`) on one ASCII
letter or digit. Lowercase script/double-struck mappings and Unicode gaps
are corrected; unsupported characters no longer produce unrelated symbols.

Explicit `ascii=` and `unicode=` win over derived spellings.
`Name.from_latex` strips surrounding whitespace, rejects blank/non-string
input, and raises `ValueError` for unsupported text unless `ascii=` is
provided. With that fallback, missing Unicode uses the ASCII spelling.
Nonempty target validation is unchanged. Plain `Name("x")` remains the
right choice for an ordinary name; `Name(r"\alpha")` still stores that
literal string in all three targets rather than inferring Greek.

For low-level lookup, import `LatexSymbols` from `galaga.names`.
`lookup` returns `(unicode, ascii)` or `None` and, unlike the factory,
does not strip whitespace. The old `galaga.latex_symbols` import is only
a temporary same-object shim scheduled for removal before stable `2.0.0`.
See [ADR-100](../adrs/100-explicit-bounded-latex-name-conversion.md).

## Migrate custom notation with immutable rules

### Scripted and compound labels

Use explicit spellings for compound labels. Appending a LaTeX script now
protects the complete label, including an existing superscript:

```python
from galaga import Algebra, Name, dual, inverse

value = Algebra(2).blade(1)
area_label = value.named(Name("area", latex=r"a \wedge b"))
square_label = value.named(Name("square", latex="x^2"))
assert dual(area_label).display("expr/latex") == r"\left(a \wedge b\right)^*"
assert inverse(square_label).display("expr/latex") == r"{x^2}^{-1}"
assert area_label.numeric is value.numeric
```

These are labels, not claims that the value equals an outer product or a
square. No binding or numeric evaluation is inferred from them.
The [bounded LaTeX guard](rendering-implementation.md#latex-script-spelling-safety)
is not a general TeX parser; explicitly group more complex opaque labels.
Use `Call` expressions when you need mathematical structure and replay.

### Immutable rules

The migrated mixed-precedence suite retains existing v2 defaults, not exact
v1 typography. Unicode uses spaced infix operators, explicit star-script
positions, and combining accents on grouped expressions; Hestenes inner
product has a functional Unicode spelling. Use `Notation.functional()`
when explicit operation names are preferable. Compound unit normalization
keeps its default hat unless you select `unit_fraction` below.

Double negation may disappear from the rendered view while remaining in
stored provenance. Negated products and nested regressive products can keep
additional parentheses. Multivector division displays multiplication by a
right inverse, and the unscaled v2 Lie/Jordan definitions omit v1's half.
The [mixed-rendering contract](../adrs/103-mixed-rendering-contracts-with-numeric-ownership.md)
checks numeric meaning as well as these presentation differences.

Import `Notation` and `RenderRule` from `galaga`. Replace
`notation.set("Reverse", "latex", ...)` with
`notation.with_rule("reverse", ..., target="latex")`, keeping the returned
value. The old mutable `galaga.notation.NotationRule` is not the v2 API.
Preset values can be shared safely without calling `copy()`.

Generic rules are fallbacks: an existing target-specific rule still wins.
For example, replacing a generic reverse rule does not remove its LaTeX
override; replace that target explicitly when changing its appearance.
`Notation.hestenes()` now selects its dagger in both Unicode and LaTeX;
the default and Doran-Lasenby presets retain tilde.

To show normalization as a distinct step between a hat name and its value:

```python
from galaga import Algebra, Name, Notation, RenderRule, unit

algebra = Algebra(3)
B = algebra.blade(3).named("B")
Bhat = unit(B).named(Name.from_latex(r"\hat{B}"))
teaching = Notation.default().with_rule("unit", RenderRule("unit_fraction"))

assert Bhat.display("full/latex", notation=teaching) == (
    r"\hat{B} \quad = \quad \frac{B}{\lVert B \rVert} \quad = \quad e_{12}"
)
assert Bhat.expr.operation_id == "unit"
```

Add `target="latex"` to `with_rule` to change just that target.
The denominator denotes Galaga's metric norm
$\sqrt{|\langle B\widetilde{B}\rangle_0|}$; the display does not assume a
positive-definite metric or evaluate anything. Zero/near-zero norms still
fail eagerly. Non-default tolerances retain a functional display so the
numeric control is not hidden. The default hat layout is unchanged.

Long functional notation uses canonical IDs such as `grade_involution`.
Short functional names are presentation only: `invol`, `dl_inner`, and
`h_inner` keep involution and competing inner products distinguishable.
Unknown rule metadata does not register a new operation.

One legacy convenience remains unavailable: the mutable
`Notation.scientific`/`with_scientific` selectors. V2 currently renders
scientific LaTeX numbers with `\times`; there is no `cdot`/`raw` switch.
See [ADR-101](../adrs/101-immutable-notation-contracts-and-unit-fraction-layout.md)
and the executable
[custom-notation notebook](../../examples/galaga_v2/custom_functional_notation.py).

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

## Migrate concrete display controls

V2 uses native bitmask order by default. Select a `DisplayOrder` explicitly
when grade grouping or another presentation order is wanted. This changes
rendered terms, not `data` or `basis_blades()` enumeration. In particular,
quaternion bivectors enumerate as `k, j, i`; use semantic roles for conventional
unpacking:

```python
from galaga import Algebra, DisplayPolicy, p_quaternion

quaternions = Algebra(config=p_quaternion())
i, j, k = (quaternions.blade(role) for role in
           ("quaternion_i", "quaternion_j", "quaternion_k"))
value = 1 + 2.3456 * i + 3.4567 * j + 4.5678 * k
precision = quaternions.presentation.with_display(DisplayPolicy(coefficient_precision=3))
assert value.display("value/unicode", presentation=precision) == "1 + 2.35i + 3.46j + 4.57k"
```

Multivector `format` specs now select content and target, for example
`f"{value:value/latex}"`. Numeric specs such as `f"{value:.3f}"` are not
currently supported. `coefficient_precision` counts significant digits; it
does not provide fixed decimal places or trailing-zero padding. For an
individual scalar coefficient, ordinary Python `format(float(grade(value, 0)),
".3f")` remains available.

Multivector `repr(value)` is ASCII, while `str(value)` is Unicode by default.
`repr(algebra)` is a diagnostic numeric-owner wrapper, not the old `Cl(p,q,r)`
summary or a stable serialized format. Use explicit `signature` and `gram`
metadata for those properties. These are existing v2 differences, not changes
to arithmetic. See [ADR-097](../adrs/097-concrete-display-contracts-outlive-legacy-rendering.md).

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
