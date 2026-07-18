"""Operation metadata for the core-backed Galaga facade.

This module owns numeric call shape and format-neutral expression schemas. A
numeric evaluator and expression node remain binary even when the public
facade accepts a variadic associative product. Rendering state stays outside
the catalog.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from types import MappingProxyType
from typing import Any, Literal, Protocol, cast

from .. import core


class CallPolicy(Protocol):
    """Adapt a public call shape to one numeric evaluator."""

    def invoke(
        self,
        operation: OperationSpec,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> Any: ...


def _identity_parameter(value: Any) -> Any:
    return value


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    """One normalized expression parameter accepted by an operation."""

    name: str
    positional: bool = False
    required: bool = False
    normalize: Callable[[Any], Any] = _identity_parameter

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("parameter name must be a non-empty string")
        if self.positional and not self.required:
            raise ValueError("positional expression parameters must be required")
        if not callable(self.normalize):
            raise TypeError("parameter normalizer must be callable")


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
    expression_arity: int | None = None
    parameters: tuple[ParameterSpec, ...] = ()
    result_kind: Literal["multivector", "scalar", "predicate", "dynamic"] = "multivector"

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("operation id must not be empty")
        if self.arity < 1:
            raise ValueError("operation arity must be positive")
        if any(not isinstance(parameter, ParameterSpec) for parameter in self.parameters):
            raise TypeError("operation parameters must be ParameterSpec values")
        expression_arity = self.arity if self.expression_arity is None else self.expression_arity
        if not isinstance(expression_arity, int) or isinstance(expression_arity, bool) or expression_arity < 1:
            raise ValueError("expression arity must be a positive integer")
        positional_parameters = sum(parameter.positional for parameter in self.parameters)
        if expression_arity + positional_parameters != self.arity:
            raise ValueError(
                f"{self.id} expression arity and positional parameters must total evaluator arity {self.arity}"
            )
        names = tuple(parameter.name for parameter in self.parameters)
        if len(set(names)) != len(names):
            raise ValueError(f"{self.id} expression parameter names must be unique")
        if self.result_kind not in {"multivector", "scalar", "predicate", "dynamic"}:
            raise ValueError("result kind must be 'multivector', 'scalar', 'predicate', or 'dynamic'")
        object.__setattr__(self, "expression_arity", expression_arity)

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Evaluate after applying this operation's public call policy."""
        return self.call_policy.invoke(self, args, kwargs)

    def bind_expression_call(
        self,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any],
    ) -> tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]]:
        """Split evaluator arguments into expression operands and parameters."""
        if len(args) != self.arity:
            raise TypeError(f"{self.id} expects {self.arity} evaluator arguments, got {len(args)}")
        expression_arity = self.expression_arity
        if expression_arity is None:  # pragma: no cover - normalized in __post_init__
            raise RuntimeError("expression arity was not normalized")
        operands = args[:expression_arity]
        positional_values = args[expression_arity:]
        values: dict[str, Any] = {}
        positional_specs = tuple(parameter for parameter in self.parameters if parameter.positional)
        for parameter, value in zip(positional_specs, positional_values, strict=True):
            values[parameter.name] = value
        for name, value in kwargs.items():
            if name in values:
                raise TypeError(f"{self.id} parameter {name!r} was supplied more than once")
            values[name] = value
        return operands, self.normalize_expression_parameters(values)

    def normalize_expression_parameters(
        self,
        parameters: Mapping[str, Any] | Iterable[tuple[str, Any]],
    ) -> tuple[tuple[str, Any], ...]:
        """Validate and freeze expression parameters in schema order."""
        items = tuple(parameters.items()) if isinstance(parameters, Mapping) else tuple(parameters)
        if any(not isinstance(name, str) or not name for name, _ in items):
            raise ValueError(f"{self.id} expression parameter names must be non-empty strings")
        if len({name for name, _ in items}) != len(items):
            raise ValueError(f"{self.id} expression parameters must not contain duplicate names")
        supplied = {cast(str, name): value for name, value in items}
        known = {parameter.name for parameter in self.parameters}
        unknown: set[str] = set(supplied) - known
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"{self.id} has no expression parameter named: {names}")
        missing = [
            parameter.name for parameter in self.parameters if parameter.required and parameter.name not in supplied
        ]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"{self.id} requires expression parameter(s): {names}")
        return tuple(
            (parameter.name, _freeze_parameter(parameter.normalize(supplied[parameter.name])))
            for parameter in self.parameters
            if parameter.name in supplied
        )

    def invoke_expression(
        self,
        operands: tuple[Any, ...],
        parameters: Mapping[str, Any] | Iterable[tuple[str, Any]] = (),
    ) -> Any:
        """Evaluate one canonical expression node through this catalog spec."""
        expression_arity = self.expression_arity
        if expression_arity is None:  # pragma: no cover - normalized in __post_init__
            raise RuntimeError("expression arity was not normalized")
        if len(operands) != expression_arity:
            raise TypeError(f"{self.id} expression expects {expression_arity} operands, got {len(operands)}")
        normalized = dict(self.normalize_expression_parameters(parameters))
        positional = [
            normalized[parameter.name]
            for parameter in self.parameters
            if parameter.positional and parameter.name in normalized
        ]
        keywords = {
            parameter.name: normalized[parameter.name]
            for parameter in self.parameters
            if not parameter.positional and parameter.name in normalized
        }
        return self.evaluate(*operands, *positional, **keywords)


