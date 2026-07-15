---
status: accepted
date: 2026-07-13
deciders: edouard
---

# ADR-071: Terathon/RGA Exterior-Algebra Convention Layer

## Context and Problem Statement

Galaga already exposes conventional Clifford-algebra products, metric duality,
and a metric-independent complement. Eric Lengyel's Rigid Geometric Algebra
(RGA) uses the same underlying exterior algebra but gives first-class names to
left/right complements, metric and antimetric applications, bulk and weight
duals, antiproducts, and transwedge products. These operations are particularly
useful with degenerate PGA metrics.

The existing Galaga meanings of `dual()`, `scalar_product()`, contractions, and
operator overloads are stable public API and cannot silently acquire RGA
semantics.

## Decision Outcome

Add the RGA operations as a parallel, explicitly named convention layer in
`galaga.algebra`:

- `metric_inner_product()` and antiscalar-valued `antidot_product()`;
- `left_complement()` and `right_complement()` as aliases for the existing
  inverse complement pair;
- metric/antimetric application, bulk/weight parts, and left/right duals;
- `antiwedge()`, `geometric_antiproduct()`, and `antireverse()`;
- left/right RGA interior products;
- experimental transwedge and transwedge-antiproduct families.

Every new implementation participates in the operation registry, grade
propagation, symbolic expression trees, evaluation, simplification traversal,
and notation rendering. True aliases reuse the registered implementation.
Named functions remain the Python API; no new operator overloads are
introduced.

`Notation.lengyel()` owns RGA rendering only. Existing Galaga `dual()` and
grade-selection contractions render functionally in this preset because their
semantics differ from RGA's star duals and interior products. Clifford
conjugation also renders functionally: the reviewed RGA sources do not assign it
the optional double-dagger notation, and overline is reserved for right
complement.

Lengyel Unicode output uses the source glyphs directly. LaTeX output uses
KaTeX-compatible commands and `\text{…}` glyphs instead of the unsupported
`\unicode{…}` macro. The RGA antiscalar keeps its Unicode name `𝟙` and renders
as `\text{𝟙}` in LaTeX. Antireverse uses KaTeX's native `\utilde{…}`
under-accent so the mark stretches with compound expressions; the notation
renderer retains `\underset` as the fallback for custom under-accent rules
without a `latex_cmd`. Lengyel right and left complements include respective
`\vphantom{Aft}` and `\vphantom{gy}` struts inside their overline and underline.
This keeps each kind of complement mark at a consistent height across an
equation while leaving other notation presets' accents unchanged.

`b_rga()` is used with the explicit signature `Algebra((1, 1, 1, 0), ...)`.
This preserves the RGA vector order e1,e2,e3,e4, makes e4 null, and preserves
the orientation of the antiscalar e1^e2^e3^e4. `Algebra(3, 0, 1)` deliberately
continues to put the null vector first and remains appropriate for the common
e0-based PGA convention.

The cached public metric matrices are read-only so callers cannot mutate an
algebra's future results.

## Consequences

- Existing GA APIs and operators retain their meanings.
- Degenerate algebras gain metric/antimetric operations without requiring a
  reciprocal null vector or inverse pseudoscalar.
- The antidot product returns a grade-n antiscalar, matching its De Morgan law
  and the geometric antiproduct identity.
- The RGA basis table and signs can be reproduced exactly, but callers must use
  the explicit RGA signature instead of the null-first `Cl(p,q,r)` constructor.
- Parameterized symbolic operations require arity-3 operation-registry and
  rendering support.

## Sources

- [RGA complements](https://rigidgeometricalgebra.org/wiki/index.php?title=Complements)
- [RGA metrics](https://rigidgeometricalgebra.org/wiki/index.php?title=Metrics)
- [RGA bulk and weight](https://rigidgeometricalgebra.org/wiki/index.php?title=Bulk_and_weight)
- [RGA duals](https://rigidgeometricalgebra.org/wiki/index.php?title=Duals)
- [RGA geometric products](https://rigidgeometricalgebra.org/wiki/index.php?title=Geometric_products)
- [RGA transwedge products](https://rigidgeometricalgebra.org/wiki/index.php?title=Transwedge_products)
- [Terathon: The Transwedge Product](https://terathon.com/blog/transwedge-product.html)
