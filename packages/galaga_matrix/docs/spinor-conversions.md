# Spinor Column Conversions

## Overview

This document specifies conversion between even-grade multivectors in $Cl(p,q)$
and spinor column vectors. The implementation uses a fixed reference column,
not a general "dimension is large enough" rule:

$$
\operatorname{spinor}(\psi) = \rho(\psi) u
$$

where $\rho$ is the selected matrix representation and $u$ is a fixed reference
spinor column for that representation. The inverse conversion solves the real
linear system induced by this exact map over the even basis blades.

## Core Definitions

### GA spinor

In geometric algebra, a spinor is an element of the even subalgebra $Cl^0(p,q)$.
A rotor is a normalized even versor, but the conversion here accepts any even
multivector, not only normalized rotors.

Examples:

- $Cl(3,0)$: $Cl^0$ is spanned by $\{1, e_{12}, e_{13}, e_{23}\}$ in
  canonical ascending blade order. If using the geometric product name
  $e_{31} = e_3 e_1$, remember $e_{31} = -e_{13}$.
- $Cl(1,3)$: $Cl^0$ is 8-dimensional.

### Column spinor

The matrix/physics-style spinor is a column vector in the representation space.
For example:

- $Cl(3,0)$ with Pauli matrices gives a 2-component complex column.
- $Cl(1,3)$ with the package's standard Dirac compact representation gives a
  4-component complex column.

For quaternionic algebras represented as 2x2 complex blocks, the complex matrix
is a faithful real representation of a quaternionic matrix algebra. Its image is
a proper real subalgebra of the ambient complex matrices.

## Reference-Vector Algorithm

The implementation chooses a stable reference column as follows:

1. Build compact gamma matrices.
2. Choose an idempotent-like projector $p = \frac12(I + \gamma)$ from the first
   diagonal positive-square gamma, falling back to the first positive-square
   gamma, then to the first coordinate projector.
3. Use the first nonzero column of $p$ as the reference vector $u$.

This projector is only a way to choose $u$. It is not treated as a primitive
complex idempotent for every algebra. In $Cl(1,3)$, $\frac12(I + \gamma^0)$ has
complex rank 2, so the implementation uses its first nonzero column as $u$,
rather than claiming a one-column minimal left ideal from the whole projector.

## Roundtrip Condition

Dimension is only a necessary condition. The actual condition is injectivity of
the concrete reference-vector map on the even subalgebra.

For even basis blades $E_i$, build:

$$
A_i = \rho(E_i)u
$$

Then stack real and imaginary parts to form a real matrix $A$. A faithful
roundtrip is supported exactly when:

$$
\operatorname{rank}_{\mathbb R}(A) = \dim_{\mathbb R} Cl^0(p,q)
$$

`_spinor_roundtrip_possible(alg)` computes this rank directly.

Examples currently covered by the rank check:

| Algebra   |     Result | Notes                                   |
| --------- | ---------: | --------------------------------------- |
| $Cl(3,0)$ | roundtrips | Pauli spinor, 4 real dof                |
| $Cl(1,3)$ | roundtrips | Dirac column, 8 real dof                |
| $Cl(0,2)$ | roundtrips | overdetermined complex column           |
| $Cl(4,0)$ | roundtrips | compact complex column                  |
| $Cl(3,1)$ |   rejected | selected map has rank 4 for 8 even dof  |
| $Cl(2,2)$ |   rejected | selected map has rank 4 for 8 even dof  |
| $Cl(4,1)$ |   rejected | selected map has rank 8 for 16 even dof |

See [Why $Cl(1,3)$ Spinor Columns Roundtrip but $Cl(3,1)$ Currently Does
Not](cl13-vs-cl31-spinor-columns.md) for the signature-specific explanation.

## `to_spinor_column`

Preconditions:

- Input must be even-grade.
- The selected reference-vector map must be full-rank over the even subalgebra.

Algorithm:

```text
function to_spinor_column(mv):
    verify mv is even
    A, even_indices = spinor_system_matrix(mv.algebra)
    verify rank(A) == len(even_indices)
    u = spinor_reference_vector(mv.algebra)
    return compact_matrix(mv) @ u
```

## `from_spinor_column`

Preconditions:

- Input must be shaped `(k, 1)` or `(k,)`.
- The selected reference-vector map must be full-rank.
- The supplied column must lie in the image of the map.

Algorithm:

```text
function from_spinor_column(alg, spinor):
    A, even_indices = spinor_system_matrix(alg)
    verify rank(A) == len(even_indices)
    reshape spinor to (k, 1)
    b = [Re(spinor); Im(spinor)]
    coeffs = solve A coeffs = b by least squares
    verify residual norm is near zero
    place coeffs in the even blade positions
    return Multivector(alg, data)
```

The residual check matters in overdetermined cases. For example, $Cl(0,2)$ has a
2-real-dimensional even subalgebra but a 2-component complex column; not every
complex column is the image of an even multivector.

## $Cl(3,0)$ Pauli Conventions

The compact basis maps:

$$
\begin{aligned}
e_1 &\mapsto \sigma_1,\\
e_2 &\mapsto \sigma_2,\\
e_3 &\mapsto \sigma_3.
\end{aligned}
$$

Using canonical ascending blade order:

$$
\begin{aligned}
e_{12} &\mapsto i\sigma_3,\\
e_{13} &\mapsto -i\sigma_2,\\
e_{23} &\mapsto i\sigma_1.
\end{aligned}
$$

If writing $e_{31} = e_3 e_1$, then $e_{31} = -e_{13}$ and:

$$
e_{31} \mapsto i\sigma_2.
$$

With reference column $(1, 0)^T$, the extracted columns are:

