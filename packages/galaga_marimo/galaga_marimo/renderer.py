"""Rendering pipeline for t-string templates.

Walks a Template's interpolations, classifies each value, and assembles
markdown suitable for marimo's mo.md().
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from string.templatelib import Interpolation, Template
from typing import Any


class RenderKind(Enum):
    TEXT = "text"
    INLINE_LATEX = "inline_latex"
    BLOCK_LATEX = "block_latex"


@dataclass(frozen=True, slots=True)
class Rendered:
    kind: RenderKind
    value: str


# Format specs that override automatic detection
_SPEC_MAP = {
    "latex": RenderKind.INLINE_LATEX,
    "inline": RenderKind.INLINE_LATEX,
    "block": RenderKind.BLOCK_LATEX,
    "text": RenderKind.TEXT,
    "unicode": RenderKind.TEXT,
}


def _has_latex(obj: Any) -> bool:
    """Check if an object can produce LaTeX output."""
    return callable(getattr(obj, "latex", None)) or callable(getattr(obj, "_repr_latex_", None))


def _strip_latex_delimiters(s: str) -> str:
    """Strip $...$ or $$...$$ wrapping from a LaTeX string."""
    if s.startswith("$$") and s.endswith("$$"):
        return s[2:-2].strip()
    if s.startswith("$") and s.endswith("$"):
        return s[1:-1]
    return s


def _get_latex(obj: Any) -> str:
    """Extract raw LaTeX string from an object.

    Prefers .latex() (returns raw LaTeX) over _repr_latex_() (returns
    $-wrapped LaTeX per the Jupyter/IPython protocol).
    """
    if callable(getattr(obj, "latex", None)):
        return obj.latex()
    return _strip_latex_delimiters(obj._repr_latex_())


def render_value(value: Any, conversion: str | None, format_spec: str) -> Rendered:
    """Render a single interpolated value.

    Priority:
    1. Explicit format spec (:latex, :block, :text, :unicode)
    2. Conversion flag (!r, !s, !a) → always text
    3. Object has .latex() or ._repr_latex_() → inline LaTeX
    4. Fallback → text via str()
    """
    # Conversion flags force text mode
    if conversion == "r":
        return Rendered(RenderKind.TEXT, repr(value))
    if conversion == "a":
        return Rendered(RenderKind.TEXT, ascii(value))
    if conversion == "s":
        return Rendered(RenderKind.TEXT, str(value))

    # Explicit format spec
    if format_spec in _SPEC_MAP:
        kind = _SPEC_MAP[format_spec]
        if kind in (RenderKind.INLINE_LATEX, RenderKind.BLOCK_LATEX) and _has_latex(value):
            return Rendered(kind, _get_latex(value))
        return Rendered(RenderKind.TEXT, str(value))

    # Numeric format specs (e.g. :.3f) → latex with formatted coefficients if possible
    if format_spec:
        if _has_latex(value):
            try:
                return Rendered(RenderKind.INLINE_LATEX, value.latex(coeff_format=format_spec))
            except TypeError:
                pass
        return Rendered(RenderKind.TEXT, format(value, format_spec))

    # Block latex wrapper
    if getattr(value, "_galaga_block", False) and _has_latex(value):
        return Rendered(RenderKind.BLOCK_LATEX, _get_latex(value))

    # Auto-detect: objects with .latex() render as inline LaTeX
    if _has_latex(value):
        return Rendered(RenderKind.INLINE_LATEX, _get_latex(value))

    # Fallback
    return Rendered(RenderKind.TEXT, str(value))


def _escape_md(s: str) -> str:
    """Minimal markdown escaping for interpolated text values."""
    # Only escape characters that would break markdown structure
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _recognize_value(value: Any, recognize, tol: float = 1e-10) -> str | None:
    """Check if value matches any known MV. Return its LaTeX label or None."""
    import numpy as np

    data = getattr(value, "data", None)
    if not isinstance(data, np.ndarray):
        return None
    # Don't annotate if the value already has a name matching a known
    name = getattr(value, "_name_latex", None) or getattr(value, "_name", None)
    knowns = recognize.values() if isinstance(recognize, dict) else recognize
    for known in knowns:
        known_data = getattr(known, "data", None)
        if not isinstance(known_data, np.ndarray):
            continue
        if data.shape != known_data.shape:
            continue
        label = getattr(known, "_name_latex", None) or getattr(known, "_name", None)
        if not label:
            continue
        if np.allclose(data, known_data, atol=tol):
            # Skip if the value's own name matches
            if name and name == label:
                return None
            return label
    return None


def _append_recognition(assembled: str, label: str, kind: RenderKind) -> str:
    """Append a recognition annotation to rendered LaTeX."""
    # Get LaTeX for the label — use it directly (it may contain LaTeX commands)
    annotation = rf"\equiv {label}"
    if kind == RenderKind.INLINE_LATEX:
        # $...$ → $... \quad (\equiv label)$
        return assembled[:-1] + rf" \quad ({annotation})$"
    # $$...$$ → $$... \quad (\equiv label)$$
    return assembled.rstrip().rstrip("$") + rf" \quad ({annotation})$$" + "\n\n"


def _assemble(rendered: Rendered) -> str:
    """Convert a Rendered value to its markdown string."""
    if rendered.kind == RenderKind.INLINE_LATEX:
        return f"${rendered.value}$"
    if rendered.kind == RenderKind.BLOCK_LATEX:
        return f"\n\n$${rendered.value}$$\n\n"
    return _escape_md(rendered.value)


def render_template(template: Template, recognize: dict | list | tuple | None = None) -> str:
    """Walk a t-string Template and produce a markdown string.

    Literal parts pass through unchanged. Interpolations are classified
    and rendered according to their type and format spec.

    Args:
        template: A t-string Template to render.
        recognize: Optional collection of named Multivectors (list, dict,
            or any iterable). When a rendered MV's numeric value matches
            a known, an annotation ``(≡ label)`` is appended using the
            known MV's own LaTeX name.
    """
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, Interpolation):
            rendered = render_value(item.value, item.conversion, item.format_spec)
            assembled = _assemble(rendered)
            if recognize and rendered.kind in (RenderKind.INLINE_LATEX, RenderKind.BLOCK_LATEX):
                match = _recognize_value(item.value, recognize)
                if match is not None:
                    assembled = _append_recognition(assembled, match, rendered.kind)
            parts.append(assembled)
    return "".join(parts)
