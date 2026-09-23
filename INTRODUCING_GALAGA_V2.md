# Introducing Galaga 2

**Explicit, observable geometric algebra for Python.**

Galaga 2 computes with real Clifford algebras over arbitrary symmetric
metrics, but its distinguishing idea is that a calculation should be as
readable as it is correct. Values are immutable, expression provenance is
optional but faithful, and presentation — blade names, notation, ordering,
LaTeX — is a separate layer that never changes the mathematics.

```python
from galaga import Algebra, norm, outer_product, presets

alg = Algebra(config=presets.euclidean(3), expr=True)
e1, e2, e3 = alg.basis_vectors(expr=True)

u = (2 * e1 + e2).named("u")
v = (e1 + 3 * e2).named("v")
area = outer_product(u, v).named("A")

assert area == 5 * (e1 ^ e2)
assert float(norm(area)) == 5.0

area.display("value/unicode")   # 5e₁₂
area.display("expr/unicode")    # u ∧ v
```

The wedge is an oriented area **bivector**, not a cross-product vector. The
name and the expression history do not change the numeric value, and the same
value can be shown as a result, as a formula, or as both.

## Why another GA library?

Geometric algebra is easy to compute and hard to *communicate*. Typical
libraries quietly fix a basis order, a blade vocabulary, an inner-product
convention and a print format. Galaga 2 makes each of those an explicit,
inspectable choice:

- the **metric** is a Gram matrix (or a signature with an explicit order);
- the **operations** have unambiguous names, with operators as conveniences;
- the **blades** are chosen by convention objects, not by global spelling;
- the **notation** is a value you can pass, scope, or capture;
- the **output** is one semantic tree rendered to ASCII, Unicode or LaTeX.

None of those choices changes equality, hashing, or the numeric result.

## Design principles

1. **Named functions are the API.** `geometric_product`, `outer_product`,
   `left_contraction`, `regressive_product`, `inverse`, `log` — operators such
   as `*`, `^`, `|`, `<<`, `>>` and `~` are conveniences over them. There is no
   ambiguous `ip()` whose meaning depends on a mode.
2. **Metrics are real and general.** Nonorthogonal, indefinite and degenerate
   metrics, native-null conformal bases, and explicit ordered signatures.
3. **Eager values, optional provenance.** Results are ordinary NumPy-backed
   values; enabling expression tracking records how they were obtained. It is
   not a deferred symbolic engine.
4. **Presentation is a layer.** Blade conventions, local names, display order,
   notation and output target compose into immutable configurations and
   reusable presenter views.
5. **Conventions are validated.** Conformal and rigid model APIs check that a
   geometry is really what it claims to be instead of silently guessing.
6. **Teaching is a first-class output.** Values, expressions and algebra tables
   all render through the same pipeline, with or without notebook tooling.

## Metrics without assumptions

```python
from galaga import Algebra, metric_inner_product

spacetime = Algebra(1, 3)                # ordered squares: +1, -1, -1, -1
projective = Algebra(3, 0, 1)            # three positive, then a null vector

oblique = Algebra(gram=[[2.0, 1.0], [1.0, 3.0]])
g1, g2 = oblique.basis_vectors()
assert float(metric_inner_product(g1, g2)) == oblique.gram[0, 1]
assert g1 * g2 == oblique.gram[0, 1] + (g1 ^ g2)   # e_i e_j + e_j e_i = 2G_ij
```

In a nonorthogonal basis, `g1 ^ g2` is a pure bivector while `g1 * g2` also
contains the Gram entry. Blade labels never turn exterior products into
geometric products or perform a basis change.

## Products and dualities that say what they mean

```python
from galaga import (
    doran_lasenby_inner,
    hestenes_inner,
    left_contraction,
    right_contraction,
    regressive_product,
)

a = alg.vector([1.0, 0.0, 0.0])
b = alg.vector([0.0, 1.0, 0.0])
assert a * b == a ^ b                       # orthogonal vectors
assert a | b == doran_lasenby_inner(a, b)   # grade-difference inner product
assert (a << b) == left_contraction(a, b)
assert (a >> b) == right_contraction(a, b)
```

