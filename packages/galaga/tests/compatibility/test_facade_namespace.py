"""Namespace and import-boundary contracts during the facade promotion."""

from __future__ import annotations

import ast
import runpy
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
from tools.legacy_import_boundary import is_legacy_module

ARCHITECTURE = runpy.run_path(str(Path(__file__).parents[1] / "facade/test_architecture_contracts.py"))


@pytest.mark.parametrize(
    "imports",
    (
        "import galaga.core; import galaga.facade; import galaga",
        "import galaga; import galaga.facade; import galaga.core",
    ),
    ids=("core-facade-public", "public-facade-core"),
)
def test_core_facade_and_public_api_import_in_either_order(imports: str) -> None:
    program = f"""
from tools.legacy_import_boundary import install_import_guard, assert_no_legacy_modules
install_import_guard()
{imports}
assert galaga.Algebra is galaga.facade.Algebra
assert galaga.OPERATIONS is galaga.facade.OPERATIONS
assert galaga.facade.Algebra(2).numeric.__class__ is galaga.core.Algebra
assert_no_legacy_modules()
"""

    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


def test_facade_implementation_has_no_outer_layer_imports() -> None:
    """Planned v2 presentation/expression imports are allowed; retired layers are not."""
    sources = list(ARCHITECTURE["python_sources"](files("galaga.facade"), "galaga.facade"))
    assert sources
    for module, package, source in sources:
        forbidden = [
            (line, name) for line, name in ARCHITECTURE["galaga_imports"](source, package) if is_legacy_module(name)
        ]
        assert not forbidden, (module, forbidden)


def test_facade_does_not_read_private_core_product_tables() -> None:
    for module, _package, source in ARCHITECTURE["python_sources"](files("galaga.facade"), "galaga.facade"):
        attributes = {node.attr for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Attribute)}
        assert attributes.isdisjoint({"_mul_index", "_mul_sign"}), module


def test_core_has_no_import_edge_to_any_outer_galaga_layer() -> None:
    for _module, package, source in ARCHITECTURE["python_sources"](files("galaga.core"), "galaga.core"):
        ARCHITECTURE["assert_core_only_imports"](source, package)
