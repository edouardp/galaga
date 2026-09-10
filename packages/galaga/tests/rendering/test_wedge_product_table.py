"""Exterior tables must agree with computed products, including signed names."""

import html
import re
import sys
from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from galaga import Algebra, outer_product
from galaga.blades import BladeLabel, BladeRef, DisplayOrder, indexed_blade_convention
from galaga.display import BilinearFormTable, WedgeProductTable, build_tree, emit, render
from galaga.names import Name
from galaga.presentation import DisplayPolicy, default_presentation
from galaga.presets import p_cga, p_rga, p_sta
from galaga.rendering import GradeColor, Identifier, Literal, Prefix
from galaga.rendering._build import wedge_product_tree


@pytest.mark.parametrize(
    "algebra",
    (
        Algebra(0),
        Algebra(1),
        Algebra(3),
        Algebra(signature=(1, -1, 0)),
        Algebra(signature=(0, 0, 0)),
        Algebra(gram=[[2, 0.5], [0.5, -1]]),
        Algebra(config=p_cga(3)),
        Algebra(config=p_cga(2, null_pair=-2)),
        Algebra(config=p_sta("mostly-minus")),
        Algebra(config=p_rga()),
    ),
)
@pytest.mark.parametrize("full", (False, True))
def test_table_entries_agree_with_computed_native_wedge_products(algebra, full):
    original = algebra.gram.copy()
    masks = (
        sorted(range(algebra.dim), key=lambda mask: (mask.bit_count(), mask))
        if full
        else [1 << index for index in range(algebra.n)]
    )
    blades = [algebra.blade(mask) for mask in masks]
    table = algebra.wedge_product_table(full)
    assert len(table.tree.headings) == len(table.tree.rows) == len(blades)
    zero_count = 0
    for i, left in enumerate(blades):
        for target in ("ascii", "unicode", "latex"):
            assert emit(table.tree.headings[i], target) == left.display(target=target, content="value")
        for j, right in enumerate(blades):
            product = outer_product(left, right)
            for target in ("ascii", "unicode", "latex"):
                assert emit(table.tree.rows[i][j], target) == product.display(target=target, content="value")
            zero_count += int(not np.any(product.data))
    assert table.latex().count(r"{\color{#bbbbbb}0}") == zero_count
    np.testing.assert_array_equal(algebra.gram, original)


def test_cga_vector_table_matches_requested_layout():
    table = Algebra(config=p_cga(3)).wedge_product_table()
    lines = table.latex().splitlines()
    assert lines[0] == r"\begin{array}{c|ccccc}"
    assert lines[1] == r"\wedge & e_{1} & e_{2} & e_{3} & e_{o} & e_{\infty} \\"
    assert lines[2] == r"\hline" and lines[-1] == r"\end{array}"
    assert lines[3] == r"e_{1} & {\color{#bbbbbb}0} & e_{12} & e_{13} & e_{1o} & e_{1\infty} \\"
    assert (
        lines[-2] == r"e_{\infty} & -e_{1\infty} & -e_{2\infty} & -e_{3\infty} & -e_{o\infty} & {\color{#bbbbbb}0} \\"
    )
    assert r"\newcommand" not in table.latex() and "$" not in table.latex()


def test_full_table_starts_with_scalar_and_groups_all_native_blades_by_grade():
    algebra = Algebra(3)
    table = algebra.wedge_product_table(full=True)
    assert [emit(node, "ascii") for node in table.tree.headings] == ["1", "e1", "e2", "e3", "e12", "e13", "e23", "e123"]
    for index, heading in enumerate(table.tree.headings):
        assert table.tree.rows[0][index] == table.tree.rows[index][0] == heading
    assert len(Algebra(config=p_cga(3)).wedge_product_table(full=True).tree.rows) == 32
    assert len(Algebra(0).wedge_product_table().tree.rows) == 0
    assert Algebra(0).wedge_product_table(full=True).tree.rows == ((Literal(1),),)


def test_scalar_one_is_not_replaced_by_a_custom_scalar_blade_name():
    labels = indexed_blade_convention(1, overrides={0: Name("scalar")})
    table = Algebra(1, blades=labels).wedge_product_table(full=True)
    assert table.tree.headings[0] == table.tree.rows[0][0] == Literal(1)
    assert "scalar" not in table.latex()


