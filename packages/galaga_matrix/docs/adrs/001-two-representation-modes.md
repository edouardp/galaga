---
status: accepted
date: 2026-04-26
deciders: edouard
---

# ADR-001: Two Representation Modes — Left-Regular and Compact

Amended by [ADR-005](005-strict-inverses-and-spinor-conventions.md): compact
mode is strict on inverse conversion. It raises when the selected compact
representation is not injective or when a matrix is outside the representation
image.

## Context and Problem Statement

Every multivector in a Clifford algebra has a matrix representation, but there
are multiple ways to construct it. Users need matrix representations for:

- Verifying algebraic identities against textbook matrix forms
- Interfacing with linear algebra libraries
- Educational notebooks comparing GA and matrix approaches
- Checking that Pauli/Dirac matrices match the standard conventions

The two natural choices are the left-regular representation (always available,
always faithful) and a compact representation from the Clifford algebra
classification theorem (small, matches textbook forms for selected signatures).

## Decision Outcome

Provide both modes via a `mode=` parameter on `to_matrix` / `from_matrix`:

- **`"left-regular"`** (default): the 2ⁿ × 2ⁿ real matrix defined by
  `L(M)_{ij} = (M * e_j)_i`. Uses the precomputed multiplication tables
  directly. Works for any algebra including degenerate (r > 0). Always
  roundtrips.

- **`"compact"`**: a small complex matrix representation from the
  Atiyah-Bott-Shapiro classification. Produces Pauli (2×2) and Dirac (4×4)
  forms for the standard signatures. Inverse conversion is available only when
  the selected representation is injective and the input matrix is in the image.

### Consequences

- Good, because left-regular is trivial to implement (reshape the multiplication
  tables) and always correct
- Good, because compact matches what users expect from textbooks
- Good, because the `mode=` parameter keeps the API surface small
- Neutral: compact is not available for degenerate algebras — raises
  `NotImplementedError` with a clear message
