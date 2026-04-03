---
status: accepted
date: 2026-04-03
deciders: edouard
---

# ADR-051: Algebra Scalar Constants and Fractions

## Context and Problem Statement

Users building physics notebooks need named scalar values (π, ℏ, c) that
render symbolically in expressions. Writing `alg.scalar(np.pi).name(latex=r"\pi")`
every time is verbose. Similarly, fractions like ½ require
`alg.scalar(1).name("1") / alg.scalar(2).name("2")`.

## Decision Outcome

Add convenience properties and methods to `Algebra`:

### Constants

| Property | Value | LaTeX |
|---|---|---|
| `alg.pi` | π | `\pi` |
| `alg.tau` | 2π | `\tau` |
| `alg.e` | Euler's e | `e` |
| `alg.sqrt2` | √2 | `\sqrt{2}` |
| `alg.h` | 6.626e-34 | `h` |
| `alg.hbar` | 1.055e-34 | `\hbar` |
| `alg.c` | 299792458 | `c` |

### Fractions

`alg.fraction(1, 2)` / `alg.frac(1, 2)` — returns a lazy MV that renders
as `\frac{1}{2}`.

### Implementation

Constants are properties that return fresh named lazy scalars on each access.
They are NOT expression tree nodes — `alg.sqrt2` is a `Sym` with the string
name `\sqrt{2}`, not a `Sqrt(Scalar(2))` node. This means:

- They render correctly in LaTeX
- They participate in lazy expressions
- They do NOT simplify symbolically (e.g. `sqrt2 * sqrt2` won't simplify to 2)

This is acceptable because these are leaf values, not expressions to be
manipulated. Users who need symbolic simplification can build proper
expression trees with `scalar_sqrt()`.

### Consequences

- Good, because common constants are one property access away
- Good, because they render with proper LaTeX names
- Good, because `alg.frac(1, 2)` eliminates verbose fraction construction
- Neutral, because constants are tied to an algebra (needed for MV context)
- Neutral, because no symbolic simplification of constant expressions
