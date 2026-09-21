"""Shared package-internal KaTeX decoration lowering.

Expression and matrix renderers both lower the same validated annotation
model. This module is the explicit internal boundary between target-specific
layout and target-independent visual decoration; it is not part of the public
``galaga_annotation`` API.
"""

from __future__ import annotations

from typing import Literal

from galaga.rendering import Decorated, Node, Text, emit

from .model import DIRECTIONAL_MARKERS, Annotation, AnnotationStyle

__all__ = ["ResolvedSide", "decorate", "default_side", "external_parts", "style_body"]

ResolvedSide = Literal["above", "below"]


def _label_lines(annotation: Annotation) -> list[str]:
    if annotation.label_latex is not None:
        return [annotation.label_latex]
    if annotation.label is None:
        return []
    return [rf"\text{{{emit(Text(line), 'latex')}}}" for line in annotation.label.splitlines()] or [r"\text{}"]


def _substack(lines: list[str]) -> str:
    if not lines:
        return ""
    if len(lines) == 1:
        return lines[0]
    return r"\substack{" + r" \\ ".join(lines) + "}"


def _brace_marker(node: Node, marker: str, side: ResolvedSide, text: str | None) -> tuple[Node, ResolvedSide]:
    if marker == "underbrace":
        effective_side: ResolvedSide = "below"
        command = r"\underbrace"
    elif marker == "underbracket":
        effective_side = "below"
        command = r"\underbracket"
    elif marker == "overbracket":
        effective_side = "above"
        command = r"\overbracket"
    elif marker == "overbrace":
        effective_side = "above"
        command = r"\overbrace"
    else:
        effective_side = side
        command = r"\overbrace" if effective_side == "above" else r"\underbrace"
    if text is None:
        return Decorated(node, f"{command}{{", "}"), effective_side
    script = f"}}^{{{text}}}" if effective_side == "above" else f"}}_{{{text}}}"
    return Decorated(node, f"{command}{{", script), effective_side


def _group_marker(node: Node, marker: str, text: str | None) -> tuple[Node, ResolvedSide]:
    side: ResolvedSide = "below" if marker == "undergroup" else "above"
    group = r"\undergroup" if side == "below" else r"\overgroup"
    if text is None:
        return Decorated(node, f"{group}{{", "}"), side
    placement = r"\underset" if side == "below" else r"\overset"
    return Decorated(node, rf"{placement}{{{text}}}{{{group}{{", "}}"), side


def _overline_marker(node: Node, text: str | None) -> tuple[Node, ResolvedSide]:
    if text is None:
        return Decorated(node, r"\overline{", "}"), "above"
    return Decorated(node, rf"\overset{{{text}}}{{\overline{{", "}}"), "above"


def _underline_marker(node: Node, text: str | None) -> tuple[Node, ResolvedSide]:
    if text is None:
        return Decorated(node, r"\underline{", "}"), "below"
    return Decorated(node, rf"\underset{{{text}}}{{\underline{{", "}}"), "below"


def _box_marker(node: Node, side: ResolvedSide, text: str | None) -> tuple[Node, ResolvedSide]:
    if text is None:
        return Decorated(node, r"\boxed{", "}"), side
    placement = r"\overset" if side == "above" else r"\underset"
    return Decorated(node, rf"{placement}{{{text}}}{{\boxed{{", "}}"), side


def _callout_symbol(marker: str, side: ResolvedSide) -> str | None:
    if marker == "arrow":
        return r"\downarrow" if side == "above" else r"\uparrow"
    if marker == "rule":
        return r"\rule[0.2em]{0.4pt}{1em}"
    return None


def _callout_parts(marker: str, side: ResolvedSide, text: str | None, clearance: str | None) -> list[str]:
    symbol = _callout_symbol(marker, side)
    strut = rf"\rule{{0pt}}{{{clearance}}}" if clearance is not None else None
    ordered = (text, symbol, strut) if side == "above" else (strut, symbol, text)
    return [part for part in ordered if part is not None]


def _callout_marker(
    node: Node, marker: str, side: ResolvedSide, text: str | None, clearance: str | None
) -> tuple[Node, ResolvedSide]:
    parts = _callout_parts(marker, side, text, clearance)
    if not parts:
        return node, side
    placement = r"\overset" if side == "above" else r"\underset"
    return Decorated(node, rf"{placement}{{{_substack(parts)}}}{{", "}"), side


def _marker_wrap(
    node: Node, marker: str, side: ResolvedSide, text: str | None, clearance: str | None
) -> tuple[Node, ResolvedSide]:
    if marker in {"brace", "underbrace", "underbracket", "overbrace", "overbracket"}:
        return _brace_marker(node, marker, side, text)
    if marker in {"undergroup", "overgroup"}:
        return _group_marker(node, marker, text)
    if marker == "underline":
        return _underline_marker(node, text)
    if marker == "overline":
        return _overline_marker(node, text)
    if marker == "box":
        return _box_marker(node, side, text)
    return _callout_marker(node, marker, side, text, clearance)


