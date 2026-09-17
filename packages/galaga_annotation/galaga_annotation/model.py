"""Immutable annotation rules and renderer-neutral styles (ADR-142).

Semantic roles and visual styles stay separate: the same role may be coloured
differently in two lessons without changing what the annotation means.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

from .targets import TARGET_TYPES, WholeExpression

__all__ = [
    "Annotation",
    "AnnotationStyle",
    "Marker",
    "MissingPolicy",
    "Side",
    "on",
]

Marker = Literal[
    "none",
    "arrow",
    "rule",
    "brace",
    "underline",
    "box",
    "underbrace",
    "overbrace",
    "undergroup",
    "overgroup",
]
Side = Literal["above", "below", "auto"]
MissingPolicy = Literal["ignore", "error"]
Emphasis = Literal["normal", "bold", "italic"]

MARKERS: frozenset[str] = frozenset(
    {"none", "arrow", "rule", "brace", "underline", "box", "underbrace", "overbrace", "undergroup", "overgroup"}
)
DIRECTIONAL_MARKERS: dict[str, str] = {
    "underbrace": "below",
    "undergroup": "below",
    "underline": "below",
    "overbrace": "above",
    "overgroup": "above",
}

_COLOR = re.compile(r"^(#[0-9a-fA-F]{3,8}|[a-zA-Z]{2,32})$")
_DIMENSION = re.compile(r"^\d+(?:\.\d+)?(?:em|ex|pt|px|mu|rem|%)$")


def _checked_color(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _COLOR.match(value):
        raise ValueError(f"{field_name} must be a hex or named colour")
    return value


def _checked_dimension(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _DIMENSION.match(value):
        raise ValueError(f"{field_name} must be a CSS/TeX dimension such as '4px' or '0.5em'")
    return value


@dataclass(frozen=True, slots=True)
class AnnotationStyle:
    """Renderer-neutral visual style for one annotation."""

    color: str | None = None
    background: str | None = None
    border: str | None = None
    label_color: str | None = None
    emphasis: Emphasis = "normal"
    marker: Marker = "none"
    clearance: str | None = None
    overlay: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "color", _checked_color(self.color, field_name="color"))
        object.__setattr__(self, "background", _checked_color(self.background, field_name="background"))
        object.__setattr__(self, "border", _checked_color(self.border, field_name="border"))
        object.__setattr__(self, "label_color", _checked_color(self.label_color, field_name="label_color"))
        if self.emphasis not in {"normal", "bold", "italic"}:
            raise ValueError("emphasis must be 'normal', 'bold', or 'italic'")
        if self.marker not in MARKERS:
            raise ValueError(f"unknown marker {self.marker!r}")
        if not isinstance(self.overlay, bool):
            raise TypeError("overlay flag must be a boolean")
        object.__setattr__(self, "clearance", _checked_dimension(self.clearance, field_name="clearance"))


def _check_optional_text(value: Any, *, field_name: str) -> None:
    if value is not None and not isinstance(value, str):
        raise TypeError(f"annotation {field_name} must be a string or None")


def _validate_labels(label: str | None, label_latex: str | None) -> bool:
    _check_optional_text(label, field_name="label")
    _check_optional_text(label_latex, field_name="label_latex")
    if label is not None and label_latex is not None:
        raise ValueError("pass either label or label_latex, not both")
    return label is not None or label_latex is not None


def _validate_style_context(style: AnnotationStyle, *, has_label: bool) -> None:
    if style.label_color is not None and not has_label:
        raise ValueError("label_color requires label or label_latex")
    if style.overlay and style.marker == "none":
        raise ValueError("overlay requires a marker")
    if style.clearance is not None and not has_label and style.marker == "none":
        raise ValueError("clearance requires a label or marker")


def _validate_placement(side: str, missing: str, marker: str) -> None:
    if side not in {"above", "below", "auto"}:
        raise ValueError("side must be 'above', 'below', or 'auto'")
    if missing not in {"ignore", "error"}:
        raise ValueError("missing must be 'ignore' or 'error'")
    direction = DIRECTIONAL_MARKERS.get(marker)
    if direction is not None and side not in {"auto", direction}:
        raise ValueError(f"marker {marker!r} is {direction}-only; side={side!r} contradicts it")


@dataclass(frozen=True, slots=True)
class Annotation:
    """One immutable rule: select a semantic target, attach presentation."""

    target: Any
    label: str | None = None
    label_latex: str | None = None
    role: str | None = None
    style: AnnotationStyle = field(default_factory=AnnotationStyle)
    side: Side = "auto"
    description: str | None = None
    missing: MissingPolicy = "ignore"
    join: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.target, TARGET_TYPES):
            raise TypeError("annotation target must be a galaga_annotation target")
        if not isinstance(self.style, AnnotationStyle):
            raise TypeError("annotation style must be an AnnotationStyle")
        if not isinstance(self.join, bool):
            raise TypeError("annotation join flag must be a boolean")
        has_label = _validate_labels(self.label, self.label_latex)
        _check_optional_text(self.role, field_name="role")
        _check_optional_text(self.description, field_name="description")
        _validate_style_context(self.style, has_label=has_label)
        _validate_placement(self.side, self.missing, self.style.marker)


def on(
    target: Any | None = None,
    *,
    label: str | None = None,
    label_latex: str | None = None,
    role: str | None = None,
    style: AnnotationStyle | None = None,
    side: Side = "auto",
    description: str | None = None,
    missing: MissingPolicy = "ignore",
    join: bool = False,
    color: str | None = None,
    background: str | None = None,
    border: str | None = None,
    label_color: str | None = None,
    emphasis: Emphasis = "normal",
    marker: Marker = "none",
    clearance: str | None = None,
    overlay: bool = False,
) -> Annotation:
    """Construct one immutable annotation rule.

    Pass either a complete ``style`` or the individual style fields, not both.
    A missing target defaults to the whole expression or value.
    """

    if target is None:
        target = WholeExpression()
    if not isinstance(target, TARGET_TYPES):
        from .targets import ExpressionPath

        if isinstance(target, tuple) and all(
            isinstance(index, int) and not isinstance(index, bool) for index in target
        ):
            target = ExpressionPath(target)
        else:
            raise TypeError("annotation target must be a galaga_annotation target")
    fields_given = (
        (color, background, border, label_color, clearance) != (None, None, None, None, None)
        or emphasis != "normal"
        or marker != "none"
        or overlay
    )
    if style is not None and fields_given:
        raise ValueError("pass either style= or individual style fields, not both")
    if style is None:
        style = AnnotationStyle(
            color=color,
            background=background,
            border=border,
            label_color=label_color,
            emphasis=emphasis,
            marker=marker,
            clearance=clearance,
            overlay=overlay,
        )
    return Annotation(
        target=target,
        label=label,
        label_latex=label_latex,
        role=role,
        style=style,
        side=side,
        description=description,
        missing=missing,
        join=join,
    )
