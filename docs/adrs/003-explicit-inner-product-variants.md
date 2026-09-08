---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-003: Explicit Inner Product Variants

The retained v1 engine did implement a mode dispatcher despite this intended
direction. Its thirteen dispatch tests now have public v2 owners, with the
old observations archived rather than the dispatcher restored; see
[ADR-112](112-explicit-inner-product-contracts-outlive-mode-dispatch.md).

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

Galaga deliberately does not provide an `ip(a, b, mode=...)` dispatcher. A
user who wants a short functional spelling can create an ordinary local alias
without hiding the convention from the surrounding code:

```python
from galaga import doran_lasenby_inner as ip
```

`dorst_inner` remains an alias for `doran_lasenby_inner`.

### Consequences

* Good, because no ambiguity — each function does exactly one thing
* Good, because users can import the specific convention they need
* Good, because `|` has a documented, fixed meaning
* Bad, because four function names to learn instead of one
