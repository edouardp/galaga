"""Architecture guards for package-private annotation implementation APIs."""

from __future__ import annotations

import ast
from pathlib import Path

import galaga_annotation as ga

PACKAGE = Path(ga.__file__).resolve().parent


def test_modules_do_not_import_private_names_from_siblings() -> None:
    violations: list[str] = []
    for source in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(source.read_text(), filename=str(source))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level == 0:
                continue
            for alias in node.names:
                if alias.name.startswith("_"):
                    violations.append(f"{source.name}:{node.lineno} imports {alias.name}")
    assert violations == []


def test_internal_decoration_helpers_are_not_public_package_api() -> None:
    assert not hasattr(ga, "decorate")
    assert not hasattr(ga, "default_side")
    assert not hasattr(ga, "external_parts")
    assert not hasattr(ga, "style_body")
