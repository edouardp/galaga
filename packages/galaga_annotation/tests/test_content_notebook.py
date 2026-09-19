"""Execute the content-part notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "content_parts.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_content_notebook_annotates_every_part(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["view"].latex()
    assert r"\colorbox{#e8f5e9}{$A$}" in rendered
    assert r"\colorbox{#fff3cd}{$\left(e_{1} + e_{2}\right) e_{1}$}" in rendered
    assert r"\textcolor{royalblue}{1 - e_{12}}" in rendered


def test_content_notebook_respects_the_content_setting(lesson) -> None:
    outputs, definitions = lesson
    assert definitions["summary"] == {"full: missing": [], "value: missing": ["name"]}
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "One display, three annotated parts" in markup
    assert "Targeting the name, expression, and value" in markup
