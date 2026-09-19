"""Execute the interactive cocarrier-marker notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "cga_marker_styles.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_marker_notebook_defaults_to_overgroup(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["view"].latex()
    assert rendered.count(r"\overgroup") == 4
    for marker in ("overbrace", "overline", "overbracket"):
        assert "\\" + marker not in rendered


def test_marker_notebook_control_changes_the_style(lesson) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"over_marker": SimpleNamespace(value="overbracket")}
    )
    rendered = definitions["view"].latex()
    assert rendered.count(r"\overbracket") == 4
    assert r"\overgroup" not in rendered


def test_marker_notebook_compares_every_style(lesson) -> None:
    _, definitions = lesson
    comparison = definitions["comparison"]
    for marker in ("overgroup", "overbrace", "overline", "overbracket"):
        assert "\\" + marker in comparison[marker].latex()


def test_marker_notebook_explains_component_versus_incidence(lesson) -> None:
    outputs, definitions = lesson
    components = definitions["component_view"].latex()
    assert all(label in components for label in ("plane part", "center part", "flat part", "flat weight"))
    assert "carrier plane" not in components

    incidence = definitions["incidence_view"].latex()
    assert all(
        label in incidence for label in ("carrier plane", "cocarrier direction", "flat line", "cocarrier moment")
    )

    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "Component versus incidence" in markup


def test_marker_notebook_exposes_the_standard_objects(lesson) -> None:
    _, definitions = lesson
    assert set(definitions["objects"]) == {
        "round point",
        "flat point",
        "dipole",
        "line",
        "circle",
        "plane",
        "sphere",
    }


@pytest.mark.parametrize(
    "name",
    ("round point", "flat point", "dipole", "line", "circle", "plane", "sphere"),
)
def test_marker_notebook_highlights_every_object(name: str) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(defs={"object_choice": SimpleNamespace(value=name)})
    rendered = definitions["view"].latex(content="value")
    assert rendered
    assert r"\colorbox" in rendered
