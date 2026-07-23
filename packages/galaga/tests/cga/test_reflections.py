from __future__ import annotations

import numpy as np

from galaga import Algebra, inverse, outer_product, p_lengyel_cga
from galaga.cga import ConformalModel


def test_plane_reflection_uses_the_ordinary_odd_versor_action() -> None:
    cga = ConformalModel(Algebra(config=p_lengyel_cga()))
    e1, _, _ = cga.euclidean_basis_vectors()
    plane = e1 + cga.infinity
    point = cga.round_point((3, 2, 0))

    reflected = -plane * point * inverse(plane)

    np.testing.assert_allclose(cga.coordinates(reflected), [-1, 2, 0], atol=1e-12)


def test_sphere_inversion_matches_the_euclidean_formula_and_is_involutive() -> None:
    cga = ConformalModel(Algebra(config=p_lengyel_cga()))
    sphere = cga.round_point((1, 0, 0), radius_squared=-4)
    point = cga.round_point((5, 0, 0))

    inverted = -sphere * point * inverse(sphere)
    restored = -sphere * inverted * inverse(sphere)

    np.testing.assert_allclose(cga.coordinates(inverted), [2, 0, 0], atol=1e-12)
    np.testing.assert_allclose(cga.coordinates(restored), [5, 0, 0], atol=1e-12)


def test_inverting_a_line_away_from_the_center_produces_a_circle_through_the_center() -> None:
    cga = ConformalModel(Algebra(config=p_lengyel_cga()))
    sphere = cga.round_point((0, 0, 0), radius_squared=-1)
    a = cga.round_point((-2, 1, 0))
    b = cga.round_point((2, 1, 0))
    line = outer_product(a, b, cga.infinity)

    circle = -sphere * line * inverse(sphere)
    inverted_a = -sphere * a * inverse(sphere)
    inverted_b = -sphere * b * inverse(sphere)

    assert line.homogeneous_grade() == circle.homogeneous_grade() == 3
    assert np.allclose(outer_product(cga.origin, circle).data, 0, rtol=0, atol=1e-12)
    assert np.allclose(outer_product(inverted_a, circle).data, 0, rtol=0, atol=1e-12)
    assert np.allclose(outer_product(inverted_b, circle).data, 0, rtol=0, atol=1e-12)
