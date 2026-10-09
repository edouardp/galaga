"""Import ordering and numeric storage encapsulation."""

from __future__ import annotations

import ast
import runpy
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

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
{imports}
assert galaga.Algebra is galaga.facade.Algebra
assert galaga.OPERATIONS is galaga.facade.OPERATIONS
assert galaga.facade.Algebra(2).numeric.__class__ is galaga.core.Algebra
"""

    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


def test_facade_does_not_read_private_core_product_tables() -> None:
    for module, _package, source in ARCHITECTURE["python_sources"](files("galaga.facade"), "galaga.facade"):
        attributes = {node.attr for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Attribute)}
        assert attributes.isdisjoint({"_mul_index", "_mul_sign"}), module
