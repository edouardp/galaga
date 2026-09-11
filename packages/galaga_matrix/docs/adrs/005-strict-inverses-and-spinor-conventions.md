---
status: accepted
date: 2026-06-30
deciders: edouard
supersedes: 003-double-algebras-lossy-compact.md
---

# ADR-005: Strict Inverses and Spinor Column Conventions

## Context and Problem Statement

The compact matrix representation and spinor conversions use linear systems to
recover multivector coefficients. Returning a least-squares best fit when the
representation is rank-deficient or when the input is outside the image is
misleading for a math package.

The first spinor implementation also used a dimension-only roundtrip predicate
and described the construction as minimal-left-ideal column extraction. That is
not correct for all selected representations. In particular, the Cl(1,3)
projector `1/2(I + gamma0)` has complex rank 2 in the standard Dirac
representation, so the implementation should be described as a fixed reference
column map.

The original API name `to_spinor_matrix` was also ambiguous: the conversion
returns a column vector, not an operator matrix.

The quaternion APIs also need a representation in actual quaternion-block form.
The standard Cl(1,3) Dirac gamma matrices are not arranged as 2x2 quaternion
blocks under the package's embedding convention.

The educational notebooks now show named basis views of the same Cl(1,3)
spinor column. Those views need documented conventions, but they should not
silently change the public default basis.

## Decision Outcome

Use strict inverse checks and explicit spinor conventions.

- `from_matrix(..., mode="compact")` checks the real system rank. If the
  compact representation is not injective for the requested algebra, it raises
  `TypeError`.
- `from_matrix(..., mode="compact")` checks the residual. If a matrix is not in
  the image of the Clifford representation, it raises `ValueError`.
- `to_spinor_column` maps an even multivector by `rho(psi) u`, where `u` is a
  fixed reference column chosen from the selected projector.
- `_spinor_roundtrip_possible` computes the rank of the actual even-blade
  reference-column system. Dimension counts are explanatory only.
- `from_spinor_column` uses the same system as `to_spinor_column` and rejects
  spinor columns outside the image.
- `to_spinor_matrix` and `from_spinor_matrix` remain as compatibility aliases.
- The Cl(1,3) public compact/spinor default remains the current standard Dirac
  basis.
- Weyl and Majorana basis views are layered on top by explicit unitary
  similarity transforms. The subsequently implemented public `.to_basis()`
  method supplies these views while preserving the default Dirac basis; see
  the [basis-change contract](../specs/basis-change.md).
- The documented Majorana convention uses
  $B_D=i_{\mathbb C}\Gamma^2_D$ for charge conjugation and chooses
  $U_{M\leftarrow D}$ so that
  $U_{M\leftarrow D}B_DU_{M\leftarrow D}^T=I_4$. In that basis,
  charge conjugation is componentwise complex conjugation and real columns are
  Majorana spinors.
- Quaternion matrix and quaternion spinor APIs use an explicit quaternion-block
  basis. For Cl(1,3), this basis is separate from the standard Dirac compact
  basis.
- Quaternion APIs reject double algebras such as Cl(0,3) instead of exposing a
  one-summand conversion as if it were the full quaternionic algebra.

### Teaching clarification, 2026-09-12

The [ideals and chirality notebook](../../../../examples/matrix/spinors_ideals_and_chirality.py)
distinguishes an ideal element from the even representative accepted by
`to_spinor_column`. Its first-column extraction is explicitly restricted to
the demonstrated Cl(3,0) ideal, not promoted as a general conversion API.
The general Clifford action on that even representative is transported through
the fixed reference, including the right-hand factor required for odd inputs.

Chirality matrices/projectors and basis-change diagnostics remain local teaching
constructions using public conversions. The notebook derives the Weyl change
from converted basis columns, checks all operator grades, and labels complex
amplitude plots separately from physical vector plots. No runtime convention,
spinor predicate, or representation default changes.

The STA chirality lesson starts with real even spinors. It derives the
right-acting complex structure `J` from `from_spinor_column(1j *
to_spinor_column(sta.identity))` and verifies its action on every even blade.
Chirality is the two-sided map `Psi -> I * Psi * J`, with real projections
`(Psi - I * Psi * J) / 2` and `(Psi + I * Psi * J) / 2`. Its matrix is built
from its action on column basis states, then checked against `1j * rho(I)`.
The lesson compares direct GA projections with projected columns reconstructed
through both Dirac and Weyl bases, including even, odd, and mixed operators.

This distinguishes a matrix of a spinor-space operation from the matrix of a
single real Clifford element. The chiral projector matrices are outside the
real compact representation's image, even when their entries are real;
`from_matrix` must continue to reject them. Projected spinor columns do have
real even representatives and roundtrip through `from_spinor_column`. No
complexification of the core algebra or relaxation of inverse checks is needed.

Matrix teaching panels stack headings, rendered mathematics, and captions
vertically. Comparison rows contain at most two panels and may wrap; wide
four-component operators and basis-change matrices occupy their own rows.
This keeps matrix labels and chirality weights readable at notebook width.
Controls are defined without display in an upstream cell, then rendered in
the same output stack as the calculation or plot that reads their values.
This preserves Marimo's reactive separation without putting controls and
results in separate output cells; chirality controls sit immediately before
the selected operator rather than above the introductory projector matrices.

### Consequences

- Good, because inverse functions now fail loudly when no unique exact inverse
  exists.
- Good, because spinor roundtrip support is proven by the actual algebraic map.
- Good, because named Weyl/Majorana teaching views can be tested without
  changing default compact matrices or spinor columns.
- Good, because Cl(1,3) quaternion output now uses real M(2,H) block matrices
  rather than reinterpreting non-quaternionic Dirac blocks.
- Bad, because callers relying on compact `from_matrix` returning a best-fit
  result for double algebras must switch to `mode="left-regular"` or avoid the
  inverse.
- Neutral, because compact `to_matrix` still works for non-degenerate algebras;
  only inverse behavior changed.
