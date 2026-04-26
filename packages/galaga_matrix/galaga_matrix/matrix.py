"""Matrix representations for Clifford algebra multivectors.

Provides two representation modes:

- **left-regular**: 2ⁿ × 2ⁿ real matrix from the left multiplication map.
  Works for any Cl(p,q,r). Faithful and always roundtrips.

- **compact**: Minimal-dimension representation using the classification of
  real Clifford algebras. Produces complex matrices.

  Special cases with named basis matrices:
    - Cl(3,0), Cl(0,3): 2×2 complex — Pauli matrices
    - Cl(1,3), Cl(3,1): 4×4 complex — Dirac (gamma) matrices

  General case via the periodicity theorem for all other signatures.

  Note: for "double" algebras (Cl(p,q) ≅ A ⊕ A, i.e. (q-p) mod 8 ∈ {3,7}),
  the compact representation is an irreducible representation of one summand.
  ``to_matrix`` works but ``from_matrix`` may not roundtrip exactly.
"""

from __future__ import annotations

import numpy as np

from galaga import Algebra
from galaga.algebra import Multivector

# ── Left-regular representation ──


def _left_regular_matrix(alg: Algebra) -> np.ndarray:
    """Build the full left-regular representation matrices for all basis blades.

    Returns shape (2^n, 2^n, 2^n): L[k] is the matrix for basis blade k.
    L[k][i,j] = sign when e_k * e_j produces a component on e_i.
    """
    dim = alg.dim
    L = np.zeros((dim, dim, dim))
    for j in range(dim):
        for k in range(dim):
            idx = alg._mul_index[k, j]
            sgn = alg._mul_sign[k, j]
            L[k, idx, j] = sgn
    return L


def to_matrix(mv: Multivector, mode: str = "left-regular") -> np.ndarray:
    """Convert a multivector to its matrix representation.

    Args:
        mv: The multivector to convert.
        mode: ``"left-regular"`` (default) for the 2ⁿ×2ⁿ real representation,
              or ``"compact"`` for the minimal faithful representation.

    Returns:
        A 2D numpy array (real or complex depending on mode and algebra).
    """
    if mode == "left-regular":
        return _to_left_regular(mv)
    if mode == "compact":
        return _to_compact(mv)
    raise ValueError(f"Unknown mode {mode!r}; use 'left-regular' or 'compact'")


def from_matrix(alg: Algebra, mat: np.ndarray, mode: str = "left-regular") -> Multivector:
    """Recover a multivector from its matrix representation.

    Args:
        alg: The Clifford algebra.
        mat: The matrix (must match the expected shape for the mode).
        mode: ``"left-regular"`` or ``"compact"``.

    Returns:
        The corresponding multivector.
    """
    if mode == "left-regular":
        return _from_left_regular(alg, mat)
    if mode == "compact":
        return _from_compact(alg, mat)
    raise ValueError(f"Unknown mode {mode!r}; use 'left-regular' or 'compact'")


# ── Left-regular implementation ──


def _to_left_regular(mv: Multivector) -> np.ndarray:
    alg = mv.algebra
    dim = alg.dim
    mat = np.zeros((dim, dim))
    for k in np.nonzero(mv.data)[0]:
        coeff = mv.data[k]
        for j in range(dim):
            idx = alg._mul_index[k, j]
            sgn = alg._mul_sign[k, j]
            mat[idx, j] += coeff * sgn
    return mat


def _from_left_regular(alg: Algebra, mat: np.ndarray) -> Multivector:
    dim = alg.dim
    if mat.shape != (dim, dim):
        raise ValueError(f"Expected ({dim}, {dim}) matrix, got {mat.shape}")
    # The first column of L(M) is M * e_0 = M * 1 = M's coefficients
    data = mat[:, 0].copy()
    return Multivector(alg, data)


