import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.util import find_spec
from pathlib import Path
from types import SimpleNamespace

import pytest
from tools.migrate_v2_notebooks import migrate_source, migrated_notebook_paths

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"


def test_new_example_notebooks_compile():
    """Verify every listed example notebook is valid Python and has marimo boilerplate."""
    for notebook in migrated_notebook_paths(ROOT):
        source = notebook.read_text()
        if sys.version_info >= (3, 14):
            compile(source, str(notebook), "exec")
        else:
            assert "app = marimo.App(" in source
            assert '__generated_with = "' in source


def test_presentation_and_oblique_lessons_cover_their_live_displays() -> None:
    notation = (EXAMPLES / "galaga_v2/notation_overrides.py").read_text()
    oblique = (EXAMPLES / "galaga_v2/oblique_plane.py").read_text()
    gallery = (EXAMPLES / "galaga_v2/display_gallery.py").read_text()

    assert "presets.sta() | notation_patch" in notation
    assert "presets.notation.override(reverse=reverse_style.value)" in notation
    assert "presets.oblique_plane(degrees=angle_degrees.value)" in oblique
    assert "oblique2d(oblique, [sample_vector, sample_bivector]" in oblique
    for display in (
        "basis_vectors()",
        "basis_blades(2)",
        "wedge_product_table(colour=True)",
        "bilinear_form_table()",
        "bilinear_form_table(full=True)",
    ):
        assert display in gallery


def test_spinor_ideals_lesson_is_in_the_executable_gallery():
    assert EXAMPLES / "matrix/spinors_ideals_and_chirality.py" in migrated_notebook_paths(ROOT)


def test_exterior_algebra_lesson_compares_real_powers_and_metric_boundaries() -> None:
    source = (EXAMPLES / "algebra/exterior_algebra_intuition.py").read_text()

    assert "presets.exterior(3)" in source
    assert "Algebra(3, expr=True)" in source
    assert "nilpotent * nilpotent" in source
    assert "_cube == 0" in source
    assert "x**1.5" in source
    assert "x ** (-1 / 3)" in source
    assert "sqrt(_null_value)" in source
    assert "_regular_value**1.5" in source
    assert "_zero**0.5" in source
    assert '("zero scalar part", e1, 0.5)' in source
    assert '("negative scalar part", -1 + e1, 0.5)' in source
    assert "dual(e1)" in source
    assert "## Interactive oriented area" in source
    assert "${" not in source
    assert "{_u:block}" in source
    assert "{_v:block}" in source


def test_reusable_presenters_lesson_shows_composed_and_scoped_recipes() -> None:
    source = (EXAMPLES / "galaga_v2/reusable_presenters.py").read_text()

    assert 'presets.blades.indexed(3, style="wedge")' in source
    assert 'presets.notation.override(reverse="dagger")' in source
    assert "Presenter(config=recipe)" in source
    assert "Presenter(notation=presets.notation.override" in source
    assert "alg.with_presentation(recipe)" in source
    assert "alg.use_presentation(recipe)" in source
    assert "alg.with_notation(_patch)" in source
    assert "alg.use_notation(_patch)" in source


def test_witt_plane_lesson_derives_geometry_and_matrix_units_from_both_null_pair_signs() -> None:
    from galaga import Algebra, metric_inner_product

    source = (EXAMPLES / "algebra/witt_plane_from_null_coordinates.py").read_text()
    assert '"−1 (CGA-style)": -1, "+1": 1' in source
    assert "MatrixRepr(raising_matrix)" in source
    assert "np.linalg.lstsq(_basis_columns, _action" in source
    assert "witt.gram[0, 1]" in source

    for sign in (-1, 1):
        algebra = Algebra(gram=((0, sign), (sign, 0)))
        p, q = algebra.basis_vectors()
        vector = 1.2 * p + 0.8 * q
        projector = p * q / (2 * sign)
        complement = q * p / (2 * sign)
        raising = p / (2**0.5 * sign)
        lowering = q / 2**0.5

        assert not algebra.is_degenerate
        assert (p * p, q * q, p * q + q * p) == (0, 0, 2 * sign)
        assert abs(float(vector * vector) - 2 * sign * 1.2 * 0.8) < 1e-12
        assert abs(float(metric_inner_product(vector, q / sign)) - 1.2) < 1e-12
        assert abs(float(metric_inner_product(vector, p / sign)) - 0.8) < 1e-12
        assert projector * projector == projector
        assert complement * complement == complement
        assert projector + complement == 1
        assert projector * complement == 0
        assert raising * raising == lowering * lowering == 0
        assert (raising * lowering).almost_equal(projector)
        assert (lowering * raising).almost_equal(complement)


