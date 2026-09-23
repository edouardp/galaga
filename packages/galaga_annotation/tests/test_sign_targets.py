"""Sign-only target resolution and lowering contracts."""

from __future__ import annotations

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra
from galaga.rendering import content_document


@pytest.fixture()
def algebra() -> Algebra:
    return Algebra(2)


@pytest.fixture()
def value(algebra: Algebra):
    e1, e2 = algebra.basis_vectors()
    return (0.5 + 2 * e1 - 3 * (e1 ^ e2)).named("A")


def _document(value, **kwargs):
    return content_document(value, content="full", target="latex", **kwargs)


def test_sign_selectors_construct_targets_and_validate(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    assert ga.SignTarget in ga.ANNOTATION_TARGET_TYPES
    assert ga.sign(e1) == ga.SignTarget((1,), algebra)
    assert ga.signs(e1, e2).masks == (1, 2)
    with pytest.raises(ValueError, match="sign target"):
        ga.SignTarget(())
    other = Algebra(2)
    with pytest.raises(ValueError, match="share one algebra"):
        ga.signs(e1, other.basis_vectors()[0])


def test_sign_target_resolves_to_the_sum_slot(algebra: Algebra, value) -> None:
    e1, e2 = algebra.basis_vectors()
    document = _document(value)
    plan = ga.resolve(document, [ga.on(ga.sign(e1)), ga.on(ga.sign(e1 ^ e2))], value=value)
    assert [placement.path for placement in plan.placements] == [
        ("parts", 1, "terms", 1, "sign"),
        ("parts", 1, "terms", 2, "sign"),
    ]


def test_implicit_leading_plus_and_singleton_follow_the_slot_policy(algebra: Algebra) -> None:
    e1, _ = algebra.basis_vectors()
    # A positive leading scalar has no visible sign.
    positive_lead = (0.5 + 2 * e1).named("A")
    plan = ga.resolve(_document(positive_lead), [ga.on(ga.sign(algebra.blade(0)))], value=positive_lead)
    assert plan.placements == ()
    assert plan.missing[0].target == ga.sign(algebra.blade(0))
    with pytest.raises(ga.MissingTargetError):
        ga.annotate(positive_lead, ga.on(ga.sign(algebra.blade(0)), missing="error")).latex()

    # A singleton negative term retains a semantic sign slot even though its
    # ordinary rendering does not need a surrounding sum.
    singleton = (-2 * e1).named("B")
    single_plan = ga.resolve(_document(singleton), [ga.on(ga.sign(e1))], value=singleton)
    assert [placement.path for placement in single_plan.placements] == [("parts", 1, "terms", 0, "sign")]


def test_sign_decoration_replaces_only_the_glyph(algebra: Algebra, value) -> None:
    e1, e2 = algebra.basis_vectors()
    plus = ga.annotate(value, ga.on(ga.sign(e1), background="#fff3cd")).latex()
    assert r"\colorbox{#fff3cd}{$+$}" in plus
    assert r"\colorbox{#fff3cd}{$-$}" not in plus

    minus = ga.annotate(value, ga.on(ga.sign(e1 ^ e2), color="crimson")).latex()
    assert r"\textcolor{crimson}{-}" in minus
    assert r"\textcolor{crimson}{+}" not in minus

    singleton = ga.annotate(-2 * e1, ga.on(ga.sign(e1), background="#fff3cd")).latex()
    assert singleton == r"\colorbox{#fff3cd}{$-$}2 e_{1}"


def test_sign_label_anchors_on_the_glyph(algebra: Algebra, value) -> None:
    e1, e2 = algebra.basis_vectors()
    text = ga.annotate(
        value,
        ga.on(ga.sign(e1 ^ e2), background="#fff3cd", label="flipped", label_color="#8a6d1a"),
    ).latex()
    assert r"\overset{\textcolor{#8a6d1a}{\text{flipped}}}{\colorbox{#fff3cd}{$-$}}" in text


def test_sign_survives_a_joined_term_span(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    # -3 e12 + 4 e12 collapse to +1 e12, so the visible e12 sign is +.
    target = (0.5 + 2 * e1 - 3 * (e1 ^ e2) + 4 * (e1 ^ e2)).named("A")
    text = ga.annotator(
        ga.on(ga.terms(e1, e1 ^ e2), background="#eeeeee", join=True),
        ga.on(ga.sign(e1 ^ e2), color="crimson"),
    )(target).latex()
    assert r"\colorbox{#eeeeee}{$2 e_{1} \textcolor{crimson}{+} e_{12}$}" in text


def test_sign_annotations_are_numerically_transparent(algebra: Algebra, value) -> None:
    e1, _ = algebra.basis_vectors()
    before = value.data.copy()
    view = ga.annotate(value, ga.on(ga.sign(e1), background="#fff3cd"))
    view.latex()
    np.testing.assert_array_equal(value.data, before)
    assert view.plain is value
