"""First KaTeX annotation renderer (SPEC-015, ADR-142).

The renderer resolves a plan to layout paths, lowers each rule to a
renderer-owned wrapper around the semantic subtree, and emits the decorated
tree through the shared Galaga emitter. Only the LaTeX target is decorated;
plain-text targets keep the undecorated rendering.

Adjacent terms carrying the same rule form a *span layer*: the rule wraps the
whole run once, so a fill stays continuous across internal separators.
External labels and markers are measured against phantom copies and lowered as
independent overlays, so their intervals may nest, cross, or remain disjoint
from content spans.
"""

from __future__ import annotations

from collections.abc import Iterable
from copy import copy as _copy
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from galaga.rendering import Decorated, Node, RenderDocument, Sum, SumTerm, Text, emit

from ._decoration import ResolvedSide, decorate, default_side, external_parts
from .model import DIRECTIONAL_MARKERS, Annotation, AnnotationStyle
from .plan import AnnotationPlan, Placement, resolve

__all__ = ["KatexResult", "LabelPlacement", "SpanLayoutError", "render_katex"]

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
    """Requested span layers cannot be represented without a policy choice."""


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
    include_leading_sign: bool = False


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
    overlays_by_container: dict[Path, tuple[_Span, ...]]
    direct_by_path: dict[Path, tuple[_Direct, ...]]
    sides: dict[_Entry, ResolvedSide]
    signs_by_sum_path: dict[Path, dict[int, tuple[Placement, ...]]]


def _entry_path(entry: _Entry) -> Path:
    if isinstance(entry, _Span):
        return (*entry.container, "terms", entry.start, "body")
    return entry.path


def _has_label(annotation: Annotation) -> bool:
    """Return whether an annotation has either supported label form."""

    return annotation.label is not None or annotation.label_latex is not None


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


def _validate_overlay_channels(overlays: tuple[_Span, ...], sides: dict[_Entry, ResolvedSide]) -> None:
    """Reject overlapping callouts competing for the same vertical channel."""

    for index, left in enumerate(overlays):
        left_side = sides.get(left) or default_side(left.annotation)
        for right in overlays[index + 1 :]:
            if left.container != right.container:
                continue
            right_side = sides.get(right) or default_side(right.annotation)
            if left_side != right_side:
                continue
            disjoint = left.stop <= right.start or right.stop <= left.start
            if not disjoint:
                raise SpanLayoutError(
                    f"annotation spans {left.start}:{left.stop} and {right.start}:{right.stop} in "
                    f"{left.container!r} overlap in the {left_side} channel; use opposite sides or fewer callouts"
                )


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


def _spans_cross(left: _Span, right: _Span) -> bool:
    """Return whether two intervals overlap without being laminar."""

    disjoint = left.stop <= right.start or right.stop <= left.start
    nested = (left.start <= right.start and right.stop <= left.stop) or (
        right.start <= left.start and left.stop <= right.stop
    )
    return not disjoint and not nested


def _validate_spans(spans: list[_Span], container: Path) -> None:
    """Joined spans must nest or stay disjoint; crossing spans are ambiguous."""

    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            if _spans_cross(left, right):
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


def _has_external_decoration(annotation: Annotation) -> bool:
    return _has_label(annotation) or annotation.style.marker != "none"


def _content_only_annotation(annotation: Annotation) -> Annotation | None:
    """Return the body-style part of a callout rule, if it has one."""

    style = annotation.style
    content_color = style.color if style.marker == "none" else None
    if content_color is None and style.background is None and style.border is None and style.emphasis == "normal":
        return None
    return Annotation(
        target=annotation.target,
        role=annotation.role,
        style=AnnotationStyle(
            color=content_color,
            background=style.background,
            border=style.border,
            emphasis=style.emphasis,
        ),
        description=annotation.description,
        missing=annotation.missing,
        join=annotation.join,
    )


def _overlay_only_annotation(annotation: Annotation) -> Annotation:
    """Return the label/marker part of a rule for independent overlay lowering."""

    style = annotation.style
    marker_color = style.color if style.marker != "none" else None
    return Annotation(
        target=annotation.target,
        label=annotation.label,
        label_latex=annotation.label_latex,
        role=annotation.role,
        style=AnnotationStyle(
            color=marker_color,
            label_color=style.label_color,
            marker=style.marker,
            clearance=style.clearance,
            overlay=style.marker != "none",
        ),
        side=annotation.side,
        description=annotation.description,
        missing=annotation.missing,
        join=annotation.join,
    )


