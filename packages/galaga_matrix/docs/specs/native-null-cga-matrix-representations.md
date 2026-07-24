# Specification: Native-Null CGA Matrix Representations

## Status

Proposed.

This document specifies matrix representations for three-dimensional
conformal geometric algebra in its native null basis. It covers:

- a faithful $4\times4$ complex representation of the full algebra;
- its $2\times2$ Vahlen block interpretation over
  $\operatorname{Cl}(3,0)$;
- a faithful $2\times2$ quaternion representation of the even subalgebra;
- conversion back to native Galaga multivector coefficients; and
- the general nondegenerate-Gram machinery needed to support the same design
  beyond the canonical CGA model.

The document is an implementation specification, not a record of an accepted
decision. An ADR should record the final public API and representation
conventions when the implementation is accepted.

## Summary

The native conformal basis is not orthogonal, but it is not degenerate.
For spatial dimension three, Galaga stores

$$
(e_1,e_2,e_3,e_o,e_\infty)
$$

with

$$
e_i\mathbin{\cdot}e_j=\delta_{ij},
\qquad
e_o^2=e_\infty^2=0,
\qquad
e_o\mathbin{\cdot}e_\infty=\kappa\ne0.
$$

Its Gram matrix is

$$
G=
\begin{pmatrix}
I_3&0&0\\
0&0&\kappa\\
0&\kappa&0
\end{pmatrix}.
$$

The null block has determinant $-\kappa^2$, so

$$
\det G=-\kappa^2\ne0.
$$

The metric has inertia $(4,1,0)$. Consequently, the abstract real Clifford
algebra is

$$
\operatorname{Cl}(4,1)\cong M_4(\mathbb C),
$$

and its even subalgebra is

$$
\operatorname{Cl}^{+}(4,1)
\cong \operatorname{Cl}(1,3)
\cong M_2(\mathbb H).
$$

These give two natural, complementary representations:

| Source domain | Matrix form | Real dimensions | Purpose |
|---|---:|---:|---|
| Full $\operatorname{Cl}(4,1)$ | $4\times4$ complex | $32$ | All multivectors and blades |
| Even $\operatorname{Cl}^{+}(4,1)$ | $2\times2$ quaternion | $16$ | Rotors, even versors, and Spin transformations |

The full representation is also naturally a $2\times2$ block matrix whose
entries are $2\times2$ Pauli matrices, hence elements of
$\operatorname{Cl}(3,0)$. This is the extended Vahlen representation. Vahlen
blocks and quaternion blocks must not be conflated:

- Vahlen form represents the **full** 32-real-dimensional algebra as
  $M_2(\operatorname{Cl}(3,0))$;
- quaternion form represents the **even** 16-real-dimensional subalgebra as
  $M_2(\mathbb H)$.

Both may use a $4\times4$ complex NumPy array as backing storage, but they have
different block semantics and generally use different bases.

## Goals

1. Make `mode="compact"` work for the native-null CGA Gram matrix.
2. Preserve the native basis and native exterior-blade coefficients on both
   sides of conversion.
3. Make the complete 32-dimensional algebra round-trip through a faithful
   $4\times4$ complex representation.
4. Add an explicit even-domain quaternion representation for the
   16-dimensional even subalgebra.
5. Expose the $2\times2$ Vahlen block structure without introducing
   object-dtype numeric storage.
6. Derive all generator and blade matrices from the metric and a pinned
   representation convention.
7. Reuse the resulting machinery for arbitrary nondegenerate Gram matrices.
8. Retain left-regular matrices as the universal fallback and as an
   independent validation oracle.

## Non-goals

- Replacing Galaga's native multivector storage with matrices.
- Giving a compact faithful representation to a degenerate algebra such as
  PGA in this phase.
- Defining a new symbolic coefficient algebra.
- Treating every invertible even multivector as a valid conformal versor.
- Encoding the Vahlen-group constraints as a geometry type system in the
  first implementation.
- Replacing the existing CGA model operations with matrix algorithms.
- Claiming that an arbitrary $2\times2$ quaternion matrix is automatically a
  normalized conformal transformation.

## Why native null vectors do not imply degeneracy

A vector may be null even when the bilinear form has no radical. The native
pair $e_o,e_\infty$ is the simplest example:

$$
e_o^2=e_\infty^2=0
$$

but

$$
e_o\mathbin{\cdot}e_\infty=\kappa\ne0.
$$

Neither vector is orthogonal to the whole vector space. The pair spans a
nondegenerate plane of signature $(1,1)$.

This distinction controls dispatch:

- native-null CGA is eligible for a compact representation;
- a metric with a genuine radical still falls back to `left-regular`.

The current compact-mode predicate conflates "not a normalized diagonal
metric" with "not compactly representable". This specification separates
those questions.

## Existing package behavior

At the time of this specification:

