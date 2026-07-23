# Rigid Geometric Algebra Convention Layer

Galaga exposes Eric Lengyel's Rigid Geometric Algebra (RGA) operations as a
parallel convention layer. Existing geometric-algebra functions and Python
operators keep their established meanings.

## Constructing the RGA Basis

RGA orders its vector basis as e1,e2,e3,e4 with e4 null. The preset binds
that metric to Eric's blade orientation, display order, notation, and semantic
model roles:

```python
from galaga import Algebra, p_rga
from galaga.rga import RigidModel

alg = Algebra(config=p_rga())
rga = RigidModel(alg, expr=True)
e1, e2, e3 = rga.euclidean_basis_vectors()
e4 = rga.projective
```

The displayed basis order is:

```text
1
e1, e2, e3, e4
e23, e31, e12, e41, e42, e43
e423, e431, e412, e321
𝟙
```

The nonascending subscripts are algebraic factorizations, not cosmetic aliases:
for example, `e31 == e3 ^ e1 == -(e1 ^ e3)`.

The Galaga 2 facade expresses the same fact with immutable signed references:

```python
from galaga import Algebra, p_rga

rga = Algebra(config=p_rga())
assert rga.blade("e31").coefficient(0b0101) == -1
assert rga.blade("e13").coefficient(0b0101) == 1
```

The integer mask remains the native ascending exterior basis. The convention
changes lookup and future rendering, not the Gram matrix or storage basis.

The Lengyel preset emits KaTeX-compatible LaTeX without `\unicode{...}`
extensions. In particular, the Unicode antiscalar `𝟙` renders as `\text{𝟙}`.
Its compact notation also distinguishes the position of related operations:
right Hodge and weight duals render as `A^★` and `A^☆`, left duals as `A_★`
and `A_☆`, and the bulk and weight projections as `A_●` and `A_○` in Unicode.
LaTeX uses the corresponding `\text{★}`, `\text{☆}`, `\text{●}`, and
`\text{○}` scripts. Both `complement(a)` and `right_complement(a)` use the
RGA overline, while `left_complement(a)` uses the underline; `antiwedge(a, b)`
uses the same `\vee` meet symbol as `regressive_product(a, b)`.

These are executable presentation contracts, not documentation-only examples.
`tests/rendering/test_rga_latex_contract.py` checks every Lengyel operation in
the supported expression channels, all sixteen blade labels, signed native
orientation, and representative compound expressions from the RGA demo and
numeric source tables.

## Operation Correspondence

| RGA concept | Galaga function | Result |
|---|---|---|
| Dot product | `metric_inner_product(a, b)` | Scalar |
| Antidot product | `antidot_product(a, b)` | Antiscalar |
| Right/left complement | `right_complement(a)`, `left_complement(a)` | Complementary grade |
| Metric/antimetric application | `metric_apply(a)`, `antimetric_apply(a)` | Same grade |
| Bulk/weight part | `bulk_part(a)`, `weight_part(a)` | Same grade |
| Right/left bulk dual | `right_hodge_dual(a)`, `left_hodge_dual(a)` | Complementary grade |
| Right/left weight dual | `right_weight_dual(a)`, `left_weight_dual(a)` | Complementary grade |
| Antiwedge | `antiwedge(a, b)` | Regressive grade |
| Geometric antiproduct | `geometric_antiproduct(a, b)` | Mixed grade in general |
| Reverse/antireverse | `reverse(a)`, `antireverse(a)` | Same grade |
| RGA interior products | `left_interior_product(a, b)`, `right_interior_product(a, b)` | Grade difference |
| Order-k transwedge | `transwedge(a, b, k)` | `gr(a) + gr(b) - 2k` |
| Order-k transwedge antiproduct | `transwedge_antiproduct(a, b, k)` | `gr(a) + gr(b) - n + 2k` |

For a vector `a`, the operand order in the two geometric-product
decompositions is significant:

```text
gp(a, B) = op(a, B) + right_interior_product(B, a)
gp(B, a) = op(B, a) + left_interior_product(a, B)
```

The metric pairing extends a diagonal vector metric to every basis blade:

```text
G[S,S] = product(signature[i] for i in S)
```

The antimetric uses absent dimensions:

```text
𝔾[S,S] = product(signature[i] for i not in S)
G @ 𝔾 = det(metric) * identity
```

The antidot product is antiscalar-valued:

```text
antidot_product(a, b) = (a.data @ 𝔾 @ b.data) * 𝟙
```

This agrees with its De Morgan definition:

```text
antidot_product(a, b)
    == right_complement(
           metric_inner_product(left_complement(a), left_complement(b))
       )
```

The bulk and weight duals also satisfy the source identities

```text
right_hodge_dual(a) = gp(reverse(a), antiscalar)
right_weight_dual(a) = geometric_antiproduct(antireverse(a), scalar_identity)
```

The first identity continues to hold in PGA even though Galaga's existing
inverse-pseudoscalar `dual()` is undefined there.

## Similar Names with Different Semantics

- `dual()` remains Galaga's inverse-pseudoscalar dual and raises for degenerate
  metrics. RGA's metric/bulk dual is `right_hodge_dual()` or
  `left_hodge_dual()`.
- `scalar_product(a, b)` remains the scalar part of `gp(a, b)`. RGA's symmetric
  exterior-algebra pairing is `metric_inner_product(a, b)`.
- `left_contraction()` and `right_contraction()` remain grade selections from
  the geometric product. RGA interior products are built from Hodge duals and
  antiwedge.
