---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-003: Explicit Inner Product Variants

## Context and Problem Statement

There are at least four different "inner product" conventions in geometric
algebra literature. Which one should the `|` operator use, and how do we
expose the others?

## Decision Drivers

* Different textbooks use different conventions
* Users coming from Hestenes vs Dorst vs Doran & Lasenby expect different behaviour
* A single `inner()` function with a mode flag hides important distinctions

## Considered Options

1. Single `inner()` with a mode parameter
2. One function per variant, each with a clear name
3. Only expose one variant

## Decision Outcome

Galaga uses geometric-algebra terminology as its primary vocabulary. Where the
GA literature has competing conventions, Galaga chooses one documented default
and exposes the other conventions under explicit names.

Chosen option: "One function per variant" — `left_contraction`,
`right_contraction`, `hestenes_inner`, `doran_lasenby_inner`, `scalar_product`
are all first-class functions. The `|` operator maps to `doran_lasenby_inner`.

An `ip(a, b, mode="doran_lasenby")` convenience function is also provided for
users who want a single entry point. `dorst_inner` is an alias for
`doran_lasenby_inner`.

### Consequences

* Good, because no ambiguity — each function does exactly one thing
* Good, because users can import the specific convention they need
* Good, because `|` has a documented, fixed meaning
* Bad, because four function names to learn instead of one
