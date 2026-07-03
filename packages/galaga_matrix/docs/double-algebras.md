# Double Clifford Algebras

## Short Version

In this package, "double algebra" means a real Clifford algebra whose
classification is a direct sum of two isomorphic simple matrix algebras:

$$
Cl(p,q) \cong A \oplus A.
$$

It is not the same idea as the spin double cover
$\operatorname{Spin}(p,q) \to SO(p,q)$, and it is not about a degenerate metric.
It is a statement about the real algebra itself.

The double cases are exactly the nondegenerate real Clifford algebras with

$$
s = (q-p) \bmod 8 \in \{3,7\}.
$$

In those cases, a single irreducible compact matrix representation only sees
one summand. It is still a valid algebra homomorphism, but it is not faithful:
different multivectors can produce the same matrix. A faithful compact
representation must include both summands, for example as a block-diagonal pair.

## The Classification Background

`galaga_matrix` uses the real Clifford algebra convention where $Cl(p,q)$ has
$p$ positive-square basis vectors and $q$ negative-square basis vectors:

$$
e_i^2 = +1 \quad (1 \le i \le p),
\qquad
e_i^2 = -1 \quad (p < i \le p+q).
$$

For nondegenerate real Clifford algebras, the Atiyah-Bott-Shapiro
classification is periodic modulo 8. In the package implementation the
classification key is:

$$
s = (q-p) \bmod 8.
$$

The compact classifier has these algebra types:

|  $s$ | Package type            | Abstract real algebra form            | Double? |
| ---: | ----------------------- | ------------------------------------- | ------- |
| 0, 6 | `real`                  | $M(k,\mathbb R)$                      | no      |
| 1, 5 | `complex`               | $M(k,\mathbb C)$                      | no      |
| 2, 4 | `quaternion`            | $M(k,\mathbb H)$                      | no      |
|    3 | `quaternion+quaternion` | $M(k,\mathbb H)\oplus M(k,\mathbb H)$ | yes     |
|    7 | `real+real`             | $M(k,\mathbb R)\oplus M(k,\mathbb R)$ | yes     |

The value of $k$ depends on $p+q$. The important structural point is whether
there is one simple matrix algebra or two copies of one.

## Why the Algebra Splits

Let

$$
I = e_1 e_2 \cdots e_n,
\qquad
n = p+q
$$

be the pseudoscalar. For odd $n$, the pseudoscalar commutes with every vector,
and therefore with every multivector:

$$
Ia = aI
\qquad
\text{for all } a \in Cl(p,q).
$$

Its square is

$$
I^2 =
(-1)^{n(n-1)/2}(-1)^q.
$$

When $I^2=-1$, the central pseudoscalar behaves like an internal imaginary unit.
The center is like $\mathbb C$, and the real algebra stays simple. This is what
happens in $Cl(3,0)$:

$$
Cl(3,0) \cong M(2,\mathbb C).
$$

When $I^2=+1$, the central pseudoscalar produces two real central idempotents:

$$
P_+ = \frac{1+I}{2},
\qquad
P_- = \frac{1-I}{2}.
$$

They satisfy

$$
P_+^2=P_+,
\qquad
P_-^2=P_-,
\qquad
P_+P_-=0,
\qquad
P_+ + P_- = 1.
$$

Because they are central, every multivector splits into two independent pieces:

$$
a = aP_+ + aP_-.
$$

The cross-products vanish:

$$
(aP_+)(bP_-) = abP_+P_- = 0.
$$

So the algebra decomposes as a direct sum of two two-sided ideals:

$$
Cl(p,q) = Cl(p,q)P_+ \oplus Cl(p,q)P_-.
$$

Those two ideals are the two summands in the double algebra.

## Simplest Example: $Cl(1,0)$

The algebra $Cl(1,0)$ has one generator $e$ with

$$
e^2=1.
$$

A general multivector is

$$
a + be.
$$

The pseudoscalar is just $I=e$, so

$$
P_+ = \frac{1+e}{2},
\qquad
P_- = \frac{1-e}{2}.
$$

The direct-sum isomorphism is:

$$
a+be
\longmapsto
(a+b,\ a-b).
$$

Multiplication is componentwise:

