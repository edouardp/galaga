# Inner Products, Contractions, and Interior Products

Part of the [`galaga.core` documentation](README.md). The normative summary is
[SPEC-003: Product and duality conventions](specs/SPEC-003-product-and-duality-conventions.md).

Geometric algebra uses the phrase *inner product* for several operations that
agree on vectors and then diverge on scalars, higher grades, or operand order.
This document separates those operations by formula and records the semantics
implemented by `galaga.core`, with legacy Galaga comparisons where migration
behavior matters.

The central distinction is:

- a scalar-valued pairing compares equal-grade components;
- a contraction or interior product removes grade and can return a nonscalar;
- selecting the scalar part of a geometric product is not the same as the
  metric-induced pairing on the exterior algebra.

`galaga.core` keeps separate names for these meanings instead of giving an unqualified
`inner_product()` name to one of them.

## Notation

Let $g$ be the symmetric $n\times n$ Gram matrix on the base vector space,
with

$$
g_{ij}=e_i\bullet e_j.
$$

Let $A_r$ and $B_s$ be homogeneous multivectors of grades $r$ and $s$. For an
arbitrary multivector $A$, write $A=\sum_r A_r$. We use:

- $AB$ for the geometric product;
- $A\wedge B$ for the exterior product;
- $\langle A\rangle_k$ for grade-$k$ projection;
- $\widetilde A$ for reversion;
- $I$ for the grade-$n$ pseudoscalar or antiscalar;
- $\vee$ for the metric-independent antiwedge/regressive product.

Every definition below extends bilinearly and grade-pair by grade-pair to
mixed-grade multivectors.

Strictly, a real inner product is positive definite. When $g$ is indefinite or
degenerate, the metric-induced operation below is a symmetric bilinear pairing,
not an inner product in that narrow sense. Lengyel and the RGA material still
call it the dot or inner product, and this document follows that terminology
when discussing their convention.

## Summary

| Operation | Homogeneous definition | Result grade | Scalar handling | Galaga name |
|---|---|---:|---|---|
| Scalar product | $\langle A_rB_s\rangle_0$ | 0 | Pairs scalar components | `scalar_product()` |
| Metric inner product | $A^\mathsf{T}(\Lambda g)B=\langle A\widetilde B\rangle_0$ | 0 | Pairs scalar components | `metric_inner_product()` |
| Left contraction | $\langle A_rB_s\rangle_{s-r}$ if $r\le s$, else 0 | $s-r$ | Scalar on the left passes through | `left_contraction()` |
| Right contraction | $\langle A_rB_s\rangle_{r-s}$ if $r\ge s$, else 0 | $r-s$ | Scalar on the right passes through | `right_contraction()` |
| Hestenes inner | $\langle A_rB_s\rangle_{\lvert r-s\rvert}$ if $r,s>0$, else 0 | $\lvert r-s\rvert$ | Discards scalar-grade contributions | `hestenes_inner()` |
| Doran–Lasenby inner | $\langle A_rB_s\rangle_{\lvert r-s\rvert}$ | $\lvert r-s\rvert$ | Scalars pass through on either side | `doran_lasenby_inner()` |
| RGA left interior | $(A_r)_{\star}\vee B_s=\langle B_s\widetilde{A_r}\rangle_{s-r}$ if $r\le s$ | $s-r$ | Scalar on the left passes through | `left_interior_product()` |
| RGA right interior | $A_r\vee(B_s)^\star=\langle\widetilde{B_s}A_r\rangle_{r-s}$ if $r\ge s$ | $r-s$ | Scalar on the right passes through | `right_interior_product()` |
| Antidot product | $(A^\mathsf{T}\mathbb G B)I$ | $n$ | Returns an antiscalar | `antidot_product()` |

Here $\Lambda g$ is the exterior extension of the vector Gram matrix,
$\mathbb G$ is its metric antiexomorphism, $(A)_\star$ is the left metric or
bulk dual, and $A^\star$ is the right metric or bulk dual.

The table describes Galaga's actual functions. Other books and libraries attach
the words *inner product*, *dot product*, and *contraction* to different rows.

## The Gram matrix and its exterior extension

The base Gram matrix contains only vector pairings. Pairing higher-grade
objects requires extending it to the full exterior algebra.

For ordered index sets

$$
I=(i_1<\dots<i_k),\qquad J=(j_1<\dots<j_k),
$$

