"""Immutable, format-neutral expression provenance nodes."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Any

from ..names import Name


class Expr:
    """Marker base class for immutable expression provenance."""

    __slots__ = ()


def _require_name(value: Name | str) -> Name:
    if isinstance(value, Name):
        return value
    if isinstance(value, str):
        return Name(value)
    raise TypeError("symbol name must be a Name or string")


def _finite_float(value: Any, *, field: str) -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"{field} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


@dataclass(frozen=True, slots=True, init=False)
class Symbol(Expr):
    """A semantic symbol whose spelling is selected only while rendering."""

    name: Name

    def __init__(self, name: Name | str) -> None:
        object.__setattr__(self, "name", _require_name(name))

    @property
    def identifier(self) -> str:
        """The stable ASCII spelling used for environment lookup."""
        return self.name.ascii


@dataclass(frozen=True, slots=True, init=False)
class ScalarLiteral(Expr):
    """A finite scalar coefficient."""

    value: float

    def __init__(self, value: Any) -> None:
        object.__setattr__(self, "value", _finite_float(value, field="scalar literal"))


@dataclass(frozen=True, slots=True, init=False)
class BladeLiteral(Expr):
    """One signed native-mask basis blade."""

    mask: int
    orientation: int

    def __init__(self, mask: int, orientation: int = 1) -> None:
        if not isinstance(mask, Integral) or isinstance(mask, bool):
            raise TypeError("blade mask must be an integer")
        normalized_mask = int(mask)
        if normalized_mask < 0:
            raise ValueError("blade mask must be non-negative")
        if not isinstance(orientation, Integral) or isinstance(orientation, bool):
            raise TypeError("blade orientation must be +1 or -1")
        normalized_orientation = int(orientation)
        if normalized_orientation not in {-1, 1}:
            raise ValueError("blade orientation must be +1 or -1")
        object.__setattr__(self, "mask", normalized_mask)
        object.__setattr__(self, "orientation", normalized_orientation)


@dataclass(frozen=True, slots=True, init=False)
class MultivectorLiteral(Expr):
    """Immutable native-mask coefficient data for one multivector."""

    coefficients: tuple[float, ...]

    def __init__(self, coefficients: Iterable[Any]) -> None:
        if isinstance(coefficients, (str, bytes)) or not isinstance(coefficients, Iterable):
            raise TypeError("multivector coefficients must be an iterable of real numbers")
        normalized = tuple(_finite_float(value, field="multivector coefficient") for value in coefficients)
        if not normalized or len(normalized) & (len(normalized) - 1):
            raise ValueError("multivector coefficient count must be a non-zero power of two")
        object.__setattr__(self, "coefficients", normalized)


@dataclass(frozen=True, slots=True, init=False)
class Call(Expr):
    """A catalog operation applied to expression operands and parameters."""

    operation_id: str
    operands: tuple[Expr, ...]
    parameters: tuple[tuple[str, Any], ...]

    def __init__(
        self,
        operation_id: str,
        operands: Iterable[Expr],
        parameters: Mapping[str, Any] | Iterable[tuple[str, Any]] = (),
    ) -> None:
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("operation id must be a non-empty string")
        normalized_operands = tuple(operands)
        if any(not isinstance(operand, Expr) for operand in normalized_operands):
            raise TypeError("call operands must be expression nodes")

        # Local import keeps the node model independent of the numeric core.
        from ..facade.catalog import get_operation

        try:
            operation = get_operation(operation_id)
        except KeyError as error:
            raise ValueError(f"unknown expression operation {operation_id!r}") from error
        if len(normalized_operands) != operation.expression_arity:
            raise ValueError(
                f"{operation_id} expression expects {operation.expression_arity} operands, "
                f"got {len(normalized_operands)}"
            )
        normalized_parameters = operation.normalize_expression_parameters(parameters)
        object.__setattr__(self, "operation_id", operation_id)
        object.__setattr__(self, "operands", normalized_operands)
        object.__setattr__(self, "parameters", normalized_parameters)


Expression = Expr


__all__ = [
    "BladeLiteral",
    "Call",
    "Expr",
    "Expression",
    "MultivectorLiteral",
    "ScalarLiteral",
    "Symbol",
]
