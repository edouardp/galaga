"""Primitive transformation identities from Chisolm's geometric algebra.

Source: Chisolm, "Geometric Algebra" (arXiv:1205.5935v1), Sections 6,
7.2, 7.3, and 9.5.2. Projection, rejection, reflection, and rotor-constructor
helpers remain facade concerns; these tests use only numeric core primitives.
"""

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    exp,
    geometric_product,
    grade,
    inverse,
    is_vector,
    outer_product,
    reverse,
    sandwich,
    scalar_product,
)


def assert_mv_close(actual, expected, *, atol: float = 1e-10) -> None:
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=atol)


def random_vector(algebra: Algebra, rng: np.random.Generator):
    return algebra.vector(rng.standard_normal(algebra.n))


def test_eq_324_reflection_in_a_plane_uses_versor_formula() -> None:
    """Eq. 3.24: even-blade reflection is ``B v B^-1``."""
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    plane = outer_product(e1, e2)
    vector = 2 * e1 - 3 * e2 + 5 * e3

    reflected = geometric_product(
        geometric_product(plane, vector),
        inverse(plane),
    )

    assert is_vector(reflected)
    assert reflected == -2 * e1 + 3 * e2 + 5 * e3


def test_eq_328_reflection_of_pseudoscalar_has_blade_parity() -> None:
    """Eq. 3.28: reflection in an r-blade maps I to ``(-1)^r I``."""
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    pseudoscalar = algebra.I
    plane = outer_product(e1, e2)

    vector_reflection = geometric_product(
        geometric_product(-e1, pseudoscalar),
        inverse(e1),
    )
    plane_reflection = geometric_product(
        geometric_product(plane, pseudoscalar),
        inverse(plane),
    )

    assert vector_reflection == -pseudoscalar
    assert plane_reflection == pseudoscalar


@pytest.mark.parametrize(
    "algebra",
    [Algebra(2, id="Cl2"), Algebra(3, id="Cl3")],
    ids=lambda algebra: algebra.id,
)
def test_eq_330_rotor_sandwich_preserves_metric_and_grade(algebra: Algebra) -> None:
    """Eq. 3.30: ``R A reverse(R)`` is a grade-preserving isometry."""
    e1, e2, *_ = algebra.basis_vectors()
    rotor = exp(-0.3 * outer_product(e1, e2))
    rng = np.random.default_rng(107)
    left = random_vector(algebra, rng)
    right = random_vector(algebra, rng)
    rotated_left = sandwich(rotor, left)
    rotated_right = sandwich(rotor, right)

    assert is_vector(rotated_left)
    assert is_vector(rotated_right)
    assert float(scalar_product(rotated_left, rotated_right)) == pytest.approx(
        float(scalar_product(left, right)),
        abs=1e-10,
    )
    assert sandwich(rotor, algebra.I).almost_equal(algebra.I)


def test_eq_330_rotates_bivectors_without_other_grades() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    rotor = exp(-0.4 * outer_product(e1, e2))
    rotated = sandwich(rotor, outer_product(e1, e3))

    for target_grade in range(algebra.n + 1):
        if target_grade != 2:
            assert grade(rotated, target_grade) == 0


def test_eq_130_exponential_rotors_have_unit_reverse_norm() -> None:
    """Eq. 1.30: ``exp(-B theta/2) reverse(R) = 1`` for unit B."""
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    plane = outer_product(e1, e2)

    for angle in (0.0, 0.5, 1.0, np.pi, 2 * np.pi):
        rotor = exp((-angle / 2) * plane)
        assert geometric_product(rotor, reverse(rotor)).almost_equal(algebra.identity)


def test_cl3_cross_product_is_metric_dual_of_the_wedge() -> None:
    """Section 6.2: ``a x b = (a wedge b) I^-1`` in Euclidean 3-space."""
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    pseudoscalar_inverse = inverse(algebra.I)

    assert geometric_product(outer_product(e1, e2), pseudoscalar_inverse) == e3
    assert geometric_product(outer_product(e2, e3), pseudoscalar_inverse) == e1
    assert geometric_product(outer_product(e3, e1), pseudoscalar_inverse) == e2

    rng = np.random.default_rng(110)
    left_coefficients = rng.standard_normal(3)
    right_coefficients = rng.standard_normal(3)
    actual = geometric_product(
        outer_product(
            algebra.vector(left_coefficients),
            algebra.vector(right_coefficients),
        ),
        pseudoscalar_inverse,
    )
    expected = algebra.vector(np.cross(left_coefficients, right_coefficients))
    assert_mv_close(actual, expected)


def test_sta_hyperbolic_rotor_has_closed_form_and_preserves_metric() -> None:
    """Section 9.5.2: a time-space bivector generates a Lorentz boost."""
    algebra = Algebra(1, 3)
    g0, g1, _, _ = algebra.basis_vectors()
    plane = outer_product(g0, g1)
    rapidity = 0.8
    rotor = exp((-rapidity / 2) * plane)
    expected_rotor = algebra.scalar(np.cosh(rapidity / 2)) - np.sinh(rapidity / 2) * plane

    assert geometric_product(plane, plane) == 1
    assert_mv_close(rotor, expected_rotor, atol=1e-12)
    assert geometric_product(rotor, reverse(rotor)).almost_equal(algebra.identity)
    assert_mv_close(
        sandwich(rotor, g0),
        np.cosh(rapidity) * g0 + np.sinh(rapidity) * g1,
    )

    rng = np.random.default_rng(300)
    left = random_vector(algebra, rng)
    right = random_vector(algebra, rng)
    assert float(scalar_product(sandwich(rotor, left), sandwich(rotor, right))) == pytest.approx(
        float(scalar_product(left, right)), abs=1e-10
    )
