"""LaTeX → Unicode/ASCII symbol mapping.

Given a LaTeX command like ``\\phi``, returns the unicode equivalent ``ϕ``
and an ASCII fallback ``phi``. Handles Greek letters, math fonts
(``\\mathbf``, ``\\mathit``, ``\\mathcal``, ``\\mathfrak``, ``\\mathbb``),
common symbols, operators, relations, and arrows.

Usage::

    sym = LatexSymbols()
    sym.unicode(r"\\phi")       # "ϕ"
    sym.ascii(r"\\phi")         # "phi"
    sym.lookup(r"\\mathbf{v}")  # ("𝐯", "v")
"""

from __future__ import annotations

import re


# Greek lowercase: (latex_cmd, unicode_char, ascii_name)
_GREEK_LOWER = [
    ("alpha", "α"), ("beta", "β"), ("gamma", "γ"), ("delta", "δ"),
    ("epsilon", "ϵ"), ("varepsilon", "ε"), ("zeta", "ζ"), ("eta", "η"),
    ("theta", "θ"), ("vartheta", "ϑ"), ("iota", "ι"), ("kappa", "κ"),
    ("lambda", "λ"), ("mu", "μ"), ("nu", "ν"), ("xi", "ξ"),
    ("pi", "π"), ("varpi", "ϖ"), ("rho", "ρ"), ("varrho", "ϱ"),
    ("sigma", "σ"), ("varsigma", "ς"), ("tau", "τ"), ("upsilon", "υ"),
    ("phi", "ϕ"), ("varphi", "φ"), ("chi", "χ"), ("psi", "ψ"),
    ("omega", "ω"),
]

_GREEK_UPPER = [
    ("Gamma", "Γ"), ("Delta", "Δ"), ("Theta", "Θ"), ("Lambda", "Λ"),
    ("Xi", "Ξ"), ("Pi", "Π"), ("Sigma", "Σ"), ("Upsilon", "Υ"),
    ("Phi", "Φ"), ("Psi", "Ψ"), ("Omega", "Ω"),
]

_COMMON = [
    ("hbar", "ℏ"), ("ell", "ℓ"), ("nabla", "∇"), ("partial", "∂"),
    ("infty", "∞"), ("forall", "∀"), ("exists", "∃"), ("emptyset", "∅"),
    ("aleph", "ℵ"), ("wp", "℘"), ("Re", "ℜ"), ("Im", "ℑ"),
]

_OPERATORS = [
    ("cdot", "·", "."), ("times", "×", "x"), ("wedge", "∧", "^"),
    ("vee", "∨", "v"), ("star", "⋆", "*"), ("dagger", "†", "dag"),
    ("pm", "±", "+/-"), ("mp", "∓", "-/+"), ("circ", "∘", "o"),
    ("otimes", "⊗", "(x)"), ("oplus", "⊕", "(+)"),
]

_RELATIONS = [
    ("leq", "≤", "<="), ("geq", "≥", ">="), ("neq", "≠", "!="),
    ("approx", "≈", "~="), ("equiv", "≡", "==="), ("sim", "∼", "~"),
    ("propto", "∝", "propto"), ("in", "∈", "in"),
    ("subset", "⊂", "subset"), ("supset", "⊃", "supset"),
]

_ARROWS = [
    ("to", "→", "->"), ("leftarrow", "←", "<-"),
    ("Rightarrow", "⇒", "=>"), ("Leftarrow", "⇐", "<="),
    ("leftrightarrow", "↔", "<->"), ("mapsto", "↦", "|->"),
]

# Math font Unicode offsets: (uppercase_start, lowercase_start)
# These are offsets from 'A'=65 / 'a'=97 into the Unicode math blocks.
_MATHBF_UPPER = 0x1D400  # 𝐀
_MATHBF_LOWER = 0x1D41A  # 𝐚
_MATHIT_UPPER = 0x1D434  # 𝐴
_MATHIT_LOWER = 0x1D44E  # 𝑎  (note: 𝑎 is at 0x1D44E, h at 0x1D455 is missing, use ℎ)
_MATHCAL_UPPER = 0x1D49C  # 𝒜
_MATHFRAK_UPPER = 0x1D504  # 𝔄
_MATHFRAK_LOWER = 0x1D51E  # 𝔞
_MATHBB_UPPER = 0x1D538  # 𝔸

# Special mathbb characters that have dedicated Unicode codepoints
_MATHBB_SPECIAL = {
    'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ',
}

# mathcal has gaps — some letters have dedicated codepoints
_MATHCAL_SPECIAL = {
    'B': 'ℬ', 'E': 'ℰ', 'F': 'ℱ', 'H': 'ℋ', 'I': 'ℐ', 'L': 'ℒ',
    'M': 'ℳ', 'R': 'ℛ',
}

# mathfrak has gaps
_MATHFRAK_SPECIAL = {
    'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ',
}