- `left-regular` supports every symmetric Gram matrix and preserves native
  coefficients;
- `compact` accepts normalized orthogonal metrics only;
- `quaternion` accepts full algebras already classified as simple
  quaternionic matrix algebras, notably $\operatorname{Cl}(1,3)$;
- `MatrixRepr` always stores a real or complex NumPy matrix;
- `.quat` interprets $2\times2$ complex blocks as quaternions; and
- `from_matrix()` reconstructs coefficients by solving a real linear system
  against the selected blade matrices.

The proposed design keeps those strengths. The missing piece is a correct map
from native exterior blades to a compact representation.

## Conventions

### Clifford relation

Generator matrices must obey

$$
\rho(e_i)\rho(e_j)+\rho(e_j)\rho(e_i)
=2G_{ij}I.
\tag{1}
$$

This convention agrees with Galaga's vector geometric product.

### Standard null-pair normalization

Galaga's standard CGA model uses

$$
\kappa=e_o\mathbin{\cdot}e_\infty=-1.
$$

The construction below supports any nonzero $\kappa$. Examples use
$\kappa=-1$ unless stated otherwise.

### Null-pair gauge

The replacement

$$
e_o\longmapsto\lambda e_o,
\qquad
e_\infty\longmapsto\lambda^{-1}e_\infty
$$

preserves $\kappa$. Matrix representations related by this rescaling are
equivalent, but their entries are not identical.

Stable rendering, examples, and regression tests require one pinned gauge.
Galaga shall use the rational asymmetric gauge defined below. It avoids
$\sqrt2$ factors and makes conformal point matrices especially compact.

## Canonical full-algebra representation

Let

$$
\sigma_1=
\begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad
\sigma_2=
\begin{pmatrix}0&-i\\i&0\end{pmatrix},
\qquad
\sigma_3=
\begin{pmatrix}1&0\\0&-1\end{pmatrix},
$$

and let $I_2$ be the $2\times2$ identity. Define

$$
\rho(e_k)=
\begin{pmatrix}
\sigma_k&0\\
0&-\sigma_k
\end{pmatrix},
\qquad k=1,2,3,
\tag{2}
$$

$$
\rho(e_o)=
\begin{pmatrix}
0&0\\
-I_2&0
\end{pmatrix},
\tag{3}
$$

and

$$
\rho(e_\infty)=
\begin{pmatrix}
0&-2\kappa I_2\\
0&0
\end{pmatrix}.
\tag{4}
$$

For the standard normalization $\kappa=-1$,

$$
\rho(e_\infty)=
\begin{pmatrix}
0&2I_2\\
0&0
\end{pmatrix}.
$$

These matrices satisfy

$$
\rho(e_o)^2=\rho(e_\infty)^2=0,
$$

$$
\rho(e_o)\rho(e_\infty)
+\rho(e_\infty)\rho(e_o)
=2\kappa I_4,
$$

$$
\rho(e_k)^2=I_4,
$$

and all other distinct generator anticommutators vanish. Thus they satisfy
equation (1) directly in the native null basis.

### Why this is a faithful representation

There are 32 real exterior-basis coefficients in
$\operatorname{Cl}(4,1)$. A $4\times4$ complex matrix also contains 32 real
degrees of freedom. The 32 exterior-blade matrices induced by equations
(2)--(4) have real rank 32. Therefore the map is injective and surjective as a
map of real vector spaces, as well as preserving the geometric product.

The rank statement is an acceptance test, not merely a dimension-count
assumption.

### Point and round-point matrices

Write a Euclidean vector as

$$
x=x_1e_1+x_2e_2+x_3e_3
$$

and its Pauli matrix as

$$
X=x_1\sigma_1+x_2\sigma_2+x_3\sigma_3.
$$

Galaga's conformal embedding with radius-squared parameter $r^2$ is

$$
P(x,r^2)
=e_o+x-\frac{x^2+r^2}{2\kappa}e_\infty.
\tag{5}
$$

The canonical matrix is

$$
\rho(P(x,r^2))=
\begin{pmatrix}
X&(x^2+r^2)I_2\\
-I_2&-X
\end{pmatrix}.
\tag{6}
$$

The $\kappa$ factors cancel. This is one reason to prefer the pinned rational
gauge.

For a conformal point, $r^2=0$, and

$$
\rho(P(x,0))^2=0.
$$

For a round point with signed squared radius $r^2$,

$$
\rho(P(x,r^2))^2=-r^2I_4.
\tag{7}
$$

These identities provide readable examples and strong tests.

### Proposed Python example

```python
from galaga import Algebra, ConformalModel, p_cga
from galaga_matrix import from_matrix, to_matrix

algebra = Algebra(config=p_cga(spatial_dim=3))
cga = ConformalModel(algebra)

point = cga.up((1.0, 2.0, 3.0))
matrix = to_matrix(point, mode="compact")

assert matrix.shape == (4, 4)
assert matrix.basis == "cga-vahlen"
assert from_matrix(matrix).almost_equal(point)
```

