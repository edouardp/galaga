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

Replace each old dispatcher call with its chosen function:

| Old `ip` mode | Public v2 function |
|---|---|
| Default, `"doran_lasenby"`, `"dorst"` | `doran_lasenby_inner` |
| `"hestenes"` | `hestenes_inner` |
| `"left"` | `left_contraction` |
| `"right"` | `right_contraction` |
| `"scalar"` | `scalar_product` |

The functions do not accept a `mode` keyword. Their differences are numerical,
not just notation:

```python
from galaga import (
    Algebra,
    hestenes_inner,
    left_contraction,
    metric_inner_product,
    right_contraction,
    scalar_product,
)

algebra = Algebra(gram=((2, 1), (1, 3)))
e1, e2 = algebra.basis_vectors()
s = algebra.scalar(2)
B = e1 ^ e2  # e1 * e2 would also contain the off-diagonal Gram entry.
G = algebra.gram
determinant = G[0, 0] * G[1, 1] - G[0, 1] ** 2

assert s | e1 == e1 | s == 2 * e1
assert hestenes_inner(s, e1) == 0
assert left_contraction(s, e1) == right_contraction(e1, s) == 2 * e1
assert right_contraction(s, e1) == left_contraction(e1, s) == 0
assert float(scalar_product(B, B)) == -determinant
assert float(metric_inner_product(B, B)) == determinant
```

For mixed grades, apply the defining rule separately to every homogeneous
pair and add the results. Default LaTeX uses a dot for both Doran–Lasenby
and Hestenes; use `Notation.functional()` when the distinction should be
visible. The stored operation IDs and numeric results do not depend on
that choice. Explore the [inner-product notebook](../../examples/algebra/inner_product_family.py)
for four metrics, including indefinite and degenerate cases.

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

The factory flags `lazy` and `symbolic` are not v2 aliases, even when false.
Use `expr` consistently for `basis_vectors`, `basis_blades`, `locals`,
`pseudoscalar` and `blade`. Passing either retired flag raises `TypeError`.

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

## Inspect grades without assigning them to symbols

Replace private `_grade` inspection with `value.homogeneous_grade()`.
It inspects the current coefficients, returning `None` for zero or mixed
grade. Its default `1e-12` tolerance is diagnostic, not an equality rule;
`homogeneous_grade(atol=0)` includes every stored nonzero coefficient.

`grade(value, k)` projects onto a component; it does not assert that the
result is nonzero. `grade(value, "even")` and `even_grades(value)` have equal
values but different expression IDs and spelling; prefer the named parity
operations for the even/odd glyphs.

Symbols carry no fixed grade, even if the first binding is a vector:

```python
from galaga import Algebra, Call, Symbol, evaluate, simplify

algebra = Algebra(4)
e1, e2, e3, e4 = algebra.basis_vectors()
projection = Call("grade", (Symbol("v"),), {"target": 1})
assert simplify(projection) == projection
assert evaluate(projection, algebra=algebra, environment={"v": e1}) == e1
zero = evaluate(projection, algebra=algebra, environment={"v": e1 ^ e2})
assert zero == 0 and zero.homogeneous_grade() is None

B = ((e1 ^ e2) + (e3 ^ e4)).named("B")
wedge = B ^ B
assert wedge == 2 * (e1 ^ e2 ^ e3 ^ e4)
assert simplify(wedge.expr) == wedge.expr
assert evaluate(wedge.expr, algebra=algebra, environment={"B": B}) == wedge
assert evaluate(wedge.expr, algebra=algebra, environment={"B": e1}) == 0
```

Call `simplify(value.expr)` when a value has provenance. V2 deliberately
supports a smaller rewrite set than v1: even valid numeric identities such
as double reverse need not collapse their call trees. Do not rely on v1's
term collection, scalar-factor collapse or cached-grade rewrites. A universal
`x ∧ x → 0` rule is incorrect for general multivectors, including nonsimple
bivectors. `norm(unit(v))` and `inverse(inverse(v))` stay explicit and retain
their invalid-binding domain errors. The
[involutions lesson](../../examples/algebra/involutions_and_grade_ops.py)
teaches these distinctions with selectable Gram matrices; see
[ADR-114](../adrs/114-grade-inspection-and-bounded-simplification-contracts.md).

