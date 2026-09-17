"""Resolution of semantic targets to layout paths."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra, Symbol, geometric_product, outer_product
from galaga.expression import Call
from galaga.rendering import content_document


@pytest.fixture()
def algebra() -> Algebra:
    return Algebra(3, expr=True)


def _document(value, **kwargs):
    return content_document(value, content="full", target="latex", **kwargs)


def test_whole_expression_resolves_to_the_body(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    value = outer_product(e1, e2).named("A")
    plan = ga.resolve(_document(value), [ga.on(ga.whole(), label="whole")], value=value)
    assert [placement.path for placement in plan.placements] == [()]
    assert plan.missing == ()


def test_expression_paths_and_operators_resolve_to_their_occurrences(algebra: Algebra) -> None:
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    value = outer_product(e1 + e2, e3).named("A")
    plan = ga.resolve(
        _document(value),
        [
            ga.on(ga.operand(0), label="left"),
            ga.on(ga.operator("op"), label="wedge"),
            ga.on(ga.operator("geometric_product"), label="never here"),
        ],
        value=value,
    )
    paths = [placement.path for placement in plan.placements]
    assert ("parts", 1, "operands", 0, "body") in paths
    assert ("parts", 1, "operator") in paths
    assert plan.missing[0].label == "never here"


def test_implicit_geometric_product_anchors_the_whole_product(algebra: Algebra) -> None:
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    value = geometric_product(e1 + e2, e3).named("P")
    plan = ga.resolve(_document(value), [ga.on(ga.operator("gp"), label="product")], value=value)
    assert [placement.path for placement in plan.placements] == [("parts", 1)]


def test_value_component_selectors_follow_the_visible_result(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    value = (0.5 + 2 * e1 - 3 * (e1 ^ e2)).named("C")
    plan = ga.resolve(
        _document(value),
        [
            ga.on(ga.term(e1), label="vector"),
            ga.on(ga.coefficient(e1), label="weight"),
            ga.on(ga.grade(2), label="bivector"),
        ],
        value=value,
    )
    kinds = [placement.annotation.label for placement in plan.placements]
    assert kinds == ["vector", "weight", "bivector"]


def test_hidden_duplicate_result_parts_contribute_no_value_anchors(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    value = (2 * e1 + e2).named("B")  # expression and value render identically
    plan = ga.resolve(_document(value), [ga.on(ga.term(e1), label="hidden")], value=value)
    assert plan.placements == ()
    assert plan.missing[0].label == "hidden"


def test_missing_policy_controls_empty_selections(algebra: Algebra) -> None:
    e1, _, _ = algebra.basis_vectors(expr=True)
    value = algebra.scalar(1.0).named("one")
    ignored = ga.resolve(_document(value), [ga.on(ga.term(e1), label="none")], value=value)
    assert ignored.placements == ()
    assert ignored.missing[0].label == "none"
    with pytest.raises(ga.MissingTargetError, match="matched no visible content"):
        ga.resolve(_document(value), [ga.on(ga.term(e1), label="none", missing="error")], value=value)


def test_blade_targets_reject_a_different_algebra() -> None:
    source = Algebra(2, expr=True)
    other = Algebra(2, 1, expr=True)
    target = ga.term(other.basis_vectors(expr=True)[0])
    value = (source.basis_vectors(expr=True)[0] + source.scalar(1)).named("v")
    with pytest.raises(ValueError, match="different algebra"):
        ga.resolve(_document(value), [ga.on(target, label="wrong")], value=value)


def test_variable_targets_select_symbol_occurrences_and_occurrence_all() -> None:
    algebra = Algebra(2, expr=True)
    x, y = Symbol("x"), Symbol("y")
    expression = Call("add", (x, y))
    value = algebra.multivector([0.0, 1.0, 1.0, 0.0], expr=expression).named("s")
    document = content_document(value, content="expr", target="latex")
    first = ga.resolve(document, [ga.on(ga.variable("x", occurrence=0), label="x")], value=value)
    assert first.placements
    all_y = ga.resolve(document, [ga.on(ga.variable("y", occurrence="all"), label="y")], value=value)
    assert len(all_y.placements) == 1
    absent = ga.resolve(document, [ga.on(ga.variable("x", occurrence=7), label="x")], value=value)
    assert absent.placements == ()


def test_plan_groups_rules_by_path(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    value = outer_product(e1, e2).named("A")
    plan = ga.resolve(
        _document(value),
        [ga.on(ga.whole(), label="one"), ga.on(ga.whole(), background="#fff")],
        value=value,
    )
    grouped = plan.by_path()
    assert set(grouped) == {()}
    assert [rule.label for rule in grouped[()]] == ["one", None]
    assert plan.placements[0].order == 0
