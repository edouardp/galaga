"""Batched geometric algebra operations in pure NumPy.

Instead of looping over N multivectors one at a time, represent them as
(N, 16) arrays and do all products in one shot using the precomputed
multiplication tables.
"""

import time

import numpy as np

from galaga import Algebra

alg = Algebra((1, -1, -1, -1))
D = alg.dim  # 16

# The algebra's precomputed tables — these are the key:
#   mul_index[i, j] -> result blade index for basis_i * basis_j
#   mul_sign[i, j]  -> scalar factor (reorder sign × metric)
IDX = alg._mul_index  # (16, 16) int
SGN = alg._mul_sign  # (16, 16) float


def batched_gp(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Geometric product of two (N, 16) arrays -> (N, 16).

    For each basis pair (i, j), the contribution to the output blade
    IDX[i,j] is SGN[i,j] * A[:,i] * B[:,j].

    We precompute a dense (16, 16, 16) "structure tensor" that maps
    (i, j) -> k with the right sign, then it's a single einsum.
    """
    # Build structure tensor T[i, j, k] = SGN[i,j] if IDX[i,j]==k else 0
    # This is constant for the algebra — compute once, cache.
    T = _get_structure_tensor()
    # einsum: for each sample n, C[n,k] = sum_{i,j} A[n,i] * B[n,j] * T[i,j,k]
    return np.einsum("ni,nj,ijk->nk", A, B, T)


def batched_reverse(A: np.ndarray) -> np.ndarray:
    """Reverse of (N, 16) array. Grade-k blades get sign (-1)^(k(k-1)/2)."""
    return A * _get_rev_signs()


def batched_sandwich(R: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Sandwich product R X ~R for (N, 16) arrays."""
    return batched_gp(batched_gp(R, X), batched_reverse(R))


# --- Cached constants (computed once per algebra) ---

_STRUCT_TENSOR = None
_REV_SIGNS = None


def _get_structure_tensor():
    global _STRUCT_TENSOR
    if _STRUCT_TENSOR is None:
        T = np.zeros((D, D, D), dtype=np.float64)
        for i in range(D):
            for j in range(D):
                T[i, j, IDX[i, j]] += SGN[i, j]
        _STRUCT_TENSOR = T
    return _STRUCT_TENSOR


def _get_rev_signs():
    global _REV_SIGNS
    if _REV_SIGNS is None:
        signs = np.ones(D)
        for idx in range(D):
            k = bin(idx).count("1")  # grade
            signs[idx] = (-1) ** (k * (k - 1) // 2)
        _REV_SIGNS = signs
    return _REV_SIGNS


# --- Benchmark ---

if __name__ == "__main__":
    N = 100_000
    rng = np.random.default_rng(42)

    A = rng.standard_normal((N, D))
    B = rng.standard_normal((N, D))

    # Warm up (builds structure tensor + any numpy JIT)
    _ = batched_gp(A[:10], B[:10])

    # Benchmark batched gp
    t0 = time.perf_counter()
    C = batched_gp(A, B)
    t_gp = time.perf_counter() - t0
    print(f"Batched gp:       {t_gp:.3f} s  ({N / t_gp:,.0f} gp/s, {t_gp / N * 1e6:.2f} µs each)")

    # Benchmark batched sandwich
    t0 = time.perf_counter()
    S = batched_sandwich(A, B)
    t_sw = time.perf_counter() - t0
    print(f"Batched sandwich: {t_sw:.3f} s  ({N / t_sw:,.0f} sw/s, {t_sw / N * 1e6:.2f} µs each)")
