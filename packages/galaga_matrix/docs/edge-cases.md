# Edge Cases and Known Gaps

## Confirmed edge cases

### Double algebras: compact from_matrix is lossy

When `(q - p) mod 8 ∈ {3, 7}`, the Clifford algebra is a direct sum of two
simple algebras (e.g. Cl(0,3) ≅ ℍ ⊕ ℍ). The compact representation only
captures one summand, so `from_matrix` cannot recover the original multivector.

**Affected algebras** (up to n=8): Cl(1,0), Cl(2,1), Cl(3,2), Cl(4,3),
Cl(0,3), Cl(1,4), Cl(5,0), Cl(6,1), Cl(2,5).

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

### from_matrix compact uses least-squares

The coefficient extraction uses `np.linalg.lstsq` on the real/imaginary parts
of the flattened blade matrices. For simple algebras this is exact (the system
is full-rank). For double algebras the system is rank-deficient and lstsq
returns the minimum-norm solution, which silently differs from the original.

A future version could check the rank and warn or raise for rank-deficient
cases.

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

### No quaternionic output format

The classification identifies some algebras as having quaternionic entries
(e.g. Cl(0,2) ≅ ℍ). The current implementation always embeds quaternions as
2×2 complex blocks. A future version could offer a `format="quaternion"`
option that returns quaternion-valued matrices (using a quaternion type from
numpy-quaternion or similar).

### MatrixRepr formatting is basic

- No control over number formatting precision
- No option to suppress near-zero entries
- No alignment of columns by decimal point
- Complex numbers with both real and imaginary parts use `a + bi` format;
  some users may prefer `a + b\mathrm{i}` or `a + b\,i` in LaTeX

### No integration with galaga's symbolic layer

`to_matrix` operates on the numeric `.data` array. If a multivector has a
symbolic expression tree, the matrix representation doesn't preserve or
display it. A future version could produce a symbolic matrix (with expression
tree entries) for use in derivations.

### Left-regular representation is always real

The left-regular representation produces real matrices even when the algebra
has complex structure. This is correct (it's a real representation of a real
algebra) but means the matrices are larger than necessary. A complex
left-regular representation could halve the size for algebras with complex
structure.

### No `__matmul__` on MatrixRepr

`MatrixRepr` supports `np.array(mr)` via `__array__`, but `mr1 @ mr2` doesn't
work because Python's `@` operator dispatches on type, not via the array
protocol. Adding `__matmul__` would make `MatrixRepr` a fuller matrix wrapper,
which may or may not be desirable — it risks duplicating numpy's API.
