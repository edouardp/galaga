# ADR-056: Real Clifford Algebras Only

## Status

Accepted

## Context

Several GA libraries (clifford, kingdon, galgebra, GeometricAlgebra.jl, Grassmann.jl) support complex-valued coefficients, enabling complexified Clifford algebras. Galaga uses `float64` NumPy arrays internally and coerces inputs via `float()`, which rejects complex numbers with a `TypeError`.

Complexified Clifford algebras are used in some areas of theoretical physics (twistor theory, spinor classification) and signal processing, but the vast majority of GA applications — rotations, reflections, PGA, STA, electromagnetism, robotics — work entirely within real algebras.

## Decision

Galaga is a real Clifford algebra library. Coefficients are real-valued (`float64`). Complex inputs are rejected at construction time.

This is a deliberate scope constraint, not an oversight. Supporting complex coefficients would require:

- Changing the internal storage from `float64` to `complex128` (doubling memory)
- Auditing every operation for complex correctness (conjugation semantics change, norms become Hermitian, etc.)
- Deciding whether `~` means reverse, Hermitian adjoint, or complex conjugate
- Handling the interaction between Clifford conjugation and complex conjugation

These are non-trivial design decisions that would complicate the API for a use case that most users don't need.

## Consequences

- `Algebra((1,1,1)).vector([1+2j, 3, 0])` raises `TypeError`.
- Users needing complex Clifford algebras should use clifford, kingdon, or galgebra.
- This keeps the API simple, memory-efficient, and unambiguous for the common case.
- The door is not closed — a future version could add complex support behind an opt-in flag, but it is not planned.