After this feature is established, automatic mode selection shall also choose
this compact representation:

```python
matrix = to_matrix(point)
assert matrix.mode == "compact"
assert matrix.shape == (4, 4)
```

## The exterior-blade trap

Native basis coefficients are coefficients of **exterior** blades. For an
orthogonal basis,

$$
f_{i_1}\wedge\cdots\wedge f_{i_k}
=f_{i_1}\cdots f_{i_k},
$$

so an implementation can build a blade matrix by multiplying distinct gamma
matrices in order.

That shortcut is wrong in a nonorthogonal basis. For example,

$$
e_o e_\infty
=e_o\mathbin{\cdot}e_\infty+e_o\wedge e_\infty
=\kappa+e_o\wedge e_\infty.
$$

Therefore

$$
\rho(e_o\wedge e_\infty)
=\frac{
  \rho(e_o)\rho(e_\infty)
  -\rho(e_\infty)\rho(e_o)
}{2},
\tag{8}
$$

not merely $\rho(e_o)\rho(e_\infty)$.

For $\kappa=-1$,

$$
\rho(e_o\wedge e_\infty)=
\begin{pmatrix}
I_2&0\\
0&-I_2
\end{pmatrix}.
\tag{9}
$$

This distinction is the principal correctness requirement for native-Gram
compact conversion. A solution that validates only vector anticommutators can
still corrupt every higher-grade native coefficient.

## Vahlen and Möbius block form

Equations (2)--(4) naturally partition the $4\times4$ complex matrix into
$2\times2$ blocks:

$$
\rho(A)=
\begin{pmatrix}
a&b\\
c&d
\end{pmatrix},
\qquad
a,b,c,d\in\operatorname{Cl}(3,0).
\tag{10}
$$

Each $\operatorname{Cl}(3,0)$ entry is itself represented by a $2\times2$
complex Pauli matrix. Thus

$$
\operatorname{Cl}(4,1)
\cong M_2(\operatorname{Cl}(3,0))
\cong M_4(\mathbb C).
$$

For arbitrary multivectors, equation (10) is an **extended Vahlen matrix**.
When the source is a suitable normalized versor, its blocks obey the Vahlen
conditions and represent a Möbius transformation.

### A point as a rank-one block product

For $r^2=0$, equation (6) factors as

$$
\rho(P(x))=
\begin{pmatrix}X\\-I_2\end{pmatrix}
\begin{pmatrix}I_2&X\end{pmatrix}.
\tag{11}
$$

Let a conformal versor have Vahlen matrix

$$
V=
\begin{pmatrix}
a&b\\
c&d
\end{pmatrix}.
$$

Acting on the first factor in equation (11) gives

$$
V
\begin{pmatrix}X\\-I_2\end{pmatrix}=
\begin{pmatrix}
aX-b\\
cX-d
\end{pmatrix}.
$$

Whenever $d-cX$ is invertible, the induced fractional linear action in this
specification's sign convention is

$$
X'
=(aX-b)(d-cX)^{-1}.
\tag{12}
$$

Equation (12) must be treated as convention-bound. Galaga's authoritative
operation remains the Clifford sandwich

$$
P'\;=\;VP\widetilde V.
$$

Tests shall derive the fractional action from, and compare it with, that
sandwich. This avoids importing sign or involution conventions from a
different Vahlen normalization.

### Translation

For translation vector $t$ with Pauli matrix $T$, Galaga's standard
translator is

$$
\mathcal T=1-\frac12t e_\infty.
$$

Its canonical Vahlen matrix is

$$
\rho(\mathcal T)=
\begin{pmatrix}
I_2&-T\\
0&I_2
\end{pmatrix}.
\tag{13}
$$

Equation (12) gives

$$
X'=X+T.
$$

This triangular form is both a useful display and a regression oracle.

### Dilation

For

$$
D_\alpha=
\exp\left(\frac{\alpha}{2}e_o\wedge e_\infty\right)
$$

in the standard $\kappa=-1$ convention,

$$
\rho(D_\alpha)=
\begin{pmatrix}
e^{\alpha/2}I_2&0\\
0&e^{-\alpha/2}I_2
\end{pmatrix}.
\tag{14}
$$

Equation (12) gives

$$
X'=e^\alpha X.
$$

The exact sign of $\alpha$ follows the selected CGA dilation helper. The
implementation test shall compare with `ConformalModel` rather than rely only
on equation (14).

### Transversion

A lower-triangular Vahlen matrix

$$
\begin{pmatrix}
I_2&0\\
C&I_2
\end{pmatrix}
$$

acts as

$$
X'=X(I_2-CX)^{-1}.
\tag{15}
$$

