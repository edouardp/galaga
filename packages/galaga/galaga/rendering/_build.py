"""Translate eager values and provenance expressions into semantic trees."""

from __future__ import annotations

from collections.abc import Sequence
from numbers import Real
from typing import Any

from ..expression import (
    BladeLiteral,
    Expr,
    MultivectorLiteral,
    ScalarLiteral,
    Symbol,
    simplify,
)
from ..expression import (
    Call as ExpressionCall,
)
from ..names import Name
from ..presentation import PresentationConfig, RenderRule
from .tree import (
    Accent,
    Call,
    Delimited,
    Equality,
    Fraction,
    Group,
    Identifier,
    Infix,
    Literal,
    MathClass,
    Node,
    Postfix,
    Power,
    Prefix,
    Product,
    Subscript,
    Sum,
    SumTerm,
    Underset,
    Wrapper,
    grouped_child,
)


def expression_tree(
    expression: Expr,
    presentation: PresentationConfig,
    *,
    target: str | None = None,
) -> Node:
    """Build a semantic tree without evaluating ``expression``."""
    if not isinstance(expression, Expr):
        raise TypeError("expression must be an Expr")
    selected = _presentation(presentation)
    _target(target)
    return _expression_tree(simplify(expression), selected, target=target)


def _expression_tree(
    expression: Expr,
    presentation: PresentationConfig,
    *,
    target: str | None,
) -> Node:
    if isinstance(expression, Symbol):
        return Identifier(expression.name)
    if isinstance(expression, ScalarLiteral):
        return _signed_literal(expression.value, presentation)
    if isinstance(expression, BladeLiteral):
        return _blade_term(expression.mask, float(expression.orientation), presentation)
    if isinstance(expression, MultivectorLiteral):
        return _coefficient_tree(expression.coefficients, presentation)
    if isinstance(expression, ExpressionCall):
        # Resolve the operation before descending so a stale or foreign ID
        # fails in the semantic layer, independently of emitter selection.
        operation = _get_operation(expression.operation_id)
        operands = tuple(_expression_tree(operand, presentation, target=target) for operand in expression.operands)
        parameters = tuple((name, _parameter_tree(value, presentation)) for name, value in expression.parameters)
        rule = presentation.notation.rule(operation.id, target)
        return _operation_tree(operation.id, operands, parameters, rule)
    raise TypeError(f"unsupported expression node {type(expression).__name__}")


def value_tree(value: Any, presentation: PresentationConfig | None = None) -> Node:
    """Translate one core-backed facade value by inspecting coefficients only."""
    algebra = getattr(value, "algebra", None)
    data = getattr(value, "data", None)
    resolve = getattr(algebra, "resolve_presentation", None)
    if data is None or resolve is None or not callable(resolve):
        raise TypeError("value must be a core-backed facade Multivector")
    selected = _presentation(resolve(presentation))
    return _coefficient_tree(tuple(float(coefficient) for coefficient in data), selected)


def content_tree(
    value: Any,
    *,
    content: str,
    presentation: PresentationConfig | None = None,
    target: str | None = None,
) -> Node:
    """Select name, provenance, value, or a teaching equality."""
    if content not in {"name", "expr", "value", "full"}:
        raise ValueError("render content must be 'name', 'expr', 'value', or 'full'")
    algebra = getattr(value, "algebra", None)
    resolve = getattr(algebra, "resolve_presentation", None)
    if resolve is None or not callable(resolve):
        raise TypeError("value must be a core-backed facade Multivector")
    selected = _presentation(resolve(presentation))
    _target(target)
    name = getattr(value, "name", None)
    expression = getattr(value, "expr", None)
    concrete = value_tree(value, selected)
    if content == "value":
        return concrete
    if content == "name":
        return Identifier(name) if isinstance(name, Name) else concrete
    if content == "expr":
        return expression_tree(expression, selected, target=target) if isinstance(expression, Expr) else concrete

    parts: list[Node] = []
    if isinstance(name, Name):
        parts.append(Identifier(name))
    if isinstance(expression, Expr):
        parts.append(expression_tree(expression, selected, target=target))
    parts.append(concrete)
    return parts[0] if len(parts) == 1 else Equality(parts)


