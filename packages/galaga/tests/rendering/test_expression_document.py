"""Source occurrence and operator anchors remain independent of notation."""

from dataclasses import replace

import pytest

from galaga.expression import Call, ScalarLiteral, Symbol, simplify
from galaga.expression._simplify import _simplify_with_paths
from galaga.presentation import Notation, RenderRule, default_presentation
from galaga.rendering import Product, Sum, expression_document, expression_tree, latex, unicode
from galaga.rendering import ascii as ascii_renderer


def _call(operation, *operands, **parameters):
    return Call(operation, operands, parameters)


def _resolve(body, path):
    for key in path:
        body = body[key] if isinstance(key, int) else getattr(body, key)
    return body


@pytest.mark.parametrize("target", [None, "ascii", "unicode", "latex"])
def test_nested_implicit_products_have_distinct_extents_after_flattening(target):
    a, b, c = map(Symbol, "abc")
    expression = _call("geometric_product", _call("geometric_product", a, b), c)
    presentation = default_presentation(3)
    document = expression_document(expression, presentation, target=target)
    assert document.body == expression_tree(expression, presentation, target=target)
    assert isinstance(document.body, Product)
    outer, inner = document.select_expression("operator", operation_id="geometric_product")
    assert outer.path == () and outer.start is None and outer.stop is None
    assert inner.path == (0,) and (inner.start, inner.stop) == (0, 2)
    assert outer.implicit and inner.implicit
    assert outer.node is inner.node is document.body
    for anchor in document.expression_anchors:
        assert _resolve(document.body, anchor.render_path) is anchor.node
    for emitter in (ascii_renderer, unicode, latex):
        assert emitter.emit(document.body) == emitter.emit(expression_tree(expression, presentation, target=target))


def test_flattened_sum_keeps_the_binary_operation_join_slots():
    a, b, c, d = map(Symbol, "abcd")
    expression = _call("add", _call("add", a, b), _call("add", c, d))
    document = expression_document(expression, default_presentation(3))
    assert isinstance(document.body, Sum)
    root, left, right = document.select_expression("operator", operation_id="add")
    assert root.operator_indices == (2,)
    assert left.operator_indices == (1,)
    assert right.operator_indices == (3,)
    assert (left.start, left.stop) == (0, 2)
    assert (right.start, right.stop) == (2, 4)


@pytest.mark.parametrize(
    "notation, part",
    [
        (Notation.functional(), "function"),
        (Notation.default().with_rule("geometric_product", RenderRule("infix", symbol="*")), "operator"),
        (Notation.default().with_rule("geometric_product", RenderRule("juxtaposition", symbol="*")), "separator"),
    ],
)
def test_explicit_product_notations_use_the_operator_slot(notation, part):
    expression = _call("geometric_product", Symbol("a"), Symbol("b"))
    presentation = replace(default_presentation(2), notation=notation)
    document = expression_document(expression, presentation)
    (anchor,) = document.select_expression("operator")
    assert anchor.part == part
    assert not anchor.implicit
    assert anchor.node is document.body


def test_implicit_product_extent_is_local_and_contains_required_operand_groups():
    a, b, c = map(Symbol, "abc")
    product = _call("geometric_product", _call("add", a, b), c)
    document = expression_document(_call("add", product, a), default_presentation(3))
    (anchor,) = document.select_expression("operator", operation_id="geometric_product")
    assert anchor.render_path == ("terms", 0, "body")
    assert latex.emit(anchor.node) == r"\left(a + b\right) c"


def test_shared_source_symbols_keep_separate_occurrence_paths():
    x = Symbol("x")
    document = expression_document(_call("geometric_product", x, x), default_presentation(1))
    anchors = document.select_expression("symbol", name="x")
    assert [anchor.path for anchor in anchors] == [(0,), (1,)]
    assert [anchor.render_path for anchor in anchors] == [("factors", 0), ("factors", 1)]
    assert anchors[0].node is not anchors[1].node


def test_definition_notation_records_multiple_layout_occurrences_of_one_operand():
    presentation = replace(
        default_presentation(1), notation=Notation.default().with_rule("unit", RenderRule("unit_fraction"))
    )
    document = expression_document(_call("unit", Symbol("x")), presentation)
    anchors = document.select_expression("symbol", path=(0,))
    assert len(anchors) == 2
    assert anchors[0].render_path != anchors[1].render_path
    assert anchors[0].node is anchors[1].node