define the basis blades $e_I=e_{i_1}\wedge\dots\wedge e_{i_k}$ and $e_J$ in
the same way. The induced pairing is

$$
e_I\bullet e_J=\det g[I,J],
$$

where $g[I,J]$ is the $k\times k$ submatrix with rows $I$ and columns $J$.
Blades of unequal grade pair to zero.

Equivalently, the full $2^n\times2^n$ matrix $\Lambda g$ is block diagonal by
grade. Its grade-$k$ block is the $k$th compound matrix of $g$:

$$
\Lambda g=\operatorname{diag}(C_0(g),C_1(g),\ldots,C_n(g)),
\qquad C_k(g)_{I,J}=\det g[I,J].
$$

The grade-zero block is $C_0(g)=[1]$, and the grade-one block is the original
Gram matrix $C_1(g)=g$.

For arbitrary multivectors $A=\sum_I a_Ie_I$ and $B=\sum_J b_Je_J$,

$$
A\bullet B
=A^\mathsf{T}(\Lambda g)B
=\sum_{k=0}^n\ \sum_{\substack{|I|=k\\|J|=k}}
 a_Ib_J\det g[I,J].
$$

If $g=\operatorname{diag}(s_1,\ldots,s_n)$, this simplifies to

$$
e_I\bullet e_J
=\delta_{IJ}\prod_{i\in I}s_i.
$$

The compound-matrix definition is essential for a native nonorthogonal basis.
For example, with

$$
g=\begin{bmatrix}2&1\\1&3\end{bmatrix},
\qquad B=e_1\wedge e_2,
$$

the induced bivector pairing is

$$
B\bullet B=\det g=5.
$$

This is the full-algebra meaning of a Gram matrix: the vector Gram matrix
determines every same-grade blade pairing through its minors.

## Scalar product

The legacy Galaga engine and `galaga.core` define

$$
\operatorname{scalar\_product}(A,B)=\langle AB\rangle_0.
$$

For homogeneous operands, it can be nonzero only when their grades agree. It
is symmetric for a symmetric real metric, but it is not the metric-induced
pairing on the exterior algebra.

Reversion acts on grade $r$ by

$$
\widetilde{B_r}=(-1)^{r(r-1)/2}B_r.
$$

It follows that

$$
\langle A_rB_r\rangle_0
=(-1)^{r(r-1)/2}(A_r\bullet B_r),
$$

and, for mixed-grade multivectors,

$$
\operatorname{scalar\_product}(A,B)
=\sum_r(-1)^{r(r-1)/2}(A_r\bullet B_r).
$$

| Grade modulo 4 | Reversion sign | Scalar product versus metric inner product |
|---:|---:|---|
| 0 | $+1$ | Same |
| 1 | $+1$ | Same |
| 2 | $-1$ | Opposite sign |
| 3 | $-1$ | Opposite sign |

Thus, in Euclidean space with $B=e_{12}$,

$$
\operatorname{scalar\_product}(B,B)=\langle BB\rangle_0=-1,
\qquad B\bullet B=+1.
$$

Likewise, for the nonorthogonal example above,

$$
\operatorname{scalar\_product}(B,B)=-5,
\qquad B\bullet B=+5.
$$

The current
[`galaga.core.scalar_product()`](../../packages/galaga/galaga/core/__init__.py)
implements this
scalar-part operation. Existing uses with vectors remain valid because
reversion fixes grade one, so both pairings reproduce the vector Gram matrix:

$$
\operatorname{scalar\_product}(e_i,e_j)=e_i\bullet e_j=g_{ij}.
$$

The distinction appears as soon as higher grades are admitted.

## Lengyel's metric inner product

Eric Lengyel defines the inner product on the full exterior algebra as

$$
\operatorname{metric\_inner\_product}(A,B)
=A\bullet B
=A^\mathsf{T}(\Lambda g)B.
$$

In terms of the geometric product,

$$
\boxed{A\bullet B=\langle A\widetilde B\rangle_0.}
$$

Equivalent symmetric forms include

$$
\langle A\widetilde B\rangle_0
=\langle\widetilde A B\rangle_0
=\langle B\widetilde A\rangle_0
=\langle\widetilde B A\rangle_0.
$$

This operation:

- always returns a scalar;
- pairs only components of equal grade;
- agrees with $g$ on vectors;
- is positive definite on the full exterior algebra when $g$ is positive
  definite;