$$
(x_+,x_-)(y_+,y_-)
=
(x_+y_+,\ x_-y_-).
$$

So:

$$
Cl(1,0) \cong \mathbb R \oplus \mathbb R.
$$

The two irreducible one-dimensional representations are:

$$
\rho_+(e)=+1,
\qquad
\rho_-(e)=-1.
$$

Either one is a valid representation, but neither is faithful. For example,
$\rho_+$ maps both $1$ and $e$ to the same scalar:

$$
\rho_+(1)=1,
\qquad
\rho_+(e)=1,
\qquad
\rho_+(1-e)=0.
$$

That is the basic failure mode for compact one-summand representations of
double algebras.

## Quaternionic Example: $Cl(0,3)$

The algebra $Cl(0,3)$ has three generators with negative square:

$$
e_1^2=e_2^2=e_3^2=-1.
$$

Its pseudoscalar

$$
I=e_1e_2e_3
$$

is central and satisfies

$$
I^2=+1.
$$

Therefore

$$
Cl(0,3) \cong \mathbb H \oplus \mathbb H.
$$

The package's compact $Cl(0,3)$ basis uses the matrices $i\sigma_1$,
$i\sigma_2$, and $i\sigma_3$. In that selected summand, the pseudoscalar maps
to the identity matrix:

$$
\rho(I)=1.
$$

Therefore

$$
\rho(1-I)=0,
\qquad
\rho(1+I)=2.
$$

So the compact representation distinguishes the $P_+$ summand and kills the
$P_-$ summand. Again, `to_matrix(..., mode="compact")` is a valid homomorphism,
but it cannot be inverted on the whole algebra.

## Why One Irreducible Representation Cannot Be Faithful

For a double algebra

$$
Cl(p,q) \cong A \oplus A,
$$

an element is really a pair:

$$
a = (a_+,a_-).
$$

A one-summand compact representation has the form:

$$
\rho_+(a_+,a_-) = \rho_A(a_+)
$$

or

$$
\rho_-(a_+,a_-) = \rho_A(a_-).
$$

The kernel is nonzero:

$$
\ker \rho_+ = \{(0,a_-): a_- \in A\},
$$

and similarly for $\rho_-$. That means there are always nonzero multivectors
that map to the zero matrix.

The real dimension count also shows the loss. The full Clifford algebra has

$$
\dim_{\mathbb R} Cl(p,q) = 2^n.
$$

Each summand has only half that many real degrees of freedom:

$$
\dim_{\mathbb R} A = 2^{n-1}.
$$

So a one-summand representation cannot contain enough information to recover a
general multivector in the full algebra.

## What This Means for `galaga_matrix`

`galaga_matrix` has two matrix modes:

| Mode           | Representation                          | Faithful for double algebras?         |
| -------------- | --------------------------------------- | ------------------------------------- |
| `left-regular` | left multiplication on the full algebra | yes                                   |
| `compact`      | classification-based small matrices     | not when only one summand is selected |

The left-regular representation is always faithful because it acts on the whole
algebra:

$$
L_a(x)=ax.
$$

In particular,

$$
L_a(1)=a,
$$

so the first column already contains the original multivector coefficients.

The compact one-summand representation is smaller, but for double algebras it
is not injective. That is why current strict inverse behavior is:

- `to_matrix(mv, mode="compact")` works for nondegenerate double algebras.
- `from_matrix(alg, mat, mode="compact")` raises `TypeError` when the compact
  blade system is rank deficient.
- `to_matrix(mv, mode="left-regular")` and `from_matrix(..., mode="left-regular")`
  roundtrip exactly.

The strict inverse is important. A least-squares inverse would silently pick one
best-fit preimage even though many different multivectors have the same compact
matrix.

## Faithful Compact Representations Need Both Summands

The natural faithful compact representation of a double algebra is not one
irreducible block. It is the direct sum of both irreducible blocks:

$$
\rho(a_+,a_-)
=
\begin{pmatrix}
\rho_A(a_+) & 0 \\
0 & \rho_A(a_-)
\end{pmatrix}.
$$

Equivalently, an API could return a pair:

$$
(\rho_A(a_+),\rho_A(a_-)).
$$

