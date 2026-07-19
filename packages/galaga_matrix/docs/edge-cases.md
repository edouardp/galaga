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

The coefficient extraction uses `np.linalg.lstsq` on the real/imaginary parts
of the flattened blade matrices. For simple algebras this is exact (the system
is full-rank). Rank-deficient systems raise `TypeError`, and matrices outside
the image of the representation raise `ValueError` after a residual check.

## Known gaps

### No caching of blade matrices

`_build_compact_blade_matrices` rebuilds all 2ⁿ blade matrices on every call
to `to_matrix` or `from_matrix` in compact mode. For interactive use this is
fine. For batch conversion of many multivectors in the same algebra, the
matrices should be cached on the `Algebra` object or in a separate cache.

### Representation is not unique

The compact gamma matrices depend on the recursion path. Different
implementations (or different base cases) produce different but equivalent
representations. The named special cases (Pauli, Dirac) are pinned to the
standard textbook forms, but general signatures get whatever the recursion
produces.

This means `to_matrix` output for general signatures should not be compared
across library versions or against other libraries — only the algebraic
properties (squares, anticommutation, product homomorphism) are guaranteed.

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
