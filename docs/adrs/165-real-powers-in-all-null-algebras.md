---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-165: Real Powers in All-Null Algebras

## Context

ADR-007 restricts multivector `**` to integer exponents because a real
noninteger power has no general, single-valued real meaning in a Clifford
algebra. ADR-164 establishes a principal square root for an all-null algebra.
The same proof supports every finite real exponent, so retaining the
integer-only rule for that algebra would make `x ** 0.5` disagree with
`sqrt(x)`.

## Mathematical argument

For a zero Gram matrix, $\mathrm{Cl}(0,0,n)=\Lambda(V)$ [1]. Its
positive-grade ideal $J$ satisfies $J^{n+1}=0$ [2]. Write $x=a+N$ with
$N\in J$ and $a>0$. For every real $\alpha$, the generalized binomial
series [3] becomes the finite polynomial

$$
x^\alpha
=a^\alpha\sum_{k=0}^{n}\binom{\alpha}{k}(N/a)^k,
\qquad
\binom{\alpha}{0}=1,
\qquad
\binom{\alpha}{k}
=\binom{\alpha}{k-1}\frac{\alpha-k+1}{k}.
$$

There is no convergence condition on $N/a$: its power of order $n+1$ is
zero. The formal binomial identities therefore hold after substitution,
including $x^\alpha x^\beta=x^{\alpha+\beta}$ in exact arithmetic.
The scalar coefficient $a^\alpha$ uses the ordinary positive-real branch.
At $\alpha=1/2$ this is ADR-164's unique positive-scalar square root; at
$\alpha=-1$ it is the finite geometric inverse series. The formula uses
only powers of one element, so it does not assume that the full exterior
algebra is commutative.

The zero metric is the condition under which *every* positive-grade element
is guaranteed nilpotent. Other Clifford algebras can contain particular
nilpotent values, but this decision does not broaden their `**` domain.
For a nonzero zero-scalar value there is no uniform real principal power.
The zero value has the conventional $0^\alpha=0$ for $\alpha>0$ and
$0^0=1$; negative powers are undefined. Negative scalar part is outside
the selected positive-real branch, even where a particular rational power
could be given another real interpretation.

## Decision

Keep integer `**` behavior unchanged for every algebra. Accept a finite
real exponent supplied as a noninteger Python numeric type only when the
entire stored Gram matrix is zero. Use the finite binomial polynomial for
positive scalar part. Return zero for the zero multivector and positive
exponent, return identity for exponent zero, and reject negative exponents
of zero. Reject other all-null inputs outside the positive-scalar branch
with a clear `ValueError`. Continue to reject noninteger exponents on other
metrics with `TypeError`.

Factor the polynomial into one numeric helper shared by the all-null
branches of `sqrt` and `**`. Keep `sqrt`'s existing Study-number support
for other metrics. Preserve the exponent as a real expression parameter in
the facade, so `x ** 1.5` retains its displayed exponent.

This partially supersedes ADR-007 and extends ADR-164. It does not define
an `outer_power` operation for other metrics or select branches of a
general Clifford-algebra logarithm.

## Consequences

For positive-scalar all-null values, `x ** 0.5` and `sqrt(x)` agree,
`x ** 1.5` squares to `x ** 3`, and `x ** -1` retains the existing inverse
path. Float64 roundoff may prevent exact algebraic equalities; tests compare
coefficients within a numeric tolerance and cover the branch boundaries.

The exterior-algebra lesson compares the all-null behavior with a regular
metric, where integer powers still work but noninteger `**` remains
unavailable.

## References

1. [SageMath Clifford algebra documentation](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/clifford_algebra.html), on $\mathrm{Cl}(V,0)=\Lambda(V)$.
2. [Y. Sharifi, *The exterior algebra*](https://ysharifi.wordpress.com/2022/04/04/the-exterior-algebra/), theorem (iii) on products of $n+1$ zero-constant elements.
3. [E. W. Weisstein, *Binomial Series*, MathWorld](https://mathworld.wolfram.com/BinomialSeries.html), generalized binomial coefficients and expansion.
