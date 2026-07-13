# Review: Terathon Posts on GA Foundations

Sources reviewed:

- Eric Lengyel, ["Poor Foundations in Geometric Algebra"](https://terathon.com/blog/poor-foundations-ga.html),
  August 23, 2024.
- Eric Lengyel, ["The Transwedge Product"](https://terathon.com/blog/transwedge-product.html).
- Eric Lengyel, ["Geometric Algebra Books"](https://terathon.com/blog/ga-books.html).

Related Rigid Geometric Algebra wiki pages used for notation details:

- ["Dot products"](https://rigidgeometricalgebra.org/wiki/index.php?title=Dot_products).
- ["Duals"](https://rigidgeometricalgebra.org/wiki/index.php?title=Duals).
- ["Metrics"](https://rigidgeometricalgebra.org/wiki/index.php?title=Metrics).
- ["Bulk and weight"](https://rigidgeometricalgebra.org/wiki/index.php?title=Bulk_and_weight).
- ["Geometric products"](https://rigidgeometricalgebra.org/wiki/index.php?title=Geometric_products).
- ["Transwedge products"](https://rigidgeometricalgebra.org/wiki/index.php?title=Transwedge_products).

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

### Antidot Products and the Antimetric

The Rigid Geometric Algebra notation also includes an antiproduct of the dot
product. It is called the antidot product:

$$
A \mathbin{\unicode{x2218}} B
=
A^{\mathrm T}\mathbb G B,
$$

where $\mathbb G$ is the metric antiexomorphism matrix, also called the
antimetric. This mirrors the dot product

$$
A \mathbin{\unicode{x2022}} B
=
A^{\mathrm T}G B.
$$

The antidot product is also related to the dot product by a De Morgan law:

$$
A \mathbin{\unicode{x2218}} B
=
\overline{
\underline A
\mathbin{\unicode{x2022}}
\underline B
}.
$$

This was missing from the first pass. If Galaga adopts this convention layer, the
antidot product should be a first-class named operation beside the metric dot
product, not squeezed into `scalar_product()` or `metric_inner_product()`.

Candidate names:

- `metric_antidot_product(A, B)`
- `antidot_product(A, B)`
- `metric_antiexomorphism_matrix(alg)`
- `antimetric_apply(A)`

Preferred public spelling: `antidot_product(A, B)`, because that is the term
used in the RGA material. The implementation should still expose
`metric_antiexomorphism_matrix(alg)` because the distinction between $G$ and
$\mathbb G$ matters in degenerate metrics.

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

## Blade Notation and Basis Order

Lengyel's notation also differs from Galaga's usual blade naming conventions. In
Rigid Geometric Algebra, he works with the four-dimensional projective algebra

$$
\mathcal G_{3,0,1},
$$

and uses vector basis elements

$$
\mathbf e_1,\quad \mathbf e_2,\quad \mathbf e_3,\quad \mathbf e_4.
$$

Here $\mathbf e_4$ is the projective/null basis direction. This differs from the
common PGA convention used in Galaga examples, where the null basis vector is
often written $e_0$.

### RGA Basis Table

His 16 basis elements are ordered as follows:

$$
\mathbf 1
$$

$$
\mathbf e_1,\quad
\mathbf e_2,\quad
\mathbf e_3,\quad
\mathbf e_4
$$

$$
\mathbf e_{23},\quad
\mathbf e_{31},\quad
\mathbf e_{12},\quad
\mathbf e_{41},\quad
\mathbf e_{42},\quad
\mathbf e_{43}
$$

$$
\mathbf e_{423},\quad
\mathbf e_{431},\quad
\mathbf e_{412},\quad
\mathbf e_{321}
$$

$$
\unicode{x1D7D9}
$$

The bivector order is not Galaga's usual ascending-subscript order. In
particular, the spatial bivectors are cyclic:

$$
\mathbf e_{23},\quad \mathbf e_{31},\quad \mathbf e_{12},
$$

not

$$
\mathbf e_{12},\quad \mathbf e_{13},\quad \mathbf e_{23}.
$$

The mixed projective bivectors are written:

$$
\mathbf e_{41},\quad \mathbf e_{42},\quad \mathbf e_{43}.
$$

This order is deliberate. Subscripts are always written in the table order, and
signs carry the antisymmetry. For example:

$$
\mathbf e_3 \wedge \mathbf e_2
=
-\mathbf e_{23}.
$$

### Blade Shorthand

Lengyel writes:

$$
\mathbf e_{ij}
$$

as shorthand for:

$$
\mathbf e_i \wedge \mathbf e_j.
$$

Similarly:

$$
\mathbf e_{ijk}
=
\mathbf e_i \wedge \mathbf e_j \wedge \mathbf e_k,
$$

with the displayed subscript order following his basis table and the sign
absorbing any permutation needed to reach that order.

### Antiscalar Instead of Pseudoscalar

The top-grade basis element is often called the pseudoscalar or volume element,
but Lengyel prefers the antiscalar notation:

$$
\unicode{x1D7D9}
=
\mathbf e_1 \wedge \mathbf e_2 \wedge \mathbf e_3 \wedge \mathbf e_4.
$$

He uses this blackboard-bold one to put the top-grade element in symmetric
opposition to the scalar basis element:

$$
\mathbf 1
\quad\leftrightarrow\quad
\unicode{x1D7D9}.
$$

In Galaga documentation, this should be called the antiscalar when explaining
Lengyel/RGA notation. It can still be cross-referenced to the usual GA term
"pseudoscalar", but the displayed notation should use $\unicode{x1D7D9}$ in this
convention.

### Grade and Antigrade

Lengyel emphasizes two simultaneous ways to classify basis blades:

$$
\operatorname{gr}(A)
=
\text{number of present/full dimensions},
$$

and

$$
\operatorname{ag}(A)
=
\text{number of missing/empty dimensions}.
$$

In an $n$-dimensional algebra:

$$
\operatorname{gr}(A) + \operatorname{ag}(A) = n.
$$

This is why the grade-3 elements in $\mathcal G_{3,0,1}$ are naturally called
antivectors: they have grade 3 but antigrade 1. The antivector basis is:

$$
\mathbf e_{423},\quad
\mathbf e_{431},\quad
\mathbf e_{412},\quad
\mathbf e_{321}.
$$

This antigrade viewpoint is not just terminology. It explains why the notation
pairs vector-like and antivector-like objects, and why antiproducts, antidot
products, antiscalars, and weight duals are not treated as afterthoughts.

### Implications for Galaga

This should be implemented as a blade convention preset, not as part of
`Notation.lengyel()` alone. A notation preset can change how operations render,
but the RGA blade table changes basis names and display order.

Candidate API:

```python
b_lengyel_rga()
b_rga()
```

The preset should represent $\mathcal G_{3,0,1}$ with:

```python
Algebra(3, 0, 1, blades=b_lengyel_rga(), notation=Notation.lengyel())
```

The preset should provide:

- vectors displayed as $\mathbf e_1,\mathbf e_2,\mathbf e_3,\mathbf e_4$;
- scalar displayed as $\mathbf 1$ where useful in docs;
- antiscalar displayed as $\unicode{x1D7D9}$;
- bivectors displayed in the order
  $\mathbf e_{23},\mathbf e_{31},\mathbf e_{12},
  \mathbf e_{41},\mathbf e_{42},\mathbf e_{43}$;
- trivectors displayed in the order
  $\mathbf e_{423},\mathbf e_{431},\mathbf e_{412},\mathbf e_{321}$;
- optional helpers for `grade` and `antigrade` explanations.

This preset should not replace Galaga's existing PGA blade conventions. Galaga's
`b_pga()` remains useful for the common $e_0,e_1,e_2,e_3$ presentation. The
Lengyel/RGA preset should exist so notebooks and docs can faithfully reproduce
his algebraic notation when discussing his convention layer.

## Lengyel Notation Plan

The notation layer is not just cosmetic for this convention. Lengyel uses
notation to distinguish operations that many GA texts overload. If Galaga adds
these operations, `Notation.lengyel()` should faithfully render those distinctions
instead of merely changing the symbols for existing products.

The key design constraint is that Galaga's default notation already uses an
overline for Clifford conjugation and a star for the current `dual()`. In
Lengyel's notation, overline means right complement, underline means left
complement, and the star denotes the Hodge-style dual built from the extended
metric and complement. A faithful preset therefore needs new expression nodes,
not only new `NotationRule` entries for the current nodes.

### Symbol Inventory

| Concept | Lengyel notation | Unicode | LaTeX rendering | Galaga status |
|---|---:|---:|---|---|
| Geometric product | $A \mathbin{\unicode{x27D1}} B$ | `⟑` U+27D1 | `\mathbin{\unicode{x27D1}}` | current `Gp`, rendered as juxtaposition |
| Geometric antiproduct | $A \mathbin{\unicode{x27C7}} B$ | `⟇` U+27C7 | `\mathbin{\unicode{x27C7}}` | missing operation |
| Exterior product | $A \wedge B$ | `∧` | `\wedge` | current `Op` |
| Antiwedge / regressive product | $A \vee B$ | `∨` | `\vee` | current `Regressive`, sign needs audit |
| Transwedge order $k$ | $A \mathbin{\underset{k}{\unicode{x2A53}}} B$ | `⩓` U+2A53 | `\mathbin{\underset{k}{\unicode{x2A53}}}` | missing operation |
| Transwedge antiproduct order $k$ | $A \mathbin{\underset{k}{\unicode{x2A54}}} B$ | `⩔` U+2A54 | `\mathbin{\underset{k}{\unicode{x2A54}}}` | missing operation |
| Inner product | $A \mathbin{\unicode{x2022}} B$ | `•` U+2022 | `\mathbin{\unicode{x2022}}` | missing metric-induced product |
| Antidot product | $A \mathbin{\unicode{x2218}} B$ | `∘` U+2218 | `\mathbin{\unicode{x2218}}` or `\circ` | missing antimetric-induced product |
| Left contraction | $A \unicode{x230B} B$ | `⌋` U+230B | `\mathbin{\unicode{x230B}}` or `\rfloor` | current `Lc`, but semantics differ |
| Right contraction | $B \unicode{x230A} A$ | `⌊` U+230A | `\mathbin{\unicode{x230A}}` or `\lfloor` | current `Rc`, but semantics differ |
| Right complement | $\overline{A}$ | overbar | `\overline{A}` | current `complement()`, currently rendered as `A^\complement` |
| Left complement | $\underline{A}$ | underbar | `\underline{A}` | missing operation |
| Right Hodge/bulk dual | $A^{\unicode{x2605}}$ | `★` U+2605 | `A^{\unicode{x2605}}` | missing operation |
| Left Hodge/bulk dual | $A_{\unicode{x2605}}$ | `★` U+2605 | `A_{\unicode{x2605}}` | missing operation |
| Right weight antidual | $A^{\unicode{x2606}}$ | `☆` U+2606 | `A^{\unicode{x2606}}` | missing operation |
| Left weight antidual | $A_{\unicode{x2606}}$ | `☆` U+2606 | `A_{\unicode{x2606}}` | missing operation |
| Metric application | $GA$ | ordinary product-looking juxtaposition | `G A` or `\mathbf{G}A` | missing operation node |
| Antimetric application | $\mathbb G A$ | double-struck G | `\mathbb G A` | missing operation node |
| Bulk part | $A_{\unicode{x25CF}}$ | `●` U+25CF | `A_{\unicode{x25CF}}` | missing operation |
| Weight part | $A_{\unicode{x25CB}}$ | `○` U+25CB | `A_{\unicode{x25CB}}` | missing operation |
| Unit antiscalar / volume element | $\unicode{x1D7D9}$ | `𝟙` U+1D7D9 | `\unicode{x1D7D9}` | currently `pseudoscalar()` as `I` |
| Reverse | $\widetilde A$ | `~A` fallback | `\widetilde{A}` | current `Reverse` |
| Grade projection | $\langle A\rangle_k$ | `⟨A⟩ₖ` | `\langle A\rangle_k` | current `Grade` |

The table intentionally lists both current Galaga nodes and missing nodes. For
example, current `left_contraction()` should not be silently rendered as
Lengyel's left contraction if the implementation is still the conventional
grade-selection contraction. The same warning applies to `dual()`.

### Overline and Underline

The overline and underline are central to this notation:

$$
\overline{A} \quad \text{means right complement},
\qquad
\underline{A} \quad \text{means left complement}.
$$

They are not generic decoration. They must bind to the whole argument, including
compound expressions:

$$
A^{\unicode{x2605}} = \overline{GA},
\qquad
A_{\unicode{x2605}} = \underline{GA}.
$$

This creates two implementation requirements:

1. `Complement` should not be the only expression node if we add
   `left_complement()`. Use distinct nodes such as `RightComplement` and
   `LeftComplement`.
2. `Notation.lengyel()` must move Clifford conjugation away from overline.
   In this preset, rendering `conjugate(A)` as `\overline A` would be
   mathematically misleading because overline is already the right complement.

Recommended rendering behavior:

| Operation | Unicode simple argument | Unicode compound fallback | LaTeX |
|---|---|---|---|
| `right_complement(A)` | `Ā` if reliable | `overline(A)` | `\overline{A}` |
| `left_complement(A)` | `A̲` if reliable | `underline(A)` | `\underline{A}` |
| `conjugate(A)` in Lengyel preset | `conj(A)` | `conj(A)` | `\operatorname{conj}(A)` |

The combining-overline and combining-underline Unicode forms are acceptable for
single-letter display names, but they are not robust for expressions such as
`G(A + B)`. LaTeX output should therefore be the authoritative rendering for
notebooks and docs, while plain Unicode can fall back to function notation for
compound arguments.

### Dual Notation

Lengyel's right dual and left dual should be separate operations:

$$
A^{\unicode{x2605}} = \overline{GA},
\qquad
A_{\unicode{x2605}} = \underline{GA}.
$$

In nondegenerate settings he also gives the geometric-product identities:

$$
A^{\unicode{x2605}} = \widetilde A \mathbin{\unicode{x27D1}} \unicode{x1D7D9},
\qquad
A_{\unicode{x2605}} =
\unicode{x1D7D9} \mathbin{\unicode{x27D1}} \widetilde A.
$$

For Galaga, the API should avoid the bare name `dual()` because it already has a
documented meaning. Candidate names:

```python
right_hodge_dual(A)   # renders as A^{★}
left_hodge_dual(A)    # renders as A_{★}
right_bulk_dual(A)    # possible alias, if we adopt Lengyel's PGA vocabulary
left_bulk_dual(A)     # possible alias
```

The "bulk" terminology appears because in degenerate metrics there can also be
left/right weight duals. Do not invent notation for weight duals until we decide
to implement that PGA model. If needed, prefer explicit function rendering such
as `right_weight_dual(A)` over guessed symbols.

### Antidot, Antimetric, Bulk, and Weight Notation

The dot product uses the metric exomorphism matrix $G$:

$$
A \mathbin{\unicode{x2022}} B
=
A^{\mathrm T}G B.
$$

The antidot product uses the metric antiexomorphism matrix $\mathbb G$:

$$
A \mathbin{\unicode{x2218}} B
=
A^{\mathrm T}\mathbb G B.
$$

In this notation, $G$ and $\mathbb G$ are paired. For a metric $\mathfrak g$,
the RGA wiki states the relationship:

$$
G\mathbb G
=
\det(\mathfrak g)\,\mathbb{I}_{2^n}.
$$

This matters in degenerate metrics: $\mathbb G$ should not be treated as a naive
inverse of $G$.

The same distinction appears in bulk and weight projections:

$$
A_{\unicode{x25CF}} = G A,
\qquad
A_{\unicode{x25CB}} = \mathbb G A.
$$

The right bulk dual and right weight antidual are then:

$$
A^{\unicode{x2605}}
=
\overline{GA}
=
\overline{A_{\unicode{x25CF}}},
\qquad
A^{\unicode{x2606}}
=
\overline{\mathbb G A}
=
\overline{A_{\unicode{x25CB}}}.
$$

The left versions replace the right complement with the left complement:

$$
A_{\unicode{x2605}}
=
\underline{GA},
\qquad
A_{\unicode{x2606}}
=
\underline{\mathbb G A}.
$$

The antidot product should also satisfy the De Morgan relationship:

$$
A \mathbin{\unicode{x2218}} B
=
\overline{
\underline A
\mathbin{\unicode{x2022}}
\underline B
}.
$$

For Galaga, this suggests separate node names:

```text
MetricInnerProduct     # A • B
MetricAntidotProduct   # A ∘ B
MetricApply            # G A
AntimetricApply        # 𝔾 A
BulkPart               # A_●
WeightPart             # A_○
RightBulkDual          # A^★
LeftBulkDual           # A_★
RightWeightDual        # A^☆
LeftWeightDual         # A_☆
```

### Metric Application

The expression `GA` in Lengyel's definitions is not the geometric product of two
multivectors. It means the extended metric matrix `G` applied to the coordinate
column for `A`.

That should be represented explicitly:

```python
metric_apply(A)          # renders as GA in Lengyel notation
extended_metric_matrix(alg)
```

In functional notation this should render as `metric_apply(A)`. In Lengyel
notation, `metric_apply(A)` can render as `GA` for a simple argument and
`G(A + B)` for a compound argument. The renderer must not build an ordinary
`Gp(G, A)` expression for this.

### Product Notation and Existing Nodes

`Notation.lengyel()` should override existing renderings only where the
implementation semantics match:

```python
def lengyel() -> Notation:
    n = Notation()
    n.set("Gp", "unicode", NotationRule(kind="infix", separator=" ⟑ "))
    n.set("Gp", "latex", NotationRule(kind="infix", separator=r" \mathbin{\unicode{x27D1}} "))
    n.set("Op", "unicode", NotationRule(kind="infix", separator=" ∧ "))
    n.set("Op", "latex", NotationRule(kind="infix", separator=r" \wedge "))
    n.set("Regressive", "unicode", NotationRule(kind="infix", separator=" ∨ "))
    n.set("Regressive", "latex", NotationRule(kind="infix", separator=r" \vee "))
    n.set("Reverse", "latex", NotationRule(kind="accent", latex_cmd=r"\widetilde", latex_wide_cmd=r"\widetilde"))
    n.set("Conjugate", "unicode", NotationRule(kind="function", symbol="conj"))
    n.set("Conjugate", "latex", NotationRule(kind="function", symbol="conj"))
    return n
```

This is only the starting point. A faithful preset also needs rules for new node
types:

```text
MetricInnerProduct
MetricAntidotProduct
MetricApply
AntimetricApply
BulkPart
WeightPart
RightComplement
LeftComplement
RightHodgeDual
LeftHodgeDual
RightWeightDual
LeftWeightDual
GeometricAntiproduct
Transwedge
TranswedgeAntiproduct
```

The existing `Lc`, `Rc`, and `Dli` nodes should not be reused for Lengyel's
interior products unless the operations are actually implemented with his
definitions. Until then, a Lengyel preset can either leave current contractions
with their current symbols or render them functionally as
`left_contraction(A, B)` and `right_contraction(A, B)` to avoid suggesting
Lengyel semantics.

### Conjugation, Reverse, and Antireverse

In Galaga's default notation, Clifford conjugation is rendered with an overline.
That cannot remain true in `Notation.lengyel()`, because overline already means
right complement:

$$
\overline A
\quad\text{means right complement, not Clifford conjugation.}
$$

Lengyel/RGA notation clearly uses the ordinary reverse:

$$
\widetilde A,
$$

and also uses an antireverse, written as a tilde below the symbol. In
KaTeX-compatible LaTeX, a native under-accent rendering is:

$$
\utilde{A}.
$$

These two operations are grade/antigrade analogues:

$$
\widetilde A
=
(-1)^{\operatorname{gr}(A)(\operatorname{gr}(A)-1)/2}A
$$

for homogeneous $A$, and

$$
\utilde{A}
=
(-1)^{\operatorname{ag}(A)(\operatorname{ag}(A)-1)/2}A.
$$

I have not found a Lengyel/RGA page that assigns a special compact symbol to
Clifford conjugation in the usual GA sense. In his transform formulas, the
ordinary reverse and antireverse do the relevant work:

$$
x'
=
Q \mathbin{\unicode{x27D1}} x \mathbin{\unicode{x27D1}} \widetilde Q,
$$

and

$$
x'
=
Q \mathbin{\unicode{x27C7}} x
\mathbin{\unicode{x27C7}}
\utilde{Q}.
$$

For Galaga, Clifford conjugation should therefore be rendered either
definitionally or with a clearly documented Galaga-specific compact mark.

Recommended default in `Notation.lengyel()`:

$$
\operatorname{conjugate}(A)
\quad\leadsto\quad
\widehat{\widetilde A}.
$$

This uses only standard GA involutions:

$$
\operatorname{conjugate}(A)
=
\widehat{\widetilde A}
=
\widetilde{\widehat A}.
$$

Optional compact rendering:

$$
A^\ddagger
:=
\widehat{\widetilde A}.
$$

The double dagger is visually distinct from:

$$
\overline A,\quad
\underline A,\quad
A^{\unicode{x2605}},\quad
A^{\unicode{x2606}},
$$

and it is already a familiar "stronger than dagger" mark in parts of mathematics
and physics. It should still be documented as Galaga's compact notation for
Clifford conjugation, not as something Lengyel appears to use.

Avoid these in `Notation.lengyel()`:

- $\overline A$ for Clifford conjugation, because it means right complement;
- $A^*$, because black/white stars are already dual notation and `*` is often
  complex conjugation;
- $A^\dagger$, because matrix and physics readers usually read dagger as
  Hermitian adjoint;
- $A^{\mathrm T}$, because transpose belongs to matrix representations and does
  not by itself communicate the Clifford involution.

Suggested rendering table:

| Operation | Lengyel/RGA-compatible rendering | Notes |
|---|---|---|
| Reverse | $\widetilde A$ | Existing Galaga reverse can keep this |
| Antireverse | $\utilde{A}$ | New operation if antiproduct support is added |
| Grade involution | $\widehat A$ | Existing Galaga notation is acceptable |
| Clifford conjugation | $\widehat{\widetilde A}$ | Preferred explicit rendering |
| Clifford conjugation, compact | $A^\ddagger$ | Optional Galaga-specific shorthand |
| Right complement | $\overline A$ | Do not reuse for conjugation |
| Left complement | $\underline A$ | Do not reuse for conjugation |

### LaTeX Macros for Notebooks

Notebooks that teach this convention should define a small notation block near
the top. This keeps formulas readable and makes the unusual Unicode symbols
auditable:

```latex
\newcommand{\gp}{\mathbin{\unicode{x27D1}}}
\newcommand{\gap}{\mathbin{\unicode{x27C7}}}
\newcommand{\twedge}[1]{\mathbin{\underset{#1}{\unicode{x2A53}}}}
\newcommand{\tawedge}[1]{\mathbin{\underset{#1}{\unicode{x2A54}}}}
\newcommand{\inner}{\mathbin{\unicode{x2022}}}
\newcommand{\antidot}{\mathbin{\unicode{x2218}}}
\newcommand{\rcon}{\mathbin{\unicode{x230A}}}
\newcommand{\lcon}{\mathbin{\unicode{x230B}}}
\newcommand{\rcomp}[1]{\overline{#1}}
\newcommand{\lcomp}[1]{\underline{#1}}
\newcommand{\rdual}[1]{{#1}^{\unicode{x2605}}}
\newcommand{\ldual}[1]{{#1}_{\unicode{x2605}}}
\newcommand{\rwdual}[1]{{#1}^{\unicode{x2606}}}
\newcommand{\lwdual}[1]{{#1}_{\unicode{x2606}}}
\newcommand{\bulk}[1]{{#1}_{\unicode{x25CF}}}
\newcommand{\weight}[1]{{#1}_{\unicode{x25CB}}}
\newcommand{\antirev}[1]{\utilde{#1}}
\newcommand{\clconj}[1]{\widehat{\widetilde{#1}}}
\newcommand{\clconjc}[1]{{#1}^{\ddagger}}
\newcommand{\antiscalar}{\unicode{x1D7D9}}
```

If the Markdown/LaTeX renderer does not support `\unicode{...}`, use the literal
Unicode characters in the notebook source or provide a MathJax macro fallback.
The source of truth should remain the Unicode code point table above.

### Markdown Formula Examples

Use ordinary Markdown math blocks in notebooks and docs. Do not build these
formulas by joining generated strings, because bar/underline scope and
`\underset{...}{...}` notation are easy to break.

Inline examples:

- Geometric product: $A \mathbin{\unicode{x27D1}} B$
- Geometric antiproduct: $A \mathbin{\unicode{x27C7}} B$
- Exterior product: $A \wedge B$
- Antiwedge product: $A \vee B$
- Transwedge product of order $k$: $A \mathbin{\underset{k}{\unicode{x2A53}}} B$
- Transwedge antiproduct of order $k$: $A \mathbin{\underset{k}{\unicode{x2A54}}} B$
- Inner product: $A \mathbin{\unicode{x2022}} B$
- Antidot product: $A \mathbin{\unicode{x2218}} B$
- Left contraction: $A \unicode{x230B} B$
- Right contraction: $B \unicode{x230A} A$
- Right complement: $\overline{A}$
- Left complement: $\underline{A}$
- Right dual: $A^{\unicode{x2605}}$
- Left dual: $A_{\unicode{x2605}}$
- Right weight antidual: $A^{\unicode{x2606}}$
- Left weight antidual: $A_{\unicode{x2606}}$
- Extended metric applied to a multivector: $GA$
- Antimetric applied to a multivector: $\mathbb G A$
- Bulk part: $A_{\unicode{x25CF}}$
- Weight part: $A_{\unicode{x25CB}}$
- Reverse: $\widetilde A$
- Antireverse: $\utilde{A}$
- Clifford conjugation, explicit: $\widehat{\widetilde A}$
- Clifford conjugation, compact optional: $A^\ddagger$
- Unit antiscalar / volume element: $\unicode{x1D7D9}$
- Grade projection: $\langle A\rangle_k$

Display examples:

$$
A \mathbin{\unicode{x27D1}} B
= A \mathbin{\underset{0}{\unicode{x2A53}}} B
+ A \mathbin{\underset{1}{\unicode{x2A53}}} B
- A \mathbin{\underset{2}{\unicode{x2A53}}} B
- A \mathbin{\underset{3}{\unicode{x2A53}}} B
+ A \mathbin{\underset{4}{\unicode{x2A53}}} B
+ \cdots
$$

For compact formulas, use the summation form:

$$
A \mathbin{\unicode{x27D1}} B
=
\sum_k
(-1)^{k(k-1)/2}
\left(
A \mathbin{\underset{k}{\unicode{x2A53}}} B
\right).
$$

The right and left complements should visibly cover the whole argument:

$$
\overline{A + B}
\qquad
\underline{A \wedge B}
\qquad
\overline{GA}
\qquad
\underline{GA}.
$$

The Hodge/bulk duals are defined by metric application followed by the
appropriate complement:

$$
A^{\unicode{x2605}} = \overline{GA},
\qquad
A_{\unicode{x2605}} = \underline{GA}.
$$

In a nondegenerate algebra, the derived geometric-product identities are:

$$
A^{\unicode{x2605}}
=
\widetilde A \mathbin{\unicode{x27D1}} \unicode{x1D7D9},
\qquad
A_{\unicode{x2605}}
=
\unicode{x1D7D9} \mathbin{\unicode{x27D1}} \widetilde A.
$$

The inner product is the scalar metric pairing on the full exterior algebra:

$$
A \mathbin{\unicode{x2022}} B
=
A^{\mathrm T} G B.
$$

The antidot product is the corresponding scalar antimetric pairing:

$$
A \mathbin{\unicode{x2218}} B
=
A^{\mathrm T}\mathbb G B.
$$

It can also be written as the De Morgan dual of the dot product:

$$
A \mathbin{\unicode{x2218}} B
=
\overline{
\underline A
\mathbin{\unicode{x2022}}
\underline B
}.
$$

Bulk and weight projections use the metric and antimetric:

$$
A_{\unicode{x25CF}} = G A,
\qquad
A_{\unicode{x25CB}} = \mathbb G A.
$$

The corresponding bulk and weight duals are:

$$
A^{\unicode{x2605}}
=
\overline{A_{\unicode{x25CF}}},
\qquad
A^{\unicode{x2606}}
=
\overline{A_{\unicode{x25CB}}}.
$$

For same-grade multivectors, the right dual satisfies the Hodge identity:

$$
A \wedge B^{\unicode{x2605}}
=
\left(A \mathbin{\unicode{x2022}} B\right)\unicode{x1D7D9},
\qquad
\operatorname{gr}(A)=\operatorname{gr}(B).
$$

The left dual has the corresponding left-sided identity:

$$
A_{\unicode{x2605}} \wedge B
=
\left(A \mathbin{\unicode{x2022}} B\right)\unicode{x1D7D9},
\qquad
\operatorname{gr}(A)=\operatorname{gr}(B).
$$

The interior products should be written from duals and antiwedge:

$$
A \unicode{x230B} B
=
A_{\unicode{x2605}} \vee B,
\qquad
B \unicode{x230A} A
=
B \vee A^{\unicode{x2605}}.
$$

When expressed as grade selections from the geometric product, the order and
reverse are part of the notation:

$$
A \unicode{x230B} B
=
\left\langle
B \mathbin{\unicode{x27D1}} \widetilde A
\right\rangle_{\operatorname{gr}(B)-\operatorname{gr}(A)},
$$

$$
B \unicode{x230A} A
=
\left\langle
\widetilde A \mathbin{\unicode{x27D1}} B
\right\rangle_{\operatorname{gr}(B)-\operatorname{gr}(A)}.
$$

For a vector $a$ and blade $B$, the product decomposition should be written:

$$
a \mathbin{\unicode{x27D1}} B
=
B \unicode{x230A} a
+
a \wedge B.
$$

The transwedge antiproduct is defined through complements:

$$
A \mathbin{\underset{k}{\unicode{x2A54}}} B
=
\overline{
\underline A
\mathbin{\underset{k}{\unicode{x2A53}}}
\underline B
}.
$$

If a renderer cannot handle `\unicode{...}`, use literal Unicode characters:

$$
A ⟑ B
\qquad
A ⟇ B
\qquad
A ⩓_k B
\qquad
A ⩔_k B
\qquad
A • B
\qquad
A ∘ B.
$$

For conjugation, avoid overbar in this notation mode:

$$
\overline A
\neq
\operatorname{conjugate}(A)
$$

because:

$$
\overline A
=
\operatorname{right\_complement}(A).
$$

Use the explicit involution composition instead:

$$
\operatorname{conjugate}(A)
=
\widehat{\widetilde A}.
$$

If a compact postfix form is needed, define it locally:

$$
A^\ddagger
:=
\widehat{\widetilde A}.
$$

### ASCII and Python API Spelling

Python should stay ASCII even if the rendered mathematics uses Unicode:

```python
metric_inner_product(A, B)     # A • B
antidot_product(A, B)          # A ∘ B
right_complement(A)            # overline(A)
left_complement(A)             # underline(A)
right_hodge_dual(A)            # A^★
left_hodge_dual(A)             # A_★
right_weight_dual(A)           # A^☆
left_weight_dual(A)            # A_☆
antiwedge(A, B)                # A ∨ B, if sign convention matches
geometric_antiproduct(A, B)    # A ⟇ B
transwedge(A, B, k)            # A ⩓_k B
transwedge_antiproduct(A, B, k)# A ⩔_k B
metric_apply(A)                # GA
antimetric_apply(A)            # 𝔾A
bulk_part(A)                   # A_●
weight_part(A)                 # A_○
```

Avoid names like `star(A)` or `overline(A)` in the public API. They describe
notation, not mathematical semantics. The display layer can use stars and bars;
the computation layer should use names that identify the operation.

### Documentation Examples

A future notebook or docs page should show the same expression in three views:

```python
right_hodge_dual(A)
```

Default/functional explanation:

$$
\operatorname{right\_hodge\_dual}(A)
    = \operatorname{right\_complement}(G A)
$$

Lengyel notation:

$$
A^{\unicode{x2605}} = \overline{GA}.
$$

Derived nondegenerate identity:

$$
A^{\unicode{x2605}} =
\widetilde A \mathbin{\unicode{x27D1}} \unicode{x1D7D9}.
$$

Showing all three prevents users from mistaking the derived geometric-product
identity for the definition.

## Recommended Actions

### P0: Documentation Only

Add a conventions page explaining:

- GA scalar product: $\langle AB\rangle_0$;
- metric-induced exterior inner product:
  $\langle A\widetilde{B}\rangle_0$ for diagonal orthonormal metrics;
- grade-selecting contractions;
- interior products in the exterior-algebra sense;
- complement vs metric dual vs Hodge dual.
- the Lengyel notation table above, especially overline/right complement,
  underline/left complement, and star/right-left Hodge duals.
- the antidot product, antimetric, bulk part, weight part, and white-star
  weight dual notation.

This should explicitly reference the existing Galaga policy:

> Galaga uses geometric-algebra terminology as its primary vocabulary. Where
> the GA literature has competing conventions, Galaga chooses one documented
> default and exposes the other conventions under explicit names.

### P0.5: Add a Notation Preset Skeleton

Add `Notation.lengyel()` only after the symbol ownership is clear:

- overline belongs to right complement, not Clifford conjugation;
- underline belongs to left complement;
- black star belongs to Hodge/bulk duals, not current `dual()`;
- white star belongs to weight duals / antiduals;
- `∘` is the antidot product, not a generic composition operator;
- `⟑` is geometric product rendering, not a new Python operator;
- `⩓_k` and `⩔_k` require parameterized expression nodes before they can render
  correctly.

The initial preset can safely cover existing operations whose semantics match
Lengyel's notation (`Gp`, `Op`, `Regressive`, `Reverse`, `Grade`) and should
render conflicting existing operations functionally until the new operations
exist.

### P1: Add `metric_inner_product`

Implement:

```python
def metric_inner_product(a, b):
    return scalar_product(a, reverse(b))
```

for the current diagonal-metric implementation.

This should return a scalar multivector, not a Python float, to match
`scalar_product()`.

If Galaga later supports non-diagonal vector metrics, replace this shortcut with
`a.T @ extended_metric_matrix(alg) @ b`. For current diagonal signatures, the
reverse-based formula is the appropriate fast path and should be tested against
the direct extended-metric calculation.

Initial tests:

- vectors agree with existing vector inner products;
- $e_{12}\bullet e_{12}=1$ in Euclidean $Cl(3,0)$;
- mixed grades are zero;
- indefinite signatures produce metric signs correctly;
- random same-grade blades agree with a direct determinant/compound-metric
  calculation.

This is the safest first feature because it clarifies the terminology dispute
without affecting existing code.

### P1.5: Add Antimetric and Antidot Operations

After `metric_inner_product()` exists, add the corresponding antimetric
operations:

```python
def metric_antiexomorphism_matrix(alg): ...
def antimetric_apply(A): ...
def antidot_product(A, B): ...
```

These should model:

$$
A \mathbin{\unicode{x2218}} B
=
A^{\mathrm T}\mathbb G B.
$$

Tests should include:

- the De Morgan identity
  $\displaystyle A \mathbin{\unicode{x2218}} B =
  \overline{\underline A \mathbin{\unicode{x2022}} \underline B}$;
- the metric/antimetric relationship
  $\displaystyle G\mathbb G = \det(\mathfrak g)\mathbb{I}_{2^n}$;
- PGA examples where $G$ is singular but $\mathbb G$ still provides the weight
  side of the algebra;
- rendering of $A \mathbin{\unicode{x2218}} B$ in `Notation.lengyel()`;
- rendering of $A_{\unicode{x25CF}}$ and $A_{\unicode{x25CB}}$ if bulk and
  weight projections are added at the same time.

### P2: Add Explicit Left/Right Complements

Rename-by-addition:

```python
right_complement = complement
left_complement(...)
```

Keep `complement()` as the existing public name.

Tests should compute signs from the algebra, not hardcode expected values. The
display layer should render `right_complement(A)` as `\overline A` and
`left_complement(A)` as `\underline A` in `Notation.lengyel()`.

### P3: Add Hodge Dual Variants

Add:

```python
right_hodge_dual(A)
left_hodge_dual(A)
right_weight_dual(A)
left_weight_dual(A)
```

The Hodge/bulk duals should be explicitly documented as distinct from
`dual(A)`. The weight duals should be documented as antimetric/antidual
operations and can be deferred if bulk/weight PGA support is not ready.

Tests should include:

$$
A \wedge B^\star = (A \bullet B) I
$$

for same-grade blades, with the side and sign convention made explicit.

In `Notation.lengyel()`, these should render as `A^{★}` and `A_{★}` and expand
in explanatory docs to `\overline{GA}` and `\underline{GA}`.

The weight duals should render as `A^{☆}` and `A_{☆}` and expand to
`\overline{\mathbb G A}` and `\underline{\mathbb G A}`.

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

Rendering requires parameterized infix nodes, not static notation rules:

$$
A \mathbin{\underset{k}{\unicode{x2A53}}} B,
\qquad
A \mathbin{\underset{k}{\unicode{x2A54}}} B.
$$

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
6. Should `NotationRule` grow explicit overbar/underbar rule kinds, or is the
   current accent/wrap machinery enough for `RightComplement` and
   `LeftComplement`?
7. Should the antiscalar render as `𝟙`, `I_n`, or follow the algebra's existing
   pseudoscalar name when not using Lengyel notation?

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
