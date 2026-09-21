"""Execute the exterior-inside-Clifford teaching notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "exterior_algebra_inside_clifford.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_zero_metric_clifford_product_is_the_wedge_product(lesson) -> None:
    _, definitions = lesson
    assert definitions["exterior_basis_squares_are_zero"] == (True, True, True)
    assert definitions["exterior_products_agree"] is True
    assert definitions["exterior_basis_product_count"] == 64
    assert definitions["exterior_all_basis_products_agree"] is True

    geometric = definitions["exterior_product_view"].latex(content="full")
    exterior = definitions["exterior_wedge_view"].latex(content="full")
    assert "Clifford product" in geometric
    assert "only exterior grade survives" in geometric
    assert "wedge product" in exterior
    assert "the same multivector" in exterior


def test_euclidean_metric_adds_a_scalar_without_changing_the_wedge(lesson) -> None:
    _, definitions = lesson
    assert definitions["euclidean_split_holds"] is True
    assert definitions["same_exterior_coefficients_zero_euclidean"] is True
    assert definitions["euclidean_orthogonal_products_agree"] is True

    rendered = definitions["euclidean_product_view"].latex(content="full")
    assert "metric overlap" in rendered
    assert "unchanged exterior part" in rendered


def test_oblique_basis_exposes_both_parts_of_a_basis_vector_product(lesson) -> None:
    _, definitions = lesson
    assert float(definitions["oblique_basis_pairing"]) == pytest.approx(0.5)
    assert definitions["oblique_split_holds"] is True
    assert definitions["same_exterior_coefficients_zero_oblique"] is True

    rendered = definitions["oblique_product_view"].latex(content="full")
    assert "basis vectors are not orthogonal" in rendered
    assert "oriented plane" in rendered


def test_symmetrising_and_antisymmetrising_recover_vector_products(lesson) -> None:
    _, definitions = lesson
    assert definitions["vector_product_identities_hold"] is True
    assert "symmetric metric part" in definitions["symmetric_part_view"].latex(content="full")
    assert "antisymmetric exterior part" in definitions["antisymmetric_part_view"].latex(content="full")


def test_metric_slider_changes_only_the_scalar_coefficient() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(defs={"metric_coupling": SimpleNamespace(value=-0.3)})
    assert definitions["parameter_decomposition_holds"] is True
    assert float(definitions["parameter_pairing"]) == pytest.approx(-0.3)
    assert definitions["parameter_product"].data[3] == pytest.approx(1.0)

    rendered = definitions["parameter_product_view"].latex(content="full")
    assert "moves with the metric" in rendered
    assert "stays fixed" in rendered


def test_higher_grade_product_routes_overlap_below_the_wedge_grade(lesson) -> None:
    _, definitions = lesson
    assert definitions["routing_top_grade_is_wedge"] is True
    assert definitions["zero_routing_products_agree"] is True
    assert definitions["routing_grade_two"].almost_equal(definitions["routing_algebra"].blade(0b0101))

    rendered = definitions["routing_product_view"].latex(content="full")
    assert "metric resolves the overlap" in rendered
    assert "exterior product" in rendered
    assert "only the disjoint directions survive" in definitions["zero_routing_product_view"].latex(content="full")
