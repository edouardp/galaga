"""Small public namespace for complete and blade-only algebra presets."""

from __future__ import annotations

from typing import Any as _Any

from . import notation as notation
from ._implementation import (
    blades,
    cga,
    complex,
    euclidean,
    exterior,
    lengyel_cga,
    pga,
    quaternion,
    rga,
    sta,
)

__all__ = [
    "blades",
    "cga",
    "complex",
    "euclidean",
    "exterior",
    "lengyel_cga",
    "notation",
    "pga",
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
    "PGAPreset",
    "Preset",
    "QuaternionPreset",
    "SpacetimePreset",
    "p_cga",
    "p_complex",
    "p_euclidean",
    "p_exterior",
    "p_lengyel_cga",
    "p_pga",
    "p_quaternion",
    "p_rga",
    "p_sta",
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
