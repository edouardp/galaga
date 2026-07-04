# Spinors as Matrix Columns: Pauli vs Dirac

## The "Square Root of a Vector" — Pauli Version

In Cl(3,0), the compact representation maps vectors to 2×2 Hermitian matrices
(Pauli matrices). A unit vector n̂ maps to a traceless Hermitian matrix:

$$
\hat{n} = n_1\sigma_1 + n_2\sigma_2 + n_3\sigma_3
$$

The key observation: the projector ½(I + n̂) is **rank 1** and factors as an
outer product:

$$
\frac{1}{2}(I + \hat{n}) = |\psi_n\rangle\langle\psi_n|
$$

The spinor $|\psi_n\rangle$ is literally the "square root" of the direction n̂
— its outer product with itself reconstructs the projector onto that direction.

For n̂ = e₃ (the z-axis):

$$
\frac{1}{2}(I + \sigma_3) = \frac{1}{2}\begin{pmatrix}2 & 0\\0 & 0\end{pmatrix}
= \begin{pmatrix}1\\0\end{pmatrix}\begin{pmatrix}1 & 0\end{pmatrix}
$$

The spinor (1, 0)ᵀ is "spin-up along z" — the square root of the z-direction.

### Why this works in 2×2

The Pauli idempotent ½(1 + σ₃) is **rank 1** over ℂ. A rank-1 matrix has
exactly one nonzero column (after projection), so extracting that column
gives a unique (up to phase) spinor.

### Rotors and spinors in Cl(3,0)

The even subalgebra Cl⁰(3,0) has 4 real dimensions: {1, e₁₂, e₁₃, e₂₃}.
A rotor R = a + be₁₂ + ce₁₃ + de₂₃ maps to a 2×2 **unitary** matrix.

When we apply this matrix to the reference spinor (1, 0)ᵀ, we get the
first column of the unitary matrix — a unit 2-spinor. This is exactly
what `to_spinor_column(R)` computes:

$$
|\psi\rangle = \rho(R) \cdot |{\uparrow}\rangle = \text{first column of } \rho(R)
$$

The spinor encodes where the rotor "points" the reference state.

**Dimension count:** 4 real (even subalgebra) = 2 complex (spinor column). ✓

## The Dirac Version — Two Pauli Stories Stacked

In Cl(1,3), the compact representation maps multivectors to 4×4 complex
matrices (Dirac matrices).

### The idempotent is rank 2, not rank 1

The idempotent ½(1 + γ⁰) in the Dirac basis is:

$$
\frac{1}{2}(I_4 + \gamma^0) = \frac{1}{2}\begin{pmatrix}
2 & 0 & 0 & 0\\
0 & 2 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0
\end{pmatrix} = \begin{pmatrix}
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0
\end{pmatrix}
$$

This is **rank 2** over ℂ — it projects onto a 2-dimensional subspace
(columns 0 and 1). A rank-2 projector cannot factor as a single outer
product |ψ⟩⟨ψ|.

### What `to_spinor_column` does

`to_spinor_column(R)` picks **one** column from this 2D projected subspace
(specifically column 0). The result is a 4-component complex column vector.

$$
|\psi\rangle = \rho(R) \cdot u, \quad u = (1, 0, 0, 0)^T
$$

This is not "half" of the information — it's **all** of it. The 8D even
subalgebra of Cl(1,3) maps bijectively onto one 4-complex spinor:

**Dimension count:** 8 real (even subalgebra) = 4 complex (Dirac spinor) = 8 real. ✓

The second column (column 1 of the projected space) is linearly dependent
on the first via the spinor system equations. You don't lose anything by
taking just one column.

### The two Weyl halves

A 4-component Dirac spinor secretly contains two 2-component Weyl spinors:

$$
|\psi\rangle_{\text{Dirac}} = \begin{pmatrix}\psi_L\\\psi_R\end{pmatrix}
$$

In the **Dirac basis**, these halves are mixed — both participate in encoding
the rotor. In the **Weyl basis**, they separate cleanly:

```python
ket = to_spinor_column(R)
ket_weyl = ket.to_basis("weyl")
psi_L = ket_weyl.mat[0:2]  # top 2 components = left-handed Weyl spinor
psi_R = ket_weyl.mat[2:4]  # bottom 2 components = right-handed Weyl spinor
```

Each Weyl spinor has 2 complex = 4 real degrees of freedom. Together: 8 real,
matching the even subalgebra.

### Physical meaning of the two halves

- **Pure spatial rotation** (e.g., exp(−θ/2 · e₁₂)): acts the same on both
  Weyl halves (both rotate by the same angle).
- **Lorentz boost** (e.g., exp(φ/2 · γ₀γ₁)): acts oppositely on the two halves
  (one contracts, the other expands). This is why boosts mix particle/antiparticle.
- **Parity** (spatial inversion): swaps the two halves (L↔R).

## Comparison Table

| Property | Pauli Cl(3,0) | Dirac Cl(1,3) |
|----------|---------------|---------------|
| Compact matrix size | 2×2 | 4×4 |
| Idempotent rank | 1 | 2 |
| Spinor components | 2 complex | 4 complex |
| Even subalgebra dim | 4 real | 8 real |
| Spinor real d.o.f. | 4 | 8 |
| Roundtrips? | ✓ (4 = 4) | ✓ (8 = 8) |
| "Square root" picture | Clean: ½(I+n̂) = \|ψ⟩⟨ψ\| | Needs projector: rank-2 ideal |
| Weyl decomposition | N/A (already minimal) | Top/bottom halves in Weyl basis |
| Basis change | None standard | Dirac / Weyl / Majorana |

## In Code

```python
from galaga import Algebra, exp
from galaga_matrix import to_matrix, to_spinor_column, from_spinor_column

# === Pauli (Cl(3,0)) ===
alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()

R = exp(-0.3 * (e1 * e2))          # Rotor: 3D rotation
ket = to_spinor_column(R)           # 2×1 Pauli spinor
# ket.mat ≈ [[cos(0.3) - i sin(0.3)], [0]]  (rotation about z)

# The "square root" picture:
n = e3
M_n = to_matrix(n)                  # σ₃ = diag(1, -1)
proj = (MatrixRepr.identity(2) + M_n) * 0.5  # ½(I + σ₃) = [[1,0],[0,0]]
# proj is rank 1: its nonzero column IS the spin-up spinor (1,0)ᵀ

# === Dirac (Cl(1,3)) ===
sta = Algebra(1, 3)
g = sta.basis_vectors()

R_sta = exp(-0.3 * (g[0] * g[1]))   # Boost in γ₀γ₁ plane
ket_sta = to_spinor_column(R_sta)    # 4×1 Dirac spinor

# See the Weyl decomposition:
ket_weyl = ket_sta.to_basis("weyl")
psi_L = ket_weyl.mat[0:2]           # Left-handed Weyl spinor
psi_R = ket_weyl.mat[2:4]           # Right-handed Weyl spinor

# Roundtrip works from any basis:
from_spinor_column(ket_sta)                    # recovers R_sta
from_spinor_column(ket_sta.to_basis("weyl"))   # also recovers R_sta
```

## Summary

- **Pauli**: The spinor IS the square root of a direction. One column captures
  everything. The projector ½(I + n̂) is rank 1 — factors cleanly.
- **Dirac**: The spinor encodes a full Lorentz transformation (rotation + boost).
  One 4-column captures everything (8 real d.o.f.). The idempotent is rank 2 — no
  clean single outer product. But the two Weyl halves inside the 4-spinor each
  behave like a "Pauli spinor" for their respective chirality sector.