def test_conformal_spacetime_lessons_embed_classify_and_transform_events() -> None:
    import numpy as np

    from galaga import Algebra, exp, metric_inner_product, sandwich

    events = (EXAMPLES / "spacetime/conformal_spacetime_events.py").read_text()
    versors = (EXAMPLES / "spacetime/conformal_spacetime_versors.py").read_text()
    classifier = (EXAMPLES / "spacetime/conformal_spacetime_classifier.py").read_text()
    for notebook in (events, versors, classifier):
        assert "gram[4, 5] = gram[5, 4] = -1" in notebook
        assert "blades=BladeConvention(6, _labels)" in notebook
        assert 'Name("n_o", "nₒ", r"n_o")' in notebook
        assert 'Name("n_inf", "n∞", r"n_\\infty")' in notebook
    assert "meet(alice_curve, dual(light_cone))" in events
    assert "if t_e >= 1:" in events
    assert "normalize_point(sandwich(translator, source))" in versors
    assert "S^2" in classifier
    assert "not a public" in classifier

    gram = np.zeros((6, 6))
    gram[:4, :4] = np.diag([1, -1, -1, -1])
    gram[4, 5] = gram[5, 4] = -1
    algebra = Algebra(gram=gram)
    g0, g1, _, _, origin, infinity = algebra.basis_vectors()

    def event(t, x=0.0):
        physical = t * g0 + x * g1
        return origin + physical + 0.5 * float(physical * physical) * infinity

    def normalized(point):
        return point / -float(metric_inner_product(point, infinity))

    anchor = event(0)
    for t, x, causal in ((1, 0, 1), (1, 1, 0), (0, 1, -1)):
        other = event(t, x)
        pair = anchor ^ other
        line = pair ^ infinity
        interval = -2 * float(metric_inner_product(anchor, other))
        signed_round = anchor - 0.5 * causal * infinity
        assert pair.homogeneous_grade() == 2
        assert line.homogeneous_grade() == 3
        assert (line ^ infinity).almost_equal(algebra.scalar(0))
        assert abs(interval - causal) < 1e-12
        assert abs(float(signed_round * signed_round) - causal) < 1e-12
        assert abs(float(metric_inner_product(other, signed_round))) < 1e-12

    source = event(0.75, 0.1)
    displacement = 0.5 * g0 + 0.25 * g1
    translator = exp(-0.5 * (displacement ^ infinity))
    assert normalized(sandwich(translator, source)).almost_equal(event(1.25, 0.35), atol=1e-10)
    scale = float(np.exp(0.5))
    dilator = exp(0.25 * (origin ^ infinity))
    assert normalized(sandwich(dilator, source)).almost_equal(event(0.75 * scale, 0.1 * scale), atol=1e-10)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
def test_conformal_spacetime_notebooks_render_the_requested_basis_names(csta_events_lesson) -> None:
    import runpy

    expected = (r"\gamma_0", r"\gamma_1", r"\gamma_2", r"\gamma_3", r"n_o", r"n_\infty")
    for name in (
        "conformal_spacetime_events.py",
        "conformal_spacetime_versors.py",
        "conformal_spacetime_classifier.py",
    ):
        if name == "conformal_spacetime_events.py":
            definitions = csta_events_lesson
        else:
            namespace = runpy.run_path(str(EXAMPLES / "spacetime" / name), run_name="csta_lesson")
            _, definitions = namespace["app"].run()
        blades = definitions["csta"].presentation.blades
        assert tuple(blades.label(1 << index).name.latex for index in range(6)) == expected
        assert blades.label((1 << 0) | (1 << 4) | (1 << 5)).name.latex == (r"\gamma_0 \wedge n_o \wedge n_\infty")