@pytest.mark.parametrize(
    "expression",
    [
        _call("add", Symbol("x"), ScalarLiteral(0)),
        _call("add", ScalarLiteral(0), Symbol("x")),
        _call("subtract", Symbol("x"), ScalarLiteral(0)),
        _call("scalar_multiply", Symbol("x"), scalar=1),
        _call("scalar_multiply", Symbol("x"), scalar=0),
        _call("scalar_multiply", ScalarLiteral(2), scalar=-1),
        _call("scalar_multiply", Symbol("x"), scalar=-1),
        _call("scalar_divide", Symbol("x"), scalar=1),
        _call("scalar_divide", ScalarLiteral(2), scalar=2),
        _call("power", Symbol("x"), exponent=0),
        _call("power", Symbol("x"), exponent=1),
        _call("power", ScalarLiteral(2), exponent=2),
        _call("negate", _call("negate", Symbol("x"))),
        _call("add", ScalarLiteral(1), ScalarLiteral(2)),
    ],
)
def test_source_mapping_uses_the_same_simplification_as_ordinary_rendering(expression):
    simplified, paths = _simplify_with_paths(expression)
    assert simplified == simplify(expression)
    for path in paths.values():
        node = simplified
        for index in path:
            node = node.operands[index]
    document = expression_document(expression, default_presentation(1))
    assert document.body == expression_tree(expression, document.presentation)
    assert document.select_expression("operator", path=()) == ()


def test_removed_product_does_not_annotate_its_replacement_zero():
    expression = _call(
        "add", Symbol("x"), _call("scalar_multiply", _call("geometric_product", Symbol("a"), Symbol("b")), scalar=0)
    )
    document = expression_document(expression, default_presentation(2))
    assert document.select_expression("operator", operation_id="geometric_product") == ()
    assert document.select_expression("symbol", name="a") == ()
    assert document.select_expression("symbol", name="x")[0].path == (0,)


def test_double_negation_keeps_only_the_original_leaf_occurrence():
    document = expression_document(_call("negate", _call("negate", Symbol("x"))), default_presentation(1))
    assert document.select_expression("operator") == ()
    assert document.select_expression("expression", path=(0,)) == ()
    assert document.select_expression("symbol")[0].path == (0, 0)


def test_removed_outer_operation_does_not_steal_a_same_named_inner_operation():
    expression = _call("add", _call("add", Symbol("a"), Symbol("b")), ScalarLiteral(0))
    document = expression_document(expression, default_presentation(1))
    assert document.select_expression("operator", path=()) == ()
    (anchor,) = document.select_expression("operator", operation_id="add")
    assert anchor.path == (0,)


def test_negative_scalar_product_keeps_its_extent_when_sum_absorbs_its_sign():
    expression = _call("add", Symbol("a"), _call("scalar_multiply", Symbol("b"), scalar=-2))
    document = expression_document(expression, default_presentation(1))
    (anchor,) = document.select_expression("operator", operation_id="scalar_multiply")
    assert anchor.implicit
    assert anchor.node is document.body
    assert (anchor.start, anchor.stop) == (1, 2)


def test_a_different_product_operation_counts_as_one_grouped_operand():
    notation = Notation.default().with_rule(
        "geometric_product", RenderRule("juxtaposition", symbol="*", flatten=True, associativity="associative")
    )
    presentation = replace(default_presentation(1), notation=notation)
    expression = _call("geometric_product", _call("scalar_multiply", Symbol("a"), scalar=2), Symbol("b"))
    document = expression_document(expression, presentation)
    (anchor,) = document.select_expression("operator", operation_id="geometric_product")
    assert anchor.operator_indices == (1,)


def test_minus_absorbed_into_sum_keeps_its_operator_sign_anchor():
    document = expression_document(_call("add", Symbol("a"), _call("negate", Symbol("b"))), default_presentation(1))
    (anchor,) = document.select_expression("operator", operation_id="negate")
    assert anchor.part == "sign" and anchor.operator_indices == (1,)
    assert (anchor.start, anchor.stop) == (1, 2)


def test_bad_expression_selectors_fail_and_absent_matches_are_empty():
    document = expression_document(Symbol("x"), default_presentation(1))
    assert document.select_expression("symbol", name="y") == ()
    assert document.select_expression(path=(5,)) == ()
    with pytest.raises(ValueError):
        document.select_expression("invalid")
    with pytest.raises(ValueError):
        document.select_expression(path=(-1,))
    with pytest.raises(TypeError):
        expression_document(object(), default_presentation(1))
    with pytest.raises(ValueError):
        expression_document(Symbol("x"), default_presentation(1), target="html")
