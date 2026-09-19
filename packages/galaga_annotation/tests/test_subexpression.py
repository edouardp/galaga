"""Subexpression target resolution by provenance subtree."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra
from galaga.expression import Call
from galaga.rendering import content_document


@pytest.fixture()
def algebra() -> Algebra:
    return Algebra(3, expr=True)


@pytest.fixture()
def symbols(algebra: Algebra):
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    return (1 + e1 * e2).named("R"), (e1 + 2 * e2).named("v")


def _document(value, content="full"):
    return content_document(value, content=content, target="latex")


def test_subexpression_selector_extracts_and_validates(algebra: Algebra, symbols) -> None:
    R, _ = symbols
    reversed_R = ~R
    assert ga.SubexpressionTarget in ga.ANNOTATION_TARGET_TYPES
    assert ga.subexpression(reversed_R).expression == reversed_R.expr
    assert ga.subexpression(reversed_R.expr).expression == reversed_R.expr
    with pytest.raises(TypeError, match="Expr or a tracked value"):
        ga.subexpression("not an expression")
    with pytest.raises(ValueError, match="occurrence"):
        ga.subexpression(reversed_R.expr, occurrence=-1)
    assert hash(ga.on(ga.subexpression(reversed_R))) is not None


def test_subexpression_resolves_the_matching_subtree(symbols) -> None:
    R, v = symbols
    value = (R * v * ~R).named("w")
    plan = ga.resolve(_document(value), [ga.on(ga.subexpression(~R))], value=value)
    assert [placement.path for placement in plan.placements] == [("parts", 1, "factors", 2)]


def test_subexpression_occurrence_selects_among_duplicates(symbols) -> None:
    R, _ = symbols
    value = ((~R) * (~R)).named("w")
    document = _document(value)

    every = ga.resolve(document, [ga.on(ga.subexpression(~R))], value=value)
    assert [placement.path for placement in every.placements] == [
        ("parts", 1, "factors", 0),
        ("parts", 1, "factors", 1),
    ]
    first = ga.resolve(document, [ga.on(ga.subexpression(~R, occurrence=0))], value=value)
    assert [placement.path for placement in first.placements] == [("parts", 1, "factors", 0)]
    second = ga.resolve(document, [ga.on(ga.subexpression(~R, occurrence=1))], value=value)
    assert [placement.path for placement in second.placements] == [("parts", 1, "factors", 1)]
    absent = ga.resolve(document, [ga.on(ga.subexpression(~R, occurrence=5))], value=value)
    assert absent.placements == ()


def test_subexpression_matching_is_structural_not_numeric(algebra: Algebra) -> None:
    e1, _, _ = algebra.basis_vectors(expr=True)
    # e1 + e1 is not the same provenance tree as 2 * e1, even though eager
    # evaluation makes them numerically equal.
    value = (e1 + e1).named("p")
    plan = ga.resolve(_document(value), [ga.on(ga.subexpression(2 * e1))], value=value)
    assert plan.placements == ()
    assert plan.missing


def test_subexpression_distinguishes_operation_trees(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    value = (e1 * e2).named("P")
    assert ga.resolve(_document(value), [ga.on(ga.subexpression(e1 * e2))], value=value).placements
    assert ga.resolve(_document(value), [ga.on(ga.subexpression(e2 * e1))], value=value).placements == ()


def test_subexpression_requires_provenance(algebra: Algebra) -> None:
    e1, e2, _ = algebra.basis_vectors(expr=True)
    untracked = (e1 + e2).without_expr()
    with pytest.raises(ValueError, match="tracked value"):
        ga.resolve(_document(untracked, content="value"), [ga.on(ga.subexpression(e1 + e2))], value=untracked)


def test_subexpression_annotation_wraps_the_subtree(symbols) -> None:
    R, v = symbols
    value = (R * v * ~R).named("w")
    rendered = ga.annotate(
        value,
        ga.on(ga.subexpression(~R), background="#e8f5e9", label="reverse factor"),
    ).latex()
    assert r"\overset{\text{reverse factor}}{\colorbox{#e8f5e9}{$\widetilde{R}$}}" in rendered


def test_subexpression_accepts_a_bare_provenance_node(symbols) -> None:
    R, v = symbols
    value = (R * v * ~R).named("w")
    node = value.expr.operands[1]
    assert isinstance(node, Call)
    plan = ga.resolve(_document(value), [ga.on(ga.subexpression(node))], value=value)
    assert [placement.path for placement in plan.placements] == [("parts", 1, "factors", 2)]