@pytest.fixture(scope="module")
def csta_events_lesson():
    if sys.version_info < (3, 14):
        pytest.skip("Marimo t-strings require Python 3.14")
    import runpy

    namespace = runpy.run_path(str(EXAMPLES / "spacetime/conformal_spacetime_events.py"), run_name="csta_lesson")
    _, definitions = namespace["app"].run()
    yield definitions
    definitions["plt"].close("all")


def test_csta_rotor_samples_and_surface_meet_define_the_same_hyperbola(csta_events_lesson) -> None:
    import numpy as np

    from galaga import metric_inner_product

    d = csta_events_lesson
    zero = d["csta"].scalar(0)
    for tau in (0, 0.5, 0.7, 1, 2):
        q = d["alice_position"](tau)
        velocity = np.cosh(tau) * d["g0"] + np.sinh(tau) * d["g1"]
        expected = np.sinh(tau) * d["g0"] + (np.cosh(tau) - 1) * d["g1"]
        assert q.almost_equal(expected, atol=1e-10)
        assert float(velocity * velocity) == pytest.approx(1)
        assert float((q + d["g1"]) ** 2) == pytest.approx(-1)
        derivative = (d["alice_position"](tau + 1e-5) - d["alice_position"](tau - 1e-5)) / 2e-5
        assert derivative.almost_equal(velocity, atol=1e-8)
        point = d["alice_event"](tau)
        assert (point ^ d["alice_curve"]).almost_equal(zero, atol=1e-9)
        alice_round = d["event"](0, -1) + 0.5 * d["infinity"]
        assert abs(float(metric_inner_product(point, alice_round))) < 1e-9
    curve = d["alice_curve"]
    surface_curve = d["curve_from_surfaces"]
    assert curve.homogeneous_grade() == surface_curve.homogeneous_grade() == 3
    scale = np.dot(curve.data, surface_curve.data) / np.dot(curve.data, curve.data)
    assert abs(scale) > 1e-8
    assert surface_curve.almost_equal(scale * curve, atol=1e-10)


def test_csta_reception_and_echo_are_on_the_computed_meets(csta_events_lesson) -> None:
    import numpy as np

    from galaga import dual, meet, metric_inner_product

    d = csta_events_lesson
    for emission_time in (0.05, 0.5, 0.975):
        timings = d["radar_times"](emission_time)
        emission = d["event"](emission_time)
        reception = d["reception_event"](emission_time)
        echo = d["event"](timings["echo"])
        outbound_pair = meet(d["alice_curve"], dual(emission))
        earth_line = d["event"](0) ^ d["event"](1) ^ d["infinity"]
        reply_pair = meet(earth_line, dual(reception))
        assert timings["receive"] >= emission_time
        assert timings["echo"] >= timings["receive"]
        assert timings["receive"] - timings["distance"] == pytest.approx(emission_time)
        assert timings["echo"] == pytest.approx(timings["receive"] + timings["distance"])
        assert abs(float(metric_inner_product(reception, emission))) < 1e-8
        assert (reception ^ outbound_pair).almost_equal(d["csta"].scalar(0), atol=1e-8)
        # The return cone meets Earth's line at both E and F, up to projective scale.
        expected_pair = emission ^ echo
        ratio = np.dot(reply_pair.data, expected_pair.data) / np.dot(expected_pair.data, expected_pair.data)
        assert abs(ratio) > 1e-8
        assert reply_pair.almost_equal(ratio * expected_pair, atol=1e-8)
    assert d["radar_times"](0.5) == pytest.approx({"ship": np.log(2), "receive": 0.75, "distance": 0.25, "echo": 1.0})
    for emission_time in (1.0, 1.1):
        assert d["radar_times"](emission_time) is None
        assert d["reception_event"](emission_time) is None