## Inspect generic expression calls, not legacy registries

Plain numeric operands can participate in a tracked operation. Their literal
leaves are snapshots; only symbol leaves respond to new bindings. A bare
`Symbol("a")` is not a numeric operand: construct a `Call` explicitly when
you want a standalone expression.

```python
from galaga import Algebra, Call, ScalarLiteral, Symbol, evaluate, render

algebra = Algebra(3)
plane = algebra.blade(3)
original = algebra.vector((2, -1, 1))
replacement = algebra.vector((1, 2, -1))
literal = plane * original.with_expr()
named = plane * original.named("a")
assert literal == named
assert evaluate(literal.expr, algebra=algebra) == literal
assert evaluate(named.expr, algebra=algebra, environment={"a": replacement}) == plane * replacement
assert named == plane * original  # replay has not mutated the saved value

node = Call("subtract", (ScalarLiteral(3), Symbol("a")))
assert evaluate(node, algebra=algebra, environment={"a": replacement}) == 3 - replacement
assert render(node, presentation=algebra.presentation, target="latex") == "3 - a"
assert repr(node).startswith("Call(operation_id=")  # diagnostic, not mathematics
assert evaluate(ScalarLiteral(3), algebra=algebra) == 3
```

Even scalar leaves need an explicit algebra when evaluated; nodes have no
hidden-context `.eval()` method. `normalize` and `normalise` are temporary
deprecation-warning adapters to `unit`. Prefer the canonical name.
Normalization divides by the metric-derived magnitude, not by the value's
geometric inverse. Zero and nonzero null vectors cannot be normalized by
this operation. See the
[eager-values lesson](../../examples/galaga_v2/eager_values_and_expressions.py)
and [ADR-113](../adrs/113-eager-operation-contracts-outlive-mixed-symbolic-tests.md).

Galaga 2 has no per-operation expression class or symbolic-handler registration
step. Inspect `Call.operation_id`, `operands` and immutable `parameters`;
`get_operation` resolves the shared schema used by construction and replay.
Do not equate evaluator arity with the number of expression operands:

```python
from galaga import Algebra, Call, Symbol, evaluate, get_operation, grade

algebra = Algebra(gram=((2, 0.5), (0.5, -1)))
x = algebra.vector([2, 1]).named("x")
y = algebra.vector([-1, 3]).named("y")
product = x * y
bivector = grade(product, 2)

assert product.expr == Call("geometric_product", (Symbol("x"), Symbol("y")))
assert bivector.expr == Call("grade", (product.expr,), {"target": 2})
assert get_operation("grade").arity == 2
assert get_operation("grade").expression_arity == 1
assert bivector.expr.parameters == (("target", 2),)
assert list(product.data) == [-4.5, 0, 0, 7]

# Replay follows these bindings, not a saved numeric result.
replayed = evaluate(product.expr, algebra=algebra, environment={"x": y, "y": x})
assert list(replayed.data) == [-4.5, 0, 0, -7]
assert list(product.data) == [-4.5, 0, 0, 7]
```

Transwedge similarly stores two operands plus an `order` parameter; variadic
geometric and outer products lower to nested binary calls. `OPERATIONS`
enumerates the public numeric catalog, not all model-specific semantic calls
recognized by `get_operation`. Its size is not a compatibility guarantee.
This replaces v1 registry introspection, not a user-defined operation/plugin
registration API. See
[ADR-111](../adrs/111-architecture-contracts-use-the-public-operation-catalog.md).

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

### Custom under-accents

Replace mutable under-accent rules with a target-specific immutable override:

```python
from galaga import Algebra, Name, Notation, RenderRule, antireverse, p_rga

algebra = Algebra(config=p_rga())
value = algebra.blade(1).named("A")
notation = Notation.lengyel().with_rule(
    "antireverse",
    RenderRule("underaccent", symbol=Name("sim", "\u0330", r"\sim")),
    target="latex",
)
assert antireverse(value).display("expr/latex", notation=notation) == (
    r"\underset{\sim}{A}"
)
```

A glyph such as `\sim` is an annotation, not a one-argument accent command.
The emitter places it under the complete grouped body. Built-in `\utilde`
and `\underline` remain direct commands; ASCII and Unicode are unaffected
by a LaTeX-only rule. Custom command macros are not inferred from a leading
backslash. See the [rendering command boundary](rendering-implementation.md#notation-is-presentation-data)
and [ADR-105](../adrs/105-public-rga-contracts-and-underaccent-fallback.md).

The [RGA demo](../../examples/rga/rga_demo.py) computes antireverse signs by
antigrade and displays the same mixed-grade value with both presentations.
It also distinguishes signed blade names from native masks and explains why
zero reports `homogeneous_grade() is None` even when transwedge retains an
explicit `order` parameter in its expression. Bulk/weight reconstruction is
a property of the standard PGA metric, not a universal identity for arbitrary
Gram matrices.

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

## Migrate local bindings

V2's `locals()` returns a read-only mapping from an independent
`LocalNamePolicy`. Replace `grades=` by selecting signed references, and
`prefix=` or `variable_hints` by explicitly choosing keys. For example:

```python
from galaga import Algebra, LocalNamePolicy, p_sta
from galaga.expression import evaluate

sta = Algebra(config=p_sta(sigmas=True))
g0, g1, g2, g3 = sta.basis_vectors()
expected = g1 * g0
bivectors = LocalNamePolicy(
    sta.n,
    ((key, ref) for key, ref in sta.presentation.local_names.entries
     if ref.mask.bit_count() == 2),
)
view = sta.with_local_names(bivectors)
bindings = view.locals(expr=True)
assert bindings["s1"] == expected
assert evaluate(bindings["s1"].expr, algebra=view, environment=bindings) == expected

# Retain an old Python key without losing its signed meaning.
renamed = LocalNamePolicy(
    sta.n,
    (("g01" if key == "s1" else key, ref) for key, ref in bivectors.entries),
)
old_keys = sta.with_local_names(renamed).locals()
assert old_keys["g01"] == expected == -sta.blade("g0g1")
assert sta.basis_blades(2)[0] == -expected
```

The sign belongs to the reference, not to the letters in the key.
Changing `blades=` or calling `with_blades` alone does not regenerate locals.
Preset builders explicitly supply both components.

For compact Python keys with a wedge display, configure the two separately:

```python
from galaga import Algebra, LocalNamePolicy, indexed_blade_convention

display_labels = indexed_blade_convention(3, prefix="v", style="wedge")
compact_labels = indexed_blade_convention(3, prefix="v")
algebra = Algebra(
    3,
    blades=display_labels,
    local_names=LocalNamePolicy.from_convention(compact_labels),
)
v12 = algebra.locals()["v12"]
assert v12 == algebra.blade(1) ^ algebra.blade(2)
assert v12.display("name/ascii") == "v12"
assert v12.display("value/unicode") == "v₁∧v₂"
```

`from_convention` takes canonical ASCII names literally. It skips scalar
labels, invalid identifiers and keywords; aliases and roles are not included.
It neither sanitizes names nor compacts products: `v1^v2` is skipped, while
`v1v2` remains that identifier. Explicit policies may include scalar bindings
such as `{"one": 0}` or valid Unicode keys. Use explicit axis-key entries for
the former empty-prefix convenience.

Replace `lazy=True` with `expr=True`. Named locals carry symbols requiring an
explicit environment for replay; `blade(value, expr=True)` instead creates a
self-contained signed literal. `locals(expr=False)` omits initial expression
leaves but keeps names, so later operations still record symbolic provenance.
For scalar lookup use `blade(0)`, default `blade("1")`, or `scalar(1)`.
Empty-string parsing is retired. Unknown blade names raise `KeyError`,
whereas out-of-range integer masks raise `ValueError`.

The [presentation notebook](../../examples/galaga_v2/presentation_contexts.py)
demonstrates these distinctions without injecting names into Marimo's namespace.
See [ADR-106](../adrs/106-independent-public-local-name-contracts.md).

## Migrate blade conventions and STA names

Replace v1's `b_sta(sigmas=True, pseudovectors=True)` with a complete preset:

```python
from galaga import Algebra, p_sta

sta = Algebra(config=p_sta("mostly-minus", sigmas=True, pseudovectors=True))
g0, g1, g2, g3 = sta.basis_vectors()
assert sta.blade("s1") == g1 * g0
assert sta.blade("g0g1") == g0 * g1 == -sta.blade("s1")
assert sta.locals()["ig0"] == sta.I * g0
```

`sigmas` names both $\sigma_k=\gamma_k\gamma_0$ and
$i\sigma_k=I\gamma_k\gamma_0$; `pseudovectors` names $i\gamma_k=I\gamma_k$.
ASCII pseudovectors are now `ig0` … `ig3`, not `iy0` … `iy3`.
Lookup returns the signed product rather than the old unsigned storage slot.
The default preset still keeps gamma words. Both preset options are opt-in.

`p_sta("mostly-plus")` uses the time-first $(-,+,+,+)$ metric.
`Algebra(3, 1)` uses $(+,+,+,-)$; these orders cannot share a sign table.
For presentation-only configuration, pass the actual ordered squares to
`spacetime_blade_convention(signature=algebra.basis_squares, sigmas=True)`
only for an orthogonal unit-diagonal frame. Labels do not change or validate
the metric of an algebra to which they are later applied. In a general Gram
frame, name computed multivectors instead.

Other blade-convention changes:

- Replace `b_default`, `b_gamma`, `b_sigma`, and custom style/subscript
  factories with `indexed_blade_convention(dimension, ...)`. Use explicit
  `Name` objects for target-aware Greek prefixes and letter subscripts.
- Override native integer masks with strings, `Name`, or signed
  `BladeLabel` objects. Name tuples and metric-role text such as `"+1-1"`
  are not parsed; aliases and semantic roles are explicitly declared.
- Use `algebra.blade_label(mask)` for immutable metadata. To rename, build a
  new convention and use `with_blades` or a scoped presentation. Replacing
  local names is an independent `LocalNamePolicy` decision.
- Unknown lookup names raise `KeyError`. Add `"pss"` as an explicit alias
  if needed, or use `algebra.I`. For the scalar blade use mask `0` or label
  `"1"`; empty text no longer implicitly selects it.
- PGA presets use Euclidean vectors first and a final null vector. Use an
  explicit signature and indexed labels to keep historical null-first order.
  PGA/CGA pseudoscalars are not automatically named `I`.
- Use `p_cga(frame="null")` for actual null origin/infinity vectors.
  Merely renaming an orthogonal basis does not change its Gram matrix.

The [construction notebook](../../examples/galaga_v2/algebra_construction.py)
computes the signs under both STA metric choices. See
[ADR-104](../adrs/104-metric-derived-sta-names-and-public-blade-contracts.md)
for the archived contracts and validation boundaries.

For the old `b_gamma(pss="I")`, `b_sigma(pss="I")` and
`b_sigma_xyz(pss="I")` constructors, override the top-grade label explicitly:

```python
from galaga import Algebra, Name, indexed_blade_convention

signature = (1, -1, -1, -1)
dimension = len(signature)
labels = indexed_blade_convention(
    dimension, prefix=Name("g", "γ", r"\gamma"), start=0,
    style="juxtapose", overrides={(1 << dimension) - 1: Name("I")},
)
algebra = Algebra(signature, blades=labels)
volume = algebra.scalar(1)
for vector in algebra.basis_vectors():
    volume = volume ^ vector
assert algebra.blade("I") == algebra.pseudoscalar() == volume
```

Use a sigma prefix and explicit letter subscripts for the corresponding
sigma conventions. A label does not normalize a volume or make it invertible:
its square still depends on the Gram determinant and dimension. Signed
`BladeLabel` overrides distinguish oriented-name lookup from the positive
native mask. See
[ADR-110](../adrs/110-public-factory-and-display-edge-contracts.md).

## Migrate complex and quaternion conventions

Use `Algebra(config=p_complex())` or `Algebra(config=p_quaternion())` in
place of `b_complex` or `b_quaternion`. Their Euclidean even subalgebras
include the scalar part. In the quaternion convention,
`i=e23`, `j=e13`, `k=e12` satisfy Hamilton's identities; `j` is not `e31`.
Select semantic units by roles rather than unpacking native bivector order:

```python
from galaga import Algebra, p_quaternion

algebra = Algebra(config=p_quaternion())
e1, e2, e3 = algebra.basis_vectors()
expected = (e2 ^ e3, e1 ^ e3, e1 ^ e2)
i, j, k = algebra.blades("quaternion_i", "quaternion_j", "quaternion_k")
assert (i, j, k) == expected
assert i * j == k and j * k == i and k * i == j
assert algebra.basis_blades(2) == (k, j, i)
assert algebra.blade("e23") == i
```

Replace metric-role text `"+2+3"` with `"quaternion_i"` or an explicit
native mask. Replace `lazy=True` with `expr=True`. The existing
`blade(computed_value, expr=True)` factory creates a self-contained signed
literal without retaining a previous name or expression.

To replace `vector_names=["x", "y", "z"]`, replace immutable vector labels
and explicitly choose any compound labels, retaining aliases and roles:

```python
from dataclasses import replace
from galaga import Algebra, BladeConvention, Name, p_quaternion

algebra = Algebra(config=p_quaternion())
original = algebra.presentation.blades
labels = list(original.labels)
for index, name in enumerate(("x", "y", "z")):
    mask = 1 << index
    labels[mask] = replace(labels[mask], name=Name(name))
labels[algebra.dim - 1] = replace(
    labels[algebra.dim - 1], name=Name("xyz", "xyz", "x y z"),
)
view = algebra.with_blades(
    BladeConvention(algebra.n, labels, aliases=original.aliases, roles=original.roles)
)
x, y, z = view.basis_vectors()
assert z.latex() == "z"
assert view.blade("quaternion_i") == y ^ z
assert (x ^ y ^ z).latex() == "x y z"
assert view.numeric is algebra.numeric
```

Changing labels does not regenerate locals; configure `LocalNamePolicy`
separately if Python bindings should also change.

The presets supply matching metrics, but `complex_blade_convention()` and
`quaternion_blade_convention()` only supply vocabulary. On a different Gram
matrix, compute actual blade squares rather than assuming Hamilton or complex
identities from names. Reverse and Clifford conjugation agree on even
elements, not on arbitrary ambient multivectors with odd grades.

The [complex/quaternion notebook](../../examples/basics/complex_and_quaternions.py)
demonstrates the defining products, native order, conjugation, and a
Gram-derived counterexample to `i²=-1`. See
[ADR-107](../adrs/107-public-complex-and-quaternion-convention-contracts.md).

## Migrate transformation helpers

The v1 `project`, `reject`, and `reflect` helpers are not v2 aliases.
For a vector and an invertible blade, compose the public primitives explicitly:

```python
import numpy as np
import galaga as ga

algebra = ga.Algebra(gram=[[2, 0.5, 0], [0.5, -1, 0.25], [0, 0.25, 3]])
e1, e2, e3 = algebra.basis_vectors(expr=True)
v = 2 * e1 - e2 + 3 * e3
B = e1 ^ e2
projection = ga.left_contraction(v, B) * ga.inverse(B)
rejection = v - projection
np.testing.assert_allclose((projection + rejection).data, v.data, rtol=0, atol=1e-12)

# Independent coordinate check using the actual Gram matrix.
C = np.eye(3)[:, :2]
G = algebra.gram
P = C @ np.linalg.solve(C.T @ G @ C, C.T @ G)
np.testing.assert_allclose(projection.vector_part, P @ v.vector_part, rtol=0, atol=1e-12)

# Reflection in the hyperplane normal to n, not along the mirror's tangent.
n = 2 * e2
reflected = -n * v * ga.inverse(n)
H = np.eye(3) - 2 * np.outer(n.vector_part, n.vector_part @ G) / float(n * n)
np.testing.assert_allclose(reflected.vector_part, H @ v.vector_part, rtol=0, atol=1e-12)
```

The Gram matrix restricted to the blade's spanning subspace must be
nonsingular. The ambient metric can still be degenerate: `e1^e2` is invertible
in `Algebra(gram=np.diag([1, 1, 0]))`, while `e1^e3` is not.
A null normal or noninvertible blade raises `ValueError` through `inverse`;
there is no automatic pseudoinverse.

Rejection also equals `(v ^ B) * inverse(B)` for these vector/blade inputs.
Reversion is not a replacement for inverse: the normal above has square `-4`.
`sandwich(R, v)` always means `R*v*reverse(R)`, not `R*v*inverse(R)`.
Two normal reflections compose in the order `R=n2*n1`; use the inverse
unless its equality with reverse has been established.

The two-dimensional blade conjugation `B*v*inverse(B)` flips components in
the blade's **normal span**, giving `(I-2P)v`. In three dimensions, reflecting
in that plane *as a mirror* instead gives `(2P-I)v`. State which subspace
represents normals before choosing a formula.

`Algebra.rotor`, `rotor_from_bivector`, and `rotor_from_plane_angle` remain
retired. For an oriented Euclidean unit plane, compute its square before using
the familiar angle recipe:

```python
import numpy as np
import galaga as ga

algebra = ga.Algebra(2)
e1, e2 = algebra.basis_vectors(expr=True)
B = e1 ^ e2
assert B * B == -1
theta = np.pi / 2
R = ga.exp(-theta * B / 2)
np.testing.assert_allclose((R * ga.reverse(R)).data, algebra.scalar(1).data, rtol=0, atol=1e-12)
np.testing.assert_allclose(ga.sandwich(R, e1).data, e2.data, rtol=0, atol=1e-12)
```

For a coordinate bivector, `B*B` equals `G[0,1]**2-G[0,0]*G[1,1]`.
Negative, positive and zero scalar squares give trigonometric, hyperbolic
and terminating exponential branches respectively. This is a statement about
simple bivectors, not arbitrary mixed-grade inputs. Generic `exp` still accepts
scalars and vectors; it does not validate a rotation plane or guarantee a rotor.

For pseudoscalar provenance, use `pseudoscalar(expr=True)` instead of
`lazy=True`. Naming it `"I"` attaches a symbol, so explicit replay needs
`environment={"I": pseudoscalar}`.

The [projector notebook](../../examples/algebra/projectors_ga.py) draws the
actual computed plane and explains its restricted metric. The
[reflection notebook](../../examples/algebra/rotors_from_reflections.py)
distinguishes mirror tangents from normals and plots both computed reflections.
See [ADR-108](../adrs/108-public-transformation-compositions-and-geometric-notebook-plots.md).

## Migrate scalar helpers

Replace `algebra.fraction(p, q)` / `frac(p, q)` with
`algebra.scalar(p, expr=True) / q` when provenance is wanted. Replace
`algebra.pi` and the other constant properties with explicitly supplied values,
for example `algebra.scalar(math.pi, expr=True).named("pi", latex=r"\pi")`.
Use `scalar_sqrt(algebra.scalar(2, expr=True))` for a square-root expression.
The convenience members remain absent.

Names are presentation metadata, not a constants library or a unit system.
`.named(...)` does not turn on expression tracking; request `expr=True` or
`.with_expr()` explicitly. A named operand in a tracked operation becomes a
symbol, so replay needs the corresponding environment.

```python
from fractions import Fraction
import galaga as ga
from galaga.expression import evaluate

algebra = ga.Algebra(1)
third = algebra.scalar(1, expr=True) / 3
assert third.latex(content="expr") == "0.333333"
assert Fraction(float(third)) != Fraction(1, 3)

a = algebra.scalar(1, expr=True).named("a")
named_third = a / 3
assert named_third.latex(content="expr") == r"\frac{a}{3}"
assert evaluate(named_third.expr, algebra=algebra, environment={"a": a}) == named_third

small = algebra.scalar(1.2e-34, expr=True)
assert float(small) == 1.2e-34 and small != 0
assert small.latex(content="value") == "0"  # Default display filtering only.
visible = algebra.presentation.with_display(ga.DisplayPolicy(zero_tolerance=0))
assert small.display("value/latex", presentation=visible) == r"1.2 \times 10^{-34}"
assert float(small) == 1.2e-34  # Rendering did not change the coefficient.
```

Literal arithmetic may simplify during rendering; provenance is not a promise
to preserve the original fraction spelling. If only a fraction layout is
needed, `galaga.rendering.tree.Fraction(Literal(p), Literal(q))` provides one;
this is a different class from Python's `fractions.Fraction`.
Neither that layout nor a symbolic name creates exact rational arithmetic.
Scalar division by either signed zero raises `ZeroDivisionError`, replacing
the retired fraction constructor's `ValueError`.

The default value renderer hides coefficients with magnitude below `1e-12`.
Set `zero_tolerance=0` to show every stored nonzero coefficient, including
subnormals. This remains independent of exact equality and hashing. A
tolerance-filtered display or teaching equality is not an exact numeric claim.
Likewise, tests for tiny values must use zero absolute tolerance or exact
coefficient checks; the default `np.isclose(0, 1e-34)` is true.

Scientific LaTeX currently uses `\times`. The old `cdot`/`raw` selectors and
`latex(coeff_format=...)` remain unsupported. `coefficient_precision` controls
significant digits, without trailing-zero padding. For fixed numeric output,
convert a scalar explicitly, for example `format(float(small), ".3e")`.

The [eager-values notebook](../../examples/galaga_v2/eager_values_and_expressions.py)
executes the small-value and named-fraction examples. See
[ADR-109](../adrs/109-public-scalar-compositions-and-small-value-contracts.md).

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

### Rendered strings are snapshots

`.display()` and `.latex()` return ordinary strings, not the old
`_DisplayResult` object. Their repr is consequently Python's quoted string
repr. Specify `"full/latex"` when a LaTeX teaching equality is wanted;
`.display()` without arguments follows the active content/target policy.

```python
from galaga import Algebra, DisplayPolicy, Notation

algebra = Algebra(2)
x, y = (v.named(name) for v, name in zip(algebra.basis_vectors(expr=True), ("x", "y")))
value = (x * y).named("v")
saved = value.display("full/ascii")
assert type(saved) is str and saved == "v = xy = e12"
functional = algebra.presentation.with_notation(Notation.functional())
with algebra.use_presentation(functional):
    current = value.display("full/ascii")
    assert "geometric_product" in current
    assert saved == "v = xy = e12"
assert value.display("full/ascii") == saved

name_only = algebra.presentation.with_display(DisplayPolicy(content="name"))
with algebra.use_presentation(name_only):
    assert value.latex(wrap="$") == "$v$"
assert value.latex(wrap="$") == "$" + value.latex() + "$"
```

Replace `display_repr` with `DisplayPolicy(content="full")` or
`content="name"` explicitly. The default named display is a teaching equality.
Repr of the multivector always selects ASCII; its rich hook selects LaTeX.
Unlike the old bypass behavior, `wrap="$"` only adds delimiters: choose
`content="name"` when only the name should be wrapped.

`format(rendered_string, ".2f")` raises an error, and `".2"` merely truncates
the text. Neither sets coefficient precision. Configure precision before
rendering or format individual numeric coefficients after conversion.
The [presentation notebook](../../examples/galaga_v2/presentation_contexts.py)
executes the snapshot/scope distinction. See
[ADR-110](../adrs/110-public-factory-and-display-edge-contracts.md).

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
