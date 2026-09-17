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

from galaga.rendering import ExpressionAnchor, Node, RenderAnchor, RenderDocument, Sum

from .model import Annotation
from .targets import (
    CoefficientTarget,
    ExpressionPath,
    GradeTarget,
    OperationTarget,
    TermTarget,
    VariableTarget,
    WholeExpression,
)

__all__ = ["AnnotationPlan", "MissingTargetError", "Placement", "resolve"]

Path = tuple[str | int, ...]


class MissingTargetError(ValueError):
    """A rule with ``missing="error"`` matched no visible target."""


@dataclass(frozen=True, slots=True)
class Placement:
    """One resolved rule bound to one displayed layout path."""

    annotation: Annotation
    path: Path
    order: int


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
    if anchor.kind in {"term", "sign"} and anchor.term_index is not None:
        return (*anchor.render_path, "terms", anchor.term_index, "body")
    return anchor.render_path


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


def _select_whole(
    _document: RenderDocument, _target: WholeExpression, _value_algebra: Any
) -> tuple[Path, ...]:
    return ((),)


def _select_expression(
    document: RenderDocument, target: ExpressionPath, _value_algebra: Any
) -> tuple[Path, ...]:
    anchors = document.select_expression("expression", path=target.path)
    return _unique(_expression_path(anchor) for anchor in anchors)


def _select_operation(
    document: RenderDocument, target: OperationTarget, _value_algebra: Any
) -> tuple[Path, ...]:
    anchors = document.select_expression("operator", operation_id=target.operation_id)
    return _unique(_expression_path(anchor) for anchor in anchors)


def _select_variable(
    document: RenderDocument, target: VariableTarget, _value_algebra: Any
) -> tuple[Path, ...]:
    anchors = document.select_expression("symbol", name=target.name)
    selected = anchors if target.occurrence == "all" else anchors[target.occurrence : target.occurrence + 1]
    return _unique(_expression_path(anchor) for anchor in selected)


def _select_grade(document: RenderDocument, target: GradeTarget, _value_algebra: Any) -> tuple[Path, ...]:
    anchors = (anchor for grade in target.grades for anchor in document.select("term", grade=grade))
    return _unique(_term_path(anchor) for anchor in anchors)


def _require_target_algebra(target_algebra: Any, value_algebra: Any, kind: str) -> None:
    if not _same_algebra(target_algebra, value_algebra):
        raise ValueError(f"{kind} target belongs to a different algebra")


def _select_term(document: RenderDocument, target: TermTarget, value_algebra: Any) -> tuple[Path, ...]:
    _require_target_algebra(target.algebra, value_algebra, "term")
    anchors = (anchor for mask in target.masks for anchor in document.select("term", mask=mask))
    return _unique(_term_path(anchor) for anchor in anchors)


def _select_coefficient(document: RenderDocument, target: CoefficientTarget, value_algebra: Any) -> tuple[Path, ...]:
    _require_target_algebra(target.algebra, value_algebra, "coefficient")
    anchors = (anchor for mask in target.masks for anchor in document.select("coefficient", mask=mask))
    return _unique(anchor.render_path for anchor in anchors)


_Selector = Callable[[RenderDocument, Any, Any], tuple[Path, ...]]
_SELECTORS: tuple[tuple[type, _Selector], ...] = (
    (WholeExpression, _select_whole),
    (ExpressionPath, _select_expression),
    (OperationTarget, _select_operation),
    (VariableTarget, _select_variable),
    (GradeTarget, _select_grade),
    (TermTarget, _select_term),
    (CoefficientTarget, _select_coefficient),
)


def _select(document: RenderDocument, target: Any, value_algebra: Any) -> tuple[Path, ...]:
    for target_type, selector in _SELECTORS:
        if isinstance(target, target_type):
            return selector(document, target, value_algebra)
    raise TypeError(f"unsupported annotation target {type(target).__name__}")


def resolve(document: RenderDocument, rules: Iterable[Annotation], *, value: Any = None) -> AnnotationPlan:
    """Resolve annotation rules against one render document.

    ``value`` supplies the source algebra used to validate blade-bound rules.
    """

    if not isinstance(document, RenderDocument):
        raise TypeError("resolve expects a RenderDocument")
    value_algebra = getattr(value, "algebra", None)
    order: dict[Path, int] = {}
    for index, path in enumerate(_ordered_paths(document.body)):
        order.setdefault(path, index)
    placements: list[Placement] = []
    missing: list[Annotation] = []
    for rule in rules:
        if not isinstance(rule, Annotation):
            raise TypeError("annotation rules must be Annotation instances")
        paths = _select(document, rule.target, value_algebra)
        if not paths:
            if rule.missing == "error":
                raise MissingTargetError(f"annotation target {rule.target!r} matched no visible content")
            missing.append(rule)
            continue
        for path in paths:
            placements.append(Placement(rule, path, order.get(path, len(order))))
    return AnnotationPlan(tuple(placements), tuple(missing))
