"""Small public namespace for complete and blade-only algebra presets."""

from __future__ import annotations

from typing import Any as _Any

from . import display as display
from . import notation as notation
from . import presenters as presenters
from ._implementation import (
    blades,
    cga,
    complex,
    euclidean,
    exterior,
    lengyel_cga,
    oblique_plane,
    pga,
    quaternion,
    rga,
    sta,
)

__all__ = [
    "blades",
    "cga",
    "complex",
    "display",
    "euclidean",
    "exterior",
    "lengyel_cga",
    "notation",
    "oblique_plane",
    "pga",
    "presenters",
    "quaternion",
    "rga",
    "sta",
]

_COMPATIBILITY_NAMES = {
    "BladePreset",
    "CGAPreset",
    "ComplexPreset",
    "EuclideanPreset",
    "ExteriorPreset",
    "LengyelCGAPreset",
    "LengyelRGAPreset",
    "ObliquePlanePreset",
    "PGAPreset",
    "Preset",
    "QuaternionPreset",
    "SpacetimePreset",
}


def __dir__() -> list[str]:
    """Advertise only the concise public recipe surface."""
    return list(__all__)


def __getattr__(name: str) -> _Any:
    """Resolve old explicit imports without advertising them to completion."""
    if name in _COMPATIBILITY_NAMES:
        from . import _implementation

        return getattr(_implementation, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
