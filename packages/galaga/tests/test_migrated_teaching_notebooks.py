"""Execute the migrated lessons and test their displayed mathematics."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from galaga import exp, sandwich

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
ROOT = Path(__file__).resolve().parents[3]


def assert_same(actual, expected):
    np.testing.assert_allclose(actual.data, expected.data, rtol=0, atol=1e-12)


@pytest.fixture(scope="module", params=((0, 0, 0, 0), (60, 0.6, 0.7, 0.9), (270, 2, 2, 0)))
def mermaid_notebook(request):
    app = runpy.run_path(str(ROOT / "test_mermaid.py"))["app"]
    _, definitions = app.run(
        defs={
            name: SimpleNamespace(value=value)
            for name, value in zip(("d_slider", "phi_slider", "tw_phi_x", "tw_phi_y"), request.param, strict=True)
        }
    )
    return definitions


def assert_rotation_angle(definitions, plane):
    a, b = definitions["a"], definitions["b"]
    theta = np.radians(definitions["d_slider"].value)
    computed = sandwich(exp(-theta * plane / 2), a)
    expected = np.cos(theta) * a + np.sin(theta) * b
    assert_same(computed, expected)


def test_mermaid_plane_normalisation_preserves_the_slider_angle(mermaid_notebook):
    d = mermaid_notebook
    assert_same(d["B"] * d["B"], -d["alg"].identity)
    assert_rotation_angle(d, d["B"])
    assert_same(d["v_rot"], sandwich(d["R"], d["v"]))
    if d["d_slider"].value:
        with pytest.raises(AssertionError):
            assert_rotation_angle(d, (d["e1"] + d["e2"]) ^ d["e3"])


def test_mermaid_boost_invariant_and_wigner_factorisation(mermaid_notebook):
    d = mermaid_notebook
    assert_same(d["boosted_field"] ** 2, d["em_field"] ** 2)
    assert_same(d["pure_boost"] * d["wigner_rotor"], d["composite_boost"])
    assert_same(sandwich(d["wigner_rotor"], d["g0"]), d["g0"])
    theta = np.radians(d["wigner_angle"])
    expected = np.cos(theta) * d["g1"] + np.sin(theta) * d["g2"]
    assert_same(sandwich(d["wigner_rotor"], d["g1"]), expected)
    if not d["tw_phi_x"].value or not d["tw_phi_y"].value:
        assert d["wigner_angle"] == pytest.approx(0, abs=1e-12)


@pytest.fixture(scope="module")
def presentation_notebooks():
    return {
        name: runpy.run_path(str(ROOT / "examples/basics" / f"{name}.py"))["app"].run()[1]
        for name in ("dynamic_notation", "latex_rewrites_demo", "galaga_marimo_demo")
    }


def test_notation_changes_rendering_without_changing_the_value_or_provenance(presentation_notebooks):
    d = presentation_notebooks["dynamic_notation"]
    reverse = d["reversed_rotor"]
    assert_same(reverse, ~d["rotor"])
    before = reverse.expr, reverse.data.copy()
    texts = [reverse.latex(notation=n, content="full") for n in d["reverse_notations"].values()]
    assert len(set(texts)) == 4
    assert r"\widetilde" in d["reverse_renderings"]["Tilde"]
    assert r"\dagger" in d["reverse_renderings"]["Dagger"]
    assert r"\operatorname{rev}" in d["reverse_renderings"]["Function"]
    assert reverse.expr == before[0]
    np.testing.assert_array_equal(reverse.data, before[1])


def test_layout_lesson_teaches_current_emission_not_removed_rewrite_rules(presentation_notebooks):
    from galaga.expression import Symbol, evaluate
    from galaga.rendering.latex import emit

    d = presentation_notebooks["latex_rewrites_demo"]
    assert d["layout_latex"] == {
        "Ordinary fraction": r"\frac{a}{2}",
        "Script fraction": "e^{a/2}",
        "Explicit nested groups": r"\left(\left(a\right)\right)",
        "Explicit negative numerator": r"\frac{-a}{2}",
        "Explicit denominator one": r"\frac{a}{1}",
    }
    for label, node in d["layout_nodes"].items():
        before = hash(node), repr(node)
        assert emit(node) == d["layout_latex"][label]
        assert (hash(node), repr(node)) == before
    assert_same(d["layout_plane"] ** 2, -d["alg"].identity)
    assert_same(d["layout_rotor"] * ~d["layout_rotor"], d["alg"].identity)
    assert_same(d["divided_by_one"], d["division_input"])
    assert d["simplified_division"] == Symbol(d["division_input"].name)
    replayed = evaluate(d["simplified_division"], algebra=d["alg"], environment={"v": d["division_input"]})
    assert_same(replayed, d["division_input"])


def test_marimo_helpers_use_semantic_specs_and_explicit_coefficient_precision(presentation_notebooks):
    from string.templatelib import Interpolation, Template

    from galaga_marimo.renderer import render_template

    d = presentation_notebooks["galaga_marimo_demo"]
    assert_same(d["sandwich_expr"], sandwich(d["R"], d["v"]))
    assert d["coefficient_presentation"].display.coefficient_precision == 3
    assert "1.01" in d["rounded_latex"] and "3.46" in d["rounded_latex"]
    assert d["w"].coefficient(1) == 1.006
    # Build templates explicitly so this module remains importable on 3.11.
    template = Template(
        Interpolation(d["sandwich_expr"], "v", None, "expr"),
        " = ",
        Interpolation(d["sandwich_expr"], "v", None, "value"),
        "; ",
        Interpolation(d["w"].coefficient(1), "coefficient", None, ".3f"),
    )
    rendered = render_template(template)
    assert "1.006" in rendered
    assert d["sandwich_expr"].latex(content="value") in rendered


@pytest.fixture(
    scope="module",
    params=((0, 0, 0, 0, 30, 0), (60, 45, 60, 90, 60, 0.5), (180, 270, 180, 180, 90, 1)),
)
def quantum_notebook(request):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    previous = set(plt.get_fignums())
    with mpl.rc_context():
        app = runpy.run_path(str(ROOT / "examples/quantum/quantum_physics.py"))["app"]
        _, definitions = app.run(
            defs={
                name: SimpleNamespace(value=value)
                for name, value in zip(
                    ("theta_slider", "phi_slider", "meas_theta", "sg_slider", "precess_theta", "slerp_slider"),
                    request.param,
                    strict=True,
                )
            }
        )
        yield definitions
    for number in set(plt.get_fignums()) - previous:
        plt.close(number)


def test_spin_labels_and_pauli_bivector_products_agree_with_the_algebra(quantum_notebook):
    d = quantum_notebook
    for label, expected in {
        "Spin ↑z": d["e3"],
        "Spin ↓z": -d["e3"],
        "Spin +x": d["e1"],
        "Spin +y": d["e2"],
        "Spin −x": -d["e1"],
    }.items():
        assert_same(d["spin_vectors"][label], expected)
        assert_same(d["spin_states"][label] * ~d["spin_states"][label], d["alg"].identity)
    for blade in (d["B12"], d["B23"], d["B31"], d["I"]):
        assert_same(blade * blade, -d["alg"].identity)
    assert_same(d["B12"] * d["B23"], -d["B31"])
    wrong_sign = exp(np.pi / 4 * (d["e3"] ^ d["e1"]))
    with pytest.raises(AssertionError):
        assert_same(sandwich(wrong_sign, d["e3"]), d["spin_vectors"]["Spin +x"])


def test_bloch_coordinates_measurement_half_angle_and_reference_phase(quantum_notebook):
    d = quantum_notebook
    theta, phi = (np.radians(d[key].value) for key in ("theta_slider", "phi_slider"))
    expected = [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    np.testing.assert_allclose(d["bloch_vector"].vector_part, expected, rtol=0, atol=1e-12)
    difference = d["measurement_angles"] - np.radians(d["meas_theta"].value)
    np.testing.assert_allclose(d["measurement_probabilities"], np.cos(difference / 2) ** 2, rtol=0, atol=1e-12)
    assert_same(d["phase_spin"], d["bloch_vector"])
    assert not np.allclose(d["phase_rotor"].data, d["bloch_rotor"].data)


def test_stern_gerlach_probabilities_are_conditional_on_the_first_selection(quantum_notebook):
    d = quantum_notebook
    half_angle = np.radians(d["sg_slider"].value) / 2
    expected = np.cos(half_angle) ** 2
    np.testing.assert_allclose(d["sg_probabilities"], [expected, expected, expected**2], rtol=0, atol=1e-12)


def test_precession_direction_and_double_cover_are_visible_in_the_actual_vectors(quantum_notebook):
    d = quantum_notebook
    theta = np.radians(d["precess_theta"].value)
    times = d["precession_times"]
    expected = np.column_stack(
        (np.sin(theta) * np.cos(times), np.sin(theta) * np.sin(times), np.full_like(times, np.cos(theta)))
    )
    np.testing.assert_allclose(d["precession_vectors"], expected, rtol=0, atol=1e-12)
    assert_same(d["double_cover_rotors"][360], -d["alg"].identity)
    assert_same(d["double_cover_rotors"][720], d["alg"].identity)
    for degrees, vector in d["double_cover_vectors"].items():
        angle = np.radians(degrees)
        assert_same(vector, np.cos(angle) * d["e1"] + np.sin(angle) * d["e2"])


def test_phase_aligned_same_plane_slerp_reaches_the_expected_spin(quantum_notebook):
    d = quantum_notebook
    parameter = d["slerp_slider"].value
    angle = (1 - parameter) * np.pi / 6 + parameter * np.pi / 2
    expected = np.sin(angle) * d["e1"] + np.cos(angle) * d["e3"]
    assert_same(sandwich(d["slerp_rotor"], d["e3"]), expected)
    if parameter in (0, 1):
        assert_same(d["slerp_rotor"], d["slerp_endpoints"][int(parameter)])
