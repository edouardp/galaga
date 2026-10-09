"""Scale-invariant structural predicates and model-owned object classifiers."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np

from ..facade import (
    Multivector,
    complement,
    even_grades,
    is_even,
    is_rotor,
    left_complement,
    outer_product,
    reverse,
    squared,
)
from ._base import _ProjectiveBase, tolerance

if TYPE_CHECKING:
    from .cga import ConformalModel
from .classification import CGAClassification, ObjectClassification


def normalized(value: Multivector) -> Multivector:
    scale = float(np.max(np.abs(value.data)))
    return value if scale == 0 else value.algebra.multivector(value.data / scale, expr=False)


def is_zero(value: Multivector, atol: float) -> bool:
    return bool(np.max(np.abs(value.data)) <= atol)


def blade_span(value: Multivector, grade: int, atol: float) -> np.ndarray | None:
    """A nonzero k-vector is simple exactly when its wedge annihilator has dimension k."""
    vectors = tuple(value.algebra.blade(1 << index, expr=False) for index in range(value.algebra.n))
    matrix = np.column_stack([outer_product(vector, value).data for vector in vectors])
    _, singular, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.count_nonzero(singular > atol))
    return vh[rank:].T if len(vectors) - rank == grade else None


def classify_projective(
    model: _ProjectiveBase, value: Multivector, *, point_based: bool, atol: float
) -> ObjectClassification:
    model._check_value(value)
    atol = tolerance(atol)
    label = "rga" if point_based else "pga"
    scale = float(np.max(np.abs(value.data)))
    if scale == 0:
        return ObjectClassification(label, "zero", None, None, None, None)
    candidate = normalized(value)
    grade = candidate.homogeneous_grade(atol=atol)
    if grade is None:
        kind = _rigid_operator(candidate, atol) if point_based else None
        return ObjectClassification(label, kind or "general", None, None, None, None)
    if grade == 0:
        return ObjectClassification(label, "scalar", grade, None, True, None)
    if grade == model.algebra.n:
        kind = "antiscalar" if point_based else "pseudoscalar"
        return ObjectClassification(label, kind, grade, None, True, None)
    direct = candidate if point_based else normalized(left_complement(candidate))
    direct_grade = grade if point_based else model.algebra.n - grade
    span = blade_span(direct, direct_grade, atol)
    if span is None:
        return ObjectClassification(label, "general", grade, "direct", False, None)
    # A finite affine object has at least one weight-bearing vector in its span.
    row = model._projective_ref.mask.bit_length() - 1
    finite = bool(np.linalg.norm(span[row]) > atol)
    kind = {1: "point", 2: "line", 3: "plane"}[direct_grade]
    return ObjectClassification(label, kind if finite else "ideal " + kind, grade, "direct", True, finite)


def classify_conformal(
    model: ConformalModel, value: Multivector, *, representation: str = "auto", atol: float = 1e-9
) -> CGAClassification:
    model._check_value(value)
    atol = tolerance(atol)
    if model.spatial_dim not in {2, 3}:
        raise ValueError("CGA classification supports two or three spatial dimensions")
    if representation not in {"auto", "direct", "dual"}:
        raise ValueError("representation must be 'auto', 'direct', or 'dual'")
    if not np.any(value.data):
        return CGAClassification("cga", "zero", None, None, None, None)
    value = normalized(value)
    grade = value.homogeneous_grade(atol=atol)
    if grade is None:
        return CGAClassification("cga", "general", None, None, None, None)
    if grade in {0, model.algebra.n}:
        return CGAClassification("cga", "scalar" if grade == 0 else "pseudoscalar", grade, None, True, None)
    if representation == "dual":
        direct = classify_conformal(model, model.dual(value), representation="direct", atol=atol)
        return replace(direct, grade=grade, representation="dual")
    flat = is_zero(outer_product(value, model.infinity.without_expr()), atol)
    # Discard tolerated other-grade coefficients before strict model operations.
    value = value.algebra.multivector(
        [c if mask.bit_count() == grade else 0.0 for mask, c in enumerate(value.data)], expr=False
    )
    simple = blade_span(value, grade, atol) is not None
    if not simple:
        return CGAClassification("cga", "general", grade, "direct", False, None, flat=flat)
    if grade == 1:
        return _conformal_vector(model, value, flat, representation, atol)
    span = blade_span(value, grade, atol)
    origin_row = model._origin_ref.mask.bit_length() - 1
    finite = bool(np.linalg.norm(span[origin_row]) > atol)
    if flat:
        kind = {2: "flat point", 3: "line", 4: "plane"}[grade]
        return CGAClassification("cga", kind if finite else "ideal " + kind, grade, "direct", True, finite, flat=True)
    kind = {2: "dipole", 3: "circle", 4: "sphere"}[grade]
    if not finite:
        return CGAClassification(
            "cga",
            "degenerate",
            grade,
            "direct",
            True,
            False,
            (("reason", "round span has no finite weight"),),
            flat=False,
        )
    properties = _round_properties(model, span, atol)
    if properties is None:
        return CGAClassification(
            "cga",
            "degenerate",
            grade,
            "direct",
            True,
            finite,
            (("reason", "round carrier metric is singular"),),
            flat=False,
        )
    return CGAClassification("cga", kind, grade, "direct", True, finite, properties, flat=False)


def _round_properties(model: ConformalModel, span: np.ndarray, atol: float) -> tuple[tuple[str, object], ...] | None:
    weights = model._origin_ref.orientation * span[model._origin_ref.mask.bit_length() - 1]
    anchor = span @ weights / (weights @ weights)
    _, _, vh = np.linalg.svd(weights.reshape(1, -1), full_matrices=True)
    directions = span @ vh[1:].T
    induced = directions.T @ model.algebra.gram @ directions
    if np.any(np.linalg.eigvalsh(induced) <= atol):
        return None
    center = anchor - directions @ np.linalg.solve(induced, directions.T @ model.algebra.gram @ anchor)
    radius = float(-center @ model.algebra.gram @ center)
    coordinates = tuple(float(ref.orientation * center[ref.mask.bit_length() - 1]) for ref in model._base_refs)
    return (("center", coordinates), ("radius_squared", radius), ("real", radius >= -atol))


def _conformal_vector(
    model: ConformalModel, value: Multivector, flat: bool, representation: str, atol: float
) -> CGAClassification:
    if flat:
        return CGAClassification("cga", "point at infinity", 1, "direct", True, False, flat=True)
    weight = float(model.weight(value))
    square = float(squared(value))
    if abs(weight) <= atol:
        kind = "dual line" if model.spatial_dim == 2 else "dual plane"
        return CGAClassification("cga", kind, 1, "dual", True, True, flat=False)
    null = abs(square) <= atol
    if null and representation != "dual":
        return CGAClassification("cga", "round point", 1, "direct", True, True, flat=False)
    kind = "dual circle" if model.spatial_dim == 2 else "dual sphere"
    return CGAClassification("cga", kind, 1, "dual", True, True, (("radius_squared", square / weight**2),), flat=False)


def _rigid_operator(value: Multivector, atol: float) -> str | None:
    reciprocal = complement(value)
    norm = reciprocal * reverse(reciprocal)
    if norm.homogeneous_grade(atol=atol) != 0 or float(norm) <= atol:
        return None
    unit = reciprocal / np.sqrt(float(norm))
    if is_rotor(unit, atol=atol):
        return "motor"
    if is_even(unit, atol=atol) or np.any(np.abs(even_grades(unit).data) > atol):
        return None
    vectors = unit.algebra.basis_vectors(expr=False)
    actions = tuple(unit * v * reverse(unit) for v in vectors)
    if all(v.homogeneous_grade(atol=atol) == 1 for v in actions):
        return "flector"
    return None