The duality family is equally explicit: metric-independent complements, metric
Hodge duals, and weight duals, each available on the left and right, plus
`meet` and `join` aliases for the regressive and outer products.

## Algorithms with checked domains

```python
from galaga import exp, log, rotor_generator

B = e1 ^ e2
R = exp(-0.5 * B)
assert log(R).almost_equal(-0.5 * B)
assert rotor_generator(R).almost_equal(-0.5 * B)
```

Galaga ships a checked general inverse, a square root via Study-number
decomposition, real exponentials and principal logarithms with explicit domain
checks, rotor generators separate from `log`, and an outer (exterior)
transcendental family. Their algorithms are general over the native Gram
matrix; the operation vocabulary below explains how.

## Operations designed for general algebras

The long tail of Galaga's operations is built on the symmetric Gram matrix and
the native left- and right-regular actions. Where an algorithm is
dimension-dependent, Galaga selects one instead of hardcoding a
two- or three-dimensional formula.

**Products and inner products.** `scalar_product`, `metric_inner_product`,
`metric_regressive_product`, `hestenes_inner`, `doran_lasenby_inner` (alias
`dorst_inner`), `left_contraction` and `right_contraction`,
`left_interior_product` and `right_interior_product` — each is a grade-
selection rule over the actual metric, valid in any dimension.

**Duality, in five explicit families.** `complement` / `uncomplement`,
`left_complement` / `right_complement` (metric-independent exterior masks),
`dual` / `undual`, `left_hodge_dual` / `right_hodge_dual`, and
`left_weight_dual` / `right_weight_dual`, plus `meet` and `join` aliases for
the regressive and outer products.

**Space and anti-space (Lengyel).** `metric_apply` and `antimetric_apply` (the
exomorphism and its anti), `antireverse`, `antiwedge`, `antidot_product`,
`geometric_antiproduct`, and the parameterized `transwedge(a, b, k)` /
`transwedge_antiproduct(a, b, k)`. `transwedge` selects grade `r + s - 2k` of
the geometric product with the reversion sign removed, and its antiproduct is
the De Morgan complement dual. No `Cl(3,0,1)` assumption is involved.

**Brackets with explicit scaling.** `commutator`, `anticommutator`,
`lie_bracket` and `jordan_product` are unscaled; `half_commutator` and
`half_anticommutator` are the explicitly scaled forms, so no hidden half-angle
convention appears in the names.

**Transcendentals.**

- `exp` uses a closed form when `v²` is scalar and otherwise
  scaling-and-squaring Taylor evaluation with the scale derived from the
  left-regular action norm. The old dimension-limited shortcut is gone, so
  compound non-simple bivectors and mixed-grade inputs are supported.
- `log` is the real principal algebra logarithm: Study/scalar-square closed
  forms, otherwise Gauss–Legendre resolvent quadrature on the left action
  (orders 8–256, one column recovered). Singular inputs and the
  nonpositive-real branch cut are rejected rather than silently complexified.
- `sqrt` and `scalar_sqrt` use the Study-number decomposition `x = a + bI`.
- `inverse` dispatches Hitzer closed forms for `d ≤ 5` and the Shirokov
  adjugate iteration for `d ≥ 6`.
- `rotor_generator` and `is_rotor_generator` derive and validate a checked
  geometric exponent, and `is_rotor` requires the reverse sandwich to preserve
  every native basis vector.
- `outerexp`, `outersin`, `outercos` and `outertan` form the metric-free
  exterior series, which terminates at grade `n` in any dimension; `outertan`
  is `outersin · outercos⁻¹`.

**Model layers.** `ConformalModel` and `RigidModel` add validated semantic
operations — attitudes, carriers, cocarriers, centers, containers, partners,
projections, supports, distances, angles, and round/flat bulk and weight
families — on top of the same general core.