def test_csta_natural_unit_helpers_provide_numbers_and_readable_units(csta_events_lesson) -> None:
    d = csta_events_lesson
    seconds = 299_792_458 / 9.80665
    metres = 299_792_458 * seconds
    assert d["time_in"](1) == pytest.approx(seconds)
    assert d["distance_in"](1) == pytest.approx(metres)
    assert d["time_in"](1, "years") == pytest.approx(0.9687150795722889)
    assert d["distance_in"](1, "ly") == pytest.approx(d["time_in"](1, "years"))
    year_seconds = 365.25 * 86400
    time_units = {
        "s": 1.0,
        "min": 60.0,
        "h": 3600.0,
        "days": 86400.0,
        "weeks": 7 * 86400.0,
        "months": year_seconds / 12,
        "years": year_seconds,
    }
    for unit, size in time_units.items():
        assert d["time_in"](2 * size / seconds, unit) == pytest.approx(2)
        assert d["format_time"](2 * size / seconds).endswith(" " + unit)
    distance_units = {"m": 1.0, "km": 1000.0, "AU": 149_597_870_700.0, "ly": 299_792_458 * year_seconds}
    for unit, size in distance_units.items():
        assert d["distance_in"](2 * size / metres, unit) == pytest.approx(2)
        assert d["format_distance"](2 * size / metres).endswith(" " + unit)
    assert d["format_time"](0) == "0 s"
    assert d["format_distance"](0) == "0 m"
    assert d["format_time"](-90 / seconds) == "-1.50 min"
    assert d["format_distance"](1.25e6 * d["light_year_metres"] / metres) == "1.25 million ly"
    assert d["format_time"](1, "days").endswith(" days")


def test_csta_g_control_rescales_units_and_horizon_has_no_echo(csta_events_lesson) -> None:
    import runpy

    notebook = runpy.run_path(str(EXAMPLES / "spacetime/conformal_spacetime_events.py"), run_name="csta_2g")
    _, doubled = notebook["app"].run(
        defs={"acceleration_g": SimpleNamespace(value=2.0), "emission_control": SimpleNamespace(value=1.0)}
    )
    assert doubled["time_in"](1) == pytest.approx(csta_events_lesson["time_in"](1) / 2)
    assert doubled["distance_in"](1) == pytest.approx(csta_events_lesson["distance_in"](1) / 2)
    assert doubled["current_t"] == pytest.approx(csta_events_lesson["current_t"])
    assert doubled["current_x"] == pytest.approx(csta_events_lesson["current_x"])
    assert doubled["reception"] is doubled["echo_pair"] is doubled["echo_event"] is None
    doubled["plt"].close("all")


def test_new_example_notebooks_use_v2_facade_teaching_pattern():
    """Check the ledgered gallery uses expression provenance over eager values."""
    for notebook in migrated_notebook_paths(ROOT):
        source = notebook.read_text()
        assert "from galaga import" in source
        assert "from galaga.facade import" not in source
        assert "expr=True" in source or notebook.name == "display_gallery.py"
        assert "import galaga_marimo as gm" in source
        assert ".eval()" not in source
        assert ".reveal()" not in source
        assert "lazy=True" not in source
        assert "symbolic=True" not in source
        assert "repr_unicode=" not in source
        assert "display_repr=" not in source
        assert any(marker in source for marker in ('gm.md(t"""', "gm.md(t'''", 'gm.md(rt"""', "gm.md(rt'''"))
        assert "from galaga.notation import" not in source
        assert 'names="gamma"' not in source
        assert migrate_source(source) == source


def test_derived_circle_derives_ordinary_multivectors_from_widget_coordinates() -> None:
    source = (EXAMPLES / "cga/derived_circle_from_points.py").read_text()

    assert '_px, _py = circle_viz.coordinates("P", default=(-1.75, -0.75))' in source
    assert 'P = circle_cga.up(_px, _py).named("P")' in source
    assert 'C = (P ^ Q ^ R).named("C")' in source
    assert "circle_viz = viz.CGA2D(\n        circle_cga," in source
    assert "import galaga_anywidget.viz as viz" in source
    assert "def _(C, P, Q, R, circle_viz):\n    circle_viz.display(" in source
    assert "mo.vstack([" in source
    assert "circle_viz])" in source
    assert "viz.mutable(" not in source
    assert "mo.state(" not in source
    assert "get_circle_values" not in source
    assert "viz.update(" not in source


