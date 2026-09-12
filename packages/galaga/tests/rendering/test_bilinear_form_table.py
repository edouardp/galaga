"""Labelled Gram tables agree with the native algebra before rendering."""

import html
import re
import sys
from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from galaga import Algebra, scalar_product
from galaga.blades import BladeLabel, BladeRef, DisplayOrder, indexed_blade_convention
from galaga.display import BilinearFormTable, build_tree, emit, render
from galaga.names import Name
from galaga.presentation import DisplayPolicy, Notation, default_presentation
from galaga.presets import p_cga, p_rga, p_sta
from galaga.rendering import Identifier, Literal, Precedence, Table
from galaga.rendering._build import bilinear_form_tree


@pytest.mark.parametrize(
    "algebra",
    (
        Algebra(0),
        Algebra(3),
        Algebra(signature=(1, -1, 0)),
        Algebra(signature=(0, 0)),
        Algebra(gram=[[2, 0.5], [0.5, -1]]),
        Algebra(config=p_cga(3)),
        Algebra(config=p_cga(2, null_pair=-2)),
        Algebra(config=p_sta("mostly-minus")),
        Algebra(config=p_sta("mostly-plus")),
        Algebra(config=p_rga()),
    ),
)
def test_entries_and_headings_agree_with_computed_native_basis_products(algebra):
    original = algebra.gram.copy()
    basis = algebra.basis_vectors()
    table = algebra.bilinear_form_table()
    assert len(table.tree.headings) == len(table.tree.rows) == algebra.n
    for i, left in enumerate(basis):
        for target in ("ascii", "unicode", "latex"):
            assert emit(table.tree.headings[i], target) == left.display(content="value", target=target)
        for j, right in enumerate(basis):
            assert table.tree.rows[i][j].value == float(scalar_product(left, right)) == algebra.gram[i, j]
    np.testing.assert_array_equal(algebra.gram, original)
    assert table.latex().count(r"{\color{#bbbbbb}0}") == int(np.count_nonzero(original == 0))


def test_native_null_cga_layout_has_axis_labels_separators_and_scoped_grey_zeros():
    algebra = Algebra(config=p_cga(3))
    table = algebra.bilinear_form_table()
    latex = table.latex()
    lines = latex.splitlines()
    assert lines[0] == r"\begin{array}{c|ccccc}"
    assert lines[1] == r"\bullet & e_{o} & e_{1} & e_{2} & e_{3} & e_{\infty} \\"
    assert lines[2] == r"\hline" and lines[-1] == r"\end{array}"
    assert len(lines[3:-1]) == algebra.n
    for index, line in enumerate(lines[3:-1]):
        cells = line.removesuffix(r" \\").split(" & ")
        assert cells[0] == emit(table.tree.headings[index], "latex")
        expected = [r"{\color{#bbbbbb}0}" if value == 0 else f"{value:g}" for value in algebra.gram[index]]
        assert cells[1:] == expected
    assert r"\newcommand" not in latex and r"\z" not in latex and "$" not in latex
    assert table._repr_latex_() == "$$" + latex + "$$"


@pytest.mark.parametrize("orientation", (-1, 1))
def test_signed_basis_names_do_not_silently_change_the_stored_gram(orientation):
    labels = indexed_blade_convention(
        2, overrides={1: BladeLabel(Name("u", "υ", r"\upsilon"), BladeRef(1, orientation))}
    )
    algebra = Algebra(gram=[[2, 0.5], [0.5, -1]], blades=labels)
    table = algebra.bilinear_form_table()
    native, second = algebra.basis_vectors()
    named = algebra.blade("u")
    assert native == orientation * named
    assert table.tree.rows[0][1].value == float(scalar_product(native, second))
    assert table.tree.rows[0][1].value == orientation * float(scalar_product(named, second))
    assert emit(table.tree.headings[0], "latex") == native.latex(content="value")
    assert table.latex().count(r"-\upsilon") == (2 if orientation < 0 else 0)


def test_table_stays_in_native_order_even_when_multivector_display_order_changes():
    algebra = Algebra(gram=[[2, 0.5], [0.5, -1]])
    reordered = algebra.with_display_order(DisplayOrder(2, (0, 2, 1, 3)))
    assert algebra.bilinear_form_table() == reordered.bilinear_form_table()


def test_table_captures_scoped_names_precision_and_default_target():
    algebra = Algebra(gram=[[1.23456789, 0.5], [0.5, -1]])
    original = algebra.bilinear_form_table()
    selected = algebra.presentation.with_blades(indexed_blade_convention(2, prefix="x")).with_display(
        DisplayPolicy(coefficient_precision=3, target="ascii", zero_tolerance=1)
    )
    with algebra.use_presentation(selected):
        captured = algebra.bilinear_form_table()
        assert captured == algebra.with_presentation(selected).bilinear_form_table()
        assert "x1" in str(captured) and "1.23" in str(captured)
        assert "0.5" in str(captured)
    assert "x1" in str(captured) and "e1" not in str(captured)
    assert original == algebra.bilinear_form_table()
    assert "1.23457" in original.latex()


