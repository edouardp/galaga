import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest
from tools.migrate_v2_notebooks import MIGRATED_NOTEBOOKS, migrate_source

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"


def test_new_example_notebooks_compile():
    """Verify every listed example notebook is valid Python and has marimo boilerplate."""
    for notebook in MIGRATED_NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
        if sys.version_info >= (3, 14):
            compile(source, str(EXAMPLES / notebook), "exec")
        else:
            assert "app = marimo.App(" in source
            assert '__generated_with = "' in source


def test_new_example_notebooks_use_v2_facade_teaching_pattern():
    """Check the ledgered gallery uses expression provenance over eager values."""
    for notebook in MIGRATED_NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
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
            *(str(EXAMPLES / notebook) for notebook in MIGRATED_NOTEBOOKS),
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
    source_paths = [
        str(ROOT),
        str(ROOT / "packages" / "galaga"),
        str(ROOT / "packages" / "galaga_anywidget"),
        str(ROOT / "packages" / "galaga_marimo"),
        str(ROOT / "packages" / "galaga_matrix"),
        str(ROOT / "packages" / "galaga_mermaid"),
    ]
    environment = os.environ.copy()
    inherited = environment.get("PYTHONPATH")
    if inherited:
        source_paths.extend(inherited.split(os.pathsep))
    environment["PYTHONPATH"] = os.pathsep.join(source_paths)

    def execute(relative: str) -> tuple[str, subprocess.CompletedProcess[str]]:
        output = tmp_path / f"{relative.replace('/', '-')}.html"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "marimo",
                "export",
                "html",
                str(EXAMPLES / relative),
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
        futures = [pool.submit(execute, notebook) for notebook in MIGRATED_NOTEBOOKS]
        for future in as_completed(futures):
            relative, result = future.result()
            if result.returncode:
                failures.append(f"{relative}:\n{result.stdout}{result.stderr}")

    assert not failures, "\n\n".join(sorted(failures))
