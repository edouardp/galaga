"""First KaTeX annotation renderer (SPEC-015, ADR-142).

The renderer resolves a plan to layout paths, lowers each rule to a
renderer-owned wrapper around the semantic subtree, and emits the decorated
tree through the shared Galaga emitter. Only the LaTeX target is decorated;
plain-text targets keep the undecorated rendering.

Adjacent terms carrying the same rule form a *span layer*: the rule wraps the
whole run once, so a fill stays continuous across internal separators and a
label appears once per run. Independent rules form independent layers, which
may nest, allowing a wide highlight to contain narrower brackets.
"""

from __future__ import annotations

from collections.abc import Iterable
from copy import copy as _copy
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Literal

from galaga.rendering import Decorated, Node, RenderDocument, Sum, SumTerm, Text, emit

from .model import DIRECTIONAL_MARKERS, Annotation, AnnotationStyle
from .plan import AnnotationPlan, Placement, resolve

__all__ = ["KatexResult", "LabelPlacement", "SpanLayoutError", "render_katex"]

ResolvedSide = Literal["above", "below"]
Path = tuple[str | int, ...]


@dataclass(frozen=True, slots=True)
class LabelPlacement:
    """Solved placement of one labelled annotation layer."""

    path: Path
    side: ResolvedSide
    order: int
    estimated_width: float
    collided: bool


class SpanLayoutError(ValueError):
    """Two joined term spans overlap without nesting or staying disjoint."""


@dataclass(frozen=True, slots=True)
class KatexResult:
    """Annotated LaTeX plus the solved label layout and empty selections."""

    text: str
    labels: tuple[LabelPlacement, ...]
    missing: tuple[Annotation, ...]


@dataclass(frozen=True, slots=True)
class _Span:
    """One rule covering a contiguous run of direct terms in a sum."""

    container: Path
    start: int
    stop: int
    annotation: Annotation
    order: int


@dataclass(frozen=True, slots=True)
class _Direct:
    """One rule attached to a layout path that is not a term run."""

    path: Path
    annotation: Annotation
    order: int


_Entry = _Span | _Direct


@dataclass(frozen=True, slots=True)
class _RebuildContext:
    spans_by_container: dict[Path, tuple[_Span, ...]]
    direct_by_path: dict[Path, tuple[_Direct, ...]]
    sides: dict[_Entry, ResolvedSide]


def _entry_path(entry: _Entry) -> Path:
    if isinstance(entry, _Span):
        return (*entry.container, "terms", entry.start, "body")
    return entry.path


def _has_label(annotation: Annotation) -> bool:
    """Return whether an annotation has either supported label form."""

    return annotation.label is not None or annotation.label_latex is not None


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
    effective_side = side
    if marker == "underbrace":
        effective_side = "below"
    elif marker == "overbrace":
        effective_side = "above"
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
    """Wrap a body with one marker and return the effective side."""

    if marker in {"brace", "underbrace", "overbrace"}:
        return _brace_marker(node, marker, side, text)
    if marker in {"undergroup", "overgroup"}:
        return _group_marker(node, marker, text)
    if marker == "underline":
        return _underline_marker(node, text)
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


def _style_body(node: Node, style: AnnotationStyle, *, marked: bool) -> Node:
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


def _overlay_marker(node: Node, style: AnnotationStyle, side: ResolvedSide, text: str | None) -> Node:
    if style.clearance is not None:
        lift = style.clearance if side == "above" else f"-{style.clearance}"
        node = Decorated(node, rf"\vphantom{{\raisebox{{{lift}}}{{\strut}}}}", "")
    node = Decorated(node, r"\textcolor{black}{", "}")
    node, effective_side = _marker_wrap(node, style.marker, side, text, None)
    node = _color_marker(node, style.color)
    smash = r"\smash[t]{" if effective_side == "above" else r"\smash[b]{"
    return Decorated(node, smash, "}")


def _ordinary_marker(node: Node, style: AnnotationStyle, side: ResolvedSide, text: str | None) -> Node:
    marked = style.marker != "none"
    if marked and style.color is not None:
        # This reset is a temporary limitation of opaque prefix/suffix
        # wrappers; typed decoration IR can preserve inherited foreground.
        node = Decorated(node, r"\textcolor{black}{", "}")
    if not marked and text is None:
        return node
    node, _ = _marker_wrap(node, style.marker, side, text, style.clearance)
    return _color_marker(node, style.color if marked else None)