$$
\begin{aligned}
1 &\mapsto \begin{pmatrix}1\\0\end{pmatrix},\\
e_{12} &\mapsto \begin{pmatrix}i\\0\end{pmatrix},\\
e_{13} &\mapsto \begin{pmatrix}0\\1\end{pmatrix},\\
e_{23} &\mapsto \begin{pmatrix}0\\i\end{pmatrix}.
\end{aligned}
$$

For a spinor column $(\alpha, \beta)^T$, the reconstructed canonical even
multivector is:

$$
\operatorname{Re}(\alpha)
+ \operatorname{Im}(\alpha)e_{12}
+ \operatorname{Re}(\beta)e_{13}
+ \operatorname{Im}(\beta)e_{23}.
$$

If expressed with $e_{31}$, the $e_{31}$ coefficient is $-\operatorname{Re}(\beta)$.

## $Cl(1,3)$ Complex Spinors

The standard compact representation uses the Dirac gamma matrices in the Dirac
basis. The reference vector is the first nonzero column chosen from
$\frac12(I + \gamma^0)$, so the identity maps to:

$$
\begin{pmatrix}
1\\
0\\
0\\
0
\end{pmatrix}.
$$

This is a reference-vector convention. It should not be described as extracting
one complex column from a primitive complex idempotent, because
$\frac12(I + \gamma^0)$ has complex rank 2.

The current $Cl(1,3)$ complex column is in the standard Dirac basis, not the
Weyl/chiral basis. See [Dirac, Weyl, and Majorana Spinor
Bases](dirac-and-weyl-spinor-bases.md) for the basis distinction, the
left/right Weyl split, charge-conjugation conventions, and future
implementation plans. For a broader conceptual comparison with pure STA, see
[QM Spinor Bases and STA Translation](qm-bases-and-sta-translation.md).

## Quaternionic Matrix and Spinor APIs

The quaternion APIs use an explicit quaternion-block representation. They do
not reinterpret the standard Dirac compact matrices block-by-block.

The complex embedding is:

$$
a + bi + cj + dk
\longleftrightarrow
\begin{pmatrix}
a + bi & c + di \\
-c + di & a - bi
\end{pmatrix}
$$

Currently supported quaternion-block bases:

- $Cl(0,2)$: the compact basis is already in quaternion-block form.
- $Cl(1,3)$: the quaternion APIs use a separate $M(2,\mathbb H)$ basis:

$$
\gamma^0 =
\begin{pmatrix}
1 & 0\\
0 & -1
\end{pmatrix},
\quad
\gamma^1 =
\begin{pmatrix}
0 & i\\
i & 0
\end{pmatrix},
$$

$$
\gamma^2 =
\begin{pmatrix}
0 & j\\
j & 0
\end{pmatrix},
\quad
\gamma^3 =
\begin{pmatrix}
0 & k\\
k & 0
\end{pmatrix}.
$$

where the entries are quaternions. These matrices square to the (+---)
signature and anticommute.

`to_spinor_quaternion` applies the quaternion-block representation to the fixed
reference column and then packs each pair of complex entries as one quaternion.
`from_spinor_quaternion` solves the corresponding rank-checked real system.

Double algebras such as $Cl(0,3)$ are rejected by quaternion APIs. Choosing one
summand of a double algebra is not exposed as a quaternionic matrix/spinor
conversion. See [Double Clifford Algebras](double-algebras.md) for the
direct-sum background.

The two quaternion components of a $Cl(1,3)$ spinor should not be identified with
Weyl chiralities unless a chiral basis and that identification are explicitly
chosen. The current API makes no such claim.

## Normalization

The spinor conversion works for any even element.

For $Cl(3,0)$ Pauli spinors, a normalized rotor maps the selected reference state
to a unit vector under the ordinary Hermitian norm.

For $Cl(1,3)$, rotor normalization $R\widetilde{R} = 1$ is Lorentz-group
normalization, not ordinary positive-definite Hermitian normalization. Boost
spinor matrices are not unitary under $\psi^\dagger \psi$. Invariant bilinears use
the Dirac adjoint or the corresponding GA scalar bilinears.

## Error Cases

| Condition                                   | Error        | Message                                              |
| ------------------------------------------- | ------------ | ---------------------------------------------------- |
| Odd-grade components in input               | `ValueError` | `requires an even-grade multivector`                 |
| Selected spinor map is rank-deficient       | `TypeError`  | `does not support faithful spinor roundtrip`         |
| Supplied spinor column is outside the image | `ValueError` | `not in the image`                                   |
| Non-quaternionic algebra for quaternion API | `TypeError`  | `not quaternionic`                                   |
| Quaternionic double algebra                 | `TypeError`  | `not a single quaternionic matrix algebra`           |
| Unsupported quaternion-block basis          | `TypeError`  | `Quaternion block representation is not implemented` |
| Wrong spinor shape or quaternion length     | `ValueError` | `Expected ...`                                       |

## API Summary

| Function                              | Direction                    | Representation                  |
| ------------------------------------- | ---------------------------- | ------------------------------- |
| `to_spinor_column(mv)`                | even MV -> complex column    | standard compact basis          |
| `from_spinor_column(alg, spinor)`     | complex column -> even MV    | standard compact basis          |
| `to_quaternion_matrix(mv)`            | MV -> quaternion matrix      | explicit quaternion-block basis |
| `to_spinor_quaternion(mv)`            | even MV -> quaternion column | explicit quaternion-block basis |
| `from_spinor_quaternion(alg, spinor)` | quaternion column -> even MV | explicit quaternion-block basis |

`to_spinor_matrix` and `from_spinor_matrix` are compatibility aliases for the
column-named APIs.
