"""The logarithm lesson teaches algebraic branches and geometric paths."""

import html
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.migrate_v2_notebooks import migrated_notebook_paths

import galaga as ga

ROOT = Path(__file__).parents[3]
NOTEBOOK = ROOT / "examples/algebra/logarithms_and_generators.py"


def test_logarithm_notebook_is_in_the_executable_gallery():
    assert NOTEBOOK in migrated_notebook_paths(ROOT)


@pytest.fixture(scope="module")
def app():
    if sys.version_info < (3, 14):
        pytest.skip("notebook t-strings require Python 3.14")
    pytest.importorskip("marimo")
    return runpy.run_path(str(NOTEBOOK))["app"]


@pytest.fixture(scope="module")
def notebook(app):
    return app.run()


def assert_data(actual, expected, *, atol=1e-12):
    np.testing.assert_allclose(actual.data, expected.data, rtol=0, atol=atol)


def test_scalar_and_vector_examples_have_valid_nonrotor_logarithms(notebook):
    _, definitions = notebook
    algebra = definitions["vector_algebra"]
    vector = algebra.blade(1)
    assert vector * vector == algebra.gram[0, 0]
    assert float(definitions["scalar_logarithm"]) == pytest.approx(np.log(2))
    # Independent one-vector hyperbolic formula, not another call to log.
    assert_data(definitions["vector_input"], 2 * (np.cosh(0.3) + np.sinh(0.3) * vector))
    assert_data(definitions["vector_logarithm"], np.log(2) + 0.3 * vector)
    assert not ga.is_rotor(definitions["vector_input"])


def test_compound_example_derives_planes_from_the_oblique_metric(notebook):
    _, definitions = notebook
    algebra = definitions["compound_algebra"]
    gram = algebra.gram
    np.testing.assert_array_equal(definitions["compound_gram"].mat, gram)
    assert gram[0, 1] != 0
    first, second = definitions["compound_planes"]
    first_square = gram[0, 1] ** 2 - gram[0, 0] * gram[1, 1]
    second_square = gram[2, 3] ** 2 - gram[2, 2] * gram[3, 3]
    assert first * first == first_square < 0
    assert second * second == second_square > 0
    assert first * second == second * first
    a, b = np.sqrt(-first_square), np.sqrt(second_square)
    expected = (np.cos(0.2 * a) + np.sin(0.2 * a) / a * first) * (np.cosh(0.3 * b) + np.sinh(0.3 * b) / b * second)
    rotor = definitions["compound_rotor"]
    assert_data(rotor, expected)
    assert np.linalg.norm(ga.grade(rotor, 4).data) > 0.01
    nonscalar = rotor - ga.scalar_part(rotor)
    assert not ga.is_scalar(nonscalar * nonscalar)
    for key in ("compound_logarithm", "compound_recovered"):
        assert_data(definitions[key], 0.2 * first + 0.3 * second)
        assert ga.is_rotor_generator(definitions[key])


def test_nilpotent_example_keeps_the_nonzero_grade_three_correction(notebook):
    _, definitions = notebook
    n = definitions["nilpotent"]
    square = n * n
    assert square != 0 and square * n == 0
    expected = n - square / 2
    actual = definitions["nilpotent_logarithm"]
    assert_data(actual, expected)
    assert {grade for grade in (1, 2, 3) if np.any(ga.grade(actual, grade).data)} == {1, 2, 3}
    # The finite exponential is an independent oracle for this nilpotent.
    assert actual * actual * actual == 0
    assert_data(1 + actual + actual * actual / 2, definitions["nilpotent_input"])
    assert not ga.is_rotor_generator(actual)


def test_principal_branch_wraps_without_claiming_every_rejection_is_nonexistence(notebook):
    _, definitions = notebook
    plane = definitions["branch_plane"]
    original, wrapped = definitions["unwrapped_generator"], definitions["wrapped_logarithm"]
    assert_data(wrapped - original, -2 * np.pi * plane)
    expected = np.cos(1.25 * np.pi) + np.sin(1.25 * np.pi) * plane
    assert_data(ga.exp(wrapped), expected)
    failures = definitions["branch_failures"]
    assert len(failures) == 3
    assert ["singular" in error for _, _, error in failures] == [True, True, False]
    assert "principal real" in failures[-1][2]
    assert_data(ga.exp(np.pi * plane), failures[-1][1])
    for _, value, _ in failures:
        with pytest.raises(ValueError):
            ga.log(value)


def test_generator_example_distinguishes_a_rotor_endpoint_from_its_logarithm(notebook):
    _, definitions = notebook
    volume = definitions["path_volume"]
    logarithm, generator = definitions["path_logarithm"], definitions["path_generator"]
    assert ga.is_rotor(volume)
    assert_data(logarithm, np.pi / 2 * volume)
    assert not ga.is_rotor_generator(logarithm)
    assert ga.is_rotor_generator(generator)
    assert_data(ga.exp(logarithm), volume)
    assert_data(ga.exp(generator), volume)
    assert "alternative branch may exist" in definitions["path_generator_error"]


@pytest.mark.parametrize("parameter", (0, 0.25, 0.5, 0.75, 1))
def test_interactive_paths_preserve_endpoints_but_disagree_about_vector_preservation(app, parameter):
    _, definitions = app.run(defs={"path_parameter": SimpleNamespace(value=parameter)})
    algebra = definitions["path_algebra"]
    volume = definitions["path_volume"]
    vector, second = algebra.blade(1), algebra.blade(2)
    assert volume * vector == -vector * volume
    expected_algebra = np.cos(np.pi * parameter) * vector + np.sin(np.pi * parameter) * volume * vector
    expected_geometric = np.cos(np.pi * parameter) * vector - np.sin(np.pi * parameter) * second
    assert_data(definitions["algebra_path_image"], expected_algebra)
    assert_data(definitions["geometric_path_image"], expected_geometric)
    assert definitions["path_leakage"] == pytest.approx(abs(np.sin(np.pi * parameter)), abs=1e-12)
    assert ga.is_rotor(definitions["algebra_path_element"]) == (parameter in (0, 1))
    assert ga.is_rotor(definitions["geometric_path_element"])
    if parameter in (0, 1):
        endpoint = algebra.identity if parameter == 0 else volume
        assert_data(definitions["algebra_path_element"], endpoint)
        assert_data(definitions["geometric_path_element"], endpoint)


def test_rendered_lesson_contains_computed_values_and_no_unexpanded_templates(notebook):
    outputs, definitions = notebook
    markup = html.unescape("\n".join(getattr(output, "text", "") for output in outputs))
    for heading in (
        "Logarithms do not require rotors",
        "Compound inputs need the whole algebra",
        "A mixed-grade nilpotent logarithm",
        "A principal branch is a choice",
        "Same endpoint, different paths",
        "Tolerance is not a branch selector",
    ):
        assert heading in markup
    for key in (
        "vector_logarithm",
        "compound_logarithm",
        "nilpotent_logarithm",
        "wrapped_logarithm",
        "path_logarithm",
        "path_generator",
        "algebra_path_image",
        "geometric_path_image",
    ):
        assert definitions[key].latex(content="value") in markup
        assert "{" + key not in markup
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert equations and all("$" not in equation for equation in equations)
    assert r"\begin{pmatrix}" in markup
    assert "{path_time}" not in markup
    assert "alternative branch may exist" in markup
