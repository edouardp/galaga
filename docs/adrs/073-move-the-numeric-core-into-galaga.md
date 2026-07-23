---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-073: Move the Numeric Core into the Galaga Package

## Context and problem statement

The standalone Gram repository proved the native Gram-matrix representation,
product backends, metric extensions, RGA operations, and numeric functions
needed for Galaga 2.0. Keeping that implementation in a separate distribution
would now create release coordination, duplicate repository infrastructure,
and make Galaga's fundamental numeric engine appear optional when it is not.

Galaga is already a multi-package repository. The numeric implementation needs
a distinct architectural boundary, but that boundary does not require another
repository or separately versioned Python distribution.

## Decision drivers

- Keep the proven numeric boundary independently importable and testable.
- Give Galaga one repository, version, and release unit for its essential
  implementation.
- Avoid breaking the existing Galaga 1.x API while migration is underway.
- Prevent presentation, expression, and compatibility concerns from entering
  the numeric implementation.
- Preserve the option for direct numeric use without the facade.

## Considered options

1. Keep Gram as a separately published dependency.
2. Add Gram as another top-level distribution in the Galaga monorepo.
3. Move the implementation into an internal `galaga.core` namespace.
4. Merge the implementation directly into the existing `galaga.algebra`
   module.

## Decision

Choose option 3.

The proven numeric implementation lives in `galaga.core`. It exposes its own
`Algebra`, `Multivector`, and named numeric operations and retains private
backend, metadata, and metric-extension modules beneath that namespace.
`galaga.core` has no dependency on the legacy algebra, expression system,
notation, blade conventions, or rendering.

This move is initially additive:

- `galaga.Algebra` and `galaga.Multivector` continue to resolve to the existing
  1.x implementation;
- the transitional `galaga.gram_bridge` facade delegates to `galaga.core`;
- the complete numeric-core test suite runs from the Galaga repository; and
- Galaga no longer declares or resolves an external `gram` dependency.

The standalone Gram repository is retained temporarily as implementation
provenance. It is not a runtime dependency or the continuing source of truth.
It may be archived after the in-package core, tests, and documentation have
been verified and future development is occurring solely in Galaga.

A later cutover will make the composition facade the top-level Galaga API and
remove the legacy multiplication engine. That cutover is a separate phase and
is not implied by moving the core.

ADR-075 subsequently promotes the implementation from the transitional
`galaga.gram_bridge` name to `galaga.facade`. The bridge now re-exports the
facade objects; this follow-up does not change the `galaga.core` boundary or
perform the eventual top-level cutover.

ADR-088 subsequently defines how the resulting major release is published.
The numeric core and facade do not have a separate version: the Galaga 2 train
is explicitly released as `2.0.0a1`, `2.0.0a2`, `2.0.0b1`, `2.0.0rc1`, and
finally the distinct stable `2.0.0` release.

## Consequences

- Good, because Galaga 2.0 has one essential package and one coordinated
  release.
- Good, because `galaga.core` remains usable and testable without presentation
  or expression overhead.
- Good, because the legacy and replacement implementations can coexist during
  differential testing.
- Good, because companion packages can migrate to explicit public core or
  facade contracts inside one repository.
- Cost, because the package temporarily contains two numeric implementations.
- Cost, because the historical `gram_bridge` name is transitional and should
  be removed or renamed when the facade becomes the top-level API.
- Risk, because accidental imports from `galaga.core` into legacy or
  presentation modules could blur the boundary; import-direction tests should
  guard it.
