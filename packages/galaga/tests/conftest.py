"""Reject retired imports before collection and during execution."""

from __future__ import annotations

import pytest
from tools.legacy_import_boundary import assert_no_legacy_modules, install_import_guard, remove_import_guard


def pytest_configure(config: pytest.Config) -> None:
    guard = install_import_guard()
    config.add_cleanup(lambda: remove_import_guard(guard))


def pytest_collection_finish(session: pytest.Session) -> None:
    assert_no_legacy_modules()


@pytest.fixture(autouse=True)
def reject_cached_legacy_modules():
    """Check both sides of each test, including dependent fixture teardown."""
    assert_no_legacy_modules()
    yield
    assert_no_legacy_modules()


@pytest.fixture(autouse=True)
def isolate_user_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep repository tests independent of a developer's personal YAML file."""
    monkeypatch.setenv("GALAGA_CONFIG", "none")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    assert_no_legacy_modules()
