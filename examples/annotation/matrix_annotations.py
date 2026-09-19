"""Annotate matrix representations by cell, row, column and block."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    import galaga_annotation as ga
    from galaga import Algebra
    from galaga_matrix import from_matrix, to_matrix

    return Algebra, from_matrix, ga, gm, mo, np, to_matrix


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Annotating a matrix representation

    `galaga_matrix` turns a multivector into a matrix. The annotations you
    already use for expressions also select matrix content, but by
    **zero-based coordinates** instead of expression paths:

    | Selector | Semantic target |
    |---|---|
    | `ga.cell(row, column)` | one entry |
    | `ga.row(index)` / `ga.column(index)` | a complete row / column |
    | `ga.block(rows=..., columns=...)` | a rectangle or an index list |

    A whole-value label (`ga.whole()` or the `ga.annotate(matrix, label=...)`
    shorthand) covers the entire matrix. As always, annotations are
    presentation metadata: the numbers and the representation do not change.
    """)
    return


@app.cell
def _(Algebra, to_matrix):
    algebra = Algebra(2, expr=True)
    e1, e2 = algebra.basis_vectors(expr=True)
    value = (1.0 + 2.0 * e1 - e2 + 3.0 * (e1 ^ e2)).named("A")
    matrix = to_matrix(value, mode="left-regular")
    return algebra, e1, e2, matrix, value


@app.cell
def _(from_matrix, gm, matrix, np, value):
    recovered = from_matrix(matrix.algebra, matrix.mat, mode="left-regular")
    roundtrip_ok = bool(np.allclose(recovered.data, value.data))
    gm.md(t"""
    ## The value and its left-regular matrix

    `to_matrix` keeps the source multivector's name, so the display reads
    $A = \rho(A)$.

    Value: {value}

    Matrix (rows and columns follow the basis order
    $1, e_1, e_2, e_{12}$):

    {matrix:block}

    Round-trip `from_matrix(to_matrix(A)) == A`: **{roundtrip_ok}**
    """)
    return (roundtrip_ok,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Single cells and a resolved plan

    `ga.cell(r, c)` selects one entry. A cell label becomes a callout on that
    entry, and `ga.resolve_matrix` exposes exactly which coordinates a rule
    matched.
    """)
    return


@app.cell
def _(ga, gm, matrix):
    cell_view = ga.annotate(
        matrix,
        ga.on(ga.cell(0, 0), background="#e8f5e9", label="scalar input", label_color="#2f7d4f"),
        ga.on(ga.cell(0, 3), background="#fff3cd", label="bivector input", label_color="#8a6d1a"),
    )
    cell_plan = ga.resolve_matrix(
        matrix,
        [
            ga.on(ga.cell(0, 0)),
            ga.on(ga.cell(0, 3)),
        ],
    )
    cell_plan_summary = [placement.cells for placement in cell_plan.placements]
    gm.md(t"""
    **Two entries called out:** {cell_view:block}

    Resolved coordinates: `{cell_plan_summary}`
    """)
    return cell_plan_summary, cell_view


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rows and columns

    `ga.row(n)` and `ga.column(n)` select a whole line. A region label anchors
    to the region's first cell, so the row keeps one label while every cell in
    it is styled.
    """)
    return


@app.cell
def _(ga, gm, matrix):
    line_view = ga.annotate(
        matrix,
        ga.on(ga.row(1), color="#0072B2", label="row for e1"),
        ga.on(ga.column(2), background="#f3e8ff"),
    )
    gm.md(t"**A coloured row and a filled column:** {line_view:block}")
    return (line_view,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Grade blocks

    In the left-regular representation, rows and columns follow basis order, so
    each grade's basis blades form a rectangular block. We derive the blocks
    from the algebra rather than hardcoding indices, then fill each
    grade × grade block.
    """)
    return


@app.cell
def _(algebra, ga, gm, matrix):
    grade_masks = {
        grade: tuple(mask for mask in range(algebra.dim) if mask.bit_count() == grade) for grade in (0, 1, 2)
    }
    grade_fills = {0: "#e8e8e8", 1: "#d6e8f7", 2: "#f7dfd6"}
    grade_view = ga.annotator(
        *[
            ga.on(ga.block(rows=masks, columns=masks), background=grade_fills[grade])
            for grade, masks in grade_masks.items()
        ]
    )(matrix)
    gm.md(t"""
    Grade masks: `{grade_masks}`

    **Each grade's block filled:** {grade_view:block}
    """)
    return grade_masks, grade_view


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A labelled block and a whole-matrix callout

    A rectangular block can carry a border and a label (anchored to its first
    cell), while a whole-value rule brackets the entire matrix environment.
    """)
    return


