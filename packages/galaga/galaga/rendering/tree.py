"""Format-neutral semantic layout nodes for Galaga 2 rendering.

The tree records mathematical layout, not an output syntax.  In particular,
it contains no Unicode-only glyphs, LaTeX fragments, or calls into the numeric
engine.  Builders decide precedence once by inserting :class:`Group` nodes;
all emitters then serialize the same unambiguous structure.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from numbers import Integral, Real
from typing import Any

from ..names import Name


class Precedence(IntEnum):
    """Shared binding strengths used by notation rules and tree builders."""

    EQUALITY = 10
    SUM = 20
    PRODUCT = 30
    PREFIX = 40
    POWER = 50
    POSTFIX = 60
    CALL = 80
    ATOM = 100


class Associativity(StrEnum):
    """How an operation groups children at the same precedence."""

    NONE = "none"
    LEFT = "left"
    RIGHT = "right"
    ASSOCIATIVE = "associative"


class Node:
    """Marker base for immutable semantic render nodes."""

    __slots__ = ()

    @property
    def precedence(self) -> int:
        raise NotImplementedError


def _name(value: Name | str, *, field: str) -> Name:
    if isinstance(value, Name):
        return value
    if isinstance(value, str):
        return Name(value)
    raise TypeError(f"{field} must be a Name or string")


def _node(value: Any, *, field: str) -> Node:
    if not isinstance(value, Node):
        raise TypeError(f"{field} must be a semantic render node")
    return value


def _nodes(values: Any, *, field: str, minimum: int = 1) -> tuple[Node, ...]:
    try:
        normalized = tuple(values)
    except TypeError:
        raise TypeError(f"{field} must be an iterable of semantic render nodes") from None
    if len(normalized) < minimum:
        raise ValueError(f"{field} must contain at least {minimum} node(s)")
    if any(not isinstance(value, Node) for value in normalized):
        raise TypeError(f"{field} must contain only semantic render nodes")
    return normalized


def _precedence(value: Any) -> int:
    if not isinstance(value, Integral) or isinstance(value, bool):
        raise TypeError("precedence must be an integer")
    normalized = int(value)
    if normalized < 0:
        raise ValueError("precedence must be non-negative")
    return normalized


def _associativity(value: Associativity | str) -> Associativity:
    try:
        return Associativity(value)
    except (TypeError, ValueError):
        raise ValueError("associativity must be 'none', 'left', 'right', or 'associative'") from None


@dataclass(frozen=True, slots=True, init=False)
class Identifier(Node):
    """A semantic mathematical name with target-specific spellings."""

    name: Name

    def __init__(self, name: Name | str) -> None:
        object.__setattr__(self, "name", _name(name, field="identifier name"))

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class Literal(Node):
    """A finite numeric literal."""

    value: int | float
    precision: int

    def __init__(self, value: int | float, *, precision: int = 6) -> None:
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError("literal value must be a real number")
        if not isinstance(precision, Integral) or isinstance(precision, bool):
            raise TypeError("literal precision must be an integer")
        if not 1 <= precision <= 17:
            raise ValueError("literal precision must be between 1 and 17")
        normalized: int | float
        if isinstance(value, Integral):
            normalized = int(value)
        else:
            normalized = float(value)
            if not math.isfinite(normalized):
                raise ValueError("literal value must be finite")
            if normalized == 0:
                normalized = 0.0
        object.__setattr__(self, "value", normalized)
        object.__setattr__(self, "precision", int(precision))

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class Text(Node):
    """Ordinary text that an emitter must escape for its target."""

    value: str

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("text value must be a string")
        object.__setattr__(self, "value", value)

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class Group(Node):
    """Explicit grouping chosen by the shared precedence model."""

    body: Node

    def __init__(self, body: Node) -> None:
        object.__setattr__(self, "body", _node(body, field="group body"))

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class SumTerm:
    """One signed term in a :class:`Sum`."""

    body: Node
    negative: bool

    def __init__(self, body: Node, negative: bool = False) -> None:
        if not isinstance(negative, bool):
            raise TypeError("sum-term negative flag must be a boolean")
        object.__setattr__(self, "body", _node(body, field="sum-term body"))
        object.__setattr__(self, "negative", negative)


@dataclass(frozen=True, slots=True, init=False)
class Sum(Node):
    """A non-empty ordered sum with explicit term signs."""

    terms: tuple[SumTerm, ...]

    def __init__(self, terms: Any) -> None:
        try:
            normalized = tuple(terms)
        except TypeError:
            raise TypeError("sum terms must be an iterable of SumTerm values") from None
        if not normalized:
            raise ValueError("a sum must contain at least one term")
        if any(not isinstance(term, SumTerm) for term in normalized):
            raise TypeError("sum terms must contain only SumTerm values")
        object.__setattr__(self, "terms", normalized)

    @property
    def precedence(self) -> int:
        return Precedence.SUM


@dataclass(frozen=True, slots=True, init=False)
class Product(Node):
    """An ordered product, with optional explicit separator glyph."""

    factors: tuple[Node, ...]
    separator: Name | None
    binding: int
    associativity: Associativity
    operation_id: str | None

    def __init__(
        self,
        factors: Any,
        *,
        separator: Name | str | None = None,
        precedence: int = Precedence.PRODUCT,
        associativity: Associativity | str = Associativity.ASSOCIATIVE,
        operation_id: str | None = None,
    ) -> None:
        if operation_id is not None and (not isinstance(operation_id, str) or not operation_id):
            raise ValueError("product operation id must be a non-empty string or None")
        object.__setattr__(self, "factors", _nodes(factors, field="product factors"))
        object.__setattr__(
            self,
            "separator",
            None if separator is None else _name(separator, field="product separator"),
        )
        object.__setattr__(self, "binding", _precedence(precedence))
        object.__setattr__(self, "associativity", _associativity(associativity))
        object.__setattr__(self, "operation_id", operation_id)

    @property
    def precedence(self) -> int:
        return self.binding


@dataclass(frozen=True, slots=True, init=False)
class Fraction(Node):
    """A numerator over a denominator."""

    numerator: Node
    denominator: Node

    def __init__(self, numerator: Node, denominator: Node) -> None:
        object.__setattr__(self, "numerator", _node(numerator, field="fraction numerator"))
        object.__setattr__(self, "denominator", _node(denominator, field="fraction denominator"))

    @property
    def precedence(self) -> int:
        return Precedence.PRODUCT


@dataclass(frozen=True, slots=True, init=False)
class Power(Node):
    """A base with a semantic superscript."""

    base: Node
    exponent: Node

    def __init__(self, base: Node, exponent: Node) -> None:
        object.__setattr__(self, "base", _node(base, field="power base"))
        object.__setattr__(self, "exponent", _node(exponent, field="power exponent"))

    @property
    def precedence(self) -> int:
        return Precedence.POWER


@dataclass(frozen=True, slots=True, init=False)
class Subscript(Node):
    """A base with a semantic subscript."""

    base: Node
    subscript: Node

    def __init__(self, base: Node, subscript: Node) -> None:
        object.__setattr__(self, "base", _node(base, field="subscript base"))
        object.__setattr__(self, "subscript", _node(subscript, field="subscript value"))

    @property
    def precedence(self) -> int:
        return Precedence.POSTFIX


@dataclass(frozen=True, slots=True, init=False)
class Call(Node):
    """A semantic function application."""

    function: Name
    arguments: tuple[Node, ...]
    scalable: bool

    def __init__(self, function: Name | str, arguments: Any = (), *, scalable: bool = True) -> None:
        if not isinstance(scalable, bool):
            raise TypeError("call scalable flag must be a boolean")
        object.__setattr__(self, "function", _name(function, field="function name"))
        object.__setattr__(self, "arguments", _nodes(arguments, field="call arguments", minimum=0))
        object.__setattr__(self, "scalable", scalable)

    @property
    def precedence(self) -> int:
        return Precedence.CALL


@dataclass(frozen=True, slots=True, init=False)
class Prefix(Node):
    """A prefix operator applied to one operand."""

    operator: Name
    operand: Node
    binding: int

    def __init__(self, operator: Name | str, operand: Node, *, precedence: int = Precedence.PREFIX) -> None:
        object.__setattr__(self, "operator", _name(operator, field="prefix operator"))
        object.__setattr__(self, "operand", _node(operand, field="prefix operand"))
        object.__setattr__(self, "binding", _precedence(precedence))

    @property
    def precedence(self) -> int:
        return self.binding


@dataclass(frozen=True, slots=True, init=False)
class Postfix(Node):
    """A postfix operator applied to one operand."""

    operand: Node
    operator: Name
    binding: int

    def __init__(self, operand: Node, operator: Name | str, *, precedence: int = Precedence.POSTFIX) -> None:
        object.__setattr__(self, "operand", _node(operand, field="postfix operand"))
        object.__setattr__(self, "operator", _name(operator, field="postfix operator"))
        object.__setattr__(self, "binding", _precedence(precedence))

    @property
    def precedence(self) -> int:
        return self.binding


@dataclass(frozen=True, slots=True, init=False)
class Infix(Node):
    """An ordered infix application with shared precedence metadata."""

    operands: tuple[Node, ...]
    operator: Node
    binding: int
    associativity: Associativity
    operation_id: str | None

    def __init__(
        self,
        operands: Any,
        operator: Node | Name | str,
        *,
        precedence: int = Precedence.PRODUCT,
        associativity: Associativity | str = Associativity.NONE,
        operation_id: str | None = None,
    ) -> None:
        if operation_id is not None and (not isinstance(operation_id, str) or not operation_id):
            raise ValueError("infix operation id must be a non-empty string or None")
        selected_operator = operator if isinstance(operator, Node) else Identifier(operator)
        object.__setattr__(self, "operands", _nodes(operands, field="infix operands", minimum=2))
        object.__setattr__(self, "operator", selected_operator)
        object.__setattr__(self, "binding", _precedence(precedence))
        object.__setattr__(self, "associativity", _associativity(associativity))
        object.__setattr__(self, "operation_id", operation_id)

    @property
    def precedence(self) -> int:
        return self.binding


@dataclass(frozen=True, slots=True, init=False)
class Accent(Node):
    """An over- or under-accent with target-specific glyph spellings."""

    body: Node
    accent: Name
    position: str

    def __init__(self, body: Node, accent: Name | str, *, position: str = "over") -> None:
        if position not in {"over", "under"}:
            raise ValueError("accent position must be 'over' or 'under'")
        object.__setattr__(self, "body", _node(body, field="accent body"))
        object.__setattr__(self, "accent", _name(accent, field="accent name"))
        object.__setattr__(self, "position", position)

    @property
    def precedence(self) -> int:
        return Precedence.POSTFIX


@dataclass(frozen=True, slots=True, init=False)
class Underset(Node):
    """An annotation placed beneath a mathematical body when supported."""

    body: Node
    annotation: Node

    def __init__(self, body: Node, annotation: Node) -> None:
        object.__setattr__(self, "body", _node(body, field="underset body"))
        object.__setattr__(self, "annotation", _node(annotation, field="underset annotation"))

    @property
    def precedence(self) -> int:
        return Precedence.POSTFIX


@dataclass(frozen=True, slots=True, init=False)
class MathClass(Node):
    """Assign a TeX math class without contaminating the semantic body."""

    body: Node
    kind: str

    def __init__(self, body: Node, kind: str) -> None:
        if kind not in {"binary"}:
            raise ValueError("math class must be 'binary'")
        object.__setattr__(self, "body", _node(body, field="math-class body"))
        object.__setattr__(self, "kind", kind)

    @property
    def precedence(self) -> int:
        return self.body.precedence


@dataclass(frozen=True, slots=True, init=False)
class Wrapper(Node):
    """A body delimited by semantic open and close glyphs."""

    body: Node
    opening: Name
    closing: Name
    scalable: bool

    def __init__(self, body: Node, opening: Name | str, closing: Name | str, *, scalable: bool = True) -> None:
        if not isinstance(scalable, bool):
            raise TypeError("wrapper scalable flag must be a boolean")
        object.__setattr__(self, "body", _node(body, field="wrapper body"))
        object.__setattr__(self, "opening", _name(opening, field="wrapper opening"))
        object.__setattr__(self, "closing", _name(closing, field="wrapper closing"))
        object.__setattr__(self, "scalable", scalable)

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class Delimited(Node):
    """A comma-separated sequence inside semantic delimiters."""

    items: tuple[Node, ...]
    opening: Name
    closing: Name
    separator: Name
    scalable: bool

    def __init__(
        self,
        items: Any,
        *,
        opening: Name | str = "(",
        closing: Name | str = ")",
        separator: Name | str = ", ",
        scalable: bool = True,
    ) -> None:
        if not isinstance(scalable, bool):
            raise TypeError("delimiter scalable flag must be a boolean")
        object.__setattr__(self, "items", _nodes(items, field="delimited items", minimum=0))
        object.__setattr__(self, "opening", _name(opening, field="delimiter opening"))
        object.__setattr__(self, "closing", _name(closing, field="delimiter closing"))
        object.__setattr__(self, "separator", _name(separator, field="delimiter separator"))
        object.__setattr__(self, "scalable", scalable)

    @property
    def precedence(self) -> int:
        return Precedence.ATOM


@dataclass(frozen=True, slots=True, init=False)
class Equality(Node):
    """A teaching equality joining two or more independently built forms."""

    parts: tuple[Node, ...]

    def __init__(self, parts: Any) -> None:
        object.__setattr__(self, "parts", _nodes(parts, field="equality parts", minimum=2))

    @property
    def precedence(self) -> int:
        return Precedence.EQUALITY


def grouped_child(
    child: Node,
    *,
    parent_precedence: int,
    associativity: Associativity | str = Associativity.NONE,
    side: str = "only",
    operation_id: str | None = None,
) -> Node:
    """Apply the single shared parenthesization rule to one child.

    ``operation_id`` is used only to recognize a repeated associative
    operation.  Equal-precedence operations with different identities remain
    grouped, which avoids silently treating subtraction as addition or one
    geometric-algebra product as another.
    """

    selected = _node(child, field="precedence child")
    parent = _precedence(parent_precedence)
    selected_associativity = _associativity(associativity)
    if side not in {"left", "right", "middle", "only"}:
        raise ValueError("child side must be 'left', 'right', 'middle', or 'only'")
    if isinstance(selected, Group) or selected.precedence > parent:
        return selected
    if selected.precedence < parent:
        return Group(selected)

    child_operation = getattr(selected, "operation_id", None)
    same_operation = operation_id is not None and child_operation == operation_id
    if selected_associativity is Associativity.ASSOCIATIVE and same_operation:
        return selected
    if selected_associativity is Associativity.LEFT and side == "left" and same_operation:
        return selected
    if selected_associativity is Associativity.RIGHT and side == "right" and same_operation:
        return selected
    return Group(selected)


__all__ = [
    "Accent",
    "Associativity",
    "Call",
    "Delimited",
    "Equality",
    "Fraction",
    "Group",
    "Identifier",
    "Infix",
    "Literal",
    "MathClass",
    "Node",
    "Postfix",
    "Power",
    "Precedence",
    "Prefix",
    "Product",
    "Subscript",
    "Sum",
    "SumTerm",
    "Text",
    "Underset",
    "Wrapper",
    "grouped_child",
]
