"""Execute the layered expression-provenance lesson headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "expression_provenance_layers.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    return runpy.run_path(str(NOTEBOOK))["app"].run()


def test_lesson_computes_the_displayed_multivectors(lesson) -> None:
    _, definitions = lesson
    assert definitions["provenance_verified"] is True
    assert definitions["B"].almost_equal(
        (definitions["e1"] ^ definitions["e2"])
        - (definitions["e1"] ^ definitions["e3"])
        - (definitions["e2"] ^ definitions["e3"])
    )
    assert definitions["a"].almost_equal(
        -2 * definitions["e1"]
        - 3 * definitions["e2"]
        + definitions["e3"]
        + (definitions["e1"] ^ definitions["e2"] ^ definitions["e3"])
    )


def test_top_expression_labels_each_variable_with_its_definition(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["top_view"].latex()

    assert definitions["B_definition"] == r"u \wedge v"
    assert definitions["x_definition"] == r"e_{1} + 2 e_{3}"
    assert r"\textcolor{#0072B2}{u \wedge v}" in rendered
    assert r"\textcolor{#D55E00}{e_{1} + 2 e_{3}}" in rendered
    assert rendered.count(r"\rule[0.2em]{0.4pt}{1em}") == 2
    assert [label.path for label in definitions["top_view"].katex().labels] == [
        ("parts", 1, "factors", 0),
        ("parts", 1, "factors", 1),
    ]


def test_second_layer_reveals_the_inputs_to_the_wedge(lesson) -> None:
    _, definitions = lesson
    rendered = definitions["plane_view"].latex()

    assert definitions["u_definition"] == r"e_{1} + e_{2}"
    assert definitions["v_definition"] == r"e_{2} - e_{3}"
    assert r"\textcolor{#009E73}{e_{1} + e_{2}}" in rendered
    assert r"\textcolor{#7C3AED}{e_{2} - e_{3}}" in rendered
    assert r"\wedge" in rendered
    assert [label.path for label in definitions["plane_view"].katex().labels] == [
        ("parts", 1, "operands", 0),
        ("parts", 1, "operands", 1),
    ]
