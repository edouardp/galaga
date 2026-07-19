"""Executable smoke gate for the maintained Galaga 2 examples."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
EXAMPLES = ROOT / "examples/v2"
MAINTAINED_V2_EXAMPLES = tuple(sorted(EXAMPLES.glob("*.py")))


@pytest.mark.parametrize("path", MAINTAINED_V2_EXAMPLES, ids=lambda path: path.name)
def test_maintained_v2_example_executes(path: Path) -> None:
    namespace = runpy.run_path(str(path))

    namespace["run"]()


def test_v2_example_inventory_is_nonempty_and_uses_explicit_architecture_imports() -> None:
    assert MAINTAINED_V2_EXAMPLES
    for path in MAINTAINED_V2_EXAMPLES:
        source = path.read_text()
        assert "from galaga import" not in source
        assert "._" not in source
        assert "from galaga.core import" in source or "from galaga.facade import" in source
