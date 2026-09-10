"""Check the inner-product lesson using Gram minors and grade projections."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import galaga as ga

ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook t-strings require Python 3.14")


@pytest.fixture(
    scope="module",
    params=[
        ("Euclidean", "Vectors"),
        ("Oblique", "Vector–bivector"),
        ("Lorentzian", "Bivector–vector"),
        ("Degenerate", "Bivectors"),
        ("Euclidean", "Scalar–vector"),
        ("Oblique", "Scalars"),
        ("Lorentzian", "Mixed grades"),
    ],
)
def lesson(request):
    pytest.importorskip("marimo")
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
        app = runpy.run_path(str(ROOT / "examples/galaga_v2/inner_products.py"))["app"]
        return app.run(
            defs={
                "metric_choice": SimpleNamespace(value=request.param[0]),
                "case_choice": SimpleNamespace(value=request.param[1]),
            }
        )


def test_scalar_pairings_match_independent_gram_minors(lesson):
    _, values = lesson
    algebra = values["algebra"]
    indices = [tuple(i for i in range(algebra.n) if mask & (1 << i)) for mask in range(algebra.dim)]
    induced = np.zeros((algebra.dim, algebra.dim))
    scalar = np.zeros_like(induced)
    for i, rows in enumerate(indices):
        for j, cols in enumerate(indices):
            if len(rows) == len(cols):
                induced[i, j] = np.linalg.det(algebra.gram[np.ix_(rows, cols)])
                scalar[i, j] = induced[i, j] * (-1) ** (len(rows) * (len(rows) - 1) // 2)
    for name, (a, b) in values["samples"].items():
        results = values["comparisons"][name]
        for operation, matrix in (("scalar_product", scalar), ("metric_inner_product", induced)):
            expected = algebra.scalar(a.data @ matrix @ b.data)
            np.testing.assert_allclose(results[operation].data, expected.data, atol=1e-12, rtol=0)
            assert results[operation].expr.operation_id == operation
    plane = values["plane"]
    assert values["induced_square"] == pytest.approx(plane.data @ induced @ plane.data)


def test_contractions_and_grade_difference_products_match_expanded_geometric_product(lesson):
    _, values = lesson
    algebra = values["algebra"]
    for label, (a, b) in values["samples"].items():
        expected = {
            name: algebra.scalar(0)
            for name in ("left_contraction", "right_contraction", "hestenes_inner", "doran_lasenby_inner")
        }
        for r in range(algebra.n + 1):
            for s in range(algebra.n + 1):
                product = ga.grade(a, r) * ga.grade(b, s)
                if r <= s:
                    expected["left_contraction"] += ga.grade(product, s - r)
                if r >= s:
                    expected["right_contraction"] += ga.grade(product, r - s)
                if r and s:
                    expected["hestenes_inner"] += ga.grade(product, abs(r - s))
                expected["doran_lasenby_inner"] += ga.grade(product, abs(r - s))
        for name, result in expected.items():
            np.testing.assert_allclose(values["comparisons"][label][name].data, result.data, atol=1e-12, rtol=0)
        np.testing.assert_allclose((a | b).data, expected["doran_lasenby_inner"].data, atol=1e-12, rtol=0)
        assert ga.dorst_inner is ga.doran_lasenby_inner
    np.testing.assert_allclose(
        values["reconstructed_inner"].data,
        values["comparisons"]["Mixed grades"]["doran_lasenby_inner"].data,
        atol=1e-12,
        rtol=0,
    )


def test_related_rga_products_follow_hodge_and_complementary_metric(lesson):
    _, values = lesson
    rga = values["rga"]
    x, y, _, null = rga.basis_vectors()
    plane = x ^ y
    related = values["related_results"]
    assert related["left_interior"] == ga.antiwedge(ga.left_hodge_dual(x), plane)
    assert related["right_interior"] == ga.antiwedge(plane, ga.right_hodge_dual(x))
    assert related["left_interior"] == -related["left_contraction"]
    assert related["right_interior"] == -related["right_contraction"]
    assert float(related["metric"]) == 0
    assert np.linalg.norm(null.data) > 0
    expected_antidot = np.linalg.det(rga.gram[:-1, :-1]) * rga.I
    np.testing.assert_allclose(related["antidot"].data, expected_antidot.data, atol=1e-12, rtol=0)
    assert np.linalg.norm(related["antidot"].data) > 0


def test_lesson_renders_definitions_and_cites_primary_sources(lesson):
    outputs, _ = lesson
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup
    for domain in ("davidhestenes.net", "geometry.mrao.cam.ac.uk", "staff.fnwi.uva.nl", "terathon.com"):
        assert domain in markup
