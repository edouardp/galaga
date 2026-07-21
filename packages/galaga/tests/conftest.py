"""Phase 8 test boundary between the public facade and explicit v1 oracle."""

from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any

import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

_TEST_ROOT = Path(__file__).parent
_LEGACY_ORACLE_TEST_SET = frozenset(LEGACY_ORACLE_TESTS)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "legacy_oracle: deliberately executes the Galaga 1 implementation during the Phase 8 shadow cutover",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path = Path(str(item.path)).resolve()
        try:
            relative = path.relative_to(_TEST_ROOT.resolve()).as_posix()
        except ValueError:
            continue
        if relative in _LEGACY_ORACLE_TEST_SET:
            item.add_marker(pytest.mark.legacy_oracle)


@pytest.fixture(autouse=True)
def reject_unledgered_legacy_numeric_construction(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Make new tests facade-only unless the executable ledger opts them in."""
    if request.node.get_closest_marker("legacy_oracle") is not None:
        return

    import galaga.legacy as legacy

    original_algebra_init = legacy.Algebra.__init__
    original_multivector_init = legacy.Multivector.__init__

    @wraps(original_algebra_init)
    def reject_algebra(*args: Any, **kwargs: Any) -> None:
        raise AssertionError(
            "unledgered test constructed a Galaga 1 numeric object; "
            "use the public Galaga 2 API or add a reviewed legacy-oracle ledger entry"
        )

    @wraps(original_multivector_init)
    def reject_multivector(*args: Any, **kwargs: Any) -> None:
        raise AssertionError(
            "unledgered test constructed a Galaga 1 numeric object; "
            "use the public Galaga 2 API or add a reviewed legacy-oracle ledger entry"
        )

    monkeypatch.setattr(legacy.Algebra, "__init__", reject_algebra)
    monkeypatch.setattr(legacy.Multivector, "__init__", reject_multivector)