@pytest.mark.parametrize("full", (False, True))
def test_signed_input_and_output_blade_names_match_actual_products(full):
    labels = indexed_blade_convention(
        2,
        overrides={
            1: BladeLabel(Name("u", "υ", r"\upsilon"), BladeRef(1, -1)),
            3: BladeLabel(Name("B"), BladeRef(3, -1)),
        },
    )
    algebra = Algebra(gram=[[2, 0.5], [0.5, -1]], blades=labels)
    table = algebra.wedge_product_table(full)
    offset = int(full)
    assert emit(table.tree.headings[offset], "latex") == algebra.blade(1).latex() == r"-\upsilon"
    assert emit(table.tree.rows[offset][offset + 1], "latex") == outer_product(*algebra.basis_vectors()).latex() == "-B"
    assert emit(table.tree.rows[offset + 1][offset], "latex") == "B"


@pytest.mark.parametrize("full", (False, True))
def test_metric_display_order_and_zero_tolerance_do_not_change_wedge_entries(full):
    euclidean = Algebra(3)
    oblique = Algebra(gram=[[2, 0.5, 0], [0.5, -1, 0.25], [0, 0.25, 0]])
    hidden = oblique.with_display(DisplayPolicy(zero_tolerance=2, content="name"))
    reordered = hidden.with_display_order(DisplayOrder(3, tuple(reversed(range(8)))))
    assert euclidean.wedge_product_table(full) == reordered.wedge_product_table(full)


def test_table_captures_scoped_presentation_and_target():
    algebra = Algebra(2)
    original = algebra.wedge_product_table()
    teaching = algebra.presentation.with_blades(indexed_blade_convention(2, prefix="x")).with_display(
        DisplayPolicy(target="ascii", zero_tolerance=2)
    )
    with algebra.use_presentation(teaching):
        table = algebra.wedge_product_table()
        assert table == algebra.with_presentation(teaching).wedge_product_table()
    assert "x12" in str(table) and str(table).lstrip().startswith("^")
    assert original == algebra.wedge_product_table()


@pytest.mark.parametrize("full", (False, True))
def test_both_colour_spellings_enable_the_same_grade_decoration(full):
    algebra = Algebra(3)
    plain = algebra.wedge_product_table(full)
    coloured = algebra.wedge_product_table(full, color=True)
    assert coloured == algebra.wedge_product_table(full, colour=True)
    assert coloured == algebra.wedge_product_table(full, color=True, colour=True)
    assert coloured == algebra.wedge_product_table(full, color=False, colour=True)
    assert plain == algebra.wedge_product_table(full, color=False, colour=False)
    assert coloured.ascii() == plain.ascii() and coloured.unicode() == plain.unicode()
    assert coloured.tree.headings == plain.tree.headings
    masks = sorted(range(algebra.dim), key=lambda mask: (mask.bit_count(), mask)) if full else [1, 2, 4]
    for i, left in enumerate(masks):
        for j, right in enumerate(masks):
            product = outer_product(algebra.blade(left), algebra.blade(right))
            cell = coloured.tree.rows[i][j]
            if np.any(product.data):
                assert isinstance(cell, GradeColor)
                result_mask = int(np.flatnonzero(product.data)[0])
                assert cell.grade == result_mask.bit_count()
                assert cell.body == plain.tree.rows[i][j]
            else:
                assert cell == Literal(0)
    assert coloured.latex().count("#bbbbbb") == plain.latex().count("#bbbbbb")
    assert coloured.latex().count(r"\color{") > coloured.latex().count("#bbbbbb")


