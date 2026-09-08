---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-099: Symbolic Contracts and Curated Unary Properties

The additional eager-operation identities from the mixed coverage suite now
exercise these same canonical properties without v1, including unit/inverse
domain distinctions and warning adapters; see
[ADR-113](113-eager-operation-contracts-outlive-mixed-symbolic-tests.md).

## Context and problem statement

The 57 tests in `test_symbolic.py` still exercised the legacy expression
engine: named rendering, numeric replay, untracked fallback, unary properties,
bracket scaling, and grade-aware simplification. Their public responsibilities
must survive engine retirement without retaining private operation-specific
node classes or silently changing mathematical conventions.

Migration also exposed an incomplete compatibility commitment. The executable
surface ledger classifies `bar`, `dag`, `inv`, and `sq` as curated conveniences,
but the facade did not implement them. Dropping their tests would hide that
gap. Direct probes also confirmed that v1's Lie/Jordan products are half-scaled
on both tracked and untracked paths; its commutator/anticommutator are unscaled.

## Decision outcome

Complete the four facade properties as read-only calls to canonical functions:

| Property | Canonical call | Meaning |
|---|---|---|
| `value.bar` | `grade_involution(value)` | Change odd-grade signs, not Clifford conjugation |
| `value.dag` | `reverse(value)` | Reverse, not a new Hermitian-adjoint operation |
| `value.inv` | `inverse(value)` | Default controls and the same singular-domain errors |
| `value.sq` | `squared(value)` | Geometric square |

These properties add no core API, storage, evaluator, catalog entry, expression
ID, or notation rule. Each delegates once and inherits eager evaluation,
optional provenance, presentation ownership, and immutable results. Use the
named `inverse` function when non-default numeric controls are required.
The surface contract now verifies that every curated property is present,
read-only, and equivalent to its recorded canonical operation.

The symbolic suite now constructs only public facade values. Thirty-six
representative named-value recipes retain eager coefficient checks and
explicit replay, exact reviewed ASCII/Unicode/LaTeX output, operation identity,
and rendering immutability. The replacement preserves the original suite's
rendering, replay, numeric-only, property, bracket, and simplification concerns.
The [historical archive](../../packages/galaga/tools/baselines/symbolic-contracts-v1.json)
records those v1 observations, all 57 original test identifiers, explicit
inputs, eight nonzero bracket probes across tracking states, and two old
simplification observations. Capture provenance is commit
`ee9f69b6beeb3be121acbbf30ff27142b1f7b43f`, Python 3.14.4, NumPy 2.5.2.

Retain the existing v2 conventions, not a compatibility-only arithmetic path:

- `lie_bracket` and `jordan_product` are unscaled; `half_commutator` and
  `half_anticommutator` express the old half-scaled meanings.
- Nonzero probes prevent orthogonal-vector zero results from concealing a
  factor-of-two error. Independent public left actions check both products
  across Euclidean, degenerate, oblique, and native-null metrics and every
  name/tracking state.
- `simplify` remains structural. It must not replace a symbolic Jordan
  product with Hestenes inner based on bindings or guessed grades. V2's
  unscaled vector Jordan product is twice the vector metric pairing;
  bivector and mixed-grade examples also refute a universal inner rewrite.
- Existing target-specific accents, inner-product spellings, contraction
  floors, spacing, and explicit expression-content policy remain unchanged.

Property tests independently derive involution signs from exterior grades,
squares from left actions, and inverses from a linear solve. They also cover
single delegation, read-only access, singular errors, and canonical
provenance. Fresh-process tests prohibit legacy imports throughout the
symbolic and property suites. Corruption tests reject wrong eager values,
replay, rendering, jointly mis-scaled aliases, unsafe simplification, and
malformed numeric comparisons.

## Consequences and boundaries

- Good, because a missing curated API is completed with its regression tests,
  while the larger symbolic suite no longer keeps the old engine alive.
- Good, because legacy evidence and accepted v2 differences remain explicit.
- Boundary, because production changes are limited to the four properties;
  core arithmetic, bracket scaling, simplification, and rendering are unchanged.
- Pending, because fourteen construction-ledger files, other legacy imports,
  engine deletion, and final release gates remain separate work.
