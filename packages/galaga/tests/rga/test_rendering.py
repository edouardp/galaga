from __future__ import annotations

import pytest

from galaga import Algebra, DisplayPolicy, Notation, p_rga
from galaga.expression import Call, evaluate
from galaga.rga import RigidModel


@pytest.fixture
def model() -> RigidModel:
    algebra = Algebra(
        config=p_rga(),
        notation=Notation.lengyel(),
        display=DisplayPolicy(content="full"),
    )
    return RigidModel(algebra, expr=True)


def test_lengyel_rga_norms_use_bulk_weight_and_geometric_notation(model: RigidModel) -> None:
    point = model.point((3, 4, 0)).named("P")

    assert model.bulk_norm(point).latex(content="expr") == r"\lVert P \rVert_{\text{●}}"
    assert model.weight_norm(point).latex(content="expr") == r"\lVert P \rVert_{\text{○}}"
    assert model.geometric_norm(point).latex(content="expr") == r"\lVert P \rVert"
    assert model.bulk_norm(point).unicode(content="expr") == "‖P‖_●"
    assert model.weight_norm(point).unicode(content="expr") == "‖P‖_○"


def test_rga_semantic_operations_retain_roles_and_remain_evaluable(model: RigidModel) -> None:
    point = model.point((3, 4, 0)).named("P")
    other = model.point((1, 0, 0)).named("Q")
    plane = model.algebra.blade("e423", expr=True).named("X")
    line = (point ^ other).named("L")
    scaled = (3 * point).named("S")
    environment = {"P": point, "Q": other, "X": plane, "L": line, "S": scaled}
    results = (
        model.attitude(point),
        model.bulk_norm(point),
        model.weight_norm(point),
        model.geometric_norm(point),
        model.unitize(scaled),
        model.bulk_contraction(point, plane),
        model.weight_contraction(point, plane),
        model.bulk_expansion(point, plane),
        model.weight_expansion(point, plane),
        model.homogeneous_distance(point, other),
        model.homogeneous_angle(plane, plane),
        model.orthogonal_projection(point, plane),
        model.orthogonal_antiprojection(plane, point),
        model.central_projection(point, plane),
        model.central_antiprojection(plane, point),
        model.support(line),
        model.antisupport(line),
    )

    for result in results:
        assert isinstance(result.expr, Call)
        evaluated = evaluate(result.expr, algebra=model.algebra, environment=environment)
        assert evaluated.almost_equal(result)

    distance = model.homogeneous_distance(point, other)
    assert isinstance(distance.expr, Call)
    assert dict(distance.expr.parameters)["projective"] == (8, 1)
    assert "projective" not in distance.latex(content="expr")


def test_default_notation_keeps_descriptive_rga_operation_names(model: RigidModel) -> None:
    point = model.point((3, 4, 0)).named("P")

    assert model.bulk_norm(point).latex(content="expr", notation=Notation.default()) == (
        r"\operatorname{bulk\_norm}(P)"
    )
    assert (
        model.support((point ^ model.point((1, 0, 0))).named("L")).latex(
            content="expr",
            notation=Notation.default(),
        )
        == r"\operatorname{support}(L)"
    )
