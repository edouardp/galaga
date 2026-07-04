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
  the compact representation may be an irreducible representation of one
  summand. ``to_matrix`` works, but ``from_matrix`` raises when the selected
  representation is not injective.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from galaga import Algebra
from galaga.algebra import Multivector

if TYPE_CHECKING:
    from .repr import MatrixRepr

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


def to_matrix(mv: Multivector, mode: str = "left-regular") -> MatrixRepr:
    """Convert a multivector to its matrix representation.

    Args:
        mv: The multivector to convert.
        mode: ``"left-regular"`` (default) for the 2ⁿ×2ⁿ real representation,
              or ``"compact"`` for the smaller classification-based representation.

    Returns:
        A MatrixRepr wrapping the matrix, with algebra and mode metadata set.
        If the multivector has a name, the label is set to ``\\rho(name)``.
    """
    from .repr import MatrixRepr

    if mode == "left-regular":
        mat = _to_left_regular(mv)
    elif mode == "compact":
        mat = _to_compact(mv)
    else:
        raise ValueError(f"Unknown mode {mode!r}; use 'left-regular' or 'compact'")

    label = None
    mv_name = getattr(mv, "_name_latex", None) or getattr(mv, "_name", None)
    if mv_name:
        label = rf"\rho({mv_name})"

    return MatrixRepr(mat, label=label, algebra=mv.algebra, mode=mode)


def from_matrix(alg: Algebra, mat, mode: str = "left-regular") -> Multivector:
    """Recover a multivector from its matrix representation.

    Args:
        alg: The Clifford algebra.
        mat: A MatrixRepr or numpy array (must match the expected shape for the mode).
        mode: ``"left-regular"`` or ``"compact"``. If *mat* is a MatrixRepr with
              a mode already set, that mode is used and this argument is ignored.

    Returns:
        The corresponding multivector. If the input MatrixRepr has a label,
        the multivector is named ``\\rho^{-1}(label)``.
    """
    from .repr import MatrixRepr

    mat_label = None
    if isinstance(mat, MatrixRepr):
        if mat.mode and mat.mode != "quaternion":
            mode = mat.mode
        mat_label = mat.label
        mat = mat.mat

    if mode == "left-regular":
        mv = _from_left_regular(alg, mat)
    elif mode == "compact":
        mv = _from_compact(alg, mat)
    else:
        raise ValueError(f"Unknown mode {mode!r}; use 'left-regular' or 'compact'")

    if mat_label:
        mv.name(latex=rf"\rho^{{-1}}({mat_label})")

    return mv


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
    """Return compact gamma matrices for the algebra's generators.

    For simple Clifford algebras this is faithful. For double algebras
    ((q-p) mod 8 in {3, 7}) this may be one irreducible summand and therefore
    may not be faithful on the full algebra. Strict inverse APIs check rank
    before reconstructing coefficients.
    """
    p = sum(1 for s in alg.signature if s > 0)
    q = sum(1 for s in alg.signature if s < 0)
    r = sum(1 for s in alg.signature if s == 0)
    if r > 0:
        raise NotImplementedError(f"Compact representation not supported for degenerate algebras (r={r})")
    return _general_compact_basis(p, q)


def _build_blade_matrices_from_gammas(alg: Algebra, gammas: list[np.ndarray]) -> np.ndarray:
    """Build matrices for all basis blades from vector gamma matrices.

    Returns shape (2^n, k, k) where k is the compact matrix dimension.
    Index 0 is the identity (scalar blade).
    """
    n = alg.n
    dim = alg.dim
    if n == 0:
        return np.ones((1, 1, 1), dtype=complex)

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


def _build_compact_blade_matrices(alg: Algebra) -> np.ndarray:
    """Build compact matrices for all basis blades."""
    return _build_blade_matrices_from_gammas(alg, compact_basis(alg))


