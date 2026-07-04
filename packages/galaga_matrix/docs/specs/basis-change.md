# Basis Change for Matrix Representations

## Overview

`MatrixRepr.to_basis(name)` transforms a matrix representation from one named
basis to another via similarity transform: M' = S M S⁻¹ (for operators) or
ψ' = S ψ (for spinor columns).

## Named Bases

### Dirac / Cl(1,3) bases

All apply to 4×4 compact matrices from Cl(1,3) or Cl(3,1).

| Name | Also called | Key property | γ⁰ | γ⁵ |
|------|-------------|--------------|-----|-----|
| `"dirac"` | standard, canonical | γ⁰ diagonal | diag(I₂, −I₂) | off-diagonal |
| `"weyl"` | chiral | γ⁵ diagonal, chirality manifest | [[0,I],[I,0]] | diag(−I₂, I₂) |
| `"majorana"` | — | all γ purely imaginary, spinors real | σ₂-based | σ₂-based |

### Pauli / Cl(3,0) bases

Only one standard basis exists for 2×2 Pauli matrices (σ₃ diagonal). No
basis change is offered for Cl(3,0) initially. Could later add:

| Name | Property |
|------|----------|
| `"pauli"` | standard (σ₃ diagonal) — identity transform |
| `"circular"` | σ₁ diagonal — rotates to circular polarisation basis |

## Transform Matrices

All transforms are unitary: S⁻¹ = S†.

### Dirac → Weyl

$$
S_{\text{weyl}} = \frac{1}{\sqrt{2}}
\begin{pmatrix} I_2 & -I_2 \\ I_2 & I_2 \end{pmatrix}
= \frac{1}{\sqrt{2}}(1 + \gamma^5 \gamma^0)
$$

### Dirac → Majorana

$$
S_{\text{maj}} = \frac{1}{\sqrt{2}}
\begin{pmatrix} I_2 & \sigma_2 \\ \sigma_2 & -I_2 \end{pmatrix}
$$

Note: $S_{\text{maj}}$ is self-adjoint ($S = S^\dagger$).

### Weyl → Majorana

Compose: $S_{\text{weyl→maj}} = S_{\text{maj}} \cdot S_{\text{weyl}}^{-1}$.
Or compute directly from the Weyl-basis γ matrices.

## API

### `MatrixRepr.to_basis(target: str) -> MatrixRepr`

```python
M = to_matrix(g0, mode="dirac")   # 4×4 in Dirac basis
M_weyl = M.to_basis("weyl")       # 4×4 in Weyl basis
M_maj = M.to_basis("majorana")    # 4×4 in Majorana basis
```

**Behaviour:**

1. Validate that the current matrix is 4×4 from a Cl(1,3) or Cl(3,1) algebra
   (or that mode is `"dirac"`, `"compact"` with appropriate algebra).
2. Determine the source basis from `self.basis` (default: `"dirac"`).
3. Look up the transform S from source → target.
4. Compute: `new_mat = S @ self.mat @ S.H` (for operators/full MVs).
5. Return new `MatrixRepr` with:
   - `mat = new_mat`
   - `basis = target` (new attribute)
   - `mode` unchanged (still `"compact"` or `"dirac"`)
   - `algebra` inherited
   - `label` updated if present: e.g., `ρ_{\text{weyl}}(ψ)`

### New attribute: `MatrixRepr.basis`

- Type: `str | None`
- Default: `None` (meaning "whatever the compact representation produces",
  which is `"dirac"` for Cl(1,3) and `"pauli"` for Cl(3,0))
- Set explicitly by `to_basis()` or by `to_matrix(mv, mode="dirac")` etc.

### `from_matrix` with basis

When converting back to a multivector, the basis must be accounted for.
`from_matrix` checks `MatrixRepr.basis`:

- If `basis` is `None` or `"dirac"`: use compact inverse directly.
- If `basis` is `"weyl"` or `"majorana"`: first transform back to Dirac
  basis (apply S⁻¹ M S), then use compact inverse.

This ensures roundtrip:
```python
from_matrix(to_matrix(v).to_basis("weyl"))  # == v
```

## Validation Rules

| Source mode/algebra | Allowed target bases |
|---------------------|---------------------|
| Cl(1,3) compact/dirac | `"dirac"`, `"weyl"`, `"majorana"` |
| Cl(3,1) compact/dirac | `"dirac"`, `"weyl"`, `"majorana"` |
| Cl(3,0) compact/pauli | `"pauli"` (no-op), later `"circular"` |
| Any other | `TypeError` |

## Error Cases

| Condition | Error |
|-----------|-------|
| Matrix not 4×4 for Dirac bases | `TypeError("to_basis('weyl') requires 4×4 Dirac matrix")` |
| Algebra not Cl(1,3) or Cl(3,1) | `TypeError("to_basis('weyl') requires Cl(1,3) or Cl(3,1)")` |
| Unknown basis name | `ValueError("Unknown basis 'foo'; use 'dirac', 'weyl', or 'majorana'")` |
| Basis already matches target | Return self (no-op, no copy) |

## Spinor Column Transforms

For spinor columns (from `to_spinor_column`), the transform is single-sided:

$$
\psi' = S \psi
$$

This is not handled by `MatrixRepr.to_basis()` since spinor columns are raw
ndarrays, not MatrixRepr. A future `to_spinor_column(mv, basis="weyl")` could
be added, or a standalone `change_spinor_basis(spinor, from_basis, to_basis)`.

## Storage of Transform Matrices

Store as module-level constants in `galaga_matrix/bases.py`:

```python
# bases.py
import numpy as np

I2 = np.eye(2, dtype=complex)
s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli σ₂

S_DIRAC_TO_WEYL = (1/np.sqrt(2)) * np.block([[I2, -I2], [I2, I2]])
S_DIRAC_TO_MAJORANA = (1/np.sqrt(2)) * np.block([[I2, s2], [s2, -I2]])

TRANSFORMS = {
    ("dirac", "weyl"): S_DIRAC_TO_WEYL,
    ("dirac", "majorana"): S_DIRAC_TO_MAJORANA,
    ("weyl", "dirac"): S_DIRAC_TO_WEYL.conj().T,
    ("majorana", "dirac"): S_DIRAC_TO_MAJORANA.conj().T,
    ("weyl", "majorana"): S_DIRAC_TO_MAJORANA @ S_DIRAC_TO_WEYL.conj().T,
    ("majorana", "weyl"): S_DIRAC_TO_WEYL @ S_DIRAC_TO_MAJORANA.conj().T,
}
```

## Verification Tests

For each basis, verify the Clifford relations hold:

```python
gammas_weyl = [to_matrix(gi, mode="dirac").to_basis("weyl") for gi in basis_vectors]
for i in range(4):
    for j in range(4):
        anticomm = gammas[i] @ gammas[j] + gammas[j] @ gammas[i]
        assert np.allclose(anticomm.mat, 2 * eta[i,j] * np.eye(4))
```

Additional checks:
- Weyl basis: γ⁵ is diagonal with entries (−1,−1,+1,+1)
- Majorana basis: all γ matrices are purely imaginary
- Roundtrip: `from_matrix(to_matrix(v).to_basis("weyl")) == v`
- `to_basis("dirac").to_basis("weyl").to_basis("dirac")` is identity