@app.cell
def _(ga, gm, matrix):
    block_view = ga.annotate(
        matrix,
        ga.on(ga.block(rows=slice(1, 3), columns=slice(1, 3)), border="seagreen", background="#e8f5e9"),
        ga.on(ga.block(rows=slice(1, 3), columns=slice(1, 3)), label="vector × vector", side="below"),
    )
    whole_view = ga.annotate(
        matrix,
        background="#f8f9fa",
        border="#b8c7d9",
        label="left multiplication by A",
        marker="underbrace",
    )
    gm.md(t"""
    **Labelled block:** {block_view:block}

    **Whole-matrix callout:** {whole_view:block}
    """)
    return block_view, whole_view


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Quaternion-entry matrices

    Quaternion mode stores each displayed entry as a 2×2 complex block.
    `logical_shape` reports the displayed grid, so `ga.cell(0, 0)` addresses
    the first quaternion entry, not the underlying 4×4 array.
    """)
    return


@app.cell
def _(Algebra, ga, gm, to_matrix):
    sta = Algebra(1, 3)
    gamma0 = sta.basis_vectors()[0]
    quaternion_matrix = to_matrix(gamma0, mode="quaternion")
    quat_view = ga.annotate(
        quaternion_matrix,
        ga.on(ga.cell(0, 0), background="#e8f5e9", label="+1 block"),
        ga.on(ga.cell(1, 1), background="#fff3cd", label="−1 block"),
    )
    gm.md(t"""
    Logical shape: `{quaternion_matrix.logical_shape}` (underlying array
    `{quaternion_matrix.mat.shape}`).

    **Quaternion entries annotated:** {quat_view:block}
    """)
    return gamma0, quat_view, quaternion_matrix, sta


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The view stays read-only and transparent

    `AnnotatedMatrix` is a rendering view. `plain` is the original
    representation, and arithmetic is deliberately unavailable.
    """)
    return


@app.cell
def _(cell_view, matrix):
    transparent = cell_view.plain is matrix
    shape_delegated = cell_view.shape == matrix.shape
    arithmetic_blocked = False
    try:
        _ = cell_view + cell_view
    except TypeError:
        arithmetic_blocked = True
    summary = {
        "plain is matrix": transparent,
        "shape delegated": shape_delegated,
        "arithmetic blocked": arithmetic_blocked,
    }
    summary
    return (summary,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Empty selections and invalid regions

    A valid but empty selector follows the ordinary `missing` policy, while an
    out-of-range coordinate is an invalid request and raises.
    """)
    return


@app.cell
def _(ga, gm, matrix):
    empty_view = ga.annotator(ga.on(ga.block(rows=slice(2, 2)), label="no rows"))(matrix)
    empty_labels = [rule.label for rule in empty_view.katex().missing]
    strict_rule = ga.on(ga.block(rows=slice(2, 2)), label="strict", missing="error")
    strict_result = "not raised"
    try:
        ga.annotator(strict_rule)(matrix).latex()
    except ga.MissingTargetError as error:
        strict_result = type(error).__name__
    out_of_range_result = "not raised"
    try:
        ga.annotator(ga.on(ga.cell(9, 0)))(matrix).latex()
    except ValueError as error:
        out_of_range_result = type(error).__name__
    gm.md(t"""
    **Ignored empty selection:** `{empty_labels}`

    **Opt-in error:** `{strict_result}`

    **Out-of-range cell:** `{out_of_range_result}`
    """)
    return empty_labels, out_of_range_result, strict_result


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - Matrix annotations reuse the expression styles and markers, so a cell
      colour, fill, border or label behaves exactly like an expression one.
    - Targets are semantic coordinates: cells, rows, columns, index lists and
      rectangles. `ga.block(rows=[...], columns=[...])` handles non-contiguous
      selections.
    - A whole-value rule brackets the matrix; a partial-region label anchors to
      the region's first cell.
    - The adapter is optional and read-only: importing `galaga_annotation`
      never imports `galaga_matrix`, and the view never changes the numbers.
    """)
    return


if __name__ == "__main__":
    app.run()
