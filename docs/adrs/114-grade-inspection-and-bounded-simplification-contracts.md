---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-114: Grade Inspection and Bounded Simplification Contracts

## Context and problem statement

The mixed legacy coverage suite still contains 48 identities for grade
projection, cached grade propagation and simplification. All pass against v1,
but they mix numerical responsibilities with old private metadata and a larger
rewrite system. Some assert strings without checking evaluation.

Direct computation exposes two misleading assumptions. The old geometric
product test calls its result mixed, although its orthogonal vectors produce
a pure bivector. More seriously, the old unconditional self-wedge rewrite
produces zero for the nonsimple bivector `B=e12+e34` even though its actual
wedge square is `2*e1234`.

[ADR-077](077-optional-expression-provenance.md) specifies eager values and
untyped symbols with explicit bindings. Its bounded structural simplifier
already avoids those assumptions. Migration must preserve the mathematical
checks without silently broadening that simplifier or restoring hidden state.

## Decision outcome

Move all 48 class/method identities in `TestSymbolicGradeEvenOdd`,
`TestGradePropagation` and `TestSimplify` to
`tests/facade/test_grade_simplification_contracts.py`. The other 89 mixed-file
methods and unrelated code remain unchanged; remove only unused imports.
No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/grade-simplification-v1.json)
preserves complete source and SHA-256 evidence, all 137 source identities,
the 48 extracted identities and their public owner. Capture provenance is
`334133b`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2. Two signatures retain
30 operation/grade observations, eight parity projections, 60 simplification
observations and automatic-grade metadata. Record original/simplified values,
strings, node/wrapper types, cached versus inspected grades, and the fourteen
original scalar-context evaluation errors. The rotor sample uses the explicit
stored coefficients of a half-radian rotation in the first/third-vector plane.
Also retain the four-dimensional self-wedge counterexample and its incorrect
v1 simplification.

### Inspect values, not assumptions about names

`homogeneous_grade(atol=...)` inspects actual coefficients; it is not the old
`_grade` cache. It returns `None` for both zero and mixed-grade values.
Projection onto a grade may produce zero; a symbolic call's target does not
make its result a nonzero blade of that grade. Default inspection tolerance
is `1e-12`, and `atol=0` includes every stored nonzero coefficient. Neither
inspection tolerance nor provenance changes storage or exact equality.

`grade(x, "even")` and `even_grades(x)` select the same coefficients but retain
different canonical call structures and rendering. The former is parameterized
`grade`; the latter has its own operation ID and parity glyph. The same holds
for odd grades. Multi-grade selection retains its explicit target parameters.

Symbols do not acquire a permanent grade from their original binding.
Replay can bind the same symbol to a vector, bivector or mixed value.
An invertible homogeneous bivector can itself have a mixed-grade inverse:
the tested six-dimensional example produces grades 2 and 6. Do not infer an
inverse's grade from a generic operation rule.

### Keep the bounded rewrite contract explicit

Call `simplify` on an expression, not on a facade value; use `value.expr`
when present. It needs no numeric environment and remains idempotent.
Test the actual supported reductions, including double negation, additive
zero, unit/zero scalar factors and a genuine multi-pass fixed-point example.

Many mathematically valid v1 rewrites are not currently promised by v2:
double reversion/involution/conjugation, collecting equal terms, collapsing
nested scalar factors and nested grade projections may remain explicit.
This migration tests their values without pretending that their trees reduce.
Expanding the structural rule set would be a separate design and implementation.

Do not restore unconditional self-wedge elimination or grade-based rewrites
of untyped symbols. Keep `norm(unit(v))` and `inverse(inverse(v))` explicit,
including their domain errors for invalid bindings. Do not substitute a
constant for `R*reverse(R)` merely because one binding happened to be a rotor.

### Independent numeric checks and teaching

Derive grade support from native mask population counts, involution signs
from exterior grades, wedge/complement signs from permutation parity, and
magnitudes from Gram minors. Use forced-reference product tensors for
geometric and grade-selected products, and a linear solve for inverses.
Check Euclidean, oblique-indefinite and degenerate metrics, plain/literal/named
inputs, changed symbol grades, tiny coefficients, and both inverse residuals.
Mutation controls reject stale grades, invalid self-wedge/grade rewrites,
single-pass simplification, corrupt archives, wrong replay and wrong targets.

The [involutions notebook](../../examples/algebra/involutions_and_grade_ops.py)
now teaches grade decomposition and the three involutions, numeric versus
structural equality, rebinding and nonsimple bivectors. Three selectable Gram
matrices are displayed with `MatrixRepr`. Runtime tests check every metric,
computed values, projection reconstruction, symbol structure and generated
math. The migration guide provides an executable recipe.

## Consequences

All 600 focused cases pass on Python 3.14 with 100% line/branch coverage in
both test files. All 582 public cases pass directly from the built wheel with
origins verified and legacy imports blocked. Full suites pass 8,286 cases
(70 skipped) on Python 3.11 and 8,428 (20 skipped) on Python 3.14, including
maintained notebook exports.

Core and facade coverage are unchanged. String grade-target construction and
Unicode subscript fallback cover two additional rendering paths; the rounded
builder/emitter percentages remain 89%/96%. Ruff lint, configured Python
formatting, changed-file Markdown lint and all commit hooks pass. The guide
recipe executes and all 236 local links in the changed documentation resolve.
The existing matrix warning, 295 type errors and separate Markdown code-block
formatting debt remain.

The 48 historical identities remain live without importing v1.
This subgroup is complete, but the construction ledger still contains
`test_coverage.py` and `test_redesign.py`. Remaining helper, rendering,
transformation and namespace contracts, engine deletion and release gates
remain pending.
