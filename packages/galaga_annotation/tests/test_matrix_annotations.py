"""Matrix cell/region target resolution and KaTeX lowering contracts."""

from __future__ import annotations

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra
from galaga.rendering import content_document

galaga_matrix = pytest.importorskip("galaga_matrix")
from galaga_matrix import MatrixRepr, to_matrix  # noqa: E402


@pytest.fixture()
def grid() -> MatrixRepr:
    return MatrixRepr(np.arange(9).reshape(3, 3))


@pytest.fixture()
def named_grid() -> MatrixRepr:
    return MatrixRepr(np.arange(9).reshape(3, 3)).name("M")


def test_matrix_targets_are_annotation_targets() -> None:
    assert ga.MatrixCell in ga.ANNOTATION_TARGET_TYPES
    assert ga.MatrixRegion in ga.ANNOTATION_TARGET_TYPES
    rule = ga.on(ga.cell(0, 1), label="entry")
    assert rule.target == ga.MatrixCell(0, 1)


def test_matrix_cell_and_axis_validation() -> None:
    assert ga.cell(1, 2) == ga.MatrixCell(1, 2)
    with pytest.raises(ValueError, match="non-negative"):
        ga.cell(-1, 0)
    with pytest.raises(ValueError, match="non-negative"):
        ga.cell(0, True)
    with pytest.raises(ValueError, match="non-negative"):
        ga.cell(0, 1.5)
    with pytest.raises(TypeError, match="int, slice, or sequence"):
        ga.MatrixRegion(rows="0")
    with pytest.raises(ValueError, match="non-negative"):
        ga.MatrixRegion(rows=-1)
    with pytest.raises(ValueError, match="non-negative"):
        ga.MatrixRegion(rows=slice(-1, 2))
    with pytest.raises(ValueError, match="step"):
        ga.MatrixRegion(rows=slice(0, 2, 0))


def test_selector_factories_build_regions() -> None:
    assert ga.row(2) == ga.MatrixRegion(rows=2, columns=slice(None))
    assert ga.column(1) == ga.MatrixRegion(columns=1)
    assert ga.block(rows=[0, 2], columns=1) == ga.MatrixRegion(rows=(0, 2), columns=1)


def test_resolve_axis_expands_and_validates() -> None:
    assert ga.resolve_axis(1, 3, field_name="row") == (1,)
    assert ga.resolve_axis(slice(0, 2), 4, field_name="row") == (0, 1)
    assert ga.resolve_axis((2, 0, 2), 3, field_name="row") == (0, 2)
    assert ga.resolve_axis(slice(2, 2), 4, field_name="row") == ()
    with pytest.raises(ValueError, match="out of range"):
        ga.resolve_axis(3, 3, field_name="row")
    with pytest.raises(ValueError, match="out of range"):
        ga.resolve_axis(slice(0, 5), 4, field_name="row")
    with pytest.raises(ValueError, match="out of range"):
        ga.resolve_axis((0, 5), 4, field_name="row")


def test_resolve_matrix_expands_cells_rows_columns_and_blocks(grid: MatrixRepr) -> None:
    plan = ga.resolve_matrix(
        grid,
        [
            ga.on(ga.cell(0, 1)),
            ga.on(ga.row(1)),
            ga.on(ga.column(2)),
            ga.on(ga.block(rows=slice(1, 3), columns=slice(0, 2))),
        ],
    )
    assert plan.shape == (3, 3)
    assert [placement.cells for placement in plan.placements] == [
        ((0, 1),),
        ((1, 0), (1, 1), (1, 2)),
        ((0, 2), (1, 2), (2, 2)),
        ((1, 0), (1, 1), (2, 0), (2, 1)),
    ]
    assert [placement.whole for placement in plan.placements] == [False, False, False, False]


def test_resolve_matrix_detects_whole_matrix_selection(grid: MatrixRepr) -> None:
    plan = ga.resolve_matrix(grid, [ga.on(ga.block())])
    assert plan.placements[0].whole is True


def test_resolve_matrix_out_of_range_cell_is_invalid(grid: MatrixRepr) -> None:
    with pytest.raises(ValueError, match="out of range"):
        ga.resolve_matrix(grid, [ga.on(ga.cell(5, 0))])


def test_resolve_matrix_empty_selection_follows_missing_policy(grid: MatrixRepr) -> None:
    empty = ga.on(ga.block(rows=slice(2, 2)), label="gone")
    plan = ga.resolve_matrix(grid, [empty])
    assert plan.placements == ()
    assert plan.missing == (empty,)
    with pytest.raises(ga.MissingTargetError):
        ga.resolve_matrix(grid, [ga.on(ga.block(rows=slice(2, 2)), missing="error")])


def test_resolve_matrix_accepts_whole_value_target(grid: MatrixRepr) -> None:
    plan = ga.resolve_matrix(grid, [ga.on(ga.whole(), label="operator")])
    assert plan.placements[0].whole is True


def test_resolve_matrix_rejects_non_whole_expression_targets(grid: MatrixRepr) -> None:
    with pytest.raises(TypeError, match="MatrixCell or MatrixRegion"):
        ga.resolve_matrix(grid, [ga.on(ga.grade(1))])


