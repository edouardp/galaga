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


def test_spinor_ideals_lesson_is_in_the_executable_gallery():
    assert EXAMPLES / "matrix/spinors_ideals_and_chirality.py" in migrated_notebook_paths(ROOT)


def test_new_example_notebooks_use_v2_facade_teaching_pattern():
    """Check the ledgered gallery uses expression provenance over eager values."""
    for notebook in migrated_notebook_paths(ROOT):
        source = notebook.read_text()
        assert "from galaga import" in source
        assert "from galaga.facade import" not in source
        assert "expr=True" in source
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
    for name in ("galaga", "galaga_anywidget", "galaga_marimo", "galaga_matrix", "galaga_mermaid"):
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
