from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, p_pga, p_rga
from galaga.expression import Call
from galaga.rga import RigidModel


def test_rigid_model_requires_the_point_based_lengyel_convention() -> None:
    with pytest.raises(ValueError, match="p_rga"):
        RigidModel(Algebra((1, 1, 1, 0)))
    with pytest.raises(ValueError, match="p_rga"):
        RigidModel(Algebra(config=p_pga()))
    with pytest.raises(TypeError, match="boolean"):
        RigidModel(Algebra(config=p_rga()), expr=1)  # type: ignore[arg-type]


def test_model_roles_expose_the_euclidean_space_and_projective_horizon() -> None:
    model = RigidModel(Algebra(config=p_rga()))
    e1, e2, e3 = model.euclidean_basis_vectors()

    assert model.spatial_dim == 3
    assert model.projective == model.algebra.blade("e4")
    assert model.antiscalar == model.algebra.blade("I")
    assert model.horizon == model.algebra.blade("e321")
    assert (e1, e2, e3) == tuple(model.algebra.blade(name) for name in ("e1", "e2", "e3"))


def test_point_factory_roundtrips_finite_coordinates_and_weight() -> None:
    model = RigidModel(Algebra(config=p_rga()))
    point = model.point((3, 4, 5), weight=2)

    assert float(model.point_weight(point)) == pytest.approx(2)
    np.testing.assert_allclose(model.coordinates(point), [1.5, 2, 2.5])
    np.testing.assert_allclose(model.coordinates(model.homogenize(point)), [1.5, 2, 2.5])
    assert not model.coordinates(point).flags.writeable


def test_model_expression_default_is_applied_to_owned_factories() -> None:
    plain = RigidModel(Algebra(config=p_rga()))
    tracked = RigidModel(Algebra(config=p_rga()), expr=True)

    assert plain.point((1, 2, 3)).expr is None
    assert tracked.point((1, 2, 3)).expr is not None
    assert plain.point((1, 2, 3), expr=True).expr is not None
    assert tracked.point((1, 2, 3), expr=False).expr is None

    attitude = tracked.attitude(tracked.point((1, 2, 3)).named("P"))
    assert isinstance(attitude.expr, Call)
    assert attitude.expr.operation_id == "attitude"
    assert dict(attitude.expr.parameters)["origin"] == (8, 1)


def test_point_validation_rejects_wrong_shapes_and_ideal_coordinates() -> None:
    model = RigidModel(Algebra(config=p_rga()))

    with pytest.raises(ValueError, match="expected 3"):
        model.point((1, 2))
    with pytest.raises(TypeError, match="real number"):
        model.point((1, "two", 3))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="zero weight"):
        model.coordinates(model.point((1, 0, 0), weight=0))
    with pytest.raises(ValueError, match="grade-1"):
        model.coordinates(model.algebra.blade("e12"))