def test_expression_resolution_rejects_matrix_targets() -> None:
    algebra = Algebra(2, expr=True)
    e1, _ = algebra.basis_vectors(expr=True)
    document = content_document(e1, content="value", target="latex")
    with pytest.raises(TypeError, match="matrix targets"):
        ga.resolve(document, [ga.on(ga.cell(0, 0))], value=e1)


def test_cell_background_and_border_lower_to_katex(grid: MatrixRepr) -> None:
    text = ga.annotate(
        grid,
        ga.on(ga.cell(1, 1), background="#e8f5e9"),
    ).latex()
    assert r"\colorbox{#e8f5e9}{$4$}" in text
    assert text.count(r"\colorbox") == 1  # neighbouring cells stay undecorated

    bordered = ga.annotate(
        grid,
        ga.on(ga.cell(0, 0), border="seagreen", background="#fff3cd"),
    ).latex()
    assert r"\fcolorbox{seagreen}{#fff3cd}{$0$}" in bordered


def test_transparent_border_has_no_implied_theme(grid: MatrixRepr) -> None:
    text = ga.annotate(grid, ga.on(ga.cell(2, 2), border="seagreen")).latex()
    assert r"\fcolorbox{seagreen}{transparent}{$8$}" in text


def test_cell_label_lowers_to_a_cell_callout(grid: MatrixRepr) -> None:
    text = ga.annotate(
        grid,
        ga.on(ga.cell(0, 0), label="origin", label_color="#2f7d4f"),
    ).latex()
    assert r"\overset{\textcolor{#2f7d4f}{\text{origin}}}{0}" in text


def test_region_style_covers_every_cell_but_labels_once(grid: MatrixRepr) -> None:
    text = ga.annotate(
        grid,
        ga.on(ga.block(rows=slice(1, 3), columns=slice(1, 3)), background="#e8f5e9", label="block"),
    ).latex()
    assert text.count(r"\colorbox{#e8f5e9}{$") == 4
    assert text.count(r"\text{block}") == 1
    # The label anchors to the region's first cell.
    assert r"\overset{\text{block}}{\colorbox{#e8f5e9}{$4$}}" in text


def test_whole_matrix_annotation_wraps_the_environment(grid: MatrixRepr) -> None:
    text = ga.annotate(
        grid,
        ga.on(ga.block(), background="#e8f5e9", label="operator", marker="underbrace"),
    ).latex()
    assert r"\colorbox{#e8f5e9}{$" in text
    assert r"\underbrace{" in text
    assert r"\end{pmatrix}$}}_{\text{operator}}" in text


def test_named_matrix_keeps_its_symbolic_name(named_grid: MatrixRepr) -> None:
    text = ga.annotate(named_grid, ga.on(ga.cell(0, 0), background="#e8f5e9")).latex()
    assert text.startswith("M")
    assert r"\quad = \quad" in text


def test_quaternion_mode_uses_logical_cells() -> None:
    sta = Algebra(1, 3)
    g0 = sta.basis_vectors()[0]
    matrix = to_matrix(g0, mode="quaternion")
    assert matrix.logical_shape == (2, 2)
    text = ga.annotate(matrix, ga.on(ga.cell(0, 0), background="#e8f5e9")).latex()
    assert r"\colorbox{#e8f5e9}{$1$}" in text


def test_whole_value_shorthand_annotates_the_whole_matrix(grid: MatrixRepr) -> None:
    text = ga.annotate(grid, label="operator", marker="underbrace").latex()
    assert r"\underbrace" in text and r"}_{\text{operator}}" in text


def test_annotated_matrix_view_is_transparent_and_read_only(grid: MatrixRepr) -> None:
    view = ga.annotate(grid, ga.on(ga.cell(0, 0), background="#e8f5e9"))
    assert isinstance(view, ga.AnnotatedMatrix)
    assert view.plain is grid
    assert view.value is grid
    assert view.shape == (3, 3)
    data = grid.mat.copy()
    assert view.latex() == view.katex().text
    np.testing.assert_array_equal(grid.mat, data)
    for operation in (lambda: view + view, lambda: view * 2, lambda: -view):
        with pytest.raises(TypeError):
            operation()


def test_annotator_dispatch_and_repr_paths(grid: MatrixRepr) -> None:
    recipe = ga.annotator(ga.on(ga.cell(1, 1), background="#e8f5e9"))
    view = recipe(grid)
    assert isinstance(view, ga.AnnotatedMatrix)
    assert view.rules == recipe.rules
    assert view._repr_latex_() == "$" + view.latex() + "$"


def test_matrix_view_rejects_non_matrix_values() -> None:
    mv = Algebra(2).scalar(1.0)
    with pytest.raises(TypeError, match="MatrixRepr"):
        ga.AnnotatedMatrix(mv)
    assert ga.is_matrix(mv) is False


def test_matrix_repr_renders_one_marimo_math_block(grid: MatrixRepr) -> None:
    pytest.importorskip("marimo")
    view = ga.annotate(grid, ga.on(ga.cell(0, 0), background="#e8f5e9"))
    html = view._repr_html_()
    assert html is not None
    assert html.count("<marimo-tex") == 1 and html.count("</marimo-tex>") == 1
    assert "||(" in html