def _partition_span_layers(spans: list[_Span]) -> tuple[list[_Span], list[_Span]]:
    """Separate base content styles from independent external callouts.

    Labels and markers do not own visible content. They are overlays measured
    against a phantom copy of their interval, whether their range is equal to,
    nested in, disjoint from, or crossing another interval. Body styles remain
    in the laminar render tree, where crossing fills still require an explicit
    overlap policy.
    """

    body_spans: list[_Span] = []
    overlays: list[_Span] = []
    for span in spans:
        if not _has_external_decoration(span.annotation):
            body_spans.append(span)
            continue
        overlays.append(
            _Span(span.container, span.start, span.stop, _overlay_only_annotation(span.annotation), span.order)
        )
        content = _content_only_annotation(span.annotation)
        if content is not None:
            body_spans.append(_Span(span.container, span.start, span.stop, content, span.order))
    _validate_span_groups(body_spans)
    return body_spans, overlays


def _collect(plan: AnnotationPlan, body: Node) -> tuple[tuple[_Span, ...], tuple[_Span, ...], tuple[_Direct, ...]]:
    """Separate direct placements from contiguous, optionally joined spans."""

    positions = _term_positions(body)
    spans: list[_Span] = []
    directs: list[_Direct] = []
    joinable: dict[tuple[Path, Annotation], list[tuple[int, int]]] = {}
    for path, placements in _placements_by_path(plan).items():
        _record_placements(path, placements, positions, spans, directs, joinable)
    for (container, annotation), entries in joinable.items():
        spans.extend(_contiguous_spans(container, annotation, entries))
    body_spans, overlays = _partition_span_layers(spans)
    _validate_span_groups(body_spans)
    return tuple(body_spans), tuple(overlays), tuple(directs)


def _can_fuse_sign_fill(placement: Placement, span: _Span) -> bool:
    """Return whether a sign-only fill can become a span's leading fill."""

    annotation = placement.annotation
    style = annotation.style
    return (
        annotation.label is None
        and annotation.label_latex is None
        and style.marker == "none"
        and style.color is None
        and style.background is not None
        and style.background == span.annotation.style.background
        and style.border is None
        and style.emphasis == "normal"
    )


def _fuse_leading_sign_fills(
    spans: tuple[_Span, ...],
    sign_slots: dict[Path, dict[int, tuple[Placement, ...]]],
) -> tuple[tuple[_Span, ...], dict[Path, dict[int, tuple[Placement, ...]]]]:
    """Absorb a compatible sign fill into the joined span that follows it.

    A sign and a term body are separate semantic targets, but two adjacent
    ``colorbox`` wrappers cannot form one continuous visual fill.  When a
    sign-only rule requests exactly the background already owned by a joined
    body span, the sign is instead emitted inside that span.  Other sign
    decorations remain independent.
    """

    rebuilt_spans = list(spans)
    rebuilt_slots: dict[Path, dict[int, tuple[Placement, ...]]] = {}
    for container, by_index in sign_slots.items():
        rebuilt_by_index: dict[int, tuple[Placement, ...]] = {}
        for index, placements in by_index.items():
            remaining = list(placements)
            candidates = [
                (span_index, span)
                for span_index, span in enumerate(rebuilt_spans)
                if span.container == container and span.start == index
            ]
            # The narrowest compatible span is the sign's immediate visual
            # owner; any enclosing span will naturally wrap that result.
            candidates.sort(key=lambda entry: (entry[1].stop - entry[1].start, entry[1].order))
            for placement in placements:
                matches = [entry for entry in candidates if _can_fuse_sign_fill(placement, entry[1])]
                if not matches:
                    continue
                span_index, span = matches[0]
                rebuilt_spans[span_index] = _clone_with(span, {"include_leading_sign": True})
                remaining.remove(placement)
                break
            if remaining:
                rebuilt_by_index[index] = tuple(remaining)
        if rebuilt_by_index:
            rebuilt_slots[container] = rebuilt_by_index
    return tuple(rebuilt_spans), rebuilt_slots


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
        side = context.sides.get(entry) or default_side(entry.annotation)
        node = decorate(node, entry.annotation, side)
    return node