Nonorthogonal, scaled, indefinite and degenerate metrics are first-class;
product backends (diagonal fast path, packed table, bounded lazy evaluation,
reference oracle) share one semantic contract; and the logarithmic branch is
resolved without diagonalizing the element. The deliberate limits are
real-only `float64` Clifford algebras and dense `2**n` storage. The one
dimension-restricted API is the optional three-dimensional CGA object
classifier in `galaga-annotation`; the operations it annotates remain general.

## Presentation is configuration

```python
functional = presets.presenters.functional()
lengyel = presets.presenters.lengyel()

functional(area).latex()   # A = outer_product(u, v) = 5 e_{12}
lengyel(area).latex()      # A = u ∧ v = 5 e_{12}
```

Presets bundle a metric with a blade vocabulary, order, notation and optional
model metadata; individual components can be overridden. Scoped notation and
presenter views let a lesson choose the presentation at the point of display,
without mutating the algebra or the values.

## CGA and RGA model layers

```python
from galaga import Algebra, outer_product, presets
from galaga.cga import ConformalModel

cga = ConformalModel(Algebra(config=presets.cga(spatial_dim=3), expr=True), expr=True)
p = cga.up((1.0, 0.0, 0.0))
q = cga.up((0.0, 1.0, 0.0))

dipole = outer_product(p, q).without_expr()
cga.center(dipole)    # 2eₒ + e₁ + e₂ + e∞
cga.carrier(dipole)   # -eₒ₁∞ + eₒ₂∞ + e₁₂∞
```

`ConformalModel` (`galaga.cga`) provides round-point embedding, carriers,
cocarriers, centers, radius norms and dual/IPNS conversions; `RigidModel`
(`galaga.rga`) covers Lengyel-style rigid geometric algebra. Both are ordinary
multivector layers over the same numeric core.

## Annotations for teaching

The optional `galaga-annotation` companion turns a value into an annotated
view: semantic targets survive changes to presentation and never change the
value.

```python
import galaga_annotation as ga_ann
from galaga_annotation import classify_cga, highlight_cga

view = ga_ann.annotate(area, label="oriented area")
assert view.plain is area                 # rendering-only view

highlight = highlight_cga(cga)
object_view = highlight(dipole)
assert classify_cga(dipole, cga).kind == "dipole"
```

Rules are immutable and reusable; annotators compose with presenters; and the
KaTeX renderer draws labels, colours, fills, borders, braces, group accents,
arrows, rules and boxes. Conformal objects can be highlighted by their Lengyel
component families or by an incidence decomposition (carrier/cocarrier
geometry) for round points, dipoles, circles and spheres.

## Companion packages

Companions extend the core; they are **not dependencies**. `galaga` installs
and runs with NumPy alone, the core never imports a companion, and installing
or removing one never changes core semantics or values. Each consumes public
protocols — `.latex()` / `_repr_latex_`, the semantic rendering documents,
expression provenance, and the `__galaga_present__` integration hook — so the
core and the extensions can evolve independently.

| Package | Purpose | Extra requirements |
|---|---|---|
| `galaga` | numeric core, model layers, rendering | Python 3.11+, NumPy |
| `galaga-matrix` | matrix representations, conversions, spinor/quaternion modes | — |
| `galaga-annotation` | semantic annotations, KaTeX teaching output, CGA object highlights | — |
| `galaga-marimo` | t-string Markdown and LaTeX interpolation in Marimo notebooks | Python 3.14+ |
| `galaga-anywidget` | interactive geometric visualizations | — |
| `galaga-mermaid` | experimental expression-tree flowcharts | — |

Every companion targets Python 3.11 unless noted; `galaga-marimo` requires
Python 3.14 for native t-strings.

## Installation and status

Galaga 2 is an **alpha release**. Opt into the v2 prerelease train explicitly:

```bash
python -m pip install --pre "galaga>=2.0.0a7,<3"
```

