"""Immutable rule and style validation contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

import galaga_annotation as ga


def test_styles_validate_colors_dimensions_and_markers() -> None:
    assert ga.AnnotationStyle(color="royalblue", background="#e8f5e9", border="#fff").marker == "none"
    with pytest.raises(ValueError, match="colour"):
        ga.AnnotationStyle(color="red; }")
    with pytest.raises(ValueError, match="dimension"):
        ga.AnnotationStyle(clearance="4")
    with pytest.raises(ValueError, match="dimension"):
        ga.AnnotationStyle(clearance="-4px")
    with pytest.raises(ValueError, match="marker"):
        ga.AnnotationStyle(marker="sparkles")
    with pytest.raises(ValueError, match="emphasis"):
        ga.AnnotationStyle(emphasis="loud")


def test_cancellation_markers_are_inline_and_reject_external_overlay_mode() -> None:
    assert ga.AnnotationStyle(marker="cancel").marker == "cancel"
    assert ga.AnnotationStyle(marker="bcancel").marker == "bcancel"
    assert ga.AnnotationStyle(marker="xcancel").marker == "xcancel"
    with pytest.raises(ValueError, match="cancellation markers"):
        ga.on(ga.whole(), marker="cancel", overlay=True)


def test_directional_markers_reject_contradictory_sides() -> None:
    assert ga.on(ga.whole(), marker="underbrace").side == "auto"
    assert ga.on(ga.whole(), marker="underbrace", side="below").side == "below"
    assert ga.on(ga.whole(), marker="overbrace", side="above").side == "above"
    with pytest.raises(ValueError, match="contradicts"):
        ga.on(ga.whole(), marker="underbrace", side="above")
    with pytest.raises(ValueError, match="contradicts"):
        ga.on(ga.whole(), marker="overgroup", side="below")


def test_on_rejects_style_and_style_fields_together() -> None:
    with pytest.raises(ValueError, match="either style"):
        ga.on(ga.whole(), style=ga.AnnotationStyle(), color="red")


def test_rules_are_immutable_and_validate_their_fields() -> None:
    rule = ga.on(ga.whole(), label="result", role="value")
    with pytest.raises(FrozenInstanceError):
        rule.label = "changed"
    with pytest.raises(TypeError, match="target"):
        ga.on("not a target")
    with pytest.raises(TypeError, match="label"):
        ga.Annotation(target=ga.whole(), label=3)
    with pytest.raises(ValueError, match="side"):
        ga.Annotation(target=ga.whole(), side="sideways")
    with pytest.raises(ValueError, match="missing"):
        ga.Annotation(target=ga.whole(), missing="explode")


def test_rules_reject_style_combinations_that_cannot_render() -> None:
    with pytest.raises(ValueError, match="label_color"):
        ga.on(ga.whole(), label_color="red")
    with pytest.raises(ValueError, match="overlay"):
        ga.on(ga.whole(), overlay=True)
    with pytest.raises(ValueError, match="clearance"):
        ga.on(ga.whole(), clearance="4px")


def test_on_defaults_to_the_whole_expression() -> None:
    assert ga.on(label="x").target == ga.whole()
    assert ga.on((0,)).target == ga.ExpressionPath((0,))
