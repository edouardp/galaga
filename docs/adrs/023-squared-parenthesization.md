---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-023: Parenthesization in Squared Rendering

## Context and Problem Statement

The `Squared` expression node renders `x²`. When `x` is a sum like
`a + b`, the output `a + b²` is mathematically wrong — it reads as
`a + (b²)` rather than `(a + b)²`.

## Decision Outcome

The `Squared` node wraps its operand in parentheses when it is an `Add`
or `Sub` node. Single-term expressions (names, products, scalars) are
not wrapped.

```
squared(v)       →  v²
squared(a + b)   →  (a + b)²
squared(a - b)   →  (a - b)²
squared(a * b)   →  ab²        (no parens — product binds tighter)
```

LaTeX uses `\left(...\right)` for the parenthesized form.

### Consequences

* Good, because the rendered output is mathematically unambiguous
* Good, because single-term expressions stay clean (`v²` not `(v)²`)
