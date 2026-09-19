"""Execute the subexpression notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "subexpressions.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_subexpression_notebook_finds_the_subtree(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["view"].latex()
    assert r"\overset{\text{reverse factor}}{\colorbox{#e8f5e9}{$\widetilde{R}$}}" in rendered


def test_subexpression_notebook_selects_occurrences(lesson) -> None:
    _, definitions = lesson
    every = definitions["all_occurrences"].latex()
    assert every.count(r"\colorbox{#e8f5e9}{$\widetilde{R}$}") == 2
    first = definitions["first_occurrence"].latex()
    assert first.count(r"\textcolor{crimson}{\widetilde{R}}") == 1