def _core_operation(
    name: str,
    arity: int,
    *,
    call_policy: CallPolicy | None = None,
    operator: str | None = None,
    expression_arity: int | None = None,
    parameters: tuple[ParameterSpec, ...] = (),
    result_kind: Literal["multivector", "scalar", "predicate", "dynamic"] = "multivector",
) -> OperationSpec:
    return OperationSpec(
        id=name,
        arity=arity,
        evaluate=getattr(core, name),
        call_policy=call_policy or FixedCall(),
        operator=operator,
        expression_arity=expression_arity,
        parameters=parameters,
        result_kind=result_kind,
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
            expression_arity=1,
            parameters=(ParameterSpec("scalar", positional=True, required=True, normalize=_normalize_real),),
        ),
        OperationSpec(
            "scalar_divide",
            2,
            lambda value, scalar: value / scalar,
            expression_arity=1,
            parameters=(ParameterSpec("scalar", positional=True, required=True, normalize=_normalize_real),),
        ),
        OperationSpec(
            "power",
            2,
            lambda value, exponent: value**exponent,
            expression_arity=1,
            parameters=(ParameterSpec("exponent", positional=True, required=True, normalize=_normalize_integer),),
        ),
    )


def _core_operations() -> tuple[OperationSpec, ...]:
    unary = (
        "antimetric_apply",
        "antireverse",
        "bulk_part",
        "complement",
        "conjugate",
        "dual",
        "even_grades",
        "exp",
        "grade_involution",
        "left_complement",
        "left_hodge_dual",
        "left_weight_dual",
        "metric_apply",
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
        "squared",
        "uncomplement",
        "undual",
        "weight_part",
    )

    specs = [_core_operation(name, 1) for name in unary]
    specs.extend(
        _core_operation(
            name,
            1,
            parameters=(ParameterSpec("atol", normalize=_normalize_tolerance),),
            result_kind="predicate",
        )
        for name in ("is_basis_blade", "is_bivector", "is_even", "is_rotor", "is_scalar", "is_vector")
    )
    specs.extend(
        (
            _core_operation(
                "inverse",
                1,
                parameters=(
                    ParameterSpec("rtol", normalize=_normalize_tolerance),
                    ParameterSpec("atol", normalize=_normalize_tolerance),
                ),
            ),
            _core_operation(
                "log",
                1,
                parameters=(ParameterSpec("atol", normalize=_normalize_tolerance),),
            ),
            _core_operation(
                "sqrt",
                1,
                parameters=(ParameterSpec("atol", normalize=_normalize_tolerance),),
                result_kind="dynamic",
            ),
            _core_operation(
                "unit",
                1,
                parameters=(ParameterSpec("atol", normalize=_normalize_tolerance),),
            ),
            _core_operation("scalar_sqrt", 1, result_kind="dynamic"),
            _core_operation("norm", 1, result_kind="scalar"),
        )
    )
    specs.extend(
        _core_operation(name, 2)
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
            _core_operation(
                "geometric_product",
                2,
                call_policy=LeftFoldCall(),
                operator="*",
            ),
            _core_operation(
                "outer_product",
                2,
                call_policy=LeftFoldCall(),
                operator="^",
            ),
            _core_operation(
                "grade",
                2,
                operator="[]",
                expression_arity=1,
                parameters=(ParameterSpec("target", positional=True, required=True, normalize=_normalize_grade),),
            ),
            _core_operation(
                "grades",
                2,
                expression_arity=1,
                parameters=(ParameterSpec("targets", positional=True, required=True, normalize=_normalize_grades),),
            ),
            _core_operation(
                "transwedge",
                3,
                expression_arity=2,
                parameters=(ParameterSpec("order", positional=True, required=True, normalize=_normalize_integer),),
            ),
            _core_operation(
                "transwedge_antiproduct",
                3,
                expression_arity=2,
                parameters=(ParameterSpec("order", positional=True, required=True, normalize=_normalize_integer),),
            ),
        )
    )
    return tuple(specs)