def _coefficient_tree(coefficients: Sequence[float], presentation: PresentationConfig) -> Node:
    expected = 1 << presentation.dimension
    if len(coefficients) != expected:
        raise ValueError(
            f"coefficient count {len(coefficients)} does not match presentation dimension "
            f"{presentation.dimension} ({expected} coefficients)"
        )
    terms: list[SumTerm] = []
    for mask in presentation.display_order.masks:
        coefficient = float(coefficients[mask])
        if coefficient == 0 or abs(coefficient) < presentation.display.zero_tolerance:
            continue
        label = presentation.blades.label(mask)
        displayed_coefficient = coefficient * label.ref.orientation
        magnitude = abs(displayed_coefficient)
        if mask == 0:
            body: Node = _literal(magnitude, presentation)
        elif _formats_as_one(magnitude, presentation.display.coefficient_precision):
            body = Identifier(label.name)
        else:
            body = Product((_literal(magnitude, presentation), Identifier(label.name)))
        terms.append(SumTerm(body, displayed_coefficient < 0))
    if not terms:
        return _literal(0, presentation)
    if len(terms) == 1:
        term = terms[0]
        return _negated(term.body) if term.negative else term.body
    return Sum(terms)


def _blade_term(mask: int, coefficient: float, presentation: PresentationConfig) -> Node:
    limit = 1 << presentation.dimension
    if not 0 <= mask < limit:
        raise ValueError(f"blade mask {mask} is outside presentation dimension {presentation.dimension}")
    coefficients = [0.0] * limit
    coefficients[mask] = coefficient
    return _coefficient_tree(coefficients, presentation)


def _literal(value: int | float, presentation: PresentationConfig) -> Literal:
    return Literal(value, precision=presentation.display.coefficient_precision)


def _signed_literal(value: float, presentation: PresentationConfig) -> Node:
    literal = _literal(abs(value) if value < 0 else value, presentation)
    return _negated(literal) if value < 0 else literal


def _formats_as_one(value: float, precision: int) -> bool:
    return format(value, f".{precision}g") == "1"


def _negated(body: Node) -> Prefix:
    return Prefix("-", grouped_child(body, parent_precedence=40), precedence=40)


def _parameter_tree(value: Any, presentation: PresentationConfig) -> Node:
    if isinstance(value, Real) and not isinstance(value, bool):
        return _signed_literal(float(value), presentation)
    if isinstance(value, str):
        return Identifier(value)
    if isinstance(value, tuple):
        return Delimited(
            tuple(_parameter_tree(item, presentation) for item in value),
            opening=Name("[", "[", r"["),
            closing=Name("]", "]", r"]"),
        )
    raise TypeError(f"expression parameter {value!r} has no semantic rendering")


