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
            assert "app = marimo.App()" in source
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
        assert 'gm.md(rt"""' in source or "gm.md(rt'''" in source
        assert "from galaga.notation import" not in source
        assert 'names="gamma"' not in source
        assert migrate_source(source) == source


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
        str(ROOT / "packages" / "galaga_marimo"),
        str(ROOT / "packages" / "galaga_matrix"),
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