This is the block-matrix counterpart of a conformal transversion. As with
dilation, Galaga shall derive the sign and normalization of $C$ from the
existing CGA versor and sandwich definitions.

### Proposed Vahlen view

Vahlen form should be a view over compact numeric storage, not a second
numeric representation mode:

```python
translator_matrix = to_matrix(translator, mode="compact")
vahlen = translator_matrix.vahlen

vahlen.shape          # (2, 2) block entries
vahlen.blocks[0][1]   # raw 2×2 complex Pauli block
vahlen.entries[0][1]  # equivalent Cl(3,0) multivector
vahlen.latex()        # 2×2 matrix rendered with GA-valued entries
```

The proposed `VahlenRepr` view shall:

- retain the parent `MatrixRepr` and its immutable provenance;
- expose raw Pauli blocks without copying where NumPy permits;
- expose block entries as multivectors in a canonical
  $\operatorname{Cl}(3,0)$ algebra;
- render a $2\times2$ matrix of GA entries;
- validate `basis == "cga-vahlen"` and a $4\times4$ backing shape; and
- avoid object-dtype arrays.

The first numeric delivery does not depend on this view. It is a separate work
unit with separate display and round-trip tests.

## Quaternion representation of the even algebra

The full algebra is complex matrix type, not quaternion matrix type. Its even
subalgebra is quaternionic:

$$
\operatorname{Cl}^{+}(4,1)
\cong\operatorname{Cl}(1,3)
\cong M_2(\mathbb H).
\tag{16}
$$

This is the natural compact form for conformal rotors and other even versors.
It must be explicitly scoped to even multivectors. Odd Pin versors, including
single-vector reflections or inversions, remain representable in the full
complex/Vahlen form but do not belong to this quaternion domain.

### Concrete even generators

For the standard $\kappa=-1$ normalization, define an orthonormal basis for
the null plane:

$$
u=\frac{e_o-e_\infty}{\sqrt2},
\qquad
v=\frac{e_o+e_\infty}{\sqrt2},
$$

so that

$$
u^2=+1,
\qquad
v^2=-1,
\qquad
u\mathbin{\cdot}v=0.
$$

The even elements

$$
h_0=uv=e_o\wedge e_\infty,
\qquad
h_k=ue_k,\quad k=1,2,3,
\tag{17}
$$

satisfy the $\operatorname{Cl}(1,3)$ relations:

$$
h_0^2=+1,
\qquad
h_k^2=-1,
$$

with vanishing anticommutators for distinct generators.

Map them to the quaternion matrices already used by `galaga_matrix` for
$\operatorname{Cl}(1,3)$:

$$
\rho_{\mathbb H}(h_0)=
\begin{pmatrix}
1&0\\
0&-1
\end{pmatrix},
\tag{18}
$$

$$
\rho_{\mathbb H}(h_1)=
\begin{pmatrix}
0&i\\
i&0
\end{pmatrix},
\quad
\rho_{\mathbb H}(h_2)=
\begin{pmatrix}
0&j\\
j&0
\end{pmatrix},
\quad
\rho_{\mathbb H}(h_3)=
\begin{pmatrix}
0&k\\
k&0
\end{pmatrix}.
\tag{19}
$$

Equations (17)--(19) provide a concrete algebra isomorphism, not merely a
dimension argument.

For a nonstandard nonzero $\kappa$, the implementation shall derive $u$ and
$v$ from the metric factorization. It must not assume the standard
$1/\sqrt2$ coefficients.

### Quaternion forms of common even versors

Let

$$
Q=t_1i+t_2j+t_3k
$$

be the pure quaternion corresponding to the Euclidean translation vector
$t$. Equations (17)--(19) give

$$
\rho_{\mathbb H}\left(1-\frac12t e_\infty\right)=
\begin{pmatrix}
1&-Q/\sqrt2\\
0&1
\end{pmatrix}.
\tag{Q1}
$$

The $\sqrt2$ occurs because the quaternion map uses the normalized
orthogonal pair $u,v$, while the Vahlen form deliberately uses the asymmetric
native-null gauge. It is not an extra translation factor.

For a spatial rotation in the $e_1e_2$ plane,

$$
\rho_{\mathbb H}(e_1e_2)=
\begin{pmatrix}
-k&0\\
0&-k
\end{pmatrix}.
$$

Therefore

$$
\rho_{\mathbb H}
\left(
  \exp\left(-\frac{\theta}{2}e_1e_2\right)
\right)=
\begin{pmatrix}
\exp(k\theta/2)&0\\
0&\exp(k\theta/2)
\end{pmatrix}.
\tag{Q2}
$$

These exact forms are useful convention tests. A conformal point is an odd
multivector and intentionally has no matrix in the even quaternion domain.

### Complex backing for quaternion matrices

Keep the package's existing quaternion embedding:

