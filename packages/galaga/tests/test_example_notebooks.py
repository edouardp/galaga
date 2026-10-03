"""Smoke-check the editable Marimo gallery without policing lesson content."""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"
MARIMO_MARKER = "app = marimo.App("


def notebook_paths() -> tuple[Path, ...]:
    """Discover notebooks so new examples need no test inventory update."""
    gallery = (
        path
        for path in EXAMPLES.rglob("*.py")
        if "legacy" not in path.relative_to(EXAMPLES).parts and MARIMO_MARKER in path.read_text()
    )
    root_notebooks = (path for path in ROOT.glob("*.py") if MARIMO_MARKER in path.read_text())
    return tuple(sorted((*gallery, *root_notebooks)))


def _notebook_environment() -> dict[str, str]:
    environment = os.environ.copy()
    source_paths = [str(ROOT)]
    for name in (
        "galaga",
        "galaga_annotation",
        "galaga_anywidget",
        "galaga_marimo",
        "galaga_matrix",
        "galaga_mermaid",
    ):
        source_paths.append(str(ROOT / "packages" / name))
    inherited = environment.get("PYTHONPATH")
    if inherited:
        source_paths.extend(inherited.split(os.pathsep))
    environment["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(source_paths))
    return environment


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
def test_notebooks_compile_and_pass_marimo_check() -> None:
    paths = notebook_paths()
    assert paths
    for path in paths:
        compile(path.read_text(), str(path), "exec")
    result = subprocess.run(
        [sys.executable, "-m", "marimo", "check", "--quiet", *(str(path) for path in paths)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Marimo t-strings require Python 3.14")
def test_notebooks_execute_headlessly(tmp_path: Path) -> None:
    paths = notebook_paths()
    environment = _notebook_environment()

    def execute(path: Path) -> tuple[str, subprocess.CompletedProcess[str]]:
        relative = path.relative_to(ROOT).as_posix()
        output = tmp_path / f"{relative.replace('/', '-')}.html"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "marimo",
                "export",
                "html",
                str(path),
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

    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(execute, path) for path in paths]
        for future in as_completed(futures):
            relative, result = future.result()
            if result.returncode:
                detail = result.stdout + result.stderr
                errors = [line for line in detail.splitlines() if "MarimoExceptionRaisedError:" in line]
                failures.append(f"{relative}: {errors[0] if errors else detail[-500:]}")
    assert not failures, "\n\n".join(sorted(failures))
