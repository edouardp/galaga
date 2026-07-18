"""Namespace and import-boundary contracts during the facade promotion."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "imports",
    (
        "import galaga.core; import galaga.facade; import galaga.gram_bridge",
        "import galaga.gram_bridge; import galaga.facade; import galaga.core",
    ),
    ids=("core-facade-bridge", "bridge-facade-core"),
)
def test_core_facade_and_bridge_import_in_either_order(imports: str) -> None:
    program = f"""
{imports}
assert galaga.gram_bridge.Algebra is galaga.facade.Algebra
assert galaga.gram_bridge.OPERATIONS is galaga.facade.OPERATIONS
assert galaga.facade.Algebra(2).numeric.__class__ is galaga.core.Algebra
"""

    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_facade_implementation_has_no_outer_layer_imports() -> None:
    import ast

    import galaga.facade as facade_package

    forbidden = {"expr", "notation", "render", "symbolic"}
    imported: set[str] = set()
    package_path = Path(facade_package.__file__).parent
    for source_path in package_path.glob("*.py"):
        tree = ast.parse(source_path.read_text())
        imported.update(
            alias.name.removeprefix("galaga.").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module:
                imported.add(node.module.removeprefix("galaga.").split(".")[0])
            else:
                imported.update(alias.name.split(".")[0] for alias in node.names)

    assert forbidden.isdisjoint(imported)


def test_facade_does_not_read_private_core_product_tables() -> None:
    import galaga.facade as facade_package

    package_path = Path(facade_package.__file__).parent
    implementation = "\n".join(path.read_text() for path in package_path.glob("*.py"))

    assert "._mul_index" not in implementation
    assert "._mul_sign" not in implementation


def test_core_has_no_import_edge_to_any_outer_galaga_layer() -> None:
    import ast

    import galaga.core as core_package

    forbidden = {"algebra", "expr", "facade", "gram_bridge", "notation", "render", "symbolic"}
    violations: list[str] = []
    package_path = Path(core_package.__file__).parent
    for source_path in package_path.glob("*.py"):
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    if len(parts) > 1 and parts[0] == "galaga" and parts[1] in forbidden:
                        violations.append(f"{source_path.name}:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.level >= 2:
                    violations.append(f"{source_path.name}:relative-level-{node.level}")
                elif node.module and node.module.startswith("galaga."):
                    owner = node.module.split(".")[1]
                    if owner in forbidden:
                        violations.append(f"{source_path.name}:{node.module}")

    assert violations == []
