from __future__ import annotations

import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOINT_PACKAGES = (
    "galaga",
    "galaga_anywidget",
    "galaga_marimo",
    "galaga_matrix",
)


def _metadata(package: str) -> dict[str, object]:
    return tomllib.loads((ROOT / "packages" / package / "pyproject.toml").read_text())


def test_joint_release_packages_share_a_version_and_core_dependency_floor() -> None:
    projects = {package: _metadata(package)["project"] for package in JOINT_PACKAGES}
    galaga_version = projects["galaga"]["version"]

    assert {project["version"] for project in projects.values()} == {galaga_version}
    for package in JOINT_PACKAGES[1:]:
        assert f"galaga>={galaga_version}" in projects[package]["dependencies"]


def test_release_workflow_tests_builds_checks_and_publishes_anywidget() -> None:
    release = (ROOT / "scripts" / "release.sh").read_text()

    assert "packages/galaga_anywidget/tests/" in release
    assert "uv build --package galaga-anywidget --out-dir packages/galaga_anywidget/dist" in release
    assert "twine check packages/galaga_anywidget/dist/galaga_anywidget-*" in release
    assert "uv publish packages/galaga_anywidget/dist/galaga_anywidget-*" in release


def test_marimo_launcher_supplies_widget_and_markdown_packages_separately() -> None:
    makefile = (ROOT / "Makefile").read_text()

    assert "--with-editable ./packages/galaga_anywidget" in makefile
    assert "--with-editable ./packages/galaga_marimo" in makefile


def test_anywidget_has_a_guarded_standalone_publish_path() -> None:
    script_path = ROOT / "scripts" / "publish-galaga-anywidget.sh"
    script = script_path.read_text()

    assert os.access(script_path, os.X_OK)
    assert 'source "$SCRIPT_DIR/publish-guard.sh"' in script
    assert '--test) PUBLISH_URL="https://test.pypi.org/legacy/"' in script
    assert 'uv build --package galaga-anywidget --out-dir "$PKG/dist"' in script
    assert 'uvx twine check "$PKG/dist"/galaga_anywidget-*' in script


def test_python_formatter_leaves_markdown_to_the_markdown_linter() -> None:
    lint = (ROOT / "scripts" / "lint.sh").read_text()

    assert lint.count("--extend-exclude '*.md'") == 2
    assert "rumdl" in lint
