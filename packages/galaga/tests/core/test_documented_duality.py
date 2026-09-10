"""The duality guide's formulas must hold for the actual native Gram algebra."""

import numpy as np
import pytest

import galaga as facade
import galaga.core as core

GRAMS = (
    np.eye(3),
    np.diag([1.0, -1.0]),
    np.array([[2.0, 0.5], [0.5, 1.0]]),
    np.array([[0.0, -1.0], [-1.0, 0.0]]),
    np.diag([1.0, 0.0]),
    np.array([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, -1], [0, 0, 0, -1, 0]]),
)


@pytest.mark.parametrize("api", [core, facade], ids=["core", "facade"])
@pytest.mark.parametrize("gram", GRAMS, ids=["euclidean", "mixed", "oblique", "null-pair", "degenerate", "cga"])
def test_metric_complement_formula_matches_actual_products(api, gram):
    algebra = api.Algebra(gram=gram)
    pseudoscalar_square = float(algebra.I * algebra.I)
    simple_formula_failures = []
    for mask in range(algebra.dim):
        blade = algebra.blade(mask)
        grade = mask.bit_count()
        sign = (-1) ** (grade * (grade - 1) // 2)
        # The geometric product is the ground truth, independent of contraction selection.
        product = blade * algebra.I
        metric_complement = sign * api.complement(api.metric_apply(blade))
        np.testing.assert_allclose(product.data, metric_complement.data, rtol=0, atol=1e-12)
        np.testing.assert_allclose(api.left_contraction(blade, algebra.I).data, product.data, rtol=0, atol=1e-12)
        np.testing.assert_allclose((blade ^ api.complement(blade)).data, algebra.I.data, rtol=0, atol=1e-12)
        if not np.allclose(product.data, (sign * api.complement(blade)).data, rtol=0, atol=1e-12):
            simple_formula_failures.append(mask)
        if not algebra.is_degenerate:
            np.testing.assert_allclose(
                api.dual(blade).data, (metric_complement / pseudoscalar_square).data, rtol=0, atol=1e-12
            )
    assert bool(simple_formula_failures) is not np.array_equal(gram, np.eye(algebra.n))

    mixed = algebra.multivector(np.arange(1, algebra.dim + 1, dtype=float))
    expected = api.complement(api.metric_apply(api.reverse(mixed)))
    np.testing.assert_allclose((mixed * algebra.I).data, expected.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(api.left_contraction(mixed, algebra.I).data, expected.data, rtol=0, atol=1e-12)
    if algebra.is_degenerate:
        assert pseudoscalar_square == 0
        for operation in (api.dual, api.undual):
            with pytest.raises(ValueError, match="invertible pseudoscalar"):
                operation(mixed)
    else:
        np.testing.assert_allclose(api.dual(mixed).data, (expected / pseudoscalar_square).data, rtol=0, atol=1e-12)


def test_euclidean_bivector_agreement_does_not_identify_dual_with_complement():
    algebra = facade.Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    plane = e1 ^ e2
    assert facade.dual(plane) == facade.complement(plane) == e3
    assert facade.dual(e1) == -(e2 ^ e3)
    assert facade.complement(e1) == e2 ^ e3
    inverse_I = facade.inverse(algebra.I)
    assert inverse_I * plane == plane * inverse_I == e3
