# Scaling the CGA Null Pair

Part of the [`galaga.core` documentation](README.md). See
[From an orthogonal CGA basis to a native null basis](cga-null-basis-change.md)
for the complete coordinate transformation.

## Purpose

Conformal geometric algebra commonly defines its origin and infinity vectors
from an orthogonal Minkowski pair using

$$
e_o=\frac12(e_- - e_+),
\qquad
e_\infty=e_-+e_+.
$$

Why is the factor $1/2$ attached to $e_o$? Could it be attached to
$e_\infty$ instead? Could both vectors be divided by $\sqrt2$?

The short answer is yes: all three are valid conventions. The individual
scales are not fixed, but their product is fixed if we require the standard
normalization

$$
e_o\mathbin{\cdot}e_\infty=-1.
$$

This chapter derives that scaling freedom and explains what it means for CGA
formulas and implementations.

## Starting point: an orthogonal Minkowski pair

Assume two orthogonal basis vectors $e_+$ and $e_-$ satisfying

$$
e_+^2=+1,
\qquad
e_-^2=-1,
\qquad
e_+\mathbin{\cdot}e_-=0.
$$

They span a two-dimensional plane with one positive and one negative metric
direction. This plane contains two null directions:

$$
e_- - e_+
\quad\text{and}\quad
e_- + e_+.
$$

To allow arbitrary scaling, define

$$
e_o=a(e_- - e_+),
\qquad
e_\infty=b(e_- + e_+),
$$

where $a$ and $b$ are nonzero real numbers.

## Nullness does not determine the scale

Compute the square of $e_o$:

$$
\begin{aligned}
e_o^2
&=a^2(e_- - e_+)^2\\
&=a^2\left(
e_-^2
-2e_-\mathbin{\cdot}e_+
+e_+^2
\right)\\
&=a^2(-1-0+1)\\
&=0.
\end{aligned}
$$

Likewise,

$$
\begin{aligned}
e_\infty^2
&=b^2(e_- + e_+)^2\\
&=b^2\left(
e_-^2
+2e_-\mathbin{\cdot}e_+
+e_+^2
\right)\\
&=b^2(-1+0+1)\\
&=0.
\end{aligned}
$$

Both vectors are null for every nonzero choice of $a$ and $b$. Multiplying a
null vector by a nonzero scalar never stops it from being null:

$$
(\lambda v)^2=\lambda^2v^2=0.
$$

Nullness determines a **direction**, not a preferred magnitude.

## The mutual inner product fixes the product of the scales

Although nullness does not constrain $a$ or $b$, the mutual inner product does:

$$
\begin{aligned}
e_o\mathbin{\cdot}e_\infty
&=ab(e_- - e_+)\mathbin{\cdot}(e_- + e_+)\\
&=ab\left(
e_-^2
+e_-\mathbin{\cdot}e_+
-e_+\mathbin{\cdot}e_-
-e_+^2
\right)\\
&=ab(-1-1)\\
&=-2ab.
\end{aligned}
$$

The standard CGA normalization is

$$
e_o\mathbin{\cdot}e_\infty=-1.
$$

Therefore,

$$
-2ab=-1,
$$

or

$$
ab=\frac12.
$$

This is the complete scaling constraint. Neither $a$ nor $b$ is individually
fixed; only their product is.

## Three useful normalized conventions

### Conventional asymmetric scaling

Most CGA presentations choose

$$
a=\frac12,
\qquad
b=1.
$$

This gives

$$
e_o=\frac12(e_- - e_+),
\qquad
e_\infty=e_-+e_+.
$$

Since $(1/2)(1)=1/2$, the mutual inner product is $-1$.

### The factor placed on infinity instead

An equally valid choice is

$$
a=1,
\qquad
b=\frac12,
$$

giving

$$
e_o=e_- - e_+,
\qquad
e_\infty=\frac12(e_-+e_+).
$$

Again, $ab=1/2$, so the null pair has exactly the same normalized Gram matrix.

### Symmetric square-root scaling

To scale both vectors equally, choose

$$
a=b=\frac1{\sqrt2}.
$$

Then

$$
e_o=\frac{e_- - e_+}{\sqrt2},
\qquad
e_\infty=\frac{e_-+e_+}{\sqrt2}.
$$

This works because

$$
ab=\frac1{\sqrt2}\frac1{\sqrt2}=\frac12.
$$

The vectors are divided by $\sqrt2$. If both were instead multiplied by
$\sqrt2$, then $a=b=\sqrt2$, $ab=2$, and

$$
e_o\mathbin{\cdot}e_\infty=-4.
$$

They would still be null, but they would not have the conventional mutual
normalization.

