from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, outer_product, p_cga, scalar_product
from galaga.cga import ConformalModel


@pytest.fixture
def cga() -> ConformalModel:
    return ConformalModel(Algebra(config=p_cga()))


def test_direct_objects_use_wedges_of_round_points_and_native_infinity(cga: ConformalModel) -> None:
    p = cga.round_point((0.0, 0.0, 0.0))
    q = cga.round_point((1.0, 0.0, 0.0))
    r = cga.round_point((0.0, 1.0, 0.0))
    s = cga.round_point((0.0, 0.0, 1.0))

    flat_point = outer_product(p, cga.infinity)
    dipole = outer_product(p, q)
    line = outer_product(p, q, cga.infinity)
    circle = outer_product(p, q, r)
    plane = outer_product(p, q, r, cga.infinity)
    sphere = outer_product(p, q, r, s)

    assert flat_point.homogeneous_grade() == dipole.homogeneous_grade() == 2
    assert line.homogeneous_grade() == circle.homogeneous_grade() == 3
    assert plane.homogeneous_grade() == sphere.homogeneous_grade() == 4
    for geometry, contained in ((line, p), (circle, q), (plane, r), (sphere, s)):
        assert outer_product(geometry, contained) == 0


def test_point_dot_product_is_negative_half_euclidean_squared_distance(cga: ConformalModel) -> None:
    x = np.array((1.0, 2.0, -3.0))
    y = np.array((-2.0, 0.5, 4.0))

    actual = float(scalar_product(cga.round_point(x), cga.round_point(y)))

    assert actual == pytest.approx(-0.5 * float(np.dot(x - y, x - y)))


def test_wiki_dual_and_antidual_are_metric_and_antimetric_complements(cga: ConformalModel) -> None:
    p = cga.round_point((1.0, 2.0, 3.0))

    assert cga.antidual(p) == -cga.dual(p)
    assert cga.dual(cga.dual(p)).homogeneous_grade() == 1


def test_carrier_and_cocarrier_recover_flat_geometries(cga: ConformalModel) -> None:
    p = cga.round_point((-1.0, 0.0, 0.0))
    q = cga.round_point((1.0, 0.0, 0.0))
    r = cga.round_point((0.0, 1.0, 0.0))
    dipole = outer_product(p, q)
    circle = outer_product(p, q, r)

    assert cga.carrier(dipole) == outer_product(p, q, cga.infinity)
    assert cga.carrier(circle) == outer_product(p, q, r, cga.infinity)
    assert cga.cocarrier(dipole).homogeneous_grade() == 4
    assert cga.cocarrier(circle).homogeneous_grade() == 3


