"""Phase 9 tests reject retired imports before collection and during execution."""

from __future__ import annotations

import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS
from tools.legacy_import_boundary import assert_no_legacy_modules, install_import_guard, remove_import_guard


def pytest_configure(config: pytest.Config) -> None:
    if LEGACY_ORACLE_TESTS:
        raise pytest.UsageError("Phase 9 requires an empty legacy-construction ledger")
    guard = install_import_guard()
    config.add_cleanup(lambda: remove_import_guard(guard))
    config.addinivalue_line(
        "markers",
        "legacy_oracle: retired Phase 8 marker; its use now fails collection",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    marked = [item.nodeid for item in items if item.get_closest_marker("legacy_oracle") is not None]
    if marked:
        raise pytest.UsageError(f"legacy_oracle markers are retired: {', '.join(marked)}")


def pytest_collection_finish(session: pytest.Session) -> None:
    assert_no_legacy_modules()


@pytest.fixture(autouse=True)
def reject_cached_legacy_modules():
    """Check both sides of each test, including dependent fixture teardown."""
    assert_no_legacy_modules()
    yield
    assert_no_legacy_modules()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    assert_no_legacy_modules()
