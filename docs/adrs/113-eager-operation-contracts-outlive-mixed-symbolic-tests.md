---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-113: Eager Operation Contracts Outlive Mixed Symbolic Tests

## Context and problem statement

The mixed coverage suite still tests v1 arithmetic, unary operations, scalar
nodes, normalization aliases, convenience properties and display hooks. Its
42 tests pass against v1, but several assert only a string, a zero result or
agreement between two paths through the same implementation.

[ADR-077](077-optional-expression-provenance.md) specifies eager values and
explicit replay. [ADR-099](099-symbolic-contracts-and-curated-unary-properties.md)
retains curated unary properties. Retiring another import dependency must
preserve those contracts without restoring operation-specific nodes, hidden
bindings or deferred numeric arithmetic.

## Decision outcome

Move all 42 class/method identities in ten classes into
`tests/facade/test_eager_operation_contracts.py`. Preserve every other
mixed-file method and remove only the now-unused imports. The remaining 137
methods retain their existing owners. No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/eager-operation-edges-v1.json)
retains complete source and SHA-256 evidence, all 179 source identities, the
42 extracted identities and their public owner. Capture provenance is
`2735fe8`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2. Two signatures preserve
46 nonzero mixed-grade operation observations: eager/replayed coefficients,
Unicode/LaTeX/repr, wrapper and node types. Eight further observations cover
plain/named geometric and outer products in both operand orders. Scalar-node
errors, long-name unit rendering, aliases and properties remain recorded.

### Preserve v2 boundaries, not accidental v1 spelling

- Arithmetic operates on concrete multivectors. Bare nodes require explicit
  `Call` construction; `evaluate` requires an algebra and symbol environment.
- A plain operand in a tracked operation contributes a literal snapshot.
  Named operands contribute symbols. Changed bindings affect only symbols;
  neither replay nor presentation changes the saved eager value or its hash.
- Reflected operators preserve source order, including commutative addition.
  Scalar multiplication/division retain canonical IDs and scalar parameters.
- Anonymous `norm` returns a float. Named or tracked `norm` retains its
  expression in a scalar multivector.
- `ScalarLiteral` and `Call` repr expose diagnostic structure. Use `render`
  with a presentation for mathematics; there is no context-hiding `.eval()`.
- `normalize` and `normalise` remain deprecated warning adapters to `unit`,
  not permanent identity aliases. Curated `inv`, `dag` and `sq` keep their
  existing canonical operation IDs.
- Keep reviewed v2 accents, spacing, contraction floors and three-target
  spellings. For example, long-name Unicode unit rendering uses a hat, whereas
  v1 used a quotient. The archive records history, not a rendering specification.

### Derive numeric expectations independently

Check 23 recipes across Euclidean, oblique-indefinite and rank-one degenerate
Gram matrices, with plain, literal, named and both mixed tracking states.
Use grade signs for involutions, independent exterior permutation signs for
wedge, Gram minors for metric magnitudes and scalar products, and forced
reference product tensors for products and grade-filtered contractions.
Derive inverse expectations by a linear solve and verify both residuals.
Derive pseudoscalar squares from the signed Gram determinant.

Unit and inverse are different operations. An invertible mixed multivector
can exist in a degenerate algebra; a nonzero null vector may be neither
normalizable nor invertible. Normalization uses the square root of the absolute
metric pairing, so its squared norm may be negative in an indefinite metric.
Both metric dual and undual reject a singular pseudoscalar under the existing
public contract; complementary operations are distinct.

Mutation controls reject malformed/nonfinite/erased archive coefficients,
substituted unary operations, changed norm result types, reversed source
history, cached eager replay, wrong display targets and silent deprecation
adapters. Fresh-process tests block every legacy import root.

### Teach replay without implicit state

The existing [eager-values notebook](../../examples/galaga_v2/eager_values_and_expressions.py)
now contrasts literal snapshots and symbol bindings using a bivector/vector
product with vector and trivector output. It computes original and rebound
results, renders explicit node structure separately from mathematics, and
explains scalar context and normalization boundaries. Runtime tests check
coefficients, optimized blade literal leaves, changed bindings, source order
and generated Markdown. The migration guide includes an executable recipe.

## Consequences

All 489 focused cases pass on Python 3.14 with 100% line/branch coverage in
both test files. All 470 public cases pass directly from the wheel with
module origins verified and legacy imports blocked. Full suites pass 7,737
cases (67 skipped) on Python 3.11 and 7,876 (20 skipped) on Python 3.14,
including maintained notebook exports.

Core, facade and rendering coverage are unchanged: numeric facade remains
98%, core 97% and emitter 96%. Ruff lint, configured Python formatting and
changed-file Markdown lint pass. The guide recipe executes and all 230 local
links in the changed documentation resolve. The existing matrix warning,
295 type errors and separately recorded Markdown code-block formatting debt
remain.

This is a completed subgroup, not a completed mixed suite or a release.
The construction ledger still contains `test_coverage.py` and
`test_redesign.py`. Remaining contracts, namespace/construction guards, engine
deletion and final release gates remain pending.
