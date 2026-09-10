"""Named notation recipes for the public preset namespace."""

from __future__ import annotations

from ..presentation import Notation as _Notation

__all__ = [
    "default",
    "doran_lasenby",
    "functional",
    "functional_short",
    "hestenes",
    "lengyel",
    "lengyel_rga",
]


def default(*, id: str = "default") -> _Notation:
    """Return the conventional notation with an optional identifying name."""
    return _Notation.default(id=id)


def functional(*, short: bool = False) -> _Notation:
    """Return functional operation names, optionally in their short form."""
    return _Notation.functional(short=short)


def functional_short() -> _Notation:
    """Return the short functional notation."""
    return _Notation.functional_short()


def doran_lasenby() -> _Notation:
    """Return Doran–Lasenby geometric-algebra notation."""
    return _Notation.doran_lasenby()


def hestenes() -> _Notation:
    """Return Hestenes geometric-algebra notation."""
    return _Notation.hestenes()


def lengyel() -> _Notation:
    """Return Lengyel's notation."""
    return _Notation.lengyel()


def lengyel_rga() -> _Notation:
    """Return Lengyel's RGA notation."""
    return _Notation.lengyel_rga()


def __dir__() -> list[str]:
    """Advertise only named notation recipes."""
    return list(__all__)