def test_colours_are_stable_by_grade_not_dimension_and_include_scalar_and_sign():
    small = Algebra(2).wedge_product_table(True, color=True)
    large = Algebra(config=p_cga(3)).wedge_product_table(True, colour=True)
    assert emit(small.tree.rows[1][2], "latex") == emit(large.tree.rows[1][2], "latex")
    assert emit(small.tree.rows[0][0], "latex") == r"{\color{#111827}1}"
    assert emit(small.tree.rows[0][1], "latex") == r"{\color{#0072B2}e_{1}}"
    assert emit(small.tree.rows[1][2], "latex") == r"{\color{#D55E00}e_{12}}"
    assert emit(small.tree.rows[2][1], "latex") == r"{\color{#D55E00}-e_{12}}"
    palette = [emit(GradeColor(Identifier("B"), grade), "latex") for grade in range(8)]
    assert len(set(palette)) == 8
    assert emit(GradeColor(Identifier("B"), 9), "latex") == palette[1]
    assert all(emit(GradeColor(Identifier("B"), grade), "ascii") == "B" for grade in range(10))


@pytest.mark.parametrize("parameter", ("full", "color", "colour"))
@pytest.mark.parametrize("invalid", (None, 0, 1, "true", np.bool_(True)))
def test_flags_require_real_booleans(parameter, invalid):
    with pytest.raises(TypeError, match=f"{parameter} must be a boolean"):
        Algebra(2).wedge_product_table(**{parameter: invalid})


def test_rich_display_protocol_and_shared_dispatch_are_unchanged():
    table = Algebra(2).wedge_product_table(True, color=True)
    assert isinstance(table, WedgeProductTable) and not isinstance(table, BilinearFormTable)
    for target in ("ascii", "unicode", "latex"):
        expected = getattr(table, target)()
        assert render(table, target=target) == format(table, target) == expected
        assert table.display("full/" + target) == expected
        assert build_tree(table, target=target) == (table.tree, target)
    assert table._repr_latex_() == "$$" + table.latex() + "$$"
    assert str(table) == table.unicode() and repr(table) == table.ascii()
    assert table._galaga_block is True
    assert hash(table) == hash(Algebra(2).wedge_product_table(True, color=True))
    with pytest.raises(FrozenInstanceError):
        table.target = "latex"
    with pytest.raises(FrozenInstanceError):
        table.tree.rows[0][0].grade = 2
    with pytest.raises(ValueError, match="only has value content"):
        table.display(content="expr")
    with pytest.raises(ValueError, match="presentation is captured"):
        render(table, presentation=default_presentation(2))


def test_table_construction_and_rendering_do_not_allocate_or_evaluate_multivectors(monkeypatch):
    import galaga.core as core

    algebra = Algebra(3)

    def unexpected(*args, **kwargs):
        pytest.fail("a wedge-table snapshot must reuse exterior metadata")

    monkeypatch.setattr(core.Multivector, "__init__", unexpected)
    monkeypatch.setattr(core, "outer_product", unexpected)
    assert "e_{123}" in algebra.wedge_product_table(True, color=True).latex()


@pytest.mark.parametrize("grade", (-1, 1.5, "2", True, None))
def test_grade_colour_rejects_invalid_grades(grade):
    with pytest.raises(ValueError, match="non-negative integer"):
        GradeColor(Identifier("x"), grade)


def test_grade_colour_validates_its_body_and_preserves_precedence():
    with pytest.raises(TypeError, match="semantic render node"):
        GradeColor("x", 1)
    body = Prefix("-", Identifier("B"), precedence=40)
    colour = GradeColor(body, np.int64(2))
    assert colour.precedence == body.precedence
    assert emit(colour, "ascii") == emit(colour, "unicode") == "-B"


@pytest.mark.parametrize("factors", ((), ((0, 1),), ((2,),)))
def test_builder_rejects_invalid_exterior_coefficients(factors):
    with pytest.raises(ValueError):
        wedge_product_tree((1,), factors, default_presentation(1), color=False)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="native template strings require Python 3.14")
def test_marimo_standalone_and_template_display_support_coloured_full_table():
    gm = pytest.importorskip("galaga_marimo")
    mo = pytest.importorskip("marimo")
    table = Algebra(2).wedge_product_table(full=True, colour=True)
    for output in (mo.as_html(table), gm.md(eval('t"{table}"')), gm.md(eval('t"{table:block}"'))):
        markup = html.unescape(output.text)
        equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
        assert len(equations) == 1
        assert equations[0].strip() == "||[" + table.latex() + "||]"
        assert "#bbbbbb" in equations[0] and "#D55E00" in equations[0]
