"""Target construction and validation contracts."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra


@pytest.fixture()
def algebra() -> Algebra:
    return Algebra(3)


def test_selector_conveniences_construct_their_target_objects() -> None:
    assert ga.whole() == ga.WholeExpression()
    assert ga.operand(0) == ga.ExpressionPath((0,))
    assert ga.path(1, 2) == ga.ExpressionPath((1, 2))
    assert ga.grade(2) == ga.GradeTarget((2,))
    assert ga.grades(1, 3) == ga.GradeTarget((1, 3))


def test_operation_ids_resolve_aliases_and_reject_unknown_ids() -> None:
    assert ga.operator("gp").operation_id == "geometric_product"
    assert ga.operator("op").operation_id == "outer_product"
    with pytest.raises(ValueError, match="unknown operation"):
        ga.operator("no_such_operation")
    with pytest.raises(TypeError, match="non-empty string"):
        ga.operator("")


def test_expression_path_rejects_malformed_indices() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ga.ExpressionPath((-1,))
    with pytest.raises(ValueError, match="non-negative"):
        ga.ExpressionPath((True,))


def test_blade_targets_accept_scaled_basis_blades_and_raw_masks(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors()
    assert ga.blade_mask(e1) == (1, algebra)
    assert ga.blade_mask(5 * e1) == (1, algebra)
    assert ga.blade_mask(2) == (2, None)
    assert ga.term(e1).masks == (1,)
    assert ga.terms(e1, e2).masks == (1, 2)
    assert ga.coefficient(e2).masks == (2,)


def test_blade_targets_reject_mixed_terms(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors()
    with pytest.raises(ValueError, match="basis blade"):
        ga.blade_mask(e1 + e2)
    with pytest.raises(ValueError, match="basis blade"):
        ga.blade_mask(algebra.scalar(0))


def test_multi_blade_targets_reject_different_algebras() -> None:
    first = Algebra(2)
    second = Algebra(2)
    with pytest.raises(ValueError, match="one algebra"):
        ga.terms(first.basis_vectors()[0], second.basis_vectors()[1])
    with pytest.raises(ValueError, match="one algebra"):
        ga.coefficients(first.basis_vectors()[0], second.basis_vectors()[1])


def test_blade_target_rejects_non_blade_objects(algebra: Algebra) -> None:
    with pytest.raises(TypeError, match="basis blade"):
        ga.blade_mask("e1")


def test_variable_and_grade_targets_validate_their_fields() -> None:
    with pytest.raises(TypeError, match="variable name"):
        ga.variable("")
    with pytest.raises(ValueError, match="occurrence"):
        ga.variable("x", occurrence=-1)
    assert ga.variable("x", occurrence="all").occurrence == "all"
    with pytest.raises(ValueError, match="at least one grade"):
        ga.GradeTarget(())
    with pytest.raises(ValueError, match="non-negative"):
        ga.GradeTarget((0, -1))
