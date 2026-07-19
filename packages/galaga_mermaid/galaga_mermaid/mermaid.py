"""Generate Mermaid diagrams from Galaga 2 expression provenance."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from galaga.display import render
from galaga.expression import (
    BladeLiteral,
    Call,
    Expr,
    MultivectorLiteral,
    ScalarLiteral,
    Symbol,
    evaluate,
)
from galaga.names import Name
from galaga.presentation import PresentationConfig

_DIRECTIONS = {"BT", "LR", "RL", "TD"}
_LEAF_TYPES = (Symbol, ScalarLiteral, BladeLiteral, MultivectorLiteral)


def _escape(value: str) -> str:
    return value.replace('"', "#quot;")


def _expression_label(expression: Expr, presentation: PresentationConfig) -> str:
    return render(expression, target="unicode", presentation=presentation)


def _value_label(
    expression: Expr,
    *,
    algebra: Any | None,
    environment: Mapping[Name | str, Any],
) -> str | None:
    if algebra is None:
        return None
    try:
        value = evaluate(expression, algebra=algebra, environment=environment)
        return render(value, content="value", target="unicode")
    except (KeyError, TypeError, ValueError):
        return None


def _significant_descendants(expression: Expr) -> tuple[Expr, ...]:
    if isinstance(expression, _LEAF_TYPES):
        return (expression,)
    if not isinstance(expression, Call):
        return ()
    result: list[Expr] = []
    for operand in expression.operands:
        result.extend(_significant_descendants(operand))
    return tuple(result)


def expr_to_mermaid(
    expression: Expr,
    *,
    presentation: PresentationConfig,
    direction: str = "TD",
    show_values: bool = True,
    compact: bool = False,
    algebra: Any | None = None,
    environment: Mapping[Name | str, Any] | None = None,
) -> str:
    """Convert public Galaga 2 expression provenance to a Mermaid flowchart.

    ``Expr`` intentionally carries no algebra or concrete symbol values.
    Rendering therefore requires a presentation. Optional numeric annotations
    require both an algebra and values for every referenced symbol.
    """
    if not isinstance(expression, Expr):
        raise TypeError("expression must be a galaga.expression.Expr")
    if not isinstance(presentation, PresentationConfig):
        raise TypeError("presentation must be a PresentationConfig")
    if direction not in _DIRECTIONS:
        raise ValueError("direction must be 'TD', 'LR', 'BT', or 'RL'")

    selected_environment = {} if environment is None else environment
    lines: list[str] = [f"graph {direction}"]
    node_ids: dict[int, str] = {}
    edges: set[tuple[str, str]] = set()
    symbol_ids: list[str] = []
    blade_ids: list[str] = []
    scalar_ids: list[str] = []

    def make_label(node: Expr) -> str:
        label = _escape(_expression_label(node, presentation))
        if show_values:
            value = _value_label(node, algebra=algebra, environment=selected_environment)
            if value is not None:
                escaped_value = _escape(value)
                if label != escaped_value:
                    label = f"{label}<br>{escaped_value}"
        return label

    def make_node(node: Expr) -> str:
        identity = id(node)
        if identity in node_ids:
            return node_ids[identity]
        node_id = f"n{len(node_ids) + 1}"
        node_ids[identity] = node_id
        lines.append(f'    {node_id}["{make_label(node)}"]')
        if isinstance(node, Symbol):
            symbol_ids.append(node_id)
        elif isinstance(node, BladeLiteral):
            blade_ids.append(node_id)
        elif isinstance(node, (ScalarLiteral, MultivectorLiteral)):
            scalar_ids.append(node_id)
        return node_id

    def add_edge(parent: str, child: str) -> None:
        edge = (parent, child)
        if edge not in edges:
            edges.add(edge)
            lines.append(f"    {child} --> {parent}")

    def visit(node: Expr) -> str:
        node_id = make_node(node)
        if isinstance(node, Call):
            children = _significant_descendants(node) if compact else node.operands
            for child in children:
                add_edge(node_id, visit(child))
        return node_id

    visit(expression)

    for node_id in symbol_ids:
        lines.append(f"    style {node_id} fill:#e0f0ff,stroke:#4a90d9")
    for node_id in blade_ids:
        lines.append(f"    style {node_id} fill:#f0ffe0,stroke:#6a9a30")
    for node_id in scalar_ids:
        lines.append(f"    style {node_id} fill:#fff0e0,stroke:#d9a04a")
    return "\n".join(lines)


def mv_to_mermaid(
    value: Any,
    *,
    presentation: PresentationConfig | None = None,
    direction: str = "TD",
    show_values: bool = True,
    compact: bool = False,
    environment: Mapping[Name | str, Any] | None = None,
) -> str:
    """Generate a Mermaid diagram from a core-backed facade multivector."""
    algebra = getattr(value, "algebra", None)
    resolve = getattr(algebra, "resolve_presentation", None)
    with_expr = getattr(value, "with_expr", None)
    if resolve is None or not callable(resolve) or with_expr is None or not callable(with_expr):
        raise TypeError("value must be a core-backed galaga.facade.Multivector")
    expression = getattr(value, "expr", None)
    if expression is None:
        expression = cast(Any, with_expr()).expr
    if not isinstance(expression, Expr):  # pragma: no cover - defensive protocol boundary
        raise TypeError("value has no public expression provenance")
    selected_presentation = cast(PresentationConfig, resolve(presentation))
    selected_environment: dict[Name | str, Any] = dict(environment or {})
    name = getattr(value, "name", None)
    if isinstance(expression, Symbol) and isinstance(name, Name):
        selected_environment.setdefault(name, value)
    return expr_to_mermaid(
        expression,
        presentation=selected_presentation,
        direction=direction,
        show_values=show_values,
        compact=compact,
        algebra=algebra,
        environment=selected_environment,
    )
