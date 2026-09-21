"""Execute the annotated spacetime-algebra lesson headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "sta_electromagnetism.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_sta_lesson_computes_every_claim_before_display(lesson) -> None:
    _, definitions = lesson
    assert definitions["generator_square_values"] == (1.0, 1.0, 1.0, -1.0, -1.0, -1.0)
    for name in (
        "generators_verified",
        "rotors_verified",
        "field_invariants_verified",
        "force_linearity_verified",
        "force_geometry_verified",
        "boosted_invariants_verified",
    ):
        assert definitions[name] is True, name

    assert definitions["lorentz_force"].almost_equal(definitions["electric_force"] + definitions["magnetic_force"])
    assert definitions["faraday_view"].plain.almost_equal(definitions["faraday_field"])
    assert definitions["force_view"].plain.almost_equal(definitions["lorentz_force"])


def test_sta_lesson_reuses_semantic_colours_and_annotations(lesson) -> None:
    outputs, definitions = lesson
    expected = {
        "generator_view": ("boost planes", "rotation planes", "#0072B2", "#D55E00"),
        "faraday_view": ("electric part E", "magnetic part I B", "#C43C39", "#2F6FB0"),
        "invariant_view": (r"\lVert E\rVert^2-\lVert B\rVert^2", r"2I(E\cdot B)"),
        "force_view": ("electric force", "magnetic force", "#C43C39", "#2F6FB0"),
    }
    for view_name, fragments in expected.items():
        rendered = definitions[view_name].latex()
        assert all(fragment in rendered for fragment in fragments), view_name
        assert r"\colorbox" in rendered

    boosted = definitions["boosted_field_view"].latex()
    assert "electric part E" in boosted and "magnetic part I B" in boosted
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    for label in (
        "boost generator",
        "rotation generator",
        "electric part E",
        "magnetic part I B",
        "electric force",
        "magnetic force",
    ):
        assert label in markup


def test_sta_lesson_uses_braces_instead_of_group_accents(lesson) -> None:
    _, definitions = lesson
    rendered = "\n".join(
        definitions[name].latex()
        for name in (
            "generator_view",
            "selected_generators_view",
            "faraday_view",
            "invariant_view",
            "force_view",
            "boosted_field_view",
        )
    )
    assert r"\overbrace" in rendered
    assert r"\underbrace" in rendered
    assert r"\overgroup" not in rendered
    assert r"\undergroup" not in rendered