- becomes indefinite or degenerate when $g$ does;
- gives the Gram-determinant pairing of simple blades.

Lengyel's criticism of several GA conventions is specifically that an
operation capable of returning a nonscalar is an *interior product*, not an
inner product, and that $\langle AB\rangle_0$ has the wrong higher-grade signs
to induce Euclidean norms.

The Gram-native implementation calculates the operation as

```python
def metric_inner_product(left: Multivector, right: Multivector) -> Multivector:
    return scalar_product(left, reverse(right))
```

This reuses the existing Clifford product and works for diagonal,
nonorthogonal, indefinite, and degenerate Gram matrices. A lazily constructed
$\Lambda g$ should give the same answer and is useful for metric application,
Hodge duals, or matrix-oriented code, but it need not be materialized merely
to calculate the pairing.

## Conventional left and right contractions

Galaga's pre-RGA contractions are grade selections from the geometric product.
For homogeneous operands,

$$
A_r\mathbin{\rfloor}B_s =
\begin{cases}
\langle A_rB_s\rangle_{s-r},&r\le s,\\
0,&r>s,
\end{cases}
$$

and

$$
A_r\mathbin{\lfloor}B_s =
\begin{cases}
\langle A_rB_s\rangle_{r-s},&r\ge s,\\
0,&r<s.
\end{cases}
$$

Galaga exposes these as `left_contraction()` and `right_contraction()`.
They are directional:

- the left contraction removes the left operand's grade from the right;
- the right contraction removes the right operand's grade from the left;
- a scalar passes through only on the side permitted by that direction.

For example, in Euclidean $Cl(3,0)$,

$$
e_1\mathbin{\rfloor}e_{12}=e_2,
\qquad
e_{12}\mathbin{\lfloor}e_1=-e_2.
$$

When $r=s$, both conventional contractions reduce to Galaga's scalar product:

$$
A_r\mathbin{\rfloor}B_r
=A_r\mathbin{\lfloor}B_r
=\langle A_rB_r\rangle_0.
$$

They therefore do **not** reduce to Lengyel's metric inner product in grades 2
and 3 modulo 4. For $B=e_{12}$, both conventional contractions give $-1$,
whereas $B\bullet B=+1$.

These functions should remain available under their explicit names because
their definitions are common in GA literature and existing Galaga code relies
on them. They should not be conflated with the RGA interior products described
below.

## Hestenes inner product

Galaga implements the Hestenes inner product grade-pairwise as

$$
A_r\mathbin{\cdot_H}B_s =
\begin{cases}
\langle A_rB_s\rangle_{\lvert r-s\rvert},&r>0\text{ and }s>0,\\
0,&r=0\text{ or }s=0.
\end{cases}
$$

Yes: the Hestenes inner product **kills scalars**. More precisely, Galaga
discards every contribution for which either grade component is scalar. A
pure scalar operand therefore makes the entire result zero, while nonscalar
components of a mixed-grade operand can still contribute.

For positive grades it combines the two directional conventional
contractions:

- if $r<s$, it agrees with `left_contraction(A_r, B_s)`;
- if $r>s$, it agrees with `right_contraction(A_r, B_s)`;
- if $r=s>0$, it reduces to `scalar_product(A_r, B_r)`.

It is generally grade-reducing rather than scalar-valued. Under Lengyel's
terminology it is therefore an interior-product convention, despite its
traditional name.

## Doran–Lasenby, Dorst, and `|`

Galaga's Doran–Lasenby operation uses the same absolute grade difference but
does not discard scalar grades:

$$
A_r\mathbin{\cdot_{DL}}B_s
=\langle A_rB_s\rangle_{\lvert r-s\rvert}.
$$

Consequently,

$$
\alpha\mathbin{\cdot_{DL}}B=\alpha B,
\qquad
A\mathbin{\cdot_{DL}}\beta=\beta A,
$$

whereas both corresponding Hestenes results are zero for pure nonscalar
$A,B$.

In Galaga:

- `doran_lasenby_inner()` is the definitive function;
- `dorst_inner` is an alias;
- `a | b` calls `doran_lasenby_inner(a, b)`;
- `ip(a, b)` and its alias `inner_product(a, b)` default to this convention;
- `ip()` also accepts the modes `"hestenes"`, `"left"`, `"right"`, and
  `"scalar"`.

The dispatcher currently does not include Lengyel's `metric_inner_product()`
or the RGA interior products. Code that needs those meanings should call their
explicit functions.

