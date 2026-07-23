from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from galaga import Algebra, Multivector, complement, outer_product, p_cga
from galaga.cga import ConformalModel
from galaga.expression import Call, evaluate


def _round_geometries(cga: ConformalModel) -> tuple[Multivector, ...]:
    center = np.array((3.0, 4.0, 0.0))
    radius = 2.0

    def point(offset: tuple[float, float, float]) -> Multivector:
        return cga.round_point(center + radius * np.asarray(offset))

    round_point = cga.round_point(center, radius_squared=radius * radius)
    dipole = outer_product(point((1.0, 0.0, 0.0)), point((-1.0, 0.0, 0.0)))
    circle = outer_product(
        point((1.0, 0.0, 0.0)),
        point((0.0, 1.0, 0.0)),
        point((-1.0, 0.0, 0.0)),
    )
    sphere = outer_product(
        point((1.0, 0.0, 0.0)),
        point((-1.0, 0.0, 0.0)),
        point((0.0, 1.0, 0.0)),
        point((0.0, 0.0, 1.0)),
    )
    return round_point, dipole, circle, sphere


def _blade_scale(value: Multivector, basis: Multivector) -> float:
    mask = int(np.flatnonzero(basis.data)[0])
    scale = value.coefficient(mask) / basis.coefficient(mask)
    np.testing.assert_allclose(value.data, scale * basis.data, rtol=0.0, atol=1e-12)
    return float(scale)


def test_component_families_are_exact_overlapping_decompositions() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    circle = _round_geometries(cga)[2]
    round_bulk = cga.round_bulk_part(circle)
    round_weight = cga.round_weight_part(circle)
    flat_bulk = cga.flat_bulk_part(circle)
    flat_weight = cga.flat_weight_part(circle)

    assert cga.round_part(circle) == round_bulk + round_weight
    assert cga.flat_part(circle) == flat_bulk + flat_weight
    assert cga.bulk_part(circle) == round_bulk + flat_bulk
    assert cga.weight_part(circle) == round_weight + flat_weight
    assert cga.conformal_conjugate(circle) == cga.round_part(circle) - cga.flat_part(circle)
    assert cga.round_part(circle) + cga.flat_part(circle) == circle
    assert cga.bulk_part(circle) + cga.weight_part(circle) == circle


@pytest.mark.parametrize("grade", (1, 2, 3, 4))
def test_weighted_norms_match_erics_round_object_formulas(grade: int) -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    geometry = _round_geometries(cga)[grade - 1]
    weight_basis = complement(cga.infinity)

    round_weight = _blade_scale(cga.round_weight_norm(geometry), weight_basis)
    weighted_radius = _blade_scale(cga.weighted_radius_norm(geometry), cga.algebra.I)

    assert geometry.homogeneous_grade() == grade
    assert float(cga.weighted_center_norm(geometry)) == pytest.approx(5.0 * round_weight)
    assert weighted_radius == pytest.approx(2.0 * round_weight)
    assert float(cga.center_norm(geometry)) == pytest.approx(5.0)
    assert float(cga.radius_norm(geometry)) == pytest.approx(2.0)
    assert float(cga.center_distance(geometry)) == pytest.approx(5.0)
    assert float(cga.radius(geometry)) == pytest.approx(2.0)


def test_four_component_norms_have_erics_values_and_codomain_blades() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    circle = _round_geometries(cga)[2]
    parts_and_norms = (
        (cga.round_bulk_part, cga.round_bulk_norm, cga.algebra.identity),
        (cga.round_weight_part, cga.round_weight_norm, complement(cga.infinity)),
        (cga.flat_bulk_part, cga.flat_bulk_norm, cga.infinity),
        (cga.flat_weight_part, cga.flat_weight_norm, cga.algebra.I),
    )

    for part, component_norm, codomain_basis in parts_and_norms:
        expected = float(np.linalg.norm(part(circle).data))
        assert _blade_scale(component_norm(circle), codomain_basis) == pytest.approx(expected)


def test_weighted_norms_scale_but_normalized_norms_and_aliases_are_projective() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    circle = _round_geometries(cga)[2]
    scaled = -7.0 * circle

    for operation in (
        cga.weighted_center_norm,
        cga.weighted_radius_norm,
        cga.round_bulk_norm,
        cga.round_weight_norm,
        cga.flat_bulk_norm,
        cga.flat_weight_norm,
    ):
        assert operation(scaled).almost_equal(7.0 * operation(circle))

    for operation in (cga.center_norm, cga.radius_norm, cga.center_distance, cga.radius):
        assert float(operation(scaled)) == pytest.approx(float(operation(circle)))


def test_real_radius_norm_has_explicit_real_core_and_normalization_boundaries() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    imaginary = cga.round_point((3.0, 4.0, 0.0), radius_squared=-4.0)
    p = cga.round_point((0.0, 0.0, 0.0))
    q = cga.round_point((1.0, 0.0, 0.0))
    line = outer_product(p, q, cga.infinity)

    assert float(cga.center_norm(imaginary)) == pytest.approx(5.0)
    assert float(cga.center_distance(imaginary)) == pytest.approx(5.0)
    assert float(cga.radius_squared(imaginary)) == pytest.approx(-4.0)
    with pytest.raises(ValueError, match="radius norm is not real"):
        cga.weighted_radius_norm(imaginary)
    with pytest.raises(ValueError, match="radius norm is not real"):
        cga.radius_norm(imaginary)
    with pytest.raises(ValueError, match="radius norm is not real"):
        cga.radius(imaginary)
    with pytest.raises(ValueError, match="nonzero round weight"):
        cga.center_norm(line)
    with pytest.raises(ValueError, match="nonzero round weight"):
        cga.center_distance(line)

    scaled_model = ConformalModel(Algebra(config=p_cga(null_pair=-0.5)))
    scaled_point = scaled_model.round_point((3.0, 4.0, 0.0), radius_squared=4.0)
    assert float(scaled_model.center_norm(scaled_point)) == pytest.approx(5.0)
    assert float(scaled_model.center_distance(scaled_point)) == pytest.approx(5.0)
    with pytest.raises(ValueError, match="standard eo·einf"):
        scaled_model.weighted_radius_norm(scaled_point)
    with pytest.raises(ValueError, match="standard eo·einf"):
        scaled_model.radius_norm(scaled_point)


def test_all_component_and_norm_semantics_remain_executable() -> None:
    cga = ConformalModel(Algebra(config=p_cga()), expr=True)
    circle = _round_geometries(cga)[2].named("C")
    operations: tuple[Callable[[Multivector], Multivector], ...] = (
        cga.round_bulk_part,
        cga.round_weight_part,
        cga.flat_bulk_part,
        cga.flat_weight_part,
        cga.round_part,
        cga.flat_part,
        cga.bulk_part,
        cga.weight_part,
        cga.conformal_conjugate,
        cga.weighted_center_norm,
        cga.weighted_radius_norm,
        cga.round_bulk_norm,
        cga.round_weight_norm,
        cga.flat_bulk_norm,
        cga.flat_weight_norm,
        cga.center_norm,
        cga.radius_norm,
        cga.center_distance,
        cga.radius,
    )

    for operation in operations:
        result = operation(circle)
        assert isinstance(result.expr, Call)
        assert evaluate(result.expr, algebra=cga.algebra, environment={"C": circle}).almost_equal(result)
        assert "infinity" not in result.latex(content="expr")
        assert "atol" not in result.latex(content="expr")
