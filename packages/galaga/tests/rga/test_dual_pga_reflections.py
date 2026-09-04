from __future__ import annotations

import numpy as np
import pytest

from galaga import (
    Algebra,
    antireverse,
    antiwedge,
    geometric_antiproduct,
    gp,
    p_pga,
    p_rga,
    sandwich,
)
from galaga.rga import RigidModel


def _antiproduct_sandwich(operator, value):
    return geometric_antiproduct(
        geometric_antiproduct(operator, value),
        antireverse(operator),
    )


def _plane_basis(algebra: Algebra):
    e1, e2, e3, e0 = algebra.basis_vectors()
    return algebra.blades(
        e1 ^ e2 ^ e3,
        e2 ^ e3 ^ e0,
        e3 ^ e1 ^ e0,
        e1 ^ e2 ^ e0,
    )


def _plane_point(algebra: Algebra, coordinates: tuple[float, float, float]):
    e123, e230, e310, e120 = _plane_basis(algebra)
    x, y, z = coordinates
    return e123 + x * e230 + y * e310 + z * e120


def _plane_coordinates(algebra: Algebra, point) -> np.ndarray:
    e123, e230, e310, e120 = _plane_basis(algebra)

    def component(blade) -> float:
        mask = int(np.flatnonzero(blade.data)[0])
        return point.coefficient(mask) / blade.coefficient(mask)

    weight = component(e123)
    return np.array(
        (
            component(e230) / weight,
            component(e310) / weight,
            component(e120) / weight,
        )
    )


@pytest.mark.parametrize("separation", (0.0, 0.25, 1.5))
def test_parallel_plane_reflections_translate_by_twice_the_separation(
    separation: float,
) -> None:
    point_model = RigidModel(Algebra(config=p_rga()))
    point = point_model.point((-1.0, 0.75, 0.0))
    e1, e2, e3 = point_model.euclidean_basis_vectors()
    e4 = point_model.projective
    e23, e423, e321 = point_model.algebra.blades(
        e2 ^ e3,
        e4 ^ e2 ^ e3,
        e3 ^ e2 ^ e1,
    )
    point_operator = geometric_antiproduct(e423 - separation * e321, e423)

    plane_algebra = Algebra(config=p_pga())
    plane = _plane_point(plane_algebra, (-1.0, 0.75, 0.0))
    plane_e1, _, _, plane_e0 = plane_algebra.basis_vectors()
    plane_operator = gp(plane_e1 + separation * plane_e0, plane_e1)

    assert point_operator.almost_equal(point_model.antiscalar + separation * e23)
    assert plane_operator.almost_equal(plane_algebra.scalar(1) - separation * (plane_e1 ^ plane_e0))

    expected = (-1.0 + 2 * separation, 0.75, 0.0)
    np.testing.assert_allclose(
        point_model.coordinates(_antiproduct_sandwich(point_operator, point)),
        expected,
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        _plane_coordinates(plane_algebra, sandwich(plane_operator, plane)),
        expected,
        rtol=0,
        atol=1e-12,
    )


def test_both_pga_sandwiches_preserve_their_line_join() -> None:
    separation = 0.75
    point_model = RigidModel(Algebra(config=p_rga()))
    point_p = point_model.point((-1.0, 0.75, 0.0))
    point_q = point_model.point((0.5, -0.25, 0.0))
    e1, e2, e3 = point_model.euclidean_basis_vectors()
    e4 = point_model.projective
    e423, e321 = point_model.algebra.blades(e4 ^ e2 ^ e3, e3 ^ e2 ^ e1)
    point_operator = geometric_antiproduct(e423 - separation * e321, e423)
    point_line = point_p ^ point_q

    moved_point_p = _antiproduct_sandwich(point_operator, point_p)
    moved_point_q = _antiproduct_sandwich(point_operator, point_q)
    moved_point_line = _antiproduct_sandwich(point_operator, point_line)
    assert moved_point_line.almost_equal(moved_point_p ^ moved_point_q)
    assert np.allclose((moved_point_p ^ moved_point_line).data, 0)

    plane_algebra = Algebra(config=p_pga())
    plane_p = _plane_point(plane_algebra, (-1.0, 0.75, 0.0))
    plane_q = _plane_point(plane_algebra, (0.5, -0.25, 0.0))
    plane_e1, _, _, plane_e0 = plane_algebra.basis_vectors()
    plane_operator = gp(plane_e1 + separation * plane_e0, plane_e1)
    plane_line = antiwedge(plane_p, plane_q)

    moved_plane_p = sandwich(plane_operator, plane_p)
    moved_plane_q = sandwich(plane_operator, plane_q)
    moved_plane_line = sandwich(plane_operator, plane_line)
    assert moved_plane_line.almost_equal(antiwedge(moved_plane_p, moved_plane_q))
    assert np.allclose(antiwedge(moved_plane_p, moved_plane_line).data, 0)