@pytest.mark.parametrize("kind", ("dipole", "circle", "sphere"))
def test_center_and_container_preserve_round_center_and_radius(cga: ConformalModel, kind: str) -> None:
    px = cga.round_point((1.0, 0.0, 0.0))
    nx = cga.round_point((-1.0, 0.0, 0.0))
    py = cga.round_point((0.0, 1.0, 0.0))
    pz = cga.round_point((0.0, 0.0, 1.0))
    geometries = {
        "dipole": outer_product(px, nx),
        "circle": outer_product(px, py, nx),
        "sphere": outer_product(px, nx, py, pz),
    }
    geometry = geometries[kind]

    center = cga.center(geometry)
    container = cga.container(geometry)

    np.testing.assert_allclose(cga.coordinates(center), (0.0, 0.0, 0.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(center)) == pytest.approx(1.0)
    assert container.homogeneous_grade() == 4
    container_center = cga.center(container)
    np.testing.assert_allclose(cga.coordinates(container_center), (0.0, 0.0, 0.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(container_center)) == pytest.approx(1.0)


def test_partner_preserves_center_and_flips_signed_squared_radius(cga: ConformalModel) -> None:
    value = cga.round_point((1.0, -2.0, 3.0), radius_squared=4.0)

    partner = cga.partner(value)

    np.testing.assert_allclose(cga.coordinates(partner), (1.0, -2.0, 3.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(partner)) == pytest.approx(-4.0)
    assert float(scalar_product(value, partner)) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("kind", ("round-point", "dipole", "circle", "sphere"))
def test_partner_invariants_hold_for_every_round_object_grade(cga: ConformalModel, kind: str) -> None:
    px = cga.round_point((1.0, 0.0, 0.0))
    nx = cga.round_point((-1.0, 0.0, 0.0))
    py = cga.round_point((0.0, 1.0, 0.0))
    pz = cga.round_point((0.0, 0.0, 1.0))
    geometries = {
        "round-point": cga.round_point((0.0, 0.0, 0.0), radius_squared=1.0),
        "dipole": outer_product(px, nx),
        "circle": outer_product(px, py, nx),
        "sphere": outer_product(px, nx, py, pz),
    }
    geometry = geometries[kind]

    partner = cga.partner(geometry)
    partner_center = cga.center(partner)

    assert partner.homogeneous_grade() == geometry.homogeneous_grade()
    assert scalar_product(geometry, partner) == 0
    np.testing.assert_allclose(cga.coordinates(partner_center), (0.0, 0.0, 0.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(partner_center)) == pytest.approx(-1.0)
    carrier = cga.carrier(geometry).data
    partner_carrier = cga.carrier(partner).data
    pivot = int(np.argmax(np.abs(carrier)))
    np.testing.assert_allclose(
        partner_carrier * carrier[pivot],
        carrier * partner_carrier[pivot],
        rtol=0.0,
        atol=1e-12,
    )


def test_attitude_uses_origin_complement_and_has_expected_grades(cga: ConformalModel) -> None:
    p = cga.round_point((0.0, 0.0, 0.0))
    q = cga.round_point((1.0, 0.0, 0.0))
    r = cga.round_point((0.0, 1.0, 0.0))

    assert cga.attitude(p) == 1
    assert cga.attitude(outer_product(p, q, cga.infinity)).homogeneous_grade() == 2
    assert cga.attitude(outer_product(p, q, r)).homogeneous_grade() == 2


def test_expansion_and_projection_follow_the_wiki_grade_contract(cga: ConformalModel) -> None:
    origin = cga.round_point((0.0, 0.0, 0.0))
    x = cga.round_point((1.0, 0.0, 0.0))
    y = cga.round_point((0.0, 1.0, 0.0))
    plane = outer_product(origin, x, y, cga.infinity)
    value = cga.round_point((0.25, 0.5, 2.0))

    expanded = cga.expansion(value, plane)
    projected = cga.projection(value, plane)

    assert expanded.homogeneous_grade() == 2
    np.testing.assert_allclose(cga.coordinates(projected), (0.25, 0.5, 0.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(projected)) == pytest.approx(4.0)
    assert outer_product(plane, projected) == 0


def test_conventional_short_forms_are_exact_class_aliases() -> None:
    assert ConformalModel.att is ConformalModel.attitude
    assert ConformalModel.car is ConformalModel.carrier
    assert ConformalModel.ccr is ConformalModel.cocarrier
    assert ConformalModel.cen is ConformalModel.center
    assert ConformalModel.con is ConformalModel.container
    assert ConformalModel.homo is ConformalModel.homogenize
    assert ConformalModel.par is ConformalModel.partner
    assert ConformalModel.project is ConformalModel.projection
    assert ConformalModel.up is ConformalModel.round_point


def test_semantic_operations_reject_mixed_values_and_invalid_expansion_grades(cga: ConformalModel) -> None:
    other = ConformalModel(Algebra(config=p_cga()))
    p = cga.round_point((0.0, 0.0, 0.0))
    q = cga.round_point((1.0, 0.0, 0.0))

    with pytest.raises(ValueError, match="different numeric algebra"):
        cga.carrier(other.round_point((0.0, 0.0, 0.0)))
    with pytest.raises(ValueError, match="homogeneous conformal geometry"):
        cga.center(p + outer_product(p, q))
    with pytest.raises(ValueError, match="round geometry"):
        cga.carrier(outer_product(p, q, cga.infinity))
    with pytest.raises(ValueError, match="higher grade"):
        cga.expansion(outer_product(p, q), p)