def _wrap(node: Node, annotation: Annotation, side: ResolvedSide) -> Node:
    """Apply content styling, then one ordinary or overlay marker."""

    style = annotation.style
    marked = style.marker != "none"
    node = _style_body(node, style, marked=marked)
    text = _label_text(annotation)
    if marked and style.overlay:
        return _overlay_marker(node, style, side, text)
    return _ordinary_marker(node, style, side, text)


def _default_side(annotation: Annotation) -> ResolvedSide:
    direction = DIRECTIONAL_MARKERS.get(annotation.style.marker)
    if direction is not None:
        return direction  # type: ignore[return-value]
    if annotation.side in {"above", "below"}:
        return annotation.side
    return "above"


def _estimate_width(annotation: Annotation) -> float:
    if annotation.label is not None:
        lines = annotation.label.splitlines() or [""]
        character_width = 0.55
    elif annotation.label_latex is not None:
        # Raw TeX cannot be measured without KaTeX. Splitting common stacked
        # rows and using a smaller source-character factor gives a stable,
        # conservative heuristic while still reserving layout space.
        lines = annotation.label_latex.split(r"\\")
        character_width = 0.35
    else:
        lines = [""]
        character_width = 0.0
    width = max((len(line.strip()) for line in lines), default=0) * character_width + 0.3
    if annotation.style.marker in {"arrow", "rule"}:
        width += 0.5
    if annotation.style.clearance is not None:
        width += 0.4
    return width


def _solve(entries: tuple[_Entry, ...]) -> tuple[tuple[LabelPlacement, ...], dict[_Entry, ResolvedSide]]:
    """Greedy approximate placement: keep anchors centred, alternate sides."""

    labelled = sorted(
        (entry for entry in entries if _has_label(entry.annotation) or entry.annotation.style.marker != "none"),
        key=lambda entry: entry.order,
    )
    occupied: dict[str, float | None] = {"above": None, "below": None}
    labels: list[LabelPlacement] = []
    sides: dict[_Entry, ResolvedSide] = {}
    for entry in labelled:
        annotation = entry.annotation
        width = _estimate_width(annotation)
        start = entry.order - width / 2
        end = entry.order + width / 2
        direction = DIRECTIONAL_MARKERS.get(annotation.style.marker)
        explicit = annotation.side if annotation.side in {"above", "below"} else None
        side: ResolvedSide = direction or explicit or "above"  # type: ignore[assignment]

        def overlaps(candidate: str, start: float = start) -> bool:
            limit = occupied[candidate]
            return limit is not None and start < limit

        collided = False
        if overlaps(side):
            if direction is None and explicit is None:
                other: ResolvedSide = "below" if side == "above" else "above"
                if not overlaps(other):
                    side = other
                else:
                    collided = True
            else:
                collided = True
        occupied[side] = max(end, occupied[side] or end)
        sides[entry] = side
        labels.append(LabelPlacement(_entry_path(entry), side, entry.order, width, collided))
    return tuple(labels), sides


def _term_positions(body: Node) -> dict[Path, tuple[Path, int]]:
    """Map direct term-body paths to ``(sum path, term index)``."""

    positions: dict[Path, tuple[Path, int]] = {}

    def walk(node: Node, path: Path) -> None:
        if isinstance(node, Sum):
            for index, term in enumerate(node.terms):
                term_path = (*path, "terms", index, "body")
                positions[term_path] = (path, index)
                walk(term.body, term_path)
            return
        if not is_dataclass(node):
            return
        for field in fields(node):
            value = getattr(node, field.name)
            if isinstance(value, Node):
                walk(value, (*path, field.name))
            elif isinstance(value, tuple):
                for index, member in enumerate(value):
                    if isinstance(member, Node):
                        walk(member, (*path, field.name, index))

    walk(body, ())
    return positions


def _validate_spans(spans: list[_Span], container: Path) -> None:
    """Joined spans must nest or stay disjoint; crossing spans are ambiguous."""

    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            disjoint = left.stop <= right.start or right.stop <= left.start
            nested = (left.start <= right.start and right.stop <= left.stop) or (
                right.start <= left.start and left.stop <= right.stop
            )
            if not disjoint and not nested:
                raise SpanLayoutError(
                    f"joined spans {left.start}:{left.stop} and {right.start}:{right.stop} in {container!r} "
                    "overlap without nesting; split the rules or disable join"
                )


