"""Immutable semantic anchors for optional consumers of value rendering.

Anchors describe layout slots, not character offsets or annotations. Their
node references belong to this document only; rebuild them after changing
presentation. Native blade masks remain independent of labels and ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from typing import Any, Literal

from ..presentation import PresentationConfig
from .tree import Accent, Call, Equality, Identifier, Infix, Node, Postfix, Prefix, Product, Sum


@dataclass(frozen=True, slots=True)
class ContentAnchor:
    """One visible name/expression/result, or a joining equality slot.

    Relation indices identify the following equality part, just as operator
    join indices identify the following operand in a flattened expression.
    """

    kind: Literal["name", "expr", "value", "relation"]
    node: Node
    render_path: tuple[str | int, ...]
    relation_index: int | None = None


@dataclass(frozen=True, slots=True)
class ExpressionAnchor:
    """An original expression occurrence mapped into one displayed location.

    ``render_path`` addresses fields and tuple indices in the document body,
    distinguishing repeated uses of the same layout object. ``start/stop``
    describe a half-open interval of sum terms, product factors or infix
    operands when visual flattening removed the original container.
    ``part`` identifies the operation's explicit layout slot, or ``body``
    for an implicit operator. Whole-expression anchors always use ``body``.
    """

    kind: Literal["expression", "symbol", "operator"]
    path: tuple[int, ...]
    node: Node
    render_path: tuple[str | int, ...]
    part: str = "body"
    start: int | None = None
    stop: int | None = None
    operation_id: str | None = None
    name: str | None = None
    implicit: bool = False
    operator_indices: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderAnchor:
    """One visible component of a concrete multivector.

    For a multi-term sum, ``term`` and ``sign`` refer to ``term_index`` in
    ``node.terms``. For a single term they refer to its whole node and leading
    sign respectively. Coefficient anchors select the displayed magnitude;
    signs have separate anchors. Omitted unit coefficients and leading plus
    signs have no anchor. ``orientation`` is the displayed coefficient sign,
    including the blade label's orientation, not the native coefficient sign.
    """

    kind: Literal["term", "coefficient", "blade", "sign"]
    mask: int
    node: Node
    orientation: int
    term_index: int | None = None
    render_path: tuple[str | int, ...] = ()
    scope: Literal["value", "expr"] = "value"
    expression_path: tuple[int, ...] | None = None

    @property
    def grade(self) -> int:
        """Grade derived from the native blade mask."""
        return self.mask.bit_count()


@dataclass(frozen=True, slots=True)
class RenderDocument:
    """A normal render tree and a separate, ordered tuple of visible anchors."""

    body: Node
    anchors: tuple[RenderAnchor, ...]
    presentation: PresentationConfig
    expression_anchors: tuple[ExpressionAnchor, ...] = ()
    content_anchors: tuple[ContentAnchor, ...] = ()
    target: str | None = None

    def select_content(self, kind: Literal["name", "expr", "value", "relation"]) -> tuple[ContentAnchor, ...]:
        """Select visible display parts or equality slots; hidden parts are empty."""
        if kind not in {"name", "expr", "value", "relation"}:
            raise ValueError("unknown content anchor kind")
        return tuple(anchor for anchor in self.content_anchors if anchor.kind == kind)

    def select_expression(
        self,
        kind: Literal["expression", "symbol", "operator"] = "expression",
        *,
        path: tuple[int, ...] | None = None,
        operation_id: str | None = None,
        name: str | None = None,
    ) -> tuple[ExpressionAnchor, ...]:
        """Select original occurrences, allowing removed content to match nothing."""
        if kind not in {"expression", "symbol", "operator"}:
            raise ValueError("unknown expression anchor kind")
        if path is not None and (
            not isinstance(path, tuple)
            or any(not isinstance(index, int) or isinstance(index, bool) or index < 0 for index in path)
        ):
            raise ValueError("path must be a tuple of non-negative integers")
        return tuple(
            anchor
            for anchor in self.expression_anchors
            if anchor.kind == kind
            and (path is None or anchor.path == path)
            and (operation_id is None or anchor.operation_id == operation_id)
            and (name is None or anchor.name == name)
        )

    def select(
        self,
        kind: Literal["term", "coefficient", "blade", "sign"],
        *,
        mask: int | None = None,
        grade: int | None = None,
        scope: Literal["value", "expr"] = "value",
        path: tuple[int, ...] | None = None,
    ) -> tuple[RenderAnchor, ...]:
        """Select visible anchors; valid selectors may return an empty tuple."""
        if kind not in {"term", "coefficient", "blade", "sign"}:
            raise ValueError("unknown render anchor kind")
        if scope not in {"value", "expr"}:
            raise ValueError("scope must be 'value' or 'expr'")
        if path is not None and (
            scope != "expr"
            or not isinstance(path, tuple)
            or any(not isinstance(index, int) or isinstance(index, bool) or index < 0 for index in path)
        ):
            raise ValueError("path requires expression scope and non-negative integer indices")
        for name, value in (("mask", mask), ("grade", grade)):
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                raise ValueError(f"{name} must be a non-negative integer or None")
        return tuple(
            anchor
            for anchor in self.anchors
            if anchor.kind == kind
            and anchor.scope == scope
            and (path is None or (anchor.expression_path is not None and anchor.expression_path[: len(path)] == path))
            and (mask is None or anchor.mask == mask)
            and (grade is None or anchor.grade == grade)
        )


def value_document(value: Any, presentation: PresentationConfig | None = None) -> RenderDocument:
    """Build visible anchors together with the ordinary concrete value tree.

    This protocol handles concrete facade multivectors. Expression provenance
    and teaching equalities have separate document builders; table and matrix
    adapters are follow-up work. Rendering does not evaluate algebra operations.
    """
    from ._build import _coefficient_tree, _presentation
    from .tree import Sum

    algebra = getattr(value, "algebra", None)
    data = getattr(value, "data", None)
    resolve = getattr(algebra, "resolve_presentation", None)
    if data is None or not callable(resolve):
        raise TypeError("value must be a core-backed facade Multivector")
    selected = _presentation(resolve(presentation))
    components: list[tuple[int, bool, Node | None, Node | None]] = []
    body = _coefficient_tree(
        tuple(float(coefficient) for coefficient in data),
        selected,
        components=components,
        preserve_singleton_sum=True,
    )
    anchors: list[RenderAnchor] = []
    for index, (mask, negative, coefficient, blade) in enumerate(components):
        term_index = index if isinstance(body, Sum) else None
        orientation = -1 if negative else 1
        anchors.append(RenderAnchor("term", mask, body, orientation, term_index))
        if negative or index > 0:
            anchors.append(RenderAnchor("sign", mask, body, orientation, term_index))
        if coefficient is not None:
            anchors.append(RenderAnchor("coefficient", mask, coefficient, orientation))
        if blade is not None:
            anchors.append(RenderAnchor("blade", mask, blade, orientation))
    paths = {id(node): path for node, path in _layout_nodes(body)}
    anchors = [replace(anchor, render_path=paths[id(anchor.node)]) for anchor in anchors]
    return RenderDocument(body, tuple(anchors), selected)


def _layout_nodes(node: Node, path: tuple[str | int, ...] = ()):
    """Visit occurrences, never deduplicating shared nodes by object identity."""
    yield node, path
    if not is_dataclass(node):
        return
    for field in fields(node):
        child = getattr(node, field.name)
        if isinstance(child, Node):
            yield from _layout_nodes(child, (*path, field.name))
        elif isinstance(child, tuple):
            for index, member in enumerate(child):
                if isinstance(member, Node):
                    yield from _layout_nodes(member, (*path, field.name, index))
                elif isinstance(node, Sum) and field.name == "terms":
                    yield from _layout_nodes(member.body, (*path, field.name, index, "body"))


def _sequence(node: Node) -> tuple[Node, ...]:
    if isinstance(node, Sum):
        return tuple(term.body for term in node.terms)
    if isinstance(node, Product):
        return node.factors
    if isinstance(node, Infix):
        return node.operands
    return ()


def _locations(original: Node, nodes):
    direct = [(node, path, None, None) for node, path in nodes if node is original]
    if direct:
        return direct
    from ._build import _unsigned_term

    unsigned, negative = _unsigned_term(original)
    if negative:
        unsigned_sequence = _sequence(unsigned)
        matches = []
        for node, path in nodes:
            if not isinstance(node, Sum):
                continue
            for index, term in enumerate(node.terms):
                if not term.negative:
                    continue
                candidates = _sequence(term.body)
                if term.body is unsigned or (
                    unsigned_sequence
                    and len(candidates) == len(unsigned_sequence)
                    and all(left is right for left, right in zip(unsigned_sequence, candidates, strict=True))
                ):
                    matches.append((node, path, index, index + 1))
        if matches:
            return matches
    if isinstance(original, Prefix) and original.operator.ascii == "-":
        return [
            (node, path, index, index + 1)
            for node, path in nodes
            if isinstance(node, Sum)
            for index, term in enumerate(node.terms)
            if term.body is original.operand and term.negative
        ]
    sequence = _sequence(original)
    if not sequence:
        return []
    locations = []
    for node, path in nodes:
        if type(node) is not type(original):
            continue
        candidates = _sequence(node)
        for start in range(len(candidates) - len(sequence) + 1):
            if all(
                left is right for left, right in zip(sequence, candidates[start : start + len(sequence)], strict=True)
            ):
                locations.append((node, path, start, start + len(sequence)))
    return locations


def _operator_part(node: Node) -> tuple[str, bool]:
    if isinstance(node, Call):
        return "function", False
    if isinstance(node, Product):
        return ("body", True) if node.separator is None else ("separator", False)
    if isinstance(node, Sum):
        return "sign", False
    if isinstance(node, (Infix, Prefix, Postfix)):
        return "operator", False
    if isinstance(node, Accent):
        return "accent", False
    # Fractions, wrappers, scripts and composite definitions need their
    # complete notation extent; they do not have a standalone operator slot.
    return "notation", False


def _literal_anchors(original_node, components, layout_nodes, source_path):
    """Resolve literal components after grouping, flattening and sign absorption."""
    by_path = {path: node for node, path in layout_nodes}
    anchors = []
    for node, layout_path, start, _ in _locations(original_node, layout_nodes):
        for index, (mask, negative, coefficient, blade) in enumerate(components):
            term_node = node
            term_path = layout_path
            term_index = None
            orientation = -1 if negative else 1
            if isinstance(node, Sum):
                term_index = (start or 0) + index
            elif len(layout_path) >= 3 and layout_path[-3] == "terms" and layout_path[-1] == "body":
                parent = by_path[layout_path[:-3]]
                if isinstance(parent, Sum):
                    term_node = parent
                    term_path = layout_path[:-3]
                    term_index = layout_path[-2]
            if isinstance(term_node, Sum) and term_index is not None:
                orientation = -1 if term_node.terms[term_index].negative else 1
                component_prefix = (*term_path, "terms", term_index, "body")
                sign_visible = orientation < 0 or term_index > 0
            else:
                component_prefix = term_path
                sign_visible = negative
            anchors.append(
                RenderAnchor(
                    "term",
                    mask,
                    term_node,
                    orientation,
                    term_index,
                    term_path,
                    scope="expr",
                    expression_path=source_path,
                )
            )
            if sign_visible:
                anchors.append(
                    RenderAnchor(
                        "sign",
                        mask,
                        term_node,
                        orientation,
                        term_index,
                        term_path,
                        scope="expr",
                        expression_path=source_path,
                    )
                )
            for kind, component in (("coefficient", coefficient), ("blade", blade)):
                if component is None:
                    continue
                for located, component_path, _, _ in _locations(component, layout_nodes):
                    if component_path[: len(component_prefix)] == component_prefix:
                        anchors.append(
                            RenderAnchor(
                                kind,
                                mask,
                                located,
                                orientation,
                                render_path=component_path,
                                scope="expr",
                                expression_path=source_path,
                            )
                        )
    return anchors


def expression_document(expression, presentation: PresentationConfig, *, target: str | None = None) -> RenderDocument:
    """Build expression anchors without evaluating or modifying provenance.

    Original binary paths survive presentation flattening as layout intervals.
    Simplified-away operations have no operator anchor. This initial API
    covers expression/symbol/operator occurrences and visible literal
    components. Teaching equalities are built by ``content_document``.
    """
    from ..expression import Call as ExpressionCall
    from ..expression import Expr, Symbol
    from ..expression._simplify import _simplify_with_paths
    from ._build import _expression_tree, _presentation, _target

    if not isinstance(expression, Expr):
        raise TypeError("expression must be an Expr")
    selected = _presentation(presentation)
    _target(target)
    simplified, sources = _simplify_with_paths(expression)
    records: list[tuple[tuple[int, ...], Expr, Node]] = []
    literals: dict[tuple[int, ...], list[tuple[int, bool, Node | None, Node | None]]] = {}
    body = _expression_tree(simplified, selected, target=target, occurrences=records, literal_components=literals)
    rendered = {path: (expr, node) for path, expr, node in records}
    layout_nodes = tuple(_layout_nodes(body))
    # Removed wrappers still have whole-expression extents. Only the deepest
    # original occurrence mapping to a surviving node owns its operation;
    # otherwise add(add(a,b),0) would relabel the surviving inner addition.
    owners: dict[tuple[int, ...], tuple[int, ...]] = {}
    for source_path, render_source in sources.items():
        if render_source not in owners or len(source_path) > len(owners[render_source]):
            owners[render_source] = source_path
    anchors: list[ExpressionAnchor] = []
    components: list[RenderAnchor] = []
    for source_path, render_source in sorted(sources.items()):
        source = expression
        for index in source_path:
            if not isinstance(source, ExpressionCall):  # Internal source-map invariant.
                raise RuntimeError("invalid simplification source path")
            source = source.operands[index]
        current, original_node = rendered[render_source]
        if render_source in literals and owners[render_source] == source_path:
            components.extend(_literal_anchors(original_node, literals[render_source], layout_nodes, source_path))
        for node, layout_path, start, stop in _locations(original_node, layout_nodes):
            anchors.append(ExpressionAnchor("expression", source_path, node, layout_path, start=start, stop=stop))
            if isinstance(source, Symbol) and isinstance(current, Symbol):
                anchors.append(ExpressionAnchor("symbol", source_path, node, layout_path, name=source.identifier))
            if (
                isinstance(source, ExpressionCall)
                and isinstance(current, ExpressionCall)
                and source.operation_id == current.operation_id
                and owners[render_source] == source_path
            ):
                part, implicit = _operator_part(original_node)
                indices: tuple[int, ...] = ()
                if isinstance(node, (Sum, Product, Infix)) and isinstance(original_node, (Sum, Product, Infix)):
                    operand_nodes = [rendered[(*render_source, index)][1] for index in range(len(current.operands))]
                    rule = selected.notation.rule(current.operation_id, target)
                    if rule is not None and rule.argument_order is not None:
                        operand_nodes = [
                            operand_nodes[index] for index in rule.argument_order if index < len(operand_nodes)
                        ]
                    widths = [
                        len(_sequence(operand))
                        if type(operand) is type(original_node)
                        and (
                            isinstance(original_node, Sum)
                            or (
                                rule is not None
                                and rule.flatten
                                and getattr(operand, "operation_id", None) == current.operation_id
                            )
                        )
                        else 1
                        for operand in operand_nodes
                    ]
                    offset = start or 0
                    boundaries = []
                    for width in widths[:-1]:
                        offset += width
                        boundaries.append(offset)
                    indices = tuple(boundaries)
                elif isinstance(node, Sum) and isinstance(original_node, Prefix):
                    part = "sign"
                    indices = (start,) if start is not None else ()
                anchors.append(
                    ExpressionAnchor(
                        "operator",
                        source_path,
                        node,
                        layout_path,
                        part,
                        start,
                        stop,
                        source.operation_id,
                        implicit=implicit,
                        operator_indices=indices,
                    )
                )
    return RenderDocument(body, tuple(components), selected, tuple(anchors), target=target)


def content_document(
    value: Any,
    *,
    content: str | None = None,
    presentation: PresentationConfig | None = None,
    notation=None,
    target: str | None = None,
) -> RenderDocument:
    """Capture visible teaching content and anchors for a specific output target.

    Duplicate equality parts follow the ordinary emitter's first-visible
    policy. Their anchors are omitted, never moved to an identical-looking
    part with different semantics. Rebuild the document for a different target.
    """
    from ..display import _automatic_content, _notation
    from ..expression import Expr
    from ..names import Name
    from ..presenter import PresentedMultivector
    from ._build import _presentation, _target
    from ._emit import _equality_indices

    if isinstance(value, PresentedMultivector):
        presentation = value.presentation if presentation is None else presentation
        value = value.value
    resolve = getattr(getattr(value, "algebra", None), "resolve_presentation", None)
    if not callable(resolve):
        raise TypeError("content_document expects a facade Multivector or PresentedMultivector")
    selected = _presentation(resolve(presentation))
    if notation is not None:
        selected = selected.with_notation(_notation(notation))
    selected_target = selected.display.target if target is None else target
    _target(selected_target)
    selected_content = selected.display.content if content is None else content
    if selected_content == "auto":
        selected_content = _automatic_content(value)
    if selected_content not in {"name", "expr", "value", "full"}:
        raise ValueError("render content must be 'name', 'expr', 'value', or 'full'")
    concrete = value_document(value, selected)
    expression = getattr(value, "expr", None)
    name = getattr(value, "name", None)
    parts: list[tuple[Literal["name", "expr", "value"], RenderDocument]] = []
    if selected_content in {"name", "full"} and isinstance(name, Name):
        parts.append(("name", RenderDocument(Identifier(name), (), selected)))
    if selected_content in {"expr", "full"} and isinstance(expression, Expr):
        parts.append(("expr", expression_document(expression, selected, target=selected_target)))
    if selected_content in {"value", "full"} or not parts:
        parts.append(("value", concrete))
    if len(parts) > 1:
        provisional = Equality(tuple(document.body for _, document in parts))
        parts = [parts[index] for index in _equality_indices(provisional, selected_target)]
    body = parts[0][1].body if len(parts) == 1 else Equality(tuple(document.body for _, document in parts))
    components: list[RenderAnchor] = []
    occurrences: list[ExpressionAnchor] = []
    contents: list[ContentAnchor] = []
    for index, (kind, document) in enumerate(parts):
        prefix: tuple[str | int, ...] = () if len(parts) == 1 else ("parts", index)
        contents.append(ContentAnchor(kind, document.body, prefix))
        components.extend(replace(anchor, render_path=(*prefix, *anchor.render_path)) for anchor in document.anchors)
        occurrences.extend(
            replace(anchor, render_path=(*prefix, *anchor.render_path)) for anchor in document.expression_anchors
        )
        if index:
            contents.append(ContentAnchor("relation", body, (), index))
    return RenderDocument(body, tuple(components), selected, tuple(occurrences), tuple(contents), selected_target)


__all__ = [
    "ContentAnchor",
    "ExpressionAnchor",
    "RenderAnchor",
    "RenderDocument",
    "content_document",
    "expression_document",
    "value_document",
]
