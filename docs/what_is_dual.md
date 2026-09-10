# What is the Dual?

Galaga exposes several distinct operations. Do not infer a definition from
the word “dual” alone, or from a single Euclidean bivector example.

This guide describes the implemented Galaga 2 conventions. Older library
comparisons are historical observations in the
[operations survey](ga-library-operations-survey.md), not a current cross-library
API guarantee.

## The operations are different

| Operation | Galaga definition | Metric-dependent? | Degenerate metric? |
|---|---|---|---|
| `complement(A)` | Right exterior complement in the ordered native basis | No | Works |
| `uncomplement(A)` | Left exterior complement; inverse of the right complement | No | Works |
| `dual(A)` | $A\mathbin{\lfloor}I^{-1}$ | Yes | Raises `ValueError` |
| `undual(A)` | $A\mathbin{\lfloor}I$; inverse of `dual` | Yes | Raises `ValueError` |
| `right_hodge_dual(A)` | `complement(metric_apply(A))` | Yes | Defined, but may be noninvertible |
| `left_hodge_dual(A)` | `uncomplement(metric_apply(A))` | Yes | Defined, but may be noninvertible |

Here $I=e_1\wedge\cdots\wedge e_n$ is the native pseudoscalar.
For each native exterior basis blade $E$, $E\wedge\operatorname{complement}(E)=I$.
This basis-blade rule extends linearly; it does not say that
$A\wedge\operatorname{complement}(A)=I$ for arbitrary $A$.

Galaga's left contraction selects $\langle A_rB_s\rangle_{s-r}$ when $r\le s$,
without reversion. Other conventions insert reversion and consequently have
different signs. See the [product-family guide](core/inner-products-contractions-and-interior-products.md).

## Relating contraction, the metric and complement

Let $\mathcal G$ be the exterior extension of the stored Gram matrix:
`metric_apply` applies its compound matrices to each grade. For any multivector,

$$
A\mathbin{\lfloor}I
=\operatorname{complement}\!\left(\mathcal G(\widetilde A)\right).
$$

For homogeneous grade $r$, reversion is
$\widetilde A_r=(-1)^{r(r-1)/2}A_r$, so

$$
A_r\mathbin{\lfloor}I
=(-1)^{r(r-1)/2}\operatorname{complement}\!\left(\mathcal G(A_r)\right).
$$

When $I^2\ne0$, $I^{-1}=I/I^2$, hence

$$
\operatorname{dual}(A_r)
=\frac{(-1)^{r(r-1)/2}}{I^2}
 \operatorname{complement}\!\left(\mathcal G(A_r)\right).
$$

Only when the stored Gram matrix is the identity can the metric map be
dropped for every input. Thus the simpler sign-times-complement formulas are
orthonormal-Euclidean formulas, not general CGA/PGA/oblique-basis identities.
For mixed grades, use reversion rather than one grade-dependent sign.

```python
import numpy as np
from galaga import Algebra, complement, dual, left_contraction, metric_apply, reverse

algebra = Algebra(gram=[[2.0, 0.5], [0.5, 1.0]])
A = algebra.multivector([1.0, 2.0, 3.0, 4.0])
metric_complement = complement(metric_apply(reverse(A)))

np.testing.assert_allclose(
    left_contraction(A, algebra.I).data, metric_complement.data,
    rtol=0, atol=1e-12,
)
np.testing.assert_allclose(
    dual(A).data, (metric_complement / float(algebra.I * algebra.I)).data,
    rtol=0, atol=1e-12,
)
```

## A mixed-signature counterexample

In $\mathrm{Cl}(1,1)$, $e_1^2=1$, $e_2^2=-1$ and $I^2=1$:

```python
from galaga import Algebra, complement, dual, left_contraction

algebra = Algebra(1, 1)
e1, e2 = algebra.basis_vectors()
assert complement(e2) == -e1
assert left_contraction(e2, algebra.I) == e1
assert dual(e2) == e1
```

The complement ignores the negative square; contraction does not.

## Pseudoscalar multiplication is not an exterior complement

For homogeneous $A_r$, multiplication by $I$ has only grade $n-r$, so
$A_rI=A_r\mathbin{\lfloor}I$. In a nondegenerate algebra the analogous statement
holds for $I^{-1}$. It does not follow that either product is the
metric-independent complement.

For example, in $\mathrm{Cl}(3,0)$,
$\operatorname{dual}(e_{12})=e_3=\operatorname{complement}(e_{12})$, but
$\operatorname{dual}(e_1)=-e_{23}$ while
$\operatorname{complement}(e_1)=e_{23}$.
Also, $I$ is central in odd dimension: $I^{-1}e_{12}=e_{12}I^{-1}=e_3$.
Merely switching multiplication from right to left cannot explain a minus
sign for that example.

For a degenerate metric, $I^2=0$. Multiplication or contraction with $I$ is
still defined, but can lose nonzero inputs and is not an invertible duality.
Galaga therefore rejects `dual` and `undual` there. Use exterior complements
when that metric-independent mapping is what the geometry needs; do not label
$AI$ a general Poincaré dual.

The [implemented specification](core/specs/SPEC-003-product-and-duality-conventions.md)
and [core ADR-005](core/adrs/005-explicit-product-and-duality-families.md) define
these contracts. The general identities above have executable tests across
Euclidean, mixed-signature, oblique, null and degenerate metrics.
