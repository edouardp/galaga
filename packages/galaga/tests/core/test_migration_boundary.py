"""Architectural guards for the additive numeric-core migration."""

from __future__ import annotations

import ast
from importlib.metadata import requires
from pathlib import Path

import galaga.core as core
import galaga.facade as facade
import galaga.legacy as legacy
from galaga import Algebra as PublicAlgebra


def test_top_level_algebra_is_the_promoted_facade() -> None:
    """Phase 8 makes the core-backed facade the ordinary public API."""
    assert PublicAlgebra is not core.Algebra
    assert PublicAlgebra is facade.Algebra
    assert PublicAlgebra is not legacy.Algebra
    assert PublicAlgebra.__module__ == "galaga.facade._numeric"
    assert core.Algebra.__module__ == "galaga.core"


def test_core_source_does_not_import_outer_galaga_modules() -> None:
    """The numeric core may import within its package but never outward."""
    core_directory = Path(core.__file__).parent

    for source_path in core_directory.glob("*.py"):
        tree = ast.parse(source_path.read_text(), filename=str(source_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
                assert not any(name == "galaga" or name.startswith("galaga.") for name in imported), (
                    f"{source_path.name} imports outward: {imported}"
                )
            elif isinstance(node, ast.ImportFrom):
                assert node.level <= 1, (
                    f"{source_path.name} escapes galaga.core with {'.' * node.level}{node.module or ''}"
                )
                assert not (
                    node.level == 0
                    and node.module is not None
                    and (node.module == "galaga" or node.module.startswith("galaga."))
                ), f"{source_path.name} imports outward from {node.module}"


def test_distribution_has_no_external_gram_dependency() -> None:
    """The core is part of Galaga's distribution rather than another package."""
    requirements = requires("galaga") or []
    assert not any(requirement.lower().startswith("gram") for requirement in requirements)
