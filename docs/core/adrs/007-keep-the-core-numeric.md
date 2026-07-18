---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-007: Keep the Algebra Core Numeric and Presentation-Independent

## Context and problem statement

Galaga's existing `Multivector` combines numeric coefficients with names,
expression trees, symbolic propagation, rendering, and notebook display state.
That makes the numeric engine harder to replace: product code and companion
packages can accidentally depend on presentation internals.

Galaga needs a foundation whose correctness can be established solely from
metrics and coefficient arrays.

## Decision drivers

- Make the Gram-native engine independently testable.
- Prevent expression tracking from affecting numeric semantics or performance.
- Give rendering and notebook integrations a clean dependency direction.
- Keep NumPy as the only runtime dependency.
- Allow the future facade to evolve without rewriting products.

## Considered options

1. Port Galaga's combined numeric and expression-aware multivector unchanged.
2. Create separate numeric and symbolic multivector public types.
3. Build a numeric value core and let Galaga attach names and expression state
   above it.

## Decision outcome

`galaga.core` contains only real numeric algebras, immutable numeric multivectors, and
named numeric operations. It has no naming, notation, LaTeX, expression-node,
simplification, or notebook dependencies.

The numeric boundary includes checked `float(multivector)` conversion for
scalar values and explicit `.data` access for coefficient arrays. It does not
include NumPy array/ufunc protocol dispatch, which could ambiguously treat a
multivector as one scalar or as an unstructured array.

The Galaga facade may wrap or annotate these values, but dependency flow
must point toward `galaga.core`. The core must not import the facade or inspect symbolic
state to decide how to compute.

The public API favors long, convention-explicit names. A compatibility facade
may add aliases, rendering metadata, and expression tracking without changing
the coefficient result.

Application-level geometry helpers also belong above this boundary when they
only compose existing numeric operations. This follow-on distinction is
recorded in
[ADR-010](010-separate-numeric-functions-from-geometry-helpers.md).

## Consequences

- Good, because numeric laws can be tested without rendering fixtures.
- Good, because all values have concrete data and predictable cost.
- Good, because the core remains framework-independent.
- Cost, because the current `repr` is intentionally minimal.
- Cost, because Galaga integration needs an adapter rather than a direct file
  replacement.
