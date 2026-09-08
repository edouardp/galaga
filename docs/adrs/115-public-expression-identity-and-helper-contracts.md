---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-115: Public Expression Identity and Helper Contracts

## Context and problem statement

Seventeen methods in the mixed coverage suite still exercise reflected
operators, scalar nodes, private coercion/equality helpers and known-grade
queries. All pass against v1, but several names or comments overstate what
they prove. The explicit-grade test supplies a matching grade, masking that
`sym(..., grade=...)` ignores the argument. Direct `Sym` construction does
honor an override. The equality fallback test actually exercises the
recognized `Dual` branch, not an unknown-node fallback.

[ADR-077](077-optional-expression-provenance.md) separates eager values from
immutable expression structure. [ADR-114](114-grade-inspection-and-bounded-simplification-contracts.md)
preserves numeric grade inspection without fixed grades on symbols.
The remaining helper contracts must move to those public owners without
restoring the old private functions or conflating different equality policies.

## Decision outcome

Move all seventeen original method identities to
`tests/facade/test_expression_helper_contracts.py`. Keep the other 72 methods
and unrelated mixed-file code unchanged. The two display and six rotor cases
remaining in `TestCoverageGaps` belong to subsequent groups.
No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/expression-helpers-v1.json)
retains complete source and SHA-256 evidence, all 89 source identities, the
seventeen extracted identities and their new owner. Capture provenance is
`4f8b166`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2. Two signatures retain
four reflected-product observations, fourteen known-grade observations,
sixteen equality comparisons and eight parity observations before/after
simplification, with explicit bindings, values, strings and node types.
Also retain scalar rendering, the invalid-coercion error, unknown-node
equality and the ignored `sym` keyword versus direct `Sym` override.

### Distinguish the three equality questions

Numeric multivector equality follows
[ADR-095](095-exact-numeric-equality-and-compatible-hashes.md); names and
provenance do not participate. Expression equality instead compares concrete
node type, operation ID, ordered operands and normalized parameters. Symbol
identity includes all `Name` spellings. An ASCII environment key is a lookup
fallback, not permission to equate names with different variants; an exact
`Name` key takes precedence.

Equal expression nodes have compatible hashes and dictionary/set behavior.
Unequal nodes are not required to have different hashes. Same-valued bindings,
commutative numeric results or identical rendered strings do not imply equal
histories. Conversely, an unchanged expression can produce a new value under
new bindings; caching evaluation requires its algebra and binding context.

Constructors snapshot input containers into immutable tuples. External
coefficient, operand or parameter-list mutation must not change a saved node.
Existing fields remain read-only. Concrete leaf constructors and `Call`
validation replace private coercion; replay retains missing-context,
foreign-algebra, literal-dimension and unsupported-node errors.

### Compare stored floats exactly, without promising exact construction

Literal coefficients and scalar parameters are finite floats. Their equality
is exact, not tolerance-based: adjacent floats and nonzero subnormals remain
distinct, while signed zeros are equal and hash compatibly. Reject nonfinite
and invalid typed inputs before evaluation.

Construction still converts representable input types to floats. For example,
`2**53 + 1` rounds to `2**53` and `Fraction(1, 10)` becomes binary `0.1`.
The resulting literal equals another literal containing that stored float.
But the evaluated multivector must not compare equal to the original
unrepresentable integer or exact fraction: numeric comparison must not repeat
the constructor's rounding. This extends regression coverage, not the scalar
representation or equality policy.

### Preserve helper responsibilities through public behavior

Reflected geometric multiplication retains reversed operand order in both
coefficients and provenance. Explicit scalar leaves render through `render`,
not diagnostic repr. `Symbol` and `named` reject `grade=`; inspect the value's
actual coefficients or construct a grade projection instead.

Known-grade replacements use explicit replay followed by numeric inspection.
A grade-2 projection may be zero; an addition with no old static grade rule
may nevertheless produce a pure vector. Parity calls remain valid when a
symbol is rebound to a different grade. Derive expectations using native-mask
grade signs, Gram minors and forced-reference product tensors across
Euclidean, oblique-indefinite and degenerate metrics.

Mutation controls reject stale replay, reversed source order, unconditional
node equality, identity-based hashing, approximate literal equality, ASCII-only
name identity and corrupted archives. A fresh process blocks legacy imports.
The [eager-values notebook](../../examples/galaga_v2/eager_values_and_expressions.py)
now compares numeric, structural and rendered equality, changed bindings,
adjacent floats and signed-zero dictionary lookup. Runtime assertions check
both its calculations and generated teaching text.

## Consequences

All 179 focused cases pass on Python 3.14 with 100% line/branch coverage in
both test files. All 163 public cases pass from the wheel with module origins
verified and legacy imports blocked. The seventeen historical identities
retain live ownership without v1's private helpers.

Full suites pass 8,447 cases (71 skipped) on Python 3.11 and 8,590 (20 skipped)
on Python 3.14. Expression nodes and simplification have 100% line/branch
coverage; evaluation has 99%, with no missed lines and one partial branch.
The full run covers an additional numeric-facade path and catalog path;
rounded production coverage percentages otherwise remain unchanged.
Ruff lint, configured Python formatting and changed-file Markdown lint pass.
The migration recipe executes and all 246 local links in the eight changed
Markdown files resolve. The existing matrix warning, 295 type errors and
Markdown code-block formatting debt remain separate work.

This subgroup is complete, not the legacy-engine retirement or a release.
The construction ledger still contains `test_coverage.py` and
`test_redesign.py`. Remaining display, naming, rotor and namespace contracts,
engine deletion and final release gates remain pending.
