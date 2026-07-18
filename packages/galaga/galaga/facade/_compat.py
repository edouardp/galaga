"""Audited Galaga 2 compatibility adapters with removal guidance."""

from __future__ import annotations

import warnings
from types import MappingProxyType

from ._numeric import Multivector, grade_involution, norm2, unit


class GalagaDeprecationWarning(DeprecationWarning):
    """A migration warning for a public Galaga spelling scheduled for removal."""


DEPRECATED_OPERATION_ALIASES = MappingProxyType(
    {
        "involute": "grade_involution",
        "mag2": "norm2",
        "magnitude_squared": "norm2",
        "normalise": "unit",
        "normalize": "unit",
        "norm_squared": "norm2",
    }
)
"""Temporary function spelling to canonical operation ID."""


def _warn(alias: str) -> None:
    canonical = DEPRECATED_OPERATION_ALIASES[alias]
    warnings.warn(
        f"{alias} is deprecated in Galaga 2; use {canonical}",
        GalagaDeprecationWarning,
        stacklevel=3,
    )


def involute(value: Multivector) -> Multivector:
    """Deprecated compatibility spelling for :func:`grade_involution`."""
    _warn("involute")
    return grade_involution(value)


def mag2(value: Multivector) -> Multivector:
    """Deprecated compatibility spelling for :func:`norm2`."""
    _warn("mag2")
    return norm2(value)


def magnitude_squared(value: Multivector) -> Multivector:
    """Deprecated compatibility spelling for :func:`norm2`."""
    _warn("magnitude_squared")
    return norm2(value)


def norm_squared(value: Multivector) -> Multivector:
    """Deprecated compatibility spelling for :func:`norm2`."""
    _warn("norm_squared")
    return norm2(value)


def normalise(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    """Deprecated British compatibility spelling for :func:`unit`."""
    _warn("normalise")
    return unit(value, atol=atol)


def normalize(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    """Deprecated compatibility spelling for :func:`unit`."""
    _warn("normalize")
    return unit(value, atol=atol)


__all__ = [
    "DEPRECATED_OPERATION_ALIASES",
    "GalagaDeprecationWarning",
    "involute",
    "mag2",
    "magnitude_squared",
    "normalise",
    "normalize",
    "norm_squared",
]
