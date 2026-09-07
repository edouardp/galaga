---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-008: Commutator Family — Four Named Functions, No Flags

Historical v1 decision: v2 uses unscaled `lie_bracket` and `jordan_product`,
with `half_commutator` and `half_anticommutator` for the half-scaled forms.
The v2 structural simplifier does not perform the grade-aware Jordan-to-inner
rewrite below. [ADR-099](099-symbolic-contracts-and-curated-unary-properties.md)
records computed v1 evidence and the current regression contracts; see also
[ADR-074](074-long-operation-names-are-canonical.md) and
[ADR-077](077-optional-expression-provenance.md).

## Context and Problem Statement

The original `commutator(a, b)` returned `½(ab - ba)` — the half-commutator
(GA convention). But in most of mathematics and physics, the "commutator" is
`ab - ba` without the factor of ½. This is ambiguous to new users and violates
the project's design goal of being explicit.

Additionally, the anticommutator had the same issue, and the related Lie bracket
and Jordan product were missing entirely.

## Decision Drivers

* The ½ factor is not a formatting choice — it changes the algebraic convention
* A boolean flag like `commutator(a, b, half=True)` hides the distinction
* Two named functions are more readable than one function with a mode flag
* Bivectors form a Lie algebra under the half-commutator (clean structure constants)
* The Jordan product (½ of anticommutator) equals the inner product for vectors

## Considered Options

1. Keep `commutator` as ½(ab - ba), add `raw_commutator` for ab - ba
2. Single function with `half=True/False` flag
3. Four named functions: `commutator`, `lie_bracket`, `anticommutator`, `jordan_product`

## Decision Outcome

Chosen option: "Four named functions" with clear mathematical definitions:

```python
commutator(a, b)      = ab - ba          # [a, b]
anticommutator(a, b)  = ab + ba          # {a, b}
lie_bracket(a, b)     = ½(ab - ba)       # ½[a, b]
jordan_product(a, b)  = ½(ab + ba)       # ½{a, b}
```

This is a **breaking change** — `commutator` and `anticommutator` no longer
include the ½ factor.

### Symbolic Rendering

The notation makes the relationship between each pair immediately obvious:

| Function | Unicode | LaTeX |
|---|---|---|
| `commutator` | `[a, b]` | `[a, b]` |
| `lie_bracket` | `½[a, b]` | `½[a, b]` |
| `anticommutator` | `{a, b}` | `{a, b}` |
| `jordan_product` | `½{a, b}` | `½{a, b}` |

### Simplification

The symbolic layer simplifies `jordan_product(a, b)` to `hestenes_inner(a, b)`
when both arguments are known to be grade 1 (vectors), since for vectors
`½(ab + ba) = a · b`.

### Consequences

* Good, because `commutator(a, b)` now matches the standard mathematical definition
* Good, because `lie_bracket(a, b)` is self-documenting — it's the Lie algebra operation
* Good, because the ½ prefix in symbolic rendering shows the relationship visually
* Good, because `jordan_product` → inner product simplification works for vectors
* Bad, because this is a breaking change for existing users of `commutator`

## More Information

* The geometric product decomposes as: `ab = lie_bracket(a, b) + jordan_product(a, b)`
* Bivectors close under `lie_bracket` as a Lie algebra (isomorphic to su(2) in 3D)
* The Jordan product gives the symmetric/metric part of the geometric product