- `|` remains the Doran-Lasenby inner product.

## Validated Rigid Model

`galaga.rga.RigidModel` owns only operations whose meaning depends on the
point-based RGA model. Construction requires `Algebra(config=p_rga())` and
validates the declared Euclidean and projective roles against the actual Gram
matrix. A bare algebra with the same signature is deliberately insufficient:
the metric alone does not say whether vectors represent points or planes.

```python
from galaga import Algebra, p_rga
from galaga.rga import RigidModel

algebra = Algebra(config=p_rga())
rga = RigidModel(algebra, expr=True)

p = rga.point((3, 4, 0)).named("P")
q = rga.point((1, 0, 0)).named("Q")
line = p ^ q

assert tuple(rga.coordinates(p)) == (3, 4, 0)
assert float(rga.bulk_norm(p)) == 5
```

The model methods preserve Eric's paired scalar/antiscalar codomains:

| Operation | Definition or result |
|---|---|
| `attitude(x)` / `att(x)` | $x\vee\overline{e_4}$ |
| `bulk_norm(x)` | $\sqrt{x\mathbin{\bullet}x}$, scalar-valued |
| `weight_norm(x)` | $\sqrt{x\mathbin{\circ}x}$, antiscalar-valued |
| `geometric_norm(x)` | bulk norm plus weight norm |
| `unitize(x)` | divide by the nonzero weight magnitude |
| `bulk_contraction(a, b)` | $a\vee b^\star$ |
| `weight_contraction(a, b)` | $a\vee b^\mathord{☆}$ |
| `bulk_expansion(a, b)` | $a\wedge b^\star$ |
| `weight_expansion(a, b)` | $a\wedge b^\mathord{☆}$ |
| `homogeneous_distance(a, b)` / `distance(a, b)` | Euclidean distance plus homogeneous weight |
| `homogeneous_angle(a, b)` / `angle(a, b)` | absolute cosine plus homogeneous weight |
| `orthogonal_projection(a, b)` | orthogonal projection of `a` onto `b` |
| `central_projection(a, b)` | origin-centered projection of `a` onto `b` |
| `support(x)` | point on `x` nearest the coordinate origin |
| `antisupport(x)` | dual plane-side support construction |

These named operations attach semantic expression nodes. Model roles and
tolerances needed to re-evaluate them are retained as non-rendered parameters;
changing notation does not alter their numeric meaning. Under
`Notation.lengyel()`, bulk, weight, and geometric norms render as
$\lVert X\rVert_{\text{●}}$, $\lVert X\rVert_{\text{○}}$, and
$\lVert X\rVert$.

## Geometric Constraints

The exterior algebra contains more homogeneous bivectors than the projective
model contains valid lines. `line_constraint` exposes the Plücker condition
$\mathbf v\mathbin{\bullet}\mathbf m=0`, and `is_valid_line` checks it with a
scale-aware tolerance. `orthogonalize_line` keeps a finite candidate's
direction and projects its moment perpendicular to that direction.

The same boundary is explicit for transformation elements:
`motor_constraint` and `flector_constraint` implement Eric's even- and
odd-element constraints, with corresponding predicates. This validation is
especially relevant to transwedge constructions. An order-one transwedge
antiproduct can produce the algebraic candidate for a common perpendicular,
but the result may need line-constraint correction before it represents a
geometric line. Galaga does not silently apply that correction.

## Dual Approaches to PGA

Eric's point-based RGA and the more common plane-based PGA use the same
$\mathrm{Cl}(3,0,1)$ metric in dual ways:

| Point-based RGA | Plane-based PGA |
|---|---|
| vectors are points | vectors are planes |
| trivectors are planes | trivectors are points |
| point joins use `outer_product` | point joins use `antiwedge` |
| motions use geometric antiproduct sandwiches | motions use geometric-product sandwiches |

Galaga represents these as `p_rga()` and `p_pga()` rather than an implicit
mode flag. The notebook
[`dual_approaches_to_pga.py`](../examples/rga/dual_approaches_to_pga.py)
constructs the same translated coordinates through both products.

## Executable Examples

- [`rga_demo.py`](../examples/rga/rga_demo.py) surveys Eric's exterior-algebra
  product, complement, dual, and notation families.
- [`geometry_and_measurement.py`](../examples/rga/geometry_and_measurement.py)
  covers points, incidence, paired norms, distance, angle, projections,
  support, and explicit transwedge constraint correction.
- [`dual_approaches_to_pga.py`](../examples/rga/dual_approaches_to_pga.py)
  compares the point-based and plane-based formulations side by side.

## Primary References

- [RGA complements](https://rigidgeometricalgebra.org/wiki/index.php?title=Complements)
- [RGA metrics](https://rigidgeometricalgebra.org/wiki/index.php?title=Metrics)
- [RGA dot products](https://rigidgeometricalgebra.org/wiki/index.php?title=Dot_products)
- [RGA duals](https://rigidgeometricalgebra.org/wiki/index.php?title=Duals)
- [RGA interior products](https://rigidgeometricalgebra.org/wiki/index.php?title=Interior_products)
- [RGA geometric products](https://rigidgeometricalgebra.org/wiki/index.php?title=Geometric_products)
- [RGA transwedge products](https://rigidgeometricalgebra.org/wiki/index.php?title=Transwedge_products)
- [Terathon: The Transwedge Product](https://terathon.com/blog/transwedge-product.html)
- [Terathon: Dual Approaches to Projective Geometric Algebra](https://terathon.com/blog/dual-pga.html)
