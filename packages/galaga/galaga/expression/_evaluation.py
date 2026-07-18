"""Catalog-driven evaluation for expression provenance."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Real
from typing import Any, cast

from .. import core
from ..names import Name
from ._nodes import BladeLiteral, Call, Expr, MultivectorLiteral, ScalarLiteral, Symbol


def evaluate(
    expression: Expr,
    *,
    algebra: core.Algebra | Any,
    environment: Mapping[Name | str, Any] | None = None,
) -> Any:
    """Evaluate an expression against one algebra and explicit symbol values."""
    if not isinstance(expression, Expr):
        raise TypeError("expression must be an Expr")
    numeric_algebra, facade_algebra = _resolve_algebra(algebra)
    result = _evaluate(expression, numeric_algebra, environment or {})
    if facade_algebra is not None and isinstance(result, core.Multivector):
        return facade_algebra._wrap(result)
    return result


def _resolve_algebra(algebra: Any) -> tuple[core.Algebra, Any | None]:
    if isinstance(algebra, core.Algebra):
        return algebra, None
    from ..facade._numeric import Algebra as FacadeAlgebra

    if isinstance(algebra, FacadeAlgebra):
        return algebra.numeric, algebra
    raise TypeError("algebra must be a core or facade Algebra")


def _evaluate(expression: Expr, algebra: core.Algebra, environment: Mapping[Name | str, Any]) -> Any:
    if isinstance(expression, Symbol):
        return _resolve_symbol(expression, algebra, environment)
    if isinstance(expression, ScalarLiteral):
        return algebra.scalar(cast(Real, expression.value))
    if isinstance(expression, BladeLiteral):
        if expression.mask >= algebra.dim:
            raise ValueError(f"blade literal mask {expression.mask} is outside algebra dimension {algebra.n}")
        value = algebra.blade(expression.mask)
        return value if expression.orientation == 1 else algebra.multivector(-value.data)
    if isinstance(expression, MultivectorLiteral):
        if len(expression.coefficients) != algebra.dim:
            raise ValueError(
                "multivector literal coefficient count "
                f"{len(expression.coefficients)} does not match algebra dimension {algebra.dim}"
            )
        return algebra.multivector(expression.coefficients)
    if isinstance(expression, Call):
        from ..facade.catalog import get_operation

        operation = get_operation(expression.operation_id)
        operands = tuple(_evaluate(operand, algebra, environment) for operand in expression.operands)
        return operation.invoke_expression(operands, expression.parameters)
    raise TypeError(f"unsupported expression node {type(expression).__name__}")


def _resolve_symbol(symbol: Symbol, algebra: core.Algebra, environment: Mapping[Name | str, Any]) -> Any:
    if symbol.name in environment:
        value = environment[symbol.name]
    elif symbol.identifier in environment:
        value = environment[symbol.identifier]
    else:
        raise KeyError(f"no value supplied for expression symbol {symbol.identifier!r}")

    numeric = getattr(value, "numeric", value)
    if isinstance(numeric, core.Multivector):
        if numeric.algebra is not algebra:
            raise ValueError(f"symbol {symbol.identifier!r} belongs to a different algebra")
        return numeric
    if isinstance(numeric, Real) and not isinstance(numeric, bool):
        return algebra.scalar(numeric)
    raise TypeError(f"symbol {symbol.identifier!r} must resolve to a scalar or multivector")


__all__ = ["evaluate"]