Because other GA libraries map `|` to Hestenes inner, a contraction, or other
operations, portable explanations should never use “pipe means inner product”
without naming the convention.

## Lengyel/RGA interior products

Lengyel defines interior products from metric Hodge duals and the antiwedge
product instead of defining them as direct grade selections from $AB$.

Let

$$
A^\star=\operatorname{right\_complement}((\Lambda g)A),
\qquad
A_\star=\operatorname{left\_complement}((\Lambda g)A)
$$

be the right and left metric or bulk duals. Galaga implements these as
`right_hodge_dual()` and `left_hodge_dual()`.

The RGA left interior product is

$$
\operatorname{left\_interior}(A_r,B_s)
=(A_r)_\star\vee B_s
=\langle B_s\widetilde{A_r}\rangle_{s-r},
\qquad r\le s,
$$

and the RGA right interior product is

$$
\operatorname{right\_interior}(A_r,B_s)
=A_r\vee(B_s)^\star
=\langle\widetilde{B_s}A_r\rangle_{r-s},
\qquad r\ge s.
$$

Galaga exposes them as `left_interior_product()` and
`right_interior_product()`.

Their defining equal-grade property is

$$
\operatorname{left\_interior}(A_r,B_r)
=\operatorname{right\_interior}(A_r,B_r)
=A_r\bullet B_r.
$$

This is the main difference from Galaga's conventional contractions. Reversion
and operand order also change mixed-grade signs. For example,

$$
\begin{aligned}
\operatorname{left\_contraction}(e_1,e_{12})&=+e_2,\\
\operatorname{left\_interior}(e_1,e_{12})&=-e_2,\\
\operatorname{right\_contraction}(e_{12},e_1)&=-e_2,\\
\operatorname{right\_interior}(e_{12},e_1)&=+e_2.
\end{aligned}
$$

For a vector $a$ and arbitrary homogeneous $B$, the RGA decompositions of the
geometric product are

$$
aB=a\wedge B+\operatorname{right\_interior}(B,a),
$$

and

$$
Ba=B\wedge a+\operatorname{left\_interior}(a,B).
$$

The apparently reversed argument order is significant.

## A concrete comparison

The following values were evaluated with Galaga in Euclidean $Cl(3,0)$, using
$B=e_{12}$ and scalar $3$.

| Galaga operation | $(B,B)$ | $(e_1,B)$ | $(B,e_1)$ | $(3,e_1)$ |
|---|---:|---:|---:|---:|
| `scalar_product` | $-1$ | $0$ | $0$ | $0$ |
| `metric_inner_product` | $+1$ | $0$ | $0$ | $0$ |
| `left_contraction` | $-1$ | $+e_2$ | $0$ | $3e_1$ |
| `right_contraction` | $-1$ | $0$ | $-e_2$ | $0$ |
| `hestenes_inner` | $-1$ | $+e_2$ | $-e_2$ | $0$ |
| `doran_lasenby_inner` | $-1$ | $+e_2$ | $-e_2$ | $3e_1$ |
| `left_interior_product` | $+1$ | $-e_2$ | $0$ | $3e_1$ |
| `right_interior_product` | $+1$ | $0$ | $+e_2$ | $0$ |

This table captures the three independent choices that the word “inner” often
hides:

1. scalar result versus grade-difference result;
2. whether scalar operands participate;
3. whether reversal and operand order make the equal-grade result the scalar
   product or the metric-induced pairing.

## Worked examples across algebras

`galaga.core.metric_inner_product()` exposes the metric pairing directly. The
examples below compare it with the scalar part of the geometric product.

### Euclidean algebra $Cl(3,0)$

```python
from galaga.core import Algebra, metric_inner_product, scalar_product

alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()

v = 2 * e1 - e2
B = e1 ^ e2
I = e1 ^ e2 ^ e3

assert metric_inner_product(v, v) == 5
assert scalar_product(v, v) == 5

assert metric_inner_product(B, B) == 1
assert scalar_product(B, B) == -1

assert metric_inner_product(I, I) == 1
assert scalar_product(I, I) == -1
```

The positive-definite vector metric induces a positive-definite pairing on all
exterior grades. The scalar product nevertheless changes sign in grades two
and three because it omits reversion.

The conventional contraction and Hestenes/Doran–Lasenby values from the
earlier comparison table are independent of positive definiteness; changing
the signature changes metric factors, not their grade-selection rules.

