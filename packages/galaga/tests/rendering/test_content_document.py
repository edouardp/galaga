"""Teaching documents follow captured presentation and emitted visibility."""

import pytest

from galaga import Algebra, Presenter, presets
from galaga.rendering import ascii as ascii_renderer
from galaga.rendering import content_document, latex, unicode


def _resolve(body, path):
    for key in path:
        body = body[key] if isinstance(key, int) else getattr(body, key)
    return body


@pytest.mark.parametrize("target, emitter", [("ascii", ascii_renderer), ("unicode", unicode), ("latex", latex)])
@pytest.mark.parametrize("content", [None, "name", "expr", "value", "full"])
def test_content_document_matches_regular_display_and_all_locations_resolve(target, emitter, content):
    algebra = Algebra(config=presets.euclidean(2), expr=True)
    e1, e2 = algebra.basis_vectors()
    value = ((e1 + e2) ^ e2).named("B")
    assert value == e1 ^ e2
    original = value.numeric, value.expr, algebra.presentation
    document = content_document(value, content=content, target=target)
    assert emitter.emit(document.body) == value.display(content=content, target=target)
    assert document.target == target
    for anchor in (*document.anchors, *document.expression_anchors, *document.content_anchors):
        assert _resolve(document.body, anchor.render_path) is anchor.node
    assert (value.numeric, value.expr, algebra.presentation) == original


def test_named_teaching_equality_has_separate_expression_result_and_relation_anchors():
    algebra = Algebra(config=presets.euclidean(2), expr=True)
    e1, e2 = algebra.basis_vectors()
    value = ((e1 + e2) ^ e2).named("B")
    document = content_document(value, content="full", target="latex")
    assert [anchor.kind for anchor in document.content_anchors] == ["name", "expr", "relation", "value", "relation"]
    assert [anchor.relation_index for anchor in document.select_content("relation")] == [1, 2]
    (operator,) = document.select_expression("operator", operation_id="outer_product")
    assert operator.render_path == ("parts", 1)
    (term,) = document.select("term", grade=2)
    assert term.render_path == ("parts", 2)
    assert document.select_content("value")[0].node is term.node


def test_duplicate_result_is_hidden_and_does_not_redirect_its_component_annotations():
    algebra = Algebra(config=presets.euclidean(2), expr=True)
    e1, e2 = algebra.basis_vectors()
    document = content_document(e1 + e2, content="full", target="latex")
    assert document.select_content("expr")
    assert document.select_content("value") == ()
    assert document.select_content("relation") == ()
    assert document.select("term") == ()
    assert document.select_expression("operator", operation_id="add")
    explicit_result = content_document(e1 + e2, content="value", target="latex")
    assert len(explicit_result.select("term")) == 2


def test_duplicate_part_visibility_depends_on_output_target():
    algebra = Algebra(config=presets.euclidean(1))
    value = algebra.basis_vectors()[0].named("q", latex="e_{1}")
    latex_doc = content_document(value, content="full", target="latex")
    ascii_doc = content_document(value, content="full", target="ascii")
    assert latex_doc.select_content("value") == ()
    assert latex.emit(latex_doc.body) == value.latex(content="full")
    assert len(ascii_doc.select_content("relation")) == 1
    assert ascii_doc.select_content("value")
    assert ascii_renderer.emit(ascii_doc.body) == value.ascii(content="full")


@pytest.mark.parametrize("content", ["name", "expr", "full"])
def test_missing_name_and_provenance_fall_back_to_concrete_value(content):
    algebra = Algebra(config=presets.euclidean(1))
    value = algebra.scalar(2)
    document = content_document(value, content=content)
    assert document.select_content("value")
    assert document.select_content("expr") == ()
    assert document.select_content("name") == ()
    assert unicode.emit(document.body) == value.display(content=content)


def test_view_documents_use_capture_and_support_explicit_notation_override():
    algebra = Algebra(config=presets.euclidean(2), expr=True)
    e1, e2 = algebra.basis_vectors()
    value = (e1 ^ e2).named("B")
    view = presets.presenters.functional()(value)
    captured = view.render_document(content="full", target="latex")
    with algebra.use_notation(presets.notation.lengyel()):
        assert view.render_document(content="full", target="latex") == captured
    (functional,) = captured.select_expression("operator", operation_id="outer_product")
    assert functional.part == "function"
    overridden = view.render_document(content="full", target="latex", notation=presets.notation.lengyel())
    (geometric,) = overridden.select_expression("operator", operation_id="outer_product")
    assert geometric.part == "operator"
    assert latex.emit(overridden.body) == view.display(
        content="full", target="latex", notation=presets.notation.lengyel()
    )
    assert view.presentation is captured.presentation
    explicit = view.render_document(content="full", target="latex", presentation=algebra.presentation)
    assert explicit.presentation is algebra.presentation
    assert latex.emit(explicit.body) == value.latex(content="full")
    assert view.presentation is captured.presentation


def test_view_document_preserves_content_and_blade_order_choices():
    algebra = Algebra(config=presets.euclidean(3))
    value = algebra.multivector(range(1, 9))
    view = Presenter(content="value", display_order="bitmap")(value)
    document = view.render_document()
    assert [anchor.mask for anchor in document.select("term")] == list(range(8))
    assert document.presentation is view.presentation
    assert unicode.emit(document.body) == view.unicode()


def test_invalid_content_document_requests_fail():
    algebra = Algebra(config=presets.euclidean(1))
    for kwargs in ({"content": "invalid"}, {"target": "html"}, {"notation": "invalid"}):
        with pytest.raises((ValueError, TypeError)):
            content_document(algebra.identity, **kwargs)
    with pytest.raises(TypeError):
        content_document(object())
    with pytest.raises(ValueError):
        content_document(algebra.identity).select_content("invalid")
