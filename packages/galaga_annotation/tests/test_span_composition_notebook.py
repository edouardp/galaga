"""Execute the independent-span composition lesson headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "span_composition.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    return runpy.run_path(str(NOTEBOOK))["app"].run()


def test_lesson_demonstrates_every_interval_relationship(lesson) -> None:
    _, definitions = lesson
    views = definitions["comparison_views"]
    assert set(views) == {"Equal", "Callout subset", "Highlight subset", "Disjoint", "Crossing"}
    for view in views.values():
        rendered = view.latex()
        assert rendered.count(r"\colorbox{#fff3cd}") == 1
        assert rendered.count(r"\mathrlap{\smash[t]{\textcolor{#7c3aed}{\overbrace") == 1


def test_lesson_combines_highlight_above_and_below(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["three_layer_view"].latex()
    assert rendered.count(r"\colorbox{#b8e6bf}") == 1
    assert r"\mathrlap{\smash[t]{\textcolor{#0099cc}{\overbracket{" in rendered
    assert r"^{\mathclap{\text{structure above}}}" in rendered
    assert r"\overgroup" not in rendered
    assert r"\mathrlap{\smash[b]{\textcolor{#7c3aed}{\underbrace" in rendered
    assert rendered.startswith(r"\vphantom{")


def test_lesson_keeps_a_wide_label_centred_without_moving_its_brace(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["wide_label_view"].latex()
    assert r"\phantom{e_{1} + e_{2}}" in rendered
    assert r"^{\mathclap{\text{a much wider explanatory annotation}}}" in rendered


def test_lesson_keeps_a_leading_minus_inside_the_selected_run(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["negative_view"].latex()
    assert r"\phantom{\mathord{-}\>e_{1} + 2 e_{2}}" in rendered
    assert "- -" not in rendered and "+ -" not in rendered


def test_lesson_control_can_select_a_nested_relationship() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={
            "relationship_choice": SimpleNamespace(value="callout is a subset"),
            "marker_choice": SimpleNamespace(value="overbracket"),
        }
    )
    rendered = definitions["interactive_view"].latex()
    assert r"\overbracket" in rendered
    assert r"\phantom{2 e_{2} - 3 e_{3}}" in rendered
