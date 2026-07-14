# Terathon/RGA Convention Layer — Implementation Plan

## Problem Statement

The Terathon review (`docs/review-terathon-ga-foundations.md`) identifies a
coherent set of exterior-algebra operations that complement Galaga's existing
GA operations. These provide an alternative mathematical lens — particularly
useful for PGA where degenerate metrics make some GA-standard operations
ill-defined.

Galaga's posture: keep existing GA operations stable; add RGA-style operations
under explicit names as a parallel convention layer.

## Key Formulas

### Metric Exomorphism Matrix G

For a diagonal metric with signature `(s₁, s₂, ..., sₙ)`, the extended metric
G is a 2ⁿ × 2ⁿ diagonal matrix:

    G[bitmask, bitmask] = prod(signature[i] for each bit i set in bitmask)

All off-diagonal entries are zero. The scalar entry G[0,0] = 1 (empty product).

### Metric Antiexomorphism Matrix 𝔾

The antimetric is also diagonal:

    𝔾[bitmask, bitmask] = prod(signature[i] for each bit i NOT in bitmask)

Satisfies the identity: `G · 𝔾 = det(metric) · I`

For non-degenerate metrics, `𝔾 = det(metric) · G⁻¹`. For degenerate metrics
(det=0), both G and 𝔾 are independently meaningful even though their product
is zero.

### Left and Right Complement

Galaga's existing `complement()` is the **right complement** — defined by
`e_S ∧ complement(e_S) = I`. The **left complement** is defined by
`left_complement(e_S) ∧ e_S = I`.

The relationship: `left_complement = uncomplement`. This is because
`complement(complement(x)) = (-1)^(k(n-k)) · x` (i.e., the right complement
squared introduces a sign). The left complement undoes the right complement:
`left_complement(complement(x)) = x`.

### Antidot Product (Antiscalar Result)

The RGA antidot product returns an **antiscalar** (grade-n value), not a scalar:

    antidot_product(a, b) = (a.data @ 𝔾 @ b.data) · I

This is consistent with the De Morgan identity:
`antidot(a, b) = complement(metric_inner_product(left_complement(a), left_complement(b)))`
where the right side produces a grade-n result via complement of a scalar.

### Transwedge Product

    transwedge(a, b, k) = Σ over grade-k basis blades c of:
        (left_complement(c) ∨ a) ∧ (b ∨ right_hodge_dual(c))

- Order 0 reduces to wedge: `transwedge(a, b, 0) = a ∧ b`
- Signed sum reconstructs GP: `gp(a, b) = Σₖ (-1)^(k(k-1)/2) · transwedge(a, b, k)`
- For vectors: `transwedge(a, b, 1) = metric_inner_product(a, b)`

### Duals

- Right Hodge dual: `right_hodge_dual(u) = complement(G · u)`
- Left Hodge dual: `left_hodge_dual(u) = left_complement(G · u)`
- Geometric-product identity for supported diagonal metrics, including PGA:
  `right_hodge_dual(u) = gp(reverse(u), I)`
- Hodge identity: `a ∧ right_hodge_dual(b) = metric_inner_product(a, b) · I`
  for same-grade a, b
- Double-dual: `right_hodge_dual(right_hodge_dual(u)) = (-1)^(gr·ag) · det(metric) · u`

### Regressive Product (Galaga's Actual Formula)

Galaga uses (per ADR-031):

    regressive_product(A, B) = uncomplement(op(complement(A), complement(B)))

NOT `complement(op(complement(A), complement(B)))`. The `uncomplement` is the
left complement (inverse of the right complement). This distinction matters for
the antiwedge sign audit.

## Task Breakdown

### Task 0: Write ADR-071 (Exterior-Algebra Convention Layer)

Status: **DONE**

Write `docs/adrs/071-exterior-algebra-convention-layer.md` documenting:

- Decision to add Terathon/RGA operations as a parallel convention layer
- Public API placement: all new operations live in `galaga.algebra` alongside
  existing operations
- Complement semantics: `left_complement = uncomplement`
- Antidot returns antiscalar (grade-n), not scalar
- Notation.lengyel() renders conjugation functionally, never as overline
- Each implementation must register via `@ga_op` with grade propagation;
  aliases reuse their underlying registered operation

### Task 1: `extended_metric_matrix()` and `metric_inner_product()`

Status: **DONE**

Added `Algebra.extended_metric_matrix()` and `metric_inner_product(A, B)`.
Verified identity with `scalar_product(A, reverse(B))`.
The returned cached matrix is read-only, and `metric_inner_product` participates
in symbolic dispatch through `@ga_op`.

### Task 2: `left_complement()` and `right_complement()` alias

Status: **DONE**

**Objective:** Both complement directions explicitly named.

**Implementation:**

- `left_complement(A) = uncomplement(A)` — this is the true mathematical
  relationship. The left complement IS the inverse of the right complement.
  Verify: `complement(complement(x)) = (-1)^(k(n-k)) · x`, so the left
  complement undoes this sign.
