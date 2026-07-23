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
    render: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("parameter name must be a non-empty string")
        if self.positional and not self.required:
            raise ValueError("positional expression parameters must be required")
        if not callable(self.normalize):
            raise TypeError("parameter normalizer must be callable")
        if not isinstance(self.render, bool):
            raise TypeError("expression parameter render flag must be a boolean")


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


def _cga_semantic_operations() -> tuple[OperationSpec, ...]:
    """Operations used by CGA provenance without enlarging the numeric facade."""

    def role(name: str) -> ParameterSpec:
        return ParameterSpec(
            name,
            positional=True,
            required=True,
            normalize=_normalize_blade_role,
            render=False,
        )

    infinity = (role("infinity"),)
    origin = (role("origin"),)
    origin_and_infinity = (role("origin"), role("infinity"))
    tolerance = ParameterSpec("atol", normalize=_normalize_tolerance, render=False)
    return (
        OperationSpec(
            "cga_scalar_norm_root",
            1,
            _cga_scalar_norm_root,
            parameters=(tolerance,),
        ),
        OperationSpec(
            "cga_antiscalar_norm_root",
            1,
            _cga_antiscalar_norm_root,
            parameters=(tolerance,),
        ),
        OperationSpec(
            "up",
            3,
            _cga_up,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "round_point",
            4,
            _cga_round_point,
            expression_arity=2,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "weight",
            3,
            _cga_weight,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "homogenize",
            3,
            _cga_homogenize,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
        OperationSpec(
            "down",
            3,
            _cga_down,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
        OperationSpec(
            "radius_squared",
            3,
            _cga_radius_squared,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
        OperationSpec(
            "attitude",
            2,
            _cga_attitude,
            expression_arity=1,
            parameters=(role("origin"),),
        ),
        OperationSpec(
            "carrier",
            2,
            _cga_carrier,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "cocarrier",
            2,
            _cga_cocarrier,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "center",
            2,
            _cga_center,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "flat_center",
            2,
            _cga_flat_center,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "container",
            2,
            _cga_container,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "partner",
            3,
            _cga_partner,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec("expansion", 2, _cga_expansion),
        OperationSpec("projection", 2, _cga_projection),
        OperationSpec(
            "round_bulk_part",
            3,
            _cga_round_bulk_part,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "round_weight_part",
            3,
            _cga_round_weight_part,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "flat_bulk_part",
            3,
            _cga_flat_bulk_part,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "flat_weight_part",
            3,
            _cga_flat_weight_part,
            expression_arity=1,
            parameters=origin_and_infinity,
        ),
        OperationSpec(
            "round_part",
            2,
            _cga_round_part,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "flat_part",
            2,
            _cga_flat_part,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "conformal_bulk_part",
            2,
            _cga_conformal_bulk_part,
            expression_arity=1,
            parameters=origin,
        ),
        OperationSpec(
            "conformal_weight_part",
            2,
            _cga_conformal_weight_part,
            expression_arity=1,
            parameters=origin,
        ),
        OperationSpec(
            "conformal_conjugate",
            2,
            _cga_conformal_conjugate,
            expression_arity=1,
            parameters=infinity,
        ),
        OperationSpec(
            "weighted_center_norm",
            2,
            _cga_weighted_center_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "weighted_radius_norm",
            3,
            _cga_weighted_radius_norm,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
        OperationSpec(
            "round_bulk_norm",
            2,
            _cga_round_bulk_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "round_weight_norm",
            2,
            _cga_round_weight_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "flat_bulk_norm",
            2,
            _cga_flat_bulk_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "flat_weight_norm",
            2,
            _cga_flat_weight_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "center_norm",
            2,
            _cga_center_norm,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "radius_norm",
            3,
            _cga_radius_norm,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
        OperationSpec(
            "center_distance",
            2,
            _cga_center_distance,
            expression_arity=1,
            parameters=(*infinity, tolerance),
        ),
        OperationSpec(
            "radius",
            3,
            _cga_radius,
            expression_arity=1,
            parameters=(*origin_and_infinity, tolerance),
        ),
    )


def _cga_up(
    position: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    return _cga_round_point(
        position,
        position.algebra.scalar(0),
        origin,
        infinity,
    )


def _cga_round_point(
    position: core.Multivector,
    radius_squared: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    eo = _role_blade(position, origin)
    einf = _role_blade(position, infinity)
    _require_cga_euclidean_vector(position, origin, infinity)
    if not core.is_scalar(radius_squared):
        raise ValueError("round_point radius_squared must be scalar")
    null_pair = float(core.scalar_product(eo, einf))
    if not math.isfinite(null_pair) or abs(null_pair) <= 1e-12:
        raise ValueError("round_point requires a finite nonzero origin/infinity pairing")
    return eo + position + (core.squared(position) + radius_squared) * einf / (-2.0 * null_pair)


def _cga_weight(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    _require_cga_vector(value)
    eo = _role_blade(value, origin)
    einf = _role_blade(value, infinity)
    null_pair = float(core.scalar_product(eo, einf))
    if not math.isfinite(null_pair) or abs(null_pair) <= 1e-12:
        raise ValueError("weight requires a finite nonzero origin/infinity pairing")
    return core.scalar_product(value, einf) / null_pair


def _cga_homogenize(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    weight = _cga_weight(value, origin, infinity)
    coefficient = float(weight.scalar_part)
    if abs(coefficient) <= atol:
        raise ValueError("cannot homogenize a conformal vector with zero weight")
    return value / coefficient


def _cga_down(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    normalized = _cga_homogenize(value, origin, infinity, atol=atol)
    excluded = {origin[0], infinity[0]}
    return value.algebra.multivector(
        [
            coefficient if mask.bit_count() == 1 and mask not in excluded else 0.0
            for mask, coefficient in enumerate(normalized.data)
        ]
    )


def _cga_radius_squared(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    weight = _cga_weight(value, origin, infinity)
    coefficient = float(weight.scalar_part)
    if abs(coefficient) <= atol:
        raise ValueError("an infinite conformal vector has no finite round radius")
    return -core.squared(value) / (coefficient * coefficient)


def _rga_semantic_operations() -> tuple[OperationSpec, ...]:
    """Operations used by point-based RGA provenance and measurements."""

    projective = ParameterSpec(
        "projective",
        positional=True,
        required=True,
        normalize=_normalize_blade_role,
        render=False,
    )
    tolerance = ParameterSpec("atol", normalize=_normalize_tolerance, render=False)

    def unary_norm(operation_id: str, evaluator: Callable[..., core.Multivector]) -> OperationSpec:
        return OperationSpec(operation_id, 1, evaluator, parameters=(tolerance,))

    return (
        unary_norm("bulk_norm", _rga_bulk_norm),
        unary_norm("weight_norm", _rga_weight_norm),
        unary_norm("geometric_norm", _rga_geometric_norm),
        unary_norm("unitize", _rga_unitize),
        OperationSpec("bulk_contraction", 2, _rga_bulk_contraction),
        OperationSpec("weight_contraction", 2, _rga_weight_contraction),
        OperationSpec("bulk_expansion", 2, _rga_bulk_expansion),
        OperationSpec("weight_expansion", 2, _rga_weight_expansion),
        OperationSpec(
            "homogeneous_distance",
            3,
            _rga_homogeneous_distance,
            expression_arity=2,
            parameters=(projective, tolerance),
        ),
        OperationSpec(
            "homogeneous_angle",
            2,
            _rga_homogeneous_angle,
            parameters=(tolerance,),
        ),
        OperationSpec("orthogonal_projection", 2, _rga_orthogonal_projection),
        OperationSpec("orthogonal_antiprojection", 2, _rga_orthogonal_antiprojection),
        OperationSpec("central_projection", 2, _rga_central_projection),
        OperationSpec("central_antiprojection", 2, _rga_central_antiprojection),
        OperationSpec(
            "support",
            2,
            _rga_support,
            expression_arity=1,
            parameters=(projective,),
        ),
        OperationSpec(
            "antisupport",
            2,
            _rga_antisupport,
            expression_arity=1,
            parameters=(projective,),
        ),
    )


def _rga_bulk_norm(
    value: core.Multivector,
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    return _cga_scalar_norm_root(
        core.metric_inner_product(value, value),
        name="bulk norm",
        atol=atol,
    )


def _rga_weight_norm(
    value: core.Multivector,
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    return _cga_antiscalar_norm_root(
        core.antidot_product(value, value),
        name="weight norm",
        atol=atol,
    )


def _rga_geometric_norm(
    value: core.Multivector,
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    return _rga_bulk_norm(value, atol=atol) + _rga_weight_norm(value, atol=atol)


def _rga_unitize(
    value: core.Multivector,
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    weight = _rga_weight_norm(value, atol=atol)
    magnitude = _cga_blade_magnitude(weight, value.algebra.I, name="weight norm", atol=atol)
    if magnitude <= atol:
        raise ValueError("cannot unitize an element with zero weight norm")
    return value / magnitude


def _rga_bulk_contraction(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    return core.regressive_product(left, core.right_hodge_dual(right))


def _rga_weight_contraction(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    return core.regressive_product(left, core.right_weight_dual(right))


def _rga_bulk_expansion(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    return core.outer_product(left, core.right_hodge_dual(right))


def _rga_weight_expansion(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    return core.outer_product(left, core.right_weight_dual(right))


def _rga_homogeneous_distance(
    left: core.Multivector,
    right: core.Multivector,
    projective: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_rga_geometry(left)
    _require_rga_geometry(right)
    projective_blade = _role_blade(left, projective)
    horizon = core.complement(projective_blade)

    def attitude(value: core.Multivector) -> core.Multivector:
        return core.regressive_product(value, horizon)

    join = core.outer_product(left, right)
    return _rga_bulk_norm(attitude(join), atol=atol) + _rga_weight_norm(
        core.outer_product(left, attitude(right)),
        atol=atol,
    )


def _rga_homogeneous_angle(
    left: core.Multivector,
    right: core.Multivector,
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_rga_geometry(left)
    _require_rga_geometry(right)
    return _rga_bulk_norm(_rga_weight_contraction(left, right), atol=atol) + core.regressive_product(
        _rga_weight_norm(left, atol=atol),
        _rga_weight_norm(right, atol=atol),
    )


def _rga_orthogonal_projection(
    value: core.Multivector,
    onto: core.Multivector,
) -> core.Multivector:
    _require_rga_geometry(value)
    _require_rga_geometry(onto)
    return core.regressive_product(onto, _rga_weight_expansion(value, onto))


def _rga_orthogonal_antiprojection(
    value: core.Multivector,
    onto: core.Multivector,
) -> core.Multivector:
    _require_rga_geometry(value)
    _require_rga_geometry(onto)
    return core.outer_product(onto, _rga_weight_contraction(value, onto))


def _rga_central_projection(
    value: core.Multivector,
    onto: core.Multivector,
) -> core.Multivector:
    _require_rga_geometry(value)
    _require_rga_geometry(onto)
    return core.regressive_product(onto, _rga_bulk_expansion(value, onto))


def _rga_central_antiprojection(
    value: core.Multivector,
    onto: core.Multivector,
) -> core.Multivector:
    _require_rga_geometry(value)
    _require_rga_geometry(onto)
    return core.outer_product(onto, _rga_bulk_contraction(value, onto))


def _rga_support(value: core.Multivector, projective: tuple[int, int]) -> core.Multivector:
    return _rga_orthogonal_projection(_role_blade(value, projective), value)


def _rga_antisupport(value: core.Multivector, projective: tuple[int, int]) -> core.Multivector:
    horizon = core.complement(_role_blade(value, projective))
    return _rga_central_antiprojection(horizon, value)


def _cga_attitude(value: core.Multivector, origin: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    return core.regressive_product(value, core.complement(_role_blade(value, origin)))


def _cga_carrier(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    result = core.outer_product(value, _role_blade(value, infinity))
    if not any(abs(float(coefficient)) > 1e-12 for coefficient in result.data):
        raise ValueError("carrier requires a round geometry with a nonzero round part")
    return result


def _cga_cocarrier(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    return _cga_carrier(core.right_weight_dual(value), infinity)


def _cga_center(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    return core.regressive_product(_cga_cocarrier(value, infinity), value)


def _cga_flat_center(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    return core.regressive_product(
        _cga_cocarrier(value, infinity),
        _cga_carrier(value, infinity),
    )


def _cga_container(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    _require_cga_geometry(value)
    carrier = _cga_carrier(value, infinity)
    return core.outer_product(value, core.right_weight_dual(carrier))


def _cga_partner(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    grade = _require_cga_geometry(value)
    null_pair = float(core.scalar_product(_role_blade(value, origin), _role_blade(value, infinity)))
    if not math.isclose(null_pair, -1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("partner requires the standard eo·einf == -1 normalization")
    result = core.regressive_product(
        _cga_container(core.right_weight_dual(value), infinity),
        _cga_carrier(value, infinity),
    )
    return ((-1) ** (grade + 1)) * result


def _cga_expansion(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    left_grade = _require_cga_geometry(left)
    right_grade = _require_cga_geometry(right)
    if left_grade >= right_grade:
        raise ValueError("expansion requires the second geometry to have higher grade")
    return core.outer_product(left, core.right_weight_dual(right))


def _cga_projection(left: core.Multivector, right: core.Multivector) -> core.Multivector:
    return core.regressive_product(right, _cga_expansion(left, right))


def _cga_round_bulk_part(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    return _cga_component_part(value, origin, infinity, contains_origin=False, contains_infinity=False)


def _cga_round_weight_part(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    return _cga_component_part(value, origin, infinity, contains_origin=True, contains_infinity=False)


def _cga_flat_bulk_part(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    return _cga_component_part(value, origin, infinity, contains_origin=False, contains_infinity=True)


def _cga_flat_weight_part(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
) -> core.Multivector:
    return _cga_component_part(value, origin, infinity, contains_origin=True, contains_infinity=True)


def _cga_component_part(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    contains_origin: bool,
    contains_infinity: bool,
) -> core.Multivector:
    _require_cga_geometry(value)
    _role_blade(value, origin)
    _role_blade(value, infinity)
    origin_mask = origin[0]
    infinity_mask = infinity[0]
    if origin_mask == infinity_mask:
        raise ValueError("CGA expression origin and infinity roles must be distinct")
    data = [
        coefficient
        if bool(mask & origin_mask) is contains_origin and bool(mask & infinity_mask) is contains_infinity
        else 0.0
        for mask, coefficient in enumerate(value.data)
    ]
    return value.algebra.multivector(data)


def _cga_round_part(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    return _cga_role_part(value, infinity, contains_role=False)


def _cga_flat_part(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    return _cga_role_part(value, infinity, contains_role=True)


def _cga_conformal_bulk_part(value: core.Multivector, origin: tuple[int, int]) -> core.Multivector:
    return _cga_role_part(value, origin, contains_role=False)


def _cga_conformal_weight_part(value: core.Multivector, origin: tuple[int, int]) -> core.Multivector:
    return _cga_role_part(value, origin, contains_role=True)


def _cga_role_part(
    value: core.Multivector,
    role: tuple[int, int],
    *,
    contains_role: bool,
) -> core.Multivector:
    _require_cga_geometry(value)
    _role_blade(value, role)
    role_mask = role[0]
    return value.algebra.multivector(
        [coefficient if bool(mask & role_mask) is contains_role else 0.0 for mask, coefficient in enumerate(value.data)]
    )


def _cga_conformal_conjugate(value: core.Multivector, infinity: tuple[int, int]) -> core.Multivector:
    return _cga_round_part(value, infinity) - _cga_flat_part(value, infinity)


def _cga_weighted_center_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    pairing = core.metric_inner_product(value, _cga_conformal_conjugate(value, infinity))
    return _cga_scalar_norm_root(pairing, name="center norm", atol=atol)


def _cga_weighted_radius_norm(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    _require_standard_cga_normalization(value, origin, infinity, operation="weighted_radius_norm")
    return _cga_antiscalar_norm_root(
        core.antidot_product(value, value),
        name="radius norm",
        atol=atol,
    )


def _cga_round_bulk_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    einf = _role_blade(value, infinity)
    carrier = core.outer_product(value, einf)
    reduced = core.regressive_product(carrier, core.complement(einf))
    return _cga_scalar_norm_root(
        core.metric_inner_product(reduced, reduced),
        name="round bulk norm",
        atol=atol,
    )


def _cga_round_weight_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    einf = _role_blade(value, infinity)
    carrier = core.outer_product(value, einf)
    antiscalar = _cga_antiscalar_norm_root(
        core.antidot_product(carrier, carrier),
        name="round weight norm",
        atol=atol,
    )
    return core.regressive_product(antiscalar, core.complement(einf))


def _cga_flat_bulk_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    einf = _role_blade(value, infinity)
    reduced = core.regressive_product(value, core.complement(einf))
    magnitude = _cga_scalar_norm_root(
        core.metric_inner_product(reduced, reduced),
        name="flat bulk norm",
        atol=atol,
    )
    return core.outer_product(magnitude, einf)


def _cga_flat_weight_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_cga_geometry(value)
    einf = _role_blade(value, infinity)
    reduced = core.regressive_product(value, core.complement(einf))
    isolated = core.outer_product(reduced, einf)
    return _cga_antiscalar_norm_root(
        core.antidot_product(isolated, isolated),
        name="flat weight norm",
        atol=atol,
    )


def _cga_center_norm(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    center = _cga_weighted_center_norm(value, infinity, atol=atol)
    weight = _cga_round_weight_magnitude(value, infinity, atol=atol)
    return center / weight


def _cga_radius_norm(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    _require_standard_cga_normalization(value, origin, infinity, operation="radius_norm")
    weighted = _cga_weighted_radius_norm(value, origin, infinity, atol=atol)
    numerator = _cga_blade_magnitude(weighted, value.algebra.I, name="radius norm", atol=atol)
    denominator = _cga_round_weight_magnitude(value, infinity, atol=atol)
    return value.algebra.scalar(numerator / denominator)


def _cga_center_distance(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    return _cga_center_norm(value, infinity, atol=atol)


def _cga_radius(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> core.Multivector:
    return _cga_radius_norm(value, origin, infinity, atol=atol)


def _cga_scalar_norm_root(
    value: core.Multivector,
    *,
    name: str = "CGA norm",
    atol: float,
) -> core.Multivector:
    if not core.is_scalar(value, atol=atol):
        raise ValueError(f"{name} squared must be scalar")
    coefficient = float(value.scalar_part)
    scale = max(1.0, abs(coefficient))
    if coefficient < -atol * scale:
        raise ValueError(f"{name} is not real")
    return value.algebra.scalar(math.sqrt(max(0.0, coefficient)))


def _cga_antiscalar_norm_root(
    value: core.Multivector,
    *,
    name: str = "CGA norm",
    atol: float,
) -> core.Multivector:
    coefficient = _cga_blade_magnitude(
        value,
        value.algebra.I,
        name=f"{name} squared",
        atol=atol,
    )
    scale = max(1.0, abs(coefficient))
    if coefficient < -atol * scale:
        raise ValueError(f"{name} is not real")
    return math.sqrt(max(0.0, coefficient)) * value.algebra.I


def _cga_round_weight_magnitude(
    value: core.Multivector,
    infinity: tuple[int, int],
    *,
    atol: float,
) -> float:
    einf = _role_blade(value, infinity)
    basis = core.complement(einf)
    magnitude = _cga_blade_magnitude(
        _cga_round_weight_norm(value, infinity, atol=atol),
        basis,
        name="round weight norm",
        atol=atol,
    )
    if abs(magnitude) <= atol:
        raise ValueError("normalized conformal measurement requires nonzero round weight")
    return magnitude


def _cga_blade_magnitude(
    value: core.Multivector,
    basis: core.Multivector,
    *,
    name: str,
    atol: float,
) -> float:
    masks = [mask for mask, coefficient in enumerate(basis.data) if coefficient]
    if len(masks) != 1:  # pragma: no cover - internal role/complement invariant
        raise RuntimeError("expected a single basis blade")
    mask = masks[0]
    coefficient = float(value.data[mask] / basis.data[mask])
    scale = max(1.0, abs(coefficient))
    if any(
        abs(float(actual - coefficient * expected)) > atol * scale
        for actual, expected in zip(value.data, basis.data, strict=True)
    ):
        raise ValueError(f"{name} must be proportional to its expected basis blade")
    return coefficient


def _require_standard_cga_normalization(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    operation: str,
) -> None:
    null_pair = float(core.scalar_product(_role_blade(value, origin), _role_blade(value, infinity)))
    if not math.isclose(null_pair, -1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{operation} requires the standard eo·einf == -1 normalization")


def _role_blade(value: core.Multivector, role: tuple[int, int]) -> core.Multivector:
    mask, orientation = role
    if mask >= value.algebra.dim or mask == 0 or mask.bit_count() != 1:
        raise ValueError("CGA expression role must refer to a basis vector")
    blade = value.algebra.blade(mask)
    return blade if orientation == 1 else value.algebra.multivector(-blade.data)


def _require_cga_geometry(value: core.Multivector) -> int:
    grade = value.homogeneous_grade()
    if grade is None or not 1 <= grade < value.algebra.n:
        raise ValueError("expected a homogeneous conformal geometry of grade 1 through n - 1")
    return grade


def _require_cga_vector(value: core.Multivector) -> None:
    if value.homogeneous_grade() != 1:
        raise ValueError("expected a homogeneous conformal vector")


def _require_cga_euclidean_vector(
    value: core.Multivector,
    origin: tuple[int, int],
    infinity: tuple[int, int],
    *,
    atol: float = 1e-12,
) -> None:
    if value.homogeneous_grade(atol=atol) not in {None, 1}:
        raise ValueError("expected a vector in the embedded Euclidean subspace")
    excluded = {origin[0], infinity[0]}
    for mask, coefficient in enumerate(value.data):
        if mask.bit_count() != 1 or mask in excluded:
            if abs(float(coefficient)) > atol:
                raise ValueError("expected a vector in the embedded Euclidean subspace")


def _require_rga_geometry(value: core.Multivector) -> int:
    grade = value.homogeneous_grade()
    if grade is None or not 1 <= grade < value.algebra.n:
        raise ValueError("expected a homogeneous rigid geometry of grade 1 through n - 1")
    return grade


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


def _normalize_blade_role(value: Any) -> tuple[int, int]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise TypeError("model expression role must be a (mask, orientation) pair")
    mask, orientation = value
    normalized_mask = _normalize_integer(mask)
    normalized_orientation = _normalize_integer(orientation)
    if normalized_mask <= 0:
        raise ValueError("model expression role mask must be positive")
    if normalized_orientation not in {-1, 1}:
        raise ValueError("model expression role orientation must be -1 or 1")
    return normalized_mask, normalized_orientation


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

_expression_operation_items = (
    *_operation_items,
    *_cga_semantic_operations(),
    *_rga_semantic_operations(),
)
_expression_operation_dict = {operation.id: operation for operation in _expression_operation_items}
if len(_expression_operation_dict) != len(_expression_operation_items):
    raise RuntimeError("duplicate operation id in facade expression catalog")

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
        return _expression_operation_dict[operation_id]
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