@pytest.mark.parametrize("small", (1e-16, -1e-16, np.nextafter(0.0, 1.0)))
def test_only_exact_zeros_are_muted_and_tiny_couplings_remain_visible(small):
    algebra = Algebra(gram=[[1, small], [small, 0]], display=DisplayPolicy(zero_tolerance=1))
    table = algebra.bilinear_form_table()
    assert table.tree.rows[0][1].value == small
    assert table.latex().count(r"{\color{#bbbbbb}0}") == 1
    assert "10^{" in table.latex()
    assert table.tree.rows[1][0].value != 0


def test_zero_dimensional_and_signed_zero_tables_are_well_formed():
    empty = Algebra(0).bilinear_form_table()
    assert empty.latex() == "\\begin{array}{c}\n\\bullet \\\\\n\\hline\n\\end{array}"
    assert empty.ascii() == ".\n-" and empty.unicode() == "•\n-"
    zero = Algebra(gram=[[-0.0]]).bilinear_form_table()
    assert "-0" not in zero.latex() and zero.latex().count("#bbbbbb") == 1


def test_public_hooks_and_shared_rendering_agree():
    table = Algebra(gram=[[2, 0.5], [0.5, -1]]).bilinear_form_table()
    for target in ("ascii", "unicode", "latex"):
        expected = getattr(table, target)()
        assert render(table, target=target) == expected
        assert format(table, target) == expected
        assert table.display(content="value", target=target) == expected
        assert render(table, "full/" + target) == expected
        assert build_tree(table, target=target) == (table.tree, target)
    assert str(table) == table.unicode() == format(table, "")
    assert repr(table) == table.ascii() == format(table, "a")
    assert table._galaga_block is True
    assert table.tree.precedence == Precedence.ATOM
    assert table.ascii() == " . |  e1  e2\n---+--------\ne1 |   2 0.5\ne2 | 0.5  -1"


def test_table_snapshot_and_semantic_rows_are_immutable():
    source = [[2, 0.5], [0.5, -1]]
    table = Algebra(gram=source).bilinear_form_table()
    source[0][0] = 9
    assert table.tree.rows[0][0].value == 2
    with pytest.raises(FrozenInstanceError):
        table.target = "latex"
    with pytest.raises(FrozenInstanceError):
        table.tree.rows = ()
    with pytest.raises(FrozenInstanceError):
        table.tree.rows[0][0].value = 9
    assert hash(table) == hash(Algebra(gram=[[2, 0.5], [0.5, -1]]).bilinear_form_table())


@pytest.mark.parametrize(
    "kwargs",
    (
        {"content": "name"},
        {"content": "expr"},
        {"target": "html"},
        {"presentation": default_presentation(1)},
        {"notation": Notation.default()},
    ),
)
def test_unsupported_table_display_requests_fail_explicitly(kwargs):
    with pytest.raises(ValueError):
        render(Algebra(1).bilinear_form_table(), **kwargs)


@pytest.mark.parametrize(
    "headings,rows,corner,error",
    (
        (None, (), Identifier("."), TypeError),
        (("x",), ((Literal(1),),), Identifier("."), TypeError),
        ((), None, Identifier("."), TypeError),
        ((Identifier("x"),), (None,), Identifier("."), TypeError),
        ((Identifier("x"),), ((1,),), Identifier("."), TypeError),
        ((Identifier("x"),), (), Identifier("."), ValueError),
        ((Identifier("x"),), ((),), Identifier("."), ValueError),
        ((), (), ".", TypeError),
    ),
)
def test_invalid_semantic_table_shapes_fail_at_construction(headings, rows, corner, error):
    with pytest.raises(error):
        Table(headings, rows, corner=corner)


def test_invalid_display_table_and_builder_inputs_fail_explicitly():
    with pytest.raises(TypeError):
        BilinearFormTable(Identifier("x"))
    with pytest.raises(ValueError):
        BilinearFormTable(Table((), (), corner=Identifier(".")), target="html")
    with pytest.raises(ValueError):
        bilinear_form_tree([[1]], default_presentation(2))
    with pytest.raises(TypeError):
        bilinear_form_tree([[1]], None)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="native template strings require Python 3.14")
def test_marimo_standalone_and_template_rendering_have_one_math_wrapper():
    gm = pytest.importorskip("galaga_marimo")
    mo = pytest.importorskip("marimo")
    table = Algebra(config=p_cga(3)).bilinear_form_table()
    for output in (mo.as_html(table), gm.md(eval('t"{table}"')), gm.md(eval('t"{table:block}"'))):
        markup = html.unescape(output.text)
        equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
        assert len(equations) == 1
        # Marimo transports display-math boundaries as ||[ ... ||].
        assert equations[0].strip() == "||[" + table.latex() + "||]"
        assert "$" not in equations[0] and "#bbbbbb" in equations[0]


def test_semantic_table_can_render_non_numeric_cells_without_zero_styling():
    tree = Table((Identifier("x"),), ((Identifier("z"),),), corner=Identifier("."))
    assert "x & z" in emit(tree, "latex")
    assert "#bbbbbb" not in emit(tree, "latex")
