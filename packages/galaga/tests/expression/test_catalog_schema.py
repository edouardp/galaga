from __future__ import annotations

import math
from typing import Any

import pytest

from galaga.facade import OPERATIONS, OperationSpec, ParameterSpec


@pytest.mark.parametrize(
    "factory",
    [
        lambda: ParameterSpec(""),
        lambda: ParameterSpec("value", positional=True),
        lambda: ParameterSpec("value", normalize=None),
        lambda: ParameterSpec("value", render=1),
    ],
)
def test_parameter_specs_reject_invalid_declarations(factory: Any) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: OperationSpec("invalid", 1, lambda value: value, expression_arity=0),
        lambda: OperationSpec(
            "invalid",
            2,
            lambda value, parameter: value,
            expression_arity=1,
        ),
        lambda: OperationSpec(
            "invalid",
            2,
            lambda value, parameter: value,
            expression_arity=1,
            parameters=(ParameterSpec("parameter", positional=True, required=True),) * 2,
        ),
        lambda: OperationSpec("invalid", 1, lambda value: value, parameters=("parameter",)),
        lambda: OperationSpec("invalid", 1, lambda value: value, result_kind="unknown"),
    ],
)
def test_operation_specs_reject_incoherent_expression_schemas(factory: Any) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()


def test_parameters_are_validated_normalized_and_ordered_by_schema() -> None:
    inverse = OPERATIONS["inverse"]

    assert inverse.normalize_expression_parameters({"atol": 1e-8, "rtol": 1e-6}) == (
        ("rtol", 1e-6),
        ("atol", 1e-8),
    )
    with pytest.raises(ValueError, match="duplicate"):
        inverse.normalize_expression_parameters((("atol", 1e-8), ("atol", 1e-7)))
    with pytest.raises(ValueError, match="non-empty strings"):
        inverse.normalize_expression_parameters(((1, 1e-8),))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="no expression parameter"):
        inverse.normalize_expression_parameters({"unknown": 1})
    with pytest.raises(ValueError, match="non-negative"):
        inverse.normalize_expression_parameters({"atol": -1})
    with pytest.raises(ValueError, match="finite"):
        inverse.normalize_expression_parameters({"atol": math.inf})


def test_required_parameter_binding_and_expression_invocation_are_checked() -> None:
    grade = OPERATIONS["grade"]

    with pytest.raises(ValueError, match="requires"):
        grade.normalize_expression_parameters({})
    with pytest.raises(TypeError, match="expects 2 evaluator arguments"):
        grade.bind_expression_call((object(),), {})
    with pytest.raises(TypeError, match="expects 1 operands"):
        grade.invoke_expression((), {"target": 0})
    with pytest.raises(TypeError, match="integer"):
        grade.normalize_expression_parameters({"target": 1.5})


def test_parameter_families_have_canonical_immutable_forms() -> None:
    assert OPERATIONS["scalar_multiply"].normalize_expression_parameters({"scalar": 2}) == (("scalar", 2.0),)
    assert OPERATIONS["grade"].normalize_expression_parameters({"target": "even"}) == (("target", "even"),)
    assert OPERATIONS["grades"].normalize_expression_parameters({"targets": [3, 1]}) == (("targets", (3, 1)),)

    with pytest.raises(TypeError, match="iterable"):
        OPERATIONS["grades"].normalize_expression_parameters({"targets": "0,2"})
    with pytest.raises(TypeError, match="integer"):
        OPERATIONS["power"].normalize_expression_parameters({"exponent": True})


def test_generic_parameter_values_are_frozen_or_rejected() -> None:
    operation = OperationSpec(
        "metadata",
        1,
        lambda value, **kwargs: value,
        parameters=(ParameterSpec("options", required=True),),
    )

    assert operation.normalize_expression_parameters({"options": {"right": [2, 3], "left": 1}}) == (
        ("options", (("left", 1), ("right", (2, 3)))),
    )

    class MutableOnly:
        __hash__ = None

    with pytest.raises(TypeError, match="not immutable"):
        operation.normalize_expression_parameters({"options": MutableOnly()})
