"""Isolate developer preferences from repository tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolate_user_configuration(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """Keep repository tests independent of a developer's global TOML file."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
