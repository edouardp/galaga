---
status: accepted
date: 2026-09-09
deciders: edouard
---

# ADR-125: Separate Algebra Logarithms from Rotor Generators

## Context and problem statement

`log` previously accepted only reverse-unit even elements with scalar-square
nonscalar parts. Strengthening `is_rotor` in
[ADR-124](124-rotor-predicate-requires-vector-preservation.md) exposed two
independent issues: nonrotors can have perfectly valid algebra logarithms,
and a rotor's principal algebra logarithm need not generate a path of rotors.

Computed examples in Euclidean dimension six establish the distinction.
For $I=e_{123456}$, $I^2=-1$ and $\widetilde I=-I$:

- $U=(1+I)/\sqrt2$ is not a rotor, but $\log U=\pi I/4$ exists.
- $I$ is a rotor and $\log I=\pi I/2$, but $\exp((\log I)/2)=U$.
- The alternative bivector $B=\pi(e_{12}+e_{34}+e_{56})/2$ also satisfies
  $\exp B=I$, while its scaled exponentials are rotors.

Even positive scalar multivectors other than one were rejected by the old
guard. A geometric validation flag on `log` would continue to mix meanings.

## Decision outcome

### `log` means the principal algebra logarithm

Keep `log(value, *, atol=1e-12)`, operating on real multivectors like `exp`.
Remove rotorhood and Study-number shape as domain requirements. Select the
real principal branch of the faithful native left-regular action. Reject
singular inputs, the nonpositive-real spectral branch cut, and numerically
unresolved cases. A branch-cut rejection does not assert that no other real
logarithm exists. Do not silently complexify, choose a plane, or normalize
away the input's scalar scale.

Use positive-scalar and exact scalar-square Study closed forms as fast paths.
The formulas include the scalar logarithm of the magnitude; they do not
assume $A\widetilde A=1$. Preserve tiny nonzero coefficients and do not
threshold a nonscalar square into a null generator.

For the general case, evaluate the resolvent integral

$$
\log M=\int_0^1 (M-1)(1+t(M-1))^{-1}\,dt
$$

on the native left action, taking only the first column needed to recover
multivector coefficients. Increasing Gauss-Legendre orders 8 through 256
provide successive estimates. Eigenvalues diagnose the branch only; the
algorithm does not diagonalize via eigenvectors and supports defective
nilpotent cases. Positive scalar scaling limits coefficient magnitudes while
retaining the scalar logarithm. Every nonscalar result must satisfy the
original algebra's exponential round-trip.

The integral and principal-branch conventions are described by
[Higham](https://nhigham.com/2020/11/17/what-is-the-matrix-logarithm/).
Quadrature can converge slowly for ill-conditioned inputs; this is a known
limitation, not a reason to silently return an unresolved approximation
([Tatsuoka et al.](https://arxiv.org/abs/1901.07834)). Keep the NumPy-only
runtime dependency. More advanced scaling or a matrix-function dependency
would be a separate optimization decision.

`atol` bounds successive candidate coefficient differences. The exponential
backward residual uses `atol * max(1, max(abs(A.data)))` with no additional
relative term. This is not a forward-error certificate near the branch cut.
Reject numerically singular/ill-conditioned actions, unresolved spectral
cuts, failed linear solves, exhausted quadrature, and failed round-trips.

### Separate the intentionally geometric operation

Add `rotor_generator(R, *, atol=1e-12)`. Require `is_rotor(R)`, compute the
principal algebra logarithm, and require `is_rotor_generator` on the result.
The returned exponent includes the full scale/half-angle; it is not a unit
plane. Do not project away grades or replace the rotor by a normalized value.

This first implementation deliberately does not search alternative branches.
For $I$ above it raises an error saying that the principal logarithm is not a
rotor generator and another branch may exist. It succeeds for the covered
simple and compound principal-branch rotations, boosts and null motions.
No guarantee of a solution for every rotor or every real signature is made.

Add the independent predicate `is_rotor_generator(B, *, atol=1e-12)`:

1. $B$ is even.
2. $B+\widetilde B=0$.
3. Every $Be_i-e_iB$ lies in the native vector subspace.

These are the infinitesimal conditions for the same group tested by
`is_rotor`: reverse skewness keeps the exponential reverse-unit and the
commutator condition keeps its vector action closed. In nondegenerate
metrics this reduces to bivectors, including zero and nonsimple bivectors.
For degenerate metrics it also admits kernel generators with trivial vector
action. This intentionally matches `is_rotor`, rather than claiming a new
versor-factorization theorem. Absolute coefficient tolerance applies to all
checks; numerical acceptance does not bound error at arbitrarily large times.

### Keep facade, expression, and teaching contracts aligned

Expose canonical core operations through the existing facade catalog and
top-level namespace. `rotor_generator` has its own replayable expression ID;
it is not a `log` alias. The predicate is independently evaluable. Existing
`log` expressions retain their name and gain the mathematical domain.

Update the existing rotor notebook with positive-scalar and nonrotor logs,
compound generator recovery, and both six-dimensional half-step paths.
Teach the explicit principal-branch limitation instead of suggesting that
any logarithm can be used for geometric interpolation.

## Consequences and verification strategy

This supersedes the logarithm restriction in core
[ADR-011](../core/adrs/011-evaluate-numeric-functions-with-explicit-real-branches.md)
and resolves the log-domain follow-up in ADR-124. `sqrt`, `exp`, `sandwich`,
equality/hash semantics, package dependencies and release versions are
unchanged. No changelog update or publication is part of this work.

The core scalar factory's annotation now explicitly includes built-in
`float`, which its existing `numbers.Real` runtime check already accepted.
This avoids introducing static-checker errors at the new scalar-logarithm
call sites without changing scalar construction behavior. The existing
repository typing backlog drops from 34 errors to 11 (17 warnings remain).

Tests derive metric squares before formulas, compare general logarithms to
independent Taylor/factored exponentials and computed spectral projectors,
cover all backend strategies and oblique/degenerate metrics, and verify
negative controls for branch selection, convergence and round-trip checks.
The six-dimensional tests distinguish valid algebra logs from valid
geometric generators; facade tests cover names, rendering, and changed-binding
replay. Notebook tests inspect both coefficients and rendered output.

## Verification results

- 376 focused core/facade/notebook cases pass on Python 3.14. All statements
  and branches of `log`, its closed-form/round-trip helpers, the quadrature
  module, `rotor_generator`, and `is_rotor_generator` are covered.
- Full package and release-workflow suites: 9,330 passed / 102 skipped on
  Python 3.11; 9,504 passed / 20 skipped on Python 3.14. Both retain only the
  existing matrix complex-to-real casting warning. Python 3.14 notebook
  export uses an unsandboxed run for local kernel sockets.
- Fresh wheel and sdist contain all 33 source-identical runtime files and no
  legacy engine. A separate installed-wheel process verifies scalar and
  nonrotor logs, compound generator recovery and branch-boundary rejection,
  with all checked module origins outside the repository.
- Ruff, Python formatting, Markdown lint for changed documents, and
  `git diff --check` pass. The 11 remaining type errors and 17 warnings are
  outside the new logarithm/generator code.

No commit or publication is implied by these checks. The unrelated user edit
to `examples/matrix/cga_via_gram_matrix.py` remains untouched.
