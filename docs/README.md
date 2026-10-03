# Galaga Documentation

This index distinguishes current Galaga 2 documentation from historical
migration material. Public behavior is defined by the current package guides,
implemented specifications, accepted ADRs, and tests. Historical plans explain
how the replacement was carried out; they are not alternate APIs.

## Start learning

Follow the [Galaga 2 notebook lessons](../examples/galaga_v2/README.md) in
this order: [construct an algebra](../examples/galaga_v2/algebra_construction.py),
[calculate with values and expressions](../examples/galaga_v2/eager_values_and_expressions.py),
[choose a presentation](../examples/galaga_v2/presentation_contexts.py), then
[customize notation](../examples/galaga_v2/custom_functional_notation.py).
The [numeric-core lesson](../examples/galaga_v2/numeric_core.py) explains the
engine beneath those examples. The notebook README continues into products,
rotors, geometric models, and visualization by topic.

These Marimo notebooks require **Python 3.14** because their dynamic Markdown
uses t-strings. Open the gallery from a repository checkout with
`make run-marimo`. If you use **Python 3.11–3.13**, the installed `galaga`
package and its [quick start](../packages/galaga/README.md#quick-start) work
without the notebook helper. Follow the same first steps in a Python REPL or
script:

```shell
python -m pip install --pre "galaga>=2.0.0b1,<3"
```

```python
from galaga import Algebra, outer_product

alg = Algebra(2)
e1, e2 = alg.basis_vectors(expr=True)
u = (2 * e1 + e2).named("u")
v = (e1 + 3 * e2).named("v")
area = outer_product(u, v)
assert area == 5 * (e1 ^ e2)
print(area.display("expr/unicode"))
print(area.display("value/unicode"))
```

Next, use [metric construction](../packages/galaga/README.md#define-the-metric)
to try another signature, [named operations](../packages/galaga/README.md#quick-start)
to compare products, and [presentation and notebook tables](../packages/galaga/README.md#rendering-and-notebook-tables)
to display the same value in different forms. This path needs only the core
`galaga` distribution and Python 3.11 or newer.

## Use Galaga 2

- [Package guide](../packages/galaga/README.md): installation, construction,
  products, expressions, presentation, and protocols.
- [Galaga 1 to 2 migration guide](v2/migration-guide.md): concrete source
  changes and compatibility boundaries.
- [Native-null CGA](cga/README.md): conformal model, objects, components,
  norms, and transformations.
- [Interactive CGA visualization](../packages/galaga_anywidget/README.md):
  synchronized AnyWidget views and Marimo-reactive construction.
- [Semantic annotations](../packages/galaga_annotation/README.md): highlights,
  labels, braces, callouts, and matrix annotations for teaching renderings,
  defined by [SPEC-015](specs/SPEC-015-expression-and-matrix-annotations.md).
- [Rigid Geometric Algebra](rga-convention-layer.md): Lengyel RGA convention,
  model semantics, measurements, and constraints.
- [Rotors, generators, and spinors](rotors-generators-spinors.md): mathematical
  distinctions used by the API and examples.
- [Logarithms and rotor generators notebook](../examples/algebra/logarithms_and_generators.py):
  computed examples, branch boundaries, and an interactive comparison of
  algebraic and geometric paths.
- [Inner products, contractions, and interior products](core/inner-products-contractions-and-interior-products.md):
  the explicit product families and their behavior across representative
  algebras.
- [Duality and exterior complements](what_is_dual.md): general-Gram formulas,
  Euclidean-only simplifications, mixed grades and degenerate metrics.
- [One spinor, three representations notebook](../examples/matrix/spinors_ideals_and_chirality.py):
  ideals, columns, reflections, the rotation double cover, and chirality in
  Dirac/Weyl bases, including real-GA projections and projected-spinor roundtrips.

## Understand the implementation

- [Galaga 2 architecture and status](v2/README.md)
- [Numeric core](core/README.md)
- [Presentation configuration](v2/presentation-configuration.md)
- [Expression provenance](v2/expression-provenance.md)
- [Semantic rendering](v2/rendering-implementation.md)
- [Matrix integration](v2/matrix-migration.md)
- [Optional integrations](v2/integration-migration.md)
- [Design principles](DESIGN_DECISIONS.md)
- [Architectural Decision Records](adrs/README.md)

## Release Galaga

- [Release process](RELEASE_PROCESS.md) is the operational source of truth.
- [Type-checking status](PYREFLY_STATUS.md) records the blocking local type
  gate and its latest measured checkpoint; no CI is required for release.
- [Post-a4 documentation review](v2/documentation-review.md) records corrected
  guidance, executable examples, validation results and historical-document boundaries.
- [Galaga 2 core cutover plan](v2/core-cutover-plan.md) records phase gates,
  including the stable-release removal gate.
- [Historical initial PyPI plan](PYPI_RELEASE_PLAN.md) is retained for context
  and explicitly redirects to the current release process.

## Historical and planning records

The following retain chronology and may contain old namespaces or source
examples intentionally:

- `docs/v2/*-plan.md`, migration inventories, parity reports, and performance
  baselines;
- `docs/proposals/`;
- the legacy presentation specifications under `docs/specs/`; and
- superseded or historical ADRs.

Root-level conversation transcripts and old library surveys are also historical
material, not an unimplemented feature list. The
[capability roadmap](v2/galaga-replacement-roadmap.md) separates the remaining
release steps from post-2.0 proposals.

Each index or document should state when it is historical. Do not copy an API
example from those records without checking the current package guide or
migration guide.
