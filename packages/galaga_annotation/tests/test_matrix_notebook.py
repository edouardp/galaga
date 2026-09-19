"""Execute the matrix annotation notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "matrix_annotations.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    pytest.importorskip("galaga_matrix")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_matrix_notebook_resolves_cells_rows_and_blocks(lesson) -> None:
    _, definitions = lesson
    assert definitions["roundtrip_ok"] is True
    assert definitions["cell_plan_summary"] == [((0, 0),), ((0, 3),)]
    assert definitions["grade_masks"] == {0: (0,), 1: (1, 2), 2: (3,)}
    assert definitions["summary"] == {
        "plain is matrix": True,
        "shape delegated": True,
        "arithmetic blocked": True,
    }


def test_matrix_notebook_lowers_every_selector(lesson) -> None:
    _, definitions = lesson

    cell_text = definitions["cell_view"].latex()
    assert r"\overset{\textcolor{#2f7d4f}{\text{scalar input}}}{\colorbox{#e8f5e9}{$1$}}" in cell_text
    assert r"\overset{\textcolor{#8a6d1a}{\text{bivector input}}}{\colorbox{#fff3cd}{$-3$}}" in cell_text

    line_text = definitions["line_view"].latex()
    assert r"\textcolor{#0072B2}{\text{e1 row}}" not in line_text
    assert r"\textcolor{#0072B2}{" in line_text
    assert r"\colorbox{#f3e8ff}{$" in line_text

    grade_text = definitions["grade_view"].latex()
    assert r"\colorbox{#e8e8e8}{$" in grade_text
    assert r"\colorbox{#d6e8f7}{$" in grade_text
    assert r"\colorbox{#f7dfd6}{$" in grade_text

    block_text = definitions["block_view"].latex()
    assert r"\fcolorbox{seagreen}{#e8f5e9}{$" in block_text
    assert r"\underset{\text{vector × vector}}" in block_text

    whole_text = definitions["whole_view"].latex()
    assert r"\underbrace{" in whole_text
    assert r"}_{\text{left multiplication by A}}" in whole_text

    quat_text = definitions["quat_view"].latex()
    assert r"\colorbox{#e8f5e9}{$1$}" in quat_text
    assert r"\colorbox{#fff3cd}{$-1$}" in quat_text


def test_matrix_notebook_reports_empty_and_invalid_regions(lesson) -> None:
    outputs, definitions = lesson
    assert definitions["empty_labels"] == ["no rows"]
    assert definitions["strict_result"] == "MissingTargetError"
    assert definitions["out_of_range_result"] == "ValueError"
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "\\colorbox" in markup
    assert "\\fcolorbox" in markup
    assert "\\underbrace" in markup
