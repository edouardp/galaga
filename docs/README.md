# Galaga Documentation

This index distinguishes current Galaga 2 documentation from historical
migration material. Public behavior is defined by the current package guides,
implemented specifications, accepted ADRs, and tests. Historical plans explain
how the replacement was carried out; they are not alternate APIs.

## Use Galaga 2

- [Package guide](../packages/galaga/README.md): installation, construction,
  products, expressions, presentation, and protocols.
- [Galaga 1 to 2 migration guide](v2/migration-guide.md): concrete source
  changes and compatibility boundaries.
- [Native-null CGA](cga/README.md): conformal model, objects, components,
  norms, and transformations.
- [Interactive CGA visualization](../packages/galaga_anywidget/README.md):
  synchronized AnyWidget views and Marimo-reactive construction.
- [Rigid Geometric Algebra](rga-convention-layer.md): Lengyel RGA convention,
  model semantics, measurements, and constraints.
- [Rotors, generators, and spinors](rotors-generators-spinors.md): mathematical
  distinctions used by the API and examples.
- [Inner products, contractions, and interior products](core/inner-products-contractions-and-interior-products.md):
  the explicit product families and their behavior across representative
  algebras.

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

Each index or document should state when it is historical. Do not copy an API
example from those records without checking the current package guide or
migration guide.