## Comparison table

| Convention | $a$ | $b$ | $e_o\cdot e_\infty$ |
| --- | ---: | ---: | ---: |
| Conventional | $1/2$ | $1$ | $-1$ |
| Factor on infinity | $1$ | $1/2$ | $-1$ |
| Symmetric | $1/\sqrt2$ | $1/\sqrt2$ | $-1$ |
| Both multiplied by $\sqrt2$ | $\sqrt2$ | $\sqrt2$ | $-4$ |

The first three rows are different normalized conventions. The final row is
included to distinguish multiplying by $\sqrt2$ from dividing by $\sqrt2$.

## Reciprocal scaling freedom

Suppose $(e_o,e_\infty)$ is already a normalized null pair:

$$
e_o^2=e_\infty^2=0,
\qquad
e_o\mathbin{\cdot}e_\infty=-1.
$$

For any nonzero $\lambda$, define

$$
e_o'=\lambda e_o,
\qquad
e_\infty'=\lambda^{-1}e_\infty.
$$

Their squares remain zero, and

$$
\begin{aligned}
e_o'\mathbin{\cdot}e_\infty'
&=(\lambda e_o)\mathbin{\cdot}
(\lambda^{-1}e_\infty)\\
&=\lambda\lambda^{-1}
(e_o\mathbin{\cdot}e_\infty)\\
&=-1.
\end{aligned}
$$

Thus normalized null pairs form a one-parameter family related by reciprocal
rescaling.

For example, begin with the conventional pair and choose $\lambda=2$:

$$
e_o'=2\left(\frac12(e_- - e_+)\right)=e_- - e_+,
$$

and

$$
e_\infty'=\frac12(e_-+e_+).
$$

This moves the factor $1/2$ from $e_o$ to $e_\infty$.

## Every normalized choice has the same Gram matrix

In the ordered basis $(e_o,e_\infty)$, every normalized choice has

$$
G_{o\infty}=
\begin{pmatrix}
e_o^2 & e_o\mathbin{\cdot}e_\infty\\
e_\infty\mathbin{\cdot}e_o & e_\infty^2
\end{pmatrix}=
\begin{pmatrix}
0&-1\\
-1&0
\end{pmatrix}.
$$

This is worth emphasizing:

> The native Gram matrix does not distinguish which normalized scaling was
> used to construct the null pair from $e_+$ and $e_-$.

The Gram matrix describes relationships among the native basis vectors. The
separate change-of-basis matrix describes how those vectors are expressed in a
particular external orthogonal frame.

If software only needs to work in the native null basis, the Gram matrix is
enough. If it must convert values to or from a particular $e_+,e_-$ basis, it
also needs the chosen scaling convention.

## Change-of-basis matrices

For the general definitions

$$
e_o=a(e_- - e_+),
\qquad
e_\infty=b(e_- + e_+),
$$

the final two rows of the change-of-basis matrix are

$$
T_{a,b}=
\begin{pmatrix}
-a&a\\
b&b
\end{pmatrix},
$$

where columns are ordered as $(e_+,e_-)$. Its determinant is

$$
\det(T_{a,b})=-2ab.
$$

For every normalized choice, $ab=1/2$, so

$$
\det(T_{a,b})=-1.
$$

Every normalized choice is therefore invertible and reverses the orientation
of this ordered two-dimensional basis.

The inverse formulas are

$$
e_-=\frac12\left(\frac{e_o}{a}+\frac{e_\infty}{b}\right),
$$

and

$$
e_+=\frac12\left(\frac{e_\infty}{b}-\frac{e_o}{a}\right).
$$

For the symmetric convention, these simplify to

$$
e_-=\frac{e_o+e_\infty}{\sqrt2},
\qquad
e_+=\frac{e_\infty-e_o}{\sqrt2}.
$$

## The outer and geometric products are also normalized

Reciprocal rescaling preserves the null-plane bivector:

$$
e_o'\wedge e_\infty'
=(\lambda e_o)\wedge(\lambda^{-1}e_\infty)
=e_o\wedge e_\infty.
$$

For any choice satisfying $ab=1/2$,

$$
e_o\wedge e_\infty=-e_+\wedge e_-.
$$

The geometric product is therefore structurally identical in every normalized
null convention:

$$
e_oe_\infty
=e_o\mathbin{\cdot}e_\infty+e_o\wedge e_\infty
=-1+e_o\wedge e_\infty.
$$

Likewise,

$$
e_\infty e_o=-1-e_o\wedge e_\infty.
$$

Moving the factor does not change these native-basis multiplication rules.

## Effect on conformal point embedding

For a normalized null pair, the standard embedding of a Euclidean vector $x$
is

