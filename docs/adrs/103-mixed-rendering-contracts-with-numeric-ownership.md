---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-103: Mixed Rendering Contracts with Numeric Ownership

## Context and problem statement

The remaining `test_render.py` imports v1 expressions, the legacy engine,
and its tree-walking renderer. Its 141 tests cover arithmetic, products,
scripts, accents, division, sandwiches, mixed precedence, and notation
overrides. Unlike the preceding pure LaTeX suite, these symbols carry
meaningful, distinct basis-vector bindings, and named sandwiches carry an
explicit bivector. Those numeric responsibilities must survive migration.

The old tests pass before migration. A direct public-expression port exposes
54 methods whose output differs from current v2 policy. Review shows these
are already documented differences, not new production defects.

## Decision outcome

### Keep every historical test identity and its numeric evidence

The [archive](../../packages/galaga/tools/baselines/render-contracts-v1.json)
was captured on 2026-09-07 at commit `370a4e1`, using Python 3.14.4 and
NumPy 2.5.2. It preserves the full source hash, all 141 identifiers and method
sources, and 143 actual rendering observations. Each observation includes
its target, displayed string, symbol bindings, and evaluated coefficients in
native-mask order. Scalars are recorded in the same coefficient shape.

Keep all 141 class/method identifiers in the live suite. Construct public
`Call`, `ScalarLiteral`, and unbound `Symbol` expressions; notation
overrides use immutable public rules and algebra views. Do not introduce
an adapter that reimplements old expression classes.

A separate public numeric suite executes every live historical method with
its archived bindings. Each rendering call must also reproduce the captured
numeric result through explicit evaluation, with only the already reviewed
Lie/Jordan factor-of-two correction. Rendering preserves expression hashes.
Shape and finiteness checks prevent broadcasting or nonfinite values from
passing numeric comparison.

Three old permissive assertions become exact contracts: nested reverse,
negative scalar multiplication inside a product, and custom function-style
LaTeX. Historical source and output remain evidence; accepted v2 output is
pinned independently in live literal assertions.

### Retain existing v2 presentation choices

No production code or display policy changes in this work unit:

- Infix products and scalar division use v2 spacing and glyphs. Hestenes
  inner product retains its explicit Unicode functional fallback.
- Unicode accents attach to grouped expressions instead of v1's textual
  fallback prefixes/functions. Conjugation uses the combining overline.
  Dual and undual keep explicit positional star notation.
- LaTeX reverse uses the existing wide tilde.
- Unit normalization keeps the default hat for compounds. The opt-in
  `unit_fraction` rule from ADR-101 remains available; automatic
  atom-versus-compound switching is not restored.
- The renderer simplifies a double negation in its temporary display view
  without changing stored provenance.
- Negated products and nested regressive products retain the shared
  builder's conservative parentheses.
- At this checkpoint multivector division remains a geometric product with a
  right inverse. [ADR-119](119-division-provenance-and-exact-scalar-dispatch.md)
  subsequently preserves a two-operand division call and fraction rendering;
  the numeric right-division oracle below remains unchanged.
- Lie and Jordan products retain their documented unscaled v2 definitions.
  Removing the printed half is not merely a typography change.

These continue ADR-078, ADR-098, ADR-099, and ADR-101 rather than selecting
new defaults.

### Add independent, non-vacuous composition checks

The original orthogonal-vector Jordan example evaluates to zero, so it cannot
distinguish scaled from unscaled semantics. Add mixed-grade inputs whose Lie
and Jordan products are both nonzero, across Euclidean, oblique-indefinite,
and native-null Gram matrices.

Before naming values or constructing display expressions, force the core's
reference product backend, derive reverse signs from grades, and calculate
expected coefficients with left-action matrices. Solve the denominator's
left action for division; explicitly show that putting its inverse on the
wrong side gives a different result. This is independent of facade arithmetic
composition and expression replay, not an independent Clifford-algebra library.

Ten compositions check exact ASCII, Unicode, and LaTeX scope: brackets,
division, negated/reversed products, reversal inside a product, sandwiches,
grade projection, squared sums, and negative addends. Eager coefficients,
explicit replay, data, hashes, and expression identity are checked separately.
Notation-view and scoped-override checks preserve numeric sharing and restore
the source presentation. Corruption tests reject old half scaling, wrong
replay, wrong formatting, and altered archive inputs or outputs.

## Verification and consequences

All 394 focused cases pass with 100% line and branch coverage in the three
test files. Fresh-process gates prohibit every legacy import. All 378 public
cases also pass directly from the wheel with package origins verified.

The full package/release suites pass 5,494 cases on Python 3.11 and 5,611 on
Python 3.14, including maintained notebook exports. Core and facade numeric
coverage remain 97%; emitter coverage remains 94%. The existing matrix
complex-to-real warning and 295 type-check errors remain.

`test_render.py` leaves the construction-exemption ledger, reducing it
from eleven files to ten. Remaining blade-convention/mixed legacy suites,
namespace guards, engine deletion, and final release gates are separate work.
No runtime code, notebook content, changelog, or release version changes.