def _rebuild(node: Node, path: Path, context: _RebuildContext) -> Node:
    if isinstance(node, Sum):
        signs = context.signs_by_sum_path.get(path)
        if signs is not None:
            node = _apply_signs(node, signs)
    spans = context.spans_by_container.get(path)
    overlays = context.overlays_by_container.get(path)
    if isinstance(node, Sum) and (spans is not None or overlays is not None):
        rebuilt = _render_sum(node, path, spans or (), overlays or (), context)
    else:
        rebuilt = _clone_with(node, _rebuild_fields(node, path, context))
    return _apply_directs(rebuilt, path, context)


def _apply_signs(node: Sum, entries: dict[int, tuple[Placement, ...]]) -> Sum:
    """Replace a term's emitted sign glyph with its decorated annotation."""

    terms = list(node.terms)
    for index, placements in entries.items():
        term = terms[index]
        glyph: Node = Text("-") if term.negative else Text("+")
        for placement in sorted(placements, key=lambda entry: entry.order):
            glyph = decorate(glyph, placement.annotation, default_side(placement.annotation))
        terms[index] = _clone_with(term, {"sign": glyph})
    return _clone_with(node, {"terms": tuple(terms)})


def _partition_signs(
    placements: tuple[Placement, ...],
) -> tuple[dict[Path, dict[int, tuple[Placement, ...]]], tuple[Placement, ...]]:
    """Split sign-slot placements from the term-body layout pipeline."""

    signs: dict[Path, dict[int, list[Placement]]] = {}
    rest: list[Placement] = []
    for placement in placements:
        path = placement.path
        term_index = path[-2] if len(path) >= 3 else None
        if len(path) >= 3 and path[-3] == "terms" and path[-1] == "sign" and isinstance(term_index, int):
            signs.setdefault(path[:-3], {}).setdefault(term_index, []).append(placement)
        else:
            rest.append(placement)
    return {
        path: {index: tuple(entries) for index, entries in by_index.items()} for path, by_index in signs.items()
    }, tuple(rest)


@dataclass(slots=True)
class _SumLayout:
    terms: tuple[SumTerm, ...]
    bodies: list[Node]
    sides: dict[_Entry, ResolvedSide]
    included_leading_signs: frozenset[int]

    def plain(self, start: int, stop: int, leading_inside: bool) -> Node:
        term = self.terms[start]
        if stop - start == 1:
            body = self.bodies[start]
            if leading_inside and (term.negative or term.sign is not None):
                return Sum((SumTerm(body, negative=term.negative, sign=term.sign),))
            return body
        terms = (
            SumTerm(
                self.bodies[index],
                negative=self.terms[index].negative if index > start or leading_inside else False,
                sign=self.terms[index].sign if index > start or leading_inside else None,
            )
            for index in range(start, stop)
        )
        return Sum(tuple(terms))

    def callout_measure(self, start: int, stop: int) -> Node:
        """Reproduce the visible sign class while measuring a callout span."""

        measured = self.plain(start, stop, leading_inside=True)
        term = self.terms[start]
        if not (term.negative or term.sign is not None):
            return measured
        if not isinstance(measured, Sum):
            raise RuntimeError("signed callout measurement must retain its Sum container")
        terms = list(measured.terms)
        first = terms[0]
        # Measurement copies semantic ink, not its decorations.  In
        # particular, a colorbox inside KaTeX's vphantom can still paint its
        # background and cover unrelated visible content at the origin.
        sign = Text("-" if term.negative else "+")
        # Keep the sign glyph ordinary inside the isolated phantom. KaTeX's
        # visible sign atom has one medium-space more horizontal advance than
        # that isolated glyph, for both leading and non-leading signs; retain
        # the same advance so the marker ends at the visible body's far edge.
        measured_sign = Decorated(sign, r"\mathord{", r"}\>")
        terms[0] = _clone_with(first, {"sign": measured_sign})
        return Sum(tuple(terms))

    def wrap(self, body: Node, spans: list[_Span]) -> Node:
        for span in sorted(spans, key=lambda entry: entry.order):
            side = self.sides.get(span) or default_side(span.annotation)
            body = decorate(body, span.annotation, side)
        return body

    def add_overlays(self, overlays: tuple[_Span, ...]) -> tuple[str, ...]:
        """Attach callouts at interval starts and return outer reservations."""

        prefixes: dict[int, list[str]] = {}
        reservations: list[str] = []
        for span in sorted(overlays, key=lambda entry: entry.order):
            # A negative coefficient is part of the annotated component even
            # when its emitted minus also separates it from the preceding sum
            # term.  Measure from that visible sign and attach the callout
            # before it.  Body fills retain their separate policy: adjacent
            # fill spans do not absorb the separator between them.
            term = self.terms[span.start]
            measured = self.callout_measure(span.start, span.stop)
            phantom = Decorated(measured, r"\phantom{", "}")
            side = self.sides.get(span) or default_side(span.annotation)
            reserved, overlaid = external_parts(phantom, span.annotation, side)
            reservations.append(reserved)
            prefixes.setdefault(span.start, []).append(overlaid)
        for start, values in prefixes.items():
            prefix = "".join(values)
            term = self.terms[start]
            if term.negative or term.sign is not None:
                sign = term.sign or Text("-")
                math_class = r"\mathord{" if start == 0 else r"\mathbin{"
                decorated_sign = Decorated(sign, math_class + prefix + r"\mathord{", "}}")
                terms = list(self.terms)
                terms[start] = _clone_with(term, {"sign": decorated_sign})
                self.terms = tuple(terms)
            else:
                self.bodies[start] = Decorated(self.bodies[start], prefix, "")
        return tuple(reservations)

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
            sign_is_inside = segment_start in self.included_leading_signs
            negative = self.terms[segment_start].negative if index > 0 and not sign_is_inside else False
            if index > 0 and sign_is_inside:
                # The nested body emits its own leading sign.  An explicit
                # empty separator prevents the outer Sum from adding a second
                # plus/minus glyph in front of that body.
                sign = Text("")
            else:
                sign = self.terms[segment_start].sign if index > 0 else None
            terms.append(SumTerm(body, negative=negative, sign=sign))
        return Sum(tuple(terms))

    def region(self, start: int, stop: int, leading_inside: bool, active: list[_Span]) -> Node:
        covering = [span for span in active if span.start == start and span.stop == stop]
        remaining = [span for span in active if span not in covering]
        if covering:
            owns_sign = any(span.include_leading_sign for span in covering)
            return self.wrap(self.region(start, stop, leading_inside or owns_sign, remaining), covering)
        inside = [span for span in remaining if span.start < stop and span.stop > start]
        if not inside:
            return self.plain(start, stop, leading_inside)
        pivot = max(inside, key=lambda span: (span.stop - span.start, -span.start))
        return self.split(start, stop, leading_inside, inside, pivot)


