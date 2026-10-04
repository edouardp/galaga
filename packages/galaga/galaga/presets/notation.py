"""Named notation recipes for the public preset namespace."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from ..composition import NotationPatch as _NotationPatch
from ..presentation import Notation as _Notation
from ..presentation import RenderRule as _RenderRule
from ..presentation import _normalize_rules

__all__ = [
    "default",
    "doran_lasenby",
    "functional",
    "functional_short",
    "hestenes",
    "lengyel",
    "lengyel_rga",
    "override",
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


def override(
    *,
    reverse: Literal["tilde", "dagger"] | None = None,
    rules: Mapping[str | tuple[str, str], _RenderRule] | None = None,
    ascii: Mapping[str, _RenderRule] | None = None,
    unicode: Mapping[str, _RenderRule] | None = None,
    latex: Mapping[str, _RenderRule] | None = None,
) -> _NotationPatch:
    """Override selected operation rules while inheriting every other rule.

    ``rules`` uses the same keys as ``Notation``: an operation ID for a
    target-neutral rule, or ``(operation_id, target)`` for one output target.
    The target maps are convenient spellings for target-specific changes.
    """
    entries: list[tuple[str | tuple[str, str], _RenderRule]] = []
    if rules is not None:
        if not isinstance(rules, Mapping):
            raise TypeError("notation override rules must be a mapping")
        entries.extend(rules.items())
    for target, selected in (("ascii", ascii), ("unicode", unicode), ("latex", latex)):
        if selected is None:
            continue
        if not isinstance(selected, Mapping):
            raise TypeError(f"notation override {target} must be a mapping")
        entries.extend(((operation_id, target), rule) for operation_id, rule in selected.items())
    return _NotationPatch(reverse=reverse, rules=_normalize_rules(entries))


def __dir__() -> list[str]:
    """Advertise only named notation recipes."""
    return list(__all__)
