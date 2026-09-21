"""Execute the plane-based and point-based PGA decomposition lesson."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "pga_decompositions.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_presets_share_the_metric_but_not_the_model_semantics(lesson) -> None:
    _, definitions = lesson
    assert definitions["pga_models_share_metric"] is True
    assert definitions["pga_models_have_distinct_semantics"] is True
    assert definitions["plane_algebra"].model.id == "pga"
    assert definitions["point_algebra"].model.id == "lengyel-rga"


def test_grade_and_parity_decompositions_reconstruct_the_value(lesson) -> None:
    _, definitions = lesson
    assert definitions["grade_decomposition_holds"] is True
    assert definitions["parity_reconstruction_holds"] is True
    assert definitions["graded_reconstruction"].almost_equal(definitions["graded_value"])
    rendered = definitions["graded_value_view"].latex()
    for grade_number in range(5):
        assert f"grade {grade_number}" in rendered


def test_playfair_split_is_square_zero_and_uses_the_grade_twist(lesson) -> None:
    _, definitions = lesson
    assert definitions["playfair_parts_reconstruct"] is True
    assert definitions["playfair_ideal_is_square_zero"] is True
    assert definitions["twisted_product_holds"] is True
    assert definitions["twisted_bulk_product_holds"] is True
    rendered = definitions["playfair_value_view"].latex()
    assert "Euclidean: Cl(W)" in rendered
    assert "ideal: Cl(W)e0" in rendered


def test_point_dependent_playfair_projection_selects_the_parallel_plane(lesson) -> None:
    _, definitions = lesson
    assert definitions["playfair_at_point_reconstructs"] is True
    assert definitions["plane_at_point_incidence"] is True
    assert definitions["plane_at_infinity"].almost_equal(2 * definitions["plane_e0"])
    rendered = definitions["playfair_at_point_view"].latex(content="expr")
    assert "parallel plane through P" in rendered
    assert "ideal residual" in rendered


def test_point_and_plane_models_exchange_object_specific_meanings(lesson) -> None:
    _, definitions = lesson
    assert definitions["object_bulk_weight_reconstructions"] == (True, True, True, True)
    assert "homogeneous weight" in definitions["plane_point_view"].latex(content="value")
    assert "position" in definitions["point_point_view"].latex(content="value")
    assert "normal" in definitions["plane_plane_view"].latex(content="value")
    assert "offset" in definitions["point_plane_view"].latex(content="value")

    plane_line = definitions["plane_line_view"].latex(content="value")
    point_line = definitions["point_line_view"].latex(content="value")
    assert "direction" in plane_line and "moment" in plane_line
    assert "direction" in point_line and "moment" in point_line
    assert definitions["plucker_constraint"] == pytest.approx(0.0)
    assert definitions["plane_line_is_simple"] is True
    assert definitions["point_line_is_simple"] is True


def test_bivector_lie_split_has_semidirect_closure(lesson) -> None:
    _, definitions = lesson
    assert definitions["rotation_bracket_stays_bulk"] is True
    assert definitions["mixed_bracket_stays_ideal"] is True
    assert definitions["translations_commute"] is True
    rendered = definitions["rigid_motion_generator_view"].latex()
    assert "rotation: so(3)" in rendered
    assert "translation: R3" in rendered


def test_complement_is_taught_as_a_correspondence_not_a_decomposition(lesson) -> None:
    outputs, definitions = lesson
    assert definitions["complement_swaps_point_plane_grades"] is True
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "Complement duality is not another additive decomposition" in markup
    assert "Playfair decomposition" in markup
    assert "Dual Approaches to Projective Geometric Algebra" in markup
