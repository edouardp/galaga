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
from galaga.expression import Expr

__all__ = [
    "CoefficientTarget",
    "ContentKind",
    "ContentTarget",
    "ExpressionPath",
    "GradeTarget",
    "MatrixAxis",
    "MatrixCell",
    "MatrixRegion",
    "OperationTarget",
    "SignTarget",
    "SubexpressionTarget",
    "TermTarget",
    "VariableTarget",
    "WholeExpression",
    "blade_mask",
    "block",
    "cell",
    "coefficient",
    "coefficients",
    "column",
    "content",
    "grade",
    "grades",
    "operand",
    "operator",
    "path",
    "resolve_axis",
    "row",
    "sign",
    "signs",
    "subexpression",
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


ContentKind = Literal["name", "expr", "value"]


@dataclass(frozen=True, slots=True)
class ContentTarget:
    """One displayed content part: the variable name, expression, or value.

    These are the parts ``content_document`` shows as ``name = expr = value``.
    A target matches only when the active content setting displays that part.
    """

    kind: ContentKind

    def __post_init__(self) -> None:
        if self.kind not in {"name", "expr", "value"}:
            raise ValueError("content target kind must be 'name', 'expr', or 'value'")


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
class SubexpressionTarget:
    """Provenance subtree occurrences, matched structurally.

    The expression is compared to the recorded source subtree at every
    surviving expression path, so a target follows an edited expression as
    long as the same subtree remains. Matching is structural, never numeric.
    """

    expression: Expr
    occurrence: int | Literal["all"] = "all"

    def __post_init__(self) -> None:
        if not isinstance(self.expression, Expr):
            raise TypeError("subexpression target requires a galaga.expression.Expr")
        if self.occurrence != "all" and (
            not isinstance(self.occurrence, int) or isinstance(self.occurrence, bool) or self.occurrence < 0
        ):
            raise ValueError("subexpression occurrence must be 'all' or a non-negative integer")


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


@dataclass(frozen=True, slots=True)
class SignTarget:
    """Displayed signs of terms, without their coefficients or blades."""

    masks: tuple[int, ...]
    algebra: Any = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "masks", _checked_masks(self.masks, field_name="sign target"))


def whole() -> WholeExpression:
    """Select the complete displayed expression or value."""
    return WholeExpression()


def content(kind: ContentKind) -> ContentTarget:
    """Select one displayed content part: 'name', 'expr', or 'value'."""
    return ContentTarget(kind)


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


def subexpression(value: Any, occurrence: int | Literal["all"] = "all") -> SubexpressionTarget:
    """Select provenance subtree occurrences matching ``value`` structurally.

    ``value`` may be a ``galaga.expression.Expr`` or a tracked value whose
    ``expr`` is one. Matching requires expression provenance on the annotated
    value; an untracked value is an invalid request rather than an empty match.
    """

    if isinstance(value, Expr):
        expression = value
    else:
        expression = getattr(value, "expr", None)
        if not isinstance(expression, Expr):
            raise TypeError("subexpression target requires a galaga.expression.Expr or a tracked value")
    return SubexpressionTarget(expression, occurrence)


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


def sign(blade: Any) -> SignTarget:
    """Select only the displayed sign of one term."""
    mask, algebra = blade_mask(blade)
    return SignTarget((mask,), algebra)


def signs(*blades: Any) -> SignTarget:
    """Select only the displayed signs of several terms."""
    masks = []
    algebra = None
    for blade in blades:
        mask, blade_algebra = blade_mask(blade)
        if algebra is None:
            algebra = blade_algebra
        elif blade_algebra is not None and blade_algebra is not algebra:
            raise ValueError("sign targets must share one algebra")
        masks.append(mask)
    return SignTarget(tuple(masks), algebra)


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
    ContentTarget,
    ExpressionPath,
    OperationTarget,
    VariableTarget,
    SubexpressionTarget,
    GradeTarget,
    TermTarget,
    CoefficientTarget,
    SignTarget,
)

