"""Matrix-region annotations and KaTeX lowering (SPEC-015 section 10).

Matrix annotations select cells or regions of a ``galaga_matrix.MatrixRepr``
by semantic coordinates. The adapter reads the companion package's public
``logical_shape`` and ``cell_latex`` hooks, so it never re-implements the
matrix conversion or the complex/quaternion cell formatting.

Only the LaTeX target is decorated. Lowering reuses the expression annotator's
style and marker wrappers by wrapping a raw cell in a ``Decorated`` node, so a
cell colour, fill, border, label, brace, or callout behaves exactly like the
equivalent expression decoration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from html import escape
from typing import Any

from galaga.rendering import Decorated, Text, emit

from ._decoration import decorate, default_side, style_body
from .model import Annotation
from .plan import MissingTargetError
from .targets import MatrixCell, MatrixRegion, WholeExpression, resolve_axis

__all__ = [
    "AnnotatedMatrix",
    "MatrixKatexResult",
    "MatrixPlacement",
    "MatrixPlan",
    "is_matrix",
    "render_matrix_katex",
    "resolve_matrix",
]

Cell = tuple[int, int]


def _matrix_class() -> type | None:
    """Return the companion ``MatrixRepr`` class when it is installed."""

    try:
        from galaga_matrix import MatrixRepr
    except ImportError:
        return None
    return MatrixRepr


def is_matrix(value: Any) -> bool:
    """Return whether ``value`` is a galaga_matrix representation."""

    matrix_class = _matrix_class()
    return matrix_class is not None and isinstance(value, matrix_class)


def _require_matrix(value: Any, operation: str) -> Any:
    matrix_class = _matrix_class()
    if matrix_class is None:
        raise ImportError(f"{operation} requires the optional galaga_matrix package")
    if not isinstance(value, matrix_class):
        raise TypeError(f"{operation} expects a galaga_matrix.MatrixRepr")
    return value


@dataclass(frozen=True, slots=True)
class MatrixPlacement:
    """One resolved rule bound to concrete matrix cells."""

    annotation: Annotation
    cells: tuple[Cell, ...]
    order: int
    whole: bool


@dataclass(frozen=True, slots=True)
class MatrixPlan:
    """Resolved matrix placements plus rules that matched nothing."""

    placements: tuple[MatrixPlacement, ...]
    missing: tuple[Annotation, ...]
    shape: tuple[int, int]


@dataclass(frozen=True, slots=True)
class MatrixKatexResult:
    """Annotated matrix LaTeX plus empty selections."""

    text: str
    missing: tuple[Annotation, ...]


def _target_cells(matrix: Any, target: Any) -> tuple[Cell, ...]:
    rows, columns = matrix.logical_shape
    if isinstance(target, WholeExpression):
        return tuple((row, column) for row in range(rows) for column in range(columns))
    if isinstance(target, MatrixCell):
        if target.row >= rows or target.column >= columns:
            raise ValueError(f"matrix cell ({target.row}, {target.column}) is out of range for shape {(rows, columns)}")
        return ((target.row, target.column),)
    if isinstance(target, MatrixRegion):
        row_indices = resolve_axis(target.rows, rows, field_name="matrix rows")
        column_indices = resolve_axis(target.columns, columns, field_name="matrix columns")
        return tuple((row, column) for row in row_indices for column in column_indices)
    raise TypeError(f"matrix annotations require a MatrixCell or MatrixRegion target, got {type(target).__name__}")


def resolve_matrix(matrix: Any, rules: Iterable[Annotation]) -> MatrixPlan:
    """Resolve matrix rules to concrete cells against one representation.

    Out-of-range coordinates are invalid requests and raise ``ValueError``; a
    valid selector that is empty (for example an empty slice) follows the rule's
    ``missing`` policy exactly like expression annotations.
    """

    matrix = _require_matrix(matrix, "resolve_matrix")
    shape = matrix.logical_shape
    total = shape[0] * shape[1]
    placements: list[MatrixPlacement] = []
    missing: list[Annotation] = []
    for order, rule in enumerate(rules):
        if not isinstance(rule, Annotation):
            raise TypeError("annotation rules must be Annotation instances")
        cells = _target_cells(matrix, rule.target)
        if not cells:
            if rule.missing == "error":
                raise MissingTargetError(f"matrix annotation target {rule.target!r} matched no visible cells")
            missing.append(rule)
            continue
        placements.append(MatrixPlacement(rule, cells, order, len(cells) == total))
    return MatrixPlan(tuple(placements), tuple(missing), shape)


def _raw_node(latex: str) -> Decorated:
    """Wrap already-rendered LaTeX so the shared marker wrappers can decorate it."""

    return Decorated(Text(""), latex, "")


def _decorate_cell(latex: str, annotation: Annotation, *, labelled: bool) -> str:
    node = _raw_node(latex)
    if labelled:
        node = decorate(node, annotation, default_side(annotation))
    else:
        node = style_body(node, annotation.style, marked=False)
    return emit(node, "latex")


def _decorate_region(grid: list[list[str]], placement: MatrixPlacement) -> None:
    anchor = placement.cells[0]
    for cell in placement.cells:
        labelled = cell == anchor
        grid[cell[0]][cell[1]] = _decorate_cell(grid[cell[0]][cell[1]], placement.annotation, labelled=labelled)


def _assemble(grid: list[list[str]]) -> str:
    backslash = chr(92)
    separator = " " + backslash * 2 + "\n"
    lines = [" & ".join(row) for row in grid]
    return backslash + "begin{pmatrix}\n" + separator.join(lines) + "\n" + backslash + "end{pmatrix}"


def _named(matrix: Any, body: str) -> str:
    name = matrix.symbolic_name
    if name is None:
        return body
    separator = " " + chr(92) + "quad = " + chr(92) + "quad "
    return f"{name.latex}{separator}{body}"


def render_matrix_katex(matrix: Any, rules: Iterable[Annotation]) -> MatrixKatexResult:
    """Render one matrix representation with resolved annotations as KaTeX."""

    matrix = _require_matrix(matrix, "render_matrix_katex")
    plan = resolve_matrix(matrix, rules)
    rows, columns = plan.shape
    grid = [[matrix.cell_latex(row, column) for column in range(columns)] for row in range(rows)]
    for placement in plan.placements:
        if not placement.whole:
            _decorate_region(grid, placement)
    body = _assemble(grid)
    for placement in plan.placements:
        if placement.whole:
            body = emit(decorate(_raw_node(body), placement.annotation, default_side(placement.annotation)), "latex")
    return MatrixKatexResult(_named(matrix, body), plan.missing)


@dataclass(frozen=True, slots=True)
class AnnotatedMatrix:
    """A matrix representation plus immutable annotation rules.

    Rendering-only, like :class:`galaga_annotation.Annotated`, with no
    arithmetic. Read-only matrix attributes are delegated to the wrapped value.
    """

    value: Any
    rules: tuple[Annotation, ...] = ()

    def __post_init__(self) -> None:
        if not is_matrix(self.value):
            raise TypeError("AnnotatedMatrix expects a galaga_matrix.MatrixRepr")
        rules = tuple(self.rules)
        if any(not isinstance(rule, Annotation) for rule in rules):
            raise TypeError("AnnotatedMatrix rules must be Annotation instances")
        object.__setattr__(self, "rules", rules)

    @property
    def plain(self) -> Any:
        """The original matrix representation, without annotation state."""
        return self.value

    def katex(self) -> MatrixKatexResult:
        """Render annotated LaTeX plus the unresolved rules."""
        return render_matrix_katex(self.value, self.rules)

    def latex(self) -> str:
        """Raw annotated matrix LaTeX."""
        return self.katex().text

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def _repr_html_(self) -> str | None:
        """Marimo inline math markup, mirroring the expression view."""
        try:
            import marimo  # noqa: F401
        except ImportError:
            return None
        latex = escape(self.latex(), quote=True)
        return f'<marimo-tex class="arithmatex">||({latex}||)</marimo-tex>'

    def display(self) -> Any:
        """The wrapped representation's own display result, without rules."""
        return self.value.display()

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "value"), name)

    def __str__(self) -> str:
        return self.latex()

    def __repr__(self) -> str:
        return f"AnnotatedMatrix({self.value!r}, rules={len(self.rules)})"
