# SPEC: Basis Change for Dirac Matrix Representations

## Status

Accepted — implemented.

## Problem

The compact matrix representation for Cl(1,3) and Cl(3,1) produces γ matrices
in the Dirac (standard) basis. Physics uses several other named bases — Weyl
(chiral) and Majorana — which are related by unitary similarity transforms.

Users working with the Weyl basis (where γ⁵ is diagonal and chiral projections
are trivial) or the Majorana basis (where all γ matrices are purely imaginary
and spinors can be real) currently have no way to convert within galaga_matrix.

## Rules

### Rule 1: `MatrixRepr.to_basis(target)` method

Transforms the matrix to a named basis via similarity: M' = S M S†.
Returns a new `MatrixRepr` with the transformed data.

| Source basis | Target       | Transform S                    |
| ------------ | ------------ | ------------------------------ |
| `"dirac"`    | `"weyl"`     | (1/√2) [[I₂, −I₂], [I₂, I₂]]   |
| `"dirac"`    | `"majorana"` | (1/√2) [[I₂, σ₂], [σ₂, −I₂]]   |
| `"weyl"`     | `"dirac"`    | S_weyl†                        |
| `"weyl"`     | `"majorana"` | S_maj · S_weyl†                |
| `"majorana"` | `"dirac"`    | S_maj† (= S_maj, self-adjoint) |
| `"majorana"` | `"weyl"`     | S_weyl · S_maj†                |

### Rule 2: `.basis` attribute

`MatrixRepr` gains a `basis` attribute:

| Value        | Meaning                                    |
| ------------ | ------------------------------------------ |
| `None`       | Unspecified (default for all current code) |
| `"dirac"`    | Dirac/standard basis                       |
| `"weyl"`     | Weyl/chiral basis                          |
| `"majorana"` | Majorana basis                             |
| `"pauli"`    | Standard Pauli (Cl(3,0), no-op)            |

`to_matrix(mv, mode="dirac")` sets `basis="dirac"`.
`to_matrix(mv, mode="compact")` for Cl(1,3)/Cl(3,1) sets `basis="dirac"`.
`to_basis(target)` sets `basis=target` on the result.

### Rule 3: Default source basis

When `.basis` is `None`, it is treated as `"dirac"` for 4×4 matrices from
Cl(1,3)/Cl(3,1), and `"pauli"` for 2×2 matrices from Cl(3,0)/Cl(0,3).

### Rule 4: No-op when source == target

`M.to_basis("dirac")` on a matrix already in Dirac basis returns `self`
(no copy, no computation).

### Rule 5: Validation

| Condition                      | Error                                                             |
| ------------------------------ | ----------------------------------------------------------------- |
| Matrix not 4×4                 | `TypeError("requires 4×4 Dirac matrix")`                          |
| Algebra not Cl(1,3) or Cl(3,1) | `TypeError("requires Cl(1,3) or Cl(3,1)")`                        |
| Unknown basis name             | `ValueError("Unknown basis; use 'dirac', 'weyl', or 'majorana'")` |

### Rule 6: `from_matrix` with non-default basis

When a `MatrixRepr` has `basis` set to `"weyl"` or `"majorana"`,
`from_matrix` transforms back to Dirac basis before applying the compact
inverse. This ensures roundtrip correctness:

```python
from_matrix(to_matrix(v, mode="dirac").to_basis("weyl"))  # == v
```

### Rule 7: Symbolic expression propagation

If the source is symbolic, the result carries a `MatrixBasisChange` expression.
Display names are not copied blindly; callers can name the derived matrix
explicitly when useful:

```python
W = M.to_basis("weyl").name(latex=r"\rho^{\mathrm{Weyl}}(v)")
```

### Rule 8: Metadata propagation

`algebra` and `mode` are inherited. `basis` is set to target. `kind` is
preserved.

## Examples

```python
sta = Algebra(1, 3)
g0, g1, g2, g3 = sta.basis_vectors()

# Convert γ⁰ to Weyl basis
M = to_matrix(g0, mode="dirac")        # Dirac basis: diag(I₂, −I₂)
W = M.to_basis("weyl")                 # Weyl basis: [[0,I],[I,0]]
assert W.basis == "weyl"
assert np.allclose(W.mat, [[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])

# γ⁵ is diagonal in Weyl basis
g5 = to_matrix(1j * g0 * g1 * g2 * g3, mode="dirac")
g5_weyl = g5.to_basis("weyl")
assert np.allclose(np.diag(g5_weyl.mat), [-1, -1, 1, 1])

# Majorana basis: all γ purely imaginary
M_maj = M.to_basis("majorana")
assert np.allclose(M_maj.mat.real, 0)  # (for spatial γ)
# Note: γ⁰ in Majorana basis is real, spatial γ are imaginary

# Roundtrip
v = g0 + 0.5 * g1
assert np.allclose(from_matrix(to_matrix(v).to_basis("weyl")).data, v.data)

# Chain
assert np.allclose(
    M.to_basis("weyl").to_basis("majorana").to_basis("dirac").mat,
    M.mat,
    atol=1e-12
)
```

## Edge Cases

- `to_basis("dirac")` on a Dirac-basis matrix: returns self (no-op).
- `to_basis("weyl")` on a matrix with no algebra: raises `TypeError`.
- `to_basis("weyl")` on a `"pauli"` mode 2×2 matrix: raises `TypeError`.
- Quaternion MatrixRepr: raises `TypeError`.

## Impact

- New file: `galaga_matrix/bases.py` — stores transform matrices as constants.
- New attribute: `MatrixRepr.basis` (str | None).
- New method: `MatrixRepr.to_basis(target: str) -> MatrixRepr`.
- Modified: `from_matrix` — checks `.basis`, transforms back if non-default.
- Modified: `to_matrix` — sets `.basis` for Dirac/Pauli modes.
