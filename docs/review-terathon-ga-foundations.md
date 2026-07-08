# Review: Terathon Posts on GA Foundations

Sources reviewed:

- Eric Lengyel, ["Poor Foundations in Geometric Algebra"](https://terathon.com/blog/poor-foundations-ga.html),
  August 23, 2024.
- Eric Lengyel, ["The Transwedge Product"](https://terathon.com/blog/transwedge-product.html).
- Eric Lengyel, ["Geometric Algebra Books"](https://terathon.com/blog/ga-books.html).

## Overview

Lengyel's posts are opinionated and often polemical, but they contain a
coherent technical position that is relevant to Galaga's design goal of making
competing GA conventions explicit.

The recurring theme is that many GA texts define inner products, contractions,
and duals by selecting parts of the geometric product. Lengyel argues that this
is backwards. His preferred foundation starts with the exterior algebra, metric
extension, complements, Hodge duals, antiwedge products, and interior products.
The geometric product is then treated as a structured combination of these
products, not as the source from which every other product must be derived.

This review does not adopt the rhetoric or the claim that all mainstream GA
conventions are simply wrong. Galaga should keep its GA-facing defaults stable.
The useful action is to expose Lengyel-style operations under explicit names and
document how they differ from the usual GA conventions already implemented.

This fits Galaga's project posture: Galaga is a pedagogical, convention-explicit
library rather than a performance-first library. The existence of overlapping
operations is acceptable when the overlap helps users understand where GA
authors disagree.

## Galaga's Existing Alignment

Galaga already aligns with several parts of this philosophy:

- Competing products are named explicitly:
  `left_contraction`, `right_contraction`, `hestenes_inner`,
  `doran_lasenby_inner`, and `scalar_product`.
- The `|` operator is documented as sugar for one chosen convention, not as a
  universal meaning of "inner product".
- `dual()` and `complement()` are separate.
- `complement()` works in degenerate algebras where pseudoscalar-inverse duals
  do not.
- `regressive_product()` is complement-based rather than metric-dual-based.
- Design docs already say that Galaga chooses documented defaults while
  exposing competing conventions under explicit names.

This means Galaga does not need a philosophical reset. The likely improvement is
to add a small "exterior-algebra convention layer" beside the existing GA
operation layer.

Because pedagogy and explicitness are primary goals, the main concern is not
whether these operations duplicate compositions that users could write by hand.
The main concern is whether the names identify coherent mathematical
conventions and whether the docs explain the relationship between them.

## Main Technical Claims

### Inner Products

Lengyel argues that an inner product on the full exterior algebra should be the
metric-induced scalar pairing:

$$
A \bullet B = A^\mathsf{T} G B,
$$

where $G$ is the extension of the vector-space metric to the full exterior
algebra.

For diagonal orthonormal metrics, this agrees with:

$$
A \bullet B = \langle A\widetilde{B}\rangle_0
$$

on homogeneous blades of the same grade.

This differs from Galaga's current `scalar_product(A, B)`, which is:

$$
\operatorname{scalar\_product}(A,B)=\langle AB\rangle_0.
$$

For example, in Euclidean $Cl(3,0)$:

$$
B=e_{12},\qquad
\langle BB\rangle_0=-1,\qquad
\langle B\widetilde{B}\rangle_0=1.
$$

Galaga should not change `scalar_product()`, because that name already matches
a common GA convention. But it would be useful to add a scalar-valued
metric-induced product under a different name.

Candidate names:

- `metric_inner_product(A, B)`
- `exterior_inner_product(A, B)`
- `induced_inner_product(A, B)`

Preferred name: `metric_inner_product`, because it emphasizes that this is the
metric pairing extended to the exterior algebra.

### Contractions and Interior Products

Galaga's current contractions are grade-selection operations derived from the
geometric product:

$$
A \lrcorner B = \langle AB\rangle_{s-r},
$$

for homogeneous grades $r$ and $s$, with the usual zero behavior when the grade
condition cannot be satisfied.

Lengyel argues that true interior products should be defined through Hodge duals
and antiwedge products, and should reduce to the metric-induced inner product
when the operands have the same grade.

Galaga should keep the existing contraction functions, because they are standard
GA operations and already documented. But it could add separate functions for
the exterior-algebra/interior-product convention.

Candidate names:

- `left_interior_product(A, B)`
- `right_interior_product(A, B)`
- possibly short aliases only after the conventions are well documented.

The core test should be:

$$
A \operatorname{int} B = A \bullet B
$$

for same-grade blades $A$ and $B$.

### Duals and Complements

Galaga currently has:

$$
\operatorname{dual}(A)=A\lrcorner I^{-1},
$$

which requires an invertible pseudoscalar.

It also has `complement(A)`, documented as a metric-independent right
complement. This is already close to the direction Lengyel prefers for
degenerate algebras.

The missing pieces are:

- an explicit `right_complement(A)` name;
- a corresponding `left_complement(A)`;
- Hodge-dual functions that apply the extended metric and then complement.

Candidate names:

- `right_complement(A)` aliasing current `complement(A)`;
- `left_complement(A)`;
- `right_hodge_dual(A)`;
- `left_hodge_dual(A)`.

Do not change `dual()`. Its current meaning is documented and matches a common
GA convention. Add the Hodge variants beside it.

### Antiwedge and Regressive Product

Lengyel uses "antiwedge" as a fundamental operation dual to wedge. Galaga
currently exposes `regressive_product()` and aliases it as `meet`.

Potential action:

```python
antiwedge = regressive_product
```

This should only be added if the sign convention matches the Terathon/PGA
Illuminated antiwedge convention. If the sign differs, implement a separate
`antiwedge()` and document the sign relation.

Tests should compare:

$$
A \vee B
$$

against known PGA meet examples and against the current
`regressive_product(A, B)` for a representative set of basis blades.

### Transwedge Product

The transwedge product is Lengyel's family of products interpolating between
wedge and interior products. For order $k=0$, it reduces to the wedge product.
For maximal order on simple blades, it reduces to an interior product. Lengyel
states the geometric product as a signed sum of transwedge products:

$$
AB =
\sum_{k=0}^{n}
(-1)^{k(k-1)/2}
\left(A \mathbin{\operatorname{twedge}_k} B\right).
$$

This is interesting for Galaga because it exposes the grade structure of the
geometric product in a product-family API.

Potential experimental API:

```python
transwedge(A, B, k)
transwedge_antiproduct(A, B, k)
```

Do not add operators initially. This is specialized enough that named functions
are clearer.

Tests should include:

- `transwedge(A, B, 0) == op(A, B)`;
- maximal-order cases agree with the chosen interior-product convention;
- signed sum over all orders reconstructs `gp(A, B)`;
- PGA examples for skew-line perpendicular construction, if we add enough PGA
  object helpers to express the examples clearly.

### Degenerate Metrics and PGA

Lengyel is especially critical of pretending that null basis vectors have
reciprocals. This matches Galaga's existing direction: `dual()` raises for
degenerate metrics and points users to `complement()`.

Potential actions:

- Add tests ensuring no API tries to form a reciprocal of a null basis vector.
- Expand PGA docs to distinguish:
  metric duals requiring $I^{-1}$; complements that work without the metric;
  possible Hodge-dual behavior in degenerate metrics; and norms or weights
  that live in different scalar embeddings, if we decide to support that part
  of Lengyel's PGA model.

The last point is advanced and should be deferred until Galaga has stronger PGA
object helpers and examples.

## Recommended Actions

### P0: Documentation Only

Add a conventions page explaining:

- GA scalar product: $\langle AB\rangle_0$;
- metric-induced exterior inner product:
  $\langle A\widetilde{B}\rangle_0$ for diagonal orthonormal metrics;
- grade-selecting contractions;
- interior products in the exterior-algebra sense;
- complement vs metric dual vs Hodge dual.

This should explicitly reference the existing Galaga policy:

> Galaga uses geometric-algebra terminology as its primary vocabulary. Where
> the GA literature has competing conventions, Galaga chooses one documented
> default and exposes the other conventions under explicit names.

### P1: Add `metric_inner_product`

Implement:

```python
def metric_inner_product(a, b):
    return scalar_product(a, reverse(b))
```

for the current diagonal-metric implementation.

This should return a scalar multivector, not a Python float, to match
`scalar_product()`.

Initial tests:

- vectors agree with existing vector inner products;
- $e_{12}\bullet e_{12}=1$ in Euclidean $Cl(3,0)$;
- mixed grades are zero;
- indefinite signatures produce metric signs correctly;
- random same-grade blades agree with a direct determinant/compound-metric
  calculation.

This is the safest first feature because it clarifies the terminology dispute
without affecting existing code.

### P2: Add Explicit Left/Right Complements

Rename-by-addition:

```python
right_complement = complement
left_complement(...)
```

Keep `complement()` as the existing public name.

Tests should compute signs from the algebra, not hardcode expected values.

### P3: Add Hodge Dual Variants

Add:

```python
right_hodge_dual(A)
left_hodge_dual(A)
```

These should be explicitly documented as distinct from `dual(A)`.

Tests should include:

$$
A \wedge B^\star = (A \bullet B) I
$$

for same-grade blades, with the side and sign convention made explicit.

### P4: Add Interior Product Variants

Add:

```python
left_interior_product(A, B)
right_interior_product(A, B)
```

These should be built from Hodge duals and antiwedge/complement primitives
rather than from grade selection of `gp()`.

Tests should show:

- same-grade operands reduce to `metric_inner_product`;
- scalar behavior is documented and intentional;
- vector cases agree with ordinary vector metric pairing;
- sign behavior is stable under left/right complement choices.

### P5: Add Antiwedge Alias or Function

If signs match:

```python
antiwedge = regressive_product
```

If signs differ:

```python
def antiwedge(A, B): ...
```

with a doc table comparing `antiwedge`, `regressive_product`, `meet`, and
`metric_regressive_product`.

### P6: Experimental Transwedge

Only after P1-P5 are settled, add:

```python
transwedge(A, B, k)
transwedge_antiproduct(A, B, k)
```

Mark as experimental in docs until the implementation has enough reference
examples and cross-library checks.

## Actions to Avoid

- Do not rename `scalar_product()` to mean the metric-induced inner product.
- Do not change `dual()` silently.
- Do not change the `|` operator.
- Do not adopt "the only correct convention" wording in user-facing docs.
- Do not add new operators for transwedge or antiwedge before the named
  functions and sign conventions are stable.

## Open Questions

1. Should `metric_inner_product()` be the preferred Galaga spelling, or should
   we use `exterior_inner_product()` to avoid overloading "inner product" again?
2. Should Hodge dual functions work for degenerate metrics immediately, or
   should they initially support only nondegenerate metrics while complement
   remains the degenerate-safe operation?
3. Is Galaga's current complement sign convention identical to Lengyel's
   antiwedge convention?
4. Should `norm2()` continue to mean $\langle A\widetilde A\rangle_0$, or
   should docs explicitly tie it to `metric_inner_product(A, A)` once that
   function exists?
5. Should this convention layer live in core `galaga`, or under a separate
   namespace such as `galaga.exterior`?

## Suggested ADR

If we implement any of these APIs, add an ADR along these lines:

```text
ADR-070: Exterior-Algebra Convention Layer
```

Likely decision:

- Existing GA operation names and operator overloads remain stable.
- Lengyel/Terathon-style exterior-algebra operations are added under explicit
  names.
- Documentation presents this as another convention layer, not as a correction
  that invalidates the current GA API.
