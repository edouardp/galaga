"""BasisBlade — named basis blade in a Clifford algebra.

Each blade has three name variants (ascii, unicode, latex) that can
be overridden individually. The Algebra holds one per bitmask.
"""

from __future__ import annotations


class BasisBlade:
    """Names for a single basis blade, indexed by bitmask."""

    __slots__ = ("_bitmask", "_ascii", "_unicode", "_latex")

    def __init__(self, bitmask: int, ascii: str, unicode: str, latex: str):
        self._bitmask = bitmask
        self._ascii = ascii
        self._unicode = unicode
        self._latex = latex

    @property
    def ascii_name(self) -> str:
        return self._ascii

    @ascii_name.setter
    def ascii_name(self, value: str):
        self._ascii = value

    @property
    def unicode_name(self) -> str:
        return self._unicode

    @unicode_name.setter
    def unicode_name(self, value: str):
        self._unicode = value

    @property
    def latex_name(self) -> str:
        return self._latex

    @latex_name.setter
    def latex_name(self, value: str):
        self._latex = value

    def rename(self, ascii: str | None = None, unicode: str | None = None,
               latex: str | None = None) -> BasisBlade:
        """Override one or more name variants. Returns self for chaining."""
        if ascii is not None:
            self._ascii = ascii
        if unicode is not None:
            self._unicode = unicode
        if latex is not None:
            self._latex = latex
        return self

    def __repr__(self) -> str:
        return f"BasisBlade(0b{self._bitmask:b}, {self._ascii!r})"
