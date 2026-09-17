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
        if scalar == -1:
            return Call("negate", operands)
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


def _simplify_with_paths(expression: Expr) -> tuple[Expr, dict[tuple[int, ...], tuple[int, ...]]]:
    """Track surviving occurrences using the same rewrites as ``simplify``.

    Keys address the original tree; values address the simplified tree.
    Folded operations keep their whole-expression occurrence, but discarded
    operands have no entry. Consumers must separately check operation IDs.
    """

    def walk(node: Expr) -> tuple[Expr, dict[tuple[int, ...], tuple[int, ...]]]:
        if not isinstance(node, Call):
            return node, {(): ()}
        children = tuple(walk(child) for child in node.operands)
        operands = tuple(child for child, _ in children)
        call = node if operands == node.operands else Call(node.operation_id, operands, node.parameters)
        result = _rewrite(call)
        paths: dict[tuple[int, ...], tuple[int, ...]] = {(): ()}
        if result is call:
            for index, (_, child_paths) in enumerate(children):
                for old, new in child_paths.items():
                    paths[(index, *old)] = (index, *new)
        elif result is operands[0]:
            for old, new in children[0][1].items():
                paths[(0, *old)] = new
        elif len(operands) > 1 and result is operands[1]:
            for old, new in children[1][1].items():
                paths[(1, *old)] = new
        elif node.operation_id == "negate" and isinstance(operands[0], Call) and operands[0].operation_id == "negate":
            for old, new in children[0][1].items():
                if new[:1] == (0,):
                    paths[(0, *old)] = new[1:]
        elif isinstance(result, Call):
            # scalar_multiply(x, -1) becomes negate(x), preserving its operand.
            for index, (_, child_paths) in enumerate(children):
                for old, new in child_paths.items():
                    paths[(index, *old)] = (index, *new)
        return result, paths

    if not isinstance(expression, Expr):
        raise TypeError("expression must be an Expr")
    current = expression
    mapping: dict[tuple[int, ...], tuple[int, ...]] | None = None
    while True:
        result, paths = walk(current)
        mapping = paths if mapping is None else {old: paths[new] for old, new in mapping.items() if new in paths}
        if result == current:
            return result, mapping
        current = result


__all__ = ["simplify"]