def _to_matrix_from_blade_mats(mv: Multivector, blade_mats: np.ndarray) -> np.ndarray:
    k = blade_mats.shape[1]
    result = np.zeros((k, k), dtype=blade_mats.dtype)
    for i in np.nonzero(mv.data)[0]:
        result += mv.data[i] * blade_mats[i]
    return result


def _to_compact(mv: Multivector) -> np.ndarray:
    return _to_matrix_from_blade_mats(mv, _build_compact_blade_matrices(mv.algebra))


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
    coeffs, _, rank, _ = np.linalg.lstsq(A, b, rcond=None)
    if rank < dim:
        raise TypeError(
            "Compact representation is not injective for this algebra; cannot recover a unique multivector."
        )

    err = np.linalg.norm(A @ coeffs - b)
    if err > 1e-9:
        raise ValueError("Matrix is not in the image of this Clifford representation.")

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quat):
            return NotImplemented
        return (
            abs(self.a - other.a) < 1e-12
            and abs(self.b - other.b) < 1e-12
            and abs(self.c - other.c) < 1e-12
            and abs(self.d - other.d) < 1e-12
        )

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


def _signature_pq(alg: Algebra) -> tuple[int, int]:
    return (
        sum(1 for s in alg.signature if s > 0),
        sum(1 for s in alg.signature if s < 0),
    )


def _quaternion_block_basis(alg: Algebra) -> list[np.ndarray]:
    """Return gamma matrices arranged as 2x2 complex quaternion blocks.

    This is intentionally separate from compact_basis: the standard Dirac
    matrices used there for Cl(1,3) are not in this block convention.
    """
    p, q = _signature_pq(alg)
    etype, _ = _classify(p, q)
    if etype != "quaternion":
        if "quaternion" in etype:
            raise TypeError(
                f"Cl({p},{q}) is type '{etype}', not a single quaternionic matrix algebra. "
                "Quaternion form requires a simple quaternionic algebra."
            )
        raise TypeError(
            f"Cl({p},{q}) is type '{etype}', not quaternionic. Quaternion form requires a simple quaternionic algebra."
        )

    if (p, q) == (0, 2):
        return compact_basis(alg)

    if (p, q) == (1, 3):
        z = np.zeros((2, 2), dtype=complex)
        one = _quat_to_complex(1, 0, 0, 0)
        minus_one = _quat_to_complex(-1, 0, 0, 0)
        qi = _quat_to_complex(0, 1, 0, 0)
        qj = _quat_to_complex(0, 0, 1, 0)
        qk = _quat_to_complex(0, 0, 0, 1)

        g0 = np.block([[one, z], [z, minus_one]])
        return [
            g0,
            np.block([[z, qi], [qi, z]]),
            np.block([[z, qj], [qj, z]]),
            np.block([[z, qk], [qk, z]]),
        ]

    raise TypeError(f"Quaternion block representation is not implemented for Cl({p},{q}).")


def _build_quaternion_block_blade_matrices(alg: Algebra) -> np.ndarray:
    return _build_blade_matrices_from_gammas(alg, _quaternion_block_basis(alg))


def _to_quaternion_block_complex(mv: Multivector) -> np.ndarray:
    return _to_matrix_from_blade_mats(mv, _build_quaternion_block_blade_matrices(mv.algebra))


# ── Spinor (column vector) representation ──


def _choose_idempotent(gammas: list[np.ndarray], k: int) -> np.ndarray:
    """Choose an idempotent p = ½(I + γ) where γ is diagonal and γ² = I.

    Prefers the first basis vector whose compact matrix is diagonal and
    squares to +I. For Cl(3,0) this gives σ₃, yielding p = diag(1,0).
    For Cl(1,3) this gives γ⁰, yielding p = diag(1,1,0,0).
    """
    I_k = np.eye(k, dtype=complex)

    for g in gammas:
        if np.allclose(g, np.diag(np.diag(g))) and np.allclose(g @ g, I_k):
            return 0.5 * (I_k + g)

    # Fallback: use first gamma that squares to +I (may not be diagonal)
    for g in gammas:
        if np.allclose(g @ g, I_k):
            return 0.5 * (I_k + g)

    # Last resort: project onto first column
    p = np.zeros((k, k), dtype=complex)
    p[0, 0] = 1.0
    return p


