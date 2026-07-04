# galaga_matrix

Matrix representations for [galaga](../../packages/galaga) Clifford algebras.

> **Status**: published to PyPI alongside galaga. Released as part of the monorepo.

## What it does

Every multivector in a Clifford algebra can be represented as a matrix. This package provides `to_matrix` / `from_matrix` conversions, spinor-column conversions for supported even subalgebras, quaternion-block output for selected quaternionic signatures, and a `MatrixRepr` wrapper with LaTeX rendering for use in marimo notebooks and Jupyter.

The canonical spinor-column API is `to_spinor_column` / `from_spinor_column`.
`to_spinor_matrix` / `from_spinor_matrix` are compatibility aliases.

## Two modes

| Mode | Matrix size | Entries | Works for | Roundtrips |
|---|---|---|---|---|
| `left-regular` | 2ⁿ × 2ⁿ | real | any Cl(p,q,r) | always |
| `compact` | 2^⌊n/2⌋ × 2^⌊n/2⌋ | complex | non-degenerate Cl(p,q) | only when the selected representation is injective |

## Quick start

```python
from galaga import Algebra
from galaga_matrix import to_matrix, from_matrix, MatrixRepr

# Pauli matrices from Cl(3,0)
cl3 = Algebra(3)
e1, e2, e3 = cl3.basis_vectors()

mat = to_matrix(e1, mode="compact")   # returns MatrixRepr (2×2 Pauli σ₁)
mat.label                              # None (e1 is unnamed)
mat @ mat                              # MatrixRepr: σ₁² = I
mat.inv()                              # MatrixRepr: σ₁⁻¹ = σ₁
mat.trace()                            # 0 (traceless)
mat.mv                                 # back to Multivector

# Named MV gets automatic ρ(name) label
R = (e1 * e2).name(latex=r"\hat{B}")
M = to_matrix(R, mode="compact")      # M.label = "\\rho(\\hat{B})"
M.latex()                              # "\\rho(\\hat{B}) = \\begin{pmatrix}..."

# from_matrix accepts MatrixRepr or raw ndarray
from_matrix(cl3, M)                    # MV named ρ⁻¹(ρ(B̂))
from_matrix(cl3, M.mat, mode="compact")  # unnamed MV (raw array)

# Dirac matrices from Cl(1,3)
sta = Algebra(1, 3)
g0 = sta.basis_vectors()[0]
to_matrix(g0, mode="compact")  # 4×4 Dirac γ⁰

# Left-regular works for everything, including PGA
pga = Algebra(2, 0, 1)
v = pga.basis_vectors()[0]
to_matrix(v)  # 8×8 real matrix
```

## MatrixRepr

`MatrixRepr` is a transparent numpy proxy that wraps a matrix with:

- **All arithmetic operations** — `@`, `+`, `-`, `*`, `/`, `**` return `MatrixRepr`
- **Linear algebra** — `.T`, `.H`, `.conj()`, `.trace()`, `.det()`, `.inv()`
- **Numpy interop** — `np.add(M, N)`, `np.conj(M)` etc. return `MatrixRepr` via `__array_ufunc__`
- **Metadata propagation** — `algebra` and `mode` pass through operations; `label` does not
- **Indexing** — `M[i,j]` for elements, `M[0:2, 0:2]` for submatrices
- **Rendering** — `.latex()`, `._repr_latex_()` for notebooks
- **Escape hatch** — `.mat` gives the raw numpy array
- **Roundtrip** — `.mv` converts back to a `Multivector` (requires `algebra=`)
- **Factories** — `MatrixRepr.identity(k)`, `MatrixRepr.zeros((m,n))`, `.kron(other)`

### Auto-labeling

`to_matrix(named_mv)` labels the result as `ρ(name)`. `from_matrix(alg, labeled_matrix)`
names the recovered MV as `ρ⁻¹(label)`. Unnamed inputs pass through without labeling.

Works in galaga_marimo t-strings:

```python
gm.md(t"""
The Pauli matrix: {e1.pauli:block}
""")
```

## Named special cases

The compact representation produces the standard textbook matrices:

- **Cl(3,0)**: 2×2 Pauli matrices (σ₁, σ₂, σ₃)
- **Cl(0,3)**: 2×2 with iσ₁, iσ₂, iσ₃
- **Cl(1,3)**: 4×4 Dirac matrices (γ⁰, γ¹, γ², γ³) in the Dirac representation
- **Cl(3,1)**: 4×4 Dirac matrices in the mostly-plus convention

All other non-degenerate signatures are handled by the general periodicity recursion.

## Limitations

- **Degenerate algebras** (r > 0): only `left-regular` mode works. `compact` raises `NotImplementedError`.
- **Double algebras** (Cl(p,q) where (q−p) mod 8 ∈ {3, 7}): `to_matrix` compact works, but `from_matrix` compact raises if the selected compact representation is not injective. Use `left-regular` for exact inverse conversion. See [Double Clifford Algebras](docs/double-algebras.md).
- **Quaternion output**: `to_quaternion_matrix` and quaternion spinor conversions use explicit quaternion-block bases. They currently support Cl(0,2) and Cl(1,3), and reject double algebras such as Cl(0,3).
- **Spinor roundtrip**: spinor conversions are rank-checked for the actual reference-column map. Signatures whose even subalgebra is not injective under that map raise `TypeError`.
- **No caching**: blade matrices are rebuilt on every call. Fine for interactive use, not for hot loops.

## Architecture decisions

See [docs/adrs/](docs/adrs/README.md).

## Tests

```bash
PYTHONPATH=.:packages/galaga_matrix uv run pytest packages/galaga_matrix/tests/
```
