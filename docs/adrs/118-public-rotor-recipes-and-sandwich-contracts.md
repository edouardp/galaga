---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-118: Public Rotor Recipes and Sandwich Contracts

## Context and problem statement

Twenty rotor/sandwich identities remain in `test_coverage.py`. All twenty
pass on v1 before migration. Their Euclidean examples mostly obscure the old
constructor's unconditional trigonometric formula. Computing the other
domains first reveals three important boundaries:

- A positive-square bivector needs a hyperbolic exponential; the old helper's
  sine/cosine result is not unit under reversion.
- The STA pseudoscalar phase is even but not a rotor. Its reverse sandwich
  fixes vectors, so checking only that action would miss the distinction.
- A nonsimple Euclidean four-dimensional bivector has a nonscalar square.
  The old helper drops the grade-four term, yet its scalar-only predicate
  incorrectly reports a rotor.

Public `exp` and `is_rotor` already handle these cases correctly. This unit
preserves that behavior and refines the teaching/migration contracts; it does
not introduce a new numeric algorithm or restore a convenience constructor.

## Decision outcome

### Retain every historical identity without restoring helper validation

Move all twenty identities to `facade/test_rotor_sandwich_contracts.py`.
The [archive](../../packages/galaga/tools/baselines/rotor-sandwich-v1.json)
retains full source/SHA-256, all source identities, 27 rotation observations
covering all three constructor names and angle forms, five actual errors,
five metric/generator domain probes and four named sandwich observations.
Coefficients, inputs, reverse products, predicate results and actual rendering
are retained, including wrong historical results. Capture provenance is
`fe6d88a`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2.

Historical rejection names document constructor retirement, not restrictions
on generic `exp`: scalar, vector and trivector exponentials remain valid.
Convert degrees with `np.deg2rad`. V1 really accepted positional radians,
despite the contrary docstring in its old test. Its three constructor names
remain absent from the public algebra.

### Compute the generator's domain and keep its scale explicit

For a simple coordinate plane `B=e1^e2`, derive
$B^2=G_{12}^2-G_{11}G_{22}$. A negative scalar square permits normalization
by $\sqrt{-B^2}$ and the oriented angle recipe $\exp(-\theta\widehat B/2)$.
A positive square uses $\sqrt{B^2}$ and rapidity, not a Euclidean angle.
A null plane cannot be normalized this way: keep its scale and use
$\exp(tB)=1+tB$. Exponentiation itself never normalizes the generator.

For commuting disjoint planes, test the full exponential against their
factorized product and an independently evaluated series of the forced
reference backend's left action. Preserve the grade-four cross term and the
whole reverse product. These are independent evaluation paths, not a second
Clifford-algebra library. Do not extend the existing Study-number `log`
domain merely because generic `exp` supports a nonsimple input.

For STA, compute $I^2=-1$ and $\widetilde I=I$. Thus
$P=\exp(-I/4)$ is even, but $P\widetilde P=P^2\ne1$.
Its reverse sandwich fixes vectors but changes some other grades. Inverse
conjugation is different and can mix vector/trivector grades.
`sandwich`/`sw` always use reverse, even for nonunit operands:
scaling a rotor by two scales its reverse sandwich by four.

The public `is_rotor` contract checks evenness and the **whole** reverse
product against one, with zero relative tolerance and the requested absolute
tolerance. This predicate is not a general high-dimensional certificate of
vector-space preservation. No predicate or equality semantics change here.

A computed six-dimensional Euclidean pseudoscalar exponential satisfies this
predicate but maps a vector to vector-plus-grade-five components. A dedicated
regression records that limitation. Deciding whether to strengthen the
predicate or expose a separate strict validator is a release follow-up,
not silently resolved by migrating these tests.

### Preserve eager values and explicit symbolic replay

Named sandwich operands use `named(...).with_expr()` and a public
`Call("sandwich", ...)`, not an old mutable symbolic product tree.
Their numeric results are eager snapshots; replay requires explicit symbol
bindings and can use changed values. `sw` remains the same public function.
Unicode is preserved; current LaTeX uses `\widetilde` instead of v1's
`\tilde`. Rendering and replay leave original coefficients/hashes unchanged.

### Finish the mixed-file ownership migration and teach the boundaries

Keep `test_coverage.py` as an import-free ownership record because existing
migration guards inspect that path. It collects no duplicate tests. Remove
it from the construction-exemption ledger; regression tests prevent the
isolation codemod from rewriting it. `test_redesign.py` is the sole remaining
entry and still contains substantial mixed contracts.

Extend the existing
[exponential notebook](../../examples/algebra/exp_log_rotors.py), rather than
adding a duplicate introduction. It teaches explicit degrees/half-angle
orientation, four displayed Gram matrices and their exponential branches,
compound grade-four terms, the restricted logarithm, and even STA phases
versus rotors. All metric displays use `MatrixRepr` and dynamic Markdown uses
native template strings.

Four runtime cases inspect the lesson at zero, 55, 90 and 180 degrees,
including coordinate-matrix action oracles and actual rendered coefficients.
Negative controls reject corrupted archives, reversed rotation orientation,
the old scalar-only predicate and an inverse-for-reverse substitution.
A fresh process blocks all legacy imports.

## Verification and consequences

All 153 focused cases pass on Python 3.14, with 100% line/branch coverage in
both new test files. Full-suite, wheel and coverage comparisons are recorded
in the [migration inventory](../v2/numeric-test-migration-inventory.md).

The construction ledger falls from two files to one. Finish the remaining
`test_redesign.py` contracts, then namespace/construction guards, obsolete
engine deletion and release gates. This is a completed migration/teaching
unit, not a release. It refines
[ADR-108](108-public-transformation-compositions-and-geometric-notebook-plots.md).