$$
X(x)=e_o+x+\frac12x^2e_\infty.
$$

Assuming $x$ is orthogonal to the null plane,

$$
\begin{aligned}
X(x)^2
&=x^2
+2\left(\frac12x^2\right)
(e_o\mathbin{\cdot}e_\infty)\\
&=x^2-x^2\\
&=0.
\end{aligned}
$$

The derivation uses only

$$
e_o^2=e_\infty^2=0
\quad\text{and}\quad
e_o\mathbin{\cdot}e_\infty=-1.
$$

Therefore, the formula has the same appearance for the conventional, swapped,
and symmetric normalized pairs.

There is nevertheless an important consistency rule. If vectors are expanded
back into a fixed external $e_+,e_-$ frame, reciprocal scaling changes the
embedded representative. Relative to the original convention, it acts as a
Lorentz boost in the null plane and corresponds to a conformal change of
scale. Do not construct $e_o$ using one convention and $e_\infty$ or point
formulas using another.

Projectively, multiplying $e_o$ or $e_\infty$ by a nonzero scalar does not
change the null direction representing origin or infinity. It does change the
normalization of concrete multivectors, which matters when extracting metric
quantities such as distances.

## What if the mutual product is not normalized to -1?

Suppose $e_o^2=e_\infty^2=0$, but

$$
e_o\mathbin{\cdot}e_\infty=-\kappa
$$

for some nonzero $\kappa$. The pair still spans a valid nondegenerate null
plane. However, formulas containing fixed numerical coefficients must change.

For example, seek an embedding of the form

$$
X(x)=e_o+x+c x^2e_\infty.
$$

Its square is

$$
X(x)^2=x^2-2c\kappa x^2.
$$

Nullness requires

$$
c=\frac1{2\kappa}.
$$

The familiar coefficient $1/2$ is correct specifically when $\kappa=1$.
This is why normalization is not merely cosmetic: it determines the constants
appearing throughout the CGA API.

## Implications for a Gram-native implementation

A Gram-native algebra using the normalized basis stores

$$
G=
\begin{pmatrix}
I_3&0\\
0&
\begin{matrix}
0&-1\\
-1&0
\end{matrix}
\end{pmatrix}.
$$

From this matrix alone, the algebra knows:

- both final basis vectors are null;
- their mutual inner product is $-1$;
- the metric is nondegenerate; and
- their geometric product contains scalar and bivector parts.

It does not know whether those vectors were originally defined using
$(a,b)=(1/2,1)$, $(1,1/2)$, or $(1/\sqrt2,1/\sqrt2)$. That historical
information is unnecessary for native calculations. It matters only when
converting to a specifically normalized orthogonal basis or matching an
external convention.

For interoperability, a CGA layout should therefore document two things:

1. the native null Gram matrix; and
2. the change-of-basis convention used for any exposed $e_+,e_-$ conversion.

## Which convention should Galaga use?

All normalized choices are mathematically valid. The decision is primarily
about interoperability and reader expectations.

The conventional asymmetric choice

$$
e_o=\frac12(e_- - e_+),
\qquad
e_\infty=e_-+e_+
$$

is common in CGA texts and existing software. Retaining it minimizes surprises
when formulas are expanded in an orthogonal frame.

The symmetric choice

$$
e_o=\frac{e_- - e_+}{\sqrt2},
\qquad
e_\infty=\frac{e_-+e_+}{\sqrt2}
$$

is aesthetically balanced and gives a particularly symmetric change-of-basis
matrix. It is not more correct; it is a different convention.

Once Galaga works natively with the null Gram matrix, ordinary calculations do
not expose this distinction. The choice becomes visible only at the boundary
between null and orthogonal frames.

## Summary

For

$$
e_o=a(e_- - e_+),
\qquad
e_\infty=b(e_- + e_+),
$$

both vectors are null for any nonzero $a,b$. The conventional reciprocal
normalization requires

$$
ab=\frac12.
$$

Consequently, all of the following are valid:

$$
(a,b)=
\left(\frac12,1\right),
\quad
\left(1,\frac12\right),
\quad
\left(\frac1{\sqrt2},\frac1{\sqrt2}\right).
$$

The first is traditional, the second moves the factor to infinity, and the
third shares it symmetrically. Each gives

$$
e_o^2=e_\infty^2=0,
\qquad
e_o\mathbin{\cdot}e_\infty=-1,
$$

and each produces the same native null-basis Gram matrix.

## Related documentation

- [Implementation overview](implementation-overview.md)
- [Architecture](architecture.md)
- [Canonical Gram-matrix decision](adrs/002-canonical-native-gram-matrix.md)
