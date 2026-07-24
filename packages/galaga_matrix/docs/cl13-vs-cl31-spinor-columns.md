# Why $Cl(1,3)$ Spinor Columns Roundtrip but $Cl(3,1)$ Currently Does Not

## Short Version

Both signatures can be useful for spacetime algebra work, but the current
`galaga_matrix` spinor-column API is testing a stricter thing than "can I do STA
algebra with this signature?"

The API checks whether the specific map

$$
\Phi_u : Cl^0(p,q) \to \mathbb C^k,
\qquad
\Phi_u(\psi) = \rho(\psi)u
$$

is injective for the package's selected compact representation $\rho$ and its
selected reference column $u$.

For the current implementation:

| Algebra | Real algebra type | Even dof | Reference-column rank | Result |
|---|---|---:|---:|---|
| $Cl(1,3)$ | $M(2,\mathbb H)$ | 8 | 8 | supported |
| $Cl(3,1)$ | $M(4,\mathbb R)$ | 8 | 4 | rejected |

So $Cl(3,1)$ is not rejected because it is useless for STA. It is rejected
because the currently selected reference column loses half of the even
subalgebra.

## What "Works" Means

There are several different senses in which a Clifford algebra can "work":

1. **Geometric algebra operations work.** Products, reverses, rotors, sandwich
   products, and grade projections can all be valid.
2. **A matrix representation works.** The gamma matrices satisfy the Clifford
   relations:

   $$
   \gamma_i\gamma_j + \gamma_j\gamma_i = 2g_{ij}I.
   $$
3. **A spinor-column roundtrip works.** A single column $\rho(\psi)u$ contains
   enough information to recover every even multivector $\psi \in Cl^0(p,q)$.

The current `to_spinor_column` / `from_spinor_column` API requires the third
condition. That condition is stronger than the first two.

## Real Signatures Are Not Just Cosmetic

Over the complex numbers, the two signatures become equivalent:

$$
Cl(1,3)\otimes\mathbb C
\cong
Cl(3,1)\otimes\mathbb C
\cong
M(4,\mathbb C).
$$

That is why both signatures can have familiar complex gamma matrices. The
metric signs can be moved around by factors of $i$ after complexification.

Over the real numbers, however, the algebras are different. In the
`galaga_matrix` convention, $Cl(p,q)$ has $p$ positive-square generators and
$q$ negative-square generators, and the classification uses

$$
s = (q-p) \bmod 8.
$$

For the two STA signatures:

$$
Cl(1,3) \cong M(2,\mathbb H),
$$

while

$$
Cl(3,1) \cong M(4,\mathbb R).
$$

So they are not the same real Clifford algebra. They do share closely related
spin geometry, and their even subalgebras are both isomorphic to a real form of
$M(2,\mathbb C)$:

$$
Cl^0(1,3) \cong Cl(3,0) \cong M(2,\mathbb C),
$$

and

$$
Cl^0(3,1) \cong Cl(1,2) \cong M(2,\mathbb C).
$$

That shared even-algebra structure is why both signatures can feel like valid
STA choices in notebooks.

## The Column Map Being Tested

The spinor-column conversion does not simply ask whether a complex matrix
representation exists. It builds a real linear map from even coefficients to a
complex column.

For even basis blades $E_i$, the implementation computes:

$$
A_i = \rho(E_i)u.
$$

It then stacks real and imaginary parts:

$$
A =
\begin{pmatrix}
\operatorname{Re}(A_1) & \operatorname{Re}(A_2) & \cdots \\
\operatorname{Im}(A_1) & \operatorname{Im}(A_2) & \cdots
\end{pmatrix}.
$$

The conversion can roundtrip exactly only when:

$$
\operatorname{rank}_{\mathbb R}(A) =
\dim_{\mathbb R} Cl^0(p,q).
$$

For four-dimensional nondegenerate algebras, the even subalgebra has

$$
\dim_{\mathbb R} Cl^0 = 2^{4-1} = 8
$$

real degrees of freedom. A $4 \times 1$ complex column also has 8 real degrees
of freedom, so a full-rank map is possible. It is not automatic.

## What Happens for $Cl(1,3)$

For $Cl(1,3)$, `galaga_matrix` uses the standard Dirac compact basis:

$$
(\gamma^0)^2 = +I,
\qquad
(\gamma^i)^2 = -I
\quad (i=1,2,3).
$$

The reference-vector algorithm chooses the first nonzero column of

$$
p = \frac12(I+\gamma^0).
$$

In this basis, that gives:

$$
u =
\begin{pmatrix}
1\\0\\0\\0
\end{pmatrix}.
$$

The computed real system has:

$$
A \in \mathbb R^{8\times 8},
\qquad
\operatorname{rank}(A)=8.
$$

The singular values are all 1:

$$
1,1,1,1,1,1,1,1.
$$

Therefore no nonzero even multivector annihilates the chosen reference column:

$$
\rho(\psi)u=0
\quad\Longrightarrow\quad
\psi=0
\qquad
(\psi\in Cl^0(1,3)).
$$

That is why the current API supports:

```python
to_spinor_column(psi)
from_spinor_column(sta, column)
```

for $Cl(1,3)$.

## What Happens for $Cl(3,1)$

For $Cl(3,1)$, the package uses a mostly-plus compact basis:

$$
(\gamma^1)^2=(\gamma^2)^2=(\gamma^3)^2=+I,
\qquad
(\gamma^0)^2=-I.
$$

The real algebra type is different:

$$
Cl(3,1)\cong M(4,\mathbb R).
$$

The current reference-vector algorithm first tries to build a projector from a
positive-square gamma. For the selected compact basis, it chooses a reference
column equivalent to:

$$
u =
\begin{pmatrix}
\frac12\\
0\\
0\\
\frac12
\end{pmatrix}.
$$

With that specific $u$, the real system has:

$$
A \in \mathbb R^{8\times 8},
\qquad
\operatorname{rank}(A)=4.
$$

The singular values are:

$$
1,1,1,1,0,0,0,0.
$$

So there is a nontrivial kernel:

$$
\ker \Phi_u =
\{\psi\in Cl^0(3,1) : \rho(\psi)u=0\}
\neq 0.
$$

Using the default $Cl(3,1)$ basis ordering $e_1,e_2,e_3,e_4$, with
$e_1,e_2,e_3$ positive and $e_4$ negative, the following nonzero even elements
annihilate the selected reference column:

$$
\rho(1+e_{24})u = 0,
$$

$$
\rho(e_{13}-e_{1234})u = 0,
$$

$$
\rho(e_{12}+e_{14})u = 0,
$$

$$
\rho(-e_{23}+e_{34})u = 0.
$$

That means the column cannot distinguish $\psi$ from $\psi+n$ for any $n$ in
this kernel:

$$
\rho(\psi+n)u =
\rho(\psi)u+\rho(n)u =
\rho(\psi)u.
$$

An inverse would have to guess which preimage was intended. The implementation
therefore rejects the conversion instead of returning a least-squares
projection.

## This Does Not Mean $Cl(3,1)$ Cannot Have Spinors

The rejection is not a theorem that $Cl(3,1)$ has no spinors. It is a statement
about the current package convention:

$$
\text{selected compact representation} +
\text{selected reference column} +
\text{single-column inverse}
$$

is not faithful for $Cl(3,1)$.

A different reference column can make the same rank test pass. For example,
with the current compact $Cl(3,1)$ matrices, the simple reference column

$$
u =
\begin{pmatrix}
1\\0\\0\\0
\end{pmatrix}
$$

gives rank 8 for the even-column map. Generic real or complex reference columns
also give rank 8 in the current representation.

Supporting $Cl(3,1)$ spinor-column roundtrips would therefore require a
deliberate convention change or extension, such as:

- choose a rank-checked reference column instead of the current projector-first
  reference;
- document the resulting $Cl(3,1)$ column convention;
- add tests showing that the inverse reconstructs all even coefficients;
- check that the convention behaves well for the intended physics examples.

Until that decision is made, the safer behavior is to reject $Cl(3,1)$ for
`to_spinor_column` / `from_spinor_column`.

## Why Your STA Notebook Can Still Be Right

If your notebook found that both $Cl(1,3)$ and $Cl(3,1)$ "work for STA", that is
not in conflict with this behavior.

It may have been testing one of these facts:

- both signatures support valid geometric algebra products;
- both can represent spacetime vectors and bivectors with different sign
  conventions;
- both have valid gamma matrices after complexification;
- both support rotor-style calculations when the metric signs are handled
  consistently;
- both have even subalgebras related to $M(2,\mathbb C)$.

The spinor-column API is testing something narrower:

$$
\psi \mapsto \rho(\psi)u
$$

must be injective on every even multivector for the selected $u$.

For $Cl(1,3)$, the current selected $u$ is cyclic enough to recover all 8 real
even coefficients. For $Cl(3,1)$, the current selected $u$ is not.

## Practical Rule

Use this distinction:

- Use `to_matrix(..., mode="compact")` when you want the compact gamma-matrix
  representation of $Cl(1,3)$ or $Cl(3,1)$.
- Use `mode="left-regular"` when you need an always-faithful matrix
  representation and exact inverse conversion.
- Use `to_spinor_column` / `from_spinor_column` only for signatures whose
  selected reference-column map passes the rank check.

At the moment, that means $Cl(1,3)$ is supported and $Cl(3,1)$ is rejected by
the spinor-column roundtrip API.
