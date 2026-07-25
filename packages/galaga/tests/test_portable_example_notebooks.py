"""Contracts for repository-independent Marimo notebook source."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
from tools.portable_notebooks import make_notebook_portable, make_path_portable

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"
_MARIMO_APP_MARKER = "app = marimo.App"
_MARIMO_GENERATOR = '__generated_with = "0.23.14"'


def _marimo_notebooks() -> list[Path]:
    return sorted(path for path in EXAMPLES.rglob("*.py") if _MARIMO_APP_MARKER in path.read_text())


def test_path_bootstrap_removal_is_structural_and_idempotent() -> None:
    source = """\
import marimo

app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    root = str(Path(__file__).parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    return


@app.cell
def _():
    import galaga
    return (galaga,)
"""

    portable = make_notebook_portable(source)

    assert "import sys" not in portable
    assert "sys.path" not in portable
    assert "import galaga" in portable
    assert make_notebook_portable(portable) == portable


def test_path_guard_rejects_non_notebooks_and_paths_outside_examples(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    example = repository / "examples" / "ordinary.py"
    example.parent.mkdir(parents=True)
    example.write_text("print('not a Marimo notebook')\n")

    with pytest.raises(ValueError, match="non-Marimo"):
        make_path_portable(example, repository=repository, check=False)

    outside = tmp_path / "outside.py"
    outside.write_text("app = marimo.App()\n")
    with pytest.raises(ValueError, match="outside"):
        make_path_portable(outside, repository=repository, check=False)


def test_all_marimo_notebooks_are_repository_independent() -> None:
    notebooks = _marimo_notebooks()

    assert notebooks
    for notebook in notebooks:
        source = notebook.read_text()
        assert _MARIMO_GENERATOR in source, notebook
        assert "sys.path" not in source, notebook
        assert "Path(__file__)" not in source, notebook
        assert make_notebook_portable(source) == source, notebook


def test_run_marimo_uses_local_editable_packages_without_notebook_path_mutation() -> None:
    result = subprocess.run(
        ["make", "--no-print-directory", "--dry-run", "run-marimo"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    command = re.sub(r"\\\n\\s*", " ", result.stdout)

    assert "uv run --python 3.14" in command
    for package in ("galaga", "galaga_marimo", "galaga_matrix", "galaga_mermaid"):
        assert f"--with-editable ./packages/{package}" in command
    assert "marimo edit --no-token examples" in command
    assert "PYTHONPATH" not in command
