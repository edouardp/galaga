"""Named notation recipes for the public preset namespace."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from ..composition import NotationPatch as _NotationPatch
from ..presentation import Notation as _Notation
from ..presentation import RenderRule as _RenderRule
from ..presentation import _normalize_rules, _parse_rule_shorthand

_RuleChoice = _RenderRule | str

__all__ = [
    "default",
    "doran_lasenby",
    "functional",
    "functional_short",
    "hestenes",
    "lengyel",
    "lengyel_rga",
    "override",
]


def default(*, id: str = "default") -> _Notation:
    """Return the conventional notation with an optional identifying name."""
    return _Notation.default(id=id)


def functional(*, short: bool = False) -> _Notation:
    """Return functional operation names, optionally in their short form."""
    return _Notation.functional(short=short)


def functional_short() -> _Notation:
    """Return the short functional notation."""
    return _Notation.functional_short()


def doran_lasenby() -> _Notation:
    """Return Doran–Lasenby geometric-algebra notation."""
    return _Notation.doran_lasenby()


def hestenes() -> _Notation:
    """Return Hestenes geometric-algebra notation."""
    return _Notation.hestenes()


def lengyel() -> _Notation:
    """Return Lengyel's notation."""
    return _Notation.lengyel()


def lengyel_rga() -> _Notation:
    """Return Lengyel's RGA notation."""
    return _Notation.lengyel_rga()


def override(  # noqa: PLR0913 - explicit operation keywords support editor autocomplete
    *,
    reverse: Literal["tilde", "dagger"] | None = None,
    rules: Mapping[str | tuple[str, str], _RuleChoice] | None = None,
    ascii: Mapping[str, _RuleChoice] | None = None,
    unicode: Mapping[str, _RuleChoice] | None = None,
    latex: Mapping[str, _RuleChoice] | None = None,
    add: _RuleChoice | None = None,
    subtract: _RuleChoice | None = None,
    divide: _RuleChoice | None = None,
    negate: _RuleChoice | None = None,
    scalar_multiply: _RuleChoice | None = None,
    scalar_divide: _RuleChoice | None = None,
    power: _RuleChoice | None = None,
    antimetric_apply: _RuleChoice | None = None,
    antireverse: _RuleChoice | None = None,
    complement: _RuleChoice | None = None,
    clifford_conjugate: _RuleChoice | None = None,
    dual: _RuleChoice | None = None,
    even_grades: _RuleChoice | None = None,
    exp: _RuleChoice | None = None,
    grade_involution: _RuleChoice | None = None,
    left_complement: _RuleChoice | None = None,
    left_hodge_dual: _RuleChoice | None = None,
    left_weight_dual: _RuleChoice | None = None,
    metric_apply: _RuleChoice | None = None,
    norm2: _RuleChoice | None = None,
    odd_grades: _RuleChoice | None = None,
    outercos: _RuleChoice | None = None,
    outerexp: _RuleChoice | None = None,
    outersin: _RuleChoice | None = None,
    outertan: _RuleChoice | None = None,
    right_complement: _RuleChoice | None = None,
    right_hodge_dual: _RuleChoice | None = None,
    right_weight_dual: _RuleChoice | None = None,
    squared: _RuleChoice | None = None,
    uncomplement: _RuleChoice | None = None,
    undual: _RuleChoice | None = None,
    is_basis_blade: _RuleChoice | None = None,
    is_bivector: _RuleChoice | None = None,
    is_even: _RuleChoice | None = None,
    is_rotor: _RuleChoice | None = None,
    is_rotor_generator: _RuleChoice | None = None,
    is_scalar: _RuleChoice | None = None,
    is_vector: _RuleChoice | None = None,
    inverse: _RuleChoice | None = None,
    log: _RuleChoice | None = None,
    rotor_generator: _RuleChoice | None = None,
    sqrt: _RuleChoice | None = None,
    unit: _RuleChoice | None = None,
    scalar_sqrt: _RuleChoice | None = None,
    norm: _RuleChoice | None = None,
    antidot_product: _RuleChoice | None = None,
    anticommutator: _RuleChoice | None = None,
    antiwedge: _RuleChoice | None = None,
    commutator: _RuleChoice | None = None,
    doran_lasenby_inner: _RuleChoice | None = None,
    geometric_antiproduct: _RuleChoice | None = None,
    half_anticommutator: _RuleChoice | None = None,
    half_commutator: _RuleChoice | None = None,
    hestenes_inner: _RuleChoice | None = None,
    jordan_product: _RuleChoice | None = None,
    left_contraction: _RuleChoice | None = None,
    left_interior_product: _RuleChoice | None = None,
    lie_bracket: _RuleChoice | None = None,
    metric_inner_product: _RuleChoice | None = None,
    metric_regressive_product: _RuleChoice | None = None,
    regressive_product: _RuleChoice | None = None,
    right_contraction: _RuleChoice | None = None,
    right_interior_product: _RuleChoice | None = None,
    sandwich: _RuleChoice | None = None,
    scalar_product: _RuleChoice | None = None,
    geometric_product: _RuleChoice | None = None,
    outer_product: _RuleChoice | None = None,
    grade: _RuleChoice | None = None,
    grades: _RuleChoice | None = None,
    transwedge: _RuleChoice | None = None,
    transwedge_antiproduct: _RuleChoice | None = None,
    **operations: _RuleChoice,
) -> _NotationPatch:
    """Override selected operation rules while inheriting every other rule.

    ``rules`` uses the same keys as ``Notation``: an operation ID for a
    target-neutral rule, or ``(operation_id, target)`` for one output target.
    The target maps are convenient spellings for target-specific changes.
    Operation keyword arguments supply generic rules. Values may be complete
    ``RenderRule`` objects or compact strings such as ``"prefix:star"``.
    """
    named_operations = {
        name: value
        for name, value in locals().items()
        if name not in {"reverse", "rules", "ascii", "unicode", "latex", "operations"} and value is not None
    }
    entries: list[tuple[str | tuple[str, str], _RuleChoice]] = []
    if rules is not None:
        if not isinstance(rules, Mapping):
            raise TypeError("notation override rules must be a mapping")
        entries.extend(rules.items())
    entries.extend(named_operations.items())
    entries.extend(operations.items())
    for target, selected in (("ascii", ascii), ("unicode", unicode), ("latex", latex)):
        if selected is None:
            continue
        if not isinstance(selected, Mapping):
            raise TypeError(f"notation override {target} must be a mapping")
        entries.extend(((operation_id, target), rule) for operation_id, rule in selected.items())
    normalized: list[tuple[str | tuple[str, str], _RenderRule]] = []
    for key, rule in entries:
        parsed = _parse_rule_shorthand(rule) if isinstance(rule, str) else rule
        if isinstance(key, str) and isinstance(rule, str):
            normalized.extend(((key, target), parsed) for target in ("ascii", "unicode", "latex"))
        else:
            normalized.append((key, parsed))
    return _NotationPatch(reverse=reverse, rules=_normalize_rules(normalized))


def __dir__() -> list[str]:
    """Advertise only named notation recipes."""
    return list(__all__)