Either form preserves both components. It doubles the size of the one-summand
compact representation, but it is still usually much smaller than the
left-regular matrix.

This is the likely direction if `galaga_matrix` later adds faithful compact
roundtrips for double algebras.

## Relation to Quaternion APIs

The quaternion APIs intentionally reject double algebras such as $Cl(0,3)$.
That can look surprising because

$$
Cl(0,3) \cong \mathbb H \oplus \mathbb H
$$

contains quaternionic summands. The problem is that the full algebra is not a
single copy of $\mathbb H$; it is two independent copies. Returning one
quaternion would expose only one summand and hide the other.

So the package distinguishes:

- $Cl(0,2)\cong \mathbb H$: one quaternionic algebra, supported by quaternion
  output.
- $Cl(0,3)\cong \mathbb H\oplus\mathbb H$: two quaternionic algebras, rejected
  by the current quaternion matrix/spinor APIs.

A future API could represent $Cl(0,3)$ as a pair of quaternionic outputs, but
that would be a different convention from the current single quaternion-block
conversion.

## Relation to Spinor Columns

Double-algebra issues and spinor-column issues are related by the same
principle - injectivity - but they are not identical.

The compact full-matrix inverse asks whether the map

$$
a \mapsto \rho(a)
$$

is injective on the whole Clifford algebra.

The spinor-column conversion asks whether the map

$$
\psi \mapsto \rho(\psi)u
$$

is injective on the even subalgebra $Cl^0(p,q)$ for the selected reference
column $u$.

Those are different rank tests. For example, the current $Cl(3,1)$ spinor
column issue is not a double-algebra issue:

$$
Cl(3,1) \cong M(4,\mathbb R),
$$

so the full real algebra is simple. The failure there is that the currently
selected reference column has rank 4 on an 8-real-dimensional even subalgebra.

Conversely, a double full algebra can have an even-subalgebra spinor map that
roundtrips, because the even subalgebra may fit inside one selected summand.
The implementation therefore checks the actual rank of each conversion map
instead of relying only on the classification label.

## Examples

Some common double signatures are:

| Algebra   | $s=(q-p)\bmod 8$ | Decomposition                         |
| --------- | ---------------: | ------------------------------------- |
| $Cl(1,0)$ |                7 | $\mathbb R\oplus\mathbb R$            |
| $Cl(2,1)$ |                7 | $M(2,\mathbb R)\oplus M(2,\mathbb R)$ |
| $Cl(3,2)$ |                7 | $M(4,\mathbb R)\oplus M(4,\mathbb R)$ |
| $Cl(4,3)$ |                7 | $M(8,\mathbb R)\oplus M(8,\mathbb R)$ |
| $Cl(0,3)$ |                3 | $\mathbb H\oplus\mathbb H$            |
| $Cl(5,0)$ |                3 | $M(2,\mathbb H)\oplus M(2,\mathbb H)$ |
| $Cl(1,4)$ |                3 | $M(2,\mathbb H)\oplus M(2,\mathbb H)$ |
| $Cl(2,5)$ |                3 | $M(4,\mathbb H)\oplus M(4,\mathbb H)$ |

Non-examples are just as important:

| Algebra   | Decomposition    | Why it is not double                    |
| --------- | ---------------- | --------------------------------------- |
| $Cl(3,0)$ | $M(2,\mathbb C)$ | simple real algebra with complex center |
| $Cl(1,3)$ | $M(2,\mathbb H)$ | simple quaternionic matrix algebra      |
| $Cl(3,1)$ | $M(4,\mathbb R)$ | simple real matrix algebra              |
| $Cl(0,2)$ | $\mathbb H$      | single quaternion algebra               |

## Practical Rule

For users of `galaga_matrix`:

- Use `mode="left-regular"` when you need an exact matrix roundtrip for any
  algebra, including double and degenerate signatures.
- Use `mode="compact"` when you want small textbook-style matrices and only need
  `to_matrix`, or when `from_matrix` passes the strict rank and residual checks.
- Treat a one-summand compact representation of a double algebra as a valid
  representation of one irreducible module, not as a lossless encoding of the
  whole Clifford algebra.
- Do not infer spinor-column support from the double/non-double label. Spinor
  conversions have their own rank check on the selected reference-column map.
