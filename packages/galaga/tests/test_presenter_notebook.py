"""Execute presenter teaching choices and check the algebra behind each view."""

import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.migrate_v2_notebooks import migrated_notebook_paths

ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples/galaga_v2/reusable_presenters.py"
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")


def test_presenter_notebook_is_in_the_executable_gallery():
    assert NOTEBOOK in migrated_notebook_paths(ROOT)


@pytest.fixture(
    scope="module",
    params=[
        (notation, content, signature)
        for notation in ("Lengyel", "Functional", "Short Functional", "Conventional")
        for content in ("auto", "name", "expr", "value", "full")
        for signature in ("mostly-minus", "mostly-plus")
    ],
)
def lesson(request):
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    notation, content, signature = request.param
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={
            "notation_choice": SimpleNamespace(value=notation),
            "content_choice": SimpleNamespace(value=content),
            "target_choice": SimpleNamespace(value="unicode"),
            "precision_choice": SimpleNamespace(value=6),
            "signature_choice": SimpleNamespace(value=signature),
        }
    )
    return outputs, definitions, content


def test_notation_and_content_controls_keep_the_same_wedge_result(lesson):
    _, d, content = lesson
    expected = (d["metric_inner_product"](d["e1"], d["e1"]) + d["e2"]) ^ ~d["e3"]
    view = d["chosen_view"]
    assert view.value == expected
    assert view.value is d["wedge_result"]
    assert view.presentation.display.content == content
    assert view.presentation.display.target == "unicode"
    assert view.presentation.display.coefficient_precision == 6
    assert view.latex() == expected.latex(presentation=view.presentation)
    assert d["pairing"] == d["alg"].scalar(d["alg"].gram[0, 0])


def test_output_cell_sets_display_target_and_precision():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={
            "notation_choice": SimpleNamespace(value="Short Functional"),
            "content_choice": SimpleNamespace(value="full"),
            "target_choice": SimpleNamespace(value="ascii"),
            "precision_choice": SimpleNamespace(value=3),
            "signature_choice": SimpleNamespace(value="mostly-minus"),
        }
    )
    display = definitions["chosen_view"].presentation.display
    assert display.content == "full"
    assert display.target == "ascii"
    assert display.coefficient_precision == 3


def test_order_and_oblique_style_lessons_preserve_numeric_truth(lesson):
    _, d, _ = lesson
    native, graded = d["bitmap_view"], d["grade_view"]
    assert native.value is graded.value is d["mixed"]
    np.testing.assert_array_equal(native.value.data, graded.value.data)
    assert native.presentation.display_order.masks == tuple(range(8))
    assert native.latex() != graded.latex()
    assert d["oblique_product"] == d["oblique"].gram[0, 1] + (d["a"] ^ d["b"])
    assert r"\wedge" in d["exterior_words"](d["oblique_product"]).latex()
    assert "0.5" in d["exterior_words"](d["oblique_product"]).latex()


def test_signed_sta_names_and_cga_frame_validation_are_computed(lesson):
    _, d, _ = lesson
    time, first, _, _ = d["sta"].basis_vectors()
    product = first * time
    ref = d["sigma_view"].presentation.blades.resolve("s1")
    assert product == d["sta"].blade(ref) == d["sigma_product"] == -d["native_product"]
    assert d["native_sigma_view"].latex() == "-" + d["sigma_view"].latex()
    cga = d["cga"]
    for original, view in zip(d["cga_parts"], d["cga_views"], strict=True):
        assert view.value is original
        np.testing.assert_array_equal(view.value.algebra.gram, cga.gram)
    assert cga.I == cga.basis_vectors()[0] ^ d["cga_parts"][0] ^ cga.basis_vectors()[-1]
    assert d["rejected_frame"]


def test_saved_views_and_markdown_remain_renderable(lesson):
    outputs, d, _ = lesson
    view = d["saved_view"]
    assert view.value is d["pairing"]
    assert view.latex() == d["saved_latex"]
    assert r"\bullet" in view.latex()
    assert view.latex() != d["pairing"].latex()
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert equations
    assert all("$" not in equation for equation in equations)
    assert "{chosen_view}" not in markup and "{sigma_view}" not in markup
