"""Division must not discard small grades or form overflowing scalar inverses."""

import numpy as np
import pytest

import galaga.core as core

GRAMS = (((1, 0), (0, 1)), ((2, 0.5), (0.5, -1)), ((1, 1), (1, 1)))


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("epsilon", (5e-13, -5e-13, 1e-20))
@pytest.mark.parametrize("reflected", (False, True))
def test_near_scalar_division_keeps_every_nonzero_grade(gram, epsilon, reflected):
    algebra = core.Algebra(gram=gram)
    vector = algebra.blade(1)
    denominator = 1 + epsilon * vector
    assert core.is_scalar(denominator)  # A tolerant predicate is not a storage test.
    expected = (1 - epsilon * vector).data / (1 - epsilon**2 * gram[0][0])
    result = 1 / denominator if reflected else algebra.scalar(1) / denominator
    np.testing.assert_allclose(result.data, expected, rtol=2e-15, atol=0)
    assert result.coefficient(1) != 0


@pytest.mark.parametrize("number", (float(np.nextafter(0.0, 1.0)), -1e-310, 9.109e-31))
@pytest.mark.parametrize("reflected", (False, True))
def test_scalar_division_does_not_require_a_representable_reciprocal(number, reflected):
    algebra = core.Algebra(2)
    denominator = algebra.scalar(number)
    with np.errstate(over="raise", invalid="raise"):
        result = number / denominator if reflected else algebra.scalar(number) / denominator
    np.testing.assert_array_equal(result.data, algebra.identity.data)


@pytest.mark.parametrize("epsilon", (5e-13, -5e-13))
def test_a_small_invertible_vector_is_not_a_zero_scalar_divisor(epsilon):
    algebra = core.Algebra(2)
    vector = algebra.blade(1)
    result = algebra.scalar(1) / (epsilon * vector)
    np.testing.assert_allclose(result.data, vector.data / epsilon, rtol=2e-15, atol=0)


@pytest.mark.parametrize("gram", GRAMS)
def test_multivector_division_is_right_multiplication_by_the_inverse(gram):
    algebra = core.Algebra(gram=gram)
    a, b = algebra.basis_vectors()
    numerator, denominator = b + (a ^ b), 2 + a
    expected_inverse = (2 - a) / (4 - gram[0][0])
    result = numerator / denominator
    np.testing.assert_allclose(result.data, (numerator * expected_inverse).data, rtol=2e-15, atol=2e-15)
    np.testing.assert_allclose((result * denominator).data, numerator.data, rtol=0, atol=2e-15)
    assert not result.almost_equal(expected_inverse * numerator)


@pytest.mark.parametrize("reflected", (False, True))
def test_zero_scalar_division_has_a_clear_arithmetic_error(reflected):
    algebra = core.Algebra(2)
    with pytest.raises(ZeroDivisionError):
        _ = 1 / algebra.scalar(0) if reflected else algebra.scalar(1) / algebra.scalar(0)
