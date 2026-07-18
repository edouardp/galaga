"""Immutable presentation names for ASCII, Unicode, and LaTeX targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True, slots=True)
class Name:
    """One semantic name with target-specific spellings."""

    ascii: str
    unicode: str | None = None
    latex: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ascii, str) or not self.ascii:
            raise ValueError("an ASCII name must be a non-empty string")
        unicode = self.ascii if self.unicode is None else self.unicode
        latex = unicode if self.latex is None else self.latex
        if not isinstance(unicode, str) or not unicode:
            raise ValueError("a Unicode name must be a non-empty string")
        if not isinstance(latex, str) or not latex:
            raise ValueError("a LaTeX name must be a non-empty string")
        object.__setattr__(self, "unicode", unicode)
        object.__setattr__(self, "latex", latex)

    @property
    def variants(self) -> tuple[str, str, str]:
        """The ASCII, Unicode, and LaTeX spellings in target order."""
        return self.ascii, cast(str, self.unicode), cast(str, self.latex)

    def for_target(self, target: str) -> str:
        """Return one spelling for ``ascii``, ``unicode``, or ``latex``."""
        if target == "ascii":
            return self.ascii
        if target == "unicode":
            return cast(str, self.unicode)
        if target == "latex":
            return cast(str, self.latex)
        raise ValueError("target must be 'ascii', 'unicode', or 'latex'")

    def __str__(self) -> str:
        return cast(str, self.unicode)


__all__ = ["Name"]