def _even_indices(dim: int) -> np.ndarray:
    return np.array([i for i in range(dim) if i.bit_count() % 2 == 0])


def _spinor_reference_vector_from_gammas(gammas: list[np.ndarray]) -> np.ndarray:
    if not gammas:
        return np.ones((1, 1), dtype=complex)

    k = gammas[0].shape[0]
    p = _choose_idempotent(gammas, k)
    norms = np.linalg.norm(p, axis=0)
    col = int(np.argmax(norms))
    if norms[col] < 1e-14:
        u = np.zeros((k, 1), dtype=complex)
        u[0, 0] = 1.0
        return u
    return p[:, col : col + 1]


def _spinor_reference_vector(alg: Algebra) -> np.ndarray:
    return _spinor_reference_vector_from_gammas(compact_basis(alg))


def _spinor_system_matrix_from_blade_mats(
    alg: Algebra,
    blade_mats: np.ndarray,
    reference: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    even_indices = _even_indices(alg.dim)
    cols = (blade_mats[even_indices] @ reference)[:, :, 0]  # (n_even, k)
    A_complex = cols.T  # (k, n_even)
    A_real = np.vstack([A_complex.real, A_complex.imag])
    return A_real, even_indices


def _spinor_system_matrix(alg: Algebra) -> tuple[np.ndarray, np.ndarray]:
    return _spinor_system_matrix_from_blade_mats(
        alg,
        _build_compact_blade_matrices(alg),
        _spinor_reference_vector(alg),
    )


def _quaternion_spinor_system_matrix(alg: Algebra) -> tuple[np.ndarray, np.ndarray]:
    gammas = _quaternion_block_basis(alg)
    return _spinor_system_matrix_from_blade_mats(
        alg,
        _build_blade_matrices_from_gammas(alg, gammas),
        _spinor_reference_vector_from_gammas(gammas),
    )


def _spinor_system_is_full_rank(A: np.ndarray, even_indices: np.ndarray) -> bool:
    return bool(np.linalg.matrix_rank(A, tol=1e-10) == len(even_indices))


def _unsupported_spinor_error(alg: Algebra) -> TypeError:
    p, q = _signature_pq(alg)
    etype, _ = _classify(p, q)
    return TypeError(
        f"Cl({p},{q}) (type '{etype}') does not support faithful spinor roundtrip "
        "with the selected compact representation and reference spinor. "
        "Use to_matrix(mv, mode='compact') for the full matrix representation."
    )


def _spinor_roundtrip_possible(alg: Algebra) -> bool:
    """Check if even-grade MVs can be faithfully represented as spinor columns.

    This is a rank check for the actual reference-vector map, not a dimension
    count inferred from the algebra classification.
    """
    try:
        A, even_indices = _spinor_system_matrix(alg)
    except NotImplementedError:
        return False
    return _spinor_system_is_full_rank(A, even_indices)


def to_spinor_column(mv: Multivector) -> np.ndarray:
    """Convert an even-grade multivector to its spinor column vector.

    For Cl(3,0): returns a 2×1 complex column (Pauli spinor).
    For Cl(1,3): returns a 4×1 complex column (Dirac spinor).

    The spinor is the action of the compact matrix representation on a fixed
    reference column u: spinor(ψ) = ρ(ψ)u. Faithful roundtrip is guaranteed only
    when the resulting real even-blade system is full rank.

    Args:
        mv: An even-grade multivector.

    Returns:
        A (k, 1) complex numpy array — the spinor column vector.

    Raises:
        ValueError: If the multivector has odd-grade components.
        TypeError: If the algebra does not support faithful spinor roundtrip.
    """
    from galaga import is_even

    if not is_even(mv):
        raise ValueError(
            "to_spinor_column requires an even-grade multivector. "
            "Use galaga.even_grades(mv) to project to the even part first."
        )

    if not _spinor_roundtrip_possible(mv.algebra):
        raise _unsupported_spinor_error(mv.algebra)

    return _to_compact(mv) @ _spinor_reference_vector(mv.algebra)


def to_spinor_matrix(mv: Multivector) -> np.ndarray:
    """Compatibility alias for to_spinor_column."""
    return to_spinor_column(mv)


def _solve_spinor_system(
    alg: Algebra,
    spinor: np.ndarray,
    A: np.ndarray,
    even_indices: np.ndarray,
) -> Multivector:
    if not _spinor_system_is_full_rank(A, even_indices):
        raise _unsupported_spinor_error(alg)

    k = A.shape[0] // 2
    spinor = np.asarray(spinor, dtype=complex)
    if spinor.shape == (k,):
        spinor = spinor.reshape(k, 1)
    if spinor.shape != (k, 1):
        raise ValueError(f"Expected ({k}, 1) spinor, got {spinor.shape}")

    b = np.concatenate([spinor[:, 0].real, spinor[:, 0].imag])
    coeffs_even, _, rank, _ = np.linalg.lstsq(A, b, rcond=None)
    if rank != len(even_indices):
        raise TypeError("Selected spinor map is rank-deficient.")

    err = np.linalg.norm(A @ coeffs_even - b)
    if err > 1e-9:
        raise ValueError("Spinor column is not in the image of this Clifford spinor representation.")

    data = np.zeros(alg.dim)
    data[even_indices] = coeffs_even
    return Multivector(alg, data)


def from_spinor_column(alg: Algebra, spinor: np.ndarray) -> Multivector:
    """Recover an even-grade multivector from a spinor column vector.

    The inverse of to_spinor_column. Given a (k,1) column vector,
    reconstructs the even MV ψ such that to_spinor_column(ψ) ≈ spinor.

    Args:
        alg: The Clifford algebra.
        spinor: A (k, 1) or (k,) complex array.

    Returns:
        The even-grade multivector.

    Raises:
        ValueError: If the spinor has the wrong shape.
        TypeError: If the algebra does not support faithful spinor roundtrip.
    """
    try:
        A, even_indices = _spinor_system_matrix(alg)
    except NotImplementedError as exc:
        raise _unsupported_spinor_error(alg) from exc
    return _solve_spinor_system(alg, spinor, A, even_indices)


def from_spinor_matrix(alg: Algebra, spinor: np.ndarray) -> Multivector:
    """Compatibility alias for from_spinor_column."""
    return from_spinor_column(alg, spinor)


# ── Quaternion spinor (column vector) representation ──


def _quat_from_column_pair(z0: complex, z1: complex) -> Quat:
    """Extract a quaternion from a pair of complex numbers.

    Uses the convention that the first column of the 2×2 complex embedding
    of q = a + bi + cj + dk is:
        [[a + bi], [-c + di]]

    So given z0 = a + bi and z1 = -c + di:
        a = Re(z0), b = Im(z0), c = -Re(z1), d = Im(z1)
    """
    a = z0.real
    b = z0.imag
    c = -z1.real
    d = z1.imag
    return Quat(a, b, c, d)


def _column_pair_from_quat(q: Quat) -> tuple[complex, complex]:
    """Convert a quaternion to its column-pair complex representation.

    Inverse of _quat_from_column_pair.
    q = a + bi + cj + dk → z0 = a + bi, z1 = -c + di
    """
    z0 = q.a + q.b * 1j
    z1 = -q.c + q.d * 1j
    return z0, z1


def to_spinor_quaternion(mv: Multivector) -> list[Quat]:
    """Convert an even-grade multivector to a quaternionic spinor column.

    Only works for supported simple quaternionic algebras with an explicit
    quaternion-block basis. Currently this covers Cl(0,2) and Cl(1,3).

    The quaternionic spinor is obtained by:
    1. Building a quaternion-block matrix representation.
    2. Applying it to the fixed reference spinor column.
    3. Reading consecutive pairs of complex entries as quaternion components.

    Args:
        mv: An even-grade multivector in a quaternionic algebra.

    Returns:
        A list of Quat objects — the quaternionic spinor column.

    Raises:
        ValueError: If the multivector has odd-grade components.
        TypeError: If the algebra is not supported as a simple quaternionic
            block representation.
    """
    from galaga import is_even

    if not is_even(mv):
        raise ValueError(
            "to_spinor_quaternion requires an even-grade multivector. "
            "Use galaga.even_grades(mv) to project to the even part first."
        )

    p, q = _signature_pq(mv.algebra)
    _, qdim = _classify(p, q)
    gammas = _quaternion_block_basis(mv.algebra)
    A, even_indices = _quaternion_spinor_system_matrix(mv.algebra)
    if not _spinor_system_is_full_rank(A, even_indices):
        raise TypeError(
            f"Cl({p},{q}) does not support faithful quaternionic spinor roundtrip "
            "with the selected quaternion-block representation."
        )

    spinor = _to_quaternion_block_complex(mv) @ _spinor_reference_vector_from_gammas(gammas)

    # Read pairs of complex entries as quaternion components
    result = []
    for i in range(qdim):
        z0 = spinor[2 * i, 0]
        z1 = spinor[2 * i + 1, 0]
        result.append(_quat_from_column_pair(z0, z1))
    return result


def from_spinor_quaternion(alg: Algebra, spinor: list[Quat]) -> Multivector:
    """Recover an even-grade multivector from a quaternionic spinor column.

    The inverse of to_spinor_quaternion for the same quaternion-block basis.

    Args:
        alg: The Clifford algebra (must be quaternionic).
        spinor: A list of Quat objects (length = qdim).

    Returns:
        The even-grade multivector.

    Raises:
        TypeError: If the algebra is not supported as a simple quaternionic
            block representation.
        ValueError: If the spinor has the wrong length.
    """
    p, q = _signature_pq(alg)
    _, qdim = _classify(p, q)
    _quaternion_block_basis(alg)

    if len(spinor) != qdim:
        raise ValueError(f"Expected {qdim} quaternion entries, got {len(spinor)}")

    # Convert quaternion list back to complex column vector
    complex_col = np.zeros((2 * qdim, 1), dtype=complex)
    for i, qval in enumerate(spinor):
        if not isinstance(qval, Quat):
            raise TypeError(f"Expected Quat entries, got {type(qval).__name__} at index {i}")
        z0, z1 = _column_pair_from_quat(qval)
        complex_col[2 * i, 0] = z0
        complex_col[2 * i + 1, 0] = z1

    A, even_indices = _quaternion_spinor_system_matrix(alg)
    return _solve_spinor_system(alg, complex_col, A, even_indices)


# ── Quaternion matrix form ──


def to_quaternion_matrix(mv: Multivector) -> list[list[Quat]]:
    """Convert a multivector to its quaternion matrix form.

    Only works for supported simple quaternionic algebras with an explicit
    quaternion-block basis. Currently this covers Cl(0,2) and Cl(1,3).
    """
    p, q = _signature_pq(mv.algebra)
    _, qdim = _classify(p, q)
    _quaternion_block_basis(mv.algebra)

    cmat = _to_quaternion_block_complex(mv)
    # cmat is (2*qdim × 2*qdim) complex — read as (qdim × qdim) quaternion blocks
    rows = []
    for i in range(qdim):
        row = []
        for j in range(qdim):
            block = cmat[2 * i : 2 * i + 2, 2 * j : 2 * j + 2]
            row.append(_extract_quat(block))
        rows.append(row)
    return rows
