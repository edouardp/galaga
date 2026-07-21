"""Safety tests for the Phase 8 legacy-test isolation codemod."""

from pathlib import Path

import pytest
from tools.isolate_phase8_legacy_tests import isolate_path, isolate_source


def test_only_actual_top_level_galaga_imports_move_to_legacy() -> None:
    source = """\
from galaga import Algebra, reverse
from galaga.facade import DisplayPolicy
from galaga.algebra import _private_oracle

# from galaga import Multivector
EXAMPLE = "from galaga import outer_product"
"""

    isolated = isolate_source(source)

    assert "from galaga.legacy import Algebra, reverse" in isolated
    assert "from galaga.facade import DisplayPolicy" in isolated
    assert "from galaga.algebra import _private_oracle" in isolated
    assert "# from galaga import Multivector" in isolated
    assert 'EXAMPLE = "from galaga import outer_product"' in isolated


def test_isolation_is_idempotent() -> None:
    source = "from galaga import Algebra\n"
    isolated = isolate_source(source)

    assert isolate_source(isolated) == isolated


def test_path_guard_rejects_unledgered_and_outside_tests(tmp_path: Path) -> None:
    tests_root = tmp_path / "tests"
    unledgered = tests_root / "unledgered.py"
    unledgered.parent.mkdir()
    unledgered.write_text("from galaga import Algebra\n")

    with pytest.raises(ValueError, match="not in the Phase 8"):
        isolate_path(unledgered, tests_root=tests_root, check=False)
    with pytest.raises(ValueError, match="outside"):
        isolate_path(tmp_path / "outside.py", tests_root=tests_root, check=False)
