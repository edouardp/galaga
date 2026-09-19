"""Execute the sign-highlight notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "sign_highlights.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_sign_notebook_highlights_the_glyph(lesson) -> None:
    _, definitions = lesson
    assert definitions["sign_colour"].value == "#fff3cd"
    rendered = definitions["signs_view"].latex()
    assert r"\colorbox{#fff3cd}{$+$}" in rendered
    assert r"\colorbox{#fff3cd}{$-$}" in rendered
    # Neighbouring terms keep their coefficients and blades.
    assert r"2 e_{1}" in rendered and r"3 e_{12}" in rendered


def test_sign_notebook_shows_multiple_signs_and_spans(lesson) -> None:
    outputs, definitions = lesson
    multiple = definitions["all_signs"].latex()
    assert multiple.count(r"\textcolor{crimson}{") == 3

    span = definitions["span_view"].latex()
    assert r"\colorbox{#eeeeee}{$2 e_{1} \textcolor{crimson}{-} 3 e_{12}$}" in span

    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "Two signs, boxed" in markup
    assert "A sign inside a joined span" in markup
