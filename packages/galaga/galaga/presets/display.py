"""Sparse display overrides for presentation composition."""

from __future__ import annotations

from ..presentation import DisplayPolicy as _DisplayPolicy

__all__ = ["override"]


def override(
    *,
    content: str | None = None,
    target: str | None = None,
    zero_tolerance: float | None = None,
    coefficient_precision: int | None = None,
) -> _DisplayPolicy:
    """Change only the supplied display choices of an algebra or presenter."""
    return _DisplayPolicy(
        content=content,
        target=target,
        zero_tolerance=zero_tolerance,
        coefficient_precision=coefficient_precision,
    )


def __dir__() -> list[str]:
    return list(__all__)
