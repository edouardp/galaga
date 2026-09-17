"""Joined term spans: opt-in continuous highlights and nested layers."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra


def _value(algebra: Algebra, coefficients: list[float]):
    return algebra.multivector(coefficients, expr=False)


def test_join_defaults_to_separate_term_placements() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), background="#eee")).latex()
    assert rendered == r"\colorbox{#eee}{$e_{1}$} + \colorbox{#eee}{$e_{2}$} + e_{3}"


def test_join_merges_adjacent_terms_into_one_continuous_span() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(
        value, ga.on(ga.terms(e1, e2), background="#eee", join=True)
    ).latex()
    assert rendered == r"\colorbox{#eee}{$e_{1} + e_{2}$} + e_{3}"


def test_joined_span_shows_one_label_for_the_whole_run() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(
        value, ga.on(ga.terms(e1, e2), background="#eee", label="pair", join=True)
    ).latex()
    assert rendered == r"\overset{\text{pair}}{\colorbox{#eee}{$e_{1} + e_{2}$}} + e_{3}"


def test_unjoined_labels_stay_with_each_term() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), label="term")).latex()
    assert r"\overset{\text{term}}{e_{1}}" in rendered
    assert r"\underset{\text{term}}{e_{2}}" in rendered
    assert rendered.count("term") == 2


def test_joined_span_keeps_a_leading_sign_inside_the_highlight() -> None:
    algebra = Algebra(3)
    e1, e2 = algebra.basis_vectors()[:2]
    value = _value(algebra, [0.0, -1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), background="#eee", join=True)).latex()
    assert rendered == r"\colorbox{#eee}{$-e_{1} + e_{2}$}"


def test_separator_between_joined_spans_stays_unhighlighted() -> None:
    algebra = Algebra(3)
    e1, e2 = algebra.basis_vectors()[:2]
    value = _value(algebra, [0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rendered = ga.annotator(
        ga.on(ga.term(e1), background="#b8e6bf", join=True),
        ga.on(ga.term(e2), background="#d8c4ee", join=True),
    )(value).latex()
    assert rendered == r"\colorbox{#b8e6bf}{$e_{1}$} - \colorbox{#d8c4ee}{$e_{2}$}"


def test_nested_joined_layers_keep_the_wide_span_continuous() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2, e3, e4), background="#b8e6bf", join=True),
        ga.on(ga.terms(e1, e2), label="inner", marker="overgroup", join=True),
    )(value).latex()
    assert rendered == (
        r"\colorbox{#b8e6bf}{$\overset{\text{inner}}{\overgroup{e_{1} + e_{2}}} + e_{3} + e_{4}$}"
    )


def test_non_contiguous_joined_terms_split_into_their_own_runs() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(
        value, ga.on(ga.terms(e1, e3), background="#eee", join=True)
    ).latex()
    assert rendered == r"\colorbox{#eee}{$e_{1}$} + e_{2} + \colorbox{#eee}{$e_{3}$}"


def test_join_flag_is_validated_and_preserved_by_the_fluent_api() -> None:
    with pytest.raises(TypeError, match="join"):
        ga.Annotation(target=ga.whole(), join="yes")
    rule = ga.annotator().mark(ga.grade(1), background="#eee", join=True).rules[0]
    assert rule.join is True


def test_nested_layers_do_not_duplicate_leading_signs() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    # -e1 + e2 - e3 + e4
    value = _value(algebra, [0.0, -1.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2, e3, e4), background="#b8e6bf", join=True),
        ga.on(ga.terms(e1, e2), label="inner", marker="overgroup", join=True),
        ga.on(ga.term(e1), label="leading", side="below"),
        ga.on(ga.term(e2), label="middle", marker="undergroup"),
    )(value).latex()
    assert "- -" not in rendered
    assert "+ -" not in rendered
    assert rendered == (
        r"\colorbox{#b8e6bf}{$\overset{\text{inner}}{\overgroup{\underset{\text{leading}}{-e_{1}} + "
        r"\underset{\text{middle}}{\undergroup{e_{2}}}}} - e_{3} + e_{4}$}"
    )


def test_crossing_joined_spans_are_rejected() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    with pytest.raises(ga.SpanLayoutError, match="nest"):
        ga.annotator(
            ga.on(ga.terms(e1, e2), background="#eee", join=True),
            ga.on(ga.terms(e2, e3), background="#ddd", join=True),
        )(value).latex()
