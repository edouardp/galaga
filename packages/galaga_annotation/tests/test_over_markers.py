"""Overline and bracket marker lowering contracts."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra


@pytest.fixture()
def algebra() -> Algebra:
    return Algebra(2)


def test_over_markers_validate_and_are_above_only() -> None:
    for marker in ("overline", "overbracket"):
        assert ga.AnnotationStyle(marker=marker).marker == marker
        assert ga.on(ga.whole(), marker=marker).side == "auto"
        with pytest.raises(ValueError, match="contradicts"):
            ga.on(ga.whole(), marker=marker, side="below")


def test_underbracket_validates_and_is_below_only() -> None:
    assert ga.AnnotationStyle(marker="underbracket").marker == "underbracket"
    assert ga.on(ga.whole(), marker="underbracket").side == "auto"
    with pytest.raises(ValueError, match="contradicts"):
        ga.on(ga.whole(), marker="underbracket", side="above")


def test_overline_lowers_as_an_accent(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    labelled = ga.annotate(e1 + e2, marker="overline", label="sum").latex()
    assert r"\overset{\text{sum}}{\overline{e_{1} + e_{2}}}" in labelled

    bare = ga.annotate(e1 + e2, marker="overline").latex()
    assert r"\overline{e_{1} + e_{2}}" in bare
    assert r"\overset" not in bare


def test_overbracket_lowers_with_limits(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    labelled = ga.annotate(e1 + e2, marker="overbracket", label="sum").latex()
    assert r"\overbracket{e_{1} + e_{2}}^{\text{sum}}" in labelled

    bare = ga.annotate(e1 + e2, marker="overbracket").latex()
    assert r"\overbracket{e_{1} + e_{2}}" in bare


def test_underbracket_lowers_with_limits(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    labelled = ga.annotate(e1 + e2, marker="underbracket", label="sum").latex()
    assert r"\underbracket{e_{1} + e_{2}}_{\text{sum}}" in labelled

    bare = ga.annotate(e1 + e2, marker="underbracket").latex()
    assert r"\underbracket{e_{1} + e_{2}}" in bare


def test_underbracket_overlay_uses_the_below_span_lane(algebra: Algebra) -> None:
    e1, e2 = algebra.basis_vectors()
    rendered = ga.annotator(
        ga.on(
            ga.terms(e1, e2),
            marker="underbracket",
            label="sum",
            join=True,
            overlay=True,
        )
    )(e1 + e2).latex()

    assert r"\mathrlap{\smash[b]{\underbracket{" in rendered
    assert r"}_{\mathclap{\text{sum}}}" in rendered
