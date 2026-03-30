"""Configurable notation rules for symbolic rendering.

GA has many competing notations — reverse alone can be written as ~x, x̃,
x†, x^†, x^R, or rev(x). Different textbooks and communities use different
conventions. This module lets users choose.

Each GA operation has rendering rules for three formats (ascii, unicode, latex).
The Notation class holds these rules and can be overridden per-algebra.
The renderer (ga.render) queries the Notation object instead of hardcoded tables.

Rule kinds:
    prefix:        "-x", "*v"           — symbol prepended to operand
    postfix:       "x†", "x⁻¹", "x²"    — symbol appended to operand
    superscript:   "x^{dagger}"         — symbol placed in LaTeX superscript (auto-braced)
    accent:        "x̃" / "~(a+b)"       — combining char for atoms, prefix fallback for compounds
    infix:         "a∧b", "a·b"         — symbol between two operands
    function:      "rev(x)", "wedge(a,b)" — function call style
    wrap:          "⟨x⟩₁", "‖x‖"        — open/close delimiters around content
    juxtaposition: "ab"                 — no symbol, smart spacing for multi-char names

Why per-algebra?
    Different algebras may use different conventions (e.g. STA uses dagger
    for reverse, while Euclidean GA uses tilde). Each Algebra holds its own
    Notation instance.

Why three formats?
    ASCII is for code/logs, unicode for terminals/REPL, LaTeX for notebooks.
    They can be overridden independently.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass


@dataclass
class NotationRule:
    """How to render one operation in one format."""

    kind: str  # "prefix", "postfix", "superscript", "accent", "infix", "wrap", "juxtaposition"
    symbol: str = ""
    # accent-specific
    combining: str = ""
    fallback_prefix: str = ""
    latex_cmd: str = ""
    latex_wide_cmd: str = ""
    # wrap-specific
    open: str = ""
    close: str = ""
    # infix/juxtaposition-specific
    separator: str = ""


def _accent(combining: str, fallback: str, latex_cmd: str, latex_wide: str) -> dict[str, NotationRule]:
    return {
        "ascii": NotationRule(kind="prefix", symbol=fallback),
        "unicode": NotationRule(kind="accent", combining=combining, fallback_prefix=fallback),
        "latex": NotationRule(kind="accent", latex_cmd=latex_cmd, latex_wide_cmd=latex_wide),
    }


def _postfix(uni: str, latex: str, ascii: str = "") -> dict[str, NotationRule]:
    return {
        "ascii": NotationRule(kind="postfix", symbol=ascii or uni),
        "unicode": NotationRule(kind="postfix", symbol=uni),
        "latex": NotationRule(kind="postfix", symbol=latex),
    }


def _infix(uni: str, latex: str, ascii: str = "") -> dict[str, NotationRule]:
    return {
        "ascii": NotationRule(kind="infix", separator=ascii or uni),
        "unicode": NotationRule(kind="infix", separator=uni),
        "latex": NotationRule(kind="infix", separator=latex),
    }


def _wrap(
    uni_open: str, uni_close: str, latex_open: str, latex_close: str, ascii_open: str = "", ascii_close: str = ""
) -> dict[str, NotationRule]:
    return {
        "ascii": NotationRule(kind="wrap", open=ascii_open or uni_open, close=ascii_close or uni_close),
        "unicode": NotationRule(kind="wrap", open=uni_open, close=uni_close),
        "latex": NotationRule(kind="wrap", open=latex_open, close=latex_close),
    }


# Default rendering rules for every Expr node type.
# Keyed by class name (string) → format → NotationRule.
# These match the library's built-in conventions. Users override via
# Notation.set() or by passing a preset to Algebra(notation=...).

_DEFAULTS: dict[str, dict[str, NotationRule]] = {
    # Accent (combining char for atoms, prefix fallback for compounds)
    "Reverse": _accent("\u0303", "~", r"\tilde", r"\widetilde"),
    "Involute": _accent("\u0302", "inv", r"\hat", r"\widehat"),
    "Conjugate": _accent("\u0304", "conj", r"\bar", r"\overline"),
    # Postfix
    "Dual": _postfix("⋆", "^*", "*"),
    "Undual": _postfix("⋆⁻¹", "^{*^{-1}}", "*^-1"),
    "Complement": _postfix("ᶜ", "^{\\complement}", "^c"),
    "Uncomplement": _postfix("ᶜ⁻¹", "^{\\complement^{-1}}", "^c^-1"),
    "Inverse": _postfix("⁻¹", "^{-1}", "^-1"),
    "Squared": _postfix("²", "^2", "^2"),
    # Prefix
    "Neg": {
        "ascii": NotationRule(kind="prefix", symbol="-"),
        "unicode": NotationRule(kind="prefix", symbol="-"),
        "latex": NotationRule(kind="prefix", symbol="-"),
    },
    "ScalarMul": {
        "ascii": NotationRule(kind="prefix"),
        "unicode": NotationRule(kind="prefix"),
        "latex": NotationRule(kind="prefix"),
    },
    "ScalarDiv": {
        "ascii": NotationRule(kind="postfix", symbol="/"),
        "unicode": NotationRule(kind="postfix", symbol="/"),
        "latex": NotationRule(kind="postfix", symbol="/"),
    },
    # Juxtaposition (geometric product)
    "Gp": {
        "ascii": NotationRule(kind="juxtaposition", separator=""),
        "unicode": NotationRule(kind="juxtaposition", separator=""),
        "latex": NotationRule(kind="juxtaposition", separator=" "),
    },
    # Infix binary
    "Op": _infix("∧", r" \wedge ", "^"),
    "Lc": _infix("⌋", r" \;\lrcorner\; ", "_|"),
    "Rc": _infix("⌊", r" \;\llcorner\; ", "|_"),
    "Hi": _infix("·", r" \cdot ", "."),
    "Dli": _infix("·", r" \cdot ", "."),
    "Sp": _infix("∗", r" * ", "*"),
    "Div": _infix("/", "/", "/"),
    "Regressive": _infix("∨", r" \vee ", "v"),
    "Add": _infix(" + ", " + ", " + "),
    "Sub": _infix(" - ", " - ", " - "),
    # Wrap
    "Grade": _wrap("⟨", "⟩", r"\langle ", r" \rangle", "<", ">"),
    "Norm": _wrap("‖", "‖", r"\lVert ", r" \rVert", "||", "||"),
    "Unit": {
        "ascii": NotationRule(kind="accent", combining="", fallback_prefix="unit(", symbol=")"),
        "unicode": NotationRule(kind="accent", combining="\u0302", fallback_prefix="", symbol="/"),
        "latex": NotationRule(kind="accent", latex_cmd=r"\hat", latex_wide_cmd=r"\widehat"),
    },
    "Exp": _wrap("exp(", ")", "e^{", "}"),
    "Log": _wrap("log(", ")", r"\log\left(", r"\right)"),
    "Sqrt": _wrap("√(", ")", r"\sqrt{", "}"),
    "Even": _wrap("⟨", "⟩₊", r"\langle ", r" \rangle_{\text{even}}"),
    "Odd": _wrap("⟨", "⟩₋", r"\langle ", r" \rangle_{\text{odd}}"),
    "Commutator": _wrap("[", "]", "[", "]"),
    "Anticommutator": _wrap("{", "}", r"\{", r"\}"),
    "LieBracket": _wrap("½[", "]", r"\tfrac{1}{2}[", "]"),
    "JordanProduct": _wrap("½{", "}", r"\tfrac{1}{2}\{", r"\}"),
}


class Notation:
    """Configurable rendering rules for all GA operations."""

    def __init__(self):
        self._rules: dict[str, dict[str, NotationRule]] = {}
        for name, fmts in _DEFAULTS.items():
            self._rules[name] = {k: copy.copy(v) for k, v in fmts.items()}

    def get(self, node_name: str, fmt: str) -> NotationRule | None:
        """Get the rendering rule for a node type name and format."""
        fmts = self._rules.get(node_name)
        if fmts is None:
            return None
        return fmts.get(fmt)

    def set(self, node_name: str, fmt: str, rule: NotationRule):
        """Override a rendering rule for a node type and format."""
        if node_name not in self._rules:
            self._rules[node_name] = {}
        self._rules[node_name][fmt] = rule

    def copy(self) -> Notation:
        """Return an independent copy of this notation."""
        n = Notation.__new__(Notation)
        n._rules = {}
        for name, fmts in self._rules.items():
            n._rules[name] = {k: copy.copy(v) for k, v in fmts.items()}
        return n

    @staticmethod
    def default() -> Notation:
        """Default notation — the library's built-in conventions."""
        return Notation()

    @staticmethod
    def doran_lasenby() -> Notation:
        """Doran & Lasenby ("Geometric Algebra for Physicists") conventions.

        - Reverse: tilde (same as default)
        - Grade involution: hat (same as default)
        - Conjugate: overline (same as default)
        - Dual: I⁻¹x (prefix with pseudoscalar inverse)
        - Inner product: dot (same as default)
        """
        n = Notation()
        # D&L use tilde for reverse — same as default
        # D&L use dagger for Clifford conjugate in some contexts
        n.set("Conjugate", "unicode", NotationRule(kind="accent", combining="\u0304", fallback_prefix="conj"))
        n.set("Conjugate", "latex", NotationRule(kind="accent", latex_cmd=r"\bar", latex_wide_cmd=r"\overline"))
        return n

    @staticmethod
    def hestenes() -> Notation:
        """Hestenes & Sobczyk ("Clifford Algebra to Geometric Calculus") conventions.

        - Reverse: dagger †
        - Grade involution: hat (same as default)
        - Dual: star (same as default)
        """
        n = Notation()
        n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        n.set("Reverse", "ascii", NotationRule(kind="postfix", symbol="dag"))
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
        return n

    @staticmethod
    def functional() -> Notation:
        """Functional notation — all operations as long-form function calls.

        geometric_product(a, b), outer_product(a, b), reverse(a), etc.
        Useful for pedagogical contexts or when symbols are ambiguous.
        """
        return Notation._make_functional(
            {
                "Gp": "geometric_product",
                "Op": "outer_product",
                "Lc": "left_contraction",
                "Rc": "right_contraction",
                "Hi": "hestenes_inner",
                "Dli": "doran_lasenby_inner",
                "Sp": "scalar_product",
                "Div": "divide",
                "Regressive": "regressive_product",
            }
        )

    @staticmethod
    def functional_short() -> Notation:
        """Functional notation — all operations as short-form function calls.

        gp(a, b), op(a, b), rev(a), inv(a), etc.
        """
        return Notation._make_functional(
            {
                "Gp": "gp",
                "Op": "op",
                "Lc": "lc",
                "Rc": "rc",
                "Hi": "hi",
                "Dli": "dli",
                "Sp": "sp",
                "Div": "div",
                "Regressive": "meet",
            },
            {
                "Reverse": "rev",
                "Involute": "inv",
                "Conjugate": "conj",
                "Inverse": "inverse",
                "Sqrt": "sqrt",
                "Even": "even",
                "Odd": "odd",
            },
        )

    @staticmethod
    def _make_functional(
        binary_names: dict[str, str],
        unary_overrides: dict[str, str] | None = None,
    ) -> Notation:
        """Build a functional notation with the given op names."""
        n = Notation()
        unary_defaults = {
            "Reverse": "reverse",
            "Involute": "involute",
            "Conjugate": "conjugate",
            "Dual": "dual",
            "Undual": "undual",
            "Complement": "complement",
            "Uncomplement": "uncomplement",
            "Inverse": "inverse",
            "Squared": "squared",
            "Norm": "norm",
            "Unit": "unit",
            "Exp": "exp",
            "Log": "log",
            "Sqrt": "scalar_sqrt",
            "Even": "even_grades",
            "Odd": "odd_grades",
            "Commutator": "commutator",
            "Anticommutator": "anticommutator",
            "LieBracket": "lie_bracket",
            "JordanProduct": "jordan_product",
        }
        if unary_overrides:
            unary_defaults.update(unary_overrides)
        for name, symbol in unary_defaults.items():
            for fmt in ("unicode", "ascii", "latex"):
                n.set(name, fmt, NotationRule(kind="function", symbol=symbol))
        for name, symbol in binary_names.items():
            for fmt in ("unicode", "ascii", "latex"):
                n.set(name, fmt, NotationRule(kind="function", symbol=symbol))
        for fmt in ("unicode", "ascii", "latex"):
            n.set("Grade", fmt, NotationRule(kind="function", symbol="grade"))
        return n