def test_circle_circle_meet_keeps_the_dipole_in_ordinary_python() -> None:
    source = (EXAMPLES / "cga/circle_circle_meet.py").read_text()

    assert 'intersection_viz.coordinates("A", default=(-1.0, 0.0))' in source
    assert "circle_a = circle_model.dual(_dual_circle_a).named" in source
    assert 'intersection_dipole = meet(circle_a, circle_b).named("D")' in source
    assert "immutable=[circle_a, circle_b, intersection_dipole]" in source
    assert "circle_model.attitude(intersection_dipole).named(" in source
    assert "circle_model.carrier(intersection_dipole).named(" in source
    assert "circle_model.center(intersection_dipole)" in source
    assert "circle_model.radius_squared(_dipole_center).named(" in source
    assert "circle_model.container(intersection_dipole).named(" in source
    assert "viz.mutable(" not in source
    assert "mo.state(" not in source


def test_direct_and_dual_cga_notebook_uses_one_model_and_explicit_duality() -> None:
    source = (EXAMPLES / "cga/direct_and_dual_representations.py").read_text()

    assert "cga = ConformalModel(conformal_algebra, expr=True)" in source
    assert "C_opns = outer_product(P, Q, R)" in source
    assert "C_ipns = cga.dual(C_opns)" in source
    assert "L_opns = outer_product(P, R, cga.infinity)" in source
    assert "L_ipns = cga.dual(L_opns)" in source
    assert "P_strict_dual = cga.dual(P)" in source
    assert "scalar_product(P, P)" in source
    assert "conformal_algebra.metric_determinant" in source
    assert "representation=" not in source
    assert "with_representation" not in source
    assert ".convert(" not in source


def test_general_gram_compact_notebooks_teach_the_algebraic_boundaries() -> None:
    foundations = (EXAMPLES / "matrix/general_gram_compact_foundations.py").read_text()
    workflow = (EXAMPLES / "matrix/general_gram_compact_workflow.py").read_text()

    assert "## Why the bivector is not an ordered matrix product" in foundations
    assert "outer_product(e1_oblique, e2_oblique)" in foundations
    assert "gamma_1 @ gamma_2 + gamma_2 @ gamma_1" in foundations
    assert 'gram_matrix = MatrixRepr(gram_2d).name(latex=r"G")' in foundations
    assert 'to_matrix(sample_value, mode="compact")' in foundations
    assert "automatic_regular = to_matrix(sample_value)" in foundations
    assert "recovered_sample = from_matrix(explicit_compact)" in foundations

    assert "dense_gram = basis_transform @ orthogonal_metric @ basis_transform.T" in workflow
    assert 'dense_gram_matrix = MatrixRepr(dense_gram).name(latex=r"G")' in workflow
    assert "2.0 * dense_gram[_row, _column]" in workflow
    assert "geometric_product(dense_left, dense_right)" in workflow
    assert 'to_matrix(coefficient_sample, mode="compact")' in workflow
    assert "recovered_coefficients = from_matrix(compact_sample)" in workflow


def test_cga_gram_matrix_notebook_connects_metric_geometry_and_compact_matrices() -> None:
    source = (EXAMPLES / "matrix/cga_via_gram_matrix.py").read_text()

    assert "cga_gram = np.zeros((spatial_dimension + 2, spatial_dimension + 2))" in source
    assert "cga_gram[0, spatial_dimension + 1] = null_pair_scale" in source
    assert 'cga_gram_matrix = MatrixRepr(cga_gram).name(latex=r"G_{\\mathrm{CGA}}")' in source
    assert "ConformalModel(cga_algebra, expr=True)" in source
    assert 'to_matrix(cga_model.origin, mode="compact")' in source
    assert "point_matrix @ point_matrix" in source
    assert "sandwich(translator, conformal_point)" in source
    assert "translator_matrix @ to_matrix(conformal_point" in " ".join(source.split())
    assert "automatic_point_matrix = to_matrix(conformal_point)" in source