$$
a+bi+cj+dk
\longleftrightarrow
\begin{pmatrix}
a+bi&c+di\\
-c+di&a-bi
\end{pmatrix}.
\tag{20}
$$

A $2\times2$ quaternion matrix is therefore stored as a $4\times4$ complex
NumPy array. `MatrixRepr.quat` recovers the logical quaternion grid.

This gives:

- one numeric storage and arithmetic path;
- no object-dtype matrix multiplication;
- compatibility with NumPy linear algebra; and
- human-readable quaternion rendering when requested.

### Proposed API

The existing quaternion mode represents the full source algebra when that
algebra is itself quaternionic. Native CGA requires a distinct source-domain
declaration.

Add a `domain` parameter and matching `MatrixRepr` metadata:

```python
matrix = to_matrix(versor, mode="quaternion", domain="even")

assert matrix.mode == "quaternion"
assert matrix.domain == "even"
assert matrix.basis == "cga-even-cl13"
assert matrix.mat.shape == (4, 4)  # complex backing
assert len(matrix.quat) == 2       # logical 2×2 quaternion matrix

recovered = from_matrix(matrix)
assert recovered.almost_equal(versor)
```

Defaults preserve current behavior:

```python
to_matrix(x, mode="quaternion")
# Equivalent to:
to_matrix(x, mode="quaternion", domain="full")
```

Raw matrix inversion must state the missing provenance:

```python
recovered = from_matrix(
    algebra,
    raw_complex_matrix,
    mode="quaternion",
    domain="even",
    basis="cga-even-cl13",
)
```

The exact raw-array API may use a representation descriptor rather than
separate keywords if that becomes the accepted package-wide design. The
essential rule is that `mode="quaternion"` alone must not ambiguously mean
both the full algebra and its even subalgebra.

### Domain rules

- `domain="even"` rejects any odd-grade coefficient above the numeric
  tolerance.
- Reconstruction solves only for the 16 even exterior-basis coefficients.
- Addition, multiplication, inversion, and integer powers preserve the
  `domain="even"` metadata when their operands are compatible.
- Combining matrices from different representation bases or source domains
  must raise or require an explicit conversion.
- A raw $2\times2$ quaternion matrix is not accepted as a conformal versor
  merely because it lies in $M_2(\mathbb H)$.
- Versor normalization and Vahlen-group constraints belong to validation
  helpers or the CGA model, not to `from_matrix()`.

### Agreement with the full complex representation

The quaternion representation and the restriction of the full complex
representation to even elements are equivalent, but they need not be
entry-for-entry identical. There is a fixed invertible complex matrix $S_H$
such that

$$
\rho_{\mathbb C}(R)
=S_H\,\iota\!\left(\rho_{\mathbb H}(R)\right)S_H^{-1}
\tag{21}
$$

for every even multivector $R$, where $\iota$ is equation (20), once both
basis conventions are pinned.

The implementation shall compute and store one validated $S_H$ for the
canonical model. Equation (21) is an acceptance test across all 16 even basis
blades and randomized even multivectors.

### Proposed quaternion example

```python
from galaga import Algebra, ConformalModel, exp, p_cga
from galaga_matrix import from_matrix, to_matrix

algebra = Algebra(config=p_cga(spatial_dim=3))
cga = ConformalModel(algebra)
e1, e2, e3, eo, einf = algebra.basis_vectors()

rotation = exp(-0.35 * (e1 ^ e2) / 2)
translation = 1 - 0.5 * e1 * einf
versor = translation * rotation

matrix = to_matrix(versor, mode="quaternion", domain="even")

assert matrix.quat[0][0] is not None
assert from_matrix(matrix).almost_equal(versor)
```

The corresponding full compact matrix remains available:

```python
complex_matrix = to_matrix(versor, mode="compact")
```

These are two representations of the same even element, optimized for
different interpretations.

## General construction for a nondegenerate Gram matrix

The canonical CGA matrices are worth pinning because they give recognizable
Vahlen form. The implementation should nevertheless solve the underlying
problem generally.

Let $G$ be a real symmetric nondegenerate Gram matrix. Compute a congruence

$$
G=S\eta S^{\mathsf T},
\tag{22}
$$

where

$$
\eta=\operatorname{diag}(
\underbrace{1,\ldots,1}_{p},
\underbrace{-1,\ldots,-1}_{q}
).
$$

If $(f_1,\ldots,f_n)$ is the normalized orthogonal basis, the native basis is

$$
e_i=\sum_aS_{ia}f_a.
\tag{23}
$$

Let $\gamma_a=\rho(f_a)$ be the existing orthogonal compact gamma matrices.
Then the native vector matrices are

$$
\Gamma_i=\sum_aS_{ia}\gamma_a.
\tag{24}
$$

Equations (22)--(24) imply

$$
\Gamma_i\Gamma_j+\Gamma_j\Gamma_i=2G_{ij}I.
$$

