---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-164: Square Roots in an All-Null Exterior Algebra

## Context

ADR-053 made `sqrt` available for scalar values and Study numbers $a+N$
whose nonscalar part has scalar square. This includes a single null blade but
excludes mixed-grade values such as $1+e_1+e_{23}$ in
$\mathrm{Cl}(0,0,3)$. That value has a real square root, so the Study-number
restriction is incomplete for an all-null algebra.

The Clifford algebra of the zero quadratic form is the exterior algebra
$\Lambda(V)$ [1]. Let

$$
J=\bigoplus_{k=1}^{n}\Lambda^k(V)
$$

be its positive-grade ideal. Exterior degree gives $J^{n+1}=0$: every product
of $n+1$ positive-grade factors has degree at least $n+1$ and vanishes [2].
Thus every $N\in J$ is nilpotent, including mixed-grade values whose square
is neither zero nor scalar.

## Mathematical argument

For $x=a+N$ with $a>0$, put $u=N/a$. The generalized binomial series [3]
defines the finite polynomial

$$
P(u)=\sum_{k=0}^{n}\binom{1/2}{k}u^k,
\qquad
\binom{1/2}{0}=1,
\qquad
\binom{1/2}{k}
=\binom{1/2}{k-1}\frac{3/2-k}{k}.
$$

The formal identity

$$
\left(\sum_{k\geq0}\binom{1/2}{k}t^k\right)^2=1+t
$$

may be evaluated at $u$ without a convergence assumption because
$u^{n+1}=0$. Consequently,

$$
r=\sqrt a\,P(u)
\qquad\Longrightarrow\qquad
r^2=a+N=x.
$$

Commutativity of the full exterior algebra is unnecessary. Every term is a
power of the single element $u$, so $u^ju^k=u^{j+k}=u^ku^j$, while scalars
are central.

This is the **unique** square root with positive scalar coefficient. Any
such root has scalar coefficient $b=\sqrt a$. Suppose $r=b+R$ and $s=b+S$
are two roots with $R,S\in J$, and put $D=R-S\in J$. If $D\in J^d$, then

$$
0=r^2-s^2=2bD+DR+SD\equiv2bD\pmod{J^{d+1}}.
$$

Because $2b\ne0$, this implies $D\in J^{d+1}$. Starting at $d=1$ and
repeating through $J^{n+1}=0$ gives $D=0$.

For $a<0$, no real square root exists: the scalar coefficient of any $y^2$
is the square of the scalar coefficient of $y$. At $a=0$, zero has the
conventional root zero, while nonzero inputs have no canonical principal
branch. Some have no root, such as a grade-one vector, whereas others have
multiple roots. In four dimensions,

$$
e_{1234}=\left(\frac{e_{12}+e_{34}}{\sqrt2}\right)^2.
$$

Both signs of the displayed root give the same square.

## Decision

Extend the existing geometric `sqrt` for algebras whose entire stored Gram
matrix is zero. For positive scalar part, evaluate the finite binomial
polynomial with **geometric products**, and verify that its square matches
the input within the existing numeric tolerance. Preserve the scalar and
Study-number branches for all other metrics. Return zero for zero; reject
all-null values with negative scalar part or nonzero values with zero scalar
part using an explicit real-branch error.

The zero-scalar rejection does not imply that a square root does not exist;
it means that no canonical real principal root is selected for that domain.

This changes the restricted domain recorded in ADR-053 and SPEC-005; it does
not add an `outer_sqrt` operation. In an all-null algebra geometric and
exterior products coincide. On other metrics, a wedge-product square root
would solve a different equation and needs its own decision if requested.

## Consequences

Every $a+N$ with $a>0$ in $\mathrm{Cl}(0,0,n)$ has a supported principal
real square root, including nonscalar $N^2$. Existing Study-number results
remain the same mathematical branch. The exact proof concerns real
coefficients; the float64 implementation retains its residual check and may
reject numerically unresolved inputs.

Regression tests must compare the root's geometric square with the input,
include mixed odd and even grades with nonzero nonscalar square, verify the
positive-scalar branch and its corresponding negative root on a
representative case, and exercise zero, negative-scalar, and zero-scalar
nonzero boundaries.

## References

1. [SageMath Clifford algebra documentation](https://doc.sagemath.org/html/en/reference/algebras/sage/algebras/clifford_algebra.html), on $\mathrm{Cl}(V,0)=\Lambda(V)$.
2. [Y. Sharifi, *The exterior algebra*](https://ysharifi.wordpress.com/2022/04/04/the-exterior-algebra/), theorem (iii) on products of $n+1$ zero-constant elements.
3. [E. W. Weisstein, *Binomial Series*, MathWorld](https://mathworld.wolfram.com/BinomialSeries.html), generalized binomial coefficients and expansion.
