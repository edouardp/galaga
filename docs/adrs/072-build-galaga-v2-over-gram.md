---
status: superseded
date: 2026-07-18
deciders: edouard
superseded-by: ADR-073
---

# ADR-072: Build Galaga 2.0 over the Gram Numeric Core

> **Superseded by [ADR-073](073-move-the-numeric-core-into-galaga.md).** The
> composition boundary remains accepted, but the numeric core now lives in the
> `galaga.core` namespace instead of a separately distributed `gram` package.

## Context and problem statement

Galaga 1.x combines its numeric Clifford engine with naming, expression
tracking, notation, and rendering. Its multiplication-table representation is
limited to orthogonal metrics, while the separate Gram project now provides a
tested numeric core for real symmetric Gram matrices, including nonorthogonal
and degenerate algebras.

Galaga needs to adopt that core without moving presentation state into Gram or
maintaining two numeric engines indefinitely. Because this changes the
fundamental `Algebra` and `Multivector` implementation and corrects some legacy
API semantics, it requires a major Galaga release.

## Decision drivers

- Keep one independently testable numeric implementation.
- Support native nonorthogonal Gram matrices.
- Preserve Galaga's naming, notation, expression, and teaching features as
  independently configurable outer layers.
- Prove compatibility before changing Galaga's default exports.
- Make the breaking implementation boundary visible through semantic
  versioning.

## Decision

The `galaga_v2` branch targets Galaga 2.0.0 and declares Gram as a required
dependency. Galaga and Gram both support Python 3.11 and later; only the
optional `galaga_marimo` package requires Python 3.14 for t-strings. Companion
packages retain their own versions and migrate separately.

Galaga's public `Algebra` and `Multivector` will be composition facades around
`gram.Algebra` and `gram.Multivector`; they will not subclass Gram values and
Gram will not import Galaga. Numeric operations unwrap operands, call one
public named Gram operation, and wrap the result. Optional names, expression
provenance, blade conventions, notation, and rendering remain Galaga-owned
state above that boundary.

Migration starts with an opt-in `galaga.gram_bridge` package. Existing Galaga
exports continue to use the 1.x engine until applicable numeric tests have
been run with the facade substituted for the old implementation. The final
cutover will re-export the facade as `galaga.Algebra` and
`galaga.Multivector`, then remove the old multiplication engine.

The repository uses a local editable Gram source during joint development.
Published Galaga metadata retains an ordinary versioned `gram>=0.1.0`
dependency; a releasable Gram distribution must therefore exist before
Galaga 2.0 is published.

## Consequences

- Good, because Galaga and direct Gram users share the same numeric behavior.
- Good, because Galaga can add presentation and expression features without
  adding overhead or dependencies to Gram.
- Good, because the opt-in bridge permits differential and compatibility
  testing before cutover.
- Cost, because facade allocation and dispatch add overhead that must be
  measured independently from Gram.
- Risk, because the local editable source can hide packaging omissions; clean
  wheel-install tests are required before release.
- Follow-up, because `galaga_matrix`, Marimo integration, and rich rendering
  must migrate through public facade contracts before the old engine is
  removed.
