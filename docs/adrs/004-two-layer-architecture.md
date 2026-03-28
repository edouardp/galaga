---
status: superseded
date: 2026-03-25
deciders: edouard
superseded-by: ADR-018
---

# ADR-004: Two-Layer Architecture (Numeric + Symbolic)

> **Note:** This ADR is partially superseded by [ADR-018](018-unified-naming-evaluation-semantics.md).
> The two modules (`galaga.algebra` and `galaga.symbolic`) still exist, but the boundary
> has shifted: `Multivector` now handles both naming and lazy evaluation natively.
> The `Expr` tree is an internal implementation detail, not a public type users
> work with directly. `sym()` returns a `Multivector`, not an `Expr`.

## Context and Problem Statement

Users need both fast numeric computation and pretty symbolic rendering
(LaTeX, Unicode). How do we provide both without coupling them?

## Decision Drivers

* Most users only need numeric computation
* Symbolic rendering is essential for notebooks but adds complexity
* The symbolic layer should not slow down numeric code
* Users should be able to mix numeric and symbolic seamlessly

## Considered Options

1. Single layer that always builds expression trees
2. Two separate layers with the symbolic layer as opt-in
3. Separate symbolic library with no code sharing

## Decision Outcome

Chosen option: "Two separate layers" — `galaga.algebra` is the numeric core,
`galaga.symbolic` is an opt-in expression-tree layer.

Every symbolic function is a drop-in replacement: it detects `Expr` arguments
and builds trees, but passes plain `Multivector` arguments straight through
to the numeric core with zero overhead.

### Consequences

* Good, because `from galaga import *` gives fast numeric code with no symbolic overhead
* Good, because `from galaga import symbolic as sym` opts into symbolic rendering
* Good, because the same code works with both — just wrap inputs with `sym.sym()`
* Bad, because two parallel APIs to maintain