### Spacetime algebra $Cl(1,3)$

Let $\gamma_0^2=+1$ and
$\gamma_1^2=\gamma_2^2=\gamma_3^2=-1$.

```python
from galaga.core import Algebra, metric_inner_product, scalar_product

sta = Algebra(1, 3)
g0, g1, g2, g3 = sta.basis_vectors()

u = 2 * g0 + 3 * g1
B01 = g0 ^ g1
B12 = g1 ^ g2

assert metric_inner_product(u, u) == -5       # 2**2 - 3**2

assert metric_inner_product(B01, B01) == -1  # det diag(+1, -1)
assert scalar_product(B01, B01) == 1

assert metric_inner_product(B12, B12) == 1   # det diag(-1, -1)
assert scalar_product(B12, B12) == -1
```

The metric inner product retains the induced spacetime signature. It is not
positive definite: the vector $u$ and timelike–spacelike bivector $B_{01}$
have negative squared pairing. The scalar product flips both bivector signs,
but that does not make it the metric-induced pairing.

### Rigid/projective algebra $Cl(3,0,1)$

RGA uses the explicit ordered signature $(1,1,1,0)$ so that $e_4$ is null.
The advanced RGA operations in this example are also implemented by the
legacy Galaga API:

```python
from galaga import (
    Algebra,
    antidot_product,
    b_rga,
    metric_inner_product,
)

rga = Algebra((1, 1, 1, 0), blades=b_rga())
b = rga.locals()

e1 = b["e1"]
e4 = b["e4"]
direction = b["e423"]

assert metric_inner_product(e1, e1) == 1
assert antidot_product(e1, e1) == 0

assert metric_inner_product(e4, e4) == 0
assert antidot_product(e4, e4) == rga.I

assert metric_inner_product(direction, direction) == 0
assert antidot_product(direction, direction) == rga.I
```

Any basis blade containing $e_4$ lies in the radical of $\Lambda g$, so its
ordinary metric inner product with every blade is zero. The complementary
antimetric does the opposite: it pairs the weight blades containing $e_4$ and
returns an antiscalar. The trivector $e_{423}$ represents a spatial direction
in plane-based PGA, which is why its useful magnitude comes from the antidot
product rather than the ordinary dot product.

The convenience constructor `Algebra(3, 0, 1)` orders null vectors first in
both `gram` and Galaga. Use the explicit signature when reproducing RGA's
$e_1,e_2,e_3,e_4$ naming and orientation.

### Conformal algebra $Cl(4,1)$ in a native null basis

The native basis $(e_1,e_2,e_3,e_o,e_\infty)$ has Gram matrix

$$
g=
\begin{bmatrix}
1&0&0&0&0\\
0&1&0&0&0\\
0&0&1&0&0\\
0&0&0&0&-1\\
0&0&0&-1&0
\end{bmatrix}.
$$

Thus $e_o$ and $e_\infty$ are individually null but not mutually orthogonal:

```python
import numpy as np

from galaga.core import Algebra, metric_inner_product, scalar_product

cga = Algebra(gram=np.array([
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, -1],
    [0, 0, 0, -1, 0],
], dtype=float))

e1, e2, e3, eo, einf = cga.basis_vectors()

assert metric_inner_product(eo, eo) == 0
assert metric_inner_product(einf, einf) == 0
assert metric_inner_product(eo, einf) == -1

E = eo ^ einf
assert metric_inner_product(E, E) == -1
assert scalar_product(E, E) == 1
```

The bivector value follows directly from the corresponding compound-matrix
minor:

$$
(e_o\wedge e_\infty)\bullet(e_o\wedge e_\infty)
=\det\begin{bmatrix}0&-1\\-1&0\end{bmatrix}=-1.
$$

For a Euclidean vector $x$, the normalized conformal point

$$
P(x)=e_o+x+\frac12(x\bullet x)e_\infty
$$

satisfies

$$
P(x)\bullet P(x)=0,
\qquad
P(x)\bullet P(y)=-\frac12\lVert x-y\rVert^2.
$$

For example, $x=(1,2,0)$ and $y=(-1,1,2)$ have squared distance $9$, so their
conformal point pairing is $-9/2$. These are vector pairings in the
five-dimensional algebra, so `scalar_product()` happens to agree; the
difference reappears for higher-grade conformal objects such as $E$.