### Lifting the basis change to exterior blades

Equation (24) is enough for vectors but not for native exterior-basis
coefficients. The basis change must be lifted through the outermorphism.

For ordered grade-$k$ index sets $I$ and $A$,

$$
e_I
=\sum_{\lvert A\rvert=k}
\det(S_{I,A})f_A.
\tag{25}
$$

Because the $f_a$ are orthogonal,

$$
\rho(f_A)=\gamma_{a_1}\cdots\gamma_{a_k}.
$$

Therefore

$$
\rho(e_I)
=\sum_{\lvert A\rvert=k}
\det(S_{I,A})\rho(f_A).
\tag{26}
$$

Equation (26), not an ordered product of the $\Gamma_i$, is the blade-matrix
construction.

This mirrors Galaga core's existing use of compound matrices and minors for
the exterior extension of the metric. The same mathematical idea should be
reused here.

### Factorization policy

For a generic floating-point Gram matrix:

1. Verify exact symmetry at construction time, as Galaga already does.
2. Determine inertia using the core's scale-aware policy.
3. Reject a genuine radical for compact mode.
4. Compute a deterministic symmetric eigendecomposition or an equivalent
   stable congruence.
5. Order positive directions first and negative directions second.
6. Normalize eigenvector signs deterministically.
7. Validate equation (22) with a scale-aware residual.
8. Build and validate the generator anticommutators.
9. Build exterior-blade matrices through equation (26).
10. Rank-check the resulting real representation before advertising inverse
    conversion.

Known semantic models may provide exact analytic factorizations. The
native-null CGA model shall use its analytic Witt factorization and pinned
matrix convention rather than platform-dependent eigenvectors.

### Near-degenerate metrics

A matrix can be mathematically nondegenerate but numerically too ill
conditioned for a reliable compact basis transform. In that case:

- explicit `mode="compact"` raises a diagnostic error containing the
  factorization and residual context;
- automatic mode selection falls back to `left-regular`; and
- Galaga never silently changes the stored Gram matrix or clips an
  eigenvalue.

## Representation metadata

The matrix wrapper must carry enough information to invert and interpret the
map without guessing.

Proposed metadata:

| Field | Full native CGA | Even quaternion CGA |
|---|---|---|
| `mode` | `"compact"` | `"quaternion"` |
| `domain` | `"full"` | `"even"` |
| `basis` | `"cga-vahlen"` | `"cga-even-cl13"` |
| `algebra` | original algebra | original algebra |
| `kind` | existing matrix semantic | existing matrix semantic |

`domain` describes the source coefficient space. It is independent of
`MatrixRepr.kind`, which continues to distinguish operators, kets, and bras.

Basis names must be centralized constants or typed descriptors, not repeated
string literals across dispatch, inversion, rendering, and tests.

The longer-term form may be:

```python
RepresentationSpec(
    mode="quaternion",
    domain="even",
    basis="cga-even-cl13",
)
```

The first implementation may keep keyword arguments if adding a descriptor
would make the change unnecessarily broad.

## Internal architecture

### `MetricCongruence`

An internal immutable value should contain:

- native Gram matrix identity or cache key;
- inertia $(p,q,r)$;
- $S$ and $\eta$ from equation (22);
- inverse transform where numerically safe;
- factorization residual and condition estimate; and
- a convention identifier.

The canonical CGA model uses an analytic `MetricCongruence`.

### `MatrixRepresentationPlan`

An internal plan should contain:

- source algebra;
- mode, domain, and basis;
- generator matrices;
- exterior-blade matrices;
- the native coefficient indices included in the domain;
- real system matrix and rank for reconstruction;
- tolerance policy; and
- optional block-view metadata.

Both conversion directions consume the same plan. No inverse path should
reconstruct a basis independently.

### Cache

Representation plans depend only on:

- the immutable algebra definition;
- representation mode;
- source domain;
- representation basis convention; and
- numeric dtype/tolerance policy.

They shall be cached. Multivector values and symbolic presentation must never
enter the cache key.

The cache must not retain mutable presentation state or make context-local
rendering global.

### Provenance

The existing expression nodes should record the representation mode, domain,
and basis. Rendering may use

$$
\rho_{\mathbb C}(A),
\qquad
\rho_V(A),
\qquad
\rho_{\mathbb H}^{+}(R)
$$

according to presentation policy, but provenance must retain a stable
machine-readable representation descriptor.

## Work units and gates

### Work unit 1: Representation descriptor and cache

Implement the internal plan, domain metadata, and cache without changing the
set of supported metrics.

Gate:

- existing compact, Pauli, Dirac, quaternion, and left-regular tests pass;
- current public calls preserve their behavior; and
- repeated conversions reuse the same immutable plan.

### Work unit 2: General native exterior lift

Implement equations (22)--(26) for nondegenerate Gram matrices.

