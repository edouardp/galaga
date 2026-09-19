"""CGA object classification and semantic highlight recipes.

The classifier consults the validated :class:`~galaga.cga.ConformalModel`
component families (Lengyel's round/flat bulk and weight parts). A highlight
recipe classifies one multivector and returns an annotated view. Incidence
views combine component families into carrier/cocarrier geometry, while
component-role views retain kind-specific names for each Lengyel family.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from numbers import Real
from typing import Any, Literal

import numpy as np

from galaga import Multivector, outer_product, scalar_product, squared
from galaga.cga import ConformalModel

from .annotator import annotator
from .model import on
from .targets import TermTarget, terms

__all__ = [
    "CGAObject",
    "HighlightDecomposition",
    "OverMarker",
    "cga_parts",
    "classify_cga",
    "highlight_cga",
    "highlight_object",
]

HighlightDecomposition = Literal["incidence", "components"]
OverMarker = Literal["overgroup", "overbrace", "overline", "overbracket"]
OVER_MARKERS: tuple[OverMarker, ...] = ("overgroup", "overbrace", "overline", "overbracket")

_FAMILIES = ("round_weight", "round_bulk", "flat_bulk", "flat_weight")

_ROUND = "#b8e6bf"
_FLAT = "#d8c4ee"
_ORIGIN = "#cfe2ff"
_BULK = "#e8f5e9"
_ROUND_LABEL = "#2f7d4f"
_FLAT_LABEL = "#6b4a9e"

_DEFAULT_STYLES: dict[str, tuple[str, str]] = {
    "round_weight": ("round weight", _ORIGIN),
    "round_bulk": ("round bulk", _BULK),
    "flat_bulk": ("flat bulk", _FLAT),
    "flat_weight": ("flat weight", _FLAT),
}

_KIND_STYLES: dict[str, dict[str, tuple[str, str]]] = {
    "dipole": {
        "round_weight": ("carrier line", _ROUND),
        "round_bulk": ("carrier line", _ROUND),
        "flat_bulk": ("flat point", _FLAT),
        "flat_weight": ("flat point", _FLAT),
    },
    "flat point": {
        "flat_bulk": ("position", _FLAT),
        "flat_weight": ("origin", _ORIGIN),
    },
    "line": {
        "flat_bulk": ("direction", _FLAT),
        "flat_weight": ("position", _FLAT),
    },
    "plane": {
        "flat_bulk": ("direction", _FLAT),
        "flat_weight": ("position", _FLAT),
    },
    "round point": {
        "round_weight": ("origin", _ORIGIN),
        "round_bulk": ("position", _ROUND),
        "flat_bulk": ("infinity", _FLAT),
    },
    "dual sphere": {
        "round_weight": ("origin", _ORIGIN),
        "round_bulk": ("center", _ROUND),
        "flat_bulk": ("infinity", _FLAT),
    },
    "circle": {
        "round_weight": ("plane part", _ORIGIN),
        "round_bulk": ("center part", _ROUND),
        "flat_bulk": ("flat part", _FLAT),
        "flat_weight": ("flat weight", _FLAT),
    },
    "sphere": {
        "round_weight": ("origin part", _ORIGIN),
        "round_bulk": ("center part", _ROUND),
        "flat_bulk": ("flat part", _FLAT),
        "flat_weight": ("flat weight", _FLAT),
    },
}


@dataclass(frozen=True, slots=True)
class CGAObject:
    """The modeled kind of one homogeneous conformal multivector."""

    kind: str
    grade: int | None
    flat: bool | None
    simple: bool | None


@dataclass(frozen=True, slots=True)
class _LayeredLabels:
    round_span: str
    round_cocarrier: str
    flat_span: str
    flat_cocarrier: str


_LAYERED_LABELS = {
    "dipole": _LayeredLabels("carrier line", "cocarrier normal", "flat point", "cocarrier position"),
    "circle": _LayeredLabels("carrier plane", "cocarrier direction", "flat line", "cocarrier moment"),
}
_DIRECT_KINDS = {
    2: ("flat point", "dipole"),
    3: ("line", "circle"),
    4: ("plane", "sphere"),
}


def _checked_inputs(value: Any, model: Any, operation: str) -> tuple[Multivector, ConformalModel]:
    if not isinstance(value, Multivector):
        raise TypeError(f"{operation} expects a Galaga Multivector")
    if not isinstance(model, ConformalModel):
        raise TypeError(f"{operation} expects a ConformalModel")
    if value.algebra is not model.algebra:
        raise ValueError(f"{operation} value must belong to the model algebra")
    if model.spatial_dim != 3:
        raise ValueError(f"{operation} currently supports three-dimensional conformal models")
    return value, model


def _checked_tolerance(value: Any) -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError("atol must be a real number")
    tolerance = float(value)
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("atol must be finite and non-negative")
    return tolerance


def _is_zero(value: Multivector, atol: float) -> bool:
    return not np.any(np.abs(value.data) > atol)


def _normalized(value: Multivector) -> Multivector:
    """Return a coefficient-normalized copy for projective predicates."""

    scale = float(np.max(np.abs(value.data)))
    if scale == 0:
        return value
    return value.algebra.multivector(value.data / scale, expr=False)


def _masks(value: Multivector, atol: float) -> tuple[int, ...]:
    return tuple(int(mask) for mask in np.flatnonzero(np.abs(value.data) > atol))


def _is_simple(value: Multivector, model: ConformalModel, grade: int, atol: float) -> bool:
    """Test decomposability for homogeneous blades in five-dimensional CGA."""

    if grade in {0, 1, 4, 5}:
        return True
    candidate = value if grade == 2 else _normalized(model.dual(value))
    return _is_zero(outer_product(candidate, candidate), atol)


def _grade_one_kind(value: Multivector, infinity: Multivector, flat: bool, atol: float) -> str:
    if flat:
        return "point at infinity"
    if _is_zero(squared(value), atol):
        return "round point"
    if _is_zero(scalar_product(value, infinity), atol):
        return "dual plane"
    return "dual sphere"


def _simple_kind(value: Multivector, infinity: Multivector, grade: int, flat: bool | None, atol: float) -> str:
    if grade == 0:
        return "scalar"
    if grade == 1:
        return _grade_one_kind(value, infinity, bool(flat), atol)
    flat_kind, round_kind = _DIRECT_KINDS.get(grade, ("pseudoscalar", "pseudoscalar"))
    return flat_kind if flat else round_kind


def classify_cga(value: Multivector, model: ConformalModel, *, atol: float = 1e-9) -> CGAObject:
    """Classify one homogeneous conformal multivector by algebraic family.

    Simple OPNS blades use grade and divisibility by infinity to distinguish
    flat from round families. Grade-one vectors need both common readings:
    null vectors with conformal weight are direct points, weight-zero non-null
    vectors are dual planes, and the remaining non-null vectors are dual
    spheres. The classification is projective above the absolute zero floor.
    """

    value, model = _checked_inputs(value, model, "classify_cga")
    atol = _checked_tolerance(atol)
    if _is_zero(value, atol):
        return CGAObject("zero", None, None, None)

    normalized = _normalized(value)
    grade = normalized.homogeneous_grade(atol=atol)
    if grade is None:
        return CGAObject("general", None, None, None)

    infinity = _normalized(model.infinity)
    flat = _is_zero(outer_product(normalized, infinity), atol) if 1 <= grade <= 4 else None
    simple = _is_simple(normalized, model, grade, atol)
    if not simple:
        return CGAObject("general", grade, flat, False)
    kind = _simple_kind(normalized, infinity, grade, flat, atol)
    return CGAObject(kind, grade, flat, True)


def cga_parts(value: Multivector, model: ConformalModel, *, atol: float = 1e-9) -> dict[str, TermTarget]:
    """Return the nonempty Lengyel component families as joined term targets."""

    value, model = _checked_inputs(value, model, "cga_parts")
    atol = _checked_tolerance(atol)
    if _is_zero(value, atol):
        return {}
    normalized = _normalized(value)
    part_values = {
        "round_weight": model.round_weight_part(normalized),
        "round_bulk": model.round_bulk_part(normalized),
        "flat_bulk": model.flat_bulk_part(normalized),
        "flat_weight": model.flat_weight_part(normalized),
    }
    parts: dict[str, TermTarget] = {}
    for name in _FAMILIES:
        masks = _masks(part_values[name], atol)
        if masks:
            parts[name] = terms(*(value.algebra.blade(mask) for mask in masks))
    return parts


def _combined_target(value: Multivector, parts: dict[str, TermTarget], families: tuple[str, ...]) -> TermTarget | None:
    masks = sorted({mask for family in families if family in parts for mask in parts[family].masks})
    return _terms_for(value, masks) if masks else None


def _layered_rules(
    value: Multivector, parts: dict[str, TermTarget], labels: _LayeredLabels, over_marker: OverMarker
) -> list[Any]:
    """Build Lengyel carrier/flat fills with cocarrier overlays.

    The round-weight family is the directional cocarrier subset of the full
    round span. The flat-weight family is the positional or moment cocarrier
    subset of the full flat span. This structure is shared by dipoles and
    circles; their geometric labels differ by grade.
    """

    round_span = _combined_target(value, parts, ("round_weight", "round_bulk"))
    flat_span = _combined_target(value, parts, ("flat_bulk", "flat_weight"))
    rules: list[Any] = []
    if round_span is not None:
        rules.append(
            on(
                round_span,
                background=_ROUND,
                label=labels.round_span,
                label_color=_ROUND_LABEL,
                side="below",
                join=True,
            )
        )
    if "round_weight" in parts:
        rules.append(
            on(
                parts["round_weight"],
                label=labels.round_cocarrier,
                marker=over_marker,
                color="#0099cc",
                clearance="4px",
                join=True,
            )
        )
    if flat_span is not None:
        rules.append(
            on(
                flat_span,
                background=_FLAT,
                label=labels.flat_span,
                label_color=_FLAT_LABEL,
                side="below",
                join=True,
            )
        )
    if "flat_weight" in parts:
        rules.append(
            on(
                parts["flat_weight"],
                label=labels.flat_cocarrier,
                marker=over_marker,
                color="#0099cc",
                clearance="4px",
                join=True,
            )
        )
    return rules


def _annotate(
    value: Multivector,
    model: ConformalModel,
    *,
    atol: float,
    decomposition: HighlightDecomposition,
    over_marker: OverMarker,
) -> Any:
    obj = classify_cga(value, model, atol=atol)
    parts = cga_parts(value, model, atol=atol)
    layered_labels = _LAYERED_LABELS.get(obj.kind) if decomposition == "incidence" else None
    if layered_labels is not None and parts:
        return annotator(*_layered_rules(value, parts, layered_labels, over_marker))(value)
    styles = _KIND_STYLES.get(obj.kind, _DEFAULT_STYLES)
    grouped: dict[tuple[str, str], list[TermTarget]] = {}
    order: list[tuple[str, str]] = []
    for family in _FAMILIES:
        if family not in parts:
            continue
        label, color = styles.get(family, _DEFAULT_STYLES[family])
        key = (label, color)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(parts[family])
    rules = []
    for label, color in order:
        masks: list[Any] = []
        for part in grouped[(label, color)]:
            masks.extend(part.masks)
        masks.sort()
        rules.append(
            on(
                _terms_for(value, masks),
                background=color,
                label=label,
                side="below",
                join=True,
            )
        )
    return annotator(*rules)(value)


def _terms_for(value: Multivector, masks: list[int]) -> TermTarget:
    return terms(*(value.algebra.blade(mask) for mask in masks))


def highlight_cga(
    model: ConformalModel,
    *,
    decomposition: HighlightDecomposition = "incidence",
    atol: float = 1e-9,
    over_marker: OverMarker = "overgroup",
) -> Callable[[Multivector], Any]:
    """Return a callable that classifies and highlights one CGA object.

    ``decomposition="incidence"`` emphasizes carrier/cocarrier geometry for
    supported objects. ``decomposition="components"`` keeps the
    object-specific component-role vocabulary derived from Lengyel's four
    round/flat bulk/weight families.

    ``over_marker`` selects the callout style for incidence cocarrier brackets:
    ``"overgroup"`` (default), ``"overbrace"``, ``"overline"``, or
    ``"overbracket"``.

    Usage::

        highlight = highlight_cga(cga, decomposition="incidence")
        view = highlight(dipole)
    """

    if not isinstance(model, ConformalModel):
        raise TypeError("highlight_cga expects a ConformalModel")
    if model.spatial_dim != 3:
        raise ValueError("highlight_cga currently supports three-dimensional conformal models")
    if decomposition not in {"incidence", "components"}:
        raise ValueError("decomposition must be 'incidence' or 'components'")
    if over_marker not in OVER_MARKERS:
        raise ValueError(f"over_marker must be one of {OVER_MARKERS}")
    atol = _checked_tolerance(atol)

    def highlight(value: Multivector) -> Any:
        return _annotate(value, model, atol=atol, decomposition=decomposition, over_marker=over_marker)

    return highlight


def highlight_object(
    model: ConformalModel,
    *,
    decomposition: HighlightDecomposition = "incidence",
    atol: float = 1e-9,
    over_marker: OverMarker = "overgroup",
) -> Callable[[Multivector], Any]:
    """Alias of :func:`highlight_cga` for the object-level highlight recipe."""

    return highlight_cga(model, decomposition=decomposition, atol=atol, over_marker=over_marker)
