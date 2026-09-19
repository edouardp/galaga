"""Execute the RGA object-style notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "rga_object_styles.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_rga_notebook_defaults_to_a_motor_bulk_weight_split(lesson) -> None:
    _, definitions = lesson
    assert set(definitions["objects"]) == {"point", "line", "plane", "motor", "flector"}
    rendered = definitions["view"].latex(content="value")
    assert r"\overgroup" in rendered and r"\undergroup" in rendered
    assert "bulk (attitude)" in rendered and "weight (moment)" in rendered


def test_rga_notebook_marker_control_changes_the_bulk_callout(lesson) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"over_marker": SimpleNamespace(value="overbracket")}
    )
    rendered = definitions["view"].latex(content="value")
    assert r"\overbracket" in rendered
    assert r"\overgroup" not in rendered


def test_rga_notebook_object_and_decomposition_controls(lesson) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, flector_definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"object_choice": SimpleNamespace(value="flector")}
    )
    flector = flector_definitions["view"].latex(content="value")
    assert r"\mathbf{e}_{1}" in flector and r"\mathbf{e}_{431}" in flector

    _, grade_definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"decomposition_choice": SimpleNamespace(value="grade")}
    )
    graded = grade_definitions["view"].latex(content="value")
    assert r"\overgroup" not in graded and r"\undergroup" not in graded
    assert r"\textcolor{#111827}{" in graded and r"\textcolor{#D55E00}{" in graded


def test_rga_notebook_compares_every_over_marker(lesson) -> None:
    _, definitions = lesson
    views = definitions["views"]
    for marker in ("overgroup", "overbrace", "overline", "overbracket"):
        assert "\\" + marker in views[marker].latex(content="value")
