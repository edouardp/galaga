"""Execute the annotated inner/interior-products lesson headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "inner_and_interior_products.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_vector_blade_product_splits_into_lower_and_higher_grades(lesson) -> None:
    _, definitions = lesson
    assert definitions["product_decomposition_holds"] is True
    assert definitions["grade_lowering_part"].homogeneous_grade() == 1
    assert definitions["grade_raising_part"].homogeneous_grade() == 3

    rendered = definitions["product_decomposition_view"].latex(content="full")
    assert "Clifford product" in rendered
    assert "grade lowering" in rendered
    assert "grade raising" in rendered


def test_scalar_and_metric_bivector_pairings_have_opposite_signs(lesson) -> None:
    _, definitions = lesson
    assert float(definitions["bivector_scalar_product"]) == -1
    assert float(definitions["bivector_metric_pairing"]) == 1
    assert definitions["bivector_pairings_have_opposite_signs"] is True
    assert "geometric square" in definitions["scalar_product_view"].latex(content="full")
    assert "squared area" in definitions["metric_pairing_view"].latex(content="full")


def test_hestenes_and_doran_lasenby_differ_on_scalar_inputs(lesson) -> None:
    _, definitions = lesson
    assert definitions["hestenes_scalar_vector"].almost_equal(definitions["algebra"].scalar(0))
    assert definitions["doran_scalar_vector"].almost_equal(2 * definitions["e1"])
    assert definitions["scalar_policy_distinguished"] is True


def test_contractions_choose_direction_and_operand_order(lesson) -> None:
    _, definitions = lesson
    assert definitions["contraction_direction_checks"] == (True, True, True, True)
    assert definitions["left_contraction_value"].almost_equal(definitions["e2"])
    assert definitions["right_contraction_value"].almost_equal(-definitions["e2"])


def test_rga_interior_products_use_hodge_duals_and_antiwedge(lesson) -> None:
    _, definitions = lesson
    assert definitions["interior_constructions_hold"] == (True, True, True, True)
    assert definitions["contraction_interior_signs_differ"] is True

    left = definitions["left_interior_construction_view"].latex(content="full")
    right = definitions["right_interior_construction_view"].latex(content="full")
    for rendered in (left, right):
        assert "metric dual" in rendered
        assert "antiwedge" in rendered
        assert "interior result" in rendered


def test_equal_grade_interior_products_recover_metric_pairing(lesson) -> None:
    _, definitions = lesson
    assert definitions["equal_grade_identity_holds"] is True
    assert definitions["equal_grade_left_interior"].almost_equal(definitions["equal_grade_metric"])
    assert definitions["equal_grade_right_interior"].almost_equal(definitions["equal_grade_metric"])
    assert definitions["equal_grade_left_contraction"].almost_equal(-definitions["equal_grade_metric"])
    assert definitions["equal_grade_right_contraction"].almost_equal(-definitions["equal_grade_metric"])


def test_mixed_grade_selector_labels_only_visible_output_grades(lesson) -> None:
    _, definitions = lesson
    selected = definitions["selected_mixed_result"]
    assert selected == definitions["mixed_results"]["Doran–Lasenby"]

    rendered = definitions["selected_mixed_view"].latex(content="full")
    assert "selected operation" in rendered
    assert "grade 0" in rendered
    assert "grade 1" in rendered
    assert "grade 2" in rendered
    assert "grade 3" not in rendered
