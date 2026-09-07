---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-108: Public Transformation Compositions and Geometric Notebook Plots

## Context and problem statement

The remaining low-dimensional and Chisolm transformation suites retain
nineteen historical method identities and twenty-six collected cases on the
legacy engine. Core tests already own the primitive mathematical identities.
The public API deliberately does not restore `project`, `reject`, `reflect`,
or the `Algebra.rotor` plane-angle constructor and its aliases.

Migrating these tests must preserve their mathematical evidence without
silently restoring those helpers or transferring constructor validation to
generic `exp`. Reviewing the teaching examples also exposed two plot defects:
the projector notebook drew a fixed XY surface for a rotated XZ blade, and
the reflection notebook used each plotted mirror's tangent as its normal.

## Decision outcome

Retain all nineteen identities on the public facade, using explicit primitive
compositions. Their twenty-six cases remain live. Constructor-validation cases
now distinguish the retired method from valid generic scalar/vector exponentials;
the old error observations remain archived. No production API or algorithm
changes.

The [archive](../../packages/galaga/tools/baselines/transformation-contracts-v1.json)
was captured at `7604c23` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2.
It retains both complete sources and SHA-256 digests, every method identity,
all forty seeded observations with original inputs and spanning columns, seven
low-dimensional observations, and three rotor-constructor errors. No sampled
case was skipped. Preserve the historical source attribution without presenting
the retained theorem labels as newly verified bibliographic claims.

### Make the mathematical domains explicit

- For a vector `v` and a nonzero blade `B` spanning a nondegenerate subspace,
  projection is `left_contraction(v, B) * inverse(B)`; rejection is the
  remainder, equivalently `(v ^ B) * inverse(B)`. With spanning columns `C`
  and Gram matrix `G`, compare to `C @ solve(C.T @ G @ C, C.T @ G)`.
  The restricted Gram matrix must be nonsingular; the ambient metric need not
  be. Null blades raise the existing inverse error, without a pseudoinverse.
- Reflection in the hyperplane normal to a non-null vector `n` is
  `-n * v * inverse(n)`. The independent coordinate matrix is
  `I - 2 outer(n, n @ G) / (n @ G @ n)`. Scaled and negative-square normals
  distinguish inverse from reverse. `sandwich(R, v)` always uses reversion.
- Two normal reflections compose with `R=n2*n1` and action `R*v*inverse(R)`.
  For unit Euclidean normals, reverse equals inverse. Conjugation by a
  two-dimensional blade flips the components in its *normal span*, giving
  `(I-2P)v`. In three dimensions this is not reflection in that plane as a
  mirror, which would give `(2P-I)v`.
- Compute `B*B` before choosing an exponential formula. For the coordinate
  bivector `B=e1^e2`, its square is `G12**2-G11*G22`, giving trigonometric,
  hyperbolic, or terminating branches for negative, positive, or zero square.
  The angle recipe `exp(-theta*B/2)` presupposes an oriented Euclidean unit
  plane, `B*B == -1`. Generic exponentiation has no plane-angle validation.
- Replace pseudoscalar `lazy=True` with `expr=True`. Literal provenance
  replays directly; a named `Symbol("I")` requires an explicit environment.
  Numeric coefficients and hashes do not depend on that provenance.

These decisions preserve the existing
[helper policy](../v2/compatibility-shims.md#helpers-are-not-aliases) and
[public facade boundary](085-top-level-api-is-the-facade-with-explicit-legacy-oracle.md).

### Test independent numeric evidence and actual teaching geometry

Replay every seeded observation against both archived coefficients and
coordinate projection/reflection matrices. Additional probes cover Euclidean,
oblique-indefinite and degenerate metrics, scaled blades and normals, null
failures, both expression modes, three display targets, replay and hash
stability. Bivector exponentials are checked against metric-derived scalar
formulas and an independently evaluated vector-action matrix exponential.
Corruption probes reject malformed/nonfinite coefficients, wrong contraction
side, inverse-to-reverse substitution and reversed exponential orientation.
Fresh-process tests block legacy imports.

Fix the existing notebooks rather than adding duplicate introductions:

- `projectors_ga.py` derives its plotted plane from the same rotated spanning
  vectors as the computed blade, and explains the restricted Gram matrix.
- `rotors_from_reflections.py` uses normals perpendicular to the slider-defined
  mirror lines. All three arrows come from computed multivectors; the notebook
  returns its figure for inspection and explains inverse versus reverse.

Fifteen Python 3.14 execution cases check multiple slider configurations, mesh
membership, coordinate projections, single and composed reflections, and the
actual plotted arrow components. Deliberately restoring either old geometry
causes those regression checks to fail. Python 3.11 skips these t-string
notebook executions, not the numeric contracts.

## Consequences

The 386 focused numeric/boundary cases pass, with 100% line and branch coverage
in their four test files. The construction-exemption ledger falls from six
files to four. All 376 public cases pass directly from the built wheel with
origins verified and legacy imports blocked. Full package/release suites pass
6,474 cases on Python 3.11 and 6,606 on Python 3.14, including maintained
notebook exports. Core/facade coverage and the 295-error type-check baseline
are unchanged.

The remaining construction exemptions are
`test_coverage.py`, `test_coverage_gaps.py`, `test_redesign.py`,
and `test_scalar_helpers.py`. Their mixed contracts, namespace/construction
guards, engine deletion, and final release gates remain separate work.
This completes a test-dependency and teaching-correction unit, not a release.
