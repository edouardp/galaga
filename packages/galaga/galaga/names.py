"""Immutable presentation names for ASCII, Unicode, and LaTeX targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from ._latex_symbols import LatexSymbols


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

    @classmethod
    def from_latex(cls, latex: str, *, ascii: str | None = None, unicode: str | None = None) -> Name:
        """Explicitly derive spellings for a supported single LaTeX symbol.

        Surrounding whitespace is stripped. Explicit overrides win over
        lookup results. Unsupported text requires an ``ascii=`` fallback;
        its Unicode spelling then defaults to ASCII unless also supplied.
        This opt-in helper does not change ordinary Name construction.
        """
        if not isinstance(latex, str):
            raise TypeError("LaTeX input must be a string")
        latex = latex.strip()
        if not latex:
            raise ValueError("a LaTeX name must be a non-empty string")
        derived = LatexSymbols().lookup(latex)
        if derived is None:
            if ascii is None:
                raise ValueError("unsupported LaTeX symbol; provide ascii= explicitly")
            return cls(ascii, unicode, latex)
        derived_unicode, derived_ascii = derived
        return cls(
            derived_ascii if ascii is None else ascii,
            derived_unicode if unicode is None else unicode,
            latex,
        )

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


__all__ = ["LatexSymbols", "Name"]
