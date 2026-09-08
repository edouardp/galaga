"""Batched geometric algebra operations in pure NumPy.

Instead of looping over N multivectors one at a time, represent them as
(N, 16) arrays and contract them with a structure tensor derived from
Galaga's public left-action matrices. Coefficients use native blade-mask order.

This small-algebra benchmark trades memory for batching: a dense tensor has
``(2**n)**3`` entries and is not suitable for high-dimensional algebras.
"""

import time

import numpy as np

from galaga import Algebra

alg = Algebra((1, -1, -1, -1))
D = alg.dim  # 16


def structure_tensor(algebra: Algebra) -> np.ndarray:
    """Return T[i,j,k], the coefficient of blade k in blade i * blade j.

    Column j of left_action(blade(i)) is that product. Unlike a single
    index/sign lookup, this also represents multi-term general-Gram products.
    """
    tensor = np.stack([algebra.left_action(algebra.blade(i)).T for i in range(algebra.dim)])
    tensor.setflags(write=False)
    return tensor


def batched_gp(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Geometric product of two (N, 16) arrays -> (N, 16).

    Sum A[n,i] * B[n,j] * T[i,j,k] over both input blade indices.
    """
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
        _STRUCT_TENSOR = structure_tensor(alg)
    return _STRUCT_TENSOR


def _get_rev_signs():
    global _REV_SIGNS
    if _REV_SIGNS is None:
        signs = np.ones(D)
        for idx in range(D):
            k = bin(idx).count("1")  # grade
            signs[idx] = (-1) ** (k * (k - 1) // 2)
        signs.setflags(write=False)
        _REV_SIGNS = signs
    return _REV_SIGNS


# --- Benchmark ---

if __name__ == "__main__":
    N = 100_000
    rng = np.random.default_rng(42)

    A = rng.standard_normal((N, D))
    B = rng.standard_normal((N, D))

    # Warm up the cached structure tensor and NumPy contraction.
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