Gate:

- vector anticommutators reproduce $2G$;
- every exterior-blade matrix agrees with an antisymmetrization oracle for
  small dimensions;
- native coefficients round-trip for injective representations; and
- oblique-basis results intertwine with an independently transformed
  orthogonal basis.

### Work unit 3: Canonical native-null CGA specialization

Add equations (2)--(4), exact basis metadata, and automatic compact dispatch
for the standard three-dimensional conformal model.

Gate:

- all 32 blade matrices have real rank 32;
- point and round-point matrices satisfy equations (6) and (7);
- $e_o\wedge e_\infty$ satisfies equations (8) and (9);
- random products preserve multiplication;
- all native coefficients round-trip; and
- automatic mode selects `compact`.

### Work unit 4: Even quaternion CGA

Implement equations (16)--(21), even-domain validation, and inverse
conversion over the 16 even coefficients.

Gate:

- the four generators satisfy the $\operatorname{Cl}(1,3)$ relations;
- the 16 even basis images have real rank 16;
- all 16 even basis blades round-trip;
- randomized even multivectors round-trip;
- odd and mixed-grade values are rejected;
- quaternion and full-complex images satisfy equation (21); and
- matrix products agree with even multivector geometric products.

### Work unit 5: Vahlen view

Add the `VahlenRepr` block view and GA-valued rendering.

Gate:

- block extraction is exact and does not use object-dtype backing;
- every block round-trips through the canonical Pauli
  $\operatorname{Cl}(3,0)$ map;
- point, translation, dilation, and transversion render as readable
  $2\times2$ block matrices; and
- view operations retain the parent representation provenance.

### Work unit 6: Geometry-level examples

Add executable Marimo examples under `examples/matrix/`:

- `native_cga_compact_matrices.py`;
- `cga_vahlen_mobius.py`; and
- `cga_even_quaternion_matrices.py`.

Gate:

- each notebook is in the example ledger;
- each compiles, passes dependency checks, and executes headlessly;
- matrix sandwiches agree with `ConformalModel` coordinates; and
- the prose clearly distinguishes Vahlen and quaternion blocks.

### Work unit 7: General nondegenerate-Gram promotion

After CGA and oblique test fixtures establish the machinery, allow automatic
compact selection for other well-conditioned nondegenerate Gram matrices
whose orthogonal compact representation is injective.

Gate:

- every supported inertia through the agreed dimension limit passes
  anticommutator, homomorphism, rank, and round-trip tests;
- double-algebra behavior remains explicit;
- near-degenerate metrics follow the fallback policy; and
- compact output is benchmarked against left-regular output.

## Test specification

### Exact canonical tests

For standard 3D CGA, assert the exact matrices for:

- $e_1,e_2,e_3$;
- $e_o$;
- $e_\infty$;
- $e_o\wedge e_\infty$;
- $P(0)$;
- $P(1,2,3)$;
- a round point with a nonzero signed radius; and
- the translator in equation (13).

These tests pin the public representation convention.

### Algebra-law tests

For all basis vectors $e_i,e_j$:

$$
\rho(e_i)\rho(e_j)+\rho(e_j)\rho(e_i)
=2G_{ij}I.
$$

For representative and randomized multivectors $A,B$:

$$
\rho(A+B)=\rho(A)+\rho(B),
$$

$$
\rho(AB)=\rho(A)\rho(B),
$$

$$
\rho(1)=I.
$$

### Exterior-basis tests

For every native blade through dimension five:

1. compute its matrix with the minor/outermorphism method;
2. compute an independent fully antisymmetrized gamma-product oracle;
3. compare the two;
4. reconstruct the native multivector; and
5. verify the exact native blade mask and coefficient.

The $e_o\wedge e_\infty$ test is mandatory and should be named so the original
failure mode is obvious.

### Cross-basis tests

Construct the same algebra in:

- native null coordinates;
- an orthonormal $\operatorname{Cl}(4,1)$ basis; and
- at least one rescaled or oblique basis.

For the documented outermorphism $F$ and matrix intertwiner $S_F$, test

$$
\rho_{\text{native}}(A)
=S_F\rho_{\text{orthogonal}}(F(A))S_F^{-1}.
$$

The multivector basis transform and matrix similarity transform must be
independently implemented in the test oracle.

### Quaternion tests

- Test exact images of $h_0,h_1,h_2,h_3$.
- Test the quaternion block constraints after complex embedding.
- Test round-trip of every even native exterior blade.
- Test representative rotations, translations, dilations, and composed
  motors/versors.
- Test rejection of $e_1$, $P(x)$, and any mixed even/odd value.
- Test equation (21) for all even basis blades.
- Test `.quat` rendering and NumPy-backed arithmetic.

### Möbius tests

For points away from singular denominators:

1. transform by the CGA sandwich;
2. transform the Pauli coordinate with equation (12);
3. normalize both conformal results;
4. compare Euclidean coordinates.