def _placements_by_path(plan: AnnotationPlan) -> dict[Path, list[Placement]]:
    grouped: dict[Path, list[Placement]] = {}
    for placement in plan.placements:
        grouped.setdefault(placement.path, []).append(placement)
    return grouped


def _record_placements(
    path: Path,
    placements: list[Placement],
    positions: dict[Path, tuple[Path, int]],
    spans: list[_Span],
    directs: list[_Direct],
    joinable: dict[tuple[Path, Annotation], list[tuple[int, int]]],
) -> None:
    position = positions.get(path)
    if position is None:
        directs.extend(_Direct(path, placement.annotation, placement.order) for placement in placements)
        return
    container, index = position
    for placement in placements:
        if placement.annotation.join:
            joinable.setdefault((container, placement.annotation), []).append((index, placement.order))
        else:
            spans.append(_Span(container, index, index + 1, placement.annotation, placement.order))


def _contiguous_spans(container: Path, annotation: Annotation, entries: list[tuple[int, int]]) -> list[_Span]:
    indices = sorted({index for index, _ in entries})
    order = min(entry_order for _, entry_order in entries)
    runs: list[_Span] = []
    start = previous = indices[0]
    for index in indices[1:]:
        if index != previous + 1:
            runs.append(_Span(container, start, previous + 1, annotation, order))
            start = index
        previous = index
    runs.append(_Span(container, start, previous + 1, annotation, order))
    return runs


def _validate_span_groups(spans: list[_Span]) -> None:
    for container in {span.container for span in spans}:
        _validate_spans([span for span in spans if span.container == container], container)


def _collect(plan: AnnotationPlan, body: Node) -> tuple[tuple[_Span, ...], tuple[_Direct, ...]]:
    """Separate direct placements from contiguous, optionally joined spans."""

    positions = _term_positions(body)
    spans: list[_Span] = []
    directs: list[_Direct] = []
    joinable: dict[tuple[Path, Annotation], list[tuple[int, int]]] = {}
    for path, placements in _placements_by_path(plan).items():
        _record_placements(path, placements, positions, spans, directs, joinable)
    for (container, annotation), entries in joinable.items():
        spans.extend(_contiguous_spans(container, annotation, entries))
    _validate_span_groups(spans)
    return tuple(spans), tuple(directs)


def _clone_with(node: Any, changes: dict[str, Any]) -> Any:
    """Shallow-copy a frozen render node and replace selected fields.

    ``dataclasses.replace`` re-runs custom ``__init__`` signatures, which do
    not always accept every field (for example ``Infix.binding``); copying and
    setting attributes preserves the node exactly.
    """

    if not changes:
        return node
    clone = _copy(node)
    for name, value in changes.items():
        object.__setattr__(clone, name, value)
    return clone


def _rebuild_tuple(values: tuple[Any, ...], path: Path, field_name: str, context: _RebuildContext) -> tuple[Any, ...]:
    rebuilt_values: list[Any] = []
    for index, member in enumerate(values):
        member_path = (*path, field_name, index)
        if isinstance(member, Node):
            rebuilt_values.append(_rebuild(member, member_path, context))
        elif isinstance(member, SumTerm):
            body = _rebuild(member.body, (*member_path, "body"), context)
            rebuilt_values.append(_clone_with(member, {"body": body}) if body is not member.body else member)
        else:
            rebuilt_values.append(member)
    return tuple(rebuilt_values)


def _rebuild_fields(node: Node, path: Path, context: _RebuildContext) -> dict[str, Any]:
    if not is_dataclass(node):
        return {}
    changes: dict[str, Any] = {}
    for field in fields(node):
        value = getattr(node, field.name)
        if isinstance(value, Node):
            rebuilt = _rebuild(value, (*path, field.name), context)
        elif isinstance(value, tuple):
            rebuilt = _rebuild_tuple(value, path, field.name, context)
        else:
            continue
        if rebuilt != value:
            changes[field.name] = rebuilt
    return changes


