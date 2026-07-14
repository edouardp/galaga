# Rigid Geometric Algebra Convention Layer

Galaga exposes Eric Lengyel's Rigid Geometric Algebra (RGA) operations as a
parallel convention layer. Existing geometric-algebra functions and Python
operators keep their established meanings.

## Constructing the RGA Basis

RGA orders its vector basis as e1,e2,e3,e4 with e4 null. Use an explicit
signature because Galaga's `Algebra(3, 0, 1)` convenience form intentionally
orders null vectors first:

```python
from galaga import Algebra, Notation, b_rga

alg = Algebra((1, 1, 1, 0), blades=b_rga(), notation=Notation.lengyel())
e1, e2, e3, e4 = alg.basis_vectors()
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

The Lengyel preset emits KaTeX-compatible LaTeX without `\unicode{...}`
extensions. In particular, the Unicode antiscalar `𝟙` renders as `\text{𝟙}`.

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

## Primary References

- [RGA complements](https://rigidgeometricalgebra.org/wiki/index.php?title=Complements)
- [RGA metrics](https://rigidgeometricalgebra.org/wiki/index.php?title=Metrics)
- [RGA dot products](https://rigidgeometricalgebra.org/wiki/index.php?title=Dot_products)
- [RGA duals](https://rigidgeometricalgebra.org/wiki/index.php?title=Duals)
- [RGA interior products](https://rigidgeometricalgebra.org/wiki/index.php?title=Interior_products)
- [RGA geometric products](https://rigidgeometricalgebra.org/wiki/index.php?title=Geometric_products)
- [RGA transwedge products](https://rigidgeometricalgebra.org/wiki/index.php?title=Transwedge_products)
- [Terathon: The Transwedge Product](https://terathon.com/blog/transwedge-product.html)