Cover:

- translation;
- rotation;
- dilation;
- transversion;
- inversion where represented by the chosen group component; and
- one composed general conformal transformation.

### Failure tests

- Degenerate Gram metric with explicit compact mode.
- Near-degenerate factorization outside tolerance.
- Non-injective compact representation.
- Raw inverse without sufficient mode/domain/basis information.
- Matrix outside the image of the selected representation.
- Quaternion-even conversion with odd content.
- Vahlen view on a non-CGA basis or incorrectly shaped matrix.

## Numerical policy

### Tolerances

All validation must be scale-aware. The representation plan should derive
tolerances from:

- matrix dimension;
- dtype precision;
- $\lVert G\rVert$;
- factorization condition estimate; and
- representation-basis norm.

The existing fixed inverse residual may remain as a compatibility floor, but
new general-Gram checks must not assume all metrics are normalized to unit
scale.

### Determinism

Canonical CGA matrices are exact up to floating representation and are pinned
by equations (2)--(4).

Generic Gram factorizations are not unique. Their tests should pin:

- algebra laws;
- exterior-basis preservation;
- round-trip behavior; and
- deterministic factorization conventions within one implementation.

They should not treat arbitrary compact matrix entries as a mathematical
cross-platform standard.

### Dtype

The first implementation uses `complex128`, matching current compact and
quaternion storage. Supporting `float32`, `complex64`, arbitrary precision,
or symbolic matrix entries is future work.

## Performance expectations

For 3D CGA:

| Representation | Backing shape | Backing scalar count |
|---|---:|---:|
| Left regular | $32\times32$ real | 1024 real |
| Full compact | $4\times4$ complex | 32 real equivalents |
| Even quaternion | $4\times4$ complex backing | 32 real stored, 16 constrained |

The compact full representation stores exactly the algebra's 32 real degrees
of freedom. The quaternion backing contains redundant complex coordinates
relative to its logical $2\times2$ quaternion form, but it reuses fast,
well-tested NumPy operations.

Benchmarks shall measure:

- cold and cached conversion;
- geometric-product-equivalent matrix multiplication;
- inverse conversion;
- repeated versor composition; and
- point transformation by matrix sandwich.

Performance is not an excuse to bypass the exterior-basis mapping.

## Documentation requirements

The implementation must update:

- `packages/galaga_matrix/README.md`;
- `packages/galaga_matrix/docs/edge-cases.md`;
- `packages/galaga_matrix/docs/spinor-conversions.md`;
- the package ADR index;
- the matrix example index; and
- the Galaga CGA documentation where matrix representations are mentioned.

The documentation must state clearly:

1. native-null CGA is nondegenerate;
2. full CGA is represented by $4\times4$ complex matrices;
3. its Vahlen blocks are $\operatorname{Cl}(3,0)$ entries;
4. only the even CGA subalgebra has the $2\times2$ quaternion
   representation;
5. both logical forms may have $4\times4$ complex backing; and
6. a matrix representation is not a replacement for geometric type or
   versor-validity checks.

## Acceptance summary

The feature is complete when all of the following are true:

- native 3D CGA defaults to a faithful $4\times4$ complex compact matrix;
- every one of its 32 native exterior blades round-trips;
- native nonorthogonality is handled through the exterior outermorphism;
- the even algebra has an explicit, faithful $2\times2$ quaternion form;
- complex and quaternion representations are proven equivalent on the even
  domain;
- Vahlen blocks are inspectable and renderable as
  $\operatorname{Cl}(3,0)$ entries;
- Möbius block actions agree with CGA sandwiches;
- degenerate metrics retain the left-regular fallback;
- representation construction is cached; and
- examples and documentation explain the mathematical distinctions.

## References

- Leo Dorst,
  [Conformal Geometric Algebra by Extended Vahlen Matrices](https://www.researchgate.net/publication/254915544_Conformal_geometric_algebra_by_extended_Vahlen_matrices).
- Francis E. Burstall,
  [A Clifford Algebra Model: Vahlen Matrices](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/6A7133618CB9414E1B195018A06A5C8E/9780511546693c7_p301-333_CBO.pdf/a-clifford-algebra-model-vahlen-matrices.pdf).
- Justin McInroy,
  [Vahlen Groups Defined over Commutative Rings](https://link.springer.com/article/10.1007/s00209-016-1678-x).
- [Galaga native Gram-matrix proposal](../../../../docs/proposals/native-gram-matrix-algebra.md).
- [Galaga CGA architecture](../../../../docs/cga/README.md).
- [Galaga null-pair scaling](../../../../docs/core/cga-null-pair-scaling.md).
- [Spectral-sandwich matrix representations](../spectral-sandwich-representations.md).
- [Quaternion storage specification](quaternion-unified-storage.md).