def _operation_tree(
    operation_id: str,
    operands: tuple[Node, ...],
    parameters: tuple[tuple[str, Node], ...],
    rule: RenderRule | None,
) -> Node:
    if rule is None:
        return _functional_tree(operation_id, operands, parameters)
    if rule.kind == "function":
        symbol = rule.symbol
        if symbol is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("function render rule has no symbol")
        return Call(
            symbol,
            _ordered((*operands, *(value for _, value in parameters)), rule),
            scalable=rule.scalable,
        )

    if rule.parameter is not None:
        parameter_lookup = dict(parameters)
        try:
            decoration = parameter_lookup.pop(rule.parameter)
        except KeyError as error:
            raise ValueError(
                f"notation rule for {operation_id!r} requires expression parameter {rule.parameter!r}"
            ) from error
        if parameter_lookup:
            return _functional_tree(operation_id, operands, parameters)
        arguments = _ordered(operands, rule)
    else:
        decoration = None
        arguments = _ordered((*operands, *(value for _, value in parameters)), rule)

    if rule.kind == "infix":
        if decoration is None and parameters:
            return _functional_tree(operation_id, operands, parameters)
        if len(arguments) < 2:
            raise ValueError(f"infix notation for {operation_id!r} requires at least two operands")
        symbol = rule.symbol
        if symbol is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("infix render rule has no symbol")
        if operation_id == "add" and _is_conventional_addition(rule):
            return _sum_tree(arguments)
        if operation_id == "subtract" and _is_conventional_subtraction(rule) and isinstance(arguments[0], Sum):
            return _difference_from_sum(arguments)
        operator: Node = Identifier(symbol)
        if decoration is not None:
            if rule.parameter_position == "underscript":
                operator = MathClass(Underset(operator, decoration), "binary")
            else:
                operator = Subscript(operator, decoration)
        children = _flatten_infix(arguments, operation_id, rule)
        grouped = _group_operands(children, operation_id, rule)
        return Infix(
            grouped,
            operator,
            precedence=rule.precedence,
            associativity=rule.associativity,
            operation_id=operation_id,
        )

    if rule.kind == "juxtaposition":
        if decoration is not None or len(arguments) < 2:
            return _functional_tree(operation_id, operands, parameters)
        children = _flatten_product(arguments, operation_id, rule)
        grouped = _group_operands(children, operation_id, rule)
        return Product(
            grouped,
            separator=rule.symbol,
            precedence=rule.precedence,
            associativity=rule.associativity,
            operation_id=operation_id,
        )

    if rule.kind == "fraction":
        if decoration is not None or len(arguments) != 2:
            return _functional_tree(operation_id, operands, parameters)
        return Fraction(arguments[0], arguments[1])

    if rule.kind == "sandwich":
        if decoration is not None or len(arguments) != 2:
            return _functional_tree(operation_id, operands, parameters)
        rotor, value = arguments
        return Product(
            (
                grouped_child(rotor, parent_precedence=30),
                grouped_child(value, parent_precedence=30),
                Accent(rotor, Name("~", "\u0303", r"\widetilde")),
            ),
            precedence=30,
            operation_id=operation_id,
        )

    if rule.kind == "metric_regressive":
        if decoration is not None or len(arguments) != 2:
            return _functional_tree(operation_id, operands, parameters)
        dual_symbol = Name("*", "★", "*")
        undual_symbol = Name("*^-1", "★⁻¹", r"*^{-1}")
        duals = tuple(
            Power(grouped_child(argument, parent_precedence=50), Identifier(dual_symbol)) for argument in arguments
        )
        joined = Infix(
            duals,
            Name("^", "∧", r"\wedge"),
            precedence=30,
            associativity="associative",
            operation_id="outer_product",
        )
        return Power(Group(joined), Identifier(undual_symbol))

    if rule.kind in {"superscript", "subscript"}:
        if decoration is not None:
            return _functional_tree(operation_id, operands, parameters)
        if rule.symbol is None:
            if len(arguments) != 2:
                return _functional_tree(operation_id, operands, parameters)
            base, script = arguments
        else:
            if len(arguments) != 1:
                return _functional_tree(operation_id, operands, parameters)
            base, script = arguments[0], Identifier(rule.symbol)
        if rule.kind == "superscript":
            return Power(
                grouped_child(
                    base,
                    parent_precedence=rule.precedence,
                    associativity=rule.associativity,
                    side="left",
                    operation_id=operation_id,
                ),
                grouped_child(
                    script,
                    parent_precedence=rule.precedence,
                    associativity=rule.associativity,
                    side="right",
                    operation_id=operation_id,
                ),
            )
        return Subscript(grouped_child(base, parent_precedence=rule.precedence), script)

    if rule.kind == "wrapper":
        opening = rule.opening
        closing = rule.closing
        if opening is None or closing is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("wrapper render rule has no delimiters")
        if not arguments:
            return _functional_tree(operation_id, operands, parameters)
        wrapped: Node
        if len(arguments) == 1:
            wrapped = Wrapper(arguments[0], opening, closing, scalable=rule.scalable)
        else:
            wrapped = Delimited(
                arguments,
                opening=opening,
                closing=closing,
                separator=Name(", ", ", ", r",\, "),
                scalable=rule.scalable,
            )
        return Subscript(wrapped, _compact_script(decoration)) if decoration is not None else wrapped

    if decoration is not None or len(arguments) != 1:
        return _functional_tree(operation_id, operands, parameters)
    operand = arguments[0]
    if rule.kind == "prefix":
        symbol = rule.symbol
        if symbol is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("prefix render rule has no symbol")
        return Prefix(
            symbol,
            grouped_child(operand, parent_precedence=rule.precedence, operation_id=operation_id),
            precedence=rule.precedence,
        )
    if rule.kind == "postfix":
        symbol = rule.symbol
        if symbol is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("postfix render rule has no symbol")
        return Postfix(
            grouped_child(operand, parent_precedence=rule.precedence, operation_id=operation_id),
            symbol,
            precedence=rule.precedence,
        )
    if rule.kind in {"accent", "underaccent"}:
        symbol = rule.symbol
        if symbol is None:  # pragma: no cover - RenderRule validation
            raise RuntimeError("accent render rule has no symbol")
        return Accent(
            (
                grouped_child(operand, parent_precedence=rule.precedence, operation_id=operation_id)
                if rule.group_operand
                else operand
            ),
            symbol,
            position="under" if rule.kind == "underaccent" else "over",
        )
    raise RuntimeError(f"unsupported render-rule kind {rule.kind!r}")


def _functional_tree(
    operation_id: str,
    operands: tuple[Node, ...],
    parameters: tuple[tuple[str, Node], ...],
) -> Call:
    return Call(operation_id, (*operands, *(value for _, value in parameters)))


def _compact_script(value: Node) -> Node:
    if not isinstance(value, Delimited):
        return value
    return Delimited(
        value.items,
        opening=value.opening,
        closing=value.closing,
        separator=Name(",", ",", ","),
        scalable=False,
    )


