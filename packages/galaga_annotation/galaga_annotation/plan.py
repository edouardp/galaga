"""Resolve immutable annotation rules against semantic render documents.

Resolution maps semantic targets to layout paths. A valid rule may match zero
visible targets; that is an empty selection, not an error, unless the rule
opted into ``missing="error"``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

import numpy as np

from galaga.expression import Call as ExpressionCall
from galaga.expression import Expr, evaluate
from galaga.rendering import ExpressionAnchor, Infix, Node, Product, RenderAnchor, RenderDocument, Sum

from .model import Annotation
from .targets import (
    MATRIX_TARGET_TYPES,
    CoefficientTarget,
    ContentTarget,
    ExpressionPath,
    GradeTarget,
    OperationTarget,
    SignTarget,
    SubexpressionTarget,
    TermTarget,
    VariableTarget,
    WholeExpression,
    ZeroSubexpressionTarget,
)

__all__ = ["AnnotationPlan", "MissingTargetError", "Placement", "resolve"]

Path = tuple[str | int, ...]


class MissingTargetError(ValueError):
    """A rule with ``missing="error"`` matched no visible target."""


@dataclass(frozen=True, slots=True)
class Placement:
    """One resolved rule bound to a layout path and optional sequence interval."""

    annotation: Annotation
    path: Path
    order: int
    start: int | None = None
    stop: int | None = None


@dataclass(frozen=True, slots=True)
class AnnotationPlan:
    """Resolved placements plus rules that matched nothing."""

    placements: tuple[Placement, ...]
    missing: tuple[Annotation, ...]

    def by_path(self) -> dict[Path, tuple[Annotation, ...]]:
        """Group rules by layout path, preserving resolution order."""
        grouped: dict[Path, list[Annotation]] = {}
        for placement in self.placements:
            grouped.setdefault(placement.path, []).append(placement.annotation)
        return {path: tuple(rules) for path, rules in grouped.items()}


def _ordered_paths(node: Node, path: Path = ()):
    """Yield layout paths in emission order, matching render-document paths."""
    yield path
    if not is_dataclass(node):
        return
    for field in fields(node):
        child = getattr(node, field.name)
        if isinstance(child, Node):
            yield from _ordered_paths(child, (*path, field.name))
        elif isinstance(child, tuple):
            for index, member in enumerate(child):
                if isinstance(member, Node):
                    yield from _ordered_paths(member, (*path, field.name, index))
                elif isinstance(node, Sum) and field.name == "terms" and hasattr(member, "body"):
                    yield from _ordered_paths(member.body, (*path, field.name, index, "body"))


def _term_path(anchor: RenderAnchor) -> Path:
    if anchor.kind == "term" and anchor.term_index is not None:
        return (*anchor.render_path, "terms", anchor.term_index, "body")
    return anchor.render_path


def _sign_path(anchor: RenderAnchor) -> Path:
    """Address a sum slot's sign; singleton signs have no separate slot."""

    if anchor.term_index is None:
        return anchor.render_path
    return (*anchor.render_path, "terms", anchor.term_index, "sign")


def _expression_path(anchor: ExpressionAnchor) -> Path:
    part = anchor.part
    if part in {"function", "separator", "operator", "accent"} and is_dataclass(anchor.node):
        names = {field.name for field in fields(anchor.node)}
        if part in names and isinstance(getattr(anchor.node, part), Node):
            return (*anchor.render_path, part)
    return anchor.render_path