### A nonorthogonal positive-definite Gram basis

A native Gram matrix need not be diagonal or contain null vectors:

```python
import numpy as np

from galaga.core import Algebra, metric_inner_product, scalar_product

alg = Algebra(gram=np.array([
    [2, 1],
    [1, 3],
], dtype=float))
e1, e2 = alg.basis_vectors()
B = e1 ^ e2

assert metric_inner_product(e1, e1) == 2
assert metric_inner_product(e1, e2) == 1
assert metric_inner_product(e2, e2) == 3

assert metric_inner_product(B, B) == 5
assert scalar_product(B, B) == -5
```

The off-diagonal vector pairing is stored directly in `algebra.gram`. The
bivector pairing is not the product of diagonal entries $2\cdot3$; it is the
minor $2\cdot3-1\cdot1=5$. This is why a general Gram-native
`extended_metric_matrix()` must use compound matrices rather than treating the
exterior basis as orthogonal.

## Transwedge products

Lengyel's order-$k$ transwedge product interpolates between the exterior and
interior products. For operands of grades $g$ and $h$, its output grade is

$$
g+h-2k.
$$

The endpoints are:

$$
A\mathbin{\underset{0}{\unicode{x2A53}}}B=A\wedge B,
$$

and, when $k=\operatorname{gr}(A)$,

$$
A\mathbin{\underset{k}{\unicode{x2A53}}}B
=\operatorname{right\_interior}(B,A).
$$

If $A$ and $B$ both have grade $k$, the latter reduces to

$$
A\mathbin{\underset{k}{\unicode{x2A53}}}B=A\bullet B.
$$

The complete geometric product is the signed sum

$$
AB=\sum_{k=0}^n(-1)^{k(k-1)/2}
\left(A\mathbin{\underset{k}{\unicode{x2A53}}}B\right).
$$

The sign of the terminal equal-grade transwedge term is precisely the sign
that distinguishes $\langle AB\rangle_0$ from $A\bullet B$. Galaga implements
both `transwedge()` and its De Morgan dual `transwedge_antiproduct()`.

## Antidot product, antimetric, bulk, and weight

RGA/PGA adds a product dual to the scalar-valued dot product. Let
$\mathbb G$ be the metric antiexomorphism on the exterior algebra. Galaga's
antidot product is

$$
A\circ B=(A^\mathsf{T}\mathbb G B)I.
$$

It returns an antiscalar, not a scalar. It satisfies the De Morgan identity

$$
A\circ B
=\operatorname{right\_complement}\left(
  \operatorname{left\_complement}(A)
  \bullet
  \operatorname{left\_complement}(B)
\right).
$$

For invertible $g$,

$$
(\Lambda g)\mathbb G=\det(g)I_{2^n}.
$$

For degenerate metrics, $\mathbb G$ must be built from complementary minors,
not from an inverse. This keeps the antidot product meaningful in PGA.

In RGA with $g=\operatorname{diag}(1,1,1,0)$:

- `metric_apply()` or `bulk_part()` preserves the bulk components and removes
  blades containing the null basis vector;
- `antimetric_apply()` or `weight_part()` preserves the complementary weight
  components;
- `metric_inner_product()` measures the bulk pairing and returns a scalar;
- `antidot_product()` measures the weight pairing and returns an antiscalar.

This is why plane-based PGA quantities represented by trivectors can have zero
ordinary dot product but a useful antidot product for magnitudes and angles.
Point-based and plane-based PGA exchange the practical roles of these dual
pairings.

## Norms and orthogonality

Galaga defines

$$
\operatorname{norm2}(A)=\langle A\widetilde A\rangle_0.
$$

Algebraically, this is

$$
\operatorname{norm2}(A)=A\bullet A.
$$

For positive-definite $g$, this is nonnegative and is the squared norm induced
on the full exterior algebra. For indefinite or degenerate $g$, it may be
negative or zero for nonzero $A$. Galaga's `norm()` takes
$\sqrt{|\operatorname{norm2}(A)|}$, which is useful computationally but does
not turn an indefinite or degenerate pairing into a positive-definite inner
product.

Orthogonality under Lengyel's convention means $A\bullet B=0$. Orthogonality
between different grades is automatic because $\Lambda g$ is block diagonal.
In a degenerate algebra, a nonzero element in the radical pairs to zero with
every element, so zero pairing alone does not imply independent Euclidean
directions or a nonzero norm.

