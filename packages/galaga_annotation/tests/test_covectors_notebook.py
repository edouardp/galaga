"""Execute the covectors and metric-identification lesson headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "covectors_and_metric_identification.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    pytest.importorskip("galaga_matrix")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_temperature_differential_matches_the_euclidean_gradient(lesson) -> None:
    _, definitions = lesson
    assert definitions["temperature_covector_rate"] == pytest.approx(-0.25)
    assert float(definitions["temperature_ga_rate"]) == pytest.approx(-0.25)
    assert definitions["temperature_rates_agree"] is True

    rendered = definitions["temperature_rate_view"].latex(content="full")
    assert "evaluate the covector" in rendered
    assert "metric representative of dT" in definitions["temperature_gradient_view"].latex()


def test_vector_and_covector_coordinates_transform_contragrediently(lesson) -> None:
    _, definitions = lesson
    assert definitions["original_pairing"] == pytest.approx(2.0)
    assert definitions["transformed_pairing"] == pytest.approx(2.0)
    assert definitions["wrong_pairing"] == pytest.approx(3.5)
    assert definitions["coordinate_pairing_is_invariant"] is True
    assert definitions["vector_style_covector_transform_fails"] is True


def test_reciprocal_basis_represents_covectors_in_an_oblique_metric(lesson) -> None:
    _, definitions = lesson
    np.testing.assert_allclose(definitions["reciprocal_pairings"], np.eye(2), rtol=0, atol=1e-12)
    assert definitions["reciprocal_identity_holds"] is True
    assert definitions["oblique_covector_evaluation"] == pytest.approx(2.0)
    assert definitions["oblique_ga_evaluation"] == pytest.approx(2.0)
    assert definitions["oblique_naive_evaluation"] == pytest.approx(4.5)
    assert definitions["oblique_sharp_evaluation_holds"] is True
    assert definitions["oblique_naive_identification_fails"] is True

    assert "raised with the inverse metric" in definitions["oblique_sharp_view"].latex()
    assert "same coefficients, wrong vector" in definitions["oblique_naive_view"].latex()


def test_degenerate_pga_has_covectors_without_sharp_vectors(lesson) -> None:
    _, definitions = lesson
    assert definitions["pga_algebra"].is_degenerate is True
    assert definitions["pga_e0_pairings"] == (0.0, 0.0, 0.0)
    assert definitions["pga_e0_is_in_metric_kernel"] is True
    assert definitions["pga_sharp_residual"] == pytest.approx(1.0)
    assert definitions["pga_e0_covector_has_no_sharp"] is True
    assert definitions["pga_complement_identity"] is True

    assert "nonzero vector killed by flat" in definitions["pga_kernel_view"].latex()
    assert "metric-independent exterior complement" in definitions["pga_complement_view"].latex()


def test_lesson_states_the_api_boundary(lesson) -> None:
    outputs, _ = lesson
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "Do we need a covector type in Galaga?" in markup
    assert "Degenerate PGA metric" in markup
    assert "Differential-form calculus" in markup
