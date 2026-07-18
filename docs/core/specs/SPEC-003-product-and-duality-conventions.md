# SPEC-003: Product and Duality Conventions

**Status:** Implemented

## Intent

Competing geometric-algebra conventions must be available under names that
state their mathematical meaning. A backend optimization must not change any
definition in this specification.

For a detailed derivation and examples, see
[Inner products, contractions, and interior products](../inner-products-contractions-and-interior-products.md).

## Primitive products

### Geometric product

`geometric_product(A, B)` implements the Clifford product for the algebra's
native Gram matrix. `gp` is a same-object compatibility alias. Basis vectors
must satisfy

$$
e_i e_j+e_j e_i=2G_{ij}.
$$

The product is bilinear, associative, and may return several basis-blade
components from one basis-blade pair in a nonorthogonal basis.

### Exterior product

`outer_product(A, B)` implements the metric-independent exterior product. `op`
is a same-object compatibility alias. Repeated selected basis indices give
zero; otherwise the output mask is XOR with the exterior permutation sign.

## Scalar and grade-selected products

For homogeneous grades `r` and `s`:

| Operation | Selected grade | Scalar inputs |
|---|---|---|
| `scalar_product(A, B)` | `0` from `AB` | Pairs scalars; otherwise only scalar output survives |
| `metric_inner_product(A, B)` | Scalar pairing `scalar_product(A, reverse(B))` | Pairs scalar components |
| `left_contraction(A_r, B_s)` | `s-r` when `r <= s` | A left scalar scales `B`; a right scalar survives only for `r=0` |
| `right_contraction(A_r, B_s)` | `r-s` when `r >= s` | Mirror of left contraction |
| `hestenes_inner(A_r, B_s)` | `abs(r-s)` when both grades are nonzero | Kills any pair containing a scalar grade |
| `doran_lasenby_inner(A_r, B_s)` | `abs(r-s)` | Includes scalar grades |

Mixed-grade inputs are expanded bilinearly over every homogeneous grade pair.
The `|` operator maps to Doran–Lasenby inner. `dorst_inner` is a compatibility
name for the same convention.

`metric_inner_product` is the exterior metric pairing. For exterior basis
blades of one grade, its coefficients are the corresponding minors of the
vector Gram matrix. In particular, on vectors it equals `G[i,j]`.

## Commutator family

The only scaled functions have `half` in their names:

| Operation | Definition |
|---|---|
| `commutator(A,B)` | `AB - BA` |
| `lie_bracket(A,B)` | `AB - BA` |
| `half_commutator(A,B)` | `(AB - BA)/2` |
| `anticommutator(A,B)` | `AB + BA` |
| `jordan_product(A,B)` | `AB + BA` |
| `half_anticommutator(A,B)` | `(AB + BA)/2` |

This project convention deliberately differs from literature that defines the
Jordan product with one half. For vectors, `half_anticommutator` is the Gram
pairing while `anticommutator` is twice that pairing.

## Involutions

For a homogeneous grade `k`:

| Operation | Sign |
|---|---|
| `reverse` | `(-1)**(k*(k-1)/2)` |
| `grade_involution` (`involute` alias) | `(-1)**k` |
| `conjugate` | `(-1)**(k*(k+1)/2)` |
| `antireverse` | `(-1)**((n-k)*(n-k-1)/2)` |

Reverse must be an anti-automorphism of the geometric product. Grade
involution must be an automorphism. Clifford conjugation is their composition.

## Complements and duals

`right_complement(A)` equals the metric-independent `complement(A)` and is
defined on basis blades by

$$
A\wedge\operatorname{right\_complement}(A)=I.
$$

`left_complement(A)` equals `uncomplement(A)` and satisfies

$$
\operatorname{left\_complement}(A)\wedge A=I.
$$

The left and right complements are mutual inverses and work for singular
metrics because they depend only on exterior orientation.

`dual(A)` is metric-dependent and uses the inverse pseudoscalar. `undual` is
its inverse. Both require a nondegenerate metric and must fail clearly when the
pseudoscalar is not invertible.

Right and left Hodge duals apply the exterior metric and then the corresponding
complement. Weight duals use the antimetric instead.

## Regressive products

The default regressive product is metric-independent:

$$
A\vee B=\operatorname{uncomplement}
\left(\operatorname{complement}(A)\wedge
\operatorname{complement}(B)\right).
$$

`meet` denotes this operation, `join` denotes the exterior product, and
`antiwedge` is the RGA name for the same complement-based regressive product.

`metric_regressive_product` is a separate operation based on `dual` and
`undual` and therefore requires a nondegenerate metric.

## Metric and antimetric operations

`metric_apply` applies the compound-matrix exterior extension of `G`.
`antimetric_apply` applies its signed complementary-minor counterpart.

`antidot_product(A,B)` returns a grade-`n` antiscalar, not a grade-zero scalar:

$$
(A^T\,\overline{\Lambda G}\,B)I.
$$

Bulk and weight parts are semantic names for metric and antimetric application.

## RGA operations

`geometric_antiproduct` is the De Morgan dual of the geometric product under
left/right complements. `left_interior_product` and
`right_interior_product` compose Hodge duality with the regressive product.

For nonnegative order `k`, `transwedge(A,B,k)` selects output grade
`r+s-2k` for each homogeneous input pair and applies the transwedge reversion
sign. Order zero equals the exterior product. The signed sum of orders
reconstructs the geometric product.

`transwedge_antiproduct` is its De Morgan dual. Negative or nonintegral orders
must be rejected.

## Norm and inverse

`norm2(A)` is `metric_inner_product(A,A)`, equivalently the scalar part of
`A*reverse(A)`. `norm(A)` returns the real number
`numpy.sqrt(abs(float(norm2(A))))`; it does not call the public Study-number
`sqrt`. `unit(A)` divides by that magnitude and rejects a near-zero norm.

`inverse(A)` must return a two-sided inverse or raise. Its current algorithm is
specified architecturally in
[ADR-008](../adrs/008-left-regular-general-inverse.md).

Analytic square roots and exponentials are specified separately in
[SPEC-005](SPEC-005-numeric-functions.md).
