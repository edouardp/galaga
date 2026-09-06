"""Execute the teaching maps and check them against native CGA operations."""

from __future__ import annotations

import re
import runpy
import sys
from pathlib import Path

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, to_matrix

from galaga import Algebra, sandwich, squared

ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook t-strings require Python 3.14")


@pytest.fixture(scope="module", autouse=True)
def _require_notebook_runtime():
    pytest.importorskip("marimo")


@pytest.fixture(scope="module", params=(-1.0, -2.0))
def notebook(request):
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
        app = runpy.run_path(str(ROOT / "examples/matrix/cga_complex_and_quaternion.py"))["app"]
        return app.run(defs={"null_pair_scale": request.param})


def test_even_generators_satisfy_the_computed_auxiliary_metric(notebook):
    _, definitions = notebook
    generators = definitions["even_generators"]
    algebra = definitions["cga_algebra"]
    auxiliary = definitions["auxiliary_algebra"]
    for row, left in enumerate(generators):
        for column, right in enumerate(generators):
            expected = 2 * auxiliary.gram[row, column] * algebra.identity
            np.testing.assert_allclose((left * right + right * left).data, expected.data, atol=2e-12, rtol=0)
    assert np.linalg.matrix_rank(definitions["even_frame"]) == auxiliary.dim


def test_every_native_even_blade_roundtrips_through_quaternions(notebook):
    _, definitions = notebook
    algebra = definitions["cga_algebra"]
    for mask in range(algebra.dim):
        if mask.bit_count() % 2:
            continue
        value = algebra.blade(mask)
        matrix = definitions["quaternion_image"](value)
        assert len(matrix.quat) == 2 and all(len(row) == 2 for row in matrix.quat)
        assert matrix.algebra.numeric is definitions["auxiliary_algebra"].numeric
        recovered = definitions["native_from_quaternion"](matrix)
        np.testing.assert_allclose(recovered.data, value.data, atol=2e-12, rtol=0)


def test_even_quaternion_products_match_native_geometric_products(notebook):
    _, definitions = notebook
    algebra = definitions["cga_algebra"]
    image = definitions["quaternion_image"]
    rng = np.random.default_rng(381)
    odd_masks = [mask for mask in range(algebra.dim) if mask.bit_count() % 2]
    for _ in range(8):
        coefficients = rng.normal(size=(2, algebra.dim))
        coefficients[:, odd_masks] = 0
        left, right = (algebra.multivector(row) for row in coefficients)
        np.testing.assert_allclose(image(left * right).mat, image(left).mat @ image(right).mat, atol=2e-11, rtol=0)


def test_single_quaternion_image_rejects_odd_and_mixed_examples(notebook):
    _, definitions = notebook
    for value in (definitions["point_p"], definitions["mixed_value"]):
        with pytest.raises(ValueError, match="requires an even CGA value"):
            definitions["quaternion_image"](value)


def test_central_unit_and_pair_reconstruct_every_native_blade(notebook):
    _, definitions = notebook
    algebra = definitions["cga_algebra"]
    central = definitions["central_unit"]
    assert float(squared(central)) == pytest.approx(-1)
    for mask in range(algebra.dim):
        value = algebra.blade(mask)
        np.testing.assert_allclose((central * value).data, (value * central).data, atol=2e-12, rtol=0)
        recovered = definitions["native_from_pair"](definitions["quaternion_pair"](value))
        np.testing.assert_allclose(recovered.data, value.data, atol=2e-12, rtol=0)