def _label_text(annotation: Annotation) -> str | None:
    lines = _label_lines(annotation)
    if not lines:
        return None
    text = _substack(lines)
    if annotation.style.label_color is not None:
        return rf"\textcolor{{{annotation.style.label_color}}}{{{text}}}"
    return text


def style_body(node: Node, style: AnnotationStyle, *, marked: bool) -> Node:
    """Apply foreground, emphasis, border and background to visible content."""

    emphasis = {"bold": r"\mathbf{", "italic": r"\mathit{"}.get(style.emphasis)
    if emphasis is not None:
        node = Decorated(node, emphasis, "}")
    if not marked and style.color is not None:
        node = Decorated(node, rf"\textcolor{{{style.color}}}{{", "}")
    if style.border is not None:
        background = style.background or "transparent"
        return Decorated(node, rf"\fcolorbox{{{style.border}}}{{{background}}}{{$", "$}")
    if style.background is not None:
        return Decorated(node, rf"\colorbox{{{style.background}}}{{$", "$}")
    return node


def _color_marker(node: Node, color: str | None) -> Node:
    if color is None:
        return node
    return Decorated(node, rf"\textcolor{{{color}}}{{", "}")


def _overlay_marker(
    node: Node,
    style: AnnotationStyle,
    side: ResolvedSide,
    text: str | None,
    *,
    smash: bool,
) -> Node:
    if style.clearance is not None:
        lift = style.clearance if side == "above" else f"-{style.clearance}"
        node = Decorated(node, rf"\vphantom{{\raisebox{{{lift}}}{{\rule{{0pt}}{{1em}}}}}}", "")
    node = Decorated(node, r"\textcolor{black}{", "}")
    node, effective_side = _marker_wrap(node, style.marker, side, text, None)
    node = _color_marker(node, style.color)
    if not smash:
        return node
    wrapper = r"\smash[t]{" if effective_side == "above" else r"\smash[b]{"
    return Decorated(node, wrapper, "}")


def _ordinary_marker(node: Node, style: AnnotationStyle, side: ResolvedSide, text: str | None) -> Node:
    marked = style.marker != "none"
    if marked and style.color is not None:
        # Opaque prefix/suffix wrappers cannot preserve inherited foreground;
        # typed decoration IR can remove this reset in a later design.
        node = Decorated(node, r"\textcolor{black}{", "}")
    if not marked and text is None:
        return node
    node, _ = _marker_wrap(node, style.marker, side, text, style.clearance)
    return _color_marker(node, style.color if marked else None)


def _external_callout(node: Node, annotation: Annotation, side: ResolvedSide, *, smash: bool) -> Node:
    style = annotation.style
    text = _label_text(annotation)
    if text is not None:
        # KaTeX otherwise widens an over/under construct to the label and
        # centres the measured expression inside that wider box. The overlay
        # is anchored at the expression's start, so that centring disconnects
        # the marker from the visible terms whenever the label is wider.
        # ``\mathclap`` preserves label ink and vertical extent while making
        # its horizontal contribution zero.
        text = rf"\mathclap{{{text}}}"
    if style.marker != "none":
        return _overlay_marker(node, style, side, text, smash=smash)
    node = _ordinary_marker(node, style, side, text)
    if not smash:
        return node
    wrapper = r"\smash[t]{" if side == "above" else r"\smash[b]{"
    return Decorated(node, wrapper, "}")


def external_parts(measured: Node, annotation: Annotation, side: ResolvedSide) -> tuple[str, str]:
    """Emit an outer vertical reservation and a visible zero-width overlay."""

    visible = _external_callout(measured, annotation, side, smash=True)
    reserve = _external_callout(measured, annotation, side, smash=False)
    reserved = emit(Decorated(reserve, r"\vphantom{", "}"), "latex")
    overlaid = emit(Decorated(visible, r"\mathrlap{", "}"), "latex")
    return reserved, overlaid


def decorate(node: Node, annotation: Annotation, side: ResolvedSide) -> Node:
    """Apply one complete annotation to a renderer-owned node."""

    style = annotation.style
    marked = style.marker != "none"
    node = style_body(node, style, marked=marked)
    text = _label_text(annotation)
    if marked and style.overlay:
        measured = Decorated(node, r"\phantom{", "}")
        reserved, overlaid = external_parts(measured, annotation, side)
        return Decorated(node, reserved + overlaid, "")
    return _ordinary_marker(node, style, side, text)


def default_side(annotation: Annotation) -> ResolvedSide:
    """Resolve a directional or explicit side without collision layout."""

    direction = DIRECTIONAL_MARKERS.get(annotation.style.marker)
    if direction is not None:
        return direction  # type: ignore[return-value]
    if annotation.side in {"above", "below"}:
        return annotation.side
    return "above"
