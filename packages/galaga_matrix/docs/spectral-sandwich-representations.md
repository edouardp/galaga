# Spectral-Sandwich Matrix Representations

## Purpose and status

Sobczyk's matrix gateway suggests a constructive way to identify a Clifford
algebra element with a matrix over a smaller scalar algebra:

$$
m = R P M C.
$$

Here $m$ is a multivector, $M$ is its matrix representation, $P$ is an
idempotent, and $R$ and $C$ are reciprocal row and column frames. This is more
than a way to display $m$: with the right normalization, the sandwich is an
algebra isomorphism and matrix multiplication is exactly geometric
multiplication.

This document makes that statement precise, derives the inverse map, and works
through real, complex, and quaternionic examples. It is mathematical
background for `galaga_matrix`; it does not replace the package's accepted
representation ADRs or commit the implementation to this construction.

The phrase **spectral sandwich** is used here to distinguish the construction
from a Cartan matrix in Lie theory. It is also naturally understood as a
matrix-unit or Morita-frame construction.

## The construction

Let $A$ be a real unital algebra. For a simple real Clifford algebra,
Artin-Wedderburn classification gives

$$
A \cong M_n(D),
\qquad
D \in \{\mathbb R,\mathbb C,\mathbb H\}.
$$

Choose:

- an idempotent $p\in A$, so $p^2=p$;
- a copy of the coefficient algebra $D\subseteq A$ whose elements commute
  with $p$;
- elements $r_1,\ldots,r_n$ and $c_1,\ldots,c_n$ in $A$.

They must satisfy

$$
p c_i r_j p=\delta_{ij}p
\tag{1}
$$

and

$$
\sum_{i=1}^n r_i p c_i=1.
\tag{2}
$$

The corner must also be the chosen coefficient algebra:

$$
pAp=pD,
\tag{3}
$$

with $d\mapsto pd$ injective on $D$. Condition (3) makes it possible to read a
unique $D$-valued matrix entry out of a projected Clifford element.

Collect the frame elements into

$$
R=\begin{pmatrix}r_1&\cdots&r_n\end{pmatrix},
\qquad
C=\begin{pmatrix}c_1\\ \vdots\\ c_n\end{pmatrix},
\qquad
P=pI_n.
$$

Equations (1) and (2) become

$$
PCRP=P,
\qquad
RPC=1.
\tag{4}
$$

The second identity is essential. If only $PCRP=P$ holds, then $RPC$ is an
idempotent $q$ and the construction describes the corner $qAq$, not
necessarily all of $A$.

For $M\in M_n(D)$, define

$$
\Phi(M)=RPMC
=\sum_{i,j}r_i pM_{ij}c_j.
\tag{5}
$$

The map $\Phi$ reconstructs a multivector from its matrix representation.

## Why multiplication is preserved

Because $p$ commutes with every entry of $M$ and $N$,

$$
\begin{aligned}
\Phi(M)\Phi(N)
&=RPMC\,RPNC\\
&=RM(PCRP)NC\\
&=RMPNC\\
&=RPMNC\\
&=\Phi(MN).
\end{aligned}
$$

The identity is preserved as well:

$$
\Phi(I_n)=RPC=1.
$$

Thus the sandwich is a unital algebra homomorphism. Under conditions
(1)--(3), it is an isomorphism.

The elements

$$
E_{ij}=r_i p c_j
$$

make the matrix structure visible inside $A$:

$$
E_{ij}E_{k\ell}=\delta_{jk}E_{i\ell},
\qquad
\sum_iE_{ii}=1.
$$

This is the precise sense in which $R$ and $C$ are reciprocal. They are dual
relative to the corner projector $p$; they are not merely reciprocal vector
bases for the underlying quadratic space.

## Recovering the matrix

Let $a\in A$. The $(i,j)$ entry of its matrix representation is the unique
$d_{ij}\in D$ satisfying

$$
p c_i a r_j p=pd_{ij}.
\tag{6}
$$

Define

$$
\rho(a)_{ij}=d_{ij}.
$$

To verify that this is inverse to the sandwich, substitute (5):

$$
\begin{aligned}
p c_i\Phi(M)r_jp
&=\sum_{k,\ell}
  pc_ir_kp\,M_{k\ell}\,c_\ell r_jp\\
&=pM_{ij}.
\end{aligned}
$$

Consequently,

$$
\rho\bigl(\Phi(M)\bigr)=M,
\qquad
\Phi\bigl(\rho(a)\bigr)=a.
$$

The second identity follows by resolving the identity on both sides of $a$:

$$
\begin{aligned}
a
&=\left(\sum_i r_i p c_i\right)
  a
  \left(\sum_j r_j p c_j\right)\\
&=\sum_{i,j}r_i\left(p c_i a r_j p\right)c_j\\
&=\sum_{i,j}r_i p\rho(a)_{ij}c_j\\
&=\Phi\bigl(\rho(a)\bigr).
\end{aligned}
$$

It is therefore clearer to distinguish the two directions explicitly:

$$
\rho:A\longrightarrow M_n(D),
\qquad
\Phi:M_n(D)\longrightarrow A,
\qquad
\Phi(M)=RPMC.
$$

## A reusable two-by-two frame

The examples below all start from the same metric-derived frame. Let

$$
v^2=+1,
\qquad
u^2=s\in\{+1,-1\},
\qquad
uv=-vu.
$$

Set

$$
p=\frac{1+v}{2},
\qquad
R=\begin{pmatrix}1&u\end{pmatrix},
\qquad
C=\begin{pmatrix}1\\u^{-1}\end{pmatrix}
=\begin{pmatrix}1\\su\end{pmatrix}.
\tag{7}
$$

The sign in $C$ is derived from the metric: $u^{-1}=u/u^2=su$. Since $u$
anticommutes with $v$,

$$
pup=0,
\qquad
upu^{-1}=1-p.
$$

It follows immediately that

$$
PCRP=pI_2,
\qquad
RPC=p+upu^{-1}=1.
$$

The entry algebra $D$ depends on the remaining Clifford structure.

## Worked example: $\operatorname{Cl}_{1,1}\cong M_2(\mathbb R)$

Let

$$
e_0^2=+1,
\qquad
e_1^2=-1,
\qquad
e_0e_1=-e_1e_0.
$$

Take $v=e_0$, $u=e_1$, and $D=\mathbb R$. Equation (7) gives

$$
p=\frac{1+e_0}{2},
\qquad
R=\begin{pmatrix}1&e_1\end{pmatrix},
\qquad
C=\begin{pmatrix}1\\-e_1\end{pmatrix}.
$$

The generator matrices are derived from the sandwich conditions:

$$
\rho(e_0)=
\begin{pmatrix}
1&0\\0&-1
\end{pmatrix},
\qquad
\rho(e_1)=
\begin{pmatrix}
0&-1\\1&0
\end{pmatrix}.
$$

They compute the metric rather than assume it:

$$
\rho(e_0)^2=I_2,
\qquad
\rho(e_1)^2=-I_2,
\qquad
\rho(e_0)\rho(e_1)=-\rho(e_1)\rho(e_0).
$$

For the general multivector

$$
m=a+be_0+ce_1+de_{01},
$$

multiplication of the generator matrices gives

$$
\rho(m)=
\begin{pmatrix}
a+b&-c-d\\
c-d&a-b
\end{pmatrix}.
\tag{8}
$$

For example,

$$
m=2+3e_0+5e_1+7e_{01}
$$

has

$$
\rho(m)=
\begin{pmatrix}
5&-12\\-2&-1
\end{pmatrix}.
$$

Substitution into $R p\rho(m)C$ returns the original multivector.

## Worked example: $\operatorname{Cl}_{3,0}\cong M_2(\mathbb C)$

Let $e_0,e_1,e_2$ be orthogonal and square to $+1$. Choose

$$
p=\frac{1+e_0}{2},
\qquad
R=\begin{pmatrix}1&e_1\end{pmatrix},
\qquad
C=\begin{pmatrix}1\\e_1\end{pmatrix}.
$$

The element

$$
\mathbf i=e_1e_2
$$

satisfies $\mathbf i^2=-1$ and commutes with $p$. Hence

$$
D=\operatorname{span}_{\mathbb R}\{1,\mathbf i\}\cong\mathbb C.
$$

The generator matrices are

$$
\rho(e_0)=
\begin{pmatrix}1&0\\0&-1\end{pmatrix},
\qquad
\rho(e_1)=
\begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad
\rho(e_2)=
\begin{pmatrix}0&-\mathbf i\\\mathbf i&0\end{pmatrix}.
\tag{9}
$$

These are $\sigma_3$, $\sigma_1$, and $\sigma_2$, respectively. Their names
and order depend on the chosen frame; their Clifford relations do not.

Consider

$$
m=2+3e_0-e_1+4e_2+5e_{01}.
$$

Using $\rho(e_{01})=\rho(e_0)\rho(e_1)$ gives

