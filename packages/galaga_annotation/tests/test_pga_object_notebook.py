"""Execute the PGA object-style notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "pga_object_styles.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_pga_notebook_defaults_to_a_motor_split(lesson) -> None:
    _, definitions = lesson
    assert set(definitions["objects"]) == {"point", "line", "plane", "rotor", "motor"}
    rendered = definitions["view"].latex(content="value")
    assert r"\overgroup" in rendered and r"\undergroup" in rendered
    assert "Euclidean" in rendered and "projective (e0)" in rendered


def test_pga_notebook_marker_control_changes_the_euclidean_callout(lesson) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(defs={"over_marker": SimpleNamespace(value="overline")})
    rendered = definitions["view"].latex(content="value")
    assert r"\overline" in rendered
    assert r"\overgroup" not in rendered


def test_pga_notebook_object_and_decomposition_controls(lesson) -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, rotor_definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"object_choice": SimpleNamespace(value="rotor")}
    )
    rotor = rotor_definitions["view"].latex(content="value")
    assert r"\undergroup" not in rotor  # a rotor has no projective part

    _, grade_definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"decomposition_choice": SimpleNamespace(value="grade")}
    )
    graded = grade_definitions["view"].latex(content="value")
    assert r"\overgroup" not in graded and r"\undergroup" not in graded
    assert r"\textcolor{#111827}{" in graded and r"\textcolor{#D55E00}{" in graded


def test_pga_notebook_compares_every_over_marker(lesson) -> None:
    _, definitions = lesson
    views = definitions["views"]
    for marker in ("overgroup", "overbrace", "overline", "overbracket"):
        assert "\\" + marker in views[marker].latex(content="value")
