"""Literal components retain their own provenance and displayed layout slots."""

from dataclasses import replace

import pytest

from galaga import Algebra, presets
from galaga.expression import BladeLiteral, Call, MultivectorLiteral, ScalarLiteral
from galaga.presentation import DisplayPolicy, Notation, RenderRule, default_presentation
from galaga.rendering import content_document, expression_document, expression_tree, latex


def _resolve(body, path):
    for key in path:
        body = body[key] if isinstance(key, int) else getattr(body, key)
    return body


def test_components_of_a_flattened_literal_sum_have_original_paths_and_final_slots():
    literal = MultivectorLiteral((1, -2, 0, 3))
    expression = Call("add", (literal, BladeLiteral(2)))
    document = expression_document(expression, default_presentation(2))
    assert document.body == expression_tree(expression, document.presentation)
    assert document.select("term") == ()
    terms = document.select("term", scope="expr")
    assert [(anchor.mask, anchor.term_index, anchor.expression_path) for anchor in terms] == [
        (0, 0, (0,)),
        (1, 1, (0,)),
        (3, 2, (0,)),
        (2, 3, (1,)),
    ]
    assert [anchor.mask for anchor in document.select("term", scope="expr", path=(0,), grade=2)] == [3]
    assert [anchor.mask for anchor in document.select("term", scope="expr", path=(1,))] == [2]
    assert [anchor.mask for anchor in document.select("coefficient", scope="expr")] == [0, 1, 3]
    assert [(anchor.mask, anchor.orientation) for anchor in document.select("sign", scope="expr")] == [
        (1, -1),
        (3, 1),
        (2, 1),
    ]
    for anchor in document.anchors:
        assert _resolve(document.body, anchor.render_path) is anchor.node
    for anchor in terms:
        displayed = document.body.terms[anchor.term_index]
        assert anchor.orientation == (-1 if displayed.negative else 1)


def test_operand_prefix_selection_includes_nested_literals_but_not_other_operands():
    expression = Call("outer_product", (Call("add", (BladeLiteral(1), BladeLiteral(2))), BladeLiteral(4)))
    document = expression_document(expression, default_presentation(3))
    assert [anchor.mask for anchor in document.select("term", scope="expr", path=(0,), grade=1)] == [1, 2]
    assert document.select("term", scope="expr", path=(0,), grade=2) == ()
    assert [anchor.expression_path for anchor in document.select("term", scope="expr", path=(0,))] == [(0, 0), (0, 1)]


def test_signed_rga_literal_orientation_matches_actual_algebra_and_label():
    algebra = Algebra(config=presets.rga())
    e1, _, e3, _ = algebra.basis_vectors()
    value = 2 * (e1 * e3)
    expression = MultivectorLiteral(value.data)
    document = expression_document(expression, algebra.presentation)
    assert latex.emit(document.body) == value.latex(content="value")
    for anchor in document.select("term", scope="expr"):
        displayed_coefficient = value.data[anchor.mask] * algebra.presentation.blades.label(anchor.mask).ref.orientation
        assert anchor.orientation == (-1 if displayed_coefficient < 0 else 1)
    assert document.select("sign", scope="expr", mask=5)[0].orientation == -1


@pytest.mark.parametrize("literal", [BladeLiteral(1, -1), MultivectorLiteral((0, -2)), ScalarLiteral(-2)])
def test_negative_singletons_keep_component_nodes_after_sign_absorption(literal):
    document = expression_document(Call("add", (MultivectorLiteral((1, 0)), literal)), default_presentation(1))
    terms = document.select("term", scope="expr", path=(1,))
    assert len(terms) == 1 and terms[0].term_index == 1 and terms[0].orientation == -1
    (sign,) = document.select("sign", scope="expr", path=(1,))
    assert sign.node is document.body and sign.term_index == 1
    for anchor in document.anchors:
        assert _resolve(document.body, anchor.render_path) is anchor.node