def test_construction_notebook_teaches_metric_derived_sta_names_and_signed_lookup() -> None:
    source = (EXAMPLES / "galaga_v2/algebra_construction.py").read_text()
    assert 'p_sta("mostly-minus", sigmas=True, pseudovectors=True)' in source
    assert 'p_sta("mostly-plus", sigmas=True, pseudovectors=True)' in source
    assert "_minus_sigma = _m1 * _m0" in source
    assert "_plus_spatial = _p1 ^ _p2 ^ _p3" in source
    assert 'assert _minus.blade("g0g1") == _native_bivector == -_minus_sigma' in source
    assert 'assert _plus.locals()["ig0"] == _plus.I * _p0' in source
    assert "signature=algebra.basis_squares" in source
    assert "only for an orthogonal frame" in source
    assert "multiple blades or non-unit coefficients" in source


def test_transformation_notebooks_plot_their_computed_subspaces_and_reflections() -> None:
    projectors = (EXAMPLES / "algebra/projectors_ga.py").read_text()
    mirrors = (EXAMPLES / "algebra/rotors_from_reflections.py").read_text()
    assert "_ax.plot_surface(*plane_mesh" in projectors
    assert "(R * e1 * ~R).vector_part" in projectors and "(R * e3 * ~R).vector_part" in projectors
    assert "Gram matrix restricted to its spanning subspace" in " ".join(projectors.split())
    assert "_n1 = -np.sin(_a) * e1 + np.cos(_a) * e2" in mirrors
    assert "_n2 = -np.sin(_b) * e1 + np.cos(_b) * e2" in mirrors
    assert "_y = reflected_twice.vector_part" in mirrors
    assert "_once = reflected_once.vector_part" in mirrors
    assert "it does not substitute an inverse" in mirrors


def test_quaternion_notebook_teaches_computed_units_even_grades_and_metric_boundaries() -> None:
    source = (EXAMPLES / "basics/complex_and_quaternions.py").read_text()
    assert "_expected_units = (_e2 ^ _e3, _e1 ^ _e3, _e1 ^ _e2)" in source
    assert "assert (i, j, k) == _expected_units" in source
    assert "assert i * j == k and j * k == i and k * i == j" in source
    assert "assert _native == (k, j, i)" in source
    assert "assert reverse(_z) == conjugate(_z) == 3 - 4 * _i" in source
    assert "assert _reversed - _conjugated == 10 * _e1" in source
    assert "_square = _gram[1, 2] ** 2 - _gram[1, 1] * _gram[2, 2]" in source
    assert "assert _blade * _blade == _square" in source
    assert "assert _named_i == _blade" in source
    assert "$${_square_latex!s}.$$" in source
    assert "the bivectors alone are not closed under multiplication" in source


def test_presentation_notebook_teaches_signed_locals_and_explicit_symbol_replay() -> None:
    source = (EXAMPLES / "galaga_v2/presentation_contexts.py").read_text()
    assert "_reverse_plane = _e2 ^ _e1" in source
    assert "_ref = BladeRef(_mask, int(_reverse_plane.data[_mask]))" in source
    assert 'LocalNamePolicy(algebra.n, {"x": 1, "y": 2, "plane": _ref})' in source
    assert "_signed.mask.bit_count() == 2" in source
    assert 'assert _view.with_local_names(_bivectors).locals()["plane"] == _reverse_plane' in source
    assert "evaluate(_mixed.expr, algebra=_view, environment=_bindings) == _mixed" in source
    assert "evaluate(_literal.expr, algebra=_view) == _plane" in source
    assert "neither sanitizes names nor compacts products" in source
    assert "later operations on them record symbolic provenance" in source
    for name in ("plane", "mixed", "literal"):
        assert f'_{name}_latex = _{name}.latex(content="full")' in source
        assert "$${_" + name + "_latex!s}.$$" in source


