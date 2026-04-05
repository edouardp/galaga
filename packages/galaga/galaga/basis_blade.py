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

    __slots__ = ("_bitmask", "_ascii", "_unicode", "_latex", "_sign")

    def __init__(self, bitmask: int, ascii: str, unicode: str, latex: str, sign: int = 1):
        self._bitmask = bitmask
        self._ascii = ascii
        self._unicode = unicode
        self._latex = latex
        self._sign = sign

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

    @property
    def sign(self) -> int:
        return self._sign

    def rename(
        self, name=None, /, *, ascii: str | None = None, unicode: str | None = None, latex: str | None = None
    ) -> BasisBlade:
        """Override one or more name variants. Returns self for chaining.

        Args:
            name: String (all three formats), 2-tuple (ascii, unicode),
                  or 3-tuple (ascii, unicode, latex).
            ascii: Override ASCII name only.
            unicode: Override Unicode name only.
            latex: Override LaTeX name only.
        """
        if name is not None:
            if isinstance(name, str):
                self._ascii = self._unicode = self._latex = name
            elif isinstance(name, tuple) and len(name) == 2:
                self._ascii, self._unicode = name
                self._latex = name[1]
            elif isinstance(name, tuple) and len(name) == 3:
                self._ascii, self._unicode, self._latex = name
            else:
                raise ValueError(f"name must be str, 2-tuple, or 3-tuple, got {name!r}")
        if ascii is not None:
            self._ascii = ascii
        if unicode is not None:
            self._unicode = unicode
        if latex is not None:
            self._latex = latex
        return self

    def __repr__(self) -> str:
        return f"BasisBlade(0b{self._bitmask:b}, {self._ascii!r})"
