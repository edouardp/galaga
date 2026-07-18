# From an Orthogonal CGA Basis to a Native Null Basis

Part of the [`galaga.core` documentation](README.md). For the code decomposition that
implements this model, see the
[implementation overview](implementation-overview.md).

## Who this is for

This chapter assumes that you already have a working geometric-algebra
vocabulary. You know what basis vectors and blades are, that a basis vector has
a square, and that the geometric product contains inner and outer products.

The goal is to explain the mathematical machinery underneath this statement:

> Replacing the orthogonal CGA basis
> $(e_1,e_2,e_3,e_+,e_-)$ with
> $(e_1,e_2,e_3,e_o,e_\infty)$ is a change of basis.

We will see exactly what changes, what stays the same, and why a Gram matrix is
the natural way to represent the second basis directly.

## The short version

Start with three Euclidean vectors and an orthogonal Minkowski pair:

$$
e_1^2=e_2^2=e_3^2=e_+^2=+1,
\qquad
e_-^2=-1,
$$

with distinct basis vectors mutually orthogonal. Define

$$
e_o=\frac{e_- - e_+}{2},
\qquad
e_\infty=e_-+e_+.
$$

Then

$$
e_o^2=0,
\qquad
e_\infty^2=0,
\qquad
e_o\mathbin{\cdot}e_\infty=-1.
$$

The transformation is invertible:

$$
e_-=e_o+\frac12e_\infty,
\qquad
e_+=\frac12e_\infty-e_o.
$$

Therefore, both lists are bases of the same five-dimensional vector space.
They generate the same abstract Clifford algebra, $\mathrm{Cl}(4,1)$. They
simply describe its vectors and blades using different coordinate frames.

## What a basis change means

A vector is a geometric object; its coordinates are a description relative to
a chosen basis. Changing basis is like replacing one set of rulers with
another. The object does not move, but the numbers used to describe it change.

In ordinary two-dimensional Euclidean space, you might replace $(e_x,e_y)$
with rotated vectors $(u,v)$. Neither basis is the space itself. Each is a set
of independent vectors that spans the space.

The CGA change is similar, except that the affected two-dimensional plane has
Minkowski rather than Euclidean geometry. We replace an orthogonal pair with a
pair of null vectors.

The first three vectors do not change:

$$
e_1\mapsto e_1,
\qquad
e_2\mapsto e_2,
\qquad
e_3\mapsto e_3.
$$

Everything interesting happens in the plane spanned by $e_+$ and $e_-$. This
is often called the Minkowski plane of the conformal model.

## The starting orthogonal basis

The conventional orthogonal representation uses

$$
\mathcal{E}_{\mathrm{orth}}
=(e_1,e_2,e_3,e_+,e_-).
$$

Its metric is easy to state:

$$
e_i\mathbin{\cdot}e_j=0
\quad\text{for distinct basis vectors},
$$

and

$$
e_1^2=e_2^2=e_3^2=e_+^2=+1,
\qquad
e_-^2=-1.
$$

The Gram matrix is therefore diagonal:

$$
G_{\mathrm{orth}}=
\begin{pmatrix}
1&0&0&0&0\\
0&1&0&0&0\\
0&0&1&0&0\\
0&0&0&1&0\\
0&0&0&0&-1
\end{pmatrix}.
$$

A **Gram matrix** is simply the table of all pairwise inner products:

$$
G_{ij}=e_i\mathbin{\cdot}e_j.
$$

The diagonal records the squares of the basis vectors. The off-diagonal
entries record inner products between different basis vectors. A signature
list such as $(1,1,1,1,-1)$ is enough here only because the basis is
orthogonal, so all omitted off-diagonal entries are known to be zero.

## Constructing the null vectors

We want two vectors in the $e_+,e_-$ plane whose squares vanish. Consider a
general vector in that plane:

$$
v=a e_+ + b e_-.
$$

Because $e_+$ and $e_-$ are orthogonal,

$$
v^2=a^2e_+^2+b^2e_-^2=a^2-b^2.
$$

It is null when $a^2=b^2$, or equivalently when $a=\pm b$. Thus the two null
directions are proportional to

