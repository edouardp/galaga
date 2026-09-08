"""The NumPy benchmark must derive the same products as the public algebra."""

import runpy
from pathlib import Path

import numpy as np
import pytest

from galaga import Algebra

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def benchmark():
    return runpy.run_path(str(ROOT / "bench_batched.py"))


@pytest.mark.parametrize(
    "gram",
    (
        np.diag([1, -1, -1, -1]),
        np.diag([1, 0, -1]),
        np.array([[1.0, 0.4], [0.4, 2.0]]),
        np.array([[0.0, -1.0], [-1.0, 0.0]]),
    ),
    ids=("spacetime", "degenerate", "oblique", "null-pair"),
)
def test_structure_tensor_matches_every_actual_basis_product(benchmark, gram):
    algebra = Algebra(gram=gram)
    tensor = benchmark["structure_tensor"](algebra)
    for i in range(algebra.dim):
        for j in range(algebra.dim):
            product = algebra.blade(i) * algebra.blade(j)
            np.testing.assert_allclose(tensor[i, j], product.data, rtol=0, atol=1e-12)
    assert not tensor.flags.writeable
    with pytest.raises(ValueError, match="read-only"):
        tensor[0, 0, 0] = 7


def test_oblique_product_keeps_both_scalar_and_bivector_terms(benchmark):
    algebra = Algebra(gram=np.array([[1.0, 0.4], [0.4, 2.0]]))
    e1, e2 = algebra.basis_vectors()
    product = e1 * e2
    tensor = benchmark["structure_tensor"](algebra)
    assert np.count_nonzero(product.data) == 2
    np.testing.assert_array_equal(tensor[1, 2], product.data)
    assert tensor[1, 2, 0] == algebra.gram[0, 1]


@pytest.mark.parametrize("count", (0, 1, 9))
def test_batched_operations_match_individual_mixed_grade_products(benchmark, count):
    algebra = benchmark["alg"]
    rng = np.random.default_rng(174)
    left, right = (rng.normal(size=(count, algebra.dim)) for _ in range(2))
    expected_product = np.empty_like(left)
    expected_reverse = np.empty_like(left)
    expected_sandwich = np.empty_like(left)
    for i in range(count):
        a, b = algebra.multivector(left[i]), algebra.multivector(right[i])
        expected_product[i] = (a * b).data
        expected_reverse[i] = (~a).data
        expected_sandwich[i] = (a * b * ~a).data
    np.testing.assert_allclose(benchmark["batched_gp"](left, right), expected_product, rtol=0, atol=1e-12)
    np.testing.assert_allclose(benchmark["batched_reverse"](left), expected_reverse, rtol=0, atol=1e-12)
    np.testing.assert_allclose(benchmark["batched_sandwich"](left, right), expected_sandwich, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(left, np.random.default_rng(174).normal(size=left.shape))


def test_reverse_signs_match_every_reversed_basis_blade_and_caches_are_reused(benchmark):
    algebra = benchmark["alg"]
    rows = np.eye(algebra.dim)
    expected = np.stack([(~algebra.blade(i)).data for i in range(algebra.dim)])
    np.testing.assert_array_equal(benchmark["batched_reverse"](rows), expected)
    assert benchmark["_get_structure_tensor"]() is benchmark["_get_structure_tensor"]()
    assert benchmark["_get_rev_signs"]() is benchmark["_get_rev_signs"]()
    assert not benchmark["_get_rev_signs"]().flags.writeable
