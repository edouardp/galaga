"""KaTeX lowering: wrappers, markers, escaping and label layout."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra
from galaga.rendering import content_document


@pytest.fixture()
def value():
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    return algebra, e1 + e2


def test_whole_value_labels_render_above_and_below(value) -> None:
    _, mv = value
    assert ga.annotate(mv, label="both").latex() == r"\overset{\text{both}}{e_{1} + e_{2}}"
    assert ga.annotate(mv, label="both", side="below").latex() == r"\underset{\text{both}}{e_{1} + e_{2}}"


def test_highlight_styles_lower_to_katex(value) -> None:
    _, mv = value
    assert ga.annotate(mv, color="royalblue").latex() == r"\textcolor{royalblue}{e_{1} + e_{2}}"
    assert ga.annotate(mv, background="#fff3cd").latex() == r"\colorbox{#fff3cd}{$e_{1} + e_{2}$}"
    assert ga.annotate(mv, border="seagreen").latex() == r"\fcolorbox{seagreen}{transparent}{$e_{1} + e_{2}$}"
    assert (
        ga.annotate(mv, border="seagreen", background="#e8f5e9").latex()
        == r"\fcolorbox{seagreen}{#e8f5e9}{$e_{1} + e_{2}$}"
    )
    assert ga.annotate(mv, emphasis="bold").latex() == r"\mathbf{e_{1} + e_{2}}"
    assert ga.annotate(mv, emphasis="italic").latex() == r"\mathit{e_{1} + e_{2}}"


def test_marker_lowering(value) -> None:
    _, mv = value
    assert ga.annotate(mv, label="both", marker="brace").latex() == r"\overbrace{e_{1} + e_{2}}^{\text{both}}"
    assert ga.annotate(mv, label="both", marker="brace", side="below").latex() == (
        r"\underbrace{e_{1} + e_{2}}_{\text{both}}"
    )
    assert ga.annotate(mv, label="both", marker="underbrace").latex() == r"\underbrace{e_{1} + e_{2}}_{\text{both}}"
    assert ga.annotate(mv, label="both", marker="overbrace").latex() == r"\overbrace{e_{1} + e_{2}}^{\text{both}}"
    assert ga.annotate(mv, label="both", marker="undergroup").latex() == (
        r"\underset{\text{both}}{\undergroup{e_{1} + e_{2}}}"
    )
    assert ga.annotate(mv, label="both", marker="overgroup").latex() == (
        r"\overset{\text{both}}{\overgroup{e_{1} + e_{2}}}"
    )
    assert ga.annotate(mv, marker="undergroup").latex() == r"\undergroup{e_{1} + e_{2}}"
    assert ga.annotate(mv, marker="overgroup").latex() == r"\overgroup{e_{1} + e_{2}}"
    assert ga.annotate(mv, label="both", marker="box").latex() == r"\overset{\text{both}}{\boxed{e_{1} + e_{2}}}"
    assert ga.annotate(mv, label="both", marker="box", side="below").latex() == (
        r"\underset{\text{both}}{\boxed{e_{1} + e_{2}}}"
    )
    assert ga.annotate(mv, marker="underline").latex() == r"\underline{e_{1} + e_{2}}"
    assert ga.annotate(mv, marker="underline", label="both").latex() == (
        r"\underset{\text{both}}{\underline{e_{1} + e_{2}}}"
    )
    assert ga.annotate(mv, marker="arrow").latex() == r"\overset{\downarrow}{e_{1} + e_{2}}"
    assert ga.annotate(mv, label="both", marker="arrow").latex() == (
        r"\overset{\substack{\text{both} \\ \downarrow}}{e_{1} + e_{2}}"
    )
    assert ga.annotate(mv, label="both", marker="arrow", side="below").latex() == (
        r"\underset{\substack{\uparrow \\ \text{both}}}{e_{1} + e_{2}}"
    )
    assert ga.annotate(mv, label="both", marker="rule").latex() == (
        r"\overset{\substack{\text{both} \\ \rule[0.2em]{0.4pt}{1em}}}{e_{1} + e_{2}}"
    )


@pytest.mark.parametrize("marker", ["cancel", "bcancel", "xcancel"])
def test_cancellation_markers_wrap_visible_content(marker, value) -> None:
    _, mv = value
    assert ga.annotate(mv, marker=marker).latex() == rf"\{marker}{{e_{{1}} + e_{{2}}}}"


def test_cancellation_preserves_content_colour_and_places_a_label_outside(value) -> None:
    _, mv = value
    rendered = ga.annotate(mv, marker="cancel", color="lightgrey", label="vanishes").latex()
    assert rendered == r"\overset{\text{vanishes}}{\cancel{\textcolor{lightgrey}{e_{1} + e_{2}}}}"


def test_clearance_adds_an_invisible_strut(value) -> None:
    _, mv = value
    assert ga.annotate(mv, label="both", clearance="4px").latex() == (
        r"\overset{\substack{\text{both} \\ \rule{0pt}{4px}}}{e_{1} + e_{2}}"
    )


def test_multiline_labels_become_a_substack(value) -> None:
    _, mv = value
    assert ga.annotate(mv, label="first\nsecond").latex() == (
        r"\overset{\substack{\text{first} \\ \text{second}}}{e_{1} + e_{2}}"
    )


def test_labels_are_escaped_for_latex(value) -> None:
    _, mv = value
    assert ga.annotate(mv, label="x_1 & y").latex() == r"\overset{\text{x\_1 \& y}}{e_{1} + e_{2}}"


def test_combined_styles_nest_labels_outside_boxes(value) -> None:
    _, mv = value
    rendered = ga.annotate(mv, label="both", background="#e8f5e9", color="royalblue").latex()
    assert rendered == r"\overset{\text{both}}{\colorbox{#e8f5e9}{$\textcolor{royalblue}{e_{1} + e_{2}}$}}"


def test_marker_colour_applies_to_chrome_and_overlay_reserves_bounds(value) -> None:
    _, mv = value
    over = ga.annotate(mv, label="both", marker="overgroup", color="#0099cc", overlay=True)
    over_latex = over.latex()
    assert over_latex.startswith(
        r"\vphantom{\textcolor{#0099cc}{\overset{\mathclap{\text{both}}}{\overgroup{"
        r"\textcolor{black}{\phantom{"
    )
    assert r"\mathrlap{\smash[t]{\textcolor{#0099cc}{\overset{\mathclap{\text{both}}}{\overgroup{" in over_latex
    assert over_latex.endswith(r"e_{1} + e_{2}")
    under = ga.annotate(mv, label="both", marker="undergroup", color="#0099cc", overlay=True)
    under_latex = under.latex()
    assert under_latex.startswith(
        r"\vphantom{\textcolor{#0099cc}{\underset{\mathclap{\text{both}}}{\undergroup{"
        r"\textcolor{black}{\phantom{"
    )
    assert r"\mathrlap{\smash[b]{\textcolor{#0099cc}{\underset{\mathclap{\text{both}}}{\undergroup{" in under_latex
    assert under_latex.endswith(r"e_{1} + e_{2}")
    plain = ga.annotate(mv, label="both", marker="overgroup", color="#0099cc")
    assert plain.latex() == r"\textcolor{#0099cc}{\overset{\text{both}}{\overgroup{\textcolor{black}{e_{1} + e_{2}}}}}"


def test_overlay_clearance_lifts_the_marker_not_the_terms(value) -> None:
    _, mv = value
    lifted = ga.annotate(mv, label="both", marker="overgroup", color="#0099cc", overlay=True, clearance="4px")
    lifted_latex = lifted.latex()
    assert lifted_latex.count(r"\vphantom{\raisebox{4px}{\rule{0pt}{1em}}}") == 2
    assert r"\mathrlap{\smash[t]{" in lifted_latex
    assert lifted_latex.endswith(r"e_{1} + e_{2}")
    lowered = ga.annotate(mv, label="both", marker="undergroup", color="#0099cc", overlay=True, clearance="4px")
    assert r"\vphantom{\raisebox{-4px}{\rule{0pt}{1em}}}" in lowered.latex()


def test_vertical_clearance_does_not_inflate_estimated_label_width(value) -> None:
    _, mv = value
    ordinary = ga.annotate(mv, label="both", marker="overgroup", overlay=True).katex()
    lifted = ga.annotate(mv, label="both", marker="overgroup", overlay=True, clearance="4px").katex()
    assert lifted.labels[0].estimated_width == ordinary.labels[0].estimated_width


def test_label_color_colours_only_the_label(value) -> None:
    _, mv = value
    coloured = ga.annotate(mv, label="both", label_color="#2f7d4f")
    assert coloured.latex() == r"\overset{\textcolor{#2f7d4f}{\text{both}}}{e_{1} + e_{2}}"


def test_labels_render_as_text_and_accept_raw_equation_latex(value) -> None:
    _, mv = value
    # Plain labels keep their spaces and render upright.
    text_label = ga.annotate(mv, label="carrier line")
    assert text_label.latex() == r"\overset{\text{carrier line}}{e_{1} + e_{2}}"
    # Raw labels carry arbitrary equation LaTeX, including stacked lines.
    raw = ga.on(
        ga.whole(),
        label_latex=r"\substack{\text{carrier line} \\ e_{1} \wedge e_{2}}",
    )
    result = ga.annotate(mv, raw).katex()
    assert result.text == r"\overset{\substack{\text{carrier line} \\ e_{1} \wedge e_{2}}}{e_{1} + e_{2}}"
    assert len(result.labels) == 1
    assert result.labels[0].estimated_width > 0
    with pytest.raises(ValueError, match="label_latex"):
        ga.Annotation(target=ga.whole(), label="a", label_latex="b")


def test_overlay_flag_is_validated() -> None:
    with pytest.raises(TypeError, match="overlay"):
        ga.AnnotationStyle(overlay="yes")


def test_adjacent_labels_alternate_sides_when_they_would_collide() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    mv = e1 + e2
    view = ga.annotator(
        ga.on(ga.term(e1), label="first"),
        ga.on(ga.term(e2), label="second"),
    )(mv)
    result = view.katex()
    assert [label.side for label in result.labels] == ["above", "below"]
    assert [label.collided for label in result.labels] == [False, False]
    assert r"\overset{\mathclap{\text{first}}}{\phantom{e_{1}}}" in result.text
    assert r"\underset{\mathclap{\text{second}}}{\phantom{e_{2}}}" in result.text


def test_raw_labels_and_generic_braces_follow_solved_layout() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    view = ga.annotator(
        ga.on(ga.term(e1), label_latex=r"\alpha + \beta"),
        ga.on(ga.term(e2), label="second", marker="brace"),
    )(e1 + e2)
    result = view.katex()
    assert [label.side for label in result.labels] == ["above", "below"]
    assert r"\overset{\mathclap{\alpha + \beta}}{\phantom{e_{1}}}" in result.text
    assert r"\underbrace{\textcolor{black}{\phantom{e_{2}}}}_{\mathclap{\text{second}}}" in result.text


def test_no_placements_returns_the_plain_latex(value) -> None:
    _, mv = value
    result = ga.annotate(mv).katex()
    assert result.text == mv.display(target="latex")
    assert result.labels == ()
    assert result.missing == ()


def test_empty_selections_are_reported_and_can_error(value) -> None:
    _, mv = value
    document = content_document(mv, content="value", target="latex")
    ignored = ga.render_katex(document, [ga.on(ga.grade(3), label="none")], value=mv)
    assert ignored.missing[0].label == "none"
    with pytest.raises(ga.MissingTargetError):
        ga.render_katex(document, [ga.on(ga.grade(3), label="none", missing="error")], value=mv)
