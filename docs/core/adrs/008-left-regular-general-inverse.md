---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-008: Use the Left-Regular Solve as the General Inverse Baseline

## Context and problem statement

The familiar versor formula `reverse(A)/(A*reverse(A))` is not a general
multivector inverse. Returning it for an arbitrary value can silently produce a
one-sided or entirely incorrect result. Dimension-specific Hitzer and
Shirokov algorithms are faster than a dense solve but require a careful audit
against general native Gram bases.

The initial replacement needs a basis-neutral implementation that can also act
as an oracle for future optimized paths.

## Decision drivers

- Return a true two-sided inverse or fail.
- Work for diagonal, nonorthogonal, and degenerate ambient metrics whenever the
  particular multivector is invertible.
- Reuse the backend-neutral left-action interface.
- Keep an independent verifier for future inverse algorithms.

## Considered options

1. Use the versor reverse formula for all values.
2. Port Hitzer/Shirokov immediately.
3. Solve the left-regular linear system and verify both sides.

## Decision outcome

Materialize the matrix `L_A` for left multiplication by `A`, solve

$$
L_Ax=1,
$$

construct the candidate multivector, and verify both `A*x` and `x*A` against
the identity. Linear-algebra failure or unacceptable residuals raise
`ValueError`.

The returned left-action matrix is read-only. It is also the intended public
integration point for a left-regular matrix representation.

## Consequences

- Good, because no versor assumption is hidden.
- Good, because a candidate must be a verified two-sided inverse.
- Good, because the algorithm is independent of basis orthogonality.
- Cost, because it materializes and solves a dense `dim` by `dim` system.
- Future, because a versor fast path and audited Hitzer/Shirokov paths should
  precede the solve while retaining it as a fallback or test oracle.