def _render_sum(
    node: Sum,
    path: Path,
    spans: tuple[_Span, ...],
    overlays: tuple[_Span, ...],
    context: _RebuildContext,
) -> Node:
    """Render base span layers and independent external callouts."""

    bodies = [_rebuild(term.body, (*path, "terms", index, "body"), context) for index, term in enumerate(node.terms)]
    included_leading_signs = frozenset(span.start for span in spans if span.include_leading_sign)
    layout = _SumLayout(node.terms, bodies, context.sides, included_leading_signs)
    reservations = layout.add_overlays(overlays)
    rendered = layout.region(0, len(node.terms), True, list(spans))
    if reservations:
        rendered = Decorated(rendered, "".join(reservations), "")
    return rendered


def render_katex(document: RenderDocument, rules: Iterable[Annotation], *, value: Any = None) -> KatexResult:
    """Render one semantic document with resolved annotations as KaTeX."""

    plan = resolve(document, rules, value=value)
    if not plan.placements:
        return KatexResult(emit(document.body, "latex"), (), plan.missing)
    sign_slots, term_body_placements = _partition_signs(plan.placements)
    spans, overlays, directs = _collect(AnnotationPlan(term_body_placements, plan.missing), document.body)
    spans, sign_slots = _fuse_leading_sign_fills(spans, sign_slots)
    labels, sides = _solve((*overlays, *directs))
    _validate_overlay_channels(overlays, sides)
    spans_by_container: dict[Path, list[_Span]] = {}
    for span in spans:
        spans_by_container.setdefault(span.container, []).append(span)
    overlays_by_container: dict[Path, list[_Span]] = {}
    for overlay in overlays:
        overlays_by_container.setdefault(overlay.container, []).append(overlay)
    direct_by_path: dict[Path, list[_Direct]] = {}
    for direct in directs:
        direct_by_path.setdefault(direct.path, []).append(direct)
    context = _RebuildContext(
        {container: tuple(entries) for container, entries in spans_by_container.items()},
        {container: tuple(entries) for container, entries in overlays_by_container.items()},
        {path: tuple(entries) for path, entries in direct_by_path.items()},
        sides,
        sign_slots,
    )
    body = _rebuild(document.body, (), context)
    return KatexResult(emit(body, "latex"), labels, plan.missing)
