---
status: accepted
date: 2026-07-04
deciders: edouard
---

# ADR-070: Pedagogical and Convention-Explicit Scope

## Context and Problem Statement

Galaga increasingly covers areas where the geometric algebra community does not
use one universal terminology or one universal set of definitions. Examples
include inner products, contractions, duals, complements, regressive products,
spinor conventions, and matrix representations.

Some libraries resolve this by choosing one convention and optimizing for a
compact API. Other libraries prioritize performance and expose only the
operations needed by a target application domain.

Galaga has a different purpose. It is currently a pedagogical library first,
with a secondary goal of being explicit about convention choices and making the
range of coherent GA opinions available under named operations.

## Decision Drivers

* Users should be able to learn by comparing definitions directly in code.
* Conflicting GA conventions should be represented explicitly rather than
  hidden behind one overloaded name.
* Names should identify the mathematical convention being used.
* Performance matters only after correctness, clarity, and convention
  transparency.
* Adding a named operation can be worthwhile even when an equivalent expression
  can be written from existing primitives.

## Considered Options

1. Performance-first library: minimize allocations, operations, and convention
   variants.
2. Minimal-convention library: choose one convention per concept and omit the
   alternatives.
3. Pedagogical, convention-explicit library: choose documented defaults but
   expose other coherent conventions under explicit names.

## Decision Outcome

Chosen option: "Pedagogical, convention-explicit library".

Galaga should prefer APIs that make the mathematics inspectable and
distinguish competing conventions by name. This includes exposing multiple
named operations for concepts that are often collapsed together in notation,
such as inner products, contractions, duals, complements, and matrix/spinor
representations.

This does not mean every proposed operation belongs in the public API. The bar
is that the operation should represent a coherent mathematical convention, a
common literature convention, or a useful teaching comparison. If it meets that
bar, clarity is a stronger reason to add it than micro-performance is to omit
it.

### Consequences

* Good, because Galaga can serve as a map of the GA convention landscape.
* Good, because notebooks and docs can compare definitions directly using code.
* Good, because contested terms are turned into explicit function names.
* Neutral, because some APIs will overlap algebraically.
* Bad, because the public surface becomes larger than a minimal application
  library.
* Bad, because users may need guidance on which operation to choose.

## Implications

When reviewing new operation proposals:

* Ask whether the operation teaches or disambiguates a real convention.
* Prefer named functions over mode flags for convention choices.
* Do not reject an operation merely because it can be composed from existing
  primitives.
* Do not make a convention the default solely because it is faster.
* Document default choices and alternatives together.

Performance improvements are still welcome when they preserve these goals.
Precomputed tables, cached data, and fast paths are appropriate implementation
details, but they should not obscure which mathematical operation is being
performed.
