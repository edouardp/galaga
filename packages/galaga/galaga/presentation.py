"""Immutable presentation and complete algebra configuration models."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from numbers import Integral, Real
from typing import cast

from .blades import BladeConvention, BladeRef, DisplayOrder, LocalNamePolicy
from .names import Name

_RULE_KINDS = {
    "accent",
    "fraction",
    "function",
    "infix",
    "juxtaposition",
    "metric_regressive",
    "postfix",
    "prefix",
    "sandwich",
    "subscript",
    "superscript",
    "underaccent",
    "wrapper",
}
_RULE_ASSOCIATIVITY = {"none", "left", "right", "associative"}
_RULE_TARGETS = {"ascii", "unicode", "latex"}
_DEFAULT_PRECEDENCE = {
    "function": 80,
    "wrapper": 80,
    "postfix": 60,
    "accent": 60,
    "underaccent": 60,
    "subscript": 60,
    "superscript": 50,
    "prefix": 40,
    "fraction": 30,
    "infix": 30,
    "juxtaposition": 30,
    "metric_regressive": 30,
    "sandwich": 30,
}


def _render_name(value: Name | str | None, *, field: str) -> Name | None:
    if value is None or isinstance(value, Name):
        return value
    if isinstance(value, str):
        return Name(value)
    raise TypeError(f"{field} must be a Name, string, or None")


@dataclass(frozen=True, slots=True, init=False)
class RenderRule:
    """One immutable semantic layout choice for a stable operation ID.

    A rule can be generic or installed for one output target.  Target-specific
    rules are useful when a notation has no honest plain-text equivalent for a
    compact mathematical glyph.  The rule still produces format-neutral tree
    nodes; escaping and final glyph emission remain emitter concerns.
    """

    kind: str
    symbol: Name | None
    precedence: int
    associativity: str
    parameter: str | None
    argument_order: tuple[int, ...] | None
    opening: Name | None
    closing: Name | None
    flatten: bool
    scalable: bool
    script_style: bool
    group_operand: bool
    parameter_position: str

    def __init__(
        self,
        kind: str,
        *,
        symbol: Name | str | None = None,
        precedence: int | None = None,
        associativity: str = "none",
        parameter: str | None = None,
        argument_order: Iterable[int] | None = None,
        opening: Name | str | None = None,
        closing: Name | str | None = None,
        flatten: bool = False,
        scalable: bool = True,
        script_style: bool = False,
        group_operand: bool = True,
        parameter_position: str = "subscript",
    ) -> None:
        if kind not in _RULE_KINDS:
            expected = ", ".join(sorted(_RULE_KINDS))
            raise ValueError(f"render-rule kind must be one of: {expected}")
        selected_symbol = _render_name(symbol, field="render-rule symbol")
        selected_opening = _render_name(opening, field="render-rule opening")
        selected_closing = _render_name(closing, field="render-rule closing")
        required_symbol = {"accent", "function", "infix", "postfix", "prefix", "underaccent"}
        if kind in required_symbol and selected_symbol is None:
            raise ValueError(f"{kind} render rules require a symbol")
        if kind == "wrapper" and (selected_opening is None or selected_closing is None):
            raise ValueError("wrapper render rules require opening and closing names")
        selected_precedence = _DEFAULT_PRECEDENCE[kind] if precedence is None else precedence
        if not isinstance(selected_precedence, int) or isinstance(selected_precedence, bool):
            raise TypeError("render-rule precedence must be an integer")
        if selected_precedence < 0:
            raise ValueError("render-rule precedence must be non-negative")
        if associativity not in _RULE_ASSOCIATIVITY:
            raise ValueError("render-rule associativity must be 'none', 'left', 'right', or 'associative'")
        if parameter is not None and (not isinstance(parameter, str) or not parameter):
            raise ValueError("render-rule parameter must be a non-empty string or None")
        selected_order = None if argument_order is None else tuple(argument_order)
        if selected_order is not None:
            if any(not isinstance(index, int) or isinstance(index, bool) or index < 0 for index in selected_order):
                raise ValueError("render-rule argument order must contain non-negative integers")
            if len(set(selected_order)) != len(selected_order):
                raise ValueError("render-rule argument order must not repeat an index")
        if not isinstance(flatten, bool):
            raise TypeError("render-rule flatten flag must be a boolean")
        if not isinstance(scalable, bool):
            raise TypeError("render-rule scalable flag must be a boolean")
        if not isinstance(script_style, bool):
            raise TypeError("render-rule script_style flag must be a boolean")
        if script_style and kind != "wrapper":
            raise ValueError("script_style is supported only by wrapper render rules")
        if not isinstance(group_operand, bool):
            raise TypeError("render-rule group_operand flag must be a boolean")
        if parameter_position not in {"subscript", "underscript"}:
            raise ValueError("render-rule parameter_position must be 'subscript' or 'underscript'")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "symbol", selected_symbol)
        object.__setattr__(self, "precedence", selected_precedence)
        object.__setattr__(self, "associativity", associativity)
        object.__setattr__(self, "parameter", parameter)
        object.__setattr__(self, "argument_order", selected_order)
        object.__setattr__(self, "opening", selected_opening)
        object.__setattr__(self, "closing", selected_closing)
        object.__setattr__(self, "flatten", flatten)
        object.__setattr__(self, "scalable", scalable)
        object.__setattr__(self, "script_style", script_style)
        object.__setattr__(self, "group_operand", group_operand)
        object.__setattr__(self, "parameter_position", parameter_position)


@dataclass(frozen=True, slots=True, init=False)
class Notation:
    """Immutable rendering rules keyed by stable operation ID and target."""

    id: str
    tokens: tuple[tuple[str, str], ...]
    rules: tuple[tuple[str, str | None, RenderRule], ...]

    def __init__(
        self,
        id: str = "default",
        tokens: Mapping[str, str] | Iterable[tuple[str, str]] = (),
        *,
        rules: (
            Mapping[str | tuple[str, str], RenderRule] | Iterable[tuple[str | tuple[str, str], RenderRule]] | None
        ) = None,
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise ValueError("notation id must be a non-empty string")
        items: tuple[tuple[str, str], ...]
        if isinstance(tokens, Mapping):
            items = tuple(cast(Mapping[str, str], tokens).items())
        else:
            items = tuple(tokens)
        seen: set[str] = set()
        normalized: list[tuple[str, str]] = []
        for operation_id, token in items:
            if not isinstance(operation_id, str) or not isinstance(token, str) or not operation_id or not token:
                raise ValueError("notation operation ids and tokens must be non-empty strings")
            if operation_id in seen:
                raise ValueError(f"duplicate notation token for {operation_id!r}")
            seen.add(operation_id)
            normalized.append((operation_id, token))
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "tokens", tuple(normalized))

        rule_items: Iterable[tuple[str | tuple[str, str], RenderRule]]
        if rules is None:
            rule_items = _conventional_rules().items()
        elif isinstance(rules, Mapping):
            rule_items = cast(Mapping[str | tuple[str, str], RenderRule], rules).items()
        else:
            rule_items = rules
        normalized_rules: list[tuple[str, str | None, RenderRule]] = []
        rule_keys: set[tuple[str, str | None]] = set()
        for key, rule in rule_items:
            if isinstance(key, tuple):
                if len(key) != 2:
                    raise ValueError("target-specific notation keys must be (operation_id, target) pairs")
                operation_id, target = key
            else:
                operation_id, target = key, None
            if not isinstance(operation_id, str) or not operation_id:
                raise ValueError("notation rule operation ids must be non-empty strings")
            if target is not None and target not in _RULE_TARGETS:
                raise ValueError("notation rule target must be 'ascii', 'unicode', or 'latex'")
            if not isinstance(rule, RenderRule):
                raise TypeError("notation rules must be RenderRule values")
            normalized_key = (operation_id, target)
            if normalized_key in rule_keys:
                raise ValueError(f"duplicate notation rule for {operation_id!r} and target {target!r}")
            rule_keys.add(normalized_key)
            normalized_rules.append((operation_id, target, rule))
        object.__setattr__(self, "rules", tuple(normalized_rules))

    def token(self, operation_id: str, default: str | None = None) -> str | None:
        """Return legacy token metadata without selecting layout semantics."""
        return dict(self.tokens).get(operation_id, default)

    def rule(self, operation_id: str, target: str | None = None) -> RenderRule | None:
        """Resolve a target-specific rule, then its target-neutral fallback."""
        if target is not None and target not in _RULE_TARGETS:
            raise ValueError("notation target must be 'ascii', 'unicode', or 'latex'")
        lookup = {(identifier, selected_target): rule for identifier, selected_target, rule in self.rules}
        return lookup.get((operation_id, target)) or lookup.get((operation_id, None))

    def with_rule(
        self,
        operation_id: str,
        rule: RenderRule,
        *,
        target: str | None = None,
    ) -> Notation:
        """Return a notation with one generic or target-specific rule replaced."""
        key: str | tuple[str, str]
        if target is None:
            key = operation_id
        else:
            if target not in _RULE_TARGETS:
                raise ValueError("notation rule target must be 'ascii', 'unicode', or 'latex'")
            key = (operation_id, target)
        retained = {
            (identifier if selected_target is None else (identifier, selected_target)): selected_rule
            for identifier, selected_target, selected_rule in self.rules
            if (identifier, selected_target) != (operation_id, target)
        }
        retained[key] = rule
        return Notation(self.id, self.tokens, rules=retained)

    @classmethod
    def default(cls, *, id: str = "default") -> Notation:
        """Conventional Galaga notation with explicit operation identities."""
        return cls(id, rules=_conventional_rules())

    @classmethod
    def functional(cls, *, short: bool = False) -> Notation:
        """Long canonical function calls, or an optional unambiguous short form."""
        if not short:
            return cls("functional-long", rules=())
        rules: dict[str | tuple[str, str], RenderRule] = {
            operation_id: RenderRule("function", symbol=short_name)
            for operation_id, short_name in _SHORT_FUNCTION_NAMES.items()
        }
        return cls("functional-short", rules=rules)

    @classmethod
    def functional_short(cls) -> Notation:
        """Compatibility spelling for :meth:`functional(short=True)`."""
        return cls.functional(short=True)

    @classmethod
    def doran_lasenby(cls) -> Notation:
        """Doran-Lasenby teaching notation; other inner products stay named."""
        rules = _conventional_rules()
        rules["doran_lasenby_inner"] = RenderRule(
            "infix",
            symbol=Name("|", "·", r"\cdot"),
            precedence=30,
            associativity="none",
        )
        rules["hestenes_inner"] = RenderRule("function", symbol="hestenes_inner", scalable=False)
        rules.pop(("hestenes_inner", "latex"), None)
        return cls("doran-lasenby", rules=rules)

    @classmethod
    def hestenes(cls) -> Notation:
        """Hestenes teaching notation; competing inner products stay named."""
        rules = _conventional_rules()
        rules["reverse"] = RenderRule("postfix", symbol=Name("dag", "†", r"^{\dagger}"))
        rules["hestenes_inner"] = RenderRule(
            "infix",
            symbol=Name("dot", "·", r"\cdot"),
            precedence=30,
            associativity="none",
        )
        rules["doran_lasenby_inner"] = RenderRule("function", symbol="doran_lasenby_inner")
        return cls("hestenes", rules=rules)

    @classmethod
    def lengyel(cls) -> Notation:
        """Eric Lengyel/RGA notation, with an honest functional ASCII form."""
        return cls("lengyel-rga", rules=_lengyel_rules())

    @classmethod
    def lengyel_rga(cls) -> Notation:
        """Explicit alias for :meth:`lengyel`."""
        return cls.lengyel()


_SHORT_FUNCTION_NAMES = {
    "antidot_product": "antidot",
    "doran_lasenby_inner": "dl_inner",
    "geometric_antiproduct": "gap",
    "geometric_product": "gp",
    "grade_involution": "invol",
    "hestenes_inner": "h_inner",
    "left_contraction": "lc",
    "left_interior_product": "l_interior",
    "metric_inner_product": "metric_inner",
    "outer_product": "op",
    "regressive_product": "meet",
    "reverse": "rev",
    "right_contraction": "rc",
    "right_interior_product": "r_interior",
    "scalar_product": "sp",
    "sandwich": "sw",
    "transwedge": "tw",
    "transwedge_antiproduct": "antitw",
}


def _conventional_rules() -> dict[str | tuple[str, str], RenderRule]:
    """Build a fresh conventional rule map so presets never share state."""

    def compact_function(name: str) -> RenderRule:
        return RenderRule("function", symbol=name, scalable=False)

    rules: dict[str | tuple[str, str], RenderRule] = {
        "add": RenderRule("infix", symbol="+", precedence=20, associativity="associative", flatten=True),
        "subtract": RenderRule("infix", symbol="-", precedence=20, associativity="left"),
        "negate": RenderRule("prefix", symbol="-", precedence=40),
        "scalar_multiply": RenderRule(
            "juxtaposition",
            precedence=25,
            argument_order=(1, 0),
        ),
        "scalar_divide": RenderRule("fraction"),
        "power": RenderRule("superscript", associativity="right"),
        "geometric_product": RenderRule(
            "juxtaposition",
            precedence=30,
            associativity="associative",
            flatten=True,
        ),
        "outer_product": RenderRule(
            "infix",
            symbol=Name("^", "∧", r"\wedge"),
            precedence=30,
            associativity="associative",
            flatten=True,
        ),
        "doran_lasenby_inner": RenderRule(
            "infix",
            symbol=Name("|", "·", r"\cdot"),
            precedence=30,
        ),
        "left_contraction": RenderRule(
            "infix",
            symbol=Name("_|", "⌋", r"\;\lrcorner\;"),
            precedence=30,
        ),
        "right_contraction": RenderRule(
            "infix",
            symbol=Name("|_", "⌊", r"\;\llcorner\;"),
            precedence=30,
        ),
        "hestenes_inner": compact_function("hestenes_inner"),
        ("hestenes_inner", "latex"): RenderRule(
            "infix",
            symbol=Name(".", "·", r"\cdot"),
            precedence=30,
        ),
        "scalar_product": RenderRule("infix", symbol="*", precedence=30),
        "commutator": RenderRule("wrapper", opening="[", closing="]", scalable=False),
        "lie_bracket": RenderRule("wrapper", opening="[", closing="]", scalable=False),
        "anticommutator": RenderRule(
            "wrapper",
            opening=Name("{", "{", r"\{"),
            closing=Name("}", "}", r"\}"),
            scalable=False,
        ),
        "jordan_product": RenderRule(
            "wrapper",
            opening=Name("{", "{", r"\{"),
            closing=Name("}", "}", r"\}"),
            scalable=False,
        ),
        "half_commutator": RenderRule(
            "wrapper",
            opening=Name("1/2[", "½[", r"\tfrac{1}{2}["),
            closing="]",
            scalable=False,
        ),
        "half_anticommutator": RenderRule(
            "wrapper",
            opening=Name("1/2{", "½{", r"\tfrac{1}{2}\{"),
            closing=Name("}", "}", r"\}"),
            scalable=False,
        ),
        "grade": RenderRule(
            "wrapper",
            opening=Name("<", "⟨", r"\langle "),
            closing=Name(">", "⟩", r" \rangle"),
            parameter="target",
            scalable=False,
        ),
        "grades": RenderRule(
            "wrapper",
            opening=Name("<", "⟨", r"\langle "),
            closing=Name(">", "⟩", r" \rangle"),
            parameter="targets",
            scalable=False,
        ),
        "reverse": RenderRule("accent", symbol=Name("~", "\u0303", r"\widetilde")),
        ("reverse", "latex"): RenderRule(
            "accent",
            symbol=Name("~", "\u0303", r"\widetilde"),
            group_operand=False,
        ),
        "grade_involution": RenderRule("accent", symbol=Name("hat", "\u0302", r"\widehat")),
        "conjugate": RenderRule("accent", symbol=Name("bar", "\u0305", r"\overline")),
        ("conjugate", "latex"): RenderRule(
            "accent",
            symbol=Name("bar", "\u0305", r"\overline"),
            group_operand=False,
        ),
        "inverse": RenderRule("superscript", symbol=Name("-1", "⁻¹", "-1")),
        "squared": RenderRule("superscript", symbol=Name("2", "²", "2")),
        "dual": RenderRule("superscript", symbol=Name("*", "★", "*")),
        "undual": RenderRule("superscript", symbol=Name("*^-1", "★⁻¹", r"*^{-1}")),
        "complement": RenderRule(
            "superscript",
            symbol=Name("c", "ᶜ", r"\complement"),
        ),
        "right_complement": RenderRule(
            "superscript",
            symbol=Name("c", "ᶜ", r"\complement"),
        ),
        "uncomplement": RenderRule(
            "superscript",
            symbol=Name("c^-1", "ᶜ⁻¹", r"\complement^{-1}"),
        ),
        "left_complement": RenderRule(
            "superscript",
            symbol=Name("c^-1", "ᶜ⁻¹", r"\complement^{-1}"),
        ),
        "regressive_product": RenderRule(
            "infix",
            symbol=Name("vee", "∨", r"\vee"),
            precedence=30,
        ),
        "unit": RenderRule("accent", symbol=Name("hat", "\u0302", r"\widehat")),
        "exp": RenderRule(
            "wrapper",
            opening=Name("exp(", "exp(", r"e^{"),
            closing=Name(")", ")", "}"),
            scalable=False,
            script_style=True,
        ),
        "log": RenderRule(
            "wrapper",
            opening=Name("log(", "log(", r"\log\left("),
            closing=Name(")", ")", r"\right)"),
            scalable=False,
        ),
        "sqrt": RenderRule(
            "wrapper",
            opening=Name("sqrt(", "√(", r"\sqrt{"),
            closing=Name(")", ")", "}"),
            scalable=False,
        ),
        "scalar_sqrt": RenderRule(
            "wrapper",
            opening=Name("sqrt(", "√(", r"\sqrt{"),
            closing=Name(")", ")", "}"),
            scalable=False,
        ),
        "norm": RenderRule(
            "wrapper",
            opening=Name("||", "‖", r"\lVert "),
            closing=Name("||", "‖", r" \rVert"),
            scalable=False,
        ),
        "norm2": RenderRule(
            "wrapper",
            opening=Name("||", "‖", r"\lVert "),
            closing=Name("||^2", "‖²", r" \rVert^{2}"),
            scalable=False,
        ),
        "even_grades": RenderRule(
            "wrapper",
            opening=Name("<", "⟨", r"\langle "),
            closing=Name(">even", "⟩₊", r" \rangle_{\text{even}}"),
            scalable=False,
        ),
        "odd_grades": RenderRule(
            "wrapper",
            opening=Name("<", "⟨", r"\langle "),
            closing=Name(">odd", "⟩₋", r" \rangle_{\text{odd}}"),
            scalable=False,
        ),
        "sandwich": RenderRule("sandwich"),
        "metric_regressive_product": RenderRule("metric_regressive"),
    }
    for operation_id in (
        "antidot_product",
        "antimetric_apply",
        "antireverse",
        "antiwedge",
        "bulk_part",
        "geometric_antiproduct",
        "left_hodge_dual",
        "left_interior_product",
        "left_weight_dual",
        "metric_apply",
        "metric_inner_product",
        "right_hodge_dual",
        "right_interior_product",
        "right_weight_dual",
        "transwedge",
        "transwedge_antiproduct",
        "weight_part",
    ):
        rules[operation_id] = compact_function(operation_id)
    return rules


def _lengyel_rules() -> dict[str | tuple[str, str], RenderRule]:
    rules = _conventional_rules()

    def target_rule(operation_id: str, target: str, rule: RenderRule) -> None:
        rules[(operation_id, target)] = rule

    rga_binary = {
        "geometric_product": ("gp", Name("gp", "⟑", r"\mathbin{\text{⟑}}")),
        "geometric_antiproduct": (
            "geometric_antiproduct",
            Name("geometric_antiproduct", "⟇", r"\mathbin{\text{⟇}}"),
        ),
        "metric_inner_product": (
            "metric_inner_product",
            Name("metric_inner_product", "•", r"\mathbin{\bullet}"),
        ),
        "antidot_product": (
            "antidot_product",
            Name("antidot_product", "∘", r"\mathbin{\circ}"),
        ),
        "left_interior_product": (
            "left_interior_product",
            Name("left_interior_product", "⌋", r"\mathbin{\rfloor}"),
        ),
        "right_interior_product": (
            "right_interior_product",
            Name("right_interior_product", "⌊", r"\mathbin{\lfloor}"),
        ),
        "antiwedge": ("antiwedge", Name("antiwedge", "∨", r"\vee")),
    }
    for operation_id, (ascii_name, symbol) in rga_binary.items():
        target_rule(operation_id, "ascii", RenderRule("function", symbol=ascii_name))
        target_rule(operation_id, "unicode", RenderRule("infix", symbol=symbol, precedence=30))
        target_rule(operation_id, "latex", RenderRule("infix", symbol=symbol, precedence=30))

    for operation_id, ascii_name, symbol in (
        ("transwedge", "transwedge", Name("transwedge", "⩓", r"\text{⩓}")),
        (
            "transwedge_antiproduct",
            "transwedge_antiproduct",
            Name("transwedge_antiproduct", "⩔", r"\text{⩔}"),
        ),
    ):
        target_rule(operation_id, "ascii", RenderRule("function", symbol=ascii_name))
        target_rule(
            operation_id,
            "unicode",
            RenderRule("infix", symbol=symbol, parameter="order", precedence=30),
        )
        target_rule(
            operation_id,
            "latex",
            RenderRule(
                "infix",
                symbol=symbol,
                parameter="order",
                parameter_position="underscript",
                precedence=30,
            ),
        )

    for operation_id, ascii_name, accent, kind in (
        ("complement", "complement", Name("bar", "\u0305", r"\overline"), "accent"),
        ("right_complement", "right_complement", Name("bar", "\u0305", r"\overline"), "accent"),
        ("left_complement", "left_complement", Name("underline", "\u0332", r"\underline"), "underaccent"),
        ("antireverse", "antireverse", Name("utilde", "\u0330", r"\utilde"), "underaccent"),
    ):
        target_rule(operation_id, "ascii", RenderRule("function", symbol=ascii_name))
        target_rule(operation_id, "unicode", RenderRule(kind, symbol=accent))
        target_rule(
            operation_id,
            "latex",
            RenderRule(kind, symbol=accent, group_operand=False),
        )

    for operation_id, ascii_name, symbol, kind in (
        ("right_hodge_dual", "right_hodge_dual", Name("star", "★", r"\text{★}"), "superscript"),
        ("left_hodge_dual", "left_hodge_dual", Name("star", "★", r"\text{★}"), "subscript"),
        ("right_weight_dual", "right_weight_dual", Name("white_star", "☆", r"\text{☆}"), "superscript"),
        ("left_weight_dual", "left_weight_dual", Name("white_star", "☆", r"\text{☆}"), "subscript"),
        ("bulk_part", "bulk_part", Name("bulk", "●", r"\text{●}"), "subscript"),
        ("weight_part", "weight_part", Name("weight", "○", r"\text{○}"), "subscript"),
    ):
        target_rule(operation_id, "ascii", RenderRule("function", symbol=ascii_name))
        target_rule(operation_id, "unicode", RenderRule(kind, symbol=symbol))
        target_rule(operation_id, "latex", RenderRule(kind, symbol=symbol))

    for operation_id, ascii_name, symbol in (
        ("metric_apply", "metric_apply", Name("G", "G", r"\mathbf{G}")),
        ("antimetric_apply", "antimetric_apply", Name("antiG", "𝔾", r"\mathbb{G}")),
    ):
        target_rule(operation_id, "ascii", RenderRule("function", symbol=ascii_name))
        target_rule(operation_id, "unicode", RenderRule("prefix", symbol=symbol))
        target_rule(operation_id, "latex", RenderRule("prefix", symbol=symbol))

    for target in _RULE_TARGETS:
        target_rule(
            "conjugate",
            target,
            RenderRule("function", symbol="conjugate", scalable=False),
        )
        target_rule(
            "hestenes_inner",
            target,
            RenderRule("function", symbol="hestenes_inner", scalable=False),
        )
    return rules


@dataclass(frozen=True, slots=True)
class DisplayPolicy:
    """Default rendering content and target, independent of notation."""

    content: str = "auto"
    target: str = "unicode"
    zero_tolerance: float = 1e-12
    coefficient_precision: int = 6

    def __post_init__(self) -> None:
        if self.content not in {"auto", "name", "expr", "value", "full"}:
            raise ValueError("display content must be 'auto', 'name', 'expr', 'value', or 'full'")
        if self.target not in {"ascii", "unicode", "latex"}:
            raise ValueError("display target must be 'ascii', 'unicode', or 'latex'")
        if not isinstance(self.zero_tolerance, Real) or isinstance(self.zero_tolerance, bool):
            raise TypeError("display zero_tolerance must be a real number")
        tolerance = float(self.zero_tolerance)
        if not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError("display zero_tolerance must be finite and non-negative")
        if not isinstance(self.coefficient_precision, Integral) or isinstance(self.coefficient_precision, bool):
            raise TypeError("display coefficient_precision must be an integer")
        precision = int(self.coefficient_precision)
        if not 1 <= precision <= 17:
            raise ValueError("display coefficient_precision must be between 1 and 17")
        object.__setattr__(self, "zero_tolerance", tolerance)
        object.__setattr__(self, "coefficient_precision", precision)


@dataclass(frozen=True, slots=True)
class PresentationConfig:
    """Independent immutable components used to present one algebra dimension."""

    blades: BladeConvention
    notation: Notation
    local_names: LocalNamePolicy
    display_order: DisplayOrder
    display: DisplayPolicy

    def __post_init__(self) -> None:
        expected = (
            ("blades", self.blades, BladeConvention),
            ("notation", self.notation, Notation),
            ("local_names", self.local_names, LocalNamePolicy),
            ("display_order", self.display_order, DisplayOrder),
            ("display", self.display, DisplayPolicy),
        )
        for name, value, expected_type in expected:
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} must be a {expected_type.__name__}")
        dimensions = {
            self.blades.dimension,
            self.local_names.dimension,
            self.display_order.dimension,
        }
        if len(dimensions) != 1:
            raise ValueError("blade, local-name, and display-order dimensions must match")

    @property
    def dimension(self) -> int:
        return self.blades.dimension

    def with_blades(self, blades: BladeConvention) -> PresentationConfig:
        return replace(self, blades=blades)

    def with_notation(self, notation: Notation) -> PresentationConfig:
        return replace(self, notation=notation)

    def with_local_names(self, local_names: LocalNamePolicy) -> PresentationConfig:
        return replace(self, local_names=local_names)

    def with_display_order(self, display_order: DisplayOrder) -> PresentationConfig:
        return replace(self, display_order=display_order)

    def with_display(self, display: DisplayPolicy) -> PresentationConfig:
        return replace(self, display=display)


@dataclass(frozen=True, slots=True, init=False)
class AlgebraDefinition:
    """A validated immutable real symmetric Gram matrix and backend options."""

    gram: tuple[tuple[float, ...], ...]
    id: str | None
    product_backend: str

    def __init__(
        self,
        gram: Sequence[Sequence[int | float]],
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> None:
        normalized = tuple(tuple(float(value) for value in row) for row in gram)
        dimension = len(normalized)
        if any(len(row) != dimension for row in normalized):
            raise ValueError("an algebra definition Gram matrix must be square")
        if any(not math.isfinite(value) for row in normalized for value in row):
            raise ValueError("an algebra definition Gram matrix must contain finite values")
        for row in range(dimension):
            for column in range(row + 1, dimension):
                if not math.isclose(
                    normalized[row][column],
                    normalized[column][row],
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    raise ValueError("an algebra definition Gram matrix must be symmetric")
        if id is not None and (not isinstance(id, str) or not id.strip()):
            raise ValueError("an algebra definition id must be a non-empty string or None")
        if product_backend not in {"auto", "diagonal", "packed", "lazy", "reference"}:
            raise ValueError("product_backend must be 'auto', 'diagonal', 'packed', 'lazy', or 'reference'")
        object.__setattr__(self, "gram", normalized)
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "product_backend", product_backend)

    @classmethod
    def from_signature(
        cls,
        signature: Sequence[int | float],
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> AlgebraDefinition:
        normalized = tuple(float(value) for value in signature)
        if any(value not in (-1.0, 0.0, 1.0) for value in normalized):
            raise ValueError("signature values must be +1, -1, or 0")
        gram = tuple(
            tuple(value if row == column else 0.0 for column in range(len(normalized)))
            for row, value in enumerate(normalized)
        )
        return cls(gram, id=id, product_backend=product_backend)

    @classmethod
    def from_pqr(
        cls,
        p: int,
        q: int = 0,
        r: int = 0,
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> AlgebraDefinition:
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (p, q, r)):
            raise ValueError("p, q, and r must be non-negative integers")
        return cls.from_signature(
            (0,) * r + (1,) * p + (-1,) * q,
            id=id,
            product_backend=product_backend,
        )

    @property
    def dimension(self) -> int:
        return len(self.gram)


@dataclass(frozen=True, slots=True, init=False)
class ModelConfig:
    """Optional semantic model identity and signed basis roles."""

    id: str
    roles: tuple[tuple[str, BladeRef], ...]

    def __init__(
        self,
        id: str,
        roles: Mapping[str, BladeRef] | Iterable[tuple[str, BladeRef]] = (),
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise ValueError("model id must be a non-empty string")
        items: tuple[tuple[str, BladeRef], ...]
        if isinstance(roles, Mapping):
            items = tuple(cast(Mapping[str, BladeRef], roles).items())
        else:
            items = tuple(roles)
        if len({name for name, _ in items}) != len(items):
            raise ValueError("model role names must be unique")
        if any(not isinstance(name, str) or not name for name, _ in items):
            raise ValueError("model role names must be non-empty strings")
        if any(not isinstance(ref, BladeRef) for _, ref in items):
            raise TypeError("model role references must be BladeRef values")
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "roles", items)


@dataclass(frozen=True, slots=True)
class AlgebraConfig:
    """A complete numeric definition, optional model, and presentation."""

    definition: AlgebraDefinition
    presentation: PresentationConfig
    model: ModelConfig | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.definition, AlgebraDefinition):
            raise TypeError("definition must be an AlgebraDefinition")
        if not isinstance(self.presentation, PresentationConfig):
            raise TypeError("presentation must be a PresentationConfig")
        if self.model is not None and not isinstance(self.model, ModelConfig):
            raise TypeError("model must be a ModelConfig or None")
        if self.definition.dimension != self.presentation.dimension:
            raise ValueError("algebra definition and presentation dimensions must match")
        if self.model is not None:
            limit = 1 << self.definition.dimension
            for name, ref in self.model.roles:
                if ref.mask >= limit:
                    raise ValueError(f"model role {name!r} refers to mask {ref.mask} outside the algebra dimension")

    def with_presentation(self, presentation: PresentationConfig) -> AlgebraConfig:
        return replace(self, presentation=presentation)


def default_presentation(dimension: int) -> PresentationConfig:
    """Construct independent default presentation components for a dimension."""
    from .blades import default_blade_convention

    blades = default_blade_convention(dimension)
    return PresentationConfig(
        blades=blades,
        notation=Notation(),
        local_names=LocalNamePolicy.from_convention(blades),
        display_order=DisplayOrder(dimension),
        display=DisplayPolicy(),
    )


__all__ = [
    "AlgebraConfig",
    "AlgebraDefinition",
    "DisplayPolicy",
    "ModelConfig",
    "Notation",
    "PresentationConfig",
    "RenderRule",
    "default_presentation",
]
