from __future__ import annotations

import numpy as np
import pytest

from galaga import (
    Algebra,
    geometric_product,
    left_contraction,
    outer_product,
    p_cga,
    reverse,
    scalar_product,
)
from galaga.cga import ConformalModel


def assert_projectively_equal(actual, expected, *, atol: float = 1e-12) -> None:
    expected_support = np.flatnonzero(np.abs(expected.data) > atol)
    assert expected_support.size > 0

    pivot = int(expected_support[0])
    scale = actual.data[pivot] / expected.data[pivot]
    assert abs(scale) > atol
    np.testing.assert_allclose(actual.data, scale * expected.data, rtol=0.0, atol=atol)


def test_conformal_model_has_no_representation_state() -> None:
    algebra = Algebra(config=p_cga(spatial_dim=2))
    cga = ConformalModel(algebra)

    assert not hasattr(cga, "with_representation")
    with pytest.raises(TypeError, match="unexpected keyword argument 'representation'"):
        ConformalModel(algebra, representation="dual")  # type: ignore[call-arg]


@pytest.mark.parametrize("spatial_dim", (1, 2, 3, 4))
@pytest.mark.parametrize("null_pair", (-2.0, -1.0, -0.5, 0.75))
def test_cga_dual_uses_the_complete_conformal_metric(
    spatial_dim: int,
    null_pair: float,
) -> None:
    algebra = Algebra(config=p_cga(spatial_dim=spatial_dim, null_pair=null_pair))
    cga = ConformalModel(algebra)
    conformal_dimension = spatial_dim + 2

    for mask in range(algebra.dim):
        blade = algebra.blade(mask)
        blade_grade = mask.bit_count()
        dual_grade = conformal_dimension - blade_grade
        square_factor = ((-1) ** (blade_grade * dual_grade)) * algebra.metric_determinant

        assert cga.dual(blade).homogeneous_grade() == dual_grade
        assert cga.dual(cga.dual(blade)).almost_equal(square_factor * blade)


def test_cga_dual_is_reverse_times_the_full_conformal_pseudoscalar() -> None:
    algebra = Algebra(config=p_cga(spatial_dim=2))
    cga = ConformalModel(algebra)
    e1, e2 = cga.euclidean_basis_vectors()

    for value in (e1, e2, cga.origin, cga.infinity):
        assert cga.dual(value).almost_equal(geometric_product(reverse(value), algebra.I))

    assert_projectively_equal(
        cga.dual(e1),
        outer_product(e2, cga.origin, cga.infinity),
    )


def test_direct_circle_dualizes_to_its_analytic_ipns_vector() -> None:
    cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    radius = 1.0
    center = cga.up(0.0, 0.0)
    p = cga.up(-radius, 0.0)
    q = cga.up(0.0, radius)
    r = cga.up(radius, 0.0)

    circle_opns = outer_product(p, q, r)
    circle_ipns = cga.dual(circle_opns)
    analytic_ipns = center + (radius * radius / (2.0 * cga.null_pair)) * cga.infinity

    assert circle_opns.homogeneous_grade() == 3
    assert circle_ipns.homogeneous_grade() == 1
    assert_projectively_equal(circle_ipns, analytic_ipns)

    for coordinates, expected_incidence in (
        ((-1.0, 0.0), True),
        ((0.0, 1.0), True),
        ((1.0, 0.0), True),
        ((0.0, 0.0), False),
        ((2.0, 0.0), False),
    ):
        probe = cga.up(*coordinates)
        opns_incidence = np.allclose(
            outer_product(probe, circle_opns).data,
            0.0,
            rtol=0.0,
            atol=1e-12,
        )
        ipns_incidence = abs(float(scalar_product(probe, circle_ipns))) <= 1e-12

        assert opns_incidence is expected_incidence
        assert ipns_incidence is expected_incidence


def test_direct_line_dualizes_to_its_ipns_normal_vector() -> None:
    cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    _, e2 = cga.euclidean_basis_vectors()
    p = cga.up(-1.0, 0.0)
    q = cga.up(1.0, 0.0)

    line_opns = outer_product(p, q, cga.infinity)
    line_ipns = cga.dual(line_opns)

    assert_projectively_equal(line_ipns, e2)


def test_point_has_distinct_strict_dual_and_zero_sphere_forms() -> None:
    cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    point = cga.up(-1.0, 0.0)
    strict_dual = cga.dual(point)

    assert point.homogeneous_grade() == 1
    assert strict_dual.homogeneous_grade() == cga.algebra.n - 1

    for coordinates, expected_incidence in (
        ((-1.0, 0.0), True),
        ((0.0, 0.0), False),
        ((1.0, 0.0), False),
        ((0.0, 1.0), False),
    ):
        probe = cga.up(*coordinates)
        direct_incidence = np.allclose(
            outer_product(probe, point).data,
            0.0,
            rtol=0.0,
            atol=1e-12,
        )
        strict_dual_incidence = np.allclose(
            left_contraction(probe, strict_dual).data,
            0.0,
            rtol=0.0,
            atol=1e-12,
        )
        zero_sphere_incidence = abs(float(scalar_product(probe, point))) <= 1e-12

        assert direct_incidence is expected_incidence
        assert strict_dual_incidence is expected_incidence
        assert zero_sphere_incidence is expected_incidence