def test_quaternion_pair_product_preserves_order_and_the_central_square(notebook):
    _, definitions = notebook
    algebra = definitions["cga_algebra"]
    pair = definitions["quaternion_pair"]
    central_square = float(squared(definitions["central_unit"]))
    rng = np.random.default_rng(496)
    for _ in range(8):
        left, right = (algebra.multivector(rng.normal(size=algebra.dim)) for _ in range(2))
        even_left, odd_left = pair(left)
        even_right, odd_right = pair(right)
        product_pair = (
            even_left @ even_right + central_square * (odd_left @ odd_right),
            even_left @ odd_right + odd_left @ even_right,
        )
        recovered = definitions["native_from_pair"](product_pair)
        np.testing.assert_allclose(recovered.data, (left * right).data, atol=3e-11, rtol=0)


def test_gallery_examples_roundtrip_in_both_full_representations(notebook):
    _, definitions = notebook
    for value, _ in definitions["samples"].values():
        for mode in ("compact", "left-regular"):
            matrix = to_matrix(value, mode=mode)
            assert matrix.shape == ((4, 4) if mode == "compact" else (32, 32))
            np.testing.assert_allclose(from_matrix(matrix).data, value.data, atol=2e-12, rtol=0)
            np.testing.assert_allclose(
                matrix.mat @ matrix.mat, to_matrix(value * value, mode=mode).mat, atol=2e-11, rtol=0
            )


def test_lifted_objects_have_the_incidence_and_translation_described(notebook):
    _, definitions = notebook
    p, q, r, s = (definitions[key] for key in ("point_p", "point_q", "point_r", "point_s"))
    for point in (p, q, r, s):
        np.testing.assert_allclose(squared(point).data, 0, atol=2e-12, rtol=0)
    for key, incident_points in (
        ("line", (p, q)),
        ("circle", (p, q, r)),
        ("sphere", (p, q, r, s)),
        ("plane", (p, q, r)),
    ):
        surface = definitions[key]
        assert np.linalg.norm(surface.data) > 0
        for point in incident_points:
            np.testing.assert_allclose((point ^ surface).data, 0, atol=2e-12, rtol=0)
    cga = definitions["cga"]
    expected = cga.coordinates(p) + cga.coordinates(cga.up(definitions["displacement"]))
    translated = sandwich(definitions["translation"], p)
    np.testing.assert_allclose(cga.coordinates(translated), expected, atol=2e-12, rtol=0)


def test_mixed_example_needs_both_quaternion_components(notebook):
    outputs, definitions = notebook
    value = definitions["mixed_value"]
    even, odd = definitions["quaternion_pair"](value)
    assert np.linalg.norm(even.mat) > 0 and np.linalg.norm(odd.mat) > 0
    np.testing.assert_allclose(definitions["native_from_pair"]((even, odd)).data, value.data, atol=2e-12, rtol=0)
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    normalization = next(equation for equation in equations if "J^2=-1" in equation)
    assert "$" not in normalization


def test_native_null_notebook_scalar_equation_has_no_nested_math_delimiters():
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
        app = runpy.run_path(str(ROOT / "examples/matrix/cga_via_gram_matrix.py"))["app"]
        outputs, _ = app.run()
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    equation = next(equation for equation in equations if "e_o^2=" in equation)
    assert "$" not in equation
    assert "e_o^2=0" in equation
    assert r"e_\infty^2=0" in equation
    assert r"e_o\mathbin{\cdot}e_\infty=-1" in equation


def test_oblique_notebook_generator_checks_follow_an_edited_metric():
    gram = np.array([[3.0, 0.75], [0.75, -2.0]])
    algebra = Algebra(gram=gram)
    e1, e2 = algebra.basis_vectors(expr=True)
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
        app = runpy.run_path(str(ROOT / "examples/matrix/general_gram_compact_foundations.py"))["app"]
        _, definitions = app.run(
            defs={
                "oblique": algebra,
                "gram_2d": gram,
                "gram_matrix": MatrixRepr(gram),
                "e1_oblique": e1,
                "e2_oblique": e2,
            }
        )
    assert definitions["clifford_relations_hold"]
    assert definitions["decomposition_holds"]
    assert definitions["homomorphism_holds"]
    assert definitions["roundtrip_holds"]