def test_rga_notebook_teaches_signed_storage_zero_grades_and_custom_underaccents() -> None:
    source = (EXAMPLES / "rga/rga_demo.py").read_text()
    assert '_oriented = rga.blade("e31", expr=True)' in source
    assert "_native = rga.blade(0b0101, expr=True)" in source
    assert "assert _oriented == -_native" in source
    assert "rga.n - _mask.bit_count()" in source
    assert "assert _result == _expected" in source
    assert 'RenderRule("underaccent", symbol=Name("sim", "\\u0330", r"\\sim"))' in source
    assert '_result.display("full/latex", notation=_fallback)' in source
    assert "assert _zero.homogeneous_grade() is None" in source
    assert 'assert _zero.expr.parameters == (("order", 1),)' in source


def test_custom_notation_notebook_teaches_unit_fraction_and_target_consistent_reverse() -> None:
    source = (EXAMPLES / "galaga_v2/custom_functional_notation.py").read_text()
    assert r'Name.from_latex(r"\hat{B}")' in source
    assert '"unit", RenderRule("unit_fraction")' in source
    assert 'display("full/latex", notation=_fraction_notation)' in source
    assert 'display("expr/latex", notation=Notation.hestenes())' in source
    assert "assert reverse(_B) == -_B" in source
    assert 'assert _normalized.expr.operation_id == "unit"' in source
    assert "non-default normalization tolerance" in source
    assert "Zero-norm inputs still fail eagerly" in source


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
def test_migrated_notebooks_pass_marimo_dependency_validation() -> None:
    """Reject invalid cross-cell definitions and dependencies in the gallery."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "marimo",
            "check",
            "--quiet",
            *(str(notebook) for notebook in migrated_notebook_paths(ROOT)),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
def test_migrated_notebooks_execute_headlessly(tmp_path: Path) -> None:
    """Execute every ledgered notebook through Marimo's headless runtime."""
    source_paths = _notebook_import_paths()
    environment = os.environ.copy()
    inherited = environment.get("PYTHONPATH")
    if inherited:
        source_paths.extend(inherited.split(os.pathsep))
    environment["PYTHONPATH"] = os.pathsep.join(source_paths)

    def execute(notebook: Path) -> tuple[str, subprocess.CompletedProcess[str]]:
        relative = notebook.relative_to(ROOT).as_posix()
        output = tmp_path / f"{relative.replace('/', '-')}.html"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "marimo",
                "export",
                "html",
                str(notebook),
                "--no-include-code",
                "--force",
                "-o",
                str(output),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        return relative, result

    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(execute, notebook) for notebook in migrated_notebook_paths(ROOT)]
        for future in as_completed(futures):
            relative, result = future.result()
            if result.returncode:
                failures.append(f"{relative}:\n{result.stdout}{result.stderr}")

    assert not failures, "\n\n".join(sorted(failures))


def _notebook_import_paths() -> list[str]:
    """Keep subprocesses on the same installed/source packages as this test."""
    paths = [str(ROOT)]
    for name in (
        "galaga",
        "galaga_annotation",
        "galaga_anywidget",
        "galaga_marimo",
        "galaga_matrix",
        "galaga_mermaid",
    ):
        spec = find_spec(name)
        if spec is None or spec.origin is None:
            raise ImportError(f"notebook integration requires {name}")
        paths.append(str(Path(spec.origin).resolve().parent.parent))
    return list(dict.fromkeys(paths))


def test_notebook_subprocess_paths_follow_installed_packages_not_repository_fallbacks(monkeypatch, tmp_path):
    site = tmp_path / "site-packages"
    monkeypatch.setattr(
        sys.modules[__name__], "find_spec", lambda name: SimpleNamespace(origin=str(site / name / "__init__.py"))
    )
    assert _notebook_import_paths() == [str(ROOT), str(site)]


@pytest.mark.parametrize("spec", (None, SimpleNamespace(origin=None)))
def test_notebook_subprocess_paths_reject_missing_or_namespace_dependencies(monkeypatch, spec):
    monkeypatch.setattr(sys.modules[__name__], "find_spec", lambda name: spec)
    with pytest.raises(ImportError, match="notebook integration requires galaga"):
        _notebook_import_paths()
