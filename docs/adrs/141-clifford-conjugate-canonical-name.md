---
status: accepted
date: 2026-09-16
deciders: edouard
---

# ADR-141: Use `clifford_conjugate` as the canonical conjugation operation

## Context

The operation traditionally exposed as `conjugate` is Clifford conjugation:
the composition of reversion and grade involution. The short name is familiar,
but it is ambiguous beside complex and quaternion conjugation, and it hides
which algebraic involution is meant. Galaga expressions also use operation IDs
for evaluation, provenance, and rendering, so the distinction must be explicit.

## Decision

`clifford_conjugate` is the canonical function and expression operation ID.
`conjugate` remains a permanent compatibility alias to the same function
object. The functional short name is `conj`.

The operation is still defined grade-wise by

\[
\operatorname{clifford\_conjugate}(A_r)
  = (-1)^{r(r+1)/2} A_r.
\]

The rename does not change numerical behavior. New expressions created through
either public function use the canonical `clifford_conjugate` operation ID;
explicit legacy `Call("conjugate", ...)` nodes remain evaluable for archived
and compatibility expressions.

## Consequences

- Documentation and new code distinguish Clifford conjugation from scalar,
  complex, or quaternion conjugation.
- The operation catalog has one canonical entry; the old spelling does not
  create a second implementation or catalog operation.
- Long notation renders `clifford_conjugate(A)` and short notation renders
  `conj(A)`. Conventional notation such as an overline remains available
  through presentation rules.
- Historical archives may contain `conjugate`; compatibility checks normalize
  that name to the canonical operation where appropriate.