- `right_complement = complement` (alias)
- Both aliases reuse the existing registered complement operations, including
  their symbolic support and grade propagation

**Tests:**

- `left_complement(complement(A)) == A` for all A (this IS the defining identity)
- `complement(left_complement(A)) == A` for all A
- `left_complement(e_S) ∧ e_S == I` for every basis blade
- For mixed multivectors: apply grade-by-grade and verify linearity
- Random MVs in Cl(3,0), Cl(1,3), Cl(3,0,1)

### Task 3: Antimetric operations

Status: **DONE**

**Objective:** The antimetric and operations derived from it.

**Implementation:**

- `Algebra.metric_antiexomorphism_matrix()` → diagonal `𝔾[B,B] = prod(signature[i] for i NOT in B)`
- `metric_apply(A)` → MV with data `G @ A.data`
- `antimetric_apply(A)` → MV with data `𝔾 @ A.data`
- `antidot_product(A, B)` → returns **grade-n multivector** (antiscalar):
  `(A.data @ 𝔾 @ B.data) * alg.pseudoscalar()`
- All operations registered via `@ga_op` with appropriate grade propagation

**Tests:**

- `G @ 𝔾 == det(metric) * I` for non-degenerate
- PGA: `G @ 𝔾 == 0` but both individually meaningful
- De Morgan: `antidot(A, B) == complement(metric_inner_product(left_complement(A), left_complement(B)))`
  — both sides should be grade-n multivectors

### Task 4: `right_hodge_dual()` and `left_hodge_dual()`

Status: **DONE**

**Objective:** Metric-aware duals composing metric application with complement.

**Implementation:**

- `right_hodge_dual(A) = complement(metric_apply(A))`
- `left_hodge_dual(A) = left_complement(metric_apply(A))`
- Register via `@ga_op`

**Tests:**

- Hodge identity: `op(A, right_hodge_dual(B)) == metric_inner_product(A,B) * I`
  for same-grade A, B
- All supported diagonal metrics, including PGA:
  `right_hodge_dual(A) == gp(reverse(A), alg.I)`
- PGA: works where `dual()` raises
- Double-dual: `right_hodge_dual(right_hodge_dual(A)) == (-1)^(gr*ag) * det(g) * A`
  (note: uses right_hodge_dual, NOT the existing dual())

### Task 5: Audit `antiwedge` vs `regressive_product` sign convention

Status: **DONE** — the operations are identical, so `antiwedge` is an alias.

**Objective:** Determine if signs match and add `antiwedge()`.

**Implementation:**

- Galaga's actual formula: `rp(A,B) = uncomplement(op(complement(A), complement(B)))`
  (i.e., uses left_complement as the outer operation, right complement on operands)
- RGA antiwedge: `antiwedge(A,B) = complement(op(left_complement(A), left_complement(B)))`
  (i.e., uses right complement as outer, left complement on operands)
- The two formulas are algebraically equivalent with Galaga's inverse
  left/right complements; exhaustive basis tests confirm the signs
- `antiwedge = regressive_product` (alias)

**Tests:**

- Exhaustive comparison on all basis blade pairs in Cl(3,0) and Cl(3,0,1)
- PGA meet examples from known sources
- Document any sign differences in a table

### Task 6: `antireverse()` and `geometric_antiproduct()`

Status: **DONE**

**Objective:** Anti operations.

**Implementation:**

- `antireverse(A)`: sign `(-1)^(ag*(ag-1)/2)` where ag = n - grade
- `geometric_antiproduct(A, B) = complement(gp(left_complement(A), left_complement(B)))`
- Both registered via `@ga_op`

**Tests:**

- Sign pattern verification for each grade
- De Morgan relationship with GP
- PGA sandwich formula: `Q ⟇ x ⟇ antireverse(Q)`

### Task 7: Transwedge and RGA interior-product families

Status: **DONE**

**Objective:** Product family decomposing GP.

**Implementation:**

- `transwedge(A, B, k)`: sum over grade-k basis blades c:
  `(left_complement(c) ∨ A) ∧ (B ∨ right_hodge_dual(c))`
- Mark as experimental
- Register via `@ga_op` (requires parameterized grade propagation:
  result grade = gr(A) + gr(B) - 2k)
- `transwedge_antiproduct(A, B, k)` is the De Morgan dual of `transwedge`
- `left_interior_product(A, B) = left_hodge_dual(A) ∨ B`
- `right_interior_product(A, B) = A ∨ right_hodge_dual(B)`
- Parameterized expression nodes preserve `k` through symbolic evaluation and
  render as `⩓ₖ` and `⩔ₖ` in Lengyel notation

**Tests:**

- `transwedge(A, B, 0) == op(A, B)`
- Signed sum reconstructs `gp(A, B)` exhaustively on basis-blade pairs across
  Euclidean, indefinite, and degenerate signatures
