"""Semantic anchor contracts derived from actual value rendering."""

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace

import pytest

from galaga import Algebra, Presenter, presets
from galaga.presentation import DisplayPolicy
from galaga.rendering import Literal, Node, Sum, latex, unicode, value_document, value_tree
from galaga.rendering import ascii as ascii_renderer


def _nodes(node: Node):
    """Walk render objects by occurrence, including non-Node SumTerm objects."""
    if isinstance(node, Node):
        yield node
    if is_dataclass(node):
        for field in fields(node):
            child = getattr(node, field.name)
            if isinstance(child, tuple):
                for member in child:
                    yield from _nodes(member)
            elif is_dataclass(child):
                yield from _nodes(child)


@pytest.mark.parametrize("coefficients", [(0, 0, 0, 0), (2, 0, 0, 0), (0, -2, 0, 0), (0, -1, 0, 0), (1, -2, 1, 3)])
def test_document_keeps_existing_tree_output_and_references_actual_nodes(coefficients):
    algebra = Algebra(config=presets.euclidean(2))
    value = algebra.multivector(coefficients)
    before = tuple(value.data)
    document = value_document(value)
    assert document.body == value_tree(value)
    for emitter in (ascii_renderer, unicode, latex):
        assert emitter.emit(document.body) == emitter.emit(value_tree(value))
    nodes = tuple(_nodes(document.body))
    assert all(any(anchor.node is node for node in nodes) for anchor in document.anchors)
    assert tuple(value.data) == before
    assert document.presentation is algebra.presentation


def test_terms_and_signs_are_slots_in_the_shared_sum():
    algebra = Algebra(config=presets.euclidean(2))
    document = value_document(algebra.multivector((1, -2, 1, 3)))
    assert isinstance(document.body, Sum)
    terms = document.select("term")
    assert [anchor.mask for anchor in terms] == list(algebra.presentation.display_order.masks)
    for anchor in terms:
        assert anchor.node is document.body
        assert anchor.term_index is not None
        assert anchor.orientation == (-1 if document.body.terms[anchor.term_index].negative else 1)
    assert [anchor.mask for anchor in document.select("sign")] == [1, 2, 3]
    assert document.select("coefficient", mask=2) == ()  # Unit coefficient omitted.
    assert document.select("blade", mask=0) == ()  # Scalar has no blade symbol.
    assert len(document.select("term", grade=1)) == 2


def test_displayed_orientation_is_computed_from_the_signed_blade_convention():
    algebra = Algebra(config=presets.rga())
    e1, _, e3, _ = algebra.basis_vectors()
    value = 2 * (e1 * e3)
    document = value_document(value)
    for anchor in document.select("term"):
        native = value.data[anchor.mask]
        label = document.presentation.blades.label(anchor.mask)
        assert anchor.orientation == (-1 if native * label.ref.orientation < 0 else 1)
    assert document.select("sign", mask=5)[0].orientation == -1
    assert document.select("coefficient", mask=5)[0].node == Literal(2)
    assert latex.emit(document.body) == value.latex(content="value")


def test_anchor_selection_follows_final_order_and_visibility():
    algebra = Algebra(config=presets.euclidean(3))
    value = algebra.multivector((1, 2, 3, 4, 5, 6, 7, 8))
    bitmap = Presenter(display_order="bitmap")(value)
    document = value_document(value, bitmap.presentation)
    assert [anchor.mask for anchor in document.select("term")] == list(range(8))
    assert [anchor.mask for anchor in value_document(value).select("term")] == [0, 1, 2, 4, 3, 5, 6, 7]
    assert value_document(algebra.scalar(0)).anchors == ()
    assert value_document(algebra.scalar(1)).select("term", grade=2) == ()
    presentation = replace(algebra.presentation, display=DisplayPolicy(zero_tolerance=0.01))
    assert value_document(algebra.multivector((0, 0.001, 0, 0, 0, 0, 0, 0)), presentation).anchors == ()


def test_rounded_unit_coefficient_and_leading_plus_remain_implicit():
    algebra = Algebra(config=presets.euclidean(1))
    presentation = replace(algebra.presentation, display=DisplayPolicy(coefficient_precision=3))
    document = value_document(algebra.multivector((0, 1.00001)), presentation)
    assert document.select("coefficient") == ()
    assert document.select("sign") == ()
    assert len(document.select("term")) == 1


def test_documents_are_frozen_and_bad_selectors_fail():
    algebra = Algebra(config=presets.euclidean(1))
    document = value_document(algebra.basis_vectors()[0])
    with pytest.raises(FrozenInstanceError):
        document.body = Literal(99)
    with pytest.raises(FrozenInstanceError):
        document.anchors[0].mask = 0
    for selector in ({"grade": -1}, {"mask": True}, {"grade": 1.5}):
        with pytest.raises(ValueError):
            document.select("term", **selector)
    with pytest.raises(ValueError, match="kind"):
        document.select("unknown")
    with pytest.raises(TypeError, match="Multivector"):
        value_document(object())
