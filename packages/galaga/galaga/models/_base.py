"""Shared lifecycle and algebraic constructions for runtime geometry models."""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Real
from types import MappingProxyType
from typing import Literal, TypedDict, Unpack

import numpy as np

from ..blades import BladeRef
from ..expression import Call, Expr, Symbol
from ..facade import (
    Algebra,
    Multivector,
    antimetric_apply,
    complement,
    metric_apply,
    outer_product,
    regressive_product,
    right_hodge_dual,
    right_weight_dual,
    scalar_product,
    squared,
)

CGAExpressionForm = Literal["operator", "expanded"]


class _RoleParameters(TypedDict, total=False):
    origin: tuple[int, int]
    infinity: tuple[int, int]


def _require_expression_form(value: object) -> CGAExpressionForm:
    if value not in ("operator", "expanded"):
        raise ValueError("expression_form must be 'operator' or 'expanded'")
    return value


def _require_nonnegative_tolerance(value: object) -> None:
    tolerance(value)


def tolerance(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("atol must be a real number")
    result = float(value)
    if not np.isfinite(result) or result < 0:
        raise ValueError("atol must be finite and non-negative")
    return result


def finite_real(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def coordinates(value: Iterable[Real], *, expected: int) -> tuple[float, ...]:
    result = tuple(finite_real(item, name="coordinate") for item in value)
    if len(result) != expected:
        raise ValueError(f"expected {expected} coordinates")
    return result


class _GeometryModel:
    __slots__ = ("_algebra", "_expr", "_roles")
    _model_id: str
    _preset_description: str

    def __init__(self, algebra: Algebra, *, expr: bool | None = None) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        selected = algebra.expr if expr is None else expr
        if not isinstance(selected, bool):
            raise TypeError("expr must be a boolean")
        if algebra.model is None or algebra.model.id != self._model_id:
            raise ValueError(f"{type(self).__name__} requires {self._preset_description}")
        self._algebra = algebra
        self._expr = selected
        self._roles = MappingProxyType(dict(algebra.model.roles))

    @property
    def algebra(self) -> Algebra:
        return self._algebra

    @property
    def expr(self) -> bool:
        return self._expr

    def _resolve_expr(self, value: bool | None) -> bool:
        if value is None:
            return self._expr
        if not isinstance(value, bool):
            raise TypeError("expr must be a boolean")
        return value

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("expected a Galaga Multivector")
        if value.algebra is not self._algebra:
            raise ValueError("multivector must belong to the model algebra; different numeric algebra or facade owner")
        if not np.all(np.isfinite(value.data)):
            raise ValueError("multivector coefficients must be finite")

    def _check_pair(self, left: Multivector, right: Multivector) -> None:
        self._check_value(left)
        self._check_value(right)

    def _coordinate_vector(
        self, values: tuple[float, ...], refs: tuple[BladeRef, ...], *, tracking: bool
    ) -> Multivector:
        """Place validated coordinates in the signed semantic role frame."""
        data = np.zeros(self.algebra.dim)
        for coordinate, ref in zip(values, refs, strict=True):
            data[ref.mask] = ref.orientation * coordinate
        return self.algebra.multivector(data, expr=tracking)

    def _validate_vector_roles(self, refs: tuple[BladeRef, ...]) -> None:
        if len(refs) != self.algebra.n or {ref.mask for ref in refs} != {1 << i for i in range(self.algebra.n)}:
            raise ValueError("model roles must identify every basis vector exactly once")

    @staticmethod
    def _role(ref: BladeRef) -> tuple[int, int]:
        return ref.mask, ref.orientation

    @staticmethod
    def _expression_operand(value: Multivector) -> Expr:
        if value.name is not None:
            return Symbol(value.name)
        if value.expr is not None:
            return value.expr
        expression = value.with_expr().expr
        if expression is None:
            raise RuntimeError("failed to construct expression provenance")
        return expression

    def _semantic(
        self,
        result: Multivector,
        operation_id: str,
        *values: Multivector,
        tracking: bool | None = None,
        **parameters: object,
    ) -> Multivector:
        if tracking is False:
            return result.without_expr()
        if (
            tracking is not True
            and not self._expr
            and all(value.name is None and value.expr is None for value in values)
        ):
            return result
        return result.with_expr(Call(operation_id, tuple(self._expression_operand(v) for v in values), parameters))


class _ProjectiveBase(_GeometryModel):
    __slots__ = ("_euclidean_refs", "_projective_ref")

    @property
    def projective(self) -> Multivector:
        return self.algebra.blade(self._projective_ref, expr=self.expr)

    def _validate_metric(self) -> None:
        refs = (*self._euclidean_refs, self._projective_ref)
        self._validate_vector_roles(refs)
        vectors = tuple(self.algebra.blade(ref, expr=False) for ref in refs)
        gram = np.array([[float(scalar_product(a, b)) for b in vectors] for a in vectors])
        expected = np.diag((*([1.0] * len(self._euclidean_refs)), 0.0))
        if not np.array_equal(gram, expected):
            raise ValueError("projective roles require a normalized Euclidean block and one orthogonal null vector")

    def bulk_part(self, value: Multivector) -> Multivector:
        """Project onto blades without the projective null direction."""
        self._check_value(value)
        return self._semantic(metric_apply(value), "projective_bulk_part", value)

    def weight_part(self, value: Multivector) -> Multivector:
        """Project onto blades containing the projective null direction."""
        self._check_value(value)
        return self._semantic(antimetric_apply(value), "projective_weight_part", value)


class _ConformalBase(_GeometryModel):
    _radius_square_sign = -1

    __slots__ = ("_base_refs", "_origin_ref", "_infinity_ref", "_null_pair", "_expression_form")

    def _conformal_metric(
        self, expected_base: np.ndarray, *, required_pair: float | None = None, metric_atol: float = 1e-12
    ) -> float:
        refs = (*self._base_refs, self._origin_ref, self._infinity_ref)
        self._validate_vector_roles(refs)
        vectors = tuple(self.algebra.blade(ref, expr=False) for ref in refs)
        gram = np.array([[float(scalar_product(a, b)) for b in vectors] for a in vectors])
        size = len(self._base_refs)
        if not np.allclose(gram[:size, :size], expected_base, rtol=0, atol=metric_atol):
            raise ValueError("conformal base roles have an incompatible Gram block")
        if np.any(np.abs(gram[:size, size:]) > metric_atol):
            raise ValueError("conformal null roles must be orthogonal to the base space")
        if np.any(np.abs(np.diag(gram)[size:]) > metric_atol):
            raise ValueError("conformal origin and infinity roles must be null")
        pairing = float(gram[size, size + 1])
        if not np.isfinite(pairing) or abs(pairing) <= metric_atol:
            raise ValueError("conformal null roles must have a finite nonzero mutual product")
        if required_pair is not None and pairing != required_pair:
            raise ValueError("CSTA origin·infinity must equal -1")
        return pairing

    def _embed(self, vector: Multivector, *, tracking: bool) -> Multivector:
        origin = self.algebra.blade(self._origin_ref, expr=tracking)
        infinity = self.algebra.blade(self._infinity_ref, expr=tracking)
        return origin + vector + squared(vector) * infinity / (-2.0 * self._null_pair)

    @property
    def null_pair(self) -> float:
        """The configured mutual product ``eo·einf``."""
        return self._null_pair

    @property
    def origin(self) -> Multivector:
        """The native conformal-origin basis vector ``eo``."""
        return self._algebra.blade(self._origin_ref, expr=self._expr)

    @property
    def infinity(self) -> Multivector:
        """The native conformal-infinity basis vector ``einf``."""
        return self._algebra.blade(self._infinity_ref, expr=self._expr)

    def weight(self, value: Multivector, *, expression_form: CGAExpressionForm | None = None) -> Multivector:
        """Return a conformal vector's homogeneous origin coefficient."""
        return self._weight_value(value, expression_form=expression_form)

    def _weight_value(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return a conformal vector's homogeneous origin coefficient."""
        self._require_conformal_vector(value)
        result = scalar_product(value, self.infinity) / self._null_pair
        return self._semantic(
            result,
            "weight",
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def homogenize(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Scale a finite conformal vector so its origin coefficient is one."""
        _require_nonnegative_tolerance(atol)
        selected = self._resolve_expression_form(expression_form)
        homogeneous_weight = self._weight_value(value, expression_form=selected)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("cannot homogenize a conformal vector with zero weight")
        result = value / homogeneous_weight
        return self._semantic(
            result,
            "homogenize",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def down(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Extract the base-space center of a finite conformal vector."""
        selected = self._resolve_expression_form(expression_form)
        normalized = self.homogenize(value, atol=atol, expression_form=selected)
        data = np.zeros(self._algebra.dim)
        for ref in self._base_refs:
            data[ref.mask] = normalized.coefficient(ref.mask)
        result = self._algebra.multivector(data, expr=False)
        return self._semantic(
            result,
            "down",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def coordinates(self, value: Multivector, *, atol: float = 1e-12) -> np.ndarray:
        """Return the base-space center as an immutable coordinate array."""
        center = self.down(value, atol=atol)
        result = np.array(
            [ref.orientation * center.coefficient(ref.mask) for ref in self._base_refs],
            dtype=float,
        )
        result.setflags(write=False)
        return result

    def radius_squared(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the signed squared radius encoded by a round-point vector."""
        _require_nonnegative_tolerance(atol)
        selected = self._resolve_expression_form(expression_form)
        homogeneous_weight = self._weight_value(value, expression_form=selected)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("an infinite conformal vector has no finite round radius")
        result = self._radius_square_sign * squared(value) / (homogeneous_weight * homogeneous_weight)
        return self._semantic(
            result,
            "radius_squared",
            value,
            **({"sign": self._radius_square_sign} if self._radius_square_sign != -1 else {}),
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def dual(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the CGA wiki dual ``complement(metric_apply(value))``."""
        self._check_value(value)
        tracked = self._tracked(value)
        if self._resolve_expression_form(expression_form) == "operator":
            return right_hodge_dual(tracked)
        return complement(metric_apply(tracked))

    def antidual(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the CGA wiki antidual ``complement(antimetric_apply(value))``."""
        self._check_value(value)
        tracked = self._tracked(value)
        if self._resolve_expression_form(expression_form) == "operator":
            return right_weight_dual(tracked)
        return complement(antimetric_apply(tracked))

    def round_bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing neither the origin nor infinity basis vector."""
        return self._component_part(
            value,
            "round_bulk_part",
            contains_origin=False,
            contains_infinity=False,
            expression_form=expression_form,
        )

    def round_weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing the origin but not the infinity basis vector."""
        return self._component_part(
            value,
            "round_weight_part",
            contains_origin=True,
            contains_infinity=False,
            expression_form=expression_form,
        )

    def flat_bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing infinity but not the origin basis vector."""
        return self._component_part(
            value,
            "flat_bulk_part",
            contains_origin=False,
            contains_infinity=True,
            expression_form=expression_form,
        )

    def flat_weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing both the origin and infinity basis vectors."""
        return self._component_part(
            value,
            "flat_weight_part",
            contains_origin=True,
            contains_infinity=True,
            expression_form=expression_form,
        )

    def round_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return all terms that do not contain the infinity basis vector."""
        return self._role_part(
            value,
            "round_part",
            role=self._infinity_ref,
            contains_role=False,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def flat_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return all terms that contain the infinity basis vector."""
        return self._role_part(
            value,
            "flat_part",
            role=self._infinity_ref,
            contains_role=True,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return CGA terms that do not contain the origin basis vector."""
        return self._role_part(
            value,
            "conformal_bulk_part",
            role=self._origin_ref,
            contains_role=False,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return CGA terms that contain the origin basis vector."""
        return self._role_part(
            value,
            "conformal_weight_part",
            role=self._origin_ref,
            contains_role=True,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def conformal_conjugate(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Preserve round terms and negate flat terms."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = self.round_part(value, expression_form=selected) - self.flat_part(
            value,
            expression_form=selected,
        )
        return self._semantic(
            result,
            "conformal_conjugate",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def attitude(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Extract a geometry's purely directional object."""
        self._require_geometry(value)
        result = regressive_product(value, complement(self.origin))
        return self._semantic(
            result,
            "attitude",
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def carrier(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the lowest-dimensional flat geometry containing ``value``."""
        self._require_geometry(value)
        result = outer_product(value, self.infinity)
        if not np.any(np.abs(result.data) > 1e-12):
            raise ValueError("carrier requires a round geometry with a nonzero round part")
        return self._semantic(
            result,
            "carrier",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def cocarrier(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the carrier of ``value``'s antidual."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = self.carrier(self.antidual(value), expression_form=selected)
        return self._semantic(
            result,
            "cocarrier",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def _component_part(
        self,
        value: Multivector,
        operation_id: str,
        *,
        contains_origin: bool,
        contains_infinity: bool,
        expression_form: CGAExpressionForm | None,
    ) -> Multivector:
        self._require_geometry(value)
        data = np.zeros_like(value.data)
        for mask, coefficient in enumerate(value.data):
            if (
                bool(mask & self._origin_ref.mask) is contains_origin
                and bool(mask & self._infinity_ref.mask) is contains_infinity
            ):
                data[mask] = coefficient
        result = self._algebra.multivector(data, expr=False)
        return self._semantic(
            result,
            operation_id,
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def _role_part(
        self,
        value: Multivector,
        operation_id: str,
        *,
        role: BladeRef,
        contains_role: bool,
        expression_form: CGAExpressionForm | None,
        **parameters: Unpack[_RoleParameters],
    ) -> Multivector:
        self._require_geometry(value)
        data = np.zeros_like(value.data)
        for mask, coefficient in enumerate(value.data):
            if bool(mask & role.mask) is contains_role:
                data[mask] = coefficient
        result = self._algebra.multivector(data, expr=False)
        return self._semantic(
            result,
            operation_id,
            value,
            expression_form=expression_form,
            **parameters,
        )

    def _tracked(self, value: Multivector) -> Multivector:
        if self._expr and value.name is None and value.expr is None:
            return value.with_expr()
        return value

    def _semantic(
        self,
        result: Multivector,
        operation_id: str,
        *values: Multivector,
        expression_form: CGAExpressionForm | None = None,
        tracking: bool | None = None,
        expanded: Expr | None = None,
        **parameters: object,
    ) -> Multivector:
        selected = self._resolve_expression_form(expression_form)
        if tracking is False:
            return result.without_expr() if result.expr is not None else result
        if (
            tracking is not True
            and not self._expr
            and all(value.name is None and value.expr is None for value in values)
        ):
            return result
        operator = Call(
            operation_id,
            tuple(self._expression_operand(value) for value in values),
            parameters,
        )
        if selected == "operator":
            return result.with_expr(operator)
        formula = expanded if expanded is not None else result.expr
        return result.with_expr(operator if formula is None else formula)

    def _resolve_expression_form(
        self,
        value: CGAExpressionForm | None,
    ) -> CGAExpressionForm:
        if value is None:
            return self._expression_form
        return _require_expression_form(value)

    def _require_conformal_vector(self, value: Multivector) -> None:
        self._check_value(value)
        if value.homogeneous_grade() != 1:
            raise ValueError("expected a homogeneous conformal vector")

    def _require_geometry(self, value: Multivector) -> int:
        self._check_value(value)
        value_grade = value.homogeneous_grade()
        if value_grade is None or not 1 <= value_grade < self._algebra.n:
            raise ValueError("expected a homogeneous conformal geometry of grade 1 through n - 1")
        return value_grade

    att = attitude
    car = carrier
    ccr = cocarrier
    homo = homogenize


def ordered_euclidean_roles(roles: MappingProxyType[str, BladeRef]) -> tuple[BladeRef, ...]:
    indexed: dict[int, BladeRef] = {}
    for name, ref in roles.items():
        if not name.startswith("euclidean_"):
            continue
        suffix = name.removeprefix("euclidean_")
        if not suffix.isdecimal() or int(suffix) < 1:
            raise ValueError("Euclidean model roles must be numbered from euclidean_1")
        if name != f"euclidean_{int(suffix)}" or int(suffix) in indexed:
            raise ValueError("Euclidean model roles must use unique indices euclidean_1, euclidean_2, ...")
        indexed[int(suffix)] = ref
    if not indexed or set(indexed) != set(range(1, len(indexed) + 1)):
        raise ValueError("Euclidean model roles must be contiguous from euclidean_1")
    return tuple(indexed[index] for index in range(1, len(indexed) + 1))