$$
e_- - e_+
\quad\text{and}\quad
e_- + e_+.
$$

CGA conventionally scales them as

$$
e_o=\frac{e_- - e_+}{2},
\qquad
e_\infty=e_-+e_+.
$$

The factor of $1/2$ is not needed merely to make $e_o$ null. It chooses the
useful normalization

$$
e_o\mathbin{\cdot}e_\infty=-1,
$$

which simplifies conformal point formulas.

The factor can instead be placed on $e_\infty$, or shared symmetrically by
dividing both null vectors by $\sqrt2$. For a self-contained derivation of this
freedom and its consequences, see
[Scaling the CGA Null Pair](cga-null-pair-scaling.md).

## Verifying the null identities

The inner product is bilinear. Scalars can be pulled out, and products expand
over addition. It is also symmetric for the real quadratic form used here.

First compute the square of $e_o$:

$$
\begin{aligned}
e_o^2
&=\left(\frac{e_- - e_+}{2}\right)^2\\
&=\frac14\left(
e_-^2
-2e_-\mathbin{\cdot}e_+
+e_+^2
\right)\\
&=\frac14(-1-0+1)\\
&=0.
\end{aligned}
$$

Likewise,

$$
\begin{aligned}
e_\infty^2
&=(e_-+e_+)^2\\
&=e_-^2+2e_-\mathbin{\cdot}e_++e_+^2\\
&=-1+0+1\\
&=0.
\end{aligned}
$$

Their mutual inner product is

$$
\begin{aligned}
e_o\mathbin{\cdot}e_\infty
&=\frac12(e_- - e_+)\mathbin{\cdot}(e_-+e_+)\\
&=\frac12\left(
e_-^2
+e_-\mathbin{\cdot}e_+
-e_+\mathbin{\cdot}e_-
-e_+^2
\right)\\
&=\frac12(-1-1)\\
&=-1.
\end{aligned}
$$

Notice the important distinction:

> A null vector is not the zero vector.

Both $e_o$ and $e_\infty$ are nonzero. Each has zero square, and each has a
nonzero inner product with the other.

## Proving that this is genuinely a basis

Replacing two vectors by two new vectors gives a basis only if the
transformation is invertible. Starting from

$$
2e_o=e_- - e_+,
\qquad
e_\infty=e_-+e_+,
$$

add and subtract the equations:

$$
e_-=e_o+\frac12e_\infty,
\qquad
e_+=\frac12e_\infty-e_o.
$$

Therefore $e_+$ and $e_-$ can be recovered from $e_o$ and $e_\infty$. The new
pair is linearly independent and spans exactly the same Minkowski plane.

This is the central reason the two CGA descriptions are equivalent: neither
one has gained or lost a direction.

## The change-of-basis matrix

Put the old basis vectors into the ordered list

$$
(e_1,e_2,e_3,e_+,e_-).
$$

The rows of the following matrix contain the old-basis coordinates of the new
basis vectors:

$$
T=
\begin{pmatrix}
1&0&0&0&0\\
0&1&0&0&0\\
0&0&1&0&0\\
0&0&0&-\frac12&\frac12\\
0&0&0&1&1
\end{pmatrix}.
$$

In this row convention,

$$
\begin{pmatrix}
e_1\\e_2\\e_3\\e_o\\e_\infty
\end{pmatrix}
=T
\begin{pmatrix}
e_1\\e_2\\e_3\\e_+\\e_-
\end{pmatrix}.
$$

The determinant of the final $2\times2$ block, and hence of $T$, is $-1$.
It is nonzero, confirming invertibility. The negative determinant also tells us
that this particular ordered basis change reverses orientation.

## How the Gram matrix changes

When rows of $T$ express the new basis in terms of the old basis, the new Gram
matrix is

$$
G_{\mathrm{null}}=T G_{\mathrm{orth}}T^{\mathsf T}.
$$

Carrying out the multiplication gives

$$
G_{\mathrm{null}}=
\begin{pmatrix}
1&0&0&0&0\\
0&1&0&0&0\\
0&0&1&0&0\\
0&0&0&0&-1\\
0&0&0&-1&0
\end{pmatrix}.
$$

