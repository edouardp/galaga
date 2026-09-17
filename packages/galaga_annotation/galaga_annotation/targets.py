"""Immutable semantic annotation targets for SPEC-015 and ADR-142.

Targets select displayed content by semantic identity, never by character
offsets. Selector factories in this module are conveniences over the target
dataclasses; the renderer resolves them against a semantic render document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from galaga import OPERATION_ALIASES, get_operation

__all__ = [
    "CoefficientTarget",
    "ExpressionPath",
    "GradeTarget",
    "OperationTarget",
    "TermTarget",
    "VariableTarget",
    "WholeExpression",
    "blade_mask",
    "coefficient",
    "coefficients",
    "grade",
    "grades",
    "operand",
    "operator",
    "path",
    "term",
    "terms",
    "variable",
    "whole",
]


def _canonical_operation(operation_id: str) -> str:
    if not isinstance(operation_id, str) or not operation_id:
        raise TypeError("operation id must be a non-empty string")
    canonical = OPERATION_ALIASES.get(operation_id, operation_id)
    try:
        return get_operation(canonical).id
    except KeyError as error:
        raise ValueError(f"unknown operation id {operation_id!r}") from error


def blade_mask(blade: Any) -> tuple[int, Any | None]:
    """Return ``(mask, algebra)`` for a basis blade, BladeRef, or raw mask.

    A multivector target must be a nonzero scalar multiple of exactly one
    basis blade. Its algebra is retained so recipes reject incompatible
    target algebras instead of reinterpreting a displayed name.
    """

    from galaga import Multivector

    if isinstance(blade, Multivector):
        data = np.asarray(blade.data)
        nonzero = np.flatnonzero(data)
        if nonzero.size != 1 or float(data[nonzero[0]]) == 0.0:
            raise ValueError("blade target must be a nonzero basis blade")
        return int(nonzero[0]), blade.algebra
    mask = getattr(blade, "mask", None)
    if mask is not None:
        if not isinstance(mask, int) or isinstance(mask, bool) or mask < 0:
            raise ValueError("blade mask must be a non-negative integer")
        return mask, None
    if isinstance(blade, int) and not isinstance(blade, bool):
        if blade < 0:
            raise ValueError("blade mask must be a non-negative integer")
        return blade, None
    raise TypeError("blade target must be a galaga basis blade, BladeRef, or non-negative mask")


def _checked_masks(values: Any, *, field_name: str) -> tuple[int, ...]:
    try:
        masks = tuple(values)
    except TypeError:
        raise TypeError(f"{field_name} must be an iterable of blade targets") from None
    if not masks:
        raise ValueError(f"{field_name} must contain at least one blade")
    for mask in masks:
        if not isinstance(mask, int) or isinstance(mask, bool) or mask < 0:
            raise ValueError(f"{field_name} must contain non-negative integer masks")
    return masks


@dataclass(frozen=True, slots=True)
class WholeExpression:
    """The complete displayed expression or value."""


@dataclass(frozen=True, slots=True)
class ExpressionPath:
    """One expression-tree node addressed by child indices; root is ``()``."""

    path: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.path, tuple) or any(
            not isinstance(index, int) or isinstance(index, bool) or index < 0 for index in self.path
        ):
            raise ValueError("expression path must be a tuple of non-negative integer indices")


@dataclass(frozen=True, slots=True)
class OperationTarget:
    """Operator occurrences identified by canonical operation id."""

    operation_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "operation_id", _canonical_operation(self.operation_id))


@dataclass(frozen=True, slots=True)
class VariableTarget:
    """Recorded named-symbol occurrences, selected by occurrence index."""

    name: str
    occurrence: int | Literal["all"] = 0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise TypeError("variable name must be a non-empty string")
        if self.occurrence != "all" and (
            not isinstance(self.occurrence, int) or isinstance(self.occurrence, bool) or self.occurrence < 0
        ):
            raise ValueError("variable occurrence must be 'all' or a non-negative integer")


@dataclass(frozen=True, slots=True)
class GradeTarget:
    """Complete displayed terms of the selected grades."""

    grades: tuple[int, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.grades, tuple) or not self.grades:
            raise ValueError("grade target must contain at least one grade")
        if any(not isinstance(grade, int) or isinstance(grade, bool) or grade < 0 for grade in self.grades):
            raise ValueError("grades must be non-negative integers")


@dataclass(frozen=True, slots=True)
class TermTarget:
    """Complete coefficient-plus-blade display terms."""

    masks: tuple[int, ...]
    algebra: Any = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "masks", _checked_masks(self.masks, field_name="term target"))


@dataclass(frozen=True, slots=True)
class CoefficientTarget:
    """Scalar coefficients of displayed terms, without their blades."""

    masks: tuple[int, ...]
    algebra: Any = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "masks", _checked_masks(self.masks, field_name="coefficient target"))


def whole() -> WholeExpression:
    """Select the complete displayed expression or value."""
    return WholeExpression()


def operand(index: int) -> ExpressionPath:
    """Select one root operand of the recorded expression."""
    return ExpressionPath((index,))


def path(*indices: int) -> ExpressionPath:
    """Select a nested expression node by child indices."""
    return ExpressionPath(tuple(indices))


def operator(operation_id: str) -> OperationTarget:
    """Select operator occurrences by canonical operation id or alias."""
    return OperationTarget(operation_id)


def variable(name: str, occurrence: int | Literal["all"] = 0) -> VariableTarget:
    """Select recorded named-symbol occurrences."""
    return VariableTarget(name, occurrence)


def grade(*grades: int) -> GradeTarget:
    """Select complete terms of one or more grades."""
    return GradeTarget(tuple(grades))


def grades(*grades: int) -> GradeTarget:
    """Select complete terms of one or more grades."""
    return GradeTarget(tuple(grades))


def term(blade: Any) -> TermTarget:
    """Select one complete coefficient-plus-blade term."""
    mask, algebra = blade_mask(blade)
    return TermTarget((mask,), algebra)


def terms(*blades: Any) -> TermTarget:
    """Select several complete coefficient-plus-blade terms."""
    masks = []
    algebra = None
    for blade in blades:
        mask, blade_algebra = blade_mask(blade)
        if algebra is None:
            algebra = blade_algebra
        elif blade_algebra is not None and blade_algebra is not algebra:
            raise ValueError("term targets must share one algebra")
        masks.append(mask)
    return TermTarget(tuple(masks), algebra)


def coefficient(blade: Any) -> CoefficientTarget:
    """Select only the scalar coefficient of one term."""
    mask, algebra = blade_mask(blade)
    return CoefficientTarget((mask,), algebra)


def coefficients(*blades: Any) -> CoefficientTarget:
    """Select only the scalar coefficients of several terms."""
    masks = []
    algebra = None
    for blade in blades:
        mask, blade_algebra = blade_mask(blade)
        if algebra is None:
            algebra = blade_algebra
        elif blade_algebra is not None and blade_algebra is not algebra:
            raise ValueError("coefficient targets must share one algebra")
        masks.append(mask)
    return CoefficientTarget(tuple(masks), algebra)


TARGET_TYPES = (
    WholeExpression,
    ExpressionPath,
    OperationTarget,
    VariableTarget,
    GradeTarget,
    TermTarget,
    CoefficientTarget,
)
