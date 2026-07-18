"""Small, semantics-preserving structural expression simplifier."""

from __future__ import annotations

from ._nodes import Call, Expr, ScalarLiteral


def simplify(expression: Expr) -> Expr:
    """Apply deterministic structural identities until reaching a fixed point."""
    if not isinstance(expression, Expr):
        raise TypeError("expression must be an Expr")
    previous = expression
    while True:
        current = _simplify_once(previous)
        if current == previous:
            return current
        previous = current


def _simplify_once(expression: Expr) -> Expr:
    if not isinstance(expression, Call):
        return expression
    operands = tuple(_simplify_once(operand) for operand in expression.operands)
    call = (
        expression
        if operands == expression.operands
        else Call(expression.operation_id, operands, expression.parameters)
    )
    return _rewrite(call)


def _rewrite(expression: Call) -> Expr:
    operation = expression.operation_id
    operands = expression.operands

    if operation == "negate":
        value = operands[0]
        if isinstance(value, ScalarLiteral):
            return ScalarLiteral(-value.value)
        if isinstance(value, Call) and value.operation_id == "negate":
            return value.operands[0]

    if operation in {"add", "subtract"}:
        left, right = operands
        if isinstance(left, ScalarLiteral) and isinstance(right, ScalarLiteral):
            result = left.value + right.value if operation == "add" else left.value - right.value
            return ScalarLiteral(result)
        if _is_zero(right):
            return left
        if operation == "add" and _is_zero(left):
            return right

    parameters = dict(expression.parameters)
    if operation == "scalar_multiply":
        scalar = parameters["scalar"]
        if scalar == 0:
            return ScalarLiteral(0)
        if scalar == 1:
            return operands[0]
        if isinstance(operands[0], ScalarLiteral):
            return ScalarLiteral(operands[0].value * scalar)
    if operation == "scalar_divide":
        scalar = parameters["scalar"]
        if scalar == 1:
            return operands[0]
        if isinstance(operands[0], ScalarLiteral) and scalar != 0:
            return ScalarLiteral(operands[0].value / scalar)
    if operation == "power":
        exponent = parameters["exponent"]
        if exponent == 1:
            return operands[0]
        if exponent == 0:
            return ScalarLiteral(1)
        if isinstance(operands[0], ScalarLiteral) and exponent >= 0:
            return ScalarLiteral(operands[0].value ** exponent)

    return expression


def _is_zero(expression: Expr) -> bool:
    return isinstance(expression, ScalarLiteral) and expression.value == 0


__all__ = ["simplify"]
