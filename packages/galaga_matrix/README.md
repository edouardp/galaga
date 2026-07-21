# galaga_matrix

Matrix representations for [galaga](../../packages/galaga) Clifford algebras.

> **Status**: published to PyPI alongside galaga. Released as part of the monorepo.

## What it does

Every multivector in a Clifford algebra can be represented as a matrix. This
package provides `to_matrix` / `from_matrix` conversions, spinor-column
conversions for supported even subalgebras, quaternion-block output for
selected quaternionic signatures, and a `MatrixRepr` wrapper with LaTeX
rendering for use in marimo notebooks and Jupyter.

The canonical spinor-column API is `to_spinor_column` / `from_spinor_column`.
`to_spinor_matrix` / `from_spinor_matrix` are compatibility aliases.

## Two modes

| Mode | Matrix size | Entries | Works for | Roundtrips |
|---|---|---|---|---|
| `left-regular` | 2ⁿ × 2ⁿ | real | any symmetric Gram matrix | always |
| `compact` | 2^⌊n/2⌋ × 2^⌊n/2⌋ | complex | normalized orthogonal Cl(p,q) | only when the selected representation is injective |

## Quick start

```python
from galaga.facade import Algebra
from galaga_matrix import to_matrix, from_matrix, MatrixRepr

# Pauli matrices from Cl(3,0)
cl3 = Algebra(3)
e1, e2, e3 = cl3.basis_vectors()

mat = to_matrix(e1, mode="compact")   # returns MatrixRepr (2×2 Pauli σ₁)
mat @ mat                              # MatrixRepr: σ₁² = I
mat.inv()                              # MatrixRepr: σ₁⁻¹ = σ₁
mat.trace()                            # 0 (traceless)
mat.mv                                 # back to Multivector

# Named, tracked MV gets automatic ρ(name) symbolic name
e1, e2, e3 = cl3.basis_vectors(expr=True)
R = (e1 * e2).named("B", latex=r"\hat{B}")
M = to_matrix(R, mode="compact")
M.latex()                              # "\\rho(\\hat{B}) = \\begin{pmatrix}..."
M.expr.latex()                         # "\\rho(\\hat{B})"
M.symbolic_name.latex                  # "\\rho(\\hat{B})"

# from_matrix can infer algebra and mode from MatrixRepr
from_matrix(M)                         # MV named ρ⁻¹(ρ(B̂))
from_matrix(cl3, M.mat, mode="compact")  # unnamed MV (raw array)

# Dirac matrices from Cl(1,3)
sta = Algebra(1, 3)
g0 = sta.basis_vectors()[0]
to_matrix(g0, mode="compact")  # 4×4 Dirac γ⁰

# Left-regular works for everything, including PGA
pga = Algebra(2, 0, 1)
v = pga.basis_vectors()[0]
to_matrix(v)  # 8×8 real matrix

# It also works directly in a nonorthogonal basis
oblique = Algebra(gram=[[2.0, 0.5], [0.5, -1.0]])
x = oblique.multivector([1.0, 2.0, 3.0, 4.0])
from_matrix(to_matrix(x))  # exact coefficient roundtrip in the native basis
```

## Executable examples

The repository includes a short Marimo series using the Galaga 2 facade:

- [representations and round-trips](../../examples/matrix/representations_and_roundtrips.py);
- [Pauli and Dirac matrices](../../examples/matrix/pauli_and_dirac.py); and
- [spinor columns](../../examples/matrix/spinor_columns.py).

Each notebook is compiled, dependency-checked, and executed headlessly by the
example test ledger.

## MatrixRepr

`MatrixRepr` is a transparent numpy proxy that wraps a matrix with:

- **All arithmetic operations** — `@`, `+`, `-`, `*`, `/`, `**` return `MatrixRepr`
- **Linear algebra** — `.T`, `.H`, `.conj()`, `.trace()`, `.det()`, `.inv()`
- **Numpy interop** — `np.add(M, N)`, `np.conj(M)` etc. return `MatrixRepr` via `__array_ufunc__`
- **Symbolic naming** — `.name()` assigns an immutable, target-aware `symbolic_name`
- **Immutable provenance** — `.expr` records frozen matrix-domain operations; `.as_expression()` exposes an operand
- **Metadata propagation** — `algebra`, `mode`, `basis`, and `kind` pass through operations
- **Indexing** — `M[i,j]` for elements, `M[0:2, 0:2]` for submatrices
- **Rendering** — `.latex()`, `._repr_latex_()` for notebooks
- **Escape hatch** — `.mat` gives the raw numpy array
- **Roundtrip** — `.mv` converts back to a `Multivector` (requires `algebra=`)
- **Factories** — `MatrixRepr.identity(k)`, `MatrixRepr.zeros((m,n))`, `.kron(other)`

### Auto-naming

`to_matrix(named_mv)` names the result as `ρ(name)` and gives it a symbolic
representation-map expression. `from_matrix(named_matrix)` can infer the
algebra and mode from `MatrixRepr` and names the recovered MV as
`ρ⁻¹(name-or-expression)`. Raw arrays still need
`from_matrix(alg, array, mode=...)`. Unnamed inputs pass through without new
names. Quaternion-block mode uses `ρ_{\mathbb{H}}(name)`.

### Expression ownership

`galaga_matrix.expr` owns matrix multiplication, transpose, adjoint, inverse,
basis-change, Kronecker-product, representation-map, and spinor-column nodes.
They are frozen and their matrix leaves hold read-only NumPy snapshots.

Galaga's public expression tree remains a geometric-algebra operation tree.
When a facade value carries provenance, conversion wraps it in a matrix adapter
with the active presentation. Rendering continues to honor context-local
presentation overrides on the facade algebra. `galaga_matrix` does not import
`galaga.symbolic_core` or inspect private multivector fields. This keeps the
optional package independent without losing evaluable provenance.

Works in galaga_marimo t-strings:

```python
gm.md(t"""
The Pauli matrix: {to_matrix(e1, mode="compact"):block}
""")
```

## Named special cases

The compact representation produces the standard textbook matrices:

- **Cl(3,0)**: 2×2 Pauli matrices (σ₁, σ₂, σ₃)
- **Cl(0,3)**: 2×2 with iσ₁, iσ₂, iσ₃
- **Cl(1,3)**: 4×4 Dirac matrices (γ⁰, γ¹, γ², γ³) in the Dirac representation
- **Cl(3,1)**: 4×4 Dirac matrices in the mostly-plus convention

All other normalized, non-degenerate orthogonal signatures are handled by the
general periodicity recursion.

## Limitations

- **Degenerate algebras** (r > 0): only `left-regular` mode works. `compact` raises `NotImplementedError`.
- **General Gram matrices**: `left-regular` works in the stored basis and is
  selected automatically. Compact mode currently rejects nonorthogonal and
  non-normalized metrics until a validated basis transform is implemented.
- **Double algebras** (Cl(p,q) where (q−p) mod 8 ∈ {3, 7}): `to_matrix`
  compact works, but `from_matrix` compact raises if the selected compact
  representation is not injective. Use `left-regular` for exact inverse
  conversion. See [Double Clifford Algebras](docs/double-algebras.md).
- **Quaternion output**: `to_quaternion_matrix` and quaternion spinor conversions use explicit quaternion-block bases. They currently support Cl(0,2) and Cl(1,3), and reject double algebras such as Cl(0,3).
- **Spinor roundtrip**: spinor conversions are rank-checked for the actual reference-column map. Signatures whose even subalgebra is not injective under that map raise `TypeError`.
- **No caching**: blade matrices are rebuilt on every call. Fine for interactive use, not for hot loops.

## Architecture decisions

See [docs/adrs/](docs/adrs/README.md).

## Tests

```bash
PYTHONPATH=.:packages/galaga_matrix uv run pytest packages/galaga_matrix/tests/
```