PGA additionally has the dual seminorm induced by the antidot product. Bulk
and weight information must be considered together when a nondegenerate
geometric magnitude is needed.

## Implementation status and direction for `galaga.core`

| Concept | `galaga.core` now | Legacy Galaga |
|---|---|---|
| Geometric product | `geometric_product()`, `gp` | `gp()` |
| Exterior product | `outer_product()`, `op`, `^` | `op()`, `^` |
| Reversion | `reverse()` | `reverse()` |
| Scalar part of $AB$ | `scalar_product()` | `scalar_product()` |
| Metric inner product | `metric_inner_product()` | `metric_inner_product()` |
| Conventional contractions | `left_contraction()`, `right_contraction()` | `left_contraction()`, `right_contraction()` |
| Hestenes inner | `hestenes_inner()` | `hestenes_inner()` |
| Doran–Lasenby inner | `doran_lasenby_inner()`, `dorst_inner`, `|` | `doran_lasenby_inner()`, `dorst_inner`, `|` |
| RGA interior products | `left_interior_product()`, `right_interior_product()` | `left_interior_product()`, `right_interior_product()` |
| Antidot and metric maps | `antidot_product()`, `metric_apply()`, `antimetric_apply()` | `antidot_product()`, `metric_apply()`, `antimetric_apply()` |
| Transwedge family | `transwedge()`, `transwedge_antiproduct()` | `transwedge()`, `transwedge_antiproduct()` |

Recommended direction:

1. Keep `scalar_product()` with its existing Galaga-compatible meaning
   $\langle AB\rangle_0$.
2. Keep `metric_inner_product()` as the Gram-native identity
   $\langle A\widetilde B\rangle_0$.
3. Preserve Galaga's explicit conventional contraction names, and add the RGA
   names separately rather than merging them.
4. Do not introduce an unqualified `inner_product()` unless it is an explicit
   dispatcher whose selected convention is visible. If operator compatibility
   with Galaga is required, `|` means Doran–Lasenby, not Hestenes or Lengyel's
   metric pairing.
5. Keep the compound metric and antimetric matrices lazy. The geometric-product
   implementation can calculate the metric pairing without allocating a dense
   $2^n\times2^n$ matrix.

## Related documentation

- [Implementation overview](implementation-overview.md)
- [Design principles](design-principles.md)
- [Explicit product-family decision](adrs/005-explicit-product-and-duality-families.md)
- [Metric-extension decision](adrs/009-build-metric-extensions-from-minors.md)

## References

Primary Lengyel and RGA sources:

- Eric Lengyel, [Poor Foundations in Geometric Algebra](https://terathon.com/blog/poor-foundations-ga.html).
- Eric Lengyel, [Geometric Algebra Books](https://terathon.com/blog/ga-books.html).
- Eric Lengyel, [The Transwedge Product](https://terathon.com/blog/transwedge-product.html).
- Eric Lengyel, [Dual Approaches to Projective Geometric Algebra](https://terathon.com/blog/dual-pga.html).
- Rigid Geometric Algebra, [Dot products](https://rigidgeometricalgebra.org/wiki/index.php?title=Dot_products).
- Rigid Geometric Algebra, [Metrics](https://rigidgeometricalgebra.org/wiki/index.php?title=Metrics).
- Rigid Geometric Algebra, [Interior products](https://rigidgeometricalgebra.org/wiki/index.php?title=Interior_products).
- Rigid Geometric Algebra, [Geometric products](https://rigidgeometricalgebra.org/wiki/index.php?title=Geometric_products).
- Rigid Geometric Algebra, [Transwedge products](https://rigidgeometricalgebra.org/wiki/index.php?title=Transwedge_products).

Relevant Galaga material in this repository:

- [`galaga/algebra.py`](../../packages/galaga/galaga/algebra.py) for the legacy
  executable definitions;
- [`rga-convention-layer.md`](../rga-convention-layer.md) for the RGA operation
  mapping;
- [`review-terathon-ga-foundations.md`](../review-terathon-ga-foundations.md)
  for the source review;
- [`ga-library-operations-survey.md`](../ga-library-operations-survey.md) for
  cross-library operator differences;
- [`test_ga.py`](../../packages/galaga/tests/test_ga.py) and
  [`test_rga_convention_layer.py`](../../packages/galaga/tests/test_rga_convention_layer.py)
  for executable sign and grade identities.