$$
\rho(m)=
\begin{pmatrix}
5&4-4\mathbf i\\
-6+4\mathbf i&-1
\end{pmatrix}.
\tag{10}
$$

Applying the sandwich gives

$$
R p\rho(m)C
=2+3e_0-e_1+4e_2+5e_{01}.
$$

Equation (9) also explains why the Pauli representation is intrinsic up to
similarity and permutation: it comes from a choice of primitive idempotent and
reciprocal frame, not from a unique distinguished array of numbers.

## Worked example: $\operatorname{Cl}_{4,0}\cong M_2(\mathbb H)$

Let $e_0,e_1,e_2,e_3$ be orthogonal and square to $+1$. Use the same
projector and two-component frame:

$$
p=\frac{1+e_0}{2},
\qquad
R=\begin{pmatrix}1&e_1\end{pmatrix},
\qquad
C=\begin{pmatrix}1\\e_1\end{pmatrix}.
$$

Define quaternion units inside $\operatorname{Cl}_{4,0}$ by

$$
\mathbf i=e_1e_2,
\qquad
\mathbf j=e_1e_3,
\qquad
\mathbf k=-e_2e_3.
\tag{11}
$$

The signs follow from the geometric product:

$$
\mathbf i^2=\mathbf j^2=\mathbf k^2=-1,
\qquad
\mathbf i\mathbf j=\mathbf k,
\quad
\mathbf j\mathbf k=\mathbf i,
\quad
\mathbf k\mathbf i=\mathbf j.
$$

Thus

$$
D=\operatorname{span}_{\mathbb R}
\{1,\mathbf i,\mathbf j,\mathbf k\}
\cong\mathbb H.
$$

Every element of $D$ commutes with $p$. The four vector matrices are

$$
\begin{aligned}
\rho(e_0)&=
\begin{pmatrix}1&0\\0&-1\end{pmatrix},
&
\rho(e_1)&=
\begin{pmatrix}0&1\\1&0\end{pmatrix},\\[6pt]
\rho(e_2)&=
\begin{pmatrix}0&-\mathbf i\\\mathbf i&0\end{pmatrix},
&
\rho(e_3)&=
\begin{pmatrix}0&-\mathbf j\\\mathbf j&0\end{pmatrix}.
\end{aligned}
\tag{12}
$$

They square to $I_2$ and anticommute pairwise, as required by the Euclidean
metric.

For a mixed-grade example, take

$$
m=1+2e_0+3e_2+4e_{03}+5e_{23}.
$$

Because $e_{23}=-\mathbf k$ and matrix multiplication represents the
geometric product,

$$
\rho(m)=
\begin{pmatrix}
3-5\mathbf k&-3\mathbf i-4\mathbf j\\
3\mathbf i-4\mathbf j&-1-5\mathbf k
\end{pmatrix}.
\tag{13}
$$

Direct substitution verifies

$$
R p\rho(m)C
=1+2e_0+3e_2+4e_{03}+5e_{23}.
$$

The quaternion entries can themselves be represented by $2\times2$ complex
blocks. Under that secondary embedding, the $2\times2$ quaternion matrix in
(13) becomes a constrained $4\times4$ complex matrix. It remains a real
algebra representation of $M_2(\mathbb H)$; it is not an arbitrary element of
$M_4(\mathbb C)$.

## Verification with Galaga

The algebraic claims in the quaternionic example can be checked directly with
the public Galaga facade:

```python
from galaga.facade import Algebra

cl4 = Algebra((1, 1, 1, 1))
e0, e1, e2, e3 = cl4.basis_vectors()

p = (1 + e0) / 2

assert p * p == p
assert p * e1 * p == 0
assert p + e1 * p * e1 == cl4.identity

i = e1 * e2
j = e1 * e3
k = -(e2 * e3)

assert i * i == j * j == k * k == -cl4.identity
assert i * j == k
assert j * k == i
assert k * i == j

M = [
    [3 - 5 * k, -3 * i - 4 * j],
    [3 * i - 4 * j, -1 - 5 * k],
]


def phi(matrix):
    return (
        p * matrix[0][0]
        + p * matrix[0][1] * e1
        + e1 * p * matrix[1][0]
        + e1 * p * matrix[1][1] * e1
    )


m = 1 + 2 * e0 + 3 * e2 + 4 * e0 * e3 + 5 * e2 * e3
assert phi(M) == m
```

Galaga displays its default Euclidean basis as $e_1,e_2,e_3,e_4$; the local
Python names `e0`, ..., `e3` above follow the zero-based notation used in the
derivation.

