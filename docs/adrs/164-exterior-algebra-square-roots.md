---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-164: Square Roots in an All-Null Exterior Algebra

## Context

ADR-053 made `sqrt` available for scalar values and Study numbers `a + N`
whose nonscalar part has scalar square. This includes a single null blade but
excludes mixed-grade values such as `1 + e1 + e23` in `Cl(0,0,3)`. That value
has a real square root, so the Study-number restriction is incomplete for an
all-null algebra.

The Clifford algebra of the zero quadratic form is the exterior algebra
`Λ(V)` [1]. Let `J = ⊕_{k=1}^n Λ^k(V)` be its positive-grade ideal. Exterior
degree gives `J^(n+1) = 0`: every product of `n+1` positive-grade factors has
degree at least `n+1` and vanishes [2]. Thus every `N ∈ J` is nilpotent,
including mixed-grade values whose square is neither zero nor scalar.

## Mathematical argument

For `x = a + N`, `a > 0`, put `u = N/a`. The generalized binomial series [3]
defines the polynomial

```
P(u) = Σ[k=0..n] binom(1/2, k) u^k,
binom(1/2, 0) = 1,
binom(1/2, k) = binom(1/2, k-1) * (1/2 - k + 1) / k.
```

The formal identity `(Σ[k≥0] binom(1/2,k) t^k)^2 = 1+t` may be evaluated at
`u` without a convergence assumption because `u^(n+1)=0`. Consequently
`r = sqrt(a) P(u)` satisfies `r*r = a+N` exactly over the real exterior
algebra. No commutativity of the full algebra is assumed: every term is a
power of the one element `u`, and a scalar commutes with it.

This is the **unique** square root with positive scalar part. Any such root
has scalar coefficient `b = sqrt(a)`. If two roots first differ in degree
`d`, their squared difference in `J^d/J^(d+1)` is `2b` times that difference;
all products involving a positive-grade factor lie in `J^(d+1)`. Since
`2b != 0`, the degree-`d` difference vanishes. Induction through degree `n`
proves uniqueness.

For `a < 0`, no real square root exists: the scalar coefficient of any
`y*y` is the square of the scalar coefficient of `y`. At `a = 0`, zero has
the conventional root zero, while nonzero inputs have no canonical principal
branch. Some have no root (a grade-one vector), and others have multiple
roots: in four dimensions, `e1234 = ((e12 + e34)/sqrt(2))^2`.

## Decision

Extend the existing geometric `sqrt` for algebras whose entire stored Gram
matrix is zero. For positive scalar part, evaluate the finite binomial
polynomial with **geometric products**, and verify that its square matches
the input within the existing numeric tolerance. Preserve the scalar and
Study-number branches for all other metrics. Return zero for zero; reject
all-null values with negative scalar part or nonzero values with zero scalar
part using an explicit real-branch error.

This changes the restricted domain recorded in ADR-053 and SPEC-005; it does
not add an `outer_sqrt` operation. In an all-null algebra geometric and
exterior products coincide. On other metrics, a wedge-product square root
would solve a different equation and needs its own decision if requested.

## Consequences

Every `a + N` with `a > 0` in `Cl(0,0,n)` has a supported principal real
square root, including nonscalar `N*N`. Existing Study-number results remain
the same mathematical branch. The exact proof concerns real coefficients;
the float64 implementation retains its residual check and may reject
numerically unresolved inputs.

Regression tests must compare `r*r` with the input, include mixed odd/even
grades with nonzero nonscalar square, verify uniqueness by scalar sign on a
representative case, and exercise zero, negative-scalar, and zero-scalar
nonzero boundaries.

## References

1. [SageMath Clifford algebra documentation](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/clifford_algebra.html), on `Cl(V,0) = Λ(V)`.
2. [Y. Sharifi, *The exterior algebra*](https://ysharifi.wordpress.com/2022/04/04/the-exterior-algebra/), theorem (iii) on products of `n+1` zero-constant elements.
3. [E. W. Weisstein, *Binomial Series*, MathWorld](https://mathworld.wolfram.com/BinomialSeries.html), generalized binomial coefficients and expansion.