_MATH_FONT_RE = re.compile(r"\\(mathbf|mathit|mathcal|mathfrak|mathbb)\{(\w)\}")
_ACCENT_RE = re.compile(r"\\(hat|tilde|bar|vec|dot|ddot)\{(\w)\}")

# Combining characters for single-letter accents
_ACCENT_COMBINING = {
    "hat":   "\u0302",  # combining circumflex
    "tilde": "\u0303",  # combining tilde
    "bar":   "\u0304",  # combining macron
    "vec":   "\u20D7",  # combining right arrow above
    "dot":   "\u0307",  # combining dot above
    "ddot":  "\u0308",  # combining diaeresis
}


class LatexSymbols:
    """Maps LaTeX commands to Unicode and ASCII equivalents."""

    def __init__(self):
        self._unicode: dict[str, str] = {}
        self._ascii: dict[str, str] = {}

        for name, uni in _GREEK_LOWER:
            key = f"\\{name}"
            self._unicode[key] = uni
            # "lambda" is a Python keyword, use "lambda_"
            self._ascii[key] = f"{name}_" if name == "lambda" else name

        for name, uni in _GREEK_UPPER:
            key = f"\\{name}"
            self._unicode[key] = uni
            self._ascii[key] = name

        for name, uni in _COMMON:
            key = f"\\{name}"
            self._unicode[key] = uni
            self._ascii[key] = name

        for entry in _OPERATORS:
            name, uni, asc = entry
            key = f"\\{name}"
            self._unicode[key] = uni
            self._ascii[key] = asc

        for entry in _RELATIONS:
            name, uni, asc = entry
            key = f"\\{name}"
            self._unicode[key] = uni
            self._ascii[key] = asc

        for entry in _ARROWS:
            name, uni, asc = entry
            key = f"\\{name}"
            self._unicode[key] = uni
            self._ascii[key] = asc

    def _math_font(self, latex: str) -> tuple[str, str] | None:
        """Handle \\mathbf{X}, \\mathit{X}, etc."""
        m = _MATH_FONT_RE.fullmatch(latex)
        if not m:
            return None
        font, char = m.group(1), m.group(2)
        asc = char  # ASCII is always the plain letter

        if font == "mathbf":
            if char.isupper():
                uni = chr(_MATHBF_UPPER + ord(char) - ord('A'))
            else:
                uni = chr(_MATHBF_LOWER + ord(char) - ord('a'))
        elif font == "mathit":
            if char.isupper():
                uni = chr(_MATHIT_UPPER + ord(char) - ord('A'))
            else:
                offset = ord(char) - ord('a')
                # Unicode has a gap at U+1D455 (italic h), use ℎ
                if char == 'h':
                    uni = 'ℎ'
                else:
                    uni = chr(_MATHIT_LOWER + offset)
        elif font == "mathcal":
            if char in _MATHCAL_SPECIAL:
                uni = _MATHCAL_SPECIAL[char]
            else:
                uni = chr(_MATHCAL_UPPER + ord(char) - ord('A'))
        elif font == "mathfrak":
            if char in _MATHFRAK_SPECIAL:
                uni = _MATHFRAK_SPECIAL[char]
            elif char.isupper():
                uni = chr(_MATHFRAK_UPPER + ord(char) - ord('A'))
            else:
                uni = chr(_MATHFRAK_LOWER + ord(char) - ord('a'))
        elif font == "mathbb":
            if char in _MATHBB_SPECIAL:
                uni = _MATHBB_SPECIAL[char]
            else:
                uni = chr(_MATHBB_UPPER + ord(char) - ord('A'))
        else:
            return None

        return uni, asc

    def _accent(self, latex: str) -> tuple[str, str] | None:
        """Handle \\hat{x}, \\tilde{x}, \\bar{x}, etc."""
        m = _ACCENT_RE.fullmatch(latex)
        if not m:
            return None
        accent, char = m.group(1), m.group(2)
        combining = _ACCENT_COMBINING[accent]
        return char + combining, f"{accent}_{char}"

    def unicode(self, latex: str) -> str | None:
        """Return the Unicode equivalent of a LaTeX command, or None."""
        if latex in self._unicode:
            return self._unicode[latex]
        result = self._math_font(latex) or self._accent(latex)
        return result[0] if result else None

    def ascii(self, latex: str) -> str | None:
        """Return the ASCII equivalent of a LaTeX command, or None."""
        if latex in self._ascii:
            return self._ascii[latex]
        result = self._math_font(latex) or self._accent(latex)
        return result[1] if result else None

    def lookup(self, latex: str) -> tuple[str, str] | None:
        """Return (unicode, ascii) tuple, or None if unknown."""
        u = self.unicode(latex)
        a = self.ascii(latex)
        if u is None and a is None:
            return None
        return u, a
