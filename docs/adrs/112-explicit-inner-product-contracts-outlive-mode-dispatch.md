---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-112: Explicit Inner-Product Contracts Outlive Mode Dispatch

## Context and problem statement

The mixed coverage suite still exercises v1's `ip(..., mode=...)` dispatcher
and its symbolic fallback. All thirteen tests pass, but several vector pairs
are orthogonal and produce zero. The method named
`TestSymbolicIp.test_ip_hestenes` actually calls the default Doran–Lasenby
mode. Equal output on vectors, or the same rendered dot, cannot establish
which convention is implemented.

[ADR-003](003-explicit-inner-product-variants.md) chooses named operations
and a fixed meaning for `|`. The public v2 API already rejects ambiguous
dispatchers. This migration must preserve numerical coverage without
restoring that retired API or copying the old misleading assertions.

## Decision outcome

Move all thirteen class/method identities to
`tests/facade/test_inner_product_contracts.py`. Preserve historical evidence,
exercise the explicit public replacements and leave the other 179 mixed-file
methods unchanged. No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/inner-products-v1.json)
retains complete source and SHA-256 evidence, all 192 source identities,
the thirteen extracted identities and their new owner. Capture provenance is
`02c7654`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2. Fifteen operand/metric
cases preserve 75 observations across five modes: eager and symbolic
coefficients, Unicode and LaTeX, default/Dorst results, wrapper and expression
node types, and both invalid-mode errors. Mixed coefficients use seed 112.
The archived default is a multivector with a `Dli` expression, not a
Hestenes node.

### Keep the API and rendering boundaries explicit

`ip` and `inner_product` remain absent from core, facade and top-level public
namespaces. Users can create a local import alias for one convention; this
does not alter `|`, which remains Doran–Lasenby, including reflected scalar
operands. Named functions reject `mode` keywords, foreign algebras and bare
expression nodes as numeric operands.

Public operations always return eager facade values. Anonymous inputs can
remain untracked; literal provenance and names use the same canonical
operation IDs, explicit symbol environments and immutable presentation scopes.
The old helper's missing/invalid mode behavior is historical data, not a
new v2 error contract.

The default v2 contraction glyphs remain `\rfloor` and `\lfloor`.
The archive preserves the older `\lrcorner` and `\llcorner` spelling.
Exact three-target checks retain current spacing and scalar-product spelling,
not the old compact Unicode star. Doran–Lasenby and Hestenes may share a
LaTeX dot while retaining different IDs and values; functional notation makes
the names explicit.

### Test mathematics independently of dispatch

Exercise all sixteen grade pairs in dimension three and mixed-grade inputs
under Euclidean, oblique-indefinite and degenerate metrics. Check each of six
named operations with anonymous, literal-tracked and named operands, through
all three display targets and explicit replay.

For scalar and metric pairings, construct the coefficient oracle directly
from Gram minors. The scalar part of a product includes the grade-dependent
reversion sign; the exterior metric pairing does not. Neither oracle calls
the scalar-product implementation. For Doran–Lasenby, Hestenes and both
contractions, independently grade-filter forced-reference left-action
matrices. Coordinate formulas additionally check both vector/bivector
contraction orientations and the determinant of the restricted Gram matrix.

Changed symbol bindings must change replay without mutating the eager value.
Negative controls reject erased/nonfinite/malformed archive coefficients,
swapped inner conventions, swapped contraction directions, metric/scalar
sign confusion, reversed floor glyphs and cached eager replay.

### Teach with discriminating examples

The existing [inner-product notebook](../../examples/algebra/inner_product_family.py)
now offers four Gram matrices and renders the selected matrix with
`MatrixRepr`. Six operand pairs expose scalar handling, contraction direction,
bivector self-pairings and mixed-grade contributions. Every table value is
computed. The lesson derives signs from the metric, explains nonzero null
blades and checks replay. Four runtime regressions check the default selector
and alternate metric inputs, matrix data, table values and generated math.

## Consequences

All 237 focused cases pass on Python 3.14 with 100% line/branch coverage
in both test files. All 221 public cases pass directly from the wheel with
module origins verified and legacy imports blocked. Full suites pass 7,291
cases (66 skipped) on Python 3.11 and 7,429 (20 skipped) on Python 3.14,
including maintained notebook exports.

The reflected-pipe regression covers an additional facade path, raising
numeric facade coverage to 98%; core and rendering percentages are unchanged.
The existing matrix warning, 295 type errors and separately recorded
Markdown code-block formatting debt remain.

This is one completed subgroup, not a completed mixed suite or a release.
The construction ledger still contains `test_coverage.py` and
`test_redesign.py`. Their remaining contracts, namespace/construction guards,
engine deletion and final release gates remain pending.
