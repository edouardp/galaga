from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    antireverse,
    complement,
    geometric_antiproduct,
    gp,
    reverse,
)


@pytest.fixture
def algebra() -> Algebra:
    return Algebra(gram=np.diag((1.0, 1.0, 0.0)))


def _basis(algebra: Algebra) -> tuple[Multivector, ...]:
    e1, e2, e3 = algebra.basis_vectors()
    e12, e23, e31 = algebra.blades(e1 ^ e2, e2 ^ e3, e3 ^ e1)
    return e1, e2, e3, e12, e23, e31


def _antiproduct_sandwich(operator: Multivector, value: Multivector) -> Multivector:
    return geometric_antiproduct(
        geometric_antiproduct(operator, value),
        antireverse(operator),
    )


def _product_sandwich(operator: Multivector, value: Multivector) -> Multivector:
    return gp(gp(operator, value), reverse(operator))


def _vector_action_matrix(
    action: Callable[[Multivector], Multivector],
    basis: tuple[Multivector, Multivector, Multivector],
) -> np.ndarray:
    masks = tuple(int(np.flatnonzero(vector.data)[0]) for vector in basis)
    return np.array(
        [
            [action(source).coefficient(mask) / target.coefficient(mask) for source in basis]
            for target, mask in zip(basis, masks, strict=True)
        ]
    )


def test_point_and_complementary_line_share_coordinates_and_reciprocal_distances(
    algebra: Algebra,
) -> None:
    e1, e2, e3, e12, e23, e31 = _basis(algebra)
    point = e1 + 0.5 * e2 + e3
    line = complement(point)

    assert complement(e1) == e23
    assert complement(e2) == e31
    assert complement(e3) == e12
    assert line == e23 + 0.5 * e31 + e12

    point_distance = np.linalg.norm((1.0, 0.5))
    line_distance = 1 / np.linalg.norm((1.0, 0.5))
    assert point_distance * line_distance == pytest.approx(1)


@pytest.mark.parametrize("translation", (0.0, 0.25, 0.75))
def test_regular_and_complement_translation_matrices_are_inverse_transposes(
    algebra: Algebra,
    translation: float,
) -> None:
    e1, e2, e3, _, _, e31 = _basis(algebra)
    regular_operator = algebra.I - 0.5 * translation * e2
    reciprocal_operator = complement(regular_operator)

    assert reciprocal_operator.almost_equal(algebra.identity - 0.5 * translation * e31)

    regular_matrix = _vector_action_matrix(
        lambda value: _antiproduct_sandwich(regular_operator, value),
        (e1, e2, e3),
    )
    reciprocal_matrix = _vector_action_matrix(
        lambda value: _product_sandwich(reciprocal_operator, value),
        (e1, e2, e3),
    )

    expected_regular = np.array(
        (
            (1, 0, translation),
            (0, 1, 0),
            (0, 0, 1),
        )
    )
    np.testing.assert_allclose(regular_matrix, expected_regular, rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        reciprocal_matrix,
        np.linalg.inv(regular_matrix).T,
        rtol=0,
        atol=1e-12,
    )


def test_complement_intertwines_sandwiches_and_exposes_fixed_geometry(
    algebra: Algebra,
) -> None:
    translation = 0.5
    e1, e2, e3, _, _, e31 = _basis(algebra)
    regular_operator = algebra.I - 0.5 * translation * e2
    reciprocal_operator = complement(regular_operator)
    point = 0.4 * e1 + 0.8 * e2 + e3

    translated = _antiproduct_sandwich(regular_operator, point)
    transformed_dual = _product_sandwich(reciprocal_operator, complement(point))
    assert transformed_dual.almost_equal(complement(translated))

    assert _antiproduct_sandwich(regular_operator, e2).almost_equal(e2)
    assert _product_sandwich(reciprocal_operator, e31).almost_equal(e31)
    assert _product_sandwich(reciprocal_operator, e2 + e3).almost_equal(e2 + e3)

    boundary_point = (1 / translation) * e1 + e3
    boundary_image = _product_sandwich(reciprocal_operator, boundary_point)
    assert boundary_image.coefficient(int(np.flatnonzero(e3.data)[0])) == pytest.approx(0)