# ── Compact representation ──
#
# Real Clifford algebra classification (Atiyah-Bott-Shapiro):
#
#   s = (q - p) mod 8    Matrix algebra              Entry type
#   ──────────────────────────────────────────────────────────
#   0, 6                  M(2^(n/2), ℝ)              real
#   1, 5                  M(2^((n-1)/2), ℂ)          complex
#   2, 4                  M(2^((n-2)/2), ℍ)          quaternion
#   3                     M(k, ℍ) ⊕ M(k, ℍ)         quat+quat
#   7                     M(k, ℝ) ⊕ M(k, ℝ)         real+real
#
# For the compact representation we always embed into complex matrices:
#   - Real entries stay real (imaginary part zero)
#   - Complex entries are native
#   - Quaternionic entries are embedded as 2×2 complex blocks:
#       q = a + bi + cj + dk  →  [[a+bi, c+di], [-c+di, a-bi]]


def _classify(p: int, q: int) -> tuple[str, int]:
    """Classify Cl(p,q) and return (entry_type, matrix_dim).

    Uses s = (q - p) mod 8 (standard Atiyah-Bott-Shapiro convention).

    entry_type is one of: 'real', 'complex', 'quaternion',
    'real+real', 'quaternion+quaternion'.
    matrix_dim is the size of each matrix block.
    """
    n = p + q
    s = (q - p) % 8
    k = n // 2
    if s in (0, 6):
        return "real", 2**k
    if s in (1, 5):
        return "complex", 2 ** ((n - 1) // 2)
    if s in (2, 4):
        return "quaternion", 2 ** ((n - 2) // 2)
    if s == 3:
        return "quaternion+quaternion", 2 ** ((n - 3) // 2)
    # s == 7
    return "real+real", 2 ** ((n - 1) // 2)


def _quat_to_complex(a: float, b: float, c: float, d: float) -> np.ndarray:
    """Embed quaternion a + bi + cj + dk as a 2×2 complex matrix."""
    return np.array(
        [
            [a + b * 1j, c + d * 1j],
            [-c + d * 1j, a - b * 1j],
        ]
    )


def _complex_from_quat_block(block: np.ndarray) -> tuple[float, float, float, float]:
    """Extract quaternion components from a 2×2 complex block."""
    a = block[0, 0].real
    b = block[0, 0].imag
    c = block[0, 1].real
    d = block[0, 1].imag
    return a, b, c, d


# ── Pauli matrices for Cl(3,0) ──

_PAULI_1 = np.array([[0, 1], [1, 0]], dtype=complex)
_PAULI_2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
_PAULI_3 = np.array([[1, 0], [0, -1]], dtype=complex)
_I2 = np.eye(2, dtype=complex)


def _pauli_basis(p: int, q: int) -> list[np.ndarray]:
    """Return the 2×2 complex gamma matrices for Cl(3,0) or Cl(0,3).

    Cl(3,0): σ₁, σ₂, σ₃ (standard Pauli matrices, square to +I)
    Cl(0,3): iσ₁, iσ₂, iσ₃ (square to -I)
    """
    paulis = [_PAULI_1, _PAULI_2, _PAULI_3]
    if q == 3 and p == 0:
        return [1j * s for s in paulis]
    return paulis


# ── Dirac matrices for Cl(1,3) and Cl(3,1) ──

_I4 = np.eye(4, dtype=complex)


def _dirac_basis(p: int, q: int) -> list[np.ndarray]:
    """Return the 4×4 complex gamma matrices for Cl(1,3) or Cl(3,1).

    Cl(1,3) — Dirac representation (particle physics convention):
      γ⁰ = diag(I₂, -I₂),  γⁱ = [[0, σᵢ], [-σᵢ, 0]]
      γ⁰² = +I, γⁱ² = -I

    Cl(3,1) — mostly-plus convention:
      γⁱ = [[0, σᵢ], [σᵢ, 0]] for i=1,2,3,  γ⁰ = [[I₂, 0], [0, -I₂]] * i
      γⁱ² = +I, γ⁰² = -I
    """
    paulis = [_PAULI_1, _PAULI_2, _PAULI_3]
    z = np.zeros((2, 2), dtype=complex)

    if p == 1 and q == 3:
        # γ⁰ squares to +1 (timelike), γ¹²³ square to -1 (spacelike)
        g0 = np.block([[_I2, z], [z, -_I2]])
        gammas = [g0]
        for s in paulis:
            gammas.append(np.block([[z, s], [-s, z]]))
        return gammas

    # Cl(3,1): γ¹²³ square to +1, γ⁰ squares to -1
    gammas = []
    for s in paulis:
        gammas.append(np.block([[z, s], [s, z]]))
    g0 = np.block([[_I2, z], [z, -_I2]]) * 1j
    gammas.append(g0)
    return gammas


# ── General compact basis via recursion ──


def _general_compact_basis(p: int, q: int) -> list[np.ndarray]:
    """Build compact gamma matrices for arbitrary Cl(p,q).

    Uses the periodicity isomorphism:
      Cl(p+1, q+1) ≅ Cl(p, q) ⊗ M(2, ℝ)

    The new generators are:
      - Old generators γ_i lifted as γ_i ⊗ σ₃
      - New positive-square generator: I ⊗ σ₁  (squares to +I)
      - New negative-square generator: I ⊗ σ₂  (squares to -I, since σ₂ is anti-Hermitian-ish)

    Actually σ₂² = I too, so we use I ⊗ (iσ₂) for the negative-square generator.

    Signature ordering: galaga puts p positive values first, then q negative.
    So generators 0..p-1 square to +1, generators p..p+q-1 square to -1.

    Returns list of n matrices, one per basis vector, in signature order.
    """
    n = p + q
    if n == 0:
        return []

    # ── Base cases ──
    if p == 1 and q == 0:  # Cl(1,0) ≅ ℝ ⊕ ℝ
        return [np.array([[1, 0], [0, -1]], dtype=complex)]

    if p == 0 and q == 1:  # Cl(0,1) ≅ ℂ
        return [np.array([[1j]], dtype=complex)]

    if p == 2 and q == 0:  # Cl(2,0) ≅ M(2,ℝ)
        return [
            np.array([[1, 0], [0, -1]], dtype=complex),
            np.array([[0, 1], [1, 0]], dtype=complex),
        ]

    if p == 0 and q == 2:  # Cl(0,2) ≅ ℍ
        return [
            np.array([[1j, 0], [0, -1j]], dtype=complex),
            np.array([[0, 1], [-1, 0]], dtype=complex),
        ]

    if p == 1 and q == 1:  # Cl(1,1) ≅ M(2,ℝ)
        return [
            np.array([[1, 0], [0, -1]], dtype=complex),
            np.array([[0, 1], [-1, 0]], dtype=complex),
        ]

    # Named special cases
    if (p, q) == (3, 0) or (p, q) == (0, 3):
        return _pauli_basis(p, q)
    if (p, q) == (1, 3) or (p, q) == (3, 1):
        return _dirac_basis(p, q)

    # ── Recursion: Cl(p+1, q+1) ≅ Cl(p, q) ⊗ M(2, ℝ) ──
    # Reduce by removing one positive and one negative generator.
    if p >= 1 and q >= 1:
        sub = _general_compact_basis(p - 1, q - 1)
        return _tensor_step(sub, p - 1, q - 1, add_positive=True, add_negative=True)

    # Pure positive: Cl(p, 0) with p >= 3
    # Reduce to mixed case: build Cl(p-1, 1) generators (which works via
    # the mixed recursion), then multiply the last generator by i to flip
    # its square from -1 to +1.
    if q == 0 and p >= 3:
        mixed = _general_compact_basis(p - 1, 1)
        # mixed has p-1 positive generators then 1 negative generator
        # The last one squares to -I. Multiply by i: (iγ)² = -γ² = +I
        result = list(mixed[:-1])
        result.append(1j * mixed[-1])
        return result

    # Pure negative: Cl(0, q) with q >= 3
    # Build Cl(1, q-1), then multiply the first generator by i to flip
    # its square from +1 to -1.
    if p == 0 and q >= 3:
        mixed = _general_compact_basis(1, q - 1)
        # mixed has 1 positive generator then q-1 negative generators
        # The first one squares to +I. Multiply by i: (iγ)² = -γ² = -I
        result = [1j * mixed[0]]
        result.extend(mixed[1:])
        return result

    raise NotImplementedError(f"Cl({p},{q})")


def _tensor_step(
    sub_gammas: list[np.ndarray],
    sub_p: int,
    sub_q: int,
    *,
    add_positive: bool,
    add_negative: bool,
) -> list[np.ndarray]:
    """Lift sub-algebra generators and add new ones via ⊗ M(2,ℝ).

    Signature ordering: positive generators first, then negative.
    The new positive generator goes at position sub_p (end of positives),
    the new negative generator goes at the end.
    """
    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)

    if sub_gammas:
        sub_dim = sub_gammas[0].shape[0]
    else:
        sub_dim = 1
    I_sub = np.eye(sub_dim, dtype=complex)

    # Lift existing: γ_i ⊗ σ₃
    lifted = [np.kron(g, s3) for g in sub_gammas]

    # Split into positive and negative parts
    pos_gammas = lifted[:sub_p]
    neg_gammas = lifted[sub_p:]

    result = list(pos_gammas)
    if add_positive:
        # New positive-square generator: I ⊗ σ₁ (σ₁² = I)
        result.append(np.kron(I_sub, s1))
    result.extend(neg_gammas)
    if add_negative:
        # New negative-square generator: I ⊗ iσ₂ ((iσ₂)² = -I)
        is2 = np.array([[0, 1], [-1, 0]], dtype=complex)
        result.append(np.kron(I_sub, is2))

    return result


def compact_basis(alg: Algebra) -> list[np.ndarray]:
    """Return the compact gamma matrices for the algebra's generators.

    These are the minimal-dimension faithful matrix representation of the
    basis vectors. All higher blades are obtained as products of these.
    """
    p = sum(1 for s in alg.signature if s > 0)
    q = sum(1 for s in alg.signature if s < 0)
    r = sum(1 for s in alg.signature if s == 0)
    if r > 0:
        raise NotImplementedError(f"Compact representation not supported for degenerate algebras (r={r})")
    return _general_compact_basis(p, q)


def _build_compact_blade_matrices(alg: Algebra) -> np.ndarray:
    """Build compact matrices for ALL basis blades (not just vectors).

    Returns shape (2^n, k, k) where k is the compact matrix dimension.
    Index 0 is the identity (scalar blade).
    """
    gammas = compact_basis(alg)
    n = alg.n
    dim = alg.dim
    k = gammas[0].shape[0]
    dtype = gammas[0].dtype

    # blade_mats[bitmask] = matrix for that basis blade
    blade_mats = np.zeros((dim, k, k), dtype=dtype)
    blade_mats[0] = np.eye(k, dtype=dtype)  # scalar = identity

    # Vector matrices (single-bit bitmasks)
    for i in range(n):
        blade_mats[1 << i] = gammas[i]

    # Higher blades: product of constituent vectors in canonical order
    for bitmask in range(1, dim):
        bits = []
        for i in range(n):
            if bitmask & (1 << i):
                bits.append(i)
        if len(bits) <= 1:
            continue
        mat = blade_mats[1 << bits[0]].copy()
        for i in bits[1:]:
            mat = mat @ blade_mats[1 << i]
        blade_mats[bitmask] = mat

    return blade_mats


def _to_compact(mv: Multivector) -> np.ndarray:
    blade_mats = _build_compact_blade_matrices(mv.algebra)
    k = blade_mats.shape[1]
    result = np.zeros((k, k), dtype=blade_mats.dtype)
    for i in np.nonzero(mv.data)[0]:
        result += mv.data[i] * blade_mats[i]
    return result


def _from_compact(alg: Algebra, mat: np.ndarray) -> Multivector:
    blade_mats = _build_compact_blade_matrices(alg)
    dim = alg.dim
    k = blade_mats.shape[1]

    if mat.shape != (k, k):
        raise ValueError(f"Expected ({k}, {k}) matrix, got {mat.shape}")

    # The MV coefficients are real, but the matrices are complex.
    # Stack real and imaginary parts to get a real linear system.
    flat_basis = blade_mats.reshape(dim, k * k)  # (dim, k²) complex

    # A[j, i] = contribution of blade i to matrix entry j
    # Stack real and imag: A is (2k², dim), b is (2k²,)
    A = np.vstack([flat_basis.real.T, flat_basis.imag.T])  # (2k², dim)
    flat_mat = mat.reshape(k * k)
    b = np.concatenate([flat_mat.real, flat_mat.imag])  # (2k²,)
    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return Multivector(alg, coeffs)


# ── Quaternion matrix form ──


class Quat:
    """A quaternion a + bi + cj + dk with LaTeX rendering."""

    __slots__ = ("a", "b", "c", "d")

    def __init__(self, a: float = 0, b: float = 0, c: float = 0, d: float = 0):
        self.a, self.b, self.c, self.d = a, b, c, d

    def __repr__(self) -> str:
        parts = []
        if abs(self.a) > 1e-12:
            parts.append(f"{self.a:.4g}")
        for coeff, label in [(self.b, "i"), (self.c, "j"), (self.d, "k")]:
            if abs(coeff) < 1e-12:
                continue
            if abs(abs(coeff) - 1) < 1e-12:
                sign = "-" if coeff < 0 else ("+" if parts else "")
                parts.append(f"{sign}{label}")
            else:
                sign = "+" if coeff > 0 and parts else ""
                parts.append(f"{sign}{coeff:.4g}{label}")
        return "".join(parts) or "0"

    def latex(self) -> str:
        parts = []
        for coeff, label in [(self.a, ""), (self.b, "i"), (self.c, "j"), (self.d, "k")]:
            if abs(coeff) < 1e-12:
                continue
            if label and abs(abs(coeff) - 1) < 1e-12:
                sign = "-" if coeff < 0 else ("+" if parts else "")
                parts.append(f"{sign}{label}")
            else:
                if abs(coeff - round(coeff)) < 1e-12:
                    val = str(int(round(coeff)))
                else:
                    val = f"{coeff:.4g}"
                if parts and coeff > 0:
                    val = "+" + val
                parts.append(f"{val}{label}")
        return "".join(parts) or "0"


def _extract_quat(block: np.ndarray) -> Quat:
    """Extract a quaternion from a 2×2 complex block.

    Embedding convention: q = a + bi + cj + dk →
        [[a + bi,  c + di],
         [-c + di, a - bi]]
    """
    a = block[0, 0].real
    b = block[0, 0].imag
    c = block[0, 1].real
    d = block[0, 1].imag
    return Quat(a, b, c, d)


def to_quaternion_matrix(mv: Multivector) -> list[list[Quat]]:
    """Convert a multivector to its quaternion matrix form.

    Only works for algebras classified as quaternionic: (q-p) mod 8 ∈ {2, 4}.
    Returns a list-of-lists of Quat objects.

    For Cl(1,3) (STA): returns a 2×2 quaternion matrix.
    For Cl(0,2): returns a 1×1 quaternion matrix.
    """
    p = sum(1 for s in mv.algebra.signature if s > 0)
    q = sum(1 for s in mv.algebra.signature if s < 0)
    etype, qdim = _classify(p, q)
    if "quaternion" not in etype:
        raise TypeError(
            f"Cl({p},{q}) is type '{etype}', not quaternionic. Quaternion matrix form requires (q-p) mod 8 ∈ {{2, 4}}."
        )

    cmat = _to_compact(mv)
    # cmat is (2*qdim × 2*qdim) complex — read as (qdim × qdim) quaternion blocks
    rows = []
    for i in range(qdim):
        row = []
        for j in range(qdim):
            block = cmat[2 * i : 2 * i + 2, 2 * j : 2 * j + 2]
            row.append(_extract_quat(block))
        rows.append(row)
    return rows