- For vectors: `transwedge(a, b, 1) == metric_inner_product(a, b)`
- Zero when k > gr(A) or k > gr(B)
- Signed transwedge-antiproduct sum reconstructs `geometric_antiproduct`
- Same-grade left/right interior products equal `metric_inner_product`
- Vector geometric-product decompositions verify left/right operand order

### Task 8: Bulk/weight parts and weight duals

Status: **DONE**

**Objective:** PGA decomposition.

**Implementation:**

- `bulk_part(A) = metric_apply(A)` (semantic alias)
- `weight_part(A) = antimetric_apply(A)` (semantic alias)
- `right_weight_dual(A) = complement(antimetric_apply(A))`
- `left_weight_dual(A) = left_complement(antimetric_apply(A))`
- All registered via `@ga_op`

**Tests:**

- PGA line decomposition
- Weight dual identities
- `right_weight_dual` produces expected results for PGA point/line/plane

### Task 9: `Notation.lengyel()` and `b_rga()` blade convention

Status: **DONE**

**Objective:** Rendering preset.

**Implementation for Notation.lengyel():**

- GP → ⟑, antiproduct → ⟇
- Right complement → overline, left complement → underline
- Hodge dual → A^★, weight dual → A^☆
- LaTeX uses KaTeX-compatible commands and `\text{…}` glyphs rather than the
  unsupported `\unicode{…}` macro
- Clifford conjugation → explicit `conjugate(A)` — the reviewed RGA sources do
  not assign it a compact symbol, and overline belongs to right complement
- Reverse → tilde, antireverse → `\utilde{…}` (tilde-below)

**Implementation for b_rga():**

- Use `Algebra((1, 1, 1, 0), blades=b_rga())`. The explicit signature preserves
  both RGA's e₁,e₂,e₃,e₄ order and the e₁∧e₂∧e₃∧e₄ antiscalar orientation.
  `Algebra(3,0,1)` remains intentionally null-first and is not remapped by a
  display-only blade convention.
- Cyclic bivector order via `display_order`: e₂₃, e₃₁, e₁₂, e₄₁, e₄₂, e₄₃
- Trivector order: e₄₂₃, e₄₃₁, e₄₁₂, e₃₂₁
- Antiscalar displayed as 𝟙 in Unicode and `\text{𝟙}` in LaTeX
- Non-canonical subscript ordering (e₃₁ not e₁₃) requires signed NamedBlade
  overrides to track that e₃₁ = -e₁₃

**Tests:**

- `b_rga()` applied to `Algebra((1,1,1,0))`: verify e₄² = 0 (null)
- All displayed blades derivable from wedge products with correct signs
- Display order matches Lengyel's basis table
- Rendering snapshot tests

### Task 10: Documentation — conventions comparison

Status: **DONE** — see `docs/rga-convention-layer.md`.

**Objective:** A docs page explaining the relationship between GA and RGA
operations: where they agree, where they disagree, when to use which.

## Dependency Graph

    Task 0 (ADR-071)

    Task 1 (metric G, metric_inner_product) [DONE]
      ├── Task 3 (antimetric, antidot, metric_apply)
      │     ├── Task 8 (bulk/weight parts and weight duals)
      │     └── Task 4 (Hodge duals) ← also needs Task 2
      ├── Task 7 (transwedge) ← also needs Tasks 2, 4, 5
      └── Task 4 (Hodge duals)

    Task 2 (left_complement = uncomplement alias)
      ├── Task 3 (antidot De Morgan test)
      ├── Task 5 (antiwedge audit)
      ├── Task 6 (antiproduct)
      └── Task 7 (transwedge)

    Task 5 (antiwedge)
      └── Task 7 (transwedge uses ∨)

    Task 6 (antireverse, antiproduct)
      └── Task 8 (weight dual identity test)

    Tasks 1–8 → Task 9 (notation preset)
    Tasks 1–9 → Task 10 (documentation)

## Symbolic Operation Contract

Every new operation MUST follow Galaga's operation registry contract
(ADR-065):

1. Register with `@ga_op(name, arity, grade=...)` for grade propagation, or be
   a true alias of an operation that already does
2. Export from `galaga/__init__.py` and add to `__all__`
3. Handle symbolic inputs: if any operand is symbolic, build an expression
   tree node rather than computing eagerly
4. Add a rendering handler in the notation system (at minimum, functional
   notation fallback)
5. Add symbolic round-trip tests (symbolic → eval → compare with numeric)

Scalar-valued functions are included in this contract too: a symbolic dot
product must remain symbolic even though its evaluated result has grade zero.

## Actions to Avoid

- Do not rename `scalar_product()` to mean the metric-induced inner product.
- Do not change `dual()` semantics.
- Do not change the `|` operator.
- Do not adopt "the only correct convention" wording in docs.
- Do not add Python operators for transwedge or antiwedge before named functions
  and sign conventions are stable.
- Do not confuse `dual()` with `right_hodge_dual()` in tests or docs.
- Do not treat antidot as scalar-valued — it returns an antiscalar (grade-n).