The final $2\times2$ block is

$$
\begin{pmatrix}
0&-1\\
-1&0
\end{pmatrix}.
$$

Its diagonal zeros say that $e_o$ and $e_\infty$ are null. Its off-diagonal
entries say that their mutual inner product is $-1$.

This is precisely why a diagonal signature list cannot natively describe this
basis. The essential information lives off the diagonal.

## Null basis vectors do not imply a degenerate metric

This point is easy to miss. The diagonal of $G_{\mathrm{null}}$ contains two
zeros, but the metric is not degenerate.

A metric is degenerate if some nonzero vector is orthogonal to every vector in
the space. Equivalently, its Gram matrix has a nontrivial null space and zero
determinant.

The null-plane block has determinant

$$
0\cdot0-(-1)(-1)=-1,
$$

so it is invertible. Its eigenvalues are $+1$ and $-1$. Together with the three
Euclidean directions, the complete metric has four positive eigenvalues, one
negative eigenvalue, and no zero eigenvalues. Its inertia is therefore

$$
(p,q,r)=(4,1,0).
$$

The words **null vector** and **null space of the metric** describe different
ideas:

- A null vector has zero square.
- A vector in the metric's null space is orthogonal to every vector.

The native CGA basis contains null vectors, but the metric has no null space.

## What happens to the geometric product

For vectors $a$ and $b$,

$$
ab=a\mathbin{\cdot}b+a\wedge b.
$$

In the orthogonal basis, different basis vectors have zero inner product, so
their geometric product equals their outer product. For example,

$$
e_+e_-=e_+\wedge e_-.
$$

That simplification does not hold for the native null pair:

$$
e_oe_\infty=-1+e_o\wedge e_\infty,
$$

and

$$
e_\infty e_o=-1-e_o\wedge e_\infty.
$$

Adding the two products recovers the defining Clifford relation:

$$
e_oe_\infty+e_\infty e_o
=2e_o\mathbin{\cdot}e_\infty
=-2.
$$

This has an important implementation consequence. In a non-orthogonal basis,
the geometric product of two basis blades may produce a sum of basis blades.
It is no longer always one output bitmask multiplied by one scalar.

## What happens to blades

A basis change on vectors extends naturally to blades by preserving the outer
product. This extension is called an **outermorphism**.

For example,

$$
e_1\wedge e_o
=e_1\wedge\frac{e_- - e_+}{2}
=\frac12(e_1\wedge e_- - e_1\wedge e_+).
$$

The null-plane bivector becomes

$$
\begin{aligned}
e_o\wedge e_\infty
&=\frac12(e_- - e_+)\wedge(e_-+e_+)\\
&=-e_+\wedge e_-.
\end{aligned}
$$

The minus sign agrees with $\det(T)=-1$: the ordered change of basis reverses
orientation.

Grades do not change under an invertible basis transformation. Vectors remain
vectors, bivectors remain bivectors, and the pseudoscalar remains a
pseudoscalar, although its coordinate coefficients and possibly its
orientation sign change.

## Why the null basis is useful in CGA

Let $x$ be an ordinary Euclidean vector in the span of $e_1,e_2,e_3$. Its
conformal embedding is

$$
X(x)=e_o+x+\frac12x^2e_\infty.
$$

The Euclidean subspace is orthogonal to both $e_o$ and $e_\infty$. Using the
null identities,

$$
\begin{aligned}
X(x)^2
&=e_o^2+x^2
+2\left(\frac12x^2\right)
e_o\mathbin{\cdot}e_\infty
+\left(\frac12x^2\right)^2e_\infty^2\\
&=0+x^2-x^2+0\\
&=0.
\end{aligned}
$$

Thus every Euclidean point is represented by a null vector. The chosen
normalization also gives

$$
X(x)\mathbin{\cdot}e_\infty=-1.
$$

For two embedded points,

$$
X(x)\mathbin{\cdot}X(y)
=-\frac12\lVert x-y\rVert^2.
$$

