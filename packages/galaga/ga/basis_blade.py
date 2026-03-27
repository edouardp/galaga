"""BasisBlade — named basis blade in a Clifford algebra.

Each basis blade in an algebra (e₁, e₁₂, e₁₂₃, etc.) has three display
name variants: ascii, unicode, and latex. These are stored in BasisBlade
objects, one per bitmask, held by the Algebra.

Why three variants?
  - ASCII: safe for logs, CI, copy-paste into code
  - Unicode: pretty terminal/REPL output (subscripts, Greek letters)
  - LaTeX: notebook rendering via _repr_latex_()

Why mutable?
  Users need to rename blades after algebra construction — e.g. renaming
  the pseudoscalar to "I", or bivectors to angular momentum components.
  Renaming is live: it affects all existing Multivectors immediately
  because rendering reads from BasisBlade at render time, not from
  cached names on the Multivector.
"""

from __future__ import annotations


class BasisBlade:
    """Names for a single basis blade, indexed by bitmask.

    The bitmask encodes which basis vectors are present: e.g. e₁₃ = 0b101.
    """

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
