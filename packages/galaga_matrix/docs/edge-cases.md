# Edge Cases and Known Gaps

## Confirmed edge cases

### Double algebras: compact from_matrix may be non-injective

When `(q - p) mod 8 ∈ {3, 7}`, the Clifford algebra is a direct sum of two
simple algebras (e.g. Cl(0,3) ≅ ℍ ⊕ ℍ). The compact representation only
captures one summand for some signatures, so `from_matrix` cannot always recover
the original multivector.

See [Double Clifford Algebras](double-algebras.md) for the mathematical
background and the connection to compact matrix roundtrips.

**Affected algebras** (up to n=8): Cl(1,0), Cl(2,1), Cl(3,2), Cl(4,3),
Cl(0,3), Cl(1,4), Cl(5,0), Cl(6,1), Cl(2,5).

`from_matrix(..., mode="compact")` now checks the real system rank and raises
`TypeError` when the selected compact representation is not injective.

**Workaround**: use `mode="left-regular"` for exact roundtrips.

**Possible future fix**: block-diagonal representation using both summands.
This would double the matrix size but make `from_matrix` exact.

### Degenerate algebras: no compact representation

Algebras with null basis vectors (r > 0, e.g. PGA Cl(2,0,1)) don't have a
simple matrix algebra classification. `to_matrix(mv, mode="compact")` raises
`NotImplementedError`.

**Workaround**: use `mode="left-regular"`.

**Possible future fix**: Cl(p,q,r) ≅ Cl(p,q) ⊗ ∧(ℝʳ). Could factor out the
exterior algebra part and represent the Cl(p,q) factor compactly, but the
resulting object is a matrix of exterior algebra elements, not a plain matrix.

### from_matrix compact uses strict least-squares

The coefficient extraction uses `np.linalg.lstsq` on column-normalized
real/imaginary parts of the flattened blade matrices. Column normalization
prevents metric units and grade-dependent scaling from creating a false rank
deficiency; recovered coefficients are rescaled to the native exterior basis.
For simple algebras the system is full-rank. Rank-deficient systems raise
`TypeError`, and matrices outside the image raise `ValueError` after a
scale-aware residual check.

Full rank does not guarantee accurate recovery of every coefficient. Even a
uniformly scaled metric has different powers of that scale in different
exterior grades. Small contributions can lose precision when added to larger
ones during forward conversion; normalizing the inverse system cannot recover
lost information. A small matrix residual therefore need not imply a small
native coefficient error. Choose reasonable metric units and inspect recovery
errors, or use left-regular matrices for direct native coefficient recovery.

### General Gram matrices use an equivalent compact basis

Explicit `mode="compact"` supports scaled diagonal and dense nonorthogonal
metrics when the core classifies the Gram matrix as nondegenerate. It factors
`G = S eta S.T`, maps vectors through `S`, and maps higher exterior blades
through minors of `S`. Automatic mode remains `left-regular` for these metrics.

For a generic dense metric, eigendirections determine the equivalent compact
basis. Eigenvector signs are normalized deterministically, but repeated
eigenspaces have no unique frame. Depend on anticommutation, products,
round-trips, and other algebraic properties rather than exact generic matrix
entries across platforms.

Spinor-column conversion and named Pauli, Dirac, Weyl, Majorana, and quaternion
conventions remain normalized-basis APIs. A general-Gram compact matrix does
not silently opt into those basis labels merely because its shape matches.

## Known gaps

### Representation is not unique

The compact gamma matrices depend on the recursion path and, for a dense Gram
matrix, the congruence factorization. Different implementations can produce
different but equivalent representations. The named normalized special cases
(Pauli, Dirac) are pinned to standard textbook forms, but general signatures
and Gram bases use the descriptor's generic convention.

This means `to_matrix` output for general signatures should not be compared
across library versions or against other libraries — only the algebraic
properties (squares, anticommutation, product homomorphism) are guaranteed.

### Representation plans are process-local cached data

Compact-family conversion plans cache immutable generators, exterior-blade
matrices, reconstruction systems, ranks, and metric-congruence metadata in a
bounded process-local LRU. This makes repeated conversion efficient and
prevents callers from mutating shared arrays. It does not make generic
eigendecomposition output a public entry-by-entry convention.

### Limited quaternionic output format

The quaternion matrix and quaternion spinor APIs require an explicit
quaternion-block basis. They currently support Cl(0,2) and Cl(1,3). Other
quaternionic signatures raise `TypeError` until a block basis is added.

Double algebras such as Cl(0,3) are rejected by quaternion APIs; a one-summand
representation is not exposed as a full quaternionic conversion.

### MatrixRepr formatting is basic

- No control over number formatting precision
- No option to suppress near-zero entries
- No alignment of columns by decimal point
- Complex numbers with both real and imaginary parts use `a + bi` format;
  some users may prefer `a + b\mathrm{i}` or `a + b\,i` in LaTeX

### Matrix provenance is structural, not entry-wise symbolic algebra

`to_matrix` preserves a facade value's public name and optional expression
provenance through a package-owned `MatrixRepresentation` node. Matrix
arithmetic then records frozen matrix-domain nodes. The concrete entries remain
eager NumPy values; the package does not construct a separate symbolic scalar
expression for every matrix entry.

Expression leaves snapshot their eager arrays as read-only data. Mutating a
later `MatrixRepr.mat` therefore does not mutate existing provenance, but it
also means expression evaluation returns the captured value rather than
observing subsequent array edits.

### Left-regular representation is always real

The left-regular representation produces real matrices even when the algebra
has complex structure. This is correct (it's a real representation of a real
algebra) but means the matrices are larger than necessary. A complex
left-regular representation could halve the size for algebras with complex
structure.

### The NumPy proxy is deliberately partial

`MatrixRepr` supports `@`, arithmetic, transpose, adjoint, inverse, conjugate,
Kronecker product, `__array__`, and ordinary `__array_ufunc__` calls. It is not
an ndarray subclass and does not attempt to proxy every NumPy method. Use
`.mat` or `np.asarray(matrix)` when an API requires an actual ndarray.
