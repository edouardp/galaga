"""Joined content spans and independent external-callout layers."""

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
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), background="#eee", join=True)).latex()
    assert rendered == r"\colorbox{#eee}{$e_{1} + e_{2}$} + e_{3}"


def test_joined_terms_can_be_cancelled_as_one_content_span() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(
        value,
        ga.on(ga.terms(e1, e2), marker="cancel", color="lightgrey", join=True),
    ).latex()
    assert rendered == r"\cancel{\textcolor{lightgrey}{e_{1} + e_{2}}} + e_{3}"


def test_joined_span_shows_one_label_for_the_whole_run() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), background="#eee", label="pair", join=True)).latex()
    assert rendered == (
        r"\vphantom{\overset{\mathclap{\text{pair}}}{\phantom{e_{1} + e_{2}}}}"
        r"\colorbox{#eee}{$\mathrlap{\smash[t]{\overset{\mathclap{\text{pair}}}{"
        r"\phantom{e_{1} + e_{2}}}}}"
        r"e_{1} + e_{2}$} + e_{3}"
    )


def test_unjoined_labels_stay_with_each_term() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), label="term")).latex()
    assert r"\mathrlap{\smash[t]{\overset{\mathclap{\text{term}}}{\phantom{e_{1}}}}}e_{1}" in rendered
    assert r"\mathrlap{\smash[b]{\underset{\mathclap{\text{term}}}{\phantom{e_{2}}}}}e_{2}" in rendered
    # Each label occurs in the visible overlay and its invisible bounds copy.
    assert rendered.count("term") == 4


def test_joined_span_excludes_a_leading_sign_from_the_highlight_by_default() -> None:
    algebra = Algebra(3)
    e1, e2 = algebra.basis_vectors()[:2]
    value = _value(algebra, [0.0, -1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e2), background="#eee", join=True)).latex()
    assert rendered == r"-\colorbox{#eee}{$e_{1} + e_{2}$}"


def test_joined_span_can_include_a_visible_leading_sign() -> None:
    algebra = Algebra(3)
    e1, e2 = algebra.basis_vectors()[:2]
    value = _value(algebra, [0.0, -1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(
        value,
        ga.on(ga.terms(e1, e2, include_sign=True), background="#eee", join=True),
    ).latex()
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


def test_matching_sign_fill_fuses_with_the_joined_span_that_follows_it() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    rendered = ga.annotator(
        ga.on(ga.terms(e2, e3), background="#eee", color="crimson", join=True),
        ga.on(ga.sign(e2), background="#eee"),
    )(e1 - e2 - e3).latex()
    assert rendered == r"e_{1}  \colorbox{#eee}{$\textcolor{crimson}{-e_{2} - e_{3}}$}"


def test_matching_sign_fill_extends_the_split_callout_to_the_same_span() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    rendered = ga.annotator(
        ga.on(
            ga.terms(e2, e3),
            background="#eee",
            label="signed run",
            marker="underbrace",
            join=True,
        ),
        ga.on(ga.sign(e2), background="#eee"),
    )(e1 - e2 - e3).latex()

    assert rendered.count(r"\colorbox{#eee}") == 1
    assert r"\phantom{\mathord{-}e_{2} - e_{3}}" in rendered
    assert r"\phantom{e_{2} - e_{3}}" not in rendered


def test_negative_nonleading_callout_excludes_the_sign_by_default() -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    rendered = ga.annotate(
        e1 - e2,
        ga.on(
            ga.term(e2),
            background="#eee",
            label="negated",
            marker="underbrace",
        ),
    ).latex()

    assert r"\phantom{e_{2}}" in rendered
    assert r"\phantom{\mathord{-}\>e_{2}}" not in rendered
    assert r"- \colorbox{#eee}{$\mathrlap{\smash[b]{\underbrace" in rendered


@pytest.mark.parametrize(("value_sign", "glyph"), [(-1, "-"), (1, "+")])
def test_nonleading_term_can_include_its_visible_sign(
    value_sign: int,
    glyph: str,
) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    rendered = ga.annotate(
        e1 + value_sign * e2,
        ga.on(
            ga.term(e2, include_sign=True),
            background="#eee",
            label="signed term",
            marker="underbrace",
        ),
    ).latex()

    assert rf"\phantom{{\mathord{{{glyph}}}e_{{2}}}}" in rendered
    assert rf"\mathord{{{glyph}}}}}e_{{2}}$}}" in rendered


def test_leading_term_include_sign_respects_suppressed_plus() -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    positive = ga.annotate(
        e1 + e2,
        ga.on(
            ga.term(e1, include_sign=True),
            background="#eee",
            label="first",
            marker="underbrace",
        ),
    ).latex()
    negative = ga.annotate(
        -e1 + e2,
        ga.on(
            ga.term(e1, include_sign=True),
            background="#eee",
            label="first",
            marker="underbrace",
        ),
    ).latex()

    assert positive.startswith(r"\vphantom{\underbrace{\textcolor{black}{\phantom{e_{1}}}")
    assert r"\colorbox{#eee}{$\mathrlap" in positive
    assert r"\mathord{+}" not in positive
    assert r"\phantom{\mathord{-}e_{1}}" in negative
    assert r"\mathord{-}}e_{1}$}" in negative


def test_singleton_term_can_include_or_exclude_its_negative_sign() -> None:
    algebra = Algebra(1)
    (e1,) = algebra.basis_vectors()
    value = -2 * e1
    unsigned = ga.annotate(
        value,
        ga.on(ga.term(e1), background="#eee", label="term", marker="rule"),
    ).latex()
    signed = ga.annotate(
        value,
        ga.on(
            ga.term(e1, include_sign=True),
            background="#eee",
            label="term",
            marker="rule",
        ),
    ).latex()

    assert r"\phantom{2 e_{1}}" in unsigned
    assert r"\phantom{\mathord{-}\>2 e_{1}}" not in unsigned
    assert r"-\colorbox{#eee}{$\mathord{\mathrlap" in unsigned
    assert r"\phantom{\mathord{-}2 e_{1}}" in signed
    assert signed.endswith(r"\mathord{-}}2 e_{1}$}")


def test_nested_joined_layers_keep_the_wide_span_continuous() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2, e3, e4), background="#b8e6bf", join=True),
        ga.on(ga.terms(e1, e2), label="inner", marker="overgroup", join=True),
    )(value).latex()
    assert rendered == (
        r"\vphantom{\overset{\mathclap{\text{inner}}}{\overgroup{"
        r"\textcolor{black}{\phantom{e_{1} + e_{2}}}}}}"
        r"\colorbox{#b8e6bf}{$\mathrlap{\smash[t]{\overset{\mathclap{\text{inner}}}{\overgroup{"
        r"\textcolor{black}{\phantom{e_{1} + e_{2}}}}}}}e_{1} + e_{2} + e_{3} + e_{4}$}"
    )


