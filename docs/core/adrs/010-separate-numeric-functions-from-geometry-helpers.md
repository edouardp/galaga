---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-010: Separate Numeric Functions from Geometry Helpers

## Context

The Galaga compatibility inventory grouped two different kinds of operation:

- functions that require transcendental evaluation, infinite-series
  convergence, or real branch selection; and
- geometry conveniences that are short finite compositions of operations the
  numeric core already exposes.

Treating both groups as numeric-core parity would grow the public surface
without adding equivalent numerical capability. It would also make the core
responsible for application-level choices such as rotor angle sign and the
meaning of a projection target.

## Decision

`galaga.core` exposes scalar and Study-number square roots, geometric
exponential, Study-rotor logarithm, and the outer transcendental family.
These form one analytic numeric surface: the square roots, exponential,
logarithm, outer exponential, outer sine, and outer cosine own algorithms or
branch behavior; outer tangent is their conventional checked quotient.

Do not add `Algebra.rotor`, `project`, `reject`, `reflect`, or compatibility
aliases to the core for parity alone. They remain candidates for a geometry
helper module or the Galaga facade, where their formulas can compose `exp`,
contractions, geometric products, and `inverse`.

## Consequences

- Good, because the core gains the missing numerical machinery without
  accumulating every convenient spelling from its consumers.
- Good, because geometry helpers can choose domain-specific validation and
  conventions without changing the numeric kernel.
- Good, because symbolic and expression-tree layers can wrap the same numeric
  functions without becoming dependencies of `galaga.core`.
- Cost, because users wanting the deferred conveniences must currently write
  their short defining expressions directly.
- Cost, because compatibility facades must decide which aliases and helper
  conventions they promise.

## Related decision

[ADR-011](011-evaluate-numeric-functions-with-explicit-real-branches.md)
records how the selected numeric functions are evaluated.
