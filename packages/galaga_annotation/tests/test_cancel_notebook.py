"""Execute the automatic-cancellation examples headlessly."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "test_cancel.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    return runpy.run_path(str(NOTEBOOK))["app"].run()


def test_notebook_cancels_orthogonal_inner_products(lesson) -> None:
    _, definitions = lesson
    first = definitions["first_view"].latex()
    several = definitions["several_view"].latex()

    assert r"\cancel{\textcolor{#aaaf}{e_{1} \cdot e_{2}}}" in first
    assert several.count(r"\cancel{") == 2


def test_notebook_cancels_a_composite_zero_identity(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["anticommutator_view"].latex()

    assert rendered.count(r"\cancel{") == 1
    assert r"\cancel{\textcolor{#aaaf}{e_{1} e_{2} + e_{2} e_{1}}}" in rendered


def test_notebook_makes_tolerance_explicit(lesson) -> None:
    _, definitions = lesson
    assert r"\cancel" not in definitions["exact_view"].latex()
    assert r"\cancel{\textcolor{#aaaf}{10^{-13} e_{1} \cdot e_{1}}}" in (definitions["tolerant_view"].latex())
    assert r"\cancel" not in definitions["control_view"].latex()
