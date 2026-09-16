"""One-line reusable presenters; unspecified settings always remain inherited."""

from __future__ import annotations

from typing import TYPE_CHECKING as _TYPE_CHECKING

from . import notation as _notation

if _TYPE_CHECKING:
    from ..presenter import Presenter as _Presenter

__all__ = [
    "bitmap_order",
    "default",
    "full",
    "functional",
    "grade_order",
    "lengyel",
    "short_functional",
    "values",
]


def default() -> _Presenter:
    """Inherit the value's current presentation and capture it on application."""
    from ..presenter import Presenter

    return Presenter()


def values() -> _Presenter:
    """Show only evaluated values, without discarding provenance."""
    from ..presenter import Presenter

    return Presenter(content="value")


def full() -> _Presenter:
    """Show deduplicated name/expression/value equalities."""
    from ..presenter import Presenter

    return Presenter(content="full")


def functional(*, short: bool = False) -> _Presenter:
    """Use functional operation names, preserving blade names and ordering."""
    from ..presenter import Presenter

    return Presenter(notation=_notation.functional(short=short))


def short_functional() -> _Presenter:
    """Use abbreviated functional operation names, preserving blade names and ordering."""
    from ..presenter import Presenter

    return Presenter(notation=_notation.functional_short())


def lengyel() -> _Presenter:
    """Use Lengyel operation notation, including the metric-inner-product bullet."""
    from ..presenter import Presenter

    return Presenter(notation=_notation.lengyel())


def grade_order() -> _Presenter:
    """Group blades by grade, then lexicographic native basis-index tuples."""
    from ..presenter import Presenter

    return Presenter(display_order="grade-lexicographic")


def bitmap_order() -> _Presenter:
    """Show blades in native coefficient-array order."""
    from ..presenter import Presenter

    return Presenter(display_order="bitmap")


def __dir__() -> list[str]:
    return list(__all__)
