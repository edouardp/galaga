from __future__ import annotations

import math

import numpy as np
import pytest

from galaga import Algebra, p_rga
from galaga.rga import RigidModel


@pytest.fixture
def model() -> RigidModel:
    return RigidModel(Algebra(config=p_rga()))


def test_paired_norms_and_homogeneous_distance_match_rga_definitions(model: RigidModel) -> None:
    point = model.point((3, 4, 0))
    other = model.point((1, 0, 0))

    assert model.bulk_norm(point) == model.algebra.scalar(5)
    assert model.weight_norm(point) == model.antiscalar
    assert model.geometric_norm(point) == model.algebra.scalar(5) + model.antiscalar
    assert model.homogeneous_distance(point, other).almost_equal(model.algebra.scalar(math.sqrt(20)) + model.antiscalar)
    assert model.unitize(3 * point).almost_equal(point)


def test_homogeneous_angle_keeps_scalar_cosine_and_antiscalar_weight(model: RigidModel) -> None:
    plane_x = model.algebra.blade("e423")
    plane_y = model.algebra.blade("e431")

    assert model.homogeneous_angle(plane_x, plane_x) == model.algebra.scalar(1) + model.antiscalar
    assert model.homogeneous_angle(plane_x, plane_y) == model.antiscalar


def test_projection_and_support_operations_return_projective_geometries(model: RigidModel) -> None:
    point = model.point((3, 4, 0))
    plane_x = model.algebra.blade("e423")
    projected = model.orthogonal_projection(point, plane_x)

    np.testing.assert_allclose(model.coordinates(projected), [0, 4, 0], atol=1e-12)

    line = model.point((3, 4, 0)) ^ model.point((1, 0, 0))
    assert model.support(line).homogeneous_grade() == 1
    assert model.antisupport(line).homogeneous_grade() == 3
    assert model.orthogonal_antiprojection(plane_x, point).homogeneous_grade() in {None, 3}
    assert model.central_projection(point, plane_x).homogeneous_grade() in {None, 1}
    assert model.central_antiprojection(plane_x, point).homogeneous_grade() in {None, 3}


def test_line_constraint_and_correction_encode_the_plucker_relation(model: RigidModel) -> None:
    line = model.point((0, 0, 0)) ^ model.point((1, 2, 3))
    invalid = model.algebra.blade("e41") + model.algebra.blade("e23")

    assert model.line_constraint(line) == pytest.approx(0)
    assert model.is_valid_line(line)
    assert model.line_constraint(invalid) == pytest.approx(1)
    assert not model.is_valid_line(invalid)

    corrected = model.orthogonalize_line(invalid)
    assert model.is_valid_line(corrected)
    assert corrected == model.algebra.blade("e41")


def test_motor_and_flector_constraints_detect_invalid_even_and_odd_elements(
    model: RigidModel,
) -> None:
    valid_motor = model.algebra.scalar(1) + model.algebra.blade("e41")
    invalid_motor = model.algebra.scalar(1) + model.antiscalar
    valid_flector = model.algebra.blade("e1")
    invalid_flector = model.algebra.blade("e1") + model.algebra.blade("e423")

    assert model.is_valid_motor(valid_motor)
    assert not model.is_valid_motor(invalid_motor)
    assert model.motor_constraint(invalid_motor) == pytest.approx(1)
    assert model.is_valid_flector(valid_flector)
    assert not model.is_valid_flector(invalid_flector)
    assert model.flector_constraint(invalid_flector) == pytest.approx(1)

    assert not model.is_valid_motor(valid_motor + 1e-10 * model.algebra.blade("e1"))
    assert model.is_valid_motor(valid_motor + 1e-10 * model.algebra.blade("e1"), atol=1e-9)
    assert not model.is_valid_flector(valid_flector + 1e-10)
    assert model.is_valid_flector(valid_flector + 1e-10, atol=1e-9)
