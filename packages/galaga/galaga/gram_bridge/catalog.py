"""Operation metadata for the experimental Gram-backed Galaga facade.

This module owns call-shape policy but no expression or rendering state.  A
numeric evaluator and an expression node remain binary even when the public
facade accepts a variadic associative product.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Protocol

import gram


class CallPolicy(Protocol):
    """Adapt a public call shape to one numeric evaluator."""

    def invoke(
        self,
        operation: OperationSpec,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any: ...


@dataclass(frozen=True, slots=True)
class FixedCall:
    """Require exactly the evaluator's declared positional arity."""

    def invoke(
        self,
        operation: OperationSpec,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if len(args) != operation.arity:
            raise TypeError(f"{operation.id} expects {operation.arity} positional arguments, got {len(args)}")
        return operation.evaluate(*args, **kwargs)


@dataclass(frozen=True, slots=True)
class LeftFoldCall:
    """Lower one-or-more public operands to a binary left fold."""

    min_args: int = 1

    def invoke(
        self,
        operation: OperationSpec,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any:
        if operation.arity != 2:
            raise RuntimeError(f"{operation.id} uses LeftFoldCall with nonbinary arity {operation.arity}")
        if len(args) < self.min_args:
            raise TypeError(f"{operation.id} expects at least {self.min_args} positional argument, got {len(args)}")
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"{operation.id} does not accept fold keywords: {names}")

        result = args[0]
        for operand in args[1:]:
            result = operation.evaluate(result, operand)
        return result


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """One stable operation identity and its numeric call contract."""

    id: str
    arity: int
    evaluate: Callable[..., Any]
    call_policy: CallPolicy = FixedCall()
    operator: str | None = None
    grade_rule: Callable[..., int | None] | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("operation id must not be empty")
        if self.arity < 1:
            raise ValueError("operation arity must be positive")

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Evaluate after applying this operation's public call policy."""
        return self.call_policy.invoke(self, args, kwargs)


def _gram_operation(
    name: str,
    arity: int,
    *,
    call_policy: CallPolicy | None = None,
    operator: str | None = None,
) -> OperationSpec:
    return OperationSpec(
        id=name,
        arity=arity,
        evaluate=getattr(gram, name),
        call_policy=call_policy or FixedCall(),
        operator=operator,
    )


def _structural_operations() -> tuple[OperationSpec, ...]:
    return (
        OperationSpec("add", 2, lambda left, right: left + right, operator="+"),
        OperationSpec("subtract", 2, lambda left, right: left - right, operator="-"),
        OperationSpec("negate", 1, lambda value: -value, operator="unary -"),
        OperationSpec(
            "scalar_multiply",
            2,
            lambda value, scalar: value * scalar,
        ),
        OperationSpec(
            "scalar_divide",
            2,
            lambda value, scalar: value / scalar,
        ),
        OperationSpec("power", 2, lambda value, exponent: value**exponent),
    )


def _gram_operations() -> tuple[OperationSpec, ...]:
    unary = (
        "antimetric_apply",
        "antireverse",
        "bulk_part",
        "complement",
        "conjugate",
        "dual",
        "even_grades",
        "exp",
        "involute",
        "inverse",
        "is_basis_blade",
        "is_bivector",
        "is_even",
        "is_rotor",
        "is_scalar",
        "is_vector",
        "left_complement",
        "left_hodge_dual",
        "left_weight_dual",
        "log",
        "metric_apply",
        "norm",
        "norm2",
        "odd_grades",
        "outercos",
        "outerexp",
        "outersin",
        "outertan",
        "reverse",
        "right_complement",
        "right_hodge_dual",
        "right_weight_dual",
        "scalar_sqrt",
        "sqrt",
        "squared",
        "uncomplement",
        "undual",
        "unit",
        "weight_part",
    )

    specs = [_gram_operation(name, 1) for name in unary]
    specs.extend(
        _gram_operation(name, 2)
        for name in (
            "antidot_product",
            "anticommutator",
            "antiwedge",
            "commutator",
            "doran_lasenby_inner",
            "geometric_antiproduct",
            "half_anticommutator",
            "half_commutator",
            "hestenes_inner",
            "jordan_product",
            "left_contraction",
            "left_interior_product",
            "lie_bracket",
            "metric_inner_product",
            "metric_regressive_product",
            "regressive_product",
            "right_contraction",
            "right_interior_product",
            "sandwich",
            "scalar_product",
        )
    )
    specs.extend(
        (
            _gram_operation(
                "geometric_product",
                2,
                call_policy=LeftFoldCall(),
                operator="*",
            ),
            _gram_operation(
                "outer_product",
                2,
                call_policy=LeftFoldCall(),
                operator="^",
            ),
            _gram_operation("grade", 2, operator="[]"),
            _gram_operation("grades", 2),
            _gram_operation("transwedge", 3),
            _gram_operation("transwedge_antiproduct", 3),
        )
    )
    return tuple(specs)


_operation_items = (*_structural_operations(), *_gram_operations())
_operation_dict = {operation.id: operation for operation in _operation_items}
if len(_operation_dict) != len(_operation_items):
    raise RuntimeError("duplicate operation id in Gram facade catalog")

OPERATIONS: Mapping[str, OperationSpec] = MappingProxyType(_operation_dict)

EXCLUDED_PUBLIC_NAMES: Mapping[str, str] = MappingProxyType(
    {
        "Algebra": "numeric type wrapped by the facade",
        "Multivector": "numeric type wrapped by the facade",
        "dorst_inner": "alias of hestenes_inner",
        "gp": "alias of geometric_product",
        "join": "alias of outer_product",
        "meet": "alias of regressive_product",
        "op": "alias of outer_product",
        "sw": "alias of sandwich",
    }
)


def get_operation(operation_id: str) -> OperationSpec:
    """Return one operation or raise a descriptive lookup error."""
    try:
        return OPERATIONS[operation_id]
    except KeyError as error:
        raise KeyError(f"unknown Gram facade operation {operation_id!r}") from error


__all__ = [
    "CallPolicy",
    "EXCLUDED_PUBLIC_NAMES",
    "FixedCall",
    "LeftFoldCall",
    "OPERATIONS",
    "OperationSpec",
    "get_operation",
]