def _apply_directs(node: Node, path: Path, context: _RebuildContext) -> Node:
    for entry in context.direct_by_path.get(path, ()):
        side = context.sides.get(entry) or _default_side(entry.annotation)
        node = _wrap(node, entry.annotation, side)
    return node


def _rebuild(node: Node, path: Path, context: _RebuildContext) -> Node:
    spans = context.spans_by_container.get(path)
    if isinstance(node, Sum) and spans is not None:
        rebuilt = _render_sum(node, path, spans, context)
    else:
        rebuilt = _clone_with(node, _rebuild_fields(node, path, context))
    return _apply_directs(rebuilt, path, context)


@dataclass(slots=True)
class _SumLayout:
    terms: tuple[SumTerm, ...]
    bodies: list[Node]
    sides: dict[_Entry, ResolvedSide]

    def plain(self, start: int, stop: int, leading_inside: bool) -> Node:
        if stop - start == 1:
            body = self.bodies[start]
            return Sum((SumTerm(body, negative=True),)) if leading_inside and self.terms[start].negative else body
        terms = (
            SumTerm(
                self.bodies[index],
                negative=self.terms[index].negative if index > start or leading_inside else False,
            )
            for index in range(start, stop)
        )
        return Sum(tuple(terms))

    def wrap(self, body: Node, spans: list[_Span]) -> Node:
        for span in sorted(spans, key=lambda entry: entry.order):
            side = self.sides.get(span) or _default_side(span.annotation)
            body = _wrap(body, span.annotation, side)
        return body

    @staticmethod
    def segments(start: int, stop: int, pivot: _Span) -> list[tuple[int, int]]:
        bounds = [start, pivot.start, pivot.stop, stop]
        return [(left, right) for left, right in zip(bounds, bounds[1:]) if left < right]

    def split(self, start: int, stop: int, leading_inside: bool, active: list[_Span], pivot: _Span) -> Node:
        terms: list[SumTerm] = []
        for index, (segment_start, segment_stop) in enumerate(self.segments(start, stop, pivot)):
            nested = [span for span in active if span.start < segment_stop and span.stop > segment_start]
            segment_leading = leading_inside if index == 0 else False
            body = self.region(segment_start, segment_stop, segment_leading, nested)
            negative = self.terms[segment_start].negative if index > 0 else False
            terms.append(SumTerm(body, negative=negative))
        return Sum(tuple(terms))

    def region(self, start: int, stop: int, leading_inside: bool, active: list[_Span]) -> Node:
        covering = [span for span in active if span.start == start and span.stop == stop]
        remaining = [span for span in active if span not in covering]
        if covering:
            return self.wrap(self.region(start, stop, leading_inside, remaining), covering)
        inside = [span for span in remaining if span.start < stop and span.stop > start]
        if not inside:
            return self.plain(start, stop, leading_inside)
        pivot = max(inside, key=lambda span: (span.stop - span.start, -span.start))
        return self.split(start, stop, leading_inside, inside, pivot)


def _render_sum(node: Sum, path: Path, spans: tuple[_Span, ...], context: _RebuildContext) -> Node:
    """Render nested span layers while preserving sign ownership."""

    bodies = [_rebuild(term.body, (*path, "terms", index, "body"), context) for index, term in enumerate(node.terms)]
    return _SumLayout(node.terms, bodies, context.sides).region(0, len(node.terms), True, list(spans))


def render_katex(document: RenderDocument, rules: Iterable[Annotation], *, value: Any = None) -> KatexResult:
    """Render one semantic document with resolved annotations as KaTeX."""

    plan = resolve(document, rules, value=value)
    if not plan.placements:
        return KatexResult(emit(document.body, "latex"), (), plan.missing)
    spans, directs = _collect(plan, document.body)
    labels, sides = _solve((*spans, *directs))
    spans_by_container: dict[Path, list[_Span]] = {}
    for span in spans:
        spans_by_container.setdefault(span.container, []).append(span)
    direct_by_path: dict[Path, list[_Direct]] = {}
    for direct in directs:
        direct_by_path.setdefault(direct.path, []).append(direct)
    context = _RebuildContext(
        {container: tuple(entries) for container, entries in spans_by_container.items()},
        {path: tuple(entries) for path, entries in direct_by_path.items()},
        sides,
    )
    body = _rebuild(document.body, (), context)
    return KatexResult(emit(body, "latex"), labels, plan.missing)