MatrixAxis = int | slice | tuple[int, ...] | list[int]


def _checked_non_negative(value: Any, *, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _normalize_axis(value: Any, *, field_name: str) -> MatrixAxis:
    """Normalize one row/column selector to an int, slice, or index tuple."""

    if isinstance(value, bool) or not isinstance(value, (int, slice, tuple, list)):
        raise TypeError(f"{field_name} must be an int, slice, or sequence of ints")
    if isinstance(value, int):
        return _checked_non_negative(value, field_name=field_name)
    if isinstance(value, slice):
        for part in (value.start, value.stop, value.step):
            if part is not None:
                _checked_non_negative(part, field_name=field_name)
        if value.step is not None and value.step == 0:
            raise ValueError(f"{field_name} slice step must be positive")
        return value
    indices = tuple(value)
    for index in indices:
        _checked_non_negative(index, field_name=field_name)
    return indices


def resolve_axis(axis: MatrixAxis, size: int, *, field_name: str) -> tuple[int, ...]:
    """Expand one normalized matrix axis against a concrete dimension.

    Out-of-range coordinates are invalid requests and raise ``ValueError``;
    an in-range but empty selector (for example ``slice(2, 2)``) yields ``()``
    and is handled by the ordinary empty-selection policy.
    """

    if isinstance(axis, int):
        if axis >= size:
            raise ValueError(f"{field_name} index {axis} is out of range for size {size}")
        return (axis,)
    if isinstance(axis, slice):
        if axis.stop is not None and axis.stop > size:
            raise ValueError(f"{field_name} stop {axis.stop} is out of range for size {size}")
        return tuple(range(size))[axis]
    for index in axis:
        if index >= size:
            raise ValueError(f"{field_name} index {index} is out of range for size {size}")
    return tuple(sorted(set(axis)))


@dataclass(frozen=True, slots=True)
class MatrixCell:
    """One matrix coordinate, addressed as zero-based ``(row, column)``."""

    row: int
    column: int

    def __post_init__(self) -> None:
        _checked_non_negative(self.row, field_name="matrix cell row")
        _checked_non_negative(self.column, field_name="matrix cell column")


@dataclass(frozen=True, slots=True)
class MatrixRegion:
    """A rectangular or index-list region of a matrix representation.

    Each axis may be an ``int``, a ``slice`` (half-open, positive step), or a
    sequence of indices. The whole matrix is ``MatrixRegion()``.
    """

    rows: MatrixAxis = slice(None)
    columns: MatrixAxis = slice(None)

    def __post_init__(self) -> None:
        object.__setattr__(self, "rows", _normalize_axis(self.rows, field_name="matrix rows"))
        object.__setattr__(self, "columns", _normalize_axis(self.columns, field_name="matrix columns"))


def cell(row: int, column: int) -> MatrixCell:
    """Select one matrix entry by zero-based row and column."""
    return MatrixCell(row, column)


def row(index: int) -> MatrixRegion:
    """Select one complete matrix row."""
    return MatrixRegion(rows=_checked_non_negative(index, field_name="matrix row"))


def column(index: int) -> MatrixRegion:
    """Select one complete matrix column."""
    return MatrixRegion(columns=_checked_non_negative(index, field_name="matrix column"))


def block(rows: MatrixAxis = slice(None), columns: MatrixAxis = slice(None)) -> MatrixRegion:
    """Select a rectangular or index-list matrix region."""
    return MatrixRegion(rows=rows, columns=columns)


MATRIX_TARGET_TYPES = (MatrixCell, MatrixRegion)

# Matrices are a companion representation, not part of an expression document,
# so their targets are accepted by rules but resolved by the matrix renderer.
ANNOTATION_TARGET_TYPES = (*TARGET_TYPES, *MATRIX_TARGET_TYPES)
