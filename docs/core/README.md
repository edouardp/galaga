# Galaga Numeric Core Documentation

`galaga.core` is Galaga's real numeric geometric-algebra engine. Its canonical
metric is an immutable Gram matrix. These documents describe the
implementation, its mathematical conventions, and the boundary between the
numeric engine and Galaga's facade, presentation, and expression layers.

## Start here

- [Implementation overview](implementation-overview.md) is the human-oriented
  tour of what was built, why it is divided into these components, and how the
  pieces cooperate.
- [Design principles](design-principles.md) explains the values that guide API
  and implementation choices.
- [Architecture](architecture.md) follows an algebra from construction through
  metadata, product backends, multivector operations, and derived metric
  matrices.
- [Correctness strategy](correctness-strategy.md) describes the independent
  oracles and proof ladder used by the test suite.
- [ADR-073](../adrs/073-move-the-numeric-core-into-galaga.md) records why the
  proven implementation moved into the `galaga.core` namespace.
- [Galaga 2 planning](../v2/README.md) indexes the normative core cutover plan,
  numeric test migration inventory, and architectural plans for the facade,
  presentation, expression, and compatibility layers above the core.

## Mathematical guides

- [Inner products, contractions, and interior products](inner-products-contractions-and-interior-products.md)
  compares the scalar, metric, Hestenes, Doran–Lasenby, contraction, and RGA
  families with examples.
- [From an orthogonal CGA basis to a native null basis](cga-null-basis-change.md)
  derives the conformal basis transformation and its outermorphism.
- [CGA null-pair scaling](cga-null-pair-scaling.md) compares common normalized
  null-pair conventions.
- [Native-null conformal geometric algebra](../cga/README.md) describes the
  validated model layer, embedding, direct objects, semantic operations, and
  transformation recipes built on this core.
- [SPEC-005: Numeric functions](specs/SPEC-005-numeric-functions.md) is also the
  concise reference for square-root, exponential, logarithm, outer-series,
  and real-branch domains. Checked scalar conversion is specified in
  [SPEC-002](specs/SPEC-002-multivector-representation-and-operators.md).

## Specifications

Specifications state observable behavior that tests should enforce:

- [Specifications index](specs/README.md)
- [SPEC-001: Algebra construction and metric metadata](specs/SPEC-001-algebra-construction-and-metric.md)
- [SPEC-002: Multivector representation and operators](specs/SPEC-002-multivector-representation-and-operators.md)
- [SPEC-003: Product and duality conventions](specs/SPEC-003-product-and-duality-conventions.md)
- [SPEC-004: Product backend selection and diagnostics](specs/SPEC-004-product-backends.md)
- [SPEC-005: Numeric functions](specs/SPEC-005-numeric-functions.md)

## Architectural decisions

[Architectural Decision Records](adrs/README.md) preserve the rationale behind
decisions that are easy to lose when reading code alone. They describe the
canonical Gram metric, exterior-basis storage, scalable product backends,
explicit convention families, bracket scaling, the numeric-core boundary, and
the current inverse and analytic-function strategies. Repository-level ADRs
record the facade and migration decisions above this scoped numeric history.

## Document types

| Type | Purpose | Authority |
|---|---|---|
| Guide | Explain concepts, tradeoffs, and examples | Informative |
| Specification | Define externally observable behavior | Normative |
| ADR | Record why one architectural option was selected | Normative for the decision |
| Roadmap | Track remaining work and sequencing | Planning |

When prose conflicts with executable behavior, treat the tests as evidence of
the current implementation and update the relevant specification and ADR in
the same change as the code.