def test_non_contiguous_joined_terms_split_into_their_own_runs() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    rendered = ga.annotate(value, ga.on(ga.terms(e1, e3), background="#eee", join=True)).latex()
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
    assert rendered.count(r"\colorbox{#b8e6bf}") == 1
    assert rendered.count(r"\text{leading}") == 2
    assert rendered.count(r"\text{inner}") == 2
    assert rendered.count(r"\text{middle}") == 2
    assert r"\phantom{e_{1} + e_{2}}" in rendered
    assert r"\phantom{\mathord{-}\>e_{1} + e_{2}}" not in rendered


def test_crossing_highlight_and_callout_spans_use_an_independent_overlay() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2, e3), background="#eee", join=True),
        ga.on(ga.terms(e3, e4), label="crossing", marker="overbrace", join=True),
    )(value).latex()
    assert rendered == (
        r"\vphantom{\overbrace{\textcolor{black}{\phantom{e_{3} + e_{4}}}}^"
        r"{\mathclap{\text{crossing}}}}"
        r"\colorbox{#eee}{$e_{1} + e_{2} + \mathrlap{\smash[t]{\overbrace{\textcolor{black}{"
        r"\phantom{e_{3} + e_{4}}}}^{\mathclap{\text{crossing}}}}}e_{3}$} + e_{4}"
    )


def test_wide_callout_label_does_not_change_the_measured_span_width() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#eee", join=True),
        ga.on(
            ga.terms(e1, e2),
            label="a much wider explanatory annotation",
            marker="overbrace",
            join=True,
        ),
    )(e1 + e2 + e3).latex()
    assert r"\phantom{e_{1} + e_{2}}" in rendered
    assert r"^{\mathclap{\text{a much wider explanatory annotation}}}" in rendered
    assert r"\phantom{\text{a much wider explanatory annotation}}" not in rendered


def test_crossing_joined_body_styles_still_require_an_overlap_policy() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    with pytest.raises(ga.SpanLayoutError, match="nest"):
        ga.annotator(
            ga.on(ga.terms(e1, e2), background="#eee", join=True),
            ga.on(ga.terms(e2, e3), background="#ddd", join=True),
        )(value).latex()


def test_highlight_can_have_independent_over_and_under_spans() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2, e3), background="#eee", join=True),
        ga.on(ga.terms(e2, e3, e4), label="above", marker="overbrace", join=True),
        ga.on(ga.terms(e1, e2), label="below", marker="underbrace", join=True),
    )(value).latex()
    assert r"\colorbox{#eee}" in rendered
    assert r"\mathrlap{\smash[t]{\overbrace" in rendered
    assert r"\mathrlap{\smash[b]{\underbrace" in rendered


@pytest.mark.parametrize(
    ("highlight_names", "callout_names"),
    (
        (("e1", "e2", "e3"), ("e1", "e2", "e3")),  # equal
        (("e1", "e2", "e3", "e4"), ("e2", "e3")),  # callout subset
        (("e2", "e3"), ("e1", "e2", "e3", "e4")),  # highlight subset
        (("e1", "e2"), ("e3", "e4")),  # disjoint
        (("e1", "e2", "e3"), ("e3", "e4")),  # crossing
    ),
)
def test_highlight_and_callout_share_one_interval_model(highlight_names, callout_names) -> None:
    algebra = Algebra(4)
    blades = dict(zip(("e1", "e2", "e3", "e4"), algebra.basis_vectors()))
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    rendered = ga.annotator(
        ga.on(ga.terms(*(blades[name] for name in highlight_names)), background="#eee", join=True),
        ga.on(
            ga.terms(*(blades[name] for name in callout_names)),
            label="callout",
            marker="overbrace",
            join=True,
        ),
    )(value).latex()
    assert rendered.count(r"\colorbox{#eee}") == 1
    assert rendered.count(r"\mathrlap{\smash[t]{\overbrace") == 1
    assert rendered.count(r"\text{callout}") == 2


def test_overlapping_callouts_on_one_side_require_multiple_lane_support() -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = _value(algebra, [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7)
    with pytest.raises(ga.SpanLayoutError, match="above channel"):
        ga.annotator(
            ga.on(ga.terms(e1, e2, e3), label="first", marker="overbrace", join=True),
            ga.on(ga.terms(e2, e3, e4), label="second", marker="overgroup", join=True),
        )(value).latex()
