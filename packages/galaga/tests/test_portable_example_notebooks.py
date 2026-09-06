"""Contracts for repository-independent Marimo notebook source."""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

import pytest
from tools.portable_notebooks import make_notebook_portable, make_path_portable

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"
_MARIMO_APP_MARKER = "app = marimo.App"
_MARIMO_GENERATOR = re.compile(r"""^__generated_with = (["'])[^"'\r\n]+\1$""", re.MULTILINE)


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


@pytest.mark.parametrize("version", ("0.23.14", "0.24.0", "0.24.1.dev1"))
def test_portable_notebooks_preserve_their_own_generator_metadata(version: str) -> None:
    source = f"import marimo\n\n__generated_with = {version!r}\napp = marimo.App()\n"

    assert _MARIMO_GENERATOR.search(source)
    assert make_notebook_portable(source) == source


@pytest.mark.parametrize(
    "metadata",
    ('__generated_with = ""', "__generated_with = 23", '# __generated_with = "0.24.0"', ""),
)
def test_generator_metadata_must_be_a_nonempty_string_assignment(metadata: str) -> None:
    source = f"import marimo\n\n{metadata}\napp = marimo.App()\n"

    assert _MARIMO_GENERATOR.search(source) is None


def test_all_marimo_notebooks_are_repository_independent() -> None:
    notebooks = _marimo_notebooks()

    assert notebooks
    for notebook in notebooks:
        source = notebook.read_text()
        assert _MARIMO_GENERATOR.search(source), notebook
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
    command = shlex.split(result.stdout.replace("\\\n", " "))
    option_pairs = set(zip(command, command[1:]))

    assert command[:2] == ["uv", "run"]
    assert ("--python", "3.14") in option_pairs
    for package in ("galaga", "galaga_anywidget", "galaga_marimo", "galaga_matrix", "galaga_mermaid"):
        assert ("--with-editable", f"./packages/{package}") in option_pairs
    launcher = command[command.index("marimo") :]
    assert launcher[:2] == ["marimo", "edit"]
    assert set(launcher[2:-1]) == {"--watch", "--no-token"}
    assert launcher[-1] == "examples"
    assert "PYTHONPATH" not in result.stdout