def test_subtraction_creates_a_visible_sign_for_a_positive_literal():
    document = expression_document(
        Call("subtract", (MultivectorLiteral((1, 2)), BladeLiteral(1))), default_presentation(1)
    )
    (sign,) = document.select("sign", scope="expr", path=(1,))
    assert sign.orientation == -1 and sign.term_index == 2


def test_repeated_definition_display_and_shared_source_literals_have_distinct_locations():
    literal = MultivectorLiteral((0, 2))
    presentation = replace(
        default_presentation(1), notation=Notation.default().with_rule("unit", RenderRule("unit_fraction"))
    )
    document = expression_document(Call("unit", (literal,)), presentation)
    coefficients = document.select("coefficient", scope="expr", path=(0,))
    assert len(coefficients) == 2
    assert coefficients[0].node is coefficients[1].node
    assert coefficients[0].render_path != coefficients[1].render_path
    repeated = expression_document(Call("add", (literal, literal)), default_presentation(1))
    assert [anchor.expression_path for anchor in repeated.select("term", scope="expr")] == [(0,), (1,)]


def test_hidden_removed_and_implicit_literal_components_have_no_anchor():
    presentation = replace(default_presentation(2), display=DisplayPolicy(zero_tolerance=0.01))
    document = expression_document(MultivectorLiteral((0, 1, 0.001, 0)), presentation)
    assert len(document.select("term", scope="expr")) == 1
    assert document.select("coefficient", scope="expr") == ()
    assert document.select("sign", scope="expr") == ()
    assert document.select("term", scope="expr", grade=2) == ()
    removed = expression_document(Call("scalar_multiply", (BladeLiteral(3),), {"scalar": 0}), presentation)
    assert removed.select("term", scope="expr", grade=2) == ()
    assert removed.select("term", scope="expr", path=(0,)) == ()
    assert expression_document(MultivectorLiteral((0, 0, 0, 0)), presentation).anchors == ()


def test_teaching_document_rebases_expression_components_without_mixing_the_result():
    algebra = Algebra(config=presets.euclidean(2))
    e1, e2 = algebra.basis_vectors()
    literal = MultivectorLiteral((0, 2, 0, 0))
    expression = Call("outer_product", (literal, BladeLiteral(2)))
    value = (2 * (e1 ^ e2)).with_expr(expression)
    document = content_document(value, content="full", target="latex")
    assert [anchor.mask for anchor in document.select("term", grade=2)] == [3]
    assert [anchor.mask for anchor in document.select("term", scope="expr", path=(0,))] == [1]
    assert document.select("term", scope="expr", grade=2) == ()
    assert latex.emit(document.body) == value.latex(content="full")
    for anchor in document.anchors:
        assert _resolve(document.body, anchor.render_path) is anchor.node


def test_expression_scope_validation():
    document = expression_document(BladeLiteral(1), default_presentation(1))
    for kwargs in ({"scope": "invalid"}, {"scope": "expr", "path": (-1,)}, {"path": ()}):
        with pytest.raises(ValueError):
            document.select("term", **kwargs)


def test_folded_scalars_have_a_new_component_scope_not_the_removed_operand_scopes():
    document = expression_document(Call("add", (ScalarLiteral(1), ScalarLiteral(-2))), default_presentation(1))
    assert document.select("term", scope="expr", path=(0,)) == ()
    assert document.select("term", scope="expr", path=(1,)) == ()
    (term,) = document.select("term", scope="expr", path=())
    assert term.mask == 0 and term.expression_path == () and term.orientation == -1


def test_scalar_literal_visibility_follows_its_existing_renderer_not_mv_tolerance():
    presentation = replace(default_presentation(1), display=DisplayPolicy(zero_tolerance=0.01))
    document = expression_document(ScalarLiteral(0.001), presentation)
    assert latex.emit(document.body) == "0.001"
    assert len(document.select("coefficient", scope="expr")) == 1