def _ordered(arguments: tuple[Node, ...], rule: RenderRule) -> tuple[Node, ...]:
    if rule.argument_order is None:
        return arguments
    if tuple(sorted(rule.argument_order)) != tuple(range(len(arguments))):
        raise ValueError(
            "render-rule argument order must be a complete permutation of the operation's rendered arguments"
        )
    return tuple(arguments[index] for index in rule.argument_order)


def _flatten_infix(arguments: tuple[Node, ...], operation_id: str, rule: RenderRule) -> tuple[Node, ...]:
    if not rule.flatten:
        return arguments
    flattened: list[Node] = []
    for argument in arguments:
        if isinstance(argument, Infix) and argument.operation_id == operation_id:
            flattened.extend(argument.operands)
        else:
            flattened.append(argument)
    return tuple(flattened)


def _flatten_product(arguments: tuple[Node, ...], operation_id: str, rule: RenderRule) -> tuple[Node, ...]:
    if not rule.flatten:
        return arguments
    flattened: list[Node] = []
    for argument in arguments:
        if isinstance(argument, Product) and argument.operation_id == operation_id:
            flattened.extend(argument.factors)
        else:
            flattened.append(argument)
    return tuple(flattened)


def _is_conventional_addition(rule: RenderRule) -> bool:
    """Return whether an addition rule has the built-in signed-sum semantics."""
    symbol = rule.symbol
    return (
        symbol is not None
        and symbol.ascii == symbol.unicode == symbol.latex == "+"
        and rule.precedence == 20
        and rule.associativity == "associative"
        and rule.flatten
    )


def _is_conventional_subtraction(rule: RenderRule) -> bool:
    """Return whether subtraction has the built-in signed-sum semantics."""
    symbol = rule.symbol
    return (
        symbol is not None
        and symbol.ascii == symbol.unicode == symbol.latex == "-"
        and rule.precedence == 20
        and rule.associativity == "left"
    )


def _sum_tree(arguments: tuple[Node, ...]) -> Sum:
    """Flatten addition and absorb a leading minus into each semantic term."""
    terms: list[SumTerm] = []
    for argument in arguments:
        if isinstance(argument, Sum):
            terms.extend(argument.terms)
            continue
        body, negative = _unsigned_term(argument)
        terms.append(SumTerm(body, negative))
    return Sum(terms)


def _difference_from_sum(arguments: tuple[Node, ...]) -> Sum:
    """Append a subtraction to an already-flat left-hand signed sum."""
    if len(arguments) != 2 or not isinstance(arguments[0], Sum):  # pragma: no cover - caller invariant
        raise RuntimeError("difference-from-sum requires a left-hand sum and one right operand")
    right, already_negative = _unsigned_term(arguments[1])
    return Sum((*arguments[0].terms, SumTerm(right, not already_negative)))


def _unsigned_term(node: Node) -> tuple[Node, bool]:
    """Split the conventional leading minus from one rendered sum term."""
    if isinstance(node, Prefix) and node.operator.ascii == node.operator.unicode == node.operator.latex == "-":
        return node.operand, True
    if isinstance(node, Product) and node.factors:
        coefficient = node.factors[0]
        if (
            isinstance(coefficient, Prefix)
            and coefficient.operator.ascii == coefficient.operator.unicode == coefficient.operator.latex == "-"
        ):
            return (
                Product(
                    (coefficient.operand, *node.factors[1:]),
                    separator=node.separator,
                    precedence=node.binding,
                    associativity=node.associativity,
                    operation_id=node.operation_id,
                ),
                True,
            )
    return node, False


def _group_operands(arguments: tuple[Node, ...], operation_id: str, rule: RenderRule) -> tuple[Node, ...]:
    last = len(arguments) - 1
    return tuple(
        grouped_child(
            argument,
            parent_precedence=rule.precedence,
            associativity=rule.associativity,
            side="left" if index == 0 else "right" if index == last else "middle",
            operation_id=operation_id,
        )
        for index, argument in enumerate(arguments)
    )


def _presentation(value: Any) -> PresentationConfig:
    if not isinstance(value, PresentationConfig):
        raise TypeError("presentation must be a PresentationConfig")
    return value


def _target(value: str | None) -> None:
    if value is not None and value not in {"ascii", "unicode", "latex"}:
        raise ValueError("render target must be 'ascii', 'unicode', or 'latex'")


def _get_operation(operation_id: str) -> Any:
    # Local import keeps ``galaga.rendering.tree`` independently importable;
    # importing a submodule must not initialize the full facade package.
    from ..facade.catalog import get_operation

    return get_operation(operation_id)


__all__ = ["content_tree", "expression_tree", "value_tree"]