def _normalize_real(value: Any) -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError("expression parameter must be a real number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError("expression parameter must be finite")
    return normalized


def _normalize_tolerance(value: Any) -> float:
    normalized = _normalize_real(value)
    if normalized < 0:
        raise ValueError("expression tolerance must be non-negative")
    return normalized


def _normalize_integer(value: Any) -> int:
    if not isinstance(value, Integral) or isinstance(value, bool):
        raise TypeError("expression parameter must be an integer")
    return int(value)


def _normalize_grade(value: Any) -> int | str:
    if isinstance(value, str) and value in {"even", "odd"}:
        return str(value)
    return _normalize_integer(value)


def _normalize_grades(value: Any) -> tuple[int, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise TypeError("grade targets must be an iterable of integers")
    return tuple(_normalize_integer(target) for target in value)


def _freeze_parameter(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple(sorted((key, _freeze_parameter(item)) for key, item in value.items()))
    if isinstance(value, (str, bytes)):
        return value
    try:
        hash(value)
    except TypeError:
        if isinstance(value, Iterable):
            return tuple(_freeze_parameter(item) for item in value)
        raise TypeError(f"expression parameter {value!r} is not immutable") from None
    return value


_operation_items = (*_structural_operations(), *_core_operations())
_operation_dict = {operation.id: operation for operation in _operation_items}
if len(_operation_dict) != len(_operation_items):
    raise RuntimeError("duplicate operation id in core facade catalog")

OPERATIONS: Mapping[str, OperationSpec] = MappingProxyType(_operation_dict)

EXCLUDED_PUBLIC_NAMES: Mapping[str, str] = MappingProxyType(
    {
        "Algebra": "numeric type wrapped by the facade",
        "Multivector": "numeric type wrapped by the facade",
        "OPERATION_ALIASES": "operation alias metadata",
        **{alias: f"alias of {canonical}" for alias, canonical in core.OPERATION_ALIASES.items()},
    }
)


def get_operation(operation_id: str) -> OperationSpec:
    """Return one operation or raise a descriptive lookup error."""
    try:
        return OPERATIONS[operation_id]
    except KeyError as error:
        raise KeyError(f"unknown core facade operation {operation_id!r}") from error


__all__ = [
    "CallPolicy",
    "EXCLUDED_PUBLIC_NAMES",
    "FixedCall",
    "LeftFoldCall",
    "OPERATIONS",
    "OperationSpec",
    "ParameterSpec",
    "get_operation",
]