def _same_algebra(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return True
    if left is right:
        return True
    gram_left = getattr(left, "gram", None)
    gram_right = getattr(right, "gram", None)
    if gram_left is None or gram_right is None:
        return False
    return np.shape(gram_left) == np.shape(gram_right) and np.array_equal(np.asarray(gram_left), np.asarray(gram_right))


def _unique(paths: Iterable[Path]) -> tuple[Path, ...]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            result.append(path)
    return tuple(result)


def _select_whole(_document: RenderDocument, _target: WholeExpression, _value_algebra: Any) -> tuple[Path, ...]:
    return ((),)


def _select_content(document: RenderDocument, target: ContentTarget, _value_algebra: Any) -> tuple[Path, ...]:
    return _unique(anchor.render_path for anchor in document.select_content(target.kind))


def _select_expression(document: RenderDocument, target: ExpressionPath, _value_algebra: Any) -> tuple[Path, ...]:
    anchors = document.select_expression("expression", path=target.path)
    return _unique(_expression_path(anchor) for anchor in anchors)


def _select_operation(document: RenderDocument, target: OperationTarget, _value_algebra: Any) -> tuple[Path, ...]:
    anchors = document.select_expression("operator", operation_id=target.operation_id)
    return _unique(_expression_path(anchor) for anchor in anchors)


def _select_variable(document: RenderDocument, target: VariableTarget, _value_algebra: Any) -> tuple[Path, ...]:
    anchors = document.select_expression("symbol", name=target.name)
    selected = anchors if target.occurrence == "all" else anchors[target.occurrence : target.occurrence + 1]
    return _unique(_expression_path(anchor) for anchor in selected)


def _source_at(expression: Expr, path: tuple[int, ...]) -> Expr | None:
    source: Expr = expression
    for index in path:
        if not isinstance(source, ExpressionCall) or index >= len(source.operands):
            return None
        source = source.operands[index]
    return source


def _select_subexpression(document: RenderDocument, target: SubexpressionTarget, value: Any) -> tuple[Path, ...]:
    expression = getattr(value, "expr", None)
    if not isinstance(expression, Expr):
        raise ValueError("subexpression targets require a tracked value with expression provenance")
    paths = (
        _expression_path(anchor)
        for anchor in document.select_expression("expression")
        if _source_at(expression, anchor.path) == target.expression
    )
    unique = _unique(paths)
    if target.occurrence == "all":
        return unique
    return unique[target.occurrence : target.occurrence + 1]


def _evaluates_to_zero(expression: ExpressionCall, value: Any, atol: float) -> bool | None:
    """Return zero status, or ``None`` when named symbols prevent evaluation."""

    algebra = getattr(value, "algebra", None)
    if algebra is None:
        raise ValueError("zero-subexpression targets require a value with an algebra")
    try:
        result = evaluate(expression, algebra=algebra)
    except KeyError:
        return None
    coefficients = getattr(result, "data", None)
    if coefficients is None:
        return None
    data = np.asarray(coefficients)
    return bool(data.size and np.all(np.abs(data) <= atol))


def _innermost_zero_paths(expression: Expr, value: Any, atol: float) -> tuple[tuple[int, ...], ...]:
    """Return non-overlapping zero-call paths, preferring explanatory leaves."""

    def walk(node: Expr, path: tuple[int, ...]) -> tuple[bool, tuple[tuple[int, ...], ...]]:
        if not isinstance(node, ExpressionCall):
            return False, ()
        descendant_is_zero = False
        selected: list[tuple[int, ...]] = []
        for index, operand in enumerate(node.operands):
            child_is_zero, child_paths = walk(operand, (*path, index))
            descendant_is_zero = descendant_is_zero or child_is_zero
            selected.extend(child_paths)
        current_is_zero = _evaluates_to_zero(node, value, atol) is True
        if current_is_zero and not descendant_is_zero:
            return True, (path,)
        return current_is_zero or descendant_is_zero, tuple(selected)

    return walk(expression, ())[1]


def _zero_subexpression_anchors(
    document: RenderDocument,
    target: ZeroSubexpressionTarget,
    value: Any,
) -> tuple[ExpressionAnchor, ...]:
    expression = getattr(value, "expr", None)
    if not isinstance(expression, Expr):
        raise ValueError("zero-subexpression targets require a tracked value with expression provenance")
    selected = frozenset(_innermost_zero_paths(expression, value, target.atol))
    anchors = (
        anchor
        for anchor in document.select_expression("expression")
        if anchor.path in selected and (anchor.start is None or isinstance(anchor.node, (Sum, Product, Infix)))
    )
    unique: dict[tuple[Path, int | None, int | None], ExpressionAnchor] = {}
    for anchor in anchors:
        unique.setdefault((_expression_path(anchor), anchor.start, anchor.stop), anchor)
    return tuple(unique.values())


def _select_grade(document: RenderDocument, target: GradeTarget, _value_algebra: Any) -> tuple[Path, ...]:
    anchors = (anchor for grade in target.grades for anchor in document.select("term", grade=grade))
    return _unique(_term_path(anchor) for anchor in anchors)


def _require_target_algebra(target_algebra: Any, value_algebra: Any, kind: str) -> None:
    if not _same_algebra(target_algebra, value_algebra):
        raise ValueError(f"{kind} target belongs to a different algebra")


def _select_term(document: RenderDocument, target: TermTarget, value: Any) -> tuple[Path, ...]:
    _require_target_algebra(target.algebra, getattr(value, "algebra", None), "term")
    anchors = (anchor for mask in target.masks for anchor in document.select("term", mask=mask))
    return _unique(_term_path(anchor) for anchor in anchors)


def _select_coefficient(document: RenderDocument, target: CoefficientTarget, value: Any) -> tuple[Path, ...]:
    _require_target_algebra(target.algebra, getattr(value, "algebra", None), "coefficient")
    anchors = (anchor for mask in target.masks for anchor in document.select("coefficient", mask=mask))
    return _unique(anchor.render_path for anchor in anchors)


def _select_sign(document: RenderDocument, target: SignTarget, value: Any) -> tuple[Path, ...]:
    _require_target_algebra(target.algebra, getattr(value, "algebra", None), "sign")
    anchors = (anchor for mask in target.masks for anchor in document.select("sign", mask=mask))
    return _unique(_sign_path(anchor) for anchor in anchors)


_Selector = Callable[[RenderDocument, Any, Any], tuple[Path, ...]]
_SELECTORS: tuple[tuple[type, _Selector], ...] = (
    (WholeExpression, _select_whole),
    (ContentTarget, _select_content),
    (ExpressionPath, _select_expression),
    (OperationTarget, _select_operation),
    (VariableTarget, _select_variable),
    (SubexpressionTarget, _select_subexpression),
    (GradeTarget, _select_grade),
    (TermTarget, _select_term),
    (CoefficientTarget, _select_coefficient),
    (SignTarget, _select_sign),
)


def _select(document: RenderDocument, target: Any, value: Any) -> tuple[Path, ...]:
    if isinstance(target, MATRIX_TARGET_TYPES):
        raise TypeError(
            "matrix targets resolve against a MatrixRepr, not an expression document; use render_matrix_katex"
        )
    for target_type, selector in _SELECTORS:
        if isinstance(target, target_type):
            return selector(document, target, value)
    raise TypeError(f"unsupported annotation target {type(target).__name__}")


def _path_order(document: RenderDocument) -> dict[Path, int]:
    order: dict[Path, int] = {}
    for index, path in enumerate(_ordered_paths(document.body)):
        order.setdefault(path, index)
    return order


def _placement(
    rule: Annotation,
    path: Path,
    order: dict[Path, int],
    *,
    start: int | None = None,
    stop: int | None = None,
) -> Placement:
    return Placement(rule, path, order.get(path, len(order)), start=start, stop=stop)


def _resolve_rule(
    document: RenderDocument,
    rule: Annotation,
    value: Any,
    order: dict[Path, int],
) -> tuple[Placement, ...]:
    if isinstance(rule.target, ZeroSubexpressionTarget):
        return tuple(
            _placement(
                rule,
                _expression_path(anchor),
                order,
                start=anchor.start,
                stop=anchor.stop,
            )
            for anchor in _zero_subexpression_anchors(document, rule.target, value)
        )
    return tuple(_placement(rule, path, order) for path in _select(document, rule.target, value))


def _record_missing(rule: Annotation, missing: list[Annotation]) -> None:
    if rule.missing == "error":
        raise MissingTargetError(f"annotation target {rule.target!r} matched no visible content")
    missing.append(rule)


def resolve(document: RenderDocument, rules: Iterable[Annotation], *, value: Any = None) -> AnnotationPlan:
    """Resolve annotation rules against one render document.

    ``value`` supplies the source algebra used to validate blade-bound rules
    and evaluate value-dependent expression selectors.
    """

    if not isinstance(document, RenderDocument):
        raise TypeError("resolve expects a RenderDocument")
    order = _path_order(document)
    placements: list[Placement] = []
    missing: list[Annotation] = []
    for rule in rules:
        if not isinstance(rule, Annotation):
            raise TypeError("annotation rules must be Annotation instances")
        resolved = _resolve_rule(document, rule, value, order)
        if resolved:
            placements.extend(resolved)
        else:
            _record_missing(rule, missing)
    return AnnotationPlan(tuple(placements), tuple(missing))