## Where a single sandwich does not suffice

### Direct-sum Clifford algebras

When the real Clifford algebra is semisimple rather than simple, it has two
matrix-algebra summands. For example,

$$
\operatorname{Cl}_{0,3}\cong\mathbb H\oplus\mathbb H.
$$

A primitive idempotent in one summand cannot see the other summand. A single
spectral sandwich is therefore non-faithful: it projects away part of the
multivector. An exact compact representation needs two central projectors and
one frame per summand, followed by a block-direct-sum representation.

This is the same obstruction documented in
[Double Clifford Algebras](double-algebras.md). The left-regular
representation remains an exact fallback.

### Degenerate metrics

For $\operatorname{Cl}_{p,q,r}$ with $r>0$, the null directions introduce a
nontrivial radical. The algebra is not a simple matrix algebra over
$\mathbb R$, $\mathbb C$, or $\mathbb H$, so the construction above does not
directly provide a plain compact matrix representation.

A matrix whose entries belong to an exterior or nilpotent coefficient algebra
may still be possible, but that is a different representation target. Galaga
currently uses the real left-regular representation for these metrics.

### Nonorthogonal bases

A nondegenerate symmetric Gram matrix can be transformed to an orthogonal
canonical frame. A sandwich frame may be built there and transported back to
the user's basis. The transport must preserve the complete Gram matrix:

$$
\rho(v_i)\rho(v_j)+\rho(v_j)\rho(v_i)
=2G_{ij}I.
$$

In particular, the signs and reciprocal elements in $C$ must be derived from
the metric. They must not be selected from the expected signature by hand.
Until that basis transport has an independently checked roundtrip, Galaga's
left-regular representation is the safe native-basis representation.

## Possible role in `galaga_matrix`

The construction suggests a possible future internal representation
descriptor containing:

1. the coefficient algebra $D$;
2. a primitive or central idempotent $p$;
3. the row and column frames $R,C$;
4. entry extraction from the corner $pAp$;
5. one descriptor per simple summand.

Such a descriptor could derive generator matrices, matrix-to-multivector
roundtrips, and quaternion blocks from algebraic data rather than independent
signature-specific recipes.

Any implementation should validate the algebra before accepting a frame:

1. compute $p^2=p$;
2. compute $pc_ir_jp=\delta_{ij}p$;
3. compute $\sum_i r_ipc_i=1$;
4. derive each generator matrix through the projected inverse (6);
5. verify the full Gram relation;
6. verify basis-blade roundtrips;
7. verify $\rho(ab)=\rho(a)\rho(b)$ on basis blades and sampled
   multivectors;
8. verify that the real rank equals $\dim_{\mathbb R}A$.

These checks keep the implementation tied to the algebra rather than to an
expected display convention.

## Terminology

The expression $m=RPMC$ reconstructs $m$ from $M$; it does not itself compute
$M$. Accordingly:

- use $\rho(m)=M$ for multivector-to-matrix conversion;
- use $\Phi(M)=RPMC$ for matrix-to-multivector reconstruction;
- call $p$ a primitive idempotent when it is primitive, rather than merely a
  projector;
- call $R,C$ a reciprocal spectral frame or matrix-unit frame;
- avoid the unqualified phrase *Cartan matrix*, which normally refers to a
  different object in Lie theory.

The quaternion algebra in the $\operatorname{Cl}_{4,0}$ example is an embedded
bivector subalgebra isomorphic to $\operatorname{Cl}_{0,2}$. Saying that its
entries "are $\operatorname{Cl}_{0,2}$ multivectors" is correct only after
that embedding or isomorphism has been specified.

## References

- Garret Sobczyk, [*Matrix Gateway to Geometric Algebra, Spacetime and
  Spinors*](https://garretstar.com/clemson18-nov-2019.pdf), overview slides,
  2019.
- Garret Sobczyk, [*Geometric Matrix
  Algebra*](https://doi.org/10.1016/j.laa.2007.06.015), *Linear Algebra and its
  Applications* 429 (2008), 1163--1173.
- Garret Sobczyk, [*The Missing Spectral Basis in Algebra and Number
  Theory*](https://doi.org/10.1080/00029890.2001.11919757), *American
  Mathematical Monthly* 108 (2001), 336--346.
- Wolfram Research,
  [*Matrix Gateway*](https://resources.wolframcloud.com/PacletRepository/resources/Wolfram/GeometricAlgebra/tutorial/MatrixGateway.html),
  executable examples of matrix/multivector conversion and multiplication.
