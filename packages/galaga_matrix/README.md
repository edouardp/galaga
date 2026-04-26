# galaga_matrix

Matrix representations for [galaga](../../packages/galaga) Clifford algebras.

> **Status**: experimental, not published. Lives in the monorepo but is not a workspace member or released package.

## What it does

Every multivector in a Clifford algebra can be represented as a matrix. This package provides `to_matrix` / `from_matrix` conversions and a `MatrixRepr` wrapper with LaTeX rendering for use in marimo notebooks and Jupyter.

## Two modes

| Mode | Matrix size | Entries | Works for | Roundtrips |
|---|---|---|---|---|
| `left-regular` | 2ⁿ × 2ⁿ | real | any Cl(p,q,r) | always |
| `compact` | 2^⌊n/2⌋ × 2^⌊n/2⌋ | complex | non-degenerate Cl(p,q) | simple algebras only |

## Quick start

```python
from galaga import Algebra
from galaga_matrix import to_matrix, from_matrix, MatrixRepr

# Pauli matrices from Cl(3,0)
cl3 = Algebra(3)
e1, e2, e3 = cl3.basis_vectors()

mat = to_matrix(e1, mode="compact")   # 2×2 Pauli σ₁
mr = MatrixRepr(mat, label=r"\sigma_1", algebra=cl3, mode="compact")
mr.latex()       # raw LaTeX
mr._repr_latex_()  # for Jupyter
mr.mv            # back to Multivector

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

`MatrixRepr` wraps a numpy matrix with:

- `.latex(wrap=None|"$"|"$$")` — raw LaTeX, inline, or display mode
- `._repr_latex_()` — Jupyter rendering
- `.__array__()` — seamless use with `np.array()`, `np.trace()`, `np.linalg.det()`, etc.
- `.mv` — convert back to a galaga `Multivector` (requires `algebra=` at construction)
- `.mat` — the underlying numpy array

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
- **Double algebras** (Cl(p,q) where (q−p) mod 8 ∈ {3, 7}): `to_matrix` compact works, but `from_matrix` compact is lossy — the representation maps two distinct multivectors to the same matrix.
- **No caching**: blade matrices are rebuilt on every call. Fine for interactive use, not for hot loops.

## Architecture decisions

See [docs/adrs/](docs/adrs/README.md).

## Tests

```bash
PYTHONPATH=packages/galaga_matrix pytest packages/galaga_matrix/tests/
```
