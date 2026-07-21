"""Fuzz tests: matrix representation roundtrip preserves the geometric product.

For random multivector pairs (A, B), verifies that:
    from_matrix(to_matrix(A) @ to_matrix(B)) == gp(A, B)

This validates that the matrix representation is a faithful algebra homomorphism:
    ρ(A * B) = ρ(A) @ ρ(B)

Tests both left-regular and compact modes across multiple algebras.
"""

import numpy as np
from galaga_matrix import from_matrix, to_matrix
from galaga_matrix.repr import MatrixRepr

from galaga import Algebra, Multivector, geometric_product

N_TRIALS = 1000
TOLERANCE = 1e-10


def _random_multivector(alg: Algebra, rng: np.random.Generator, sparsity: float = 0.7) -> Multivector:
    """Generate a random multivector with ~70% of blades nonzero."""
    coeffs = rng.standard_normal(alg.dim)
    mask = rng.random(alg.dim) < sparsity
    coeffs *= mask
    return alg.multivector(coeffs)


def _run_product_roundtrip(alg: Algebra, mode: str, n_trials: int = N_TRIALS) -> float:
    """Run n_trials random product roundtrips; return max error."""
    rng = np.random.default_rng(42)
    max_err = 0.0
    for _ in range(n_trials):
        A = _random_multivector(alg, rng)
        B = _random_multivector(alg, rng)

        # Direct geometric product
        C_direct = geometric_product(A, B)

        # Via matrix multiplication
        M_A = to_matrix(A, mode=mode)
        M_B = to_matrix(B, mode=mode)
        M_C = M_A.mat @ M_B.mat
        C_matrix = from_matrix(MatrixRepr(M_C, algebra=alg, mode=mode))

        err = np.max(np.abs(C_direct.data - C_matrix.data))
        max_err = max(max_err, err)

    return max_err


# ── Left-regular mode ──


class TestLeftRegularProductRoundtrip:
    """Verify ρ(A*B) = ρ(A)@ρ(B) for left-regular representation."""

    def test_cl2_left_regular(self):
        alg = Algebra(2, 0)
        max_err = _run_product_roundtrip(alg, "left-regular")
        assert max_err < TOLERANCE, f"Cl(2,0) left-regular max error: {max_err:.2e}"

    def test_cl3_left_regular(self):
        alg = Algebra(3, 0)
        max_err = _run_product_roundtrip(alg, "left-regular")
        assert max_err < TOLERANCE, f"Cl(3,0) left-regular max error: {max_err:.2e}"

    def test_cl13_left_regular(self):
        alg = Algebra(1, 3)
        max_err = _run_product_roundtrip(alg, "left-regular")
        assert max_err < TOLERANCE, f"Cl(1,3) left-regular max error: {max_err:.2e}"

    def test_cl31_left_regular(self):
        alg = Algebra(3, 1)
        max_err = _run_product_roundtrip(alg, "left-regular")
        assert max_err < TOLERANCE, f"Cl(3,1) left-regular max error: {max_err:.2e}"

    def test_cl301_pga_left_regular(self):
        alg = Algebra(3, 0, 1)
        max_err = _run_product_roundtrip(alg, "left-regular")
        assert max_err < TOLERANCE, f"Cl(3,0,1) left-regular max error: {max_err:.2e}"


# ── Compact mode ──


class TestCompactProductRoundtrip:
    """Verify ρ(A*B) = ρ(A)@ρ(B) for compact representation."""

    def test_cl2_compact(self):
        alg = Algebra(2, 0)
        max_err = _run_product_roundtrip(alg, "compact")
        assert max_err < TOLERANCE, f"Cl(2,0) compact max error: {max_err:.2e}"

    def test_cl3_compact(self):
        alg = Algebra(3, 0)
        max_err = _run_product_roundtrip(alg, "compact")
        assert max_err < TOLERANCE, f"Cl(3,0) compact max error: {max_err:.2e}"

    def test_cl13_compact(self):
        alg = Algebra(1, 3)
        max_err = _run_product_roundtrip(alg, "compact")
        assert max_err < TOLERANCE, f"Cl(1,3) compact max error: {max_err:.2e}"

    def test_cl31_compact(self):
        alg = Algebra(3, 1)
        max_err = _run_product_roundtrip(alg, "compact")
        assert max_err < TOLERANCE, f"Cl(3,1) compact max error: {max_err:.2e}"
