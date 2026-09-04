from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path

import galaga_anywidget

PACKAGES = Path(__file__).resolve().parents[2]


def test_public_widget_api_is_owned_by_galaga_anywidget() -> None:
    assert galaga_anywidget.CGA2D is galaga_anywidget.viz.CGA2D
    assert galaga_anywidget.CGA2DPlot.__module__ == "galaga_anywidget.cga2d"


def test_galaga_marimo_does_not_depend_on_or_export_the_widget() -> None:
    marimo_package = PACKAGES / "galaga_marimo"
    metadata = tomllib.loads((marimo_package / "pyproject.toml").read_text())
    package_source = (marimo_package / "galaga_marimo" / "__init__.py").read_text()

    dependencies = metadata["project"]["dependencies"]
    assert all(not dependency.startswith(("anywidget", "traitlets", "galaga-anywidget")) for dependency in dependencies)
    assert "CGA2D" not in package_source
    assert "from . import viz" not in package_source


def test_widget_assets_are_packaged_as_resources() -> None:
    static = importlib.resources.files("galaga_anywidget") / "static"

    assert (static / "cga2d.js").is_file()
    assert (static / "cga2d.css").is_file()