Euclidean distance is therefore encoded directly by an inner product in the
higher-dimensional algebra. This is one of the central ideas of conformal
geometric algebra.

## What this means for storage

Five basis vectors generate $2^5=32$ exterior basis blades. Galaga stores a
multivector as a length-32 coefficient array indexed by blade bitmasks.

In the orthogonal basis, the final vectors occupy bitmasks

```text
e+ -> 0b01000 -> coefficient index 8
e- -> 0b10000 -> coefficient index 16
```

The derived null vectors have two nonzero coefficients:

```text
eo   -> -0.5 at index 8, +0.5 at index 16
einf -> +1.0 at index 8, +1.0 at index 16
```

In the native null basis, the final basis vectors themselves are $e_o$ and
$e_\infty$:

```text
eo   -> 0b01000 -> coefficient index 8
einf -> 0b10000 -> coefficient index 16
```

Each is now one-hot. The price is that the metric can no longer be represented
by a diagonal signature. The shared Gram matrix must retain their $-1$ cross
term.

The vector is not a $5\times5$ matrix. There is one shared $5\times5$ Gram
matrix describing pairwise inner products, while each multivector still has
32 exterior-basis coefficients.

## Seeing the transformation in `galaga.core`

The numeric core constructs both metrics:

```python
import numpy as np

from galaga.core import Algebra, scalar_product

orthogonal = Algebra(4, 1)

null_gram = np.array(
    [
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, -1],
        [0, 0, 0, -1, 0],
    ],
    dtype=float,
)
native = Algebra(gram=null_gram)

T = np.eye(5)
T[3] = (0, 0, 0, -0.5, 0.5)  # eo = (em - ep) / 2
T[4] = (0, 0, 0, 1.0, 1.0)   # einf = em + ep

assert np.array_equal(T @ orthogonal.gram @ T.T, native.gram)

e1, e2, e3, eo, einf = native.basis_vectors()
assert scalar_product(eo, eo) == 0
assert scalar_product(einf, einf) == 0
assert scalar_product(eo, einf) == -1
```

The matrix congruence test is stronger than checking only the three final
assertions: it proves that every pairwise inner product transforms correctly.

## Common misconceptions

### "A zero diagonal entry means the algebra is degenerate"

Only in an orthogonal basis. For a general Gram matrix, degeneracy depends on
the complete matrix, not its diagonal.

### "A null vector is the zero vector"

No. A null vector is nonzero but has zero square. It can have nonzero inner
products with other vectors.

### "The signature is obtained by counting signs on the diagonal"

Only when the Gram matrix is diagonal. In a general basis, signature means the
numbers of positive, negative, and zero eigenvalue directions, equivalently
the inertia guaranteed by Sylvester's law.

### "Changing basis changes the Clifford algebra"

An invertible change of basis changes coordinates and the displayed Gram
matrix, but not the underlying quadratic space or abstract Clifford algebra.

### "The bitmask e45 means the geometric product eo*einf"

In a general basis, a bitmask denotes an exterior blade. Here `e45` means
$e_o\wedge e_\infty$. The geometric product also contains the scalar inner
product:

$$
e_oe_\infty=-1+e_o\wedge e_\infty.
$$

## Summary

The orthogonal and null descriptions are related by an invertible linear
transformation:

$$
(e_1,e_2,e_3,e_+,e_-)
\longleftrightarrow
(e_1,e_2,e_3,e_o,e_\infty).
$$

The orthogonal basis gives a diagonal Gram matrix and makes basis-blade
products simple. The null basis makes the geometrically meaningful origin and
infinity vectors native, at the cost of an off-diagonal metric and
multi-component basis-blade products.

Both representations describe the same $\mathrm{Cl}(4,1)$ algebra. A
Gram-native implementation allows Galaga to choose either basis honestly,
without hiding the null vectors as derived linear combinations.

## Related documentation

- [CGA null-pair scaling](cga-null-pair-scaling.md)
- [Architecture](architecture.md)
- [Algebra construction specification](specs/SPEC-001-algebra-construction-and-metric.md)
- [Canonical Gram-matrix decision](adrs/002-canonical-native-gram-matrix.md)
