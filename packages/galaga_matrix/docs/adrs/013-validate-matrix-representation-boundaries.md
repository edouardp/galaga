---
status: accepted
date: 2026-10-03
deciders: edouard
---

# ADR-013: Validate Matrix Representation Boundaries

## Context

`MatrixRepr` inherited algebra metadata from its left operand even when a
second bound operand belonged to another algebra or representation. The
left-regular inverse also read only the first matrix column, accepting any
correctly shaped matrix with that column as a multivector. This made metadata
look like proof that an arbitrary matrix represented a Clifford element.

## Decision

Before binary operations and NumPy ufuncs, bound `MatrixRepr` inputs and
ufunc output wrappers must share numeric algebra identity, representation
mode, basis, and source domain.
Presentation views of the same numeric algebra are compatible. If exactly
one operand is bound, its metadata supplies a candidate context for the
result regardless of operand order. Raw arrays and unbound wrappers can be
multiplied with bound wrappers. The result's metadata is a link to an algebra,
not proof that the result lies in its representation image; `.mv` validates
that claim. If both operands are unbound, the result remains unbound.
`pauli` and `dirac` are compact-mode aliases when the basis matches. For
matrix multiplication involving a spinor ket or bra, a full-domain operator
may act on an even-domain spinor; the source-domain check applies to ordinary
operator pairs and other operations. An operator acting on a bound ket returns
a ket with the ket's context. A Kronecker product has no inherited algebra
context, since its tensor representation is not determined by either operand.

`from_matrix(alg, wrapper)` rejects a conflicting bound algebra. For a
left-regular inverse, use the first column to construct a candidate, then
compare its entire computed left action to the supplied matrix with a small
float tolerance. Reject nonreal first-column coefficients. Compact mode
already checks rank and image residual. Quaternion mode also checks the
least-squares image residual. Every inverse mode therefore checks matrix
membership rather than relying on shape or wrapper metadata.

## Consequences

Operations on incompatible bound wrappers fail early. Raw matrix operations
still permit exploratory linear algebra, but conversion back to a multivector
checks membership in the representation image. Left-regular inversion costs
one left-action computation. This updates the metadata propagation behavior
from ADR-006 and the inverse behavior described in ADR-001.
Compatible bound products retain the algebra link and satisfy
`from_matrix(to_matrix(A) @ to_matrix(B)) == A * B` in supported representation
modes.

To form tensor products across different algebras, use raw `.mat` arrays and
choose the result's algebra context explicitly; neither input context alone
describes the tensor product.
