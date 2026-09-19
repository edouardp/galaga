"""Content-part target resolution and lowering contracts."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra, geometric_product
from galaga.rendering import content_document


@pytest.fixture()
def value():
    algebra = Algebra(2, expr=True)
    e1, e2 = algebra.basis_vectors(expr=True)
    return geometric_product(e1 + e2, e1).named("A")


def _document(value, content="full"):
    return content_document(value, content=content, target="latex")


def test_content_selector_constructs_targets_and_validates() -> None:
    assert ga.ContentTarget in ga.ANNOTATION_TARGET_TYPES
    assert ga.content("name") == ga.ContentTarget("name")
    assert ga.content("expr") == ga.ContentTarget("expr")
    assert ga.content("value") == ga.ContentTarget("value")
    with pytest.raises(ValueError, match="content target kind"):
        ga.ContentTarget("relation")
    with pytest.raises(ValueError, match="content target kind"):
        ga.content("full")


def test_content_targets_resolve_to_the_displayed_parts(value) -> None:
    plan = ga.resolve(
        _document(value),
        [ga.on(ga.content("name")), ga.on(ga.content("expr")), ga.on(ga.content("value"))],
        value=value,
    )
    assert [placement.path for placement in plan.placements] == [
        ("parts", 0),
        ("parts", 1),
        ("parts", 2),
    ]


def test_content_targets_follow_the_active_content_setting(value) -> None:
    value_only = ga.resolve(
        _document(value, content="value"),
        [ga.on(ga.content("name")), ga.on(ga.content("value"))],
        value=value,
    )
    assert [placement.path for placement in value_only.placements] == [()]
    assert [rule.target for rule in value_only.missing] == [ga.content("name")]

    with pytest.raises(ga.MissingTargetError):
        ga.annotate(value, ga.on(ga.content("name"), missing="error")).latex(content="value")


def test_content_part_annotations_wrap_the_whole_part(value) -> None:
    view = ga.annotate(
        value,
        ga.on(ga.content("name"), background="#e8f5e9"),
        ga.on(ga.content("expr"), background="#fff3cd"),
        ga.on(ga.content("value"), color="royalblue"),
    )
    rendered = view.latex(content="full")
    assert r"\colorbox{#e8f5e9}{$A$}" in rendered
    assert r"\colorbox{#fff3cd}{$\left(e_{1} + e_{2}\right) e_{1}$}" in rendered
    assert r"\textcolor{royalblue}{1 - e_{12}}" in rendered


def test_content_labels_describe_the_relation_between_parts(value) -> None:
    rendered = ga.annotate(
        value,
        ga.on(ga.content("expr"), label="computed as"),
        ga.on(ga.content("value"), label="evaluated result"),
    ).latex(content="full")
    assert r"\text{computed as}" in rendered
    assert r"\text{evaluated result}" in rendered
