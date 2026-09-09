---
status: accepted
date: 2026-09-09
deciders: edouard
---

# ADR-124: Rotor Predicate Requires Vector Preservation

Follow-up: [ADR-125](125-separate-algebra-logarithms-from-rotor-generators.md)
supersedes the temporary rotor-only `log` behavior described at this
checkpoint. `log` is now the principal algebra logarithm; geometric
validation belongs to `rotor_generator` and `is_rotor_generator`.
The `is_rotor` decision here remains unchanged.

## Context and problem statement

[ADR-118](118-public-rotor-recipes-and-sandwich-contracts.md) documented a
high-dimensional false positive in `is_rotor` and deferred the release
decision. Evenness and a unit **whole** reverse product are necessary but
not sufficient for a vector-preserving rotor action.

Compute the Euclidean six-dimensional pseudoscalar first:
$I^2=(-1)^{6(6-1)/2}\det G=-1$ and $\widetilde I=-I$.
Then $U=(1+I)/\sqrt{2}$ is even and $U\widetilde U=1$, but
$Ue_1\widetilde U=Ie_1=-e_{23456}$. The defect has magnitude one,
not a rounding-sized residual. The same issue occurs for pseudoscalar
exponentials in indefinite, non-orthogonal, and some degenerate metrics.

The existing predicate also gates the rotor-only Study-number `log`, which
therefore accepted some unit even nonrotors.

## Decision outcome

### Strengthen the existing predicate

Keep the public name and signature `is_rotor(value, *, atol=1e-12)` in both
core and facade. Require all three conditions:

1. All odd-grade coefficients are zero within tolerance.
2. The whole $R\widetilde R$ equals one within tolerance.
3. For each native basis vector $e_i$, every non-vector coefficient of
   $Re_i\widetilde R$ is zero within tolerance.

Linearity makes the $n$ native basis vectors sufficient. Use ordinary native
Gram products and grade inspection, including for singular Gram matrices;
do not orthogonalize, normalize basis vectors, or invert the metric.
Check cheap failures first, reuse the reverse, and stop at the first leaking
vector. A passing candidate requires one normalization product and $n$
sandwiches. Do not materialize a regular representation or a product tensor.

Do not introduce a second strict predicate while retaining the misleading
weaker meaning under `is_rotor`. A caller wanting just the weaker condition
can explicitly combine `is_even` and a full reverse-product check.

### Preserve numeric conventions and general operations

All three checks use the caller's absolute coefficient tolerance, with zero
relative tolerance, in the stored exterior basis. The tolerance is not
invariant under rescaling or changing that basis. Large boosts and poorly
conditioned metrics can amplify cancellation and require a deliberate larger
`atol`; do not silently loosen it or discard small input coefficients before
computing the action. Acceptance within tolerance is not an exact symbolic
certificate.

Keep the existing unit-reverse convention $R\widetilde R\approx+1$ across
signatures. This decision does not redesign spin-group component conventions
or claim a new factorization theorem for degenerate metrics. Signed identity
elements remain accepted, including in the zero-dimensional scalar algebra.
Higher even grades are not forbidden: valid compound bivector exponentials
can contain grades four and six while preserving vectors.

`sandwich`/`sw` still compute $RX\widetilde R$ for any operands; they do not
validate, normalize, or replace reverse with inverse. Generic `exp` retains
its existing domain. `log` uses the strengthened predicate automatically and
rejects the counterexample with its existing normalized-rotor error. Its
Study-number restriction and principal-branch policy are unchanged.
This is an existing implementation-domain restriction, not proof that a
nonrotor has no algebra logarithm: $\exp(\pi I/4)=U$ in the counterexample.
A general multivector logarithm would require a separate algorithm/domain
decision rather than weakening rotor validation.

Nor does the current `log` guarantee a bivector generator for every accepted
rotor. In Euclidean dimension six, $I$ itself preserves vectors, while the
current formula returns $\log I=\pi I/2$. This is an algebra logarithm,
but $\exp((\log I)/2)$ is the nonrotor $U$ above. An alternative bivector
logarithm $\pi(e_{12}+e_{34}+e_{56})/2$ also exponentiates to $I$ and its
scaled exponentials are rotors. General logarithms, geometric rotor
logarithms, and branch selection need a separate API decision; this fix
does not certify the current `log` as a general rotor-interpolation tool.

### Update the regression and teaching contracts

Replace the old facade regression's acceptance expectation with rejection,
preserving its computed sandwich and rendering/replay assertions. Cover
plain and expression-bearing values, including tolerance forwarding to
`is_rotor` and `log`.

Core regressions compute metric-derived squares and reverse signs before
classification. They cover Euclidean, indefinite, degenerate and oblique
metrics across automatic, reference, packed and lazy backend selections;
compound and noncommuting rotor compositions; both sides of the tolerance
boundary; a rescaled metric; large boosts; and signed scalar identities.
A singular-metric counterexample preserves the first five basis vectors but
not the sixth, guarding against checking only a sample of the basis.

Extend the existing
[rotor notebook](../../examples/algebra/exp_log_rotors.py) with the computed
six-dimensional counterexample, a displayed Gram matrix, and the tolerance
policy. Its runtime tests verify the actual coefficients and rendered output.

## Consequences

The high-dimensional rotor release decision is resolved by a behavior fix,
not merely a documented alpha limitation. Full validation remains necessary
for each release candidate; this work does not publish, bump a version, or
change the changelog. Other release gates remain independent.

The additional vector sandwiches make validation more expensive, including
the guard inside `log`. Retain the direct backend-neutral implementation
unless measured use justifies an equivalent optimization with the same
metric and tolerance coverage.

## Verification

The 240 focused rotor/core/facade/notebook cases pass on Python 3.14,
including 87 additional cases relative to the previous checkpoint.
The new predicate has 100% statement and branch coverage (11 statements,
eight branches). Forty-four cases fail against the former predicate and
pass after the fix.

Full package and release-workflow suites pass: 9,227 passed / 102 skipped
on Python 3.11 and 9,401 passed / 20 skipped on Python 3.14. The latter
requires an unsandboxed run for Marimo's local kernel sockets. Both runs
retain only the existing matrix complex-to-real casting warning. Ruff,
format checks, Markdown lint and `git diff --check` pass. The unrelated
user edit to `examples/matrix/cga_via_gram_matrix.py` is preserved.