For reproducible notebooks, pin the version you tested, for example
`galaga==2.0.0a7`. The core package requires only Python 3.11+ and NumPy; the
notebook, matrix, widget and annotation companions are separate installs.

## What's new in Galaga 2

- **Named, unambiguous operations** — long names are canonical, with a small
  set of permanent concise aliases.
- **Immutable values and explicit provenance** — `.named()` and `expr=True`
  replace the v1 lazy engine and its mutation-prone naming API.
- **A presentation layer** — notation, blade conventions, local names, display
  order and target are composable configuration, not global state.
- **Validated model layers** — conformal and rigid APIs with documented
  conventions and exact sign checks.
- **One rendering pipeline** — ASCII, Unicode and LaTeX from a shared semantic
  tree, including labelled Gram and wedge tables.
- **Companion packages** — matrices, annotations, notebook Markdown,
  interactive visualization and diagrams.

Galaga 1 users should start with the
[migration guide](docs/v2/migration-guide.md).

## Learn more

- [Package README](packages/galaga/README.md) — the full feature guide with
  self-contained examples.
- [Documentation index](docs/README.md) — presentation, provenance and
  rendering design notes, plus the numeric core guide.
- [Migration guide](docs/v2/migration-guide.md) — Galaga 1 to Galaga 2.
- [Teaching notebooks](examples/galaga_v2) and the
  [annotation gallery](examples/annotation) — executable Marimo lessons.
- `make run-marimo` opens the gallery against the local packages.

## Testing

Every package carries its own suite, and the core suite additionally executes
the maintained resources as integration contracts. Test cases collected at
this revision:

| Suite | Cases |
|---|---:|
| `galaga` core | 9,906 |
| `galaga-annotation` | 218 |
| `galaga-matrix` | 516 |
| `galaga-marimo` | 95 |
| `galaga-anywidget` | 72 |
| `galaga-mermaid` | 13 |
| release workflow | 196 |

That is roughly eleven thousand cases. The core suite covers numeric
contracts, product backends checked against independent oracles, grade and
duality identities, rendering parity, expression provenance, model-layer
semantics, and compatibility manifests for the v1 surface. It also runs the
108 notebooks in the maintained gallery headlessly (15 of them annotation
lessons) and executes the README and documentation examples. Release-workflow
tests keep companion versions, dependency floors, build artifacts and
publication paths synchronized.

Part of the core suite is not ordinary unit coverage but **externally grounded
algebraic identity checks**: each test class cites the published theorem,
equation or axiom it derives from, so a sign error in a product table fails
against an external derivation rather than against a previous Galaga release.

- **Chisolm reference suite** — 332 cases in the `test_chisolm_*` files,
  derived from Chisolm's *Geometric Algebra* (arXiv:1205.5935). It covers
  vector squares, the `uv = u·v + u∧v` decomposition, outer-product
  independence, grade change under inner and outer products, duality,
  involutions, commutators, projections, reflections, rotations and Lorentz
  boosts, citing numbered results such as Theorem 1–7, Eq. 1.4 and Eq. 2.61.
  Public-facade transformation contracts re-check those identities through the
  supported API.
- **Cohoe suite** — 105 cases in `test_cohoe.py`, derived from David Cohoe's
  *Rigorous Development of Geometric Algebra* (2024), covering identities that
  are new or stated differently from the Chisolm set.

These reference-derived suites sit alongside algebra-independent oracles (a
packed reference product implementation and an independent Taylor series for
the exponential), randomized identity and round-trip checks, and frozen
rendering oracles used for compatibility.

## Under the hood

A multivector stores `2**n` real `float64` coefficients in the native exterior
basis, and the metric is a symmetric Gram matrix. Products use selectable
backends (packed, lazy, reference) behind one public API; the numeric core is
independent of names, expressions and rendering. Design decisions are
recorded as architecture decision records in `docs/adrs` and
`docs/core/adrs`, with the suite inventory above as the executable contract.
